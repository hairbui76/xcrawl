"""``MOD-tag-service`` — ``tag.rescan_corpus``: a separate command with a separate ledger.

The one sentence this module exists to make true
------------------------------------------------
*Re-scanning the corpus changes nothing that a report period changes.* ``time-and-tags.md`` §7
states it as five negative constraints, and O-7 measures it as five counts that must be
unchanged across the command:

    ``#coverage_window``, ``#report``, ``#first_announced_ledger``,
    ``#backfill_ledger[consumed_in_report_id IS NOT NULL]`` and ``#outbox_intent`` all
    unchanged; ``#rescan_ledger`` up by exactly 1.

The design decision that makes that testable rather than aspirational: **this module's SQL
touches one table.** Every statement below names ``rescan_ledger`` (plus one existence read of
``tag``), so the five counts cannot move — not because a reviewer checked, but because there is
no statement that could move them. :data:`FORBIDDEN_TABLES` is asserted structurally in
``tests/integration/test_pending_survives_cursor.py``.

Why rescan exists at all
------------------------
It is the escape hatch §6.2 points at. A subscription identity consumes its backfill exactly
once; an Owner who wants to dig further does *not* get it back by removing and re-adding the
tag (that is denied, with the reason text saying so) — they run this command. Keeping the two
ledgers separate is what lets "exactly once" stay true while still leaving a way to look back.

``tag.rescan_corpus`` does **not** enqueue analysis — ``CR-TC-BACKFILL-03``
--------------------------------------------------------------------------
``time-and-tags.md`` §7 rule 5 says rescan *may* call ``analysis.enqueue_tasks`` for matched
targets without a summary. ``contracts/modules.yaml`` does not agree: ``MOD-tag-service``'s
``outbound_operations`` are ``embedding.generate_vectors`` and
``embedding.get_active_generation`` only, and ``allowed_edges`` carries no
``MOD-tag-service → MOD-analysis-service`` row. Under ``default_deny`` that call is
``FORBIDDEN_EDGE``. Card §5 settles the precedence — the registry wins over prose — and card
§10 ``SG-EDGE`` makes adding the edge change control's job, not this card's. So this module
records the request and stops there; the enqueue half is reported as ``NOT_RUN`` and raised as
``CR-TC-BACKFILL-03`` rather than implemented against an edge that does not exist.

Idempotency — ``CR-TC-BACKFILL-04``
-----------------------------------
``contracts/ports.yaml`` requires ``tag.rescan_corpus`` to be idempotent on ``request_id``,
but ``ENT-rescan-ledger`` has no column to store one in, and inventing a column would put the
schema and the contract in disagreement (``tests/contract/test_schema_matches_entities.py``
asserts equality in both directions). The registry here is therefore **process-local**, the
same disposition ``CR-TC-ANALYSIS-04`` records for ``analysis.claim_task``. What *is* durable
is the property that matters more: ``ux_rescan_open`` = ``UNIQUE(owner_id, tag_id) WHERE state
IN ('requested','running')`` means one open rescan per tag, enforced by the database across
processes and restarts. A duplicate request answers ``IDEMPOTENCY_CONFLICT``.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine, text

from server.app.auth.middleware import require_edge

OWNER_MODULE: Final[str] = "MOD-tag-service"

_CROCKFORD32: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp, 80 bits of randomness, Crockford base32.

    Defined here rather than imported from ``server.app.report.coverage``:
    ``contracts/modules.yaml`` has no ``MOD-tag-service -> MOD-report-service`` edge, and an
    import in that direction is a dependency the registry does not grant (ENF-import-rule).
    Every package in this repository carries its own for the same reason.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


#: ``ENT-rescan-ledger.state``.
STATE_REQUESTED: Final[str] = "requested"
STATE_RUNNING: Final[str] = "running"
STATE_DONE: Final[str] = "done"
STATE_FAILED: Final[str] = "failed"

#: The two states ``ux_rescan_open`` covers.
OPEN_STATES: Final[tuple[str, ...]] = (STATE_REQUESTED, STATE_RUNNING)

#: ``ux_rescan_open`` — the durable half of idempotency (see the module docstring).
IX_OPEN: Final[str] = "ux_rescan_open"

#: The five tables ``time-and-tags.md`` §7 forbids this command to write. Named so a test can
#: assert the absence structurally instead of trusting the prose.
FORBIDDEN_TABLES: Final[frozenset[str]] = frozenset(
    {
        "coverage_window",
        "report",
        "report_item",
        "first_announced_ledger",
        "backfill_ledger",
        "outbox_intent",
    }
)

_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
}


class RescanError(Exception):
    """A refusal carrying one of ``tag.rescan_corpus``'s six contract error codes."""

    def __init__(self, code: ErrorCode, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.details_safe: dict[str, Any] = details

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The wire envelope of SRC-PLAN §5.1: never a transcript, key or cookie."""
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": str(self),
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
        }


class StorageGuardPort(Protocol):
    """The write gate from ``TC-storage-write-blocked-readiness``."""

    def assert_writable(self, operation_id: OperationId) -> None: ...

    def record_write_failure(self) -> str | None: ...


@dataclass(frozen=True)
class RescanRecord:
    """One ``rescan_ledger`` row."""

    id: str
    owner_id: str
    tag_id: str | None
    requested_at: str
    scope_from: str | None
    state: str
    consumed_report_id: str | None


@dataclass
class RescanContext:
    """Everything ``tag.rescan_corpus`` needs, injected rather than imported."""

    engine: Engine
    owner_id: str
    storage_guard: StorageGuardPort | None = None
    clock: Callable[[], datetime] | None = None
    id_factory: Callable[[], str] | None = None
    #: Process-local ``request_id`` → rescan id (``CR-TC-BACKFILL-04``).
    request_receipts: dict[str, str] = field(default_factory=dict)

    def now(self) -> datetime:
        return datetime.now(UTC) if self.clock is None else self.clock()

    def new_id(self) -> str:
        return new_ulid() if self.id_factory is None else self.id_factory()


_COLUMNS = "id, owner_id, tag_id, requested_at, scope_from, state, consumed_report_id"


def _record(row: Any) -> RescanRecord:
    return RescanRecord(
        id=row[0],
        owner_id=row[1],
        tag_id=row[2],
        requested_at=row[3],
        scope_from=row[4],
        state=row[5],
        consumed_report_id=row[6],
    )


def _format(moment: datetime) -> str:
    """RFC 3339 UTC with exactly three fractional digits (``time-and-tags.md`` §1.1)."""
    utc = moment.astimezone(UTC)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"


def get(connection: Connection, *, owner_id: str, rescan_id: str) -> RescanRecord | None:
    row = connection.execute(
        text(f"SELECT {_COLUMNS} FROM rescan_ledger WHERE owner_id = :owner_id AND id = :id"),
        {"owner_id": owner_id, "id": rescan_id},
    ).fetchone()
    return None if row is None else _record(row)


def open_for_tag(
    connection: Connection, *, owner_id: str, tag_id: str | None
) -> RescanRecord | None:
    """The open rescan of one tag, if any. ``tag_id IS NULL`` means "the whole corpus"."""
    clause = "tag_id IS NULL" if tag_id is None else "tag_id = :tag_id"
    params: dict[str, Any] = {"owner_id": owner_id}
    if tag_id is not None:
        params["tag_id"] = tag_id
    row = connection.execute(
        text(
            f"SELECT {_COLUMNS} FROM rescan_ledger WHERE owner_id = :owner_id AND {clause} "
            f"AND state IN ('{STATE_REQUESTED}', '{STATE_RUNNING}') LIMIT 1"
        ),
        params,
    ).fetchone()
    return None if row is None else _record(row)


def count(connection: Connection, *, owner_id: str) -> int:
    result = connection.execute(
        text("SELECT COUNT(*) FROM rescan_ledger WHERE owner_id = :owner_id"),
        {"owner_id": owner_id},
    )
    return int(result.scalar_one())


def request_rescan(
    ctx: RescanContext,
    *,
    tag_id: str | None,
    request_id: str,
    scope_from: str | None = None,
    caller_module: str,
) -> RescanRecord:
    """``tag.rescan_corpus`` — one ``BEGIN…COMMIT`` writing exactly one ``rescan_ledger`` row.

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**

    ``caller_module`` is checked against the registry first: ``MOD-web-ui`` is the only caller
    ``allowed_edges`` grants, and FE-11 / FE-12 / FE-30 forbid the collector, the analysis
    worker and the Telegram adapter respectively (denied cases NC-02 and NC-06 — there is no
    chat command that edits a subscription). That refusal is ``FORBIDDEN_EDGE`` per the R5-01
    boundary table, which is a different question from the HTTP "who are you" the router
    answers with ``UNAUTHORIZED``; choosing the wrong one of the two is itself a FAIL under
    card §10 ``SG-DENY``.
    """
    require_edge(OperationId.TAG_RESCAN_CORPUS, caller_module, edge_ref="FE-11/FE-12/FE-30")
    if not request_id:
        raise RescanError(
            ErrorCode.VALIDATION_ERROR,
            "request_id is required",
            operation_id=OperationId.TAG_RESCAN_CORPUS.value,
            field_path="request_id",
            violation_kind="required_missing",
        )
    if ctx.storage_guard is not None:
        ctx.storage_guard.assert_writable(OperationId.TAG_RESCAN_CORPUS)

    requested_at = _format(ctx.now())
    with ctx.engine.begin() as connection:
        previous = ctx.request_receipts.get(request_id)
        if previous is not None:
            existing = get(connection, owner_id=ctx.owner_id, rescan_id=previous)
            if existing is not None:
                return existing
        if tag_id is not None:
            known = connection.execute(
                text("SELECT 1 FROM tag WHERE owner_id = :owner_id AND id = :id"),
                {"owner_id": ctx.owner_id, "id": tag_id},
            ).fetchone()
            if known is None:
                raise RescanError(
                    ErrorCode.NOT_FOUND,
                    "tag does not exist",
                    resource_kind="tag",
                    operation_id=OperationId.TAG_RESCAN_CORPUS.value,
                )
        if open_for_tag(connection, owner_id=ctx.owner_id, tag_id=tag_id) is not None:
            raise RescanError(
                ErrorCode.IDEMPOTENCY_CONFLICT,
                "a rescan is already open for this tag",
                operation_id=OperationId.TAG_RESCAN_CORPUS.value,
                idempotency_key_kind="request_id",
            )
        rescan_id = ctx.new_id()
        connection.execute(
            text(
                "INSERT INTO rescan_ledger "
                "(id, owner_id, tag_id, requested_at, scope_from, state, consumed_report_id) "
                "VALUES (:id, :owner_id, :tag_id, :requested_at, :scope_from, :state, NULL)"
            ),
            {
                "id": rescan_id,
                "owner_id": ctx.owner_id,
                "tag_id": tag_id,
                "requested_at": requested_at,
                "scope_from": scope_from,
                "state": STATE_REQUESTED,
            },
        )
        ctx.request_receipts[request_id] = rescan_id
        return RescanRecord(
            id=rescan_id,
            owner_id=ctx.owner_id,
            tag_id=tag_id,
            requested_at=requested_at,
            scope_from=scope_from,
            state=STATE_REQUESTED,
            consumed_report_id=None,
        )


def advance(connection: Connection, *, owner_id: str, rescan_id: str, state: str) -> bool:
    """Move one rescan through ``requested → running → done | failed``.

    Writes ``rescan_ledger`` and nothing else. ``consumed_report_id`` stays NULL here: §7 rule
    4 forbids rescan from creating a ``report``, so the only way that column is ever set is by
    a later period choosing to carry the rescan's findings — a decision that belongs to the
    report builder, not to this command.
    """
    if state not in (STATE_RUNNING, STATE_DONE, STATE_FAILED):
        raise RescanError(
            ErrorCode.VALIDATION_ERROR,
            "state is not one of the contract values",
            field_path="state",
            violation_kind="enum_invalid",
        )
    result = connection.execute(
        text(
            "UPDATE rescan_ledger SET state = :state "
            "WHERE owner_id = :owner_id AND id = :id AND state != :done AND state != :failed"
        ),
        {
            "state": state,
            "owner_id": owner_id,
            "id": rescan_id,
            "done": STATE_DONE,
            "failed": STATE_FAILED,
        },
    )
    return bool(result.rowcount)
