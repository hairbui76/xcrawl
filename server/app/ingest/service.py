"""``MOD-ingest-service`` -- the two ingest transactions and the two ingest reads.

Operations implemented here, named after their ids in ``contracts/ports.yaml``:

===========================  ==========================  ==============================
operation id                 function                    transaction
===========================  ==========================  ==============================
``ingest.submit_batch``      :func:`submit_batch`        ``TXN-ingest-batch``
``ingest.commit_checkpoint`` :func:`commit_checkpoint`   ``TXN-checkpoint-only``
``ingest.get_receipt``       :func:`get_receipt`         none (read)
``ingest.get_checkpoint``    :func:`get_checkpoint`      none (read)
===========================  ==========================  ==============================

The one property everything here exists to hold
-----------------------------------------------
I02, in three parts: (a) no ACK leaves the server before COMMIT returns; (b) no observable
moment exists in which ``checkpoint.acked_through_ingest_sequence`` has advanced past
durable ``post`` rows; (c) a replay of the same ``idempotency_key`` with the same
``payload_hash`` returns the same receipt and changes no count.

Part (a) is structural: the only ``engine.begin()`` blocks in this module build their
response *after* the block exits, so there is no code path on which a receipt can be
returned from inside a transaction. Part (b) is structural too: the checkpoint row is
written in the same transaction as the posts whose sequence it acknowledges, and the
checkpoint-only path is forbidden by construction from raising
``acked_through_ingest_sequence``. Part (c) is the replay branch below, which returns
before opening any write transaction at all.

Cross-domain calls
------------------
This card owns none of identity, storage health or assignment leasing. Each is reached
through the port its owning card provides, and each is optional at import time:

* ``server.app.identity.service`` (``TC-canonical-identity-merge``) -- when absent, a new
  post is stored with ``identity_resolution = 'pending'``. That is the honest value:
  "not resolved yet", not "post only" and not "linked". Nothing about identity is guessed
  here (B15/I03).
* ``server.app.storage.guard`` (``TC-storage-write-blocked-readiness``) -- consumed
  through that card's documented call contract: ``guard.assert_writable(operation_id)``
  before the transaction opens, ``guard.record_write_failure()`` when a write actually
  fails. When no guard is injected the gate simply does not run; an unwired gate is never
  reported as a healthy one (CAP-P5, I13), and a real write failure still surfaces as
  ``STORAGE_WRITE_FAILED`` from the handler around the transaction.
* an assignment/lease port (``TC-scheduler-lease-claim``) -- when absent, lease epoch
  validation does not run and the caller must supply ``run_id`` explicitly.

Denied edges (``contracts/modules.yaml``): nothing in this module calls Telegram, an AI
provider, or reads a provider secret, and no network call is made inside a transaction
(SRC-PLAN §5.1).
"""

from __future__ import annotations

import importlib
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from types import ModuleType
from typing import Any, Protocol

from pydantic import ValidationError
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.models.ingest_batch import IngestBatch
from rr_contracts.generated.models.ingest_receipt import CheckpointOnlyRequest
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine
from sqlalchemy.exc import IntegrityError, OperationalError

from server.app.ingest.idempotency import (
    ReplayDecision,
    checkpoint_only_idempotency_key,
    classify,
    compute_payload_hash,
    compute_receipt_hash,
    compute_source_snapshot_hash,
)
from server.app.ingest.repository import (
    CheckpointRow,
    IngestRepository,
    ReceiptRow,
    json_text,
    new_ulid,
)
from server.app.storage.guard import StorageRefused

#: A failed write reaches this module at either of two layers: SQLAlchemy wraps a driver
#: error as ``OperationalError``/``IntegrityError``, while a failure raised from a
#: connection-level event hook -- which is how ``server/app/db/faults.py`` reproduces a full
#: disk -- arrives as the bare ``sqlite3`` exception. Both mean the same thing here: the
#: transaction did not commit, so nothing may be ACKed.
WRITE_FAILURES: tuple[type[Exception], ...] = (OperationalError, IntegrityError, sqlite3.Error)

#: HTTP status per error code, from contracts/http/openapi.yaml paths /v1/ingest/*.
#: The card's §7 table says 400 for VALIDATION_ERROR; the OpenAPI document -- which is the
#: wire contract for these three routes -- says 422. The wire contract wins and the
#: divergence is reported as CR-TC-ingest-04.
HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.STALE_LEASE: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.WORKER_LEASE_EXPIRED: 412,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class IngestError(Exception):
    """A contract error code plus the safe envelope fields it must be reported with.

    Never carries post text, a URL, a token or a stack trace: ``contracts/errors.yaml``
    forbids all of those in an error envelope, and the only way to keep that guarantee is
    for the exception itself never to hold them.
    """

    def __init__(
        self,
        code: ErrorCode,
        message_safe: str,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {message_safe}")
        self.code = code
        self.message_safe = message_safe
        self.details_safe: dict[str, Any] | None = (
            None if details_safe is None else dict(details_safe)
        )
        self.retry_after_ms = retry_after_ms

    @property
    def http_status(self) -> int:
        return HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The ``ErrorEnvelope`` of ``contracts/http/openapi.yaml``.

        ``scope`` and ``retry_class`` are read from the generated registry rather than
        chosen here, so a handler cannot grant a retry policy the contract did not.
        """
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe,
            "retry_after_ms": self.retry_after_ms,
        }


class IngestDependencyUnavailable(Exception):
    """A port this operation needs is not wired. Surfaces as ``INTERNAL``, never as a 4xx.

    Reporting a missing internal dependency as a client error would blame the collector for
    a server deployment gap and would let a broken wiring pass a negative test.
    """


@dataclass(frozen=True)
class LeaseSnapshot:
    """What the assignment/lease port tells ingest about a job's current lease."""

    run_id: str
    lease_epoch: int
    revoked: bool = False


class AssignmentPort(Protocol):
    """Read-only view of ``MOD-job-service`` state (``TC-scheduler-lease-claim``)."""

    def lease_snapshot(self, *, job_id: str, lease_id: str) -> LeaseSnapshot | None: ...


@dataclass(frozen=True)
class ResolvedTarget:
    """Result of ``identity.resolve_target`` as this module consumes it."""

    kind: str
    key: str
    identity_resolution: str


class IdentityPort(Protocol):
    """The one operation of ``server.app.identity.service`` this card calls.

    Only ``identity.resolve_target`` -- ``mutation: false`` in ``contracts/ports.yaml``. The
    writing operations (``record_alias``, ``merge_works``, ``quarantine_conflict``) belong to
    ``TC-canonical-identity-merge``; this card's §1 non-goals put alias creation and merging
    out of scope, so ``works_linked`` stays 0 and a post that no existing alias resolves is
    stored as ``pending`` rather than being linked on a guess (B15, I03, REQ-D33).
    """

    def resolve_target(
        self,
        target: Any,
        *,
        owner_id: str,
        identifiers: Sequence[Any] = (),
        post_id: str | None = None,
        caller_module: str = ...,
    ) -> Any: ...


class StorageGuardPort(Protocol):
    """The write gate provided by ``server.app.storage.guard.StorageGuard``.

    Its call contract, quoted from that module: ask ``assert_writable`` *before* the
    transaction opens (it raises rather than returning a falsy value a caller could forget
    to check), and report a real failure with ``record_write_failure`` so the health state
    machine learns about it. Which states refuse which operations is that card's decision,
    read from ``contracts/state/storage.yaml``; ingest does not second-guess it.
    """

    def assert_writable(self, operation_id: OperationId) -> None: ...

    def record_write_failure(self) -> str | None: ...


@dataclass(frozen=True)
class IngestContext:
    """Everything an ingest operation needs, injected rather than imported.

    ``clock`` and ``id_factory`` are parameters because the oracles in
    ``acceptance/fixtures/**`` are about ordering and identity of rows, and a test that
    cannot pin either has to assert on wall-clock coincidences.
    """

    engine: Engine
    owner_id: str
    repository: IngestRepository = field(default_factory=IngestRepository)
    assignment: AssignmentPort | None = None
    identity: IdentityPort | None = None
    storage_guard: StorageGuardPort | None = None
    clock: Any = None
    id_factory: Any = None

    def now(self) -> datetime:
        if self.clock is None:
            return datetime.now(UTC)
        value: datetime = self.clock()
        return value

    def new_id(self) -> str:
        if self.id_factory is None:
            return new_ulid()
        value: str = self.id_factory()
        return value


# --------------------------------------------------------------------------- helpers


def format_timestamp(moment: datetime) -> str:
    """RFC 3339 UTC with mandatory millisecond precision (``entities.yaml`` §timestamps)."""
    return moment.astimezone(UTC).strftime(_TIMESTAMP_FORMAT)[:-3] + "Z"


def parse_timestamp(value: str) -> datetime:
    """Inverse of :func:`format_timestamp`."""
    return datetime.strptime(value, _TIMESTAMP_FORMAT + "Z").replace(tzinfo=UTC)


def _identity_module() -> ModuleType | None:
    """``server.app.identity.service`` if ``TC-canonical-identity-merge`` has landed.

    Imported by name rather than with a ``from ... import``: the module may legitimately
    not exist yet, and a static import of a missing module would make this whole package
    unimportable instead of degrading to "identity not resolved".
    """
    try:
        return importlib.import_module("server.app.identity.service")
    except ImportError:
        return None


def _assert_writable(ctx: IngestContext, operation_id: OperationId) -> None:
    """Ask the storage guard for permission BEFORE opening the transaction.

    A refusal is translated into an :class:`IngestError` carrying the guard's own error
    code -- ``STORAGE_WRITE_FAILED`` while write-blocked or in maintenance,
    ``RESTORE_UNVERIFIED`` while a restore is unreconciled. Ingest does not decide which
    state refuses what; that mapping belongs to ``contracts/state/storage.yaml`` and to the
    card that implements it.

    With no guard injected the gate does not run. That is *not* read as "healthy": nothing
    is ACKed on the strength of it, and a write that then fails for real still raises
    ``STORAGE_WRITE_FAILED`` from :func:`_storage_write_failed`.
    """
    guard = ctx.storage_guard
    if guard is None:
        return
    try:
        guard.assert_writable(operation_id)
    except StorageRefused as refusal:
        envelope: dict[str, Any] = refusal.envelope
        raise IngestError(
            ErrorCode(envelope["code"]),
            str(envelope["message_safe"]),
            details_safe=envelope.get("details_safe"),
            retry_after_ms=envelope.get("retry_after_ms"),
        ) from refusal


#: ``referenced_link.link_kind_hint`` -> the ``id_scheme`` it may stand for. A hint is a
#: hint (``ingest-batch.schema.json``): only the two canonical schemes are followed, and the
#: value is normalised by identity, never by ingest. ``publisher``/``code_repo``/``other``
#: map to nothing, because guessing an identifier from a link that does not announce one is
#: exactly what REQ-D33 forbids.
LINK_HINT_TO_SCHEME: dict[str, str] = {
    "arxiv_abs": "arxiv",
    "arxiv_pdf": "arxiv",
    "doi_org": "doi",
}


def _identifiers_from_links(port: Any, referenced_links: Sequence[Mapping[str, Any]]) -> list[Any]:
    """Build ``identity.Identifier`` values from the links a post announced.

    The types come from the identity package itself rather than being re-declared here:
    re-declaring them would be a second definition of another module's contract.
    """
    identifier_type = getattr(port, "Identifier", None)
    scheme_type = getattr(port, "IdScheme", None)
    if identifier_type is None or scheme_type is None:
        return []
    identifiers: list[Any] = []
    for link in referenced_links:
        scheme_name = LINK_HINT_TO_SCHEME.get(str(link.get("link_kind_hint", "")))
        if scheme_name is None:
            continue
        raw = str(link.get("expanded_url") or link.get("url"))
        identifiers.append(
            identifier_type(
                scheme=scheme_type(scheme_name),
                raw=raw,
                evidence_source="post_link",
                confidence="asserted_by_source",
            )
        )
    return identifiers


def _resolve_target(
    ctx: IngestContext,
    connection: Connection,
    *,
    referenced_links: Sequence[Mapping[str, Any]],
) -> tuple[ResolvedTarget | None, str | None]:
    """Call ``identity.resolve_target`` inside the ingest transaction.

    The open connection is passed through, not a fresh one: ``TXN-ingest-batch`` lists the
    identity rows among the rows written together, so an identity read that saw a different
    snapshot than the insert would break the "all or nothing" the transaction promises.

    Returns ``(target, conflict_reason)``. A conflict is not an error for the batch: the
    contract says the other items still commit and only the conflicting one is held back
    (``contracts/errors.yaml`` IDENTITY_CONFLICT), so it comes back as a value to be turned
    into a receipt warning rather than as an exception that would roll everything back.
    """
    port: Any = ctx.identity if ctx.identity is not None else _identity_module()
    if port is None:
        return None, None
    identifiers = _identifiers_from_links(port, referenced_links)
    if not identifiers:
        return None, None
    try:
        resolution = port.resolve_target(
            connection,
            owner_id=ctx.owner_id,
            identifiers=identifiers,
            caller_module="MOD-ingest-service",
        )
    except Exception as exc:  # identity raises IdentityError; it owns its own type
        code = getattr(exc, "code", None)
        if code is ErrorCode.IDENTITY_CONFLICT:
            return None, "identity_conflict"
        if code is ErrorCode.NOT_FOUND:
            return None, None
        raise
    target = resolution.target
    return (
        ResolvedTarget(
            kind=str(target["kind"]),
            key=str(target["target_key"]),
            identity_resolution=(
                "resolved_linked" if target["kind"] == "work" else "resolved_post_only"
            ),
        ),
        None,
    )


def _lease_snapshot(ctx: IngestContext, *, job_id: str, lease_id: str) -> LeaseSnapshot | None:
    if ctx.assignment is None:
        return None
    return ctx.assignment.lease_snapshot(job_id=job_id, lease_id=lease_id)


def _check_lease(ctx: IngestContext, *, job_id: str, lease_id: str, lease_epoch: int) -> str | None:
    """Validate the caller's lease and return the run id it belongs to.

    Returns ``None`` when no assignment port is wired -- lease validation then does not
    run, and the caller must supply ``run_id``. ``STALE_LEASE`` and
    ``WORKER_LEASE_EXPIRED`` are distinct: the first is an older epoch of a live lease, the
    second is a lease the scheduler has taken away (I10, ``contracts/errors.yaml``).
    """
    snapshot = _lease_snapshot(ctx, job_id=job_id, lease_id=lease_id)
    if snapshot is None:
        return None
    if snapshot.revoked:
        raise IngestError(
            ErrorCode.WORKER_LEASE_EXPIRED,
            "Lease của assignment đã bị thu hồi; không commit được.",
            details_safe={"job_id": job_id},
        )
    if lease_epoch != snapshot.lease_epoch:
        raise IngestError(
            ErrorCode.STALE_LEASE,
            "Lease epoch cũ hơn epoch hiện hành; không có dữ liệu nào thay đổi.",
            details_safe={"job_id": job_id, "lease_epoch_seen": lease_epoch},
        )
    return snapshot.run_id


def _validation_error(message: str, **details: Any) -> IngestError:
    return IngestError(ErrorCode.VALIDATION_ERROR, message, details_safe=details or None)


def _wire_counts(
    *,
    received: int,
    inserted: int,
    deduplicated: int,
    quarantined: int,
    rejected: int,
    works_linked: int,
    max_ingest_sequence: int,
) -> dict[str, int]:
    return {
        "received": received,
        "inserted": inserted,
        "deduplicated": deduplicated,
        "quarantined": quarantined,
        "rejected": rejected,
        "works_linked": works_linked,
        "max_ingest_sequence": max_ingest_sequence,
    }


def _receipt_envelope(
    receipt: ReceiptRow,
    checkpoint: CheckpointRow,
    *,
    status: str,
    accepted_items: Sequence[Mapping[str, Any]],
    warnings: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the ``{"receipt": ...}`` response of ``contracts/schemas/ingest-receipt``.

    ``storage_state`` can only be ``healthy`` or ``maintenance`` on a receipt: a receipt
    exists only because a transaction committed, so ``write_blocked`` and
    ``recovery_required`` are unrepresentable here by construction, exactly as the schema
    says.
    """
    return {
        "receipt": {
            "receipt_id": receipt.id,
            "request_id": receipt.request_id,
            "idempotency_key": receipt.idempotency_key,
            "payload_hash": receipt.payload_hash,
            "schema_version": receipt.schema_version,
            "status": status,
            "receipt_kind": receipt.receipt_kind,
            "run_id": receipt.run_id,
            "job_id": receipt.job_id,
            "lease_id": receipt.lease_id,
            "lease_epoch": receipt.lease_epoch,
            "committed_at": receipt.committed_at,
            "counts": _wire_counts(
                received=receipt.items_received,
                inserted=receipt.posts_inserted,
                deduplicated=receipt.posts_duplicate,
                quarantined=0,
                rejected=receipt.items_rejected,
                works_linked=receipt.works_linked,
                max_ingest_sequence=receipt.max_ingest_sequence,
            ),
            "accepted_items": [dict(item) for item in accepted_items],
            "checkpoint_ack": {
                "checkpoint_id": checkpoint.id,
                "checkpoint_sequence": checkpoint.sequence,
                "cursor_token": checkpoint.cursor_token,
                "cursor_state": checkpoint.cursor_state,
                "acked_through_ingest_sequence": checkpoint.acked_through_ingest_sequence,
                "items_ingested_total": checkpoint.items_ingested_total,
            },
            "receipt_hash": receipt.receipt_hash,
            "storage_state": "healthy",
            "warnings": [dict(warning) for warning in warnings],
        }
    }


def _replay_envelope(ctx: IngestContext, receipt: ReceiptRow) -> dict[str, Any]:
    """Re-render a stored receipt. Opens a read connection only -- never a write one."""
    with ctx.engine.connect() as connection:
        checkpoint = _checkpoint_by_id(ctx, connection, receipt.checkpoint_id)
    return _receipt_envelope(
        receipt,
        checkpoint,
        status="duplicate_replay",
        accepted_items=(),
        warnings=(),
    )


def _checkpoint_by_id(
    ctx: IngestContext, connection: Connection, checkpoint_id: str
) -> CheckpointRow:
    checkpoint = ctx.repository.checkpoint_by_id(connection, checkpoint_id)
    if checkpoint is None:  # pragma: no cover - unreachable while the FK holds
        raise IngestError(ErrorCode.INTERNAL, "Receipt trỏ tới checkpoint không tồn tại.")
    return checkpoint


# ------------------------------------------------------------------ ingest.submit_batch


def submit_batch(
    ctx: IngestContext,
    raw_batch: Mapping[str, Any],
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """``ingest.submit_batch`` -- ``TXN-ingest-batch``.

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**
    The response is assembled after that block returns, so no ACK can precede the commit
    (I02(a)). Posts, the checkpoint row and the receipt are written inside that one block
    and nowhere else, so no observer can see a checkpoint that points past durable data
    (I02(b)); the deferred foreign keys in revision ``0002`` make a partial write fail at
    the commit rather than be accepted.

    A replay returns *before* any write transaction is opened (I02(c)).
    """
    batch = _parse_batch(raw_batch)
    declared_hash = str(batch.payload_hash.root)
    computed_hash = compute_payload_hash(raw_batch)
    if declared_hash != computed_hash:
        raise _validation_error(
            "payload_hash không khớp nội dung lô.",
            violation_kind="payload_hash_mismatch",
        )

    idempotency_key = batch.idempotency_key
    _assert_writable(ctx, OperationId.INGEST_SUBMIT_BATCH)

    with ctx.engine.connect() as connection:
        stored = ctx.repository.find_receipt(
            connection, owner_id=ctx.owner_id, idempotency_key=idempotency_key
        )
    decision = classify(None if stored is None else stored.payload_hash, declared_hash)
    if decision is ReplayDecision.CONFLICT:
        assert stored is not None
        raise IngestError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Yêu cầu trùng khóa nhưng nội dung khác với lần đã ghi nhận.",
            details_safe={
                "idempotency_key": idempotency_key,
                "payload_hash_seen": declared_hash,
                "payload_hash_stored": stored.payload_hash,
            },
        )
    if decision is ReplayDecision.REPLAY:
        assert stored is not None
        return _replay_envelope(ctx, stored)

    lease_run_id = _check_lease(
        ctx,
        job_id=str(batch.job_id.root),
        lease_id=str(batch.lease_id.root),
        lease_epoch=batch.lease_epoch,
    )
    effective_run_id = (
        run_id or lease_run_id or (None if batch.run_id is None else str(batch.run_id.root))
    )
    if effective_run_id is None:
        raise IngestDependencyUnavailable(
            "run_id could not be resolved: no assignment port is wired and the batch "
            "carries no run_id (contracts/ports.yaml ingest.submit_batch)"
        )

    try:
        with ctx.engine.begin() as connection:
            return _commit_batch(
                ctx,
                connection,
                raw_batch=raw_batch,
                batch=batch,
                run_id=effective_run_id,
                declared_hash=declared_hash,
            )
    except IngestError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc) from exc


def _storage_write_failed(ctx: IngestContext, exc: Exception) -> IngestError:
    """Map a SQLite write failure onto ``STORAGE_WRITE_FAILED``.

    The transaction has rolled back, so nothing was persisted, nothing was ACKed and the
    cursor did not move -- which is exactly what the error code is required to mean
    (``contracts/errors.yaml``, SRC-PLAN §8.4). The driver message is deliberately not
    forwarded: an envelope may not carry SQL or internal table names.
    """
    if ctx.storage_guard is not None:
        ctx.storage_guard.record_write_failure()
    return IngestError(
        ErrorCode.STORAGE_WRITE_FAILED,
        "Không ghi được xuống kho dữ liệu; lô chưa được commit.",
        details_safe={"failure_class": type(exc).__name__},
        retry_after_ms=30_000,
    )


def _parse_batch(raw_batch: Mapping[str, Any]) -> IngestBatch:
    """Validate against ``contracts/schemas/ingest-batch.schema.json`` (generated model).

    Rejection happens here, before any connection is opened, so a schema-invalid batch
    cannot write a partial row -- the obligation the five ``neg-ingest-batch-*`` fixtures
    exist to check.
    """
    try:
        return IngestBatch.model_validate(dict(raw_batch))
    except ValidationError as exc:
        first = exc.errors()[0]
        pointer = "/" + "/".join(str(part) for part in first["loc"])
        raise _validation_error(
            "Lô ingest không hợp lệ theo hợp đồng wire.",
            violation_kind="schema_invalid",
            json_pointer=pointer,
        ) from exc


def _commit_batch(
    ctx: IngestContext,
    connection: Connection,
    *,
    raw_batch: Mapping[str, Any],
    batch: IngestBatch,
    run_id: str,
    declared_hash: str,
) -> dict[str, Any]:
    """The body of ``TXN-ingest-batch``. Runs inside one open transaction."""
    repository = ctx.repository

    # Re-check under the transaction: two concurrent calls with the same key must not both
    # proceed. The UNIQUE(owner_id, idempotency_key) index is the real guard; this read
    # turns the loser into a clean replay instead of an IntegrityError.
    stored = repository.find_receipt(
        connection, owner_id=ctx.owner_id, idempotency_key=batch.idempotency_key
    )
    if stored is not None:
        checkpoint = _checkpoint_by_id(ctx, connection, stored.checkpoint_id)
        return _receipt_envelope(
            stored, checkpoint, status="duplicate_replay", accepted_items=(), warnings=()
        )

    raw_items: list[Mapping[str, Any]] = list(raw_batch["items"])
    x_post_ids = [str(item["x_post_id"]) for item in raw_items]
    existing = repository.posts_by_x_post_id(
        connection, owner_id=ctx.owner_id, x_post_ids=x_post_ids
    )

    committed_at = _clamped_now(ctx, connection)
    receipt_id = ctx.new_id()
    checkpoint_id = ctx.new_id()
    sequence = repository.max_ingest_sequence(connection, owner_id=ctx.owner_id)

    accepted_items: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    inserted = 0
    deduplicated = 0
    max_allocated = 0

    for raw_item in raw_items:
        x_post_id = str(raw_item["x_post_id"])
        previous = existing.get(x_post_id)
        if previous is not None:
            deduplicated += 1
            observed = raw_item.get("source_deleted_observed_at")
            if observed is not None and previous.source_deleted_observed_at is None:
                repository.observe_source_deleted(
                    connection,
                    owner_id=ctx.owner_id,
                    x_post_id=x_post_id,
                    observed_at=str(observed),
                )
            accepted_items.append(
                {
                    "x_post_id": x_post_id,
                    "post_id": previous.id,
                    "outcome": "deduplicated",
                    # The ORIGINAL discovery time, not the time of this re-read: a
                    # duplicate must not look newly discovered (SRC-PLAN §9.1).
                    "discovered_at": previous.discovered_at,
                    "ingest_sequence": previous.ingest_sequence,
                    "target_ref": None,
                }
            )
            continue

        sequence += 1
        max_allocated = sequence
        inserted += 1
        post_id = ctx.new_id()
        target, conflict_reason = _resolve_target(
            ctx,
            connection,
            referenced_links=list(raw_item.get("referenced_links", [])),
        )
        if conflict_reason is not None:
            warnings.append(
                {
                    "code": ErrorCode.IDENTITY_CONFLICT.value,
                    "message_safe": (
                        "Định danh của mục này mâu thuẫn; mục được giữ lại để Owner xử lý."
                    ),
                    "x_post_id": x_post_id,
                }
            )
        thread_context = raw_item.get("thread_context") or {}
        author = raw_item["author"]
        repository.insert_post(
            connection,
            {
                "id": post_id,
                "owner_id": ctx.owner_id,
                "x_post_id": x_post_id,
                "author_handle": author["handle"],
                "author_display_name": author.get("display_name"),
                "author_x_user_id": author.get("x_user_id"),
                "url": raw_item["url"],
                "text": raw_item["text"],
                "lang": raw_item.get("lang"),
                "published_at": raw_item.get("published_at"),
                "discovered_at": committed_at,
                "ingest_sequence": sequence,
                "collected_at_client": raw_item.get("collected_at"),
                "discovered_by_run_id": run_id,
                "ingest_receipt_id": receipt_id,
                "thread_root_x_post_id": thread_context.get("thread_root_x_post_id"),
                "is_author_thread_member": int(
                    bool(thread_context.get("is_author_thread_member", False))
                ),
                "media_refs": json_text(raw_item.get("media_refs", [])),
                "referenced_links": json_text(raw_item.get("referenced_links", [])),
                "identity_resolution": (
                    "conflict"
                    if conflict_reason is not None
                    else ("pending" if target is None else target.identity_resolution)
                ),
                "source_snapshot_hash": compute_source_snapshot_hash(raw_item),
                "content_state": "present",
                "source_deleted_observed_at": raw_item.get("source_deleted_observed_at"),
            },
        )
        accepted_items.append(
            {
                "x_post_id": x_post_id,
                "post_id": post_id,
                "outcome": "inserted",
                "discovered_at": committed_at,
                "ingest_sequence": sequence,
                "target_ref": (
                    None if target is None else {"kind": target.kind, "key": target.key}
                ),
            }
        )

    previous_checkpoint = repository.latest_checkpoint(
        connection, owner_id=ctx.owner_id, run_id=run_id
    )
    previous_acked = (
        0 if previous_checkpoint is None else (previous_checkpoint.acked_through_ingest_sequence)
    )
    previous_total = 0 if previous_checkpoint is None else previous_checkpoint.items_ingested_total
    acked_through = max(previous_acked, max_allocated)
    proposal = raw_batch["client_checkpoint_proposal"]
    checkpoint = CheckpointRow(
        id=checkpoint_id,
        owner_id=ctx.owner_id,
        run_id=run_id,
        phase=str(proposal["phase"]),
        sequence=0 if previous_checkpoint is None else previous_checkpoint.sequence + 1,
        cursor_token=proposal.get("cursor_token"),
        cursor_state=str(proposal["cursor_state"]),
        acked_through_ingest_sequence=acked_through,
        items_ingested_total=previous_total + inserted,
        created_at=committed_at,
        created_by_receipt_id=receipt_id,
    )
    if previous_checkpoint is None:
        checkpoint = _with_sequence(checkpoint, 1)
    repository.insert_checkpoint(connection, checkpoint)

    counts = _wire_counts(
        received=len(raw_items),
        inserted=inserted,
        deduplicated=deduplicated,
        quarantined=0,
        rejected=0,
        works_linked=0,
        max_ingest_sequence=acked_through,
    )
    receipt = ReceiptRow(
        id=receipt_id,
        owner_id=ctx.owner_id,
        receipt_kind="batch_ingest",
        idempotency_key=batch.idempotency_key,
        request_id=str(batch.request_id.root),
        payload_hash=declared_hash,
        schema_version=str(batch.schema_version.root),
        run_id=run_id,
        job_id=str(batch.job_id.root),
        lease_id=str(batch.lease_id.root),
        lease_epoch=batch.lease_epoch,
        items_received=len(raw_items),
        posts_inserted=inserted,
        posts_duplicate=deduplicated,
        items_rejected=0,
        works_linked=0,
        checkpoint_id=checkpoint_id,
        max_ingest_sequence=acked_through,
        committed_at=committed_at,
        receipt_hash=compute_receipt_hash(
            idempotency_key=batch.idempotency_key,
            payload_hash=declared_hash,
            counts=counts,
            checkpoint_id=checkpoint_id,
            max_ingest_sequence=acked_through,
        ),
    )
    repository.insert_receipt(connection, receipt)
    return _receipt_envelope(
        receipt,
        checkpoint,
        status="committed",
        accepted_items=accepted_items,
        warnings=warnings,
    )


def _with_sequence(row: CheckpointRow, sequence: int) -> CheckpointRow:
    values = dict(vars(row))
    values["sequence"] = sequence
    return CheckpointRow(**values)


def _clamped_now(ctx: IngestContext, connection: Connection) -> str:
    """Server clock for ``discovered_at``/``committed_at``, clamped to stay monotonic.

    ``TXN-ingest-batch.clock_clamp`` (CR-PC04-03): if the server clock has moved backwards
    (NTP step, VM snapshot restore) the value is clamped to ``max(discovered_at) + 1 ms``.
    A backwards jump must not produce a post whose ``discovered_at`` falls before the left
    edge of an already-closed coverage window -- that is silent data loss, which I06
    forbids. The batch is never rejected for a clock jump: the data is not at fault.
    """
    now = ctx.now()
    previous = ctx.repository.max_discovered_at(connection, owner_id=ctx.owner_id)
    if previous is None:
        return format_timestamp(now)
    previous_moment = parse_timestamp(previous)
    if now <= previous_moment:
        return format_timestamp(previous_moment + timedelta(milliseconds=1))
    return format_timestamp(now)


# ------------------------------------------------------------- ingest.commit_checkpoint


def commit_checkpoint(
    ctx: IngestContext,
    raw_request: Mapping[str, Any],
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    """``ingest.commit_checkpoint`` -- ``TXN-checkpoint-only``.

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**

    This is the second and last legal way for a ``checkpoint`` row to become durable, and
    it is the narrow one: an empty page, the end of the feed, or the close of a collection
    segment. It writes exactly one ``checkpoint`` row and one ``ingest_receipt`` row, never
    a ``post``, and it never raises ``acked_through_ingest_sequence`` -- only
    ``TXN-ingest-batch`` may do that, and only up to a sequence it allocated itself. The
    guard below refuses a proposal that points past what is already acknowledged, which is
    counterexample 2 of I02 turned into something a test can measure.
    """
    request = _parse_checkpoint_only(raw_request)
    assignment_id = str(request.assignment_id.root)
    idempotency_key = checkpoint_only_idempotency_key(assignment_id, request.checkpoint_seq)

    _assert_writable(ctx, OperationId.INGEST_COMMIT_CHECKPOINT)

    payload_hash = compute_receipt_hash(
        idempotency_key=idempotency_key,
        payload_hash="sha256:" + "0" * 64,
        counts=_wire_counts(
            received=0,
            inserted=0,
            deduplicated=0,
            quarantined=0,
            rejected=0,
            works_linked=0,
            max_ingest_sequence=request.proposed_acked_through_ingest_sequence,
        ),
        checkpoint_id=str(request.cursor_token),
        max_ingest_sequence=request.proposed_acked_through_ingest_sequence,
    )

    with ctx.engine.connect() as connection:
        stored = ctx.repository.find_receipt(
            connection, owner_id=ctx.owner_id, idempotency_key=idempotency_key
        )
    decision = classify(None if stored is None else stored.payload_hash, payload_hash)
    if decision is ReplayDecision.CONFLICT:
        assert stored is not None
        raise IngestError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Cùng checkpoint_seq nhưng nội dung khác với lần đã ghi nhận.",
            details_safe={"idempotency_key": idempotency_key},
        )
    if decision is ReplayDecision.REPLAY:
        assert stored is not None
        return _replay_envelope(ctx, stored)

    lease_run_id = _check_lease(
        ctx,
        job_id=assignment_id,
        lease_id=str(request.lease_id.root),
        lease_epoch=request.lease_epoch,
    )
    effective_run_id = run_id or lease_run_id
    if effective_run_id is None:
        raise IngestDependencyUnavailable(
            "run_id could not be resolved for ingest.commit_checkpoint: no assignment port "
            "is wired and no run_id was supplied"
        )

    try:
        with ctx.engine.begin() as connection:
            return _commit_checkpoint_only(
                ctx,
                connection,
                request=request,
                run_id=effective_run_id,
                idempotency_key=idempotency_key,
                payload_hash=payload_hash,
            )
    except IngestError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc) from exc


def _parse_checkpoint_only(raw_request: Mapping[str, Any]) -> CheckpointOnlyRequest:
    """Validate against ``ingest-receipt.schema.json#/$defs/checkpoint_only_request``.

    ``contracts/ports.yaml`` describes an ``item_count: 0`` field on this request while the
    schema declares ``additionalProperties: false`` without one. The schema is the wire
    contract, so a body carrying ``item_count`` is rejected as an unknown field -- which
    satisfies the card's §7 obligation ("``item_count != 0`` is a ``VALIDATION_ERROR``")
    for every non-zero value and for zero alike. The divergence is CR-TC-ingest-03.
    """
    try:
        return CheckpointOnlyRequest.model_validate(dict(raw_request))
    except ValidationError as exc:
        first = exc.errors()[0]
        pointer = "/" + "/".join(str(part) for part in first["loc"])
        raise _validation_error(
            "Yêu cầu checkpoint-only không hợp lệ theo hợp đồng wire.",
            violation_kind="schema_invalid",
            json_pointer=pointer,
        ) from exc


def _commit_checkpoint_only(
    ctx: IngestContext,
    connection: Connection,
    *,
    request: CheckpointOnlyRequest,
    run_id: str,
    idempotency_key: str,
    payload_hash: str,
) -> dict[str, Any]:
    """The body of ``TXN-checkpoint-only``. Runs inside one open transaction."""
    repository = ctx.repository
    previous = repository.latest_checkpoint(connection, owner_id=ctx.owner_id, run_id=run_id)
    current_acked = 0 if previous is None else previous.acked_through_ingest_sequence
    current_sequence = 0 if previous is None else previous.sequence

    if request.checkpoint_seq <= current_sequence:
        raise _validation_error(
            "checkpoint_seq không được lùi hoặc lặp lại.",
            violation_kind="checkpoint_seq_regression",
        )
    if request.proposed_acked_through_ingest_sequence > current_acked:
        # The guard of R-01: a cursor may only reference data the server has already
        # committed. Everything else about this path is bookkeeping; this is the line that
        # keeps a checkpoint from ever pointing past durable posts.
        raise _validation_error(
            "Con trỏ đề xuất vượt quá mốc đã ACK; không ghi một phần nào.",
            violation_kind="acked_through_exceeds_committed",
        )

    committed_at = _clamped_now(ctx, connection)
    receipt_id = ctx.new_id()
    checkpoint_id = ctx.new_id()
    checkpoint = CheckpointRow(
        id=checkpoint_id,
        owner_id=ctx.owner_id,
        run_id=run_id,
        phase="collecting",
        sequence=request.checkpoint_seq,
        cursor_token=request.cursor_token,
        cursor_state=request.cursor_state.value,
        # UNCHANGED on purpose: this path never acknowledges new data.
        acked_through_ingest_sequence=current_acked,
        items_ingested_total=0 if previous is None else previous.items_ingested_total,
        created_at=committed_at,
        created_by_receipt_id=receipt_id,
    )
    repository.insert_checkpoint(connection, checkpoint)

    counts = _wire_counts(
        received=0,
        inserted=0,
        deduplicated=0,
        quarantined=0,
        rejected=0,
        works_linked=0,
        max_ingest_sequence=current_acked,
    )
    receipt = ReceiptRow(
        id=receipt_id,
        owner_id=ctx.owner_id,
        receipt_kind="checkpoint_only",
        idempotency_key=idempotency_key,
        request_id=str(request.request_id.root),
        payload_hash=payload_hash,
        schema_version=str(request.schema_version.root),
        run_id=run_id,
        job_id=str(request.assignment_id.root),
        lease_id=str(request.lease_id.root),
        lease_epoch=request.lease_epoch,
        items_received=0,
        posts_inserted=0,
        posts_duplicate=0,
        items_rejected=0,
        works_linked=0,
        checkpoint_id=checkpoint_id,
        max_ingest_sequence=current_acked,
        committed_at=committed_at,
        receipt_hash=compute_receipt_hash(
            idempotency_key=idempotency_key,
            payload_hash=payload_hash,
            counts=counts,
            checkpoint_id=checkpoint_id,
            max_ingest_sequence=current_acked,
        ),
    )
    repository.insert_receipt(connection, receipt)
    return _receipt_envelope(
        receipt, checkpoint, status="committed", accepted_items=(), warnings=()
    )


# ------------------------------------------------------------------ ingest.get_receipt


def get_receipt(ctx: IngestContext, *, idempotency_key: str) -> dict[str, Any]:
    """``ingest.get_receipt`` -- the mandatory lookup before any retry (SRC-PLAN §5.1).

    Read-only. Returns either the committed receipt or a ``not_committed`` answer, and the
    difference matters: ``not_committed`` is the server saying *definitely not*, which is a
    different thing from the client's *don't know* after a timeout. Only this answer makes
    it safe to resubmit.
    """
    with ctx.engine.connect() as connection:
        stored = ctx.repository.find_receipt(
            connection, owner_id=ctx.owner_id, idempotency_key=idempotency_key
        )
        if stored is None:
            return {
                "not_committed": {
                    "idempotency_key": idempotency_key,
                    "status": "not_committed",
                    "checked_at": format_timestamp(ctx.now()),
                    "safe_to_resubmit": True,
                }
            }
        checkpoint = _checkpoint_by_id(ctx, connection, stored.checkpoint_id)
    return _receipt_envelope(stored, checkpoint, status="committed", accepted_items=(), warnings=())


# --------------------------------------------------------------- ingest.get_checkpoint


def get_checkpoint(ctx: IngestContext, *, run_id: str) -> dict[str, Any]:
    """``ingest.get_checkpoint`` -- internal read for ``MOD-job-service``.

    Internal transport only (``contracts/ports.yaml``): it exists so the job service can
    build a resume payload without owning or touching the ``checkpoint`` table, which is
    ``MOD-ingest-service``'s alone (ruling R-01).
    """
    with ctx.engine.connect() as connection:
        checkpoint = ctx.repository.latest_checkpoint(
            connection, owner_id=ctx.owner_id, run_id=run_id
        )
    if checkpoint is None:
        raise IngestError(
            ErrorCode.NOT_FOUND,
            "Run chưa có checkpoint nào.",
            details_safe={"run_id": run_id},
        )
    return {
        "phase": checkpoint.phase,
        "cursor_token": checkpoint.cursor_token,
        "cursor_state": checkpoint.cursor_state,
        "acked_through_ingest_sequence": checkpoint.acked_through_ingest_sequence,
        "items_ingested_total": checkpoint.items_ingested_total,
        "checkpoint_sequence": checkpoint.sequence,
        "created_at": checkpoint.created_at,
    }
