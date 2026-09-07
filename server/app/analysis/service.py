"""``MOD-analysis-service`` -- the analysis task lifecycle.

Operations implemented here, named after their ids in ``contracts/ports.yaml``:

================================== ============================== =========================
operation id                       function                       transaction
================================== ============================== =========================
``analysis.enqueue_tasks``         :func:`enqueue_tasks`          ``TXN-analysis-enqueue``
``analysis.claim_task``            :func:`claim_task`             ``TXN-analysis-claim``
``analysis.get_task_input``        :func:`get_task_input`         none (read)
``analysis.heartbeat``             :func:`heartbeat`              lease extension only
``analysis.submit_result``         :func:`submit_result`          ``TXN-analysis-accept``
``analysis.report_attempt_unknown``:func:`report_attempt_unknown` ``TXN-analysis-unknown``
``analysis.request_reanalysis``    :func:`request_reanalysis`     ``TXN-analysis-reanalysis``
================================== ============================== =========================

Two server-side transitions have no port of their own because no actor triggers them --
:func:`reap_expired_leases` (T-AN-11) and :func:`auto_rerun_unknown_attempt` (T-AN-09 /
T-AN-10). They are internal scheduler steps, not operations, and are named as such.

The four properties everything here exists to hold
--------------------------------------------------
``I04``
    At most one valid result per ``(analysis key, generation)``, and **changing a tag never
    calls the model**. The second half is structural rather than defensive: a tag is not an
    input to :func:`server.app.analysis.key.analysis_key_from_inputs`, that function refuses
    the excluded names outright, and :func:`enqueue_tasks` skips any target whose key already
    has a valid row. Re-adding a tag therefore produces zero new generations, zero new
    attempts and zero provider calls -- the AC-06 oracle, measured by counting rows.
``I16``
    An attempt is never a result. There is exactly one function that writes ``analysis``
    (:func:`_commit_result`) and it is reachable only after both validation gates pass. No
    code path reads ``analysis_attempt`` and renders it as a result; the "has this been
    analysed?" question is answered by ``find_valid_by_key`` and by nothing else.
``I14``
    Unknown usage is ``NULL``, never ``0``. The generated ``Usage`` model already forces
    ``unknown = true`` to carry three nulls; :func:`_usage_columns` refuses the reverse
    (``unknown = false`` with a missing count) rather than substituting a zero.
``I10``
    A worker holding a stale lease commits nothing. Every mutation that a worker can reach
    calls :func:`_require_current_lease` first, and it distinguishes ``STALE_LEASE`` (an
    older epoch of a live lease) from ``WORKER_LEASE_EXPIRED`` (the lease is gone) because
    ruling R5-01 makes picking the wrong code a failure in its own right.

Cross-domain calls
------------------
This card owns none of settings, secrets, storage health, source content or the pending
ledger. Each is reached through a port, and each is optional at import time so a missing
sibling degrades honestly instead of being stubbed inside this package:

* :class:`ProviderConfigPort` (``MOD-settings-service``) -- ``ENT-provider-config.enabled``.
  ``contracts/ai/providers.yaml`` ships **both** Anthropic adapters ``enabled: false``
  (isolation ISO-03/ISO-05 unverified), so :func:`claim_task` hands out no task for a task
  type whose provider is disabled: with no enabled provider there is nothing a worker could
  legitimately do with a task except call a provider it may not call. With no port wired the
  same refusal applies -- an unwired provider registry is not an enabled one (CAP-P5, I13).
* :class:`SecretPort` (``MOD-secret-service``) -- ``secret.revoke_task_credential`` only,
  the single secret operation ``contracts/modules.yaml`` grants this module. It is called
  **after** the commit returns, never inside the transaction.
* :class:`StorageGuardPort` (``TC-storage-write-blocked-readiness``) -- ``assert_writable``
  before a transaction opens, ``record_write_failure`` when a write really fails.
* :class:`TaskInputPort` -- the committed source content behind a target. ``post`` and
  ``work_version`` belong to other modules, so this module does not read them directly; the
  repository here is scoped to five tables and no more.
* :class:`PendingLedgerPort` (``MOD-report-service``, ``TC-report-coverage-publish-cas``) --
  ``pending_item_ledger`` when an item exhausts its budget. Absent today, so
  :func:`_fail_task` reports ``pending_ledger_recorded: False`` instead of pretending.

Denied edges (``contracts/modules.yaml``): nothing here calls ``tag.*``, ``report.*`` or
``save.*`` (FE-12/FE-13/FE-14, denied case NC-02), nothing opens a network socket, and no
provider is ever invoked from the server -- ``ai.run_inference_task`` runs on the personal
machine inside ``MOD-analysis-worker``. The in-process edge check is :func:`require_edge`,
which answers ``FORBIDDEN_EDGE``; the HTTP who-are-you question is the router's and answers
``UNAUTHORIZED``.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from pydantic import ValidationError
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.models.analysis_result import AnalysisResult
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import AnalysisAttemptOutcome, AnalysisItemState
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError, OperationalError

from server.app.analysis.key import (
    TASK_TYPES,
    AnalysisKey,
    AnalysisKeyError,
    analysis_key_from_inputs,
    analysis_key_from_mapping,
    sha256_of,
)
from server.app.analysis.repository import (
    AnalysisRepository,
    AnalysisRow,
    AttemptRow,
    GenerationRow,
    LeaseRow,
    TaskRow,
    format_timestamp,
    json_text,
    new_ulid,
    parse_timestamp,
)
from server.app.auth.middleware import require_edge
from server.app.storage.guard import StorageRefused

# --------------------------------------------------------------------------------------
# Contract constants. Values quoted from contracts/retry-policy.yaml -- never re-derived.
# --------------------------------------------------------------------------------------

#: ``lease_ttl_analysis`` (900 s). Every inference timeout is smaller, so a hung provider
#: surfaces as ``unknown_attempt`` *before* the lease is swept (retry-policy RPC-09).
LEASE_TTL_ANALYSIS_SECONDS = 900
#: ``heartbeat_interval_analysis`` (60 s) and ``heartbeat_grace`` (30 s).
HEARTBEAT_INTERVAL_ANALYSIS_SECONDS = 60
HEARTBEAT_GRACE_SECONDS = 30
#: ``analysis_attempts_per_item`` (2) -- total tries per ``(analysis_key, generation)``, not
#: per worker. Changing worker does not refund it (T-AN-06 ``forbidden_vi``).
ANALYSIS_ATTEMPTS_PER_ITEM = 2
#: ``analysis_unknown_attempt_auto_rerun`` (1), which CONSUMES one unit of the budget above.
ANALYSIS_UNKNOWN_ATTEMPT_AUTO_RERUN = 1
#: ``ai_inference_timeout_{label,summary,direction_phrasing}``. Carried on the task input so
#: the worker uses the contract's number rather than one of its own.
AI_INFERENCE_TIMEOUT_SECONDS: dict[str, int] = {
    "label": 120,
    "summary": 300,
    "direction_phrasing": 180,
}

#: ``ENT-analysis-generation.reason`` -- the closed list of legal reanalysis triggers.
#: ``contracts/ai/tasks.yaml`` §reanalysis_triggers.forbidden puts a tag change, a provider
#: change and a new report period explicitly outside it. That omission IS REQ-AC06.
REANALYSIS_REASONS: frozenset[str] = frozenset(
    {"owner_reanalysis", "new_work_version", "prompt_version_change", "schema_version_change"}
)
#: ``contracts/ports.yaml`` spells the wire values ``manual`` / ``new_paper_version`` while
#: ``entities.yaml`` owns the stored enum. Both spellings are accepted on the wire and the
#: stored value is always the entity one (ruling R-03: entities.yaml is authoritative).
WIRE_REASON_ALIASES: dict[str, str] = {
    "manual": "owner_reanalysis",
    "new_paper_version": "new_work_version",
}

#: ``ENT-analysis.evidence_level``, ordered. ``full_text`` is unreachable at MVP -- no step
#: in SRC-SPEC §6.1 fetches one -- and a result claiming it must fail (tasks.yaml §3).
EVIDENCE_LEVEL_ORDER: tuple[str, ...] = ("post_only", "abstract", "full_text")

#: ``contracts/ai/tasks.yaml`` SV-06: a deliberately blunt block list, paired with (not
#: substituting for) the review rubric of ``contracts/ai/grounding.md`` §6.
FORBIDDEN_NOVELTY_PHRASES: tuple[str, ...] = (
    "phát hiện mới",
    "đột phá",
    "lần đầu tiên chứng minh",
    "hướng nghiên cứu mới",
    "breakthrough",
    "first to show",
    "novel discovery",
)

#: A failed write reaches this module at either of two layers -- SQLAlchemy wraps a driver
#: error, while a failure raised from a connection-level hook (how ``server/app/db/faults.py``
#: reproduces a full disk) arrives as the bare ``sqlite3`` exception. Both mean: the
#: transaction did not commit, so nothing may be reported as accepted.
WRITE_FAILURES: tuple[type[Exception], ...] = (OperationalError, IntegrityError, sqlite3.Error)

#: HTTP status per code, from the responses declared in ``contracts/http/openapi.yaml`` for
#: the six ``/v1/analysis/**`` paths. ``AI_OUTPUT_INVALID`` is 422 and ``WORKER_LEASE_EXPIRED``
#: is 412 there -- both are pinned by the document, not chosen here.
HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.AI_OUTPUT_INVALID: 422,
    ErrorCode.AI_ATTEMPT_UNCERTAIN: 422,
    ErrorCode.AI_PROVIDER_UNAVAILABLE: 503,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STALE_LEASE: 409,
    ErrorCode.WORKER_LEASE_EXPIRED: 412,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.RESTORE_UNVERIFIED: 503,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

#: ``details_safe_keys`` of ``contracts/errors.yaml`` for the codes this module raises.
#: errors.yaml: "Khóa lạ ⇒ producer tự từ chối, không gửi ra" -- so an unknown key raises
#: here rather than travelling to a client.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.AI_OUTPUT_INVALID: frozenset(
        {"task_id", "task_type", "attempt_number", "validation_failure_kind", "retry_after_ms"}
    ),
    ErrorCode.AI_ATTEMPT_UNCERTAIN: frozenset(
        {"task_id", "attempt_id", "attempt_number", "cost_uncertain", "last_known_phase"}
    ),
    ErrorCode.AI_PROVIDER_UNAVAILABLE: frozenset(
        {"task_id", "provider_name", "reason_code", "attempt_number", "retry_after_ms"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.CONFLICT: frozenset(
        {
            "resource_kind",
            "expected_predecessor_id",
            "current_predecessor_id",
            "attempt_number",
            "retry_after_ms",
        }
    ),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.STALE_LEASE: frozenset({"job_id", "lease_epoch_seen", "lease_epoch_current"}),
    ErrorCode.WORKER_LEASE_EXPIRED: frozenset(
        {"job_id", "lease_epoch_seen", "lease_epoch_current", "expired_at"}
    ),
    ErrorCode.RESTORE_UNVERIFIED: frozenset(
        {"restore_id", "snapshot_id", "storage_health", "pending_outbox_count"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}


class AnalysisError(Exception):
    """A contract error code plus the safe envelope fields it may be reported with.

    It never carries a transcript, a prompt, a model output fragment, a credential or a
    stack trace: ``contracts/errors.yaml`` §redaction and SRC-PLAN §5.1 forbid all of those
    in an envelope, and the only way to keep that guarantee is for the exception itself never
    to hold them. ``validation_failure_kind`` is a *category*, not the offending text.
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
        unknown = set(self.details_safe or {}) - DETAILS_SAFE_KEYS[code]
        if unknown:
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")

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


class AnalysisDependencyUnavailable(Exception):
    """A port this operation needs is not wired. Surfaces as ``INTERNAL``, never as a 4xx.

    Reporting a missing internal dependency as a client error would blame the worker for a
    deployment gap and would let broken wiring pass a negative test.
    """


# --------------------------------------------------------------------------------- ports


@dataclass(frozen=True)
class ProviderChoice:
    """What ``ENT-provider-config`` says about one task type."""

    task_type: str
    auth_family: str
    provider_name: str
    model_name: str
    enabled: bool


class ProviderConfigPort(Protocol):
    """Read-only view of ``MOD-settings-service``'s ``provider_config`` rows."""

    def provider_for(self, task_type: str) -> ProviderChoice | None: ...


class SecretPort(Protocol):
    """``secret.revoke_task_credential`` -- the one secret operation this module may call.

    ``secret.issue_task_credential`` is deliberately absent: that edge belongs to
    ``MOD-analysis-worker``, not to this service (``contracts/modules.yaml`` allowed_edges).
    What this module provides for it is :func:`verify_task_lease`, the check the secret
    service consults before issuing.
    """

    def revoke_task_credential(self, *, task_id: str, attempt_id: str, reason: str) -> None: ...


class StorageGuardPort(Protocol):
    """The write gate provided by ``server.app.storage.guard.StorageGuard``."""

    def assert_writable(self, operation_id: OperationId) -> None: ...

    def record_write_failure(self) -> str | None: ...


@dataclass(frozen=True)
class TaskSource:
    """One committed source handed to a worker (``contracts/ai/tasks.yaml`` §2 input)."""

    source_id: str
    kind: str
    text: str
    source_hash: str
    retrieved_at: str


class TaskInputPort(Protocol):
    """The committed source content behind a target.

    ``post`` and ``work_version`` belong to other modules. This module never reads them
    directly -- ``analysis.get_task_input`` is the only data path a worker has (B12), and it
    hands out committed rows through this seam.
    """

    def sources_for(self, *, target_key: str) -> Sequence[TaskSource]: ...


class PendingLedgerPort(Protocol):
    """``pending_item_ledger`` (``MOD-report-service``, PC04)."""

    def record_pending(self, *, target_key: str, reason: str) -> None: ...


class AdapterCallCounter(Protocol):
    """Counter of ``ai.run_inference_task`` calls, for the AC-06 oracle.

    The server never calls a provider -- inference runs on the personal machine inside
    ``MOD-analysis-worker``. This seam exists so a test can assert the count is unmoved by a
    tag edit without the assertion depending on a network probe.
    """

    @property
    def calls(self) -> int: ...


# ------------------------------------------------------------------------------- context


@dataclass(frozen=True)
class ClaimReceipt:
    """What a ``claim_request_id`` was answered with."""

    task_id: str | None
    lease_id: str | None
    lease_epoch: int | None
    payload: dict[str, Any]


@dataclass
class AnalysisContext:
    """Everything an analysis operation needs, injected rather than imported.

    ``clock`` and ``id_factory`` are parameters because the oracles in
    ``acceptance/fixtures/ai/**`` are about ordering and identity of rows, and a test that
    cannot pin either has to assert on wall-clock coincidences.

    ``claim_receipts`` and ``reanalysis_receipts`` are **process-local** idempotency
    registries. ``contracts/ports.yaml`` requires idempotency on ``claim_request_id`` and on
    ``request_id``, but neither ``ENT-analysis-task`` nor ``ENT-analysis-generation`` has a
    column to store the key in, and inventing one would put the schema and the contract in
    disagreement (``tests/contract/test_schema_matches_entities.py``). Reported as
    ``CR-TC-ANALYSIS-04``. What is durable regardless of this registry is the property that
    actually matters: no task gets two live leases (the ``WHERE state = 'pending'`` claim
    update plus ``ux_lease_job_epoch``), and no key gets two valid results
    (``ux_analysis_valid_key``).
    """

    engine: Engine
    owner_id: str
    repository: AnalysisRepository = field(default_factory=AnalysisRepository)
    provider_config: ProviderConfigPort | None = None
    secrets: SecretPort | None = None
    storage_guard: StorageGuardPort | None = None
    task_input: TaskInputPort | None = None
    pending_ledger: PendingLedgerPort | None = None
    run_id: str | None = None
    clock: Any = None
    id_factory: Any = None
    claim_receipts: dict[str, ClaimReceipt] = field(default_factory=dict)
    reanalysis_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)

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


@dataclass(frozen=True)
class TargetRequest:
    """One target ``analysis.enqueue_tasks`` is asked to queue work for.

    The caller supplies the source fingerprint because the caller is the module that just
    committed the sources (ingest) or just selected the target (report builder). It is
    computed with :func:`server.app.analysis.key.compute_source_fingerprint`, whose inputs
    are content hashes and nothing else -- no tag, no provider, no report id.
    """

    target_kind: str
    target_id: str
    task_type: str
    source_fingerprint: str
    prompt_version: str
    schema_version: str
    max_evidence_level: str = "post_only"


# ------------------------------------------------------------------------------- helpers

#: The one statement in this module that is not behind a repository method, because it
#: crosses two of them: the lease sweep needs the claim pointer and the generation id of
#: every running task in one pass.
_RUNNING_TASKS_SQL = text(
    "SELECT id, analysis_generation_id, claimed_lease_id FROM analysis_task "
    "WHERE owner_id = :owner_id AND state = 'running'"
)


def _validation_error(message: str, **details: Any) -> AnalysisError:
    return AnalysisError(ErrorCode.VALIDATION_ERROR, message, details_safe=details or None)


def _not_found(resource_kind: str, operation: OperationId) -> AnalysisError:
    return AnalysisError(
        ErrorCode.NOT_FOUND,
        "Không tìm thấy đối tượng cho yêu cầu này.",
        details_safe={"operation_id": operation.value, "resource_kind": resource_kind},
    )


def _assert_writable(ctx: AnalysisContext, operation_id: OperationId) -> None:
    """Ask the storage guard for permission BEFORE opening the transaction.

    A refusal carries the guard's own code -- ``STORAGE_WRITE_FAILED`` while write-blocked or
    in maintenance, ``RESTORE_UNVERIFIED`` while a restore is unreconciled (I15, T-AN-02
    ``forbidden_vi``: no claim while ``storage.health = recovery_required``). This module does
    not decide which state refuses what; that mapping belongs to
    ``contracts/state/storage.yaml`` and to the card that implements it.

    With no guard injected the gate does not run. That is *not* read as healthy: nothing is
    acknowledged on the strength of it, and a write that then fails for real still raises
    ``STORAGE_WRITE_FAILED`` from :func:`_storage_write_failed`.
    """
    guard = ctx.storage_guard
    if guard is None:
        return
    try:
        guard.assert_writable(operation_id)
    except StorageRefused as refusal:
        envelope: dict[str, Any] = refusal.envelope
        raise AnalysisError(
            ErrorCode(envelope["code"]),
            str(envelope["message_safe"]),
            details_safe=envelope.get("details_safe"),
            retry_after_ms=envelope.get("retry_after_ms"),
        ) from refusal


def _storage_write_failed(
    ctx: AnalysisContext, exc: Exception, operation: OperationId
) -> AnalysisError:
    """Map a SQLite write failure onto ``STORAGE_WRITE_FAILED``.

    The transaction has rolled back, so nothing was persisted and nothing was acknowledged --
    which is exactly what the code is required to mean (``contracts/errors.yaml``,
    SRC-PLAN §8.4). The driver message is deliberately not forwarded: an envelope may not
    carry SQL or internal table names.
    """
    if ctx.storage_guard is not None:
        ctx.storage_guard.record_write_failure()
    return AnalysisError(
        ErrorCode.STORAGE_WRITE_FAILED,
        "Không ghi được xuống kho dữ liệu; không có gì được commit.",
        details_safe={"failed_operation_id": operation.value, "retry_after_ms": 30_000},
        retry_after_ms=30_000,
    )


def _target_columns(target_kind: str, target_id: str) -> dict[str, Any]:
    if target_kind not in ("work", "post"):
        raise _validation_error(
            "target_kind phải là `work` hoặc `post`.",
            field_path="target_kind",
            violation_kind="enum_invalid",
        )
    return {
        "target_kind": target_kind,
        "target_work_id": target_id if target_kind == "work" else None,
        "target_post_id": target_id if target_kind == "post" else None,
        "target_key": f"{target_kind}:{target_id}",
    }


def _lease_expired(lease: LeaseRow, now: datetime) -> bool:
    """T-AN-11: expiry is ``now > expires_at + heartbeat_grace``, not ``now > expires_at``.

    The grace exists so one missed heartbeat -- a GC pause, a flaky home network -- does not
    take a task away from a worker that is still alive (retry-policy ``heartbeat_grace``).
    """
    deadline = parse_timestamp(lease.expires_at) + timedelta(seconds=HEARTBEAT_GRACE_SECONDS)
    return now > deadline


def _require_current_lease(
    ctx: AnalysisContext,
    connection: Connection,
    *,
    task: TaskRow,
    lease_id: str,
    lease_epoch: int,
    now: datetime,
    allow_expired: bool = False,
) -> LeaseRow:
    """The single gate every worker mutation passes (I10).

    The two codes are kept apart because ruling R5-01 makes choosing the wrong one a failure
    on its own:

    ``STALE_LEASE``
        The caller presents a lease or epoch that is not the current one -- someone else
        holds the task now, or the caller is replaying an older claim.
    ``WORKER_LEASE_EXPIRED``
        The caller's own lease is the current one but it has run out (or was revoked). The
        work may well have happened; what is gone is the right to commit it.

    ``allow_expired`` is set by :func:`report_attempt_unknown` alone. That operation exists
    *because* the holder stopped responding, so demanding a live lease from it would make the
    one honest report of an unknown outcome impossible to file.
    """
    lease = ctx.repository.lease_by_id(connection, lease_id)
    current_epoch = ctx.repository.max_lease_epoch(
        connection, owner_id=ctx.owner_id, job_id=task.id
    )
    if lease is None or lease.job_id != task.id or lease.owner_id != ctx.owner_id:
        raise AnalysisError(
            ErrorCode.STALE_LEASE,
            "Lease không thuộc task này.",
            details_safe={
                "job_id": task.id,
                "lease_epoch_seen": lease_epoch,
                "lease_epoch_current": current_epoch,
            },
        )
    if lease.lease_epoch != lease_epoch or lease.lease_epoch != current_epoch:
        raise AnalysisError(
            ErrorCode.STALE_LEASE,
            "Lease epoch cũ hơn epoch hiện hành; không có dữ liệu nào thay đổi.",
            details_safe={
                "job_id": task.id,
                "lease_epoch_seen": lease_epoch,
                "lease_epoch_current": current_epoch,
            },
        )
    if lease.state in ("revoked", "expired", "released") or _lease_expired(lease, now):
        if allow_expired and lease.state != "revoked":
            return lease
        raise AnalysisError(
            ErrorCode.WORKER_LEASE_EXPIRED,
            "Lease đã hết hiệu lực; kết quả của lượt này không được chấp nhận.",
            details_safe={
                "job_id": task.id,
                "lease_epoch_seen": lease_epoch,
                "lease_epoch_current": current_epoch,
                "expired_at": lease.expires_at,
            },
        )
    return lease


def _require_task(
    ctx: AnalysisContext, connection: Connection, task_id: str, operation: OperationId
) -> TaskRow:
    task = ctx.repository.task_by_id(connection, task_id)
    if task is None or task.owner_id != ctx.owner_id:
        raise _not_found("analysis_task", operation)
    return task


def _open_attempt(
    ctx: AnalysisContext,
    connection: Connection,
    *,
    generation_id: str,
    lease_id: str,
    started_at: str,
) -> AttemptRow:
    """Record the start of a try, at the only moment the server can be sure it began.

    The row is opened as ``timeout_unknown`` with ``cost_uncertain = 1``. That is not a
    placeholder, it is the truth: from this instant until an outcome is reported, the server
    does not know whether the model ran, and SRC-PLAN §10 forbids claiming that no cost was
    incurred for something nobody knows. A worker that dies here leaves exactly the row
    ``acceptance/fixtures/ai/i-crash-after-provider-completion.json`` expects, without any
    recovery code having to reconstruct it.

    ``started_at`` is the **server** clock (``ENT-analysis-attempt.started_at``): a worker's
    clock is not evidence about when the server handed out the work.
    """
    attempt = AttemptRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        analysis_generation_id=generation_id,
        attempt_number=ctx.repository.next_attempt_number(
            connection, owner_id=ctx.owner_id, analysis_generation_id=generation_id
        ),
        outcome=AnalysisAttemptOutcome.TIMEOUT_UNKNOWN.value,
        error_code=ErrorCode.AI_ATTEMPT_UNCERTAIN.value,
        started_at=started_at,
        ended_at=None,
        worker_lease_id=lease_id,
        cost_uncertain=True,
    )
    ctx.repository.insert_attempt(connection, attempt)
    return attempt


def _current_attempt(
    ctx: AnalysisContext, connection: Connection, *, generation_id: str
) -> AttemptRow | None:
    attempts = ctx.repository.attempts_for_generation(
        connection, owner_id=ctx.owner_id, analysis_generation_id=generation_id
    )
    return attempts[-1] if attempts else None


# ------------------------------------------------------------------ analysis.enqueue_tasks


def enqueue_tasks(
    ctx: AnalysisContext,
    targets: Sequence[TargetRequest],
    *,
    caller_module: str,
) -> dict[str, Any]:
    """``analysis.enqueue_tasks`` -- ``TXN-analysis-enqueue``.

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**

    This is where REQ-AC06 is decided. For every target the key is built from the seven
    contract components, and a target whose key already has a ``valid`` row is *skipped*: no
    generation row, no task row, no attempt, and therefore no provider call. Removing and
    re-adding a tag changes none of the seven components, so the same targets come back with
    the same keys and every one of them is skipped. The oracle is arithmetic --
    ``COUNT(analysis_generation)`` and ``COUNT(analysis_attempt)`` unchanged, provider call
    counter delta 0 (``ENT-analysis-generation.ac06_oracle``).

    ``caller_module`` is checked against the module registry: ``MOD-ingest-service`` and
    ``MOD-report-service`` may call this, ``MOD-x-collector`` may not (FE-07, B12/AMD-B12 --
    a worker never receives uncommitted data). The refusal is ``FORBIDDEN_EDGE`` because it
    is an in-process call across an edge that is not in ``allowed_edges``; the transport is
    ``internal`` and there is no HTTP path to it at all.
    """
    require_edge(OperationId.ANALYSIS_ENQUEUE_TASKS, caller_module, edge_ref="FE-07")
    _assert_writable(ctx, OperationId.ANALYSIS_ENQUEUE_TASKS)
    for target in targets:
        if target.task_type not in TASK_TYPES:
            raise _validation_error(
                "task_type không thuộc ba giá trị của hợp đồng.",
                field_path="task_type",
                violation_kind="enum_invalid",
            )
    try:
        with ctx.engine.begin() as connection:
            return _enqueue(ctx, connection, targets)
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_ENQUEUE_TASKS) from exc


def _enqueue(
    ctx: AnalysisContext, connection: Connection, targets: Sequence[TargetRequest]
) -> dict[str, Any]:
    """Body of ``TXN-analysis-enqueue``. Runs inside one open transaction."""
    created: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    enqueued_at = format_timestamp(ctx.now())

    for target in targets:
        columns = _target_columns(target.target_kind, target.target_id)
        target_key = str(columns["target_key"])
        generation_number = max(
            1,
            ctx.repository.max_generation_number(
                connection,
                owner_id=ctx.owner_id,
                target_key=target_key,
                task_type=target.task_type,
            ),
        )
        key = analysis_key_from_inputs(
            owner_id=ctx.owner_id,
            target_key=target_key,
            task_type=target.task_type,
            source_fingerprint=target.source_fingerprint,
            prompt_version=target.prompt_version,
            schema_version=target.schema_version,
            generation_number=generation_number,
        )
        if _valid_result_for(ctx, connection, key) is not None:
            # REQ-AC06 / B07 / D25: a key that already has a valid result is not re-queued.
            skipped.append({"target_key": target_key, "reason": "already_valid"})
            continue

        generation = ctx.repository.find_generation(
            connection,
            owner_id=ctx.owner_id,
            target_key=target_key,
            task_type=target.task_type,
            generation_number=generation_number,
        )
        if generation is None:
            generation = GenerationRow(
                id=ctx.new_id(),
                target_key=target_key,
                task_type=target.task_type,
                generation_number=generation_number,
                reason="initial",
                requested_at=enqueued_at,
                requested_by="system_pipeline",
                owner_id=ctx.owner_id,
                target_kind=str(columns["target_kind"]),
                target_work_id=columns["target_work_id"],
                target_post_id=columns["target_post_id"],
            )
            ctx.repository.insert_generation(connection, generation)

        open_task = ctx.repository.open_task_for_generation(
            connection, owner_id=ctx.owner_id, analysis_generation_id=generation.id
        )
        if open_task is not None:
            # `ux_analysis_task_open` allows one open task per generation, and the
            # idempotency key of this operation is the analysis key itself: the same key
            # must not produce a duplicate queue entry (contracts/ports.yaml).
            skipped.append(
                {
                    "target_key": target_key,
                    "reason": "already_queued",
                    "task_id": open_task.id,
                }
            )
            continue

        task = TaskRow(
            id=ctx.new_id(),
            owner_id=ctx.owner_id,
            analysis_generation_id=generation.id,
            target_key=target_key,
            task_type=target.task_type,
            state=AnalysisItemState.PENDING.value,
            claimed_by_worker_identity=None,
            claimed_lease_id=None,
            claimed_at=None,
            enqueued_at=enqueued_at,
            attempt_budget_remaining=ANALYSIS_ATTEMPTS_PER_ITEM,
        )
        ctx.repository.insert_task(connection, task)
        created.append(
            {
                "task_id": task.id,
                "target_key": target_key,
                "task_type": target.task_type,
                "analysis_key": key.as_dict(),
                "generation_number": generation_number,
            }
        )
    return {"created": created, "skipped": skipped}


def _valid_result_for(
    ctx: AnalysisContext, connection: Connection, key: AnalysisKey
) -> AnalysisRow | None:
    return ctx.repository.find_valid_by_key(connection, **key.as_dict())


# --------------------------------------------------------------------- analysis.claim_task


def claim_task(
    ctx: AnalysisContext,
    *,
    worker_identity: str,
    claim_request_id: str,
    task_types: Sequence[str] = (),
    run_id: str | None = None,
) -> dict[str, Any]:
    """``analysis.claim_task`` -- ``TXN-analysis-claim`` (T-AN-02).

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.** The
    lease row, the task's claim pointers and the opening ``analysis_attempt`` row are written
    inside it and nowhere else, so no observer can see a claimed task without its lease or an
    attempt without a claim.

    Three refusals before any row is touched:

    * storage must be writable and not ``recovery_required`` (I15) -- via the guard;
    * the worker must declare a capability for a task type whose ``provider_config`` is
      **enabled**. Both Anthropic adapters ship ``enabled: false``
      (``contracts/ai/providers.yaml``, isolation unverified), so today this hands out
      nothing: dispatching a task whose only possible next step is a call the Owner has not
      enabled would be handing out an instruction to break the contract. An unwired provider
      registry counts as not-enabled -- an undetermined state is never converted into a good
      one (CAP-P5, I13);
    * a run id must be available. ``ENT-assignment-lease.run_id`` is NOT NULL and an analysis
      claim is not scoped to a collector run; rather than invent a value this refuses with an
      internal-dependency error (``CR-TC-ANALYSIS-02``).

    Returns ``{"task": None}`` when nothing is claimable. That is a normal answer, not an
    error: an empty queue and a disabled provider both mean "no work for you right now".
    """
    receipt = ctx.claim_receipts.get(claim_request_id)
    if receipt is not None:
        # contracts/ports.yaml: "Cùng claim_request_id trả cùng task; không cấp hai lease cho
        # một task." See AnalysisContext for why this registry is process-local.
        return receipt.payload

    _assert_writable(ctx, OperationId.ANALYSIS_CLAIM_TASK)
    effective_run_id = run_id or ctx.run_id
    enabled = [t for t in (task_types or sorted(TASK_TYPES)) if _provider_enabled(ctx, t)]
    if not enabled:
        payload: dict[str, Any] = {"task": None, "reason": "no_enabled_provider"}
        ctx.claim_receipts[claim_request_id] = ClaimReceipt(None, None, None, payload)
        return payload
    if effective_run_id is None:
        raise AnalysisDependencyUnavailable(
            "run_id could not be resolved for analysis.claim_task: ENT-assignment-lease.run_id "
            "is NOT NULL and no run id is wired (CR-TC-ANALYSIS-02). The service refuses to "
            "invent one."
        )

    try:
        with ctx.engine.begin() as connection:
            payload = _claim(
                ctx,
                connection,
                worker_identity=worker_identity,
                task_types=enabled,
                run_id=effective_run_id,
            )
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_CLAIM_TASK) from exc

    ctx.claim_receipts[claim_request_id] = ClaimReceipt(
        task_id=(payload.get("task") or {}).get("task_id"),
        lease_id=(payload.get("task") or {}).get("lease_id"),
        lease_epoch=(payload.get("task") or {}).get("lease_epoch"),
        payload=payload,
    )
    return payload


def _provider_enabled(ctx: AnalysisContext, task_type: str) -> bool:
    if ctx.provider_config is None:
        return False
    choice = ctx.provider_config.provider_for(task_type)
    return choice is not None and choice.enabled


def _claim(
    ctx: AnalysisContext,
    connection: Connection,
    *,
    worker_identity: str,
    task_types: Sequence[str],
    run_id: str,
) -> dict[str, Any]:
    """Body of ``TXN-analysis-claim``. Runs inside one open transaction."""
    task = ctx.repository.next_pending_task(
        connection, owner_id=ctx.owner_id, task_types=task_types
    )
    if task is None:
        return {"task": None, "reason": "queue_empty"}

    now = ctx.now()
    claimed_at = format_timestamp(now)
    lease = LeaseRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        run_id=run_id,
        job_id=task.id,
        worker_identity=worker_identity,
        # epoch + 1, never a reused number: `ux_lease_job_epoch` makes the monotonicity a
        # database fact, so "is this the current holder" is a lookup and not a judgement.
        lease_epoch=ctx.repository.max_lease_epoch(
            connection, owner_id=ctx.owner_id, job_id=task.id
        )
        + 1,
        expires_at=format_timestamp(now + timedelta(seconds=LEASE_TTL_ANALYSIS_SECONDS)),
        state="held",
    )
    ctx.repository.insert_lease(connection, lease)
    updated = ctx.repository.mark_task_running(
        connection,
        task_id=task.id,
        worker_identity=worker_identity,
        lease_id=lease.id,
        claimed_at=claimed_at,
    )
    if updated != 1:
        # Another worker won the race between the read and this update. Nothing has been
        # handed out, so the honest answer is "no task", not an error the caller must parse.
        raise AnalysisError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Task đã được worker khác nhận.",
            details_safe={"idempotency_key": task.id},
        )
    attempt = _open_attempt(
        ctx,
        connection,
        generation_id=task.analysis_generation_id,
        lease_id=lease.id,
        started_at=claimed_at,
    )
    generation = ctx.repository.generation_by_id(connection, task.analysis_generation_id)
    assert generation is not None  # FK guarantees it; asserted so a None cannot slip past
    return {
        "task": {
            "task_id": task.id,
            "task_type": task.task_type,
            "target_key": task.target_key,
            "analysis_generation_id": generation.id,
            "generation_number": generation.generation_number,
            "attempt_id": attempt.id,
            "attempt_number": attempt.attempt_number,
            "lease_id": lease.id,
            "lease_epoch": lease.lease_epoch,
            "lease_expires_at": lease.expires_at,
            "heartbeat_interval_seconds": HEARTBEAT_INTERVAL_ANALYSIS_SECONDS,
            "inference_timeout_seconds": AI_INFERENCE_TIMEOUT_SECONDS[task.task_type],
        }
    }


# ----------------------------------------------------------------- analysis.get_task_input


def get_task_input(
    ctx: AnalysisContext, *, task_id: str, lease_id: str, lease_epoch: int
) -> dict[str, Any]:
    """``analysis.get_task_input`` -- the only data path a worker has (B12). Read-only.

    The source content is returned as **data with an explicit boundary**, never as
    instructions (SRC-SPEC §11.4, I11): each source keeps its own ``source_id`` and hash, and
    ``input_source_ids`` is the closed set every citation must fall inside (SV-02).

    ``max_evidence_level`` is computed by the **server** from the sources actually present
    (``contracts/ai/tasks.yaml`` §3), not declared by the model and not declared by the
    worker. A worker that claims a higher level than the one returned here fails SV-04.
    """
    if ctx.task_input is None:
        raise AnalysisDependencyUnavailable(
            "no TaskInputPort is wired: `post` and `work_version` belong to other modules and "
            "this service does not read them directly"
        )
    now = ctx.now()
    with ctx.engine.connect() as connection:
        task = _require_task(ctx, connection, task_id, OperationId.ANALYSIS_GET_TASK_INPUT)
        _require_current_lease(
            ctx, connection, task=task, lease_id=lease_id, lease_epoch=lease_epoch, now=now
        )
        generation = ctx.repository.generation_by_id(connection, task.analysis_generation_id)
        assert generation is not None
    sources = list(ctx.task_input.sources_for(target_key=task.target_key))
    return {
        "task_id": task.id,
        "task_type": task.task_type,
        "target_ref": {
            "kind": generation.target_kind,
            "id": generation.target_work_id or generation.target_post_id,
            "target_key": generation.target_key,
        },
        "sources": [
            {
                "source_id": source.source_id,
                "kind": source.kind,
                "text": source.text,
                "source_hash": source.source_hash,
                "retrieved_at": source.retrieved_at,
            }
            for source in sources
        ],
        "input_source_ids": [source.source_id for source in sources],
        "max_evidence_level": max_evidence_level(sources),
        "inference_timeout_seconds": AI_INFERENCE_TIMEOUT_SECONDS[task.task_type],
    }


def max_evidence_level(sources: Iterable[TaskSource]) -> str:
    """``contracts/ai/tasks.yaml`` §evidence_level_ceiling, computed from the sources present.

    ``full_text`` is never returned: no step in SRC-SPEC §6.1 fetches a full text, so the
    ceiling cannot legitimately reach it at MVP and a result claiming it must fail SV-04.
    The enum member exists so that adding a full-text source later needs no migration.
    """
    kinds = {source.kind for source in sources}
    return "abstract" if "work_version" in kinds else "post_only"


# ---------------------------------------------------------------------- analysis.heartbeat


def heartbeat(
    ctx: AnalysisContext, *, task_id: str, lease_id: str, lease_epoch: int
) -> dict[str, Any]:
    """``analysis.heartbeat`` -- extend the lease. Writes no result (T-AN-02 side effects).

    A heartbeat can only ever move ``expires_at`` forward on the lease the caller already
    holds. It cannot re-open a lease that expired, cannot change the epoch, and cannot alter
    the task state -- so a worker cannot heartbeat its way back into a task the server has
    already taken away.
    """
    now = ctx.now()
    try:
        with ctx.engine.begin() as connection:
            task = _require_task(ctx, connection, task_id, OperationId.ANALYSIS_HEARTBEAT)
            lease = _require_current_lease(
                ctx, connection, task=task, lease_id=lease_id, lease_epoch=lease_epoch, now=now
            )
            expires_at = format_timestamp(now + timedelta(seconds=LEASE_TTL_ANALYSIS_SECONDS))
            ctx.repository.extend_lease(connection, lease_id=lease.id, expires_at=expires_at)
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_HEARTBEAT) from exc
    return {
        "task_id": task_id,
        "lease_id": lease_id,
        "lease_epoch": lease_epoch,
        "lease_expires_at": expires_at,
        "cancel_requested": False,
    }


# ------------------------------------------------------------------ analysis.submit_result


def submit_result(
    ctx: AnalysisContext,
    *,
    task_id: str,
    lease_id: str,
    lease_epoch: int,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    """``analysis.submit_result`` -- ``TXN-analysis-accept`` (T-AN-03).

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block in**
    :func:`_commit_result`. The ``analysis`` row, the closing ``analysis_attempt`` row, the
    task's terminal state and the lease release are written inside that one block; the
    response is assembled after it returns, so no acknowledgement can precede the commit.

    Four gates, in the order ``contracts/ai/tasks.yaml`` §validation_pipeline fixes them, and
    a result reaches ``valid`` only after **all** of them:

    1. the envelope is well formed (transport-level; a malformed request is
       ``VALIDATION_ERROR``, not an accusation against the model);
    2. schema validation against ``analysis-result.schema.json`` -- re-run here even though
       the adapter already ran it, because the server is the authority and the worker only
       *proposes* a result (SRC-PLAN §6.1);
    3. semantic validation SV-01..SV-07, which JSON Schema cannot express. "Valid JSON" is
       explicitly not the whole contract (``forbidden_transitions``: ``running -> valid``
       while only the schema passed is a forbidden transition);
    4. commit.

    Idempotency is on ``analysis_key + attempt_id``. A replay with the same payload returns
    the stored receipt without opening a write transaction; the same key with a *different*
    payload is ``IDEMPOTENCY_CONFLICT`` and the committed row is never overwritten (fixture
    ``j``, events 2 and 3).
    """
    now = ctx.now()
    document = _parse_result(result)
    try:
        key = analysis_key_from_mapping(document.analysis_key.model_dump(mode="json"))
    except AnalysisKeyError as exc:
        raise AnalysisError(
            ErrorCode.AI_OUTPUT_INVALID,
            "analysis_key trong kết quả không đúng hình dạng hợp đồng.",
            details_safe={"validation_failure_kind": "analysis_key_mismatch"},
        ) from exc
    payload = document.model_dump(mode="json")
    payload_hash = sha256_of(payload)

    with ctx.engine.connect() as connection:
        task = _require_task(ctx, connection, task_id, OperationId.ANALYSIS_SUBMIT_RESULT)
        stored = _valid_result_for(ctx, connection, key)
        if stored is None:
            generation = ctx.repository.generation_by_id(connection, task.analysis_generation_id)
            attempt = ctx.repository.attempt_by_id(connection, str(document.attempt_id.root))
            _require_current_lease(
                ctx,
                connection,
                task=task,
                lease_id=lease_id,
                lease_epoch=lease_epoch,
                now=now,
            )
    if stored is not None:
        if stored.payload_hash == payload_hash:
            # Lost ACK: return the receipt that already exists and write nothing.
            return _result_envelope(stored, status="duplicate_replay")
        raise AnalysisError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Cùng analysis_key nhưng nội dung khác với kết quả đã commit.",
            details_safe={
                "idempotency_key": key.digest(),
                "payload_hash_seen": payload_hash,
                "payload_hash_stored": stored.payload_hash,
            },
        )
    if generation is None:  # pragma: no cover - the FK makes this unreachable
        raise _not_found("analysis_generation", OperationId.ANALYSIS_SUBMIT_RESULT)
    if attempt is None or attempt.analysis_generation_id != generation.id:
        # ``analysis.accepted_from_attempt_id`` must point at the attempt that produced the
        # result. ``0002b`` created ``analysis`` without that REFERENCES clause -- the table
        # did not exist yet (CR-TC-ANALYSIS-03) -- so the check is made here instead.
        raise _validation_error(
            "attempt_id không thuộc generation của task này.",
            field_path="attempt_id",
            violation_kind="foreign_key_missing",
        )

    # Gate 3, run on the read snapshot. A rejection has its own durable consequences
    # (T-AN-04: the attempt is closed `schema_invalid`, the budget is spent, the task waits
    # or fails) and those must SURVIVE, so they are written by their own transaction rather
    # than rolled back together with the insert that never happened.
    failure_kind = _semantic_validation(
        ctx, task=task, generation=generation, document=document, key=key
    )
    if failure_kind is not None:
        _record_rejection(ctx, task=task, attempt=attempt, lease_id=lease_id, now=now)
        raise _ai_output_invalid(failure_kind, task, attempt)

    _assert_writable(ctx, OperationId.ANALYSIS_SUBMIT_RESULT)
    try:
        with ctx.engine.begin() as connection:
            envelope = _commit_result(
                ctx,
                connection,
                task=_require_task(ctx, connection, task_id, OperationId.ANALYSIS_SUBMIT_RESULT),
                generation=generation,
                attempt=attempt,
                document=document,
                key=key,
                payload=payload,
                payload_hash=payload_hash,
                lease_id=lease_id,
                lease_epoch=lease_epoch,
                now=now,
            )
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_SUBMIT_RESULT) from exc
    # Only after the COMMIT returned. A rejected result leaves the credential alone: the task
    # still has budget and the next attempt needs it. Revoking on the failure path would turn
    # one bad model output into a task that can never be retried.
    _revoke_credential(ctx, task_id=task.id, attempt_id=str(document.attempt_id.root))
    return envelope


def _parse_result(result: Mapping[str, Any]) -> AnalysisResult:
    """Gate 2 -- validate against ``contracts/schemas/analysis-result.schema.json``.

    A schema failure is ``AI_OUTPUT_INVALID`` and not ``VALIDATION_ERROR``: the model
    produced something the contract does not accept, which is an *item* level fact with a
    retry budget, not a malformed HTTP request. The JSON pointer of the first failure is
    reported as a ``validation_failure_kind`` category; the offending value is not, because
    an envelope may not carry model output (errors.yaml §redaction).
    """
    try:
        return AnalysisResult.model_validate(dict(result))
    except ValidationError as exc:
        raise AnalysisError(
            ErrorCode.AI_OUTPUT_INVALID,
            "Kết quả không hợp lệ theo analysis-result schema.",
            details_safe={"validation_failure_kind": "schema_invalid"},
        ) from exc


def _record_rejection(
    ctx: AnalysisContext,
    *,
    task: TaskRow,
    attempt: AttemptRow,
    lease_id: str,
    now: datetime,
) -> str:
    """T-AN-04 / T-AN-07 -- persist the consequences of a rejected result.

    The attempt is closed ``schema_invalid`` with ``error_code = AI_OUTPUT_INVALID``, the
    budget is spent, and the task goes to ``retry_wait`` while budget remains or to
    ``failed`` when it does not. **No ``analysis`` row is written on this path** -- that is
    the forbidden transition ``running -> valid`` on a schema-only pass, and it is
    unreachable here because the insert lives in a different function.

    ``cost_uncertain`` becomes ``False``: unlike a timeout, a rejected output is a *known*
    result. The model ran, it answered, and the answer was wrong.
    """
    ended_at = format_timestamp(now)
    with ctx.engine.begin() as connection:
        ctx.repository.close_attempt(
            connection,
            attempt_id=attempt.id,
            outcome=AnalysisAttemptOutcome.SCHEMA_INVALID.value,
            error_code=ErrorCode.AI_OUTPUT_INVALID.value,
            ended_at=ended_at,
            cost_uncertain=False,
        )
        remaining = ctx.repository.spend_attempt_budget(connection, task_id=task.id)
        ctx.repository.set_lease_state(connection, lease_id=lease_id, state="released")
        if remaining < 1:
            return _fail_task(ctx, connection, task=task, reason="analysis_failed")
        ctx.repository.release_task(
            connection, task_id=task.id, state=AnalysisItemState.RETRY_WAIT.value
        )
    return AnalysisItemState.RETRY_WAIT.value


def _commit_result(
    ctx: AnalysisContext,
    connection: Connection,
    *,
    task: TaskRow,
    generation: GenerationRow,
    attempt: AttemptRow,
    document: AnalysisResult,
    key: AnalysisKey,
    payload: Mapping[str, Any],
    payload_hash: str,
    lease_id: str,
    lease_epoch: int,
    now: datetime,
) -> dict[str, Any]:
    """The body of ``TXN-analysis-accept``. Runs inside one open transaction.

    The only place in this package that inserts into ``analysis``, and it is reachable only
    after both gates passed. The lease is re-checked here, under the write transaction: the
    read that admitted this call happened earlier, and between the two a sweep may have taken
    the task away. Checking only on the read snapshot is precisely the stale-writer hole I10
    names.
    """
    lease = _require_current_lease(
        ctx, connection, task=task, lease_id=lease_id, lease_epoch=lease_epoch, now=now
    )
    analyzed_at = format_timestamp(now)
    row = AnalysisRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        analysis_generation_id=generation.id,
        target_kind=generation.target_kind,
        target_work_id=generation.target_work_id,
        target_post_id=generation.target_post_id,
        target_key=generation.target_key,
        task_type=key.task_type,
        source_fingerprint=key.source_fingerprint,
        prompt_version=key.prompt_version,
        schema_version=key.schema_version,
        generation_number=key.generation_number,
        status="valid",
        payload=json_text(payload),
        payload_hash=payload_hash,
        evidence_level=document.evidence_level.value,
        provider_name=document.provider.provider_name,
        model_name=document.provider.model_name,
        **_usage_columns(document),
        analyzed_at=analyzed_at,
        accepted_from_attempt_id=attempt.id,
    )
    ctx.repository.insert_analysis(connection, row)
    ctx.repository.close_attempt(
        connection,
        attempt_id=attempt.id,
        outcome=AnalysisAttemptOutcome.ACCEPTED.value,
        error_code=None,
        ended_at=analyzed_at,
        cost_uncertain=False,
    )
    ctx.repository.release_task(connection, task_id=task.id, state=AnalysisItemState.VALID.value)
    ctx.repository.set_lease_state(connection, lease_id=lease.id, state="released")
    return _result_envelope(row, status="committed")


def _usage_columns(document: AnalysisResult) -> dict[str, int | None]:
    """``usage`` -> the two nullable columns, with I14 enforced rather than assumed.

    ``NULL`` means *unknown*, which is the normal answer on the CLI path (REQ-D44). There is
    no branch here that can produce a ``0`` standing in for unknown: the only shape that
    could -- ``unknown = false`` with a count missing -- was already rejected by
    :func:`_semantic_validation` as ``usage_unknown_mismatch``, so this function maps and does
    not decide.
    """
    usage = document.usage
    if usage.unknown:
        return {"usage_tokens_in": None, "usage_tokens_out": None}
    assert usage.tokens_in is not None and usage.tokens_out is not None
    return {"usage_tokens_in": usage.tokens_in, "usage_tokens_out": usage.tokens_out}


def _result_envelope(row: AnalysisRow, *, status: str) -> dict[str, Any]:
    return {
        "status": status,
        "analysis_id": row.id,
        "generation_number": row.generation_number,
        "payload_hash": row.payload_hash,
        "analyzed_at": row.analyzed_at,
        "accepted_from_attempt_id": row.accepted_from_attempt_id,
    }


def _ai_output_invalid(kind: str, task: TaskRow, attempt: AttemptRow) -> AnalysisError:
    return AnalysisError(
        ErrorCode.AI_OUTPUT_INVALID,
        "Kết quả không qua được kiểm ngữ nghĩa; không có gì được ghi.",
        details_safe={
            "task_id": task.id,
            "task_type": task.task_type,
            "attempt_number": attempt.attempt_number,
            "validation_failure_kind": kind,
        },
    )


def _semantic_validation(
    ctx: AnalysisContext,
    *,
    task: TaskRow,
    generation: GenerationRow,
    document: AnalysisResult,
    key: AnalysisKey,
) -> str | None:
    """Gate 3 -- SV-01..SV-07 of ``contracts/ai/tasks.yaml``.

    These are the checks JSON Schema cannot express, and skipping them is a named forbidden
    transition: a result that passes only the schema must not become ``valid``.

    Returns the ``validation_failure_kind`` the contract assigns to the first failure, or
    ``None`` when every check passes. A *category* is returned, never the offending text: an
    error envelope may not carry model output (errors.yaml §redaction, SRC-PLAN §5.1).

    Pure with respect to the database -- it reads only what it was handed plus the task input
    port -- so the caller is free to decide, per outcome, which transaction the consequences
    belong in.
    """
    # SV-01: the key in the output equals the key of the assignment, component by component.
    # The model does not get to change its own target, task type or generation.
    if (
        key.target_key != generation.target_key
        or key.task_type != generation.task_type
        or key.generation_number != generation.generation_number
        or key.owner_id != ctx.owner_id
        or document.task_type.value != generation.task_type
    ):
        return "analysis_key_mismatch"

    # SV-07: version consistency between the envelope and the key.
    if str(document.schema_version) != key.schema_version:
        return "version_mismatch"

    # I14, checked here so the rejection is recorded rather than rolled back. `unknown` is a
    # legitimate answer on the CLI path (REQ-D44); "known, but the numbers are missing" is
    # not, and the one thing that must never happen is a zero standing in for unknown -- a
    # cost report would then say "free" about something that may well have been billed.
    if not document.usage.unknown and (
        document.usage.tokens_in is None or document.usage.tokens_out is None
    ):
        return "usage_unknown_mismatch"

    sources = (
        []
        if ctx.task_input is None
        else list(ctx.task_input.sources_for(target_key=task.target_key))
    )
    granted = {source.source_id for source in sources}
    declared = {str(item.root) for item in (document.input_source_ids or [])}
    if granted and declared and not declared <= granted:
        return "citation_unknown_source"
    # With no task-input port wired the server cannot know what was granted, so the result's
    # own declaration is the only closed set available. That is weaker than SV-02 intends and
    # is stated as such rather than silently skipped.
    allowed_refs = granted or declared

    result_body: Mapping[str, Any] = document.result
    statements: list[Mapping[str, Any]] = list(result_body.get("statements") or [])
    evidence_level = document.evidence_level.value

    # SV-02: every citation, evidence ref and comparator points inside the granted set. A
    # citation to a real id that was NOT granted for this run is still a failure -- that is
    # the whole hedge against invented citations.
    if allowed_refs and not _referenced_source_ids(result_body, statements) <= allowed_refs:
        return "citation_unknown_source"

    # SV-03: `author_claim` and `source_verified` need at least one citation, and
    # `source_verified` additionally needs `evidence_level >= abstract`. A statement cannot be
    # "checked against the source" when the only source is a post (REQ-AC11).
    for statement in statements:
        kind = str(statement.get("kind"))
        if kind in ("author_claim", "source_verified") and not statement.get("citation_refs"):
            return "unsupported_claim_kind"
        if kind == "source_verified" and _evidence_rank(evidence_level) < _evidence_rank(
            "abstract"
        ):
            return "unsupported_claim_kind"

    # SV-04: the level claimed is at most the ceiling the server computed from the sources
    # actually supplied. `full_text` is unreachable at MVP and always overclaims.
    if sources and _evidence_rank(evidence_level) > _evidence_rank(max_evidence_level(sources)):
        return "evidence_level_overclaim"
    if evidence_level == "full_text":
        return "evidence_level_overclaim"

    if generation.task_type == "direction_phrasing":
        # SV-06: the blunt block list. AI phrases a direction; it does not rule on scientific
        # novelty (REQ-D54, SRC-SPEC §2.3). Deliberately blunt: it is paired with the review
        # rubric of contracts/ai/grounding.md §6, not a substitute for it.
        text_value = str(result_body.get("text") or "").casefold()
        if any(phrase.casefold() in text_value for phrase in FORBIDDEN_NOVELTY_PHRASES):
            return "forbidden_novelty_phrasing"
    return None


def _referenced_source_ids(
    result_body: Mapping[str, Any], statements: Sequence[Mapping[str, Any]]
) -> set[str]:
    """Every source id the result points at, from all three places one can appear."""
    references: set[str] = set()
    for statement in statements:
        references.update(str(value) for value in (statement.get("citation_refs") or []))
    for label in result_body.get("labels") or []:
        references.update(str(value) for value in (label.get("evidence_refs") or []))
    comparator = (result_body.get("difference_from_existing") or {}).get("comparator") or {}
    if comparator.get("kind") == "ref" and comparator.get("source_ref"):
        references.add(str(comparator["source_ref"]))
    return references


def _evidence_rank(level: str) -> int:
    return EVIDENCE_LEVEL_ORDER.index(level)


def _revoke_credential(ctx: AnalysisContext, *, task_id: str, attempt_id: str) -> None:
    """``secret.revoke_task_credential`` -- called after the transaction, never inside it.

    A credential revocation is an effect on another service. Putting it inside the
    transaction would mean either revoking a credential for a commit that then rolled back,
    or holding a database transaction open across a call into another module.
    """
    if ctx.secrets is None:
        return
    ctx.secrets.revoke_task_credential(
        task_id=task_id, attempt_id=attempt_id, reason="task_finished"
    )


# ---------------------------------------------------------- analysis.report_attempt_unknown


def report_attempt_unknown(
    ctx: AnalysisContext,
    *,
    task_id: str,
    attempt_id: str,
    lease_id: str,
    lease_epoch: int,
    reason: str = "worker_lost_after_provider_call",
) -> dict[str, Any]:
    """``analysis.report_attempt_unknown`` -- ``TXN-analysis-unknown`` (T-AN-08).

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**

    This is the operation that records what the system does *not* know. The worker died, or
    the inference deadline passed, at a point where the provider may already have run and the
    bill may already exist. Three things follow, and all three are the contract's:

    * **no ``analysis`` row is created** -- an attempt is never a result (I16), and there is
      no code path here that could write one;
    * ``cost_uncertain`` stays ``true`` and ``ended_at`` stays ``NULL``: the system records
      exactly what it does not know rather than claiming no cost was incurred
      (SRC-PLAN §10 ``AI_ATTEMPT_UNCERTAIN``);
    * a later re-run writes a **new** attempt row. This one is never edited.

    An expired lease is accepted (``allow_expired``): this operation exists precisely because
    the holder stopped responding, and requiring a live lease would make the honest report
    impossible to file. A *revoked* lease is still refused -- that means the task was taken
    away and given to somebody else, so this caller is no longer the one to speak for it.

    Idempotent on ``attempt_id`` (``contracts/ports.yaml``): reporting the same attempt twice
    records one unknown attempt.
    """
    now = ctx.now()
    _assert_writable(ctx, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN)
    try:
        with ctx.engine.begin() as connection:
            task = _require_task(
                ctx, connection, task_id, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN
            )
            attempt = ctx.repository.attempt_by_id(connection, attempt_id)
            if attempt is None or attempt.analysis_generation_id != task.analysis_generation_id:
                raise _not_found("analysis_attempt", OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN)
            if task.state == AnalysisItemState.UNKNOWN_ATTEMPT.value:
                return _unknown_envelope(task, attempt, reason=reason, replayed=True)

            _require_current_lease(
                ctx,
                connection,
                task=task,
                lease_id=lease_id,
                lease_epoch=lease_epoch,
                now=now,
                allow_expired=True,
            )
            ctx.repository.close_attempt(
                connection,
                attempt_id=attempt.id,
                outcome=AnalysisAttemptOutcome.TIMEOUT_UNKNOWN.value,
                error_code=ErrorCode.AI_ATTEMPT_UNCERTAIN.value,
                # Deliberately NULL: nobody knows when -- or whether -- the try finished.
                ended_at=None,
                cost_uncertain=True,
            )
            ctx.repository.release_task(
                connection,
                task_id=task.id,
                state=AnalysisItemState.UNKNOWN_ATTEMPT.value,
            )
            ctx.repository.set_lease_state(connection, lease_id=lease_id, state="expired")
            ctx.repository.spend_attempt_budget(connection, task_id=task.id)
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN) from exc
    _revoke_credential(ctx, task_id=task_id, attempt_id=attempt_id)
    return _unknown_envelope(task, attempt, reason=reason, replayed=False)


def _unknown_envelope(
    task: TaskRow, attempt: AttemptRow, *, reason: str, replayed: bool
) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "attempt_id": attempt.id,
        "attempt_number": attempt.attempt_number,
        "state": AnalysisItemState.UNKNOWN_ATTEMPT.value,
        "cost_uncertain": True,
        "reason": reason,
        "replayed": replayed,
    }


# ----------------------------------------------------------- analysis.request_reanalysis


def request_reanalysis(
    ctx: AnalysisContext,
    *,
    target_kind: str,
    target_id: str,
    task_type: str,
    source_fingerprint: str,
    prompt_version: str,
    schema_version: str,
    reason: str,
    request_id: str,
    caller_module: str = "MOD-web-ui",
) -> dict[str, Any]:
    """``analysis.request_reanalysis`` -- ``TXN-analysis-reanalysis`` (T-AN-12).

    **Commit point: the COMMIT of the single ``with ctx.engine.begin()`` block below.**

    Reanalysis opens a **new generation** and keeps the old result untouched (REQ-D26). It is
    not a transition of the old item: the new generation is a different analysis key, which is
    why it neither collides with ``ux_analysis_valid_key`` nor breaks I04.

    ``reason`` is checked against the closed list of legal triggers. A tag change is not on
    it, nor is a provider or model change, nor a new report period
    (``contracts/ai/tasks.yaml`` §reanalysis_triggers.forbidden) -- so there is no argument
    value by which a tag edit can reach this operation. That refusal is REQ-AC06 stated from
    the other side: the enqueue path skips keys that already have results, and this path
    cannot be tricked into minting a key that does not.
    """
    require_edge(OperationId.ANALYSIS_REQUEST_REANALYSIS, caller_module, edge_ref="FE-28")
    stored = ctx.reanalysis_receipts.get(request_id)
    if stored is not None:
        return stored
    stored_reason = WIRE_REASON_ALIASES.get(reason, reason)
    if stored_reason not in REANALYSIS_REASONS:
        raise _validation_error(
            "Lý do phân tích lại không thuộc danh sách hợp lệ.",
            field_path="reason",
            violation_kind="enum_invalid",
        )
    if task_type not in TASK_TYPES:
        raise _validation_error(
            "task_type không thuộc ba giá trị của hợp đồng.",
            field_path="task_type",
            violation_kind="enum_invalid",
        )
    _assert_writable(ctx, OperationId.ANALYSIS_REQUEST_REANALYSIS)
    try:
        with ctx.engine.begin() as connection:
            payload = _open_new_generation(
                ctx,
                connection,
                target_kind=target_kind,
                target_id=target_id,
                task_type=task_type,
                source_fingerprint=source_fingerprint,
                prompt_version=prompt_version,
                schema_version=schema_version,
                reason=stored_reason,
            )
    except AnalysisError:
        raise
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(ctx, exc, OperationId.ANALYSIS_REQUEST_REANALYSIS) from exc
    ctx.reanalysis_receipts[request_id] = payload
    return payload


def _open_new_generation(
    ctx: AnalysisContext,
    connection: Connection,
    *,
    target_kind: str,
    target_id: str,
    task_type: str,
    source_fingerprint: str,
    prompt_version: str,
    schema_version: str,
    reason: str,
) -> dict[str, Any]:
    """Body of ``TXN-analysis-reanalysis``. Runs inside one open transaction."""
    columns = _target_columns(target_kind, target_id)
    target_key = str(columns["target_key"])
    generation_number = (
        ctx.repository.max_generation_number(
            connection, owner_id=ctx.owner_id, target_key=target_key, task_type=task_type
        )
        + 1
    )
    requested_at = format_timestamp(ctx.now())
    generation = GenerationRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        target_kind=str(columns["target_kind"]),
        target_work_id=columns["target_work_id"],
        target_post_id=columns["target_post_id"],
        target_key=target_key,
        task_type=task_type,
        generation_number=generation_number,
        reason=reason,
        requested_at=requested_at,
        requested_by="owner",
    )
    ctx.repository.insert_generation(connection, generation)
    task = TaskRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        analysis_generation_id=generation.id,
        target_key=target_key,
        task_type=task_type,
        state=AnalysisItemState.PENDING.value,
        claimed_by_worker_identity=None,
        claimed_lease_id=None,
        claimed_at=None,
        enqueued_at=requested_at,
        attempt_budget_remaining=ANALYSIS_ATTEMPTS_PER_ITEM,
    )
    ctx.repository.insert_task(connection, task)
    key = analysis_key_from_inputs(
        owner_id=ctx.owner_id,
        target_key=target_key,
        task_type=task_type,
        source_fingerprint=source_fingerprint,
        prompt_version=prompt_version,
        schema_version=schema_version,
        generation_number=generation_number,
    )
    return {
        "analysis_generation_id": generation.id,
        "generation_number": generation_number,
        "task_id": task.id,
        "analysis_key": key.as_dict(),
        "reason": reason,
    }


# ------------------------------------------------- internal transitions (no port of their own)


def reap_expired_leases(ctx: AnalysisContext) -> list[str]:
    """T-AN-11 -- take back tasks whose lease ran out. Returns the task ids released.

    The old worker is not asked for permission and its attempt row is **not** deleted: if it
    did call the provider, the cost is real and the attempt is the evidence. What it loses is
    the right to commit, which every later call of :func:`_require_current_lease` enforces.
    """
    now = ctx.now()
    released: list[str] = []
    with ctx.engine.begin() as connection:
        rows = connection.execute(_RUNNING_TASKS_SQL, {"owner_id": ctx.owner_id}).mappings().all()
        for row in rows:
            lease = ctx.repository.lease_by_id(connection, str(row["claimed_lease_id"]))
            if lease is None or not _lease_expired(lease, now):
                continue
            attempt = _current_attempt(
                ctx, connection, generation_id=str(row["analysis_generation_id"])
            )
            if attempt is not None and attempt.ended_at is None:
                ctx.repository.close_attempt(
                    connection,
                    attempt_id=attempt.id,
                    outcome=AnalysisAttemptOutcome.CANCELLED_STALE_LEASE.value,
                    error_code=ErrorCode.WORKER_LEASE_EXPIRED.value,
                    ended_at=format_timestamp(now),
                    cost_uncertain=attempt.cost_uncertain,
                )
            ctx.repository.set_lease_state(connection, lease_id=lease.id, state="expired")
            ctx.repository.release_task(
                connection, task_id=str(row["id"]), state=AnalysisItemState.PENDING.value
            )
            released.append(str(row["id"]))
    return released


def auto_rerun_unknown_attempt(ctx: AnalysisContext, *, task_id: str) -> str:
    """T-AN-09 / T-AN-10 -- the one automatic re-run allowed after an unknown outcome.

    Exactly one, and it **consumes** a unit of ``analysis_attempts_per_item`` rather than
    opening a new budget (retry-policy ``consumes_vi``). A second attempt at recovery has to
    be the Owner pressing reanalysis, which is a deliberate act with a visible cost.

    Why analysis may auto-re-run at all while ``delivery.state = unknown`` never does: the
    worst case here is *money*, and the worst case there is a person receiving the same
    message twice -- unobservable and not undoable (T-AN-09 ``effects_vi``).

    Returns the resulting task state.
    """
    with ctx.engine.begin() as connection:
        task = _require_task(ctx, connection, task_id, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN)
        if task.state != AnalysisItemState.UNKNOWN_ATTEMPT.value:
            return task.state
        attempts = ctx.repository.attempts_for_generation(
            connection,
            owner_id=ctx.owner_id,
            analysis_generation_id=task.analysis_generation_id,
        )
        unknown_reruns_used = max(0, len(attempts) - 1)
        if (
            task.attempt_budget_remaining < 1
            or unknown_reruns_used >= ANALYSIS_UNKNOWN_ATTEMPT_AUTO_RERUN
        ):
            return _fail_task(ctx, connection, task=task, reason="analysis_unknown")
        ctx.repository.release_task(
            connection, task_id=task.id, state=AnalysisItemState.PENDING.value
        )
        return AnalysisItemState.PENDING.value


def _fail_task(ctx: AnalysisContext, connection: Connection, *, task: TaskRow, reason: str) -> str:
    """T-AN-07 / T-AN-10 -- the budget is gone; the item is missing its analysis.

    ``failed`` here means the run knows the item has no analysis, **not** that the item has
    no research (I13): the display must keep "analysis failed" and "outcome unknown" apart.
    The item also has to reach ``pending_item_ledger`` so the report can carry it as a pending
    entry rather than dropping it (B04/B17). That table belongs to ``MOD-report-service`` and
    does not exist yet, so when no port is wired this records nothing and says so in the
    return of :func:`ledger_state`, instead of pretending the ledger entry was made.
    """
    ctx.repository.release_task(connection, task_id=task.id, state=AnalysisItemState.FAILED.value)
    if ctx.pending_ledger is not None:
        ctx.pending_ledger.record_pending(target_key=task.target_key, reason=reason)
    return AnalysisItemState.FAILED.value


def ledger_state(ctx: AnalysisContext) -> dict[str, Any]:
    """Whether the pending-item ledger is actually wired.

    A caller that needs to know "was this item recorded as pending?" must be able to find out
    that nobody recorded it. Reporting an unwired ledger as healthy is the shape of defect
    CAP-P5 and I13 exist to prevent.
    """
    return {"pending_ledger_wired": ctx.pending_ledger is not None}


# ------------------------------------------------------------------ ISO-05: lease as gate


@dataclass(frozen=True)
class TaskCredentialScope:
    """What ``secret.issue_task_credential`` is allowed to issue for one attempt (B13)."""

    task_id: str
    attempt_id: str
    task_type: str
    provider_name: str
    model_name: str
    auth_family: str


def verify_task_lease(
    ctx: AnalysisContext,
    *,
    task_id: str,
    attempt_id: str,
    lease_id: str,
    lease_epoch: int,
    worker_identity: str,
) -> TaskCredentialScope:
    """The check ``secret.issue_task_credential`` consults before issuing (ADR-0010, ISO-05).

    ``contracts/ports.yaml``: "không cấp credential cho task worker không giữ lease". The
    secret service does not own the lease, so it asks the module that does -- and this is that
    answer. A worker without the current lease gets ``STALE_LEASE`` and no credential is
    minted; a worker whose lease has run out gets ``WORKER_LEASE_EXPIRED``.

    What comes back is scoped to **one** task and one provider. There is no argument by which
    this function returns the whole key store, and no branch that widens the scope on a
    retry: that bound is what limits the blast radius of a successful prompt injection to a
    single task's credential (ADR-0010 §1, denied case NC-03).
    """
    now = ctx.now()
    with ctx.engine.connect() as connection:
        task = _require_task(ctx, connection, task_id, OperationId.SECRET_ISSUE_TASK_CREDENTIAL)
        lease = _require_current_lease(
            ctx, connection, task=task, lease_id=lease_id, lease_epoch=lease_epoch, now=now
        )
        attempt = ctx.repository.attempt_by_id(connection, attempt_id)
    if lease.worker_identity != worker_identity:
        raise AnalysisError(
            ErrorCode.STALE_LEASE,
            "Worker này không giữ lease của task.",
            details_safe={
                "job_id": task.id,
                "lease_epoch_seen": lease_epoch,
                "lease_epoch_current": lease.lease_epoch,
            },
        )
    if attempt is None or attempt.worker_lease_id != lease.id:
        raise AnalysisError(
            ErrorCode.STALE_LEASE,
            "Attempt không thuộc lease hiện hành của task.",
            details_safe={
                "job_id": task.id,
                "lease_epoch_seen": lease_epoch,
                "lease_epoch_current": lease.lease_epoch,
            },
        )
    choice = (
        None if ctx.provider_config is None else ctx.provider_config.provider_for(task.task_type)
    )
    if choice is None or not choice.enabled:
        # B13/ADR-0010 §3: an adapter whose isolation is unverified stays disabled, and a
        # disabled adapter is never handed a credential. Not a punishment -- the default.
        raise AnalysisError(
            ErrorCode.AI_PROVIDER_UNAVAILABLE,
            "Provider cho task này chưa được bật.",
            details_safe={"task_id": task.id, "reason_code": "isolation_unverified"},
        )
    return TaskCredentialScope(
        task_id=task.id,
        attempt_id=attempt.id,
        task_type=task.task_type,
        provider_name=choice.provider_name,
        model_name=choice.model_name,
        auth_family=choice.auth_family,
    )


__all__ = [
    "AI_INFERENCE_TIMEOUT_SECONDS",
    "ANALYSIS_ATTEMPTS_PER_ITEM",
    "ANALYSIS_UNKNOWN_ATTEMPT_AUTO_RERUN",
    "HEARTBEAT_GRACE_SECONDS",
    "HEARTBEAT_INTERVAL_ANALYSIS_SECONDS",
    "LEASE_TTL_ANALYSIS_SECONDS",
    "REANALYSIS_REASONS",
    "AdapterCallCounter",
    "AnalysisContext",
    "AnalysisDependencyUnavailable",
    "AnalysisError",
    "PendingLedgerPort",
    "ProviderChoice",
    "ProviderConfigPort",
    "SecretPort",
    "StorageGuardPort",
    "TargetRequest",
    "TaskCredentialScope",
    "TaskInputPort",
    "TaskSource",
    "auto_rerun_unknown_attempt",
    "claim_task",
    "enqueue_tasks",
    "get_task_input",
    "heartbeat",
    "ledger_state",
    "max_evidence_level",
    "reap_expired_leases",
    "report_attempt_unknown",
    "request_reanalysis",
    "submit_result",
    "verify_task_lease",
]
