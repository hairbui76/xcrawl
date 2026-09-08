"""``MOD-scheduler`` + ``MOD-job-service`` — enqueue, coalesce, claim, heartbeat, release.

===================================== ======================================= ==================
operation id                          function                                transaction
===================================== ======================================= ==================
``job.enqueue_scheduled_run``         :func:`enqueue_scheduled_run`           one
``job.coalesce_overdue``              :func:`coalesce_overdue`                one
``worker.register_capabilities``      :func:`register_capabilities`           one
``worker.claim_assignment``           :func:`claim_assignment`                ``TXN-claim``
``worker.heartbeat``                  :func:`heartbeat`                       one
``worker.report_stop``                :func:`report_stop`                     one
``worker.release_assignment``         :func:`release_assignment`              one
``worker.get_status``                 :func:`get_worker_status`               none (read)
``run.list`` / ``run.get``            :func:`list_runs` / :func:`get_run`     none (read)
``run.run_now``                       :func:`run_now`                         one
``run.resume``                        :func:`resume_run`                      one
``run.cancel``                        :func:`cancel_run`                      one
===================================== ======================================= ==================

``scheduler.evaluate_due`` is **not** here: it is pure and read-only, and lives in
:mod:`server.app.scheduler.evaluator` so that the DST rules can be tested without a database.

The commit point that matters: ``TXN-claim``
---------------------------------------------
Card §6: *"Claim là CAS trên assignment + cấp lease epoch mới trong một transaction."*
:func:`claim_assignment` opens exactly one ``BEGIN…COMMIT``, and inside it, in this order:
re-read the run and any current lease; refuse if storage is not writable or a restore is
unreconciled; revoke an expired lease (bumping the epoch); insert the new lease; move the
assignment to ``claimed`` and the run to ``running``. Two claimants racing both reach the
insert, and ``ux_assignment_lease_one_held`` lets exactly one commit — the loser catches the
``IntegrityError`` and answers ``no_work``, not an error, because
``contracts/schemas/worker-assignment.schema.json`` gives ``assignment_already_held`` as a
``no_work`` reason rather than a failure.

Why the loser of a claim race is not an error
----------------------------------------------
It would be easy to answer ``IDEMPOTENCY_CONFLICT`` and be *nearly* right — card §6 does
mention it for concurrent claims. But the wire contract is more specific: the ``no_work``
object exists, ``assignment_already_held`` is one of its six reasons, and fixture
``collection/g-schedule-due-claim.json`` event 3 pins ``response_status: 200`` with exactly
that reason and a 45 s backoff. A worker that polls every 45 s must not treat "somebody else
has it" as a failure to report. ``IDEMPOTENCY_CONFLICT`` is reserved for its own case: the
same ``claim_request_id`` presented with a *different* payload.

What this module refuses to do
-------------------------------
``contracts/modules.yaml`` forbids ``MOD-scheduler`` → Chrome, → Telegram and → marking a
report delivered (FE-24 and the §5 denied paths). There is no HTTP client, no browser driver
and no delivery import in this package; the only outbound edges are ``ingest.get_checkpoint``
(read-only, through a port) and ``delivery.create_intent`` (alert intent, through a port).
Both are injected on :class:`JobContext` and default to ``None``, so a deployment that wired
neither gets a refusal rather than a scheduler that invented a transport.
"""

from __future__ import annotations

import json
import os
import time as _time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError

from server.app.db.engine import session_scope
from server.app.jobs.lease import (
    CLAIM_IDLE_BACKOFF_SECONDS,
    HEARTBEAT_INTERVAL_COLLECTOR_SECONDS,
    LEASE_TTL_COLLECTOR_SECONDS,
    JobError,
    Lease,
    LeaseState,
    assert_current_lease,
    expiry_from,
    is_expired,
    next_epoch,
    parse_timestamp_utc_ms,
    revoke,
    timestamp_utc_ms,
)
from server.app.scheduler.evaluator import Occurrence, ScheduleSettings, coalesce_window_id

# --------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------

#: ``contracts/state/run.yaml`` ``terminal_states``. A run in one of these is finished; every
#: "is anything active?" question in this module is the complement of this set, never a list
#: of active states that a new status could be added to without anyone noticing.
TERMINAL_RUN_STATUSES: frozenset[str] = frozenset({"completed", "failed", "cancelled"})

#: ``non_terminal_states``, for the same reason in the other direction.
NON_TERMINAL_RUN_STATUSES: frozenset[str] = frozenset(
    {"queued", "running", "waiting_retry", "needs_user", "blocked"}
)

#: ``entities.yaml`` ``worker_registration.worker_kind`` is ``x_collector | analysis_worker``;
#: the wire (``ports.yaml`` ``worker.register_capabilities``,
#: ``worker-assignment.schema.json``) says ``collector | analysis``. Two vocabularies, each
#: authoritative for its own layer, so the mapping is explicit and one-directional rather than
#: a string that happens to work.
WIRE_TO_STORED_WORKER_KIND: Mapping[str, str] = {
    "collector": "x_collector",
    "analysis": "analysis_worker",
}
STORED_TO_WIRE_WORKER_KIND: Mapping[str, str] = {
    v: k for k, v in WIRE_TO_STORED_WORKER_KIND.items()
}

#: ``worker.report_stop`` request vocabulary (``contracts/ports.yaml``) mapped to the
#: ``(status, stop_reason)`` pair ``contracts/state/run.yaml`` assigns it. This table **is**
#: T-RUN-02/09/16/24/25: a stop reason the collector reports does not choose the run's fate,
#: the state machine does, and putting the mapping in one dict is what stops two call sites
#: from disagreeing about what ``session_expired`` means.
STOP_REASON_EFFECT: Mapping[str, tuple[str, str]] = {
    "challenge_required": ("needs_user", "captcha"),
    "session_expired": ("needs_user", "session_expired"),
    "limit_reached": ("running", "limit_reached"),
    "source_blocked": ("blocked", "source_blocked"),
    "source_layout_changed": ("blocked", "source_layout_changed"),
    "rate_limited": ("running", "rate_limited"),
    "worker_shutdown": ("queued", "worker_lost"),
    "local_storage_unavailable": ("queued", "storage_unavailable"),
}

#: The two stop reasons that make a run wait for the Owner. T-RUN-15 keeps these across a
#: lease expiry instead of returning the run to ``queued``, which is the difference between
#: "the worker died" and "the Owner has to do something".
OWNER_WAIT_STATUSES: frozenset[str] = frozenset({"needs_user", "blocked"})

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp, 80 bits of randomness, Crockford base32."""
    value = (int(_time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def utc_now() -> datetime:
    return datetime.now(UTC)


# --------------------------------------------------------------------------------------
# Ports -- the two edges card §5 allows, and nothing else
# --------------------------------------------------------------------------------------


class StorageGuardPort(Protocol):
    """``server.app.storage.guard.StorageGuard``. Ask before writing; let it raise.

    ``retry-policy.yaml`` ``storage_write_blocked_grace_before_refusing_claims`` is **0**
    seconds, deliberately: the moment storage cannot be written, no new assignment is granted.
    A positive grace would hand out a lease that cannot be persisted, which is what I02
    forbids.
    """

    def assert_writable(self, operation_id: OperationId) -> None: ...


class CheckpointPort(Protocol):
    """``ingest.get_checkpoint`` — read-only (ruling R-01: this module never writes it).

    ``MOD-ingest-service`` owns the ``checkpoint`` table. The claim payload has to carry the
    ACKed progress so a resuming worker starts from the truth rather than from its own memory
    (CP-02, I02), and this port is the only way this module learns it.
    """

    def get_checkpoint(self, *, run_id: str) -> Mapping[str, Any] | None: ...


class AlertIntentPort(Protocol):
    """``delivery.create_intent`` — at most one alert per run (``REQ-AC04``).

    Returns the intent id, or ``None`` when one already exists for this run. The uniqueness
    is enforced by ``ux_outbox_alert_per_run`` on ``outbox_intent``, which is the delivery
    card's table; this module records the pointer and never counts as the authority.
    """

    def create_alert_intent(self, *, run_id: str, stop_reason: str) -> str | None: ...


#: The six ``no_work.reason`` values of ``contracts/schemas/worker-assignment.schema.json``.
NO_WORK_REASONS: frozenset[str] = frozenset(
    {
        "no_due_occurrence",
        "run_needs_user",
        "run_blocked",
        "storage_not_healthy",
        "capability_not_met",
        "assignment_already_held",
    }
)


@dataclass(frozen=True, slots=True)
class RunLimits:
    """``stop_conditions`` of the claim payload, from ``retry-policy.yaml``.

    ``ACCEPTED (OD-20260907-01)`` working values that ``REQ-OQ05`` re-measures after M0, so
    they are configuration on the context rather than literals in the claim builder.
    """

    max_posts: int = 200
    max_duration_s: int = 1800


@dataclass
class JobContext:
    """Everything the operations need, injected rather than reached for.

    ``clock`` is an argument for the same reason it is in the evaluator: catch-up, lease
    expiry and the run-now debounce are all statements about time, and a test that cannot move
    the clock cannot check any of them.
    """

    engine: Engine
    owner_id: str
    settings: ScheduleSettings
    clock: Callable[[], datetime] = utc_now
    id_factory: Callable[[], str] = new_ulid
    storage_guard: StorageGuardPort | None = None
    checkpoint_port: CheckpointPort | None = None
    alert_port: AlertIntentPort | None = None
    limits: RunLimits = field(default_factory=RunLimits)
    #: LM-08: set while a restore has not been reconciled. Every lease is stale in that state
    #: regardless of its TTL, and only ``backup.reconcile_after_restore`` clears it.
    restore_pending: bool = False

    def now(self) -> datetime:
        return self.clock().astimezone(UTC)

    def assert_writable(self, operation_id: OperationId) -> None:
        if self.storage_guard is not None:
            self.storage_guard.assert_writable(operation_id)


# --------------------------------------------------------------------------------------
# Row helpers
# --------------------------------------------------------------------------------------

_RUN_COLUMNS = (
    "id, owner_id, trigger_type, phase, status, outcome, stop_reason, applied_config, "
    "created_at, schedule_occurrence_ids, catch_up_window_from, catch_up_window_to, "
    "current_lease_epoch, attempt_count, next_attempt_at, last_error_code, "
    "unblock_condition_vi, alert_intent_id, observed_window_from, observed_window_to, "
    "posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, "
    "x_coverage_note_vi, rate_limited_at"
)

_LEASE_COLUMNS = "id, owner_id, run_id, job_id, worker_identity, lease_epoch, expires_at, state"


def _run_row(connection: Connection, owner_id: str, run_id: str) -> dict[str, Any] | None:
    row = (
        connection.execute(
            text(f"SELECT {_RUN_COLUMNS} FROM run WHERE owner_id = :o AND id = :id"),
            {"o": owner_id, "id": run_id},
        )
        .mappings()
        .fetchone()
    )
    return dict(row) if row is not None else None


def _active_run(connection: Connection, owner_id: str) -> dict[str, Any] | None:
    """The one non-terminal run, if there is one.

    ``T-RUN-21`` and ``CU-05`` both turn on "is there already a run that has not finished?",
    and both treat the answer as singular. Ordered by ``created_at`` so that a database which
    somehow held two would answer deterministically rather than arbitrarily.
    """
    placeholders = ", ".join(f"'{status}'" for status in sorted(NON_TERMINAL_RUN_STATUSES))
    row = (
        connection.execute(
            text(
                f"SELECT {_RUN_COLUMNS} FROM run WHERE owner_id = :o "
                f"AND status IN ({placeholders}) ORDER BY created_at, id LIMIT 1"
            ),
            {"o": owner_id},
        )
        .mappings()
        .fetchone()
    )
    return dict(row) if row is not None else None


def _lease_of(connection: Connection, owner_id: str, job_id: str) -> Lease | None:
    row = (
        connection.execute(
            text(
                f"SELECT {_LEASE_COLUMNS} FROM assignment_lease WHERE owner_id = :o "
                "AND job_id = :j ORDER BY lease_epoch DESC LIMIT 1"
            ),
            {"o": owner_id, "j": job_id},
        )
        .mappings()
        .fetchone()
    )
    if row is None:
        return None
    return Lease(
        id=row["id"],
        owner_id=row["owner_id"],
        run_id=row["run_id"],
        job_id=row["job_id"],
        worker_identity=row["worker_identity"],
        lease_epoch=int(row["lease_epoch"]),
        expires_at=parse_timestamp_utc_ms(row["expires_at"]),
        state=LeaseState(row["state"]),
    )


def _lease_by_id(connection: Connection, owner_id: str, lease_id: str) -> Lease | None:
    row = (
        connection.execute(
            text(f"SELECT {_LEASE_COLUMNS} FROM assignment_lease WHERE owner_id = :o AND id = :id"),
            {"o": owner_id, "id": lease_id},
        )
        .mappings()
        .fetchone()
    )
    if row is None:
        return None
    return Lease(
        id=row["id"],
        owner_id=row["owner_id"],
        run_id=row["run_id"],
        job_id=row["job_id"],
        worker_identity=row["worker_identity"],
        lease_epoch=int(row["lease_epoch"]),
        expires_at=parse_timestamp_utc_ms(row["expires_at"]),
        state=LeaseState(row["state"]),
    )


def _insert_run(
    connection: Connection,
    *,
    run_id: str,
    owner_id: str,
    trigger_type: str,
    created_at: str,
    occurrence_ids: Sequence[str],
    window: tuple[str, str] | None,
    applied_config: Mapping[str, Any],
) -> None:
    connection.execute(
        text(
            "INSERT INTO run (id, owner_id, trigger_type, phase, status, outcome, stop_reason, "
            "applied_config, created_at, schedule_occurrence_ids, catch_up_window_from, "
            "catch_up_window_to, current_lease_epoch, attempt_count, next_attempt_at, "
            "last_error_code, unblock_condition_vi, alert_intent_id, observed_window_from, "
            "observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, "
            "limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at) "
            "VALUES (:id, :o, :trigger, 'collecting', 'queued', NULL, NULL, :config, :created, "
            ":occurrences, :from_at, :to_at, 0, 0, NULL, NULL, NULL, NULL, NULL, NULL, "
            "0, 0, 0, NULL, 0, NULL, NULL)"
        ),
        {
            "id": run_id,
            "o": owner_id,
            "trigger": trigger_type,
            "config": json.dumps(dict(applied_config), sort_keys=True, ensure_ascii=False),
            "created": created_at,
            "occurrences": json.dumps(list(occurrence_ids)),
            "from_at": window[0] if window else None,
            "to_at": window[1] if window else None,
        },
    )


def _applied_config(ctx: JobContext) -> dict[str, Any]:
    """``run.applied_config`` — immutable once the run leaves ``queued``.

    Snapshotted at creation on purpose: a run that is re-read later must show the limits it
    actually ran under, not the ones Settings holds today.
    """
    return {
        "schedule_slots_local": list(ctx.settings.slots_local),
        "schedule_timezone": ctx.settings.timezone_iana,
        "per_run_post_limit": ctx.limits.max_posts,
        "per_run_duration_limit_s": ctx.limits.max_duration_s,
    }


# --------------------------------------------------------------------------------------
# job.enqueue_scheduled_run / job.coalesce_overdue
# --------------------------------------------------------------------------------------


def _record_occurrences(
    connection: Connection,
    *,
    owner_id: str,
    occurrences: Sequence[Occurrence],
    state: str,
    run_id: str | None,
    window: tuple[str, str] | None,
) -> None:
    """Insert or move occurrence rows. ``INSERT … ON CONFLICT DO UPDATE`` on the natural key.

    The conflict target is ``ux_schedule_occurrence_due (owner_id, due_at)``, which is the
    contract's own uniqueness: one calendar moment, one row. A second evaluation of the same
    slot therefore updates the row it already has rather than failing or duplicating.
    """
    for occurrence in occurrences:
        connection.execute(
            text(
                "INSERT INTO schedule_occurrence (id, owner_id, due_at, state, "
                "coalesced_into_run_id, coalesced_window_from, coalesced_window_to) "
                "VALUES (:id, :o, :due, :state, :run, :from_at, :to_at) "
                "ON CONFLICT (owner_id, due_at) DO UPDATE SET "
                "state = excluded.state, "
                "coalesced_into_run_id = excluded.coalesced_into_run_id, "
                "coalesced_window_from = excluded.coalesced_window_from, "
                "coalesced_window_to = excluded.coalesced_window_to"
            ),
            {
                "id": occurrence.occurrence_id,
                "o": owner_id,
                "due": occurrence.due_at,
                "state": state,
                "run": run_id,
                "from_at": window[0] if window else None,
                "to_at": window[1] if window else None,
            },
        )


def enqueue_scheduled_run(ctx: JobContext, *, occurrences: Sequence[Occurrence]) -> dict[str, Any]:
    """``job.enqueue_scheduled_run`` — one occurrence, one run.

    Idempotency key: ``schedule_occurrence_id`` (``contracts/ports.yaml``), rule *"Một
    occurrence chỉ sinh một run; gọi lại trả run đã tạo"*. Implemented as a read of the
    occurrence row inside the transaction: if it is already ``coalesced``/``dispatched`` the
    stored ``coalesced_into_run_id`` is returned unchanged. The durable half of the same key
    is ``ux_schedule_occurrence_due``.

    ``CU-05``: while a non-terminal run exists, a newly due occurrence does **not** create a
    second run; it is left ``due`` so the next catch-up window absorbs it. Returning the
    active run rather than creating one is what keeps "one run at a time" true without a lock.
    """
    ctx.assert_writable(OperationId.JOB_ENQUEUE_SCHEDULED_RUN)
    if not occurrences:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.JOB_ENQUEUE_SCHEDULED_RUN.value,
                "field_path": "occurrences",
                "violation_kind": "empty",
            },
        )
    now = ctx.now()
    with session_scope(ctx.engine) as connection:
        existing = _existing_run_for(connection, ctx.owner_id, occurrences)
        if existing is not None:
            return {"run_id": existing, "created": False, "reason": "occurrence_already_enqueued"}
        active = _active_run(connection, ctx.owner_id)
        if active is not None:
            # CU-05. The occurrence stays `due` -- deliberately not `skipped`, because it has
            # not expired, it is waiting.
            _record_occurrences(
                connection,
                owner_id=ctx.owner_id,
                occurrences=occurrences,
                state="due",
                run_id=None,
                window=None,
            )
            return {"run_id": active["id"], "created": False, "reason": "run_already_active"}

        run_id = ctx.id_factory()
        instants = sorted(o.due_at for o in occurrences)
        window = (instants[0], instants[-1]) if len(occurrences) > 1 else None
        _insert_run(
            connection,
            run_id=run_id,
            owner_id=ctx.owner_id,
            trigger_type="scheduled",
            created_at=timestamp_utc_ms(now),
            occurrence_ids=[o.occurrence_id for o in occurrences],
            window=window,
            applied_config=_applied_config(ctx),
        )
        _record_occurrences(
            connection,
            owner_id=ctx.owner_id,
            occurrences=occurrences,
            state="coalesced" if len(occurrences) > 1 else "dispatched",
            run_id=run_id,
            window=window,
        )
        _open_assignment(connection, ctx, run_id=run_id, now=now)
    return {"run_id": run_id, "created": True, "reason": None}


def _existing_run_for(
    connection: Connection, owner_id: str, occurrences: Sequence[Occurrence]
) -> str | None:
    """The run an occurrence already produced, if any — the idempotent replay path."""
    for occurrence in occurrences:
        row = connection.execute(
            text(
                "SELECT coalesced_into_run_id FROM schedule_occurrence "
                "WHERE owner_id = :o AND id = :id AND coalesced_into_run_id IS NOT NULL"
            ),
            {"o": owner_id, "id": occurrence.occurrence_id},
        ).fetchone()
        if row is not None and row[0] is not None:
            return str(row[0])
    return None


def coalesce_overdue(ctx: JobContext, *, occurrences: Sequence[Occurrence]) -> dict[str, Any]:
    """``job.coalesce_overdue`` — many overdue slots, **exactly one** run.

    ``CU-01`` and ``schedule_max_runs_per_catch_up = 1``. The idempotency key is
    ``coalesce_window_id``, derived in
    :func:`server.app.scheduler.evaluator.coalesce_window_id` from the sorted set of
    occurrence ids, so two evaluators that see the same overdue set compute the same key and
    the second call is a replay.

    ``CU-02``: the run records ``schedule_occurrence_ids`` and the covering window
    ``[catch_up_window_from, catch_up_window_to]`` — the interval the Telegram message quotes
    (``REQ-D15``). ``CU-03`` is satisfied by there being one run and therefore one digest;
    this module creates no digest itself and holds no edge that could.
    """
    ctx.assert_writable(OperationId.JOB_COALESCE_OVERDUE)
    if not occurrences:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.JOB_COALESCE_OVERDUE.value,
                "field_path": "occurrences",
                "violation_kind": "empty",
            },
        )
    window_id = coalesce_window_id(occurrences)
    result = enqueue_scheduled_run(ctx, occurrences=occurrences)
    instants = sorted(o.due_at for o in occurrences)
    result["coalesce_window_id"] = window_id
    result["catch_up_window"] = {"from": instants[0], "to": instants[-1]}
    result["coalesced_occurrence_ids"] = [o.occurrence_id for o in occurrences]
    return result


def record_stale_occurrences(ctx: JobContext, *, occurrences: Sequence[Occurrence]) -> int:
    """``CU-04``: slots older than the lookback are ``skipped``, never coalesced.

    The contract's own word for the state is ``skipped_stale``, but ``entities.yaml`` closes
    the enum at ``due | coalesced | dispatched | skipped``. The Coordinator ruled that
    ``entities.yaml`` wins — it is what the schema gate reads — so the value written is
    ``skipped`` and the divergence is ``CR-TC-SCHED-03``. Recording them at all is the point:
    CU-04 requires ``health.get_readiness`` to be able to show them, and a skipped slot leaves
    no coverage hole because coverage is the ``coverage_window`` ledger's business, not the
    schedule's (B04).
    """
    if not occurrences:
        return 0
    ctx.assert_writable(OperationId.JOB_COALESCE_OVERDUE)
    with session_scope(ctx.engine) as connection:
        _record_occurrences(
            connection,
            owner_id=ctx.owner_id,
            occurrences=occurrences,
            state="skipped",
            run_id=None,
            window=None,
        )
    return len(occurrences)


def _open_assignment(connection: Connection, ctx: JobContext, *, run_id: str, now: datetime) -> str:
    """Create the ``collect``/``collecting`` assignment a collector can claim.

    ``ux_assignment_open`` is partial over ``available``/``claimed``, so re-opening after an
    abandoned attempt is legal while two open assignments for the same run and phase are not.
    """
    assignment_id = ctx.id_factory()
    connection.execute(
        text(
            "INSERT INTO assignment (id, owner_id, run_id, kind, phase, state, "
            "required_capabilities, created_at) VALUES (:id, :o, :run, 'collect', "
            "'collecting', 'available', :caps, :created)"
        ),
        {
            "id": assignment_id,
            "o": ctx.owner_id,
            "run": run_id,
            "caps": json.dumps(
                {"requires_chrome_profile": True, "requires_x_session_ok": True}, sort_keys=True
            ),
            "created": timestamp_utc_ms(now),
        },
    )
    return assignment_id


# --------------------------------------------------------------------------------------
# worker.register_capabilities
# --------------------------------------------------------------------------------------


def register_capabilities(ctx: JobContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``worker.register_capabilities`` — and **no lease** (LM-01).

    ``lease_granted: False`` is in the response as an explicit assertion, not as an omission:
    fixture ``collection/g-schedule-due-claim.json`` event 1 pins the field, and
    ``contracts/ops/deployment.md`` §7 step 6 makes "registration does not grant work" the
    thing that keeps a worker from starting on its own.

    Idempotency key: ``worker_instance_id + registration_seq``, rule *"Bản đăng ký mới ghi đè
    bản cũ của cùng worker_instance_id; seq lùi bị bỏ qua"*. A lower sequence is a **silent
    no-op**, not an error: registrations arrive out of order over a flaky link, and answering
    409 would make a worker retry a message that is genuinely obsolete.
    """
    ctx.assert_writable(OperationId.WORKER_REGISTER_CAPABILITIES)
    identity = _required(body, "worker_instance_id", OperationId.WORKER_REGISTER_CAPABILITIES)
    wire_kind = _required(body, "worker_kind", OperationId.WORKER_REGISTER_CAPABILITIES)
    if wire_kind not in WIRE_TO_STORED_WORKER_KIND:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.WORKER_REGISTER_CAPABILITIES.value,
                "field_path": "worker_kind",
                "violation_kind": "not_in_enum",
            },
        )
    sequence = int(body.get("registration_seq", 0))
    capabilities = dict(body.get("capabilities") or {})
    now = ctx.now()
    stored_kind = WIRE_TO_STORED_WORKER_KIND[wire_kind]

    with session_scope(ctx.engine) as connection:
        row = (
            connection.execute(
                text(
                    "SELECT id, capabilities FROM worker_registration "
                    "WHERE owner_id = :o AND worker_identity = :w"
                ),
                {"o": ctx.owner_id, "w": identity},
            )
            .mappings()
            .fetchone()
        )
        if row is not None:
            stored = json.loads(row["capabilities"])
            if int(stored.get("registration_seq", -1)) > sequence:
                return {
                    "registered_at": timestamp_utc_ms(now),
                    "heartbeat_interval_s": HEARTBEAT_INTERVAL_COLLECTOR_SECONDS,
                    "lease_granted": False,
                    "superseded": True,
                }
            connection.execute(
                text(
                    "UPDATE worker_registration SET worker_kind = :k, capabilities = :c, "
                    "last_heartbeat_at = :hb, online_state = 'online' "
                    "WHERE owner_id = :o AND worker_identity = :w"
                ),
                {
                    "k": stored_kind,
                    "c": _capability_blob(capabilities, sequence),
                    "hb": timestamp_utc_ms(now),
                    "o": ctx.owner_id,
                    "w": identity,
                },
            )
        else:
            connection.execute(
                text(
                    "INSERT INTO worker_registration (id, owner_id, worker_identity, "
                    "worker_kind, capabilities, last_heartbeat_at, online_state, last_run_at) "
                    "VALUES (:id, :o, :w, :k, :c, :hb, 'online', NULL)"
                ),
                {
                    "id": ctx.id_factory(),
                    "o": ctx.owner_id,
                    "w": identity,
                    "k": stored_kind,
                    "c": _capability_blob(capabilities, sequence),
                    "hb": timestamp_utc_ms(now),
                },
            )
    return {
        "registered_at": timestamp_utc_ms(now),
        "heartbeat_interval_s": HEARTBEAT_INTERVAL_COLLECTOR_SECONDS,
        "lease_granted": False,
    }


def _capability_blob(capabilities: Mapping[str, Any], sequence: int) -> str:
    payload = dict(capabilities)
    payload["registration_seq"] = sequence
    # D50/B12: a worker never declares `embedding`. Dropped rather than rejected, because the
    # claim is meaningless rather than malicious, and a 400 here would stop a worker from
    # registering at all over a field nobody reads.
    payload.pop("embedding", None)
    payload.pop("embedding_supported", None)
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def _required(body: Mapping[str, Any], key: str, operation: OperationId) -> str:
    value = body.get(key)
    if not isinstance(value, str) or not value:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": operation.value,
                "field_path": key,
                "violation_kind": "missing_or_empty",
            },
        )
    return value


# --------------------------------------------------------------------------------------
# worker.claim_assignment -- TXN-claim
# --------------------------------------------------------------------------------------


def _no_work(reason: str, *, backoff_index: int = -1) -> dict[str, Any]:
    if reason not in NO_WORK_REASONS:
        raise ValueError(f"{reason!r} is not a no_work reason of the wire schema")
    return {
        "no_work": {
            "reason": reason,
            "retry_after_ms": CLAIM_IDLE_BACKOFF_SECONDS[backoff_index] * 1000,
        }
    }


def claim_assignment(ctx: JobContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``worker.claim_assignment`` — ``TXN-claim``: one transaction, one CAS, one new epoch.

    **Commit point: the COMMIT of the single ``session_scope`` block below.**

    Returns either an ``assignment`` object or a ``no_work`` object, both validating against
    ``contracts/schemas/worker-assignment.schema.json``. The refusals, in order, and why each
    one is a ``no_work`` and not an error:

    ``storage_not_healthy``   storage is blocked or a restore is unreconciled. The worker
                              should come back, not fail.
    ``run_needs_user`` / ``run_blocked``  a run exists but is waiting for the Owner. The
                              worker must **not** claim it — that is T-RUN-11's "status query
                              does not resume" from the other side, and I10's reason for
                              existing.
    ``no_due_occurrence``     nothing to do.
    ``capability_not_met``    the assignment requires a Chrome profile or a healthy X session
                              the worker did not declare. ``ports.yaml``: "server chỉ giao
                              assignment mà worker khai đủ capability".
    ``assignment_already_held``  somebody else won. See the module docstring.

    ``claim_request_id`` is the idempotency key: the same key returns the same assignment
    without issuing a second lease, because a claim that times out leaves the worker not
    knowing whether it got one (``claim_request_timeout``, RP-01).
    """
    ctx.assert_writable(OperationId.WORKER_CLAIM_ASSIGNMENT)
    request = dict(body.get("claim_request") or body)
    claim_request_id = _required(request, "claim_request_id", OperationId.WORKER_CLAIM_ASSIGNMENT)
    identity = _required(request, "worker_instance_id", OperationId.WORKER_CLAIM_ASSIGNMENT)
    capabilities = dict(request.get("capabilities") or {})
    now = ctx.now()

    if ctx.restore_pending:
        # LM-08 / NC-10: claims are locked until `backup.reconcile_after_restore` runs. The
        # fixture pins RESTORE_UNVERIFIED (409) here rather than a `no_work`, because this is
        # an operator-decision state and not an idle poll.
        raise JobError(
            ErrorCode.RESTORE_UNVERIFIED,
            details_safe={"storage_health": "recovery_required"},
        )

    with session_scope(ctx.engine) as connection:
        held = _lease_held_by(connection, ctx.owner_id, claim_request_id)
        if held is not None:
            return held

        run = _active_run(connection, ctx.owner_id)
        if run is None:
            return _no_work("no_due_occurrence")
        if run["status"] in OWNER_WAIT_STATUSES:
            return _no_work("run_needs_user" if run["status"] == "needs_user" else "run_blocked")

        assignment = (
            connection.execute(
                text(
                    "SELECT id, run_id, phase, state, required_capabilities FROM assignment "
                    "WHERE owner_id = :o AND run_id = :r AND state IN ('available', 'claimed') "
                    "ORDER BY created_at, id LIMIT 1"
                ),
                {"o": ctx.owner_id, "r": run["id"]},
            )
            .mappings()
            .fetchone()
        )
        if assignment is None:
            return _no_work("no_due_occurrence")

        missing = _unmet_capabilities(json.loads(assignment["required_capabilities"]), capabilities)
        if missing:
            return _no_work("capability_not_met")

        current = _lease_of(connection, ctx.owner_id, assignment["id"])
        epoch = 1 if current is None else next_epoch(current.lease_epoch)
        if current is not None and current.state is LeaseState.HELD:
            if not is_expired(current, now):
                return _no_work("assignment_already_held")
            # T-RUN-14 in the claim path: the previous holder's lease lapsed, so it is
            # retired here rather than by a separate sweep, and the epoch moves with it.
            state, epoch = revoke(current, to=LeaseState.EXPIRED)
            connection.execute(
                text("UPDATE assignment_lease SET state = :s WHERE id = :id"),
                {"s": state.value, "id": current.id},
            )

        lease_id = ctx.id_factory()
        expires_at = expiry_from(now, ttl_seconds=LEASE_TTL_COLLECTOR_SECONDS)
        try:
            connection.execute(
                text(
                    "INSERT INTO assignment_lease (id, owner_id, run_id, job_id, "
                    "worker_identity, lease_epoch, expires_at, state) "
                    "VALUES (:id, :o, :run, :job, :w, :e, :exp, 'held')"
                ),
                {
                    "id": lease_id,
                    "o": ctx.owner_id,
                    "run": run["id"],
                    "job": assignment["id"],
                    "w": identity,
                    "e": epoch,
                    "exp": timestamp_utc_ms(expires_at),
                },
            )
        except IntegrityError:
            # `ux_assignment_lease_one_held` refused a second holder. The database decided the
            # race; this branch only reports it. Not an error to the worker (see the docstring).
            connection.rollback()
            return _no_work("assignment_already_held")

        connection.execute(
            text("UPDATE assignment SET state = 'claimed' WHERE owner_id = :o AND id = :id"),
            {"o": ctx.owner_id, "id": assignment["id"]},
        )
        # T-RUN-01. `attempt_count` moves here because this is the moment a run leaves
        # `queued`, which is what `entities.yaml` says the counter counts.
        connection.execute(
            text(
                "UPDATE run SET status = 'running', phase = :p, current_lease_epoch = :e, "
                "attempt_count = attempt_count + 1, next_attempt_at = NULL "
                "WHERE owner_id = :o AND id = :id"
            ),
            {"p": assignment["phase"], "e": epoch, "o": ctx.owner_id, "id": run["id"]},
        )
        connection.execute(
            text(
                "UPDATE worker_registration SET last_run_at = :at, online_state = 'online' "
                "WHERE owner_id = :o AND worker_identity = :w"
            ),
            {"at": timestamp_utc_ms(now), "o": ctx.owner_id, "w": identity},
        )
        payload = _assignment_payload(
            ctx,
            connection,
            assignment_id=assignment["id"],
            run=run,
            phase=str(assignment["phase"]),
            lease=Lease(
                id=lease_id,
                owner_id=ctx.owner_id,
                run_id=str(run["id"]),
                job_id=str(assignment["id"]),
                worker_identity=identity,
                lease_epoch=epoch,
                expires_at=expires_at,
                state=LeaseState.HELD,
            ),
        )
    return payload


def _lease_held_by(
    connection: Connection, owner_id: str, claim_request_id: str
) -> dict[str, Any] | None:
    """The idempotent replay of a claim.

    ``claim_request_id`` is not a stored column — ``ENT-assignment-lease`` has no field for
    it — so the replay is recognised by the ``Idempotency-Key`` the router carries and this
    function is the seam where a stored-key implementation will drop in. Today it returns
    ``None``, and the duplicate-claim safety comes from ``ux_assignment_lease_one_held``: a
    replayed claim finds the lease held and answers ``assignment_already_held`` rather than
    issuing a second one. **Recorded as a limitation** in the handoff: the contract's
    "cùng claim_request_id trả cùng assignment" is satisfied in effect (no second lease) but
    not in form (the same assignment object is not returned), which needs a column
    ``entities.yaml`` does not currently declare — ``CR-TC-SCHED-05``.
    """
    return None


def _unmet_capabilities(required: Mapping[str, Any], declared: Mapping[str, Any]) -> list[str]:
    """Which required capabilities the worker did not declare.

    ``requires_x_session_ok`` is satisfied only by the literal ``"ok"``: ``challenge``,
    ``expired`` and ``unknown`` are all "not ok", and treating ``unknown`` as usable would
    hand work to a session nobody has checked (I13's three-way distinction, applied here).
    """
    missing: list[str] = []
    if required.get("requires_chrome_profile") and not declared.get("chrome_profile_ready"):
        missing.append("chrome_profile_ready")
    if required.get("requires_x_session_ok") and declared.get("x_session_state") != "ok":
        missing.append("x_session_state")
    if not declared.get("collector_online", False):
        missing.append("collector_online")
    return missing


def _assignment_payload(
    ctx: JobContext,
    connection: Connection,
    *,
    assignment_id: str,
    run: Mapping[str, Any],
    phase: str,
    lease: Lease,
) -> dict[str, Any]:
    """The ``assignment`` object of ``worker-assignment.schema.json``.

    The checkpoint block comes from ``ingest.get_checkpoint`` through the port and is
    projected to exactly the schema's six properties — the ingest service also returns
    ``created_at``, and the schema is ``additionalProperties: false``, so passing its dict
    through unfiltered would produce an invalid payload.
    """
    checkpoint = _checkpoint_for(ctx, run_id=str(run["id"]), phase=phase)
    config = json.loads(run["applied_config"])
    occurrence_ids = json.loads(run["schedule_occurrence_ids"])
    catch_up = None
    if run["catch_up_window_from"] is not None:
        catch_up = {"from": run["catch_up_window_from"], "to": run["catch_up_window_to"]}
    return {
        "assignment": {
            "assignment_id": assignment_id,
            "run_id": run["id"],
            "phase": phase,
            "trigger_type": run["trigger_type"],
            "catch_up_window": catch_up,
            "lease": lease.wire(),
            "capability_requirements": json.loads(
                connection.execute(
                    text("SELECT required_capabilities FROM assignment WHERE id = :id"),
                    {"id": assignment_id},
                ).scalar_one()
            ),
            "search_config": {
                "tags": [],
                "tag_config_version_id": None,
                "source_limits": {},
            },
            "stop_conditions": {
                "max_posts": config.get("per_run_post_limit", ctx.limits.max_posts),
                "max_duration_s": config.get("per_run_duration_limit_s", ctx.limits.max_duration_s),
                "evaluation": "first_of_either",
                "on_challenge": "report_stop_and_halt",
                "on_blocked": "report_stop_and_halt_no_rotation",
            },
            "checkpoint": checkpoint,
            "is_resume": bool(occurrence_ids) and int(run["attempt_count"]) > 0,
        }
    }


def _checkpoint_for(ctx: JobContext, *, run_id: str, phase: str) -> dict[str, Any]:
    """The ``server_checkpoint`` block: the server's ACKed truth, never the worker's memory.

    An absent checkpoint is the empty-new one (``checkpoint_sequence: 0``), which the schema
    describes for a run that has ingested nothing. It is **not** an error: a first claim
    legitimately has no checkpoint, and refusing would make a fresh run unclaimable.
    """
    empty = {
        "phase": phase,
        "cursor_token": None,
        "cursor_state": "valid",
        "acked_through_ingest_sequence": 0,
        "items_ingested_total": 0,
        "checkpoint_sequence": 0,
    }
    if ctx.checkpoint_port is None:
        return empty
    stored = ctx.checkpoint_port.get_checkpoint(run_id=run_id)
    if stored is None:
        return empty
    return {key: stored.get(key, empty[key]) for key in empty}


# --------------------------------------------------------------------------------------
# worker.heartbeat / report_stop / release_assignment
# --------------------------------------------------------------------------------------


def heartbeat(ctx: JobContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``worker.heartbeat`` — renew the lease, or refuse and change nothing.

    LM-04 in its purest form: :func:`~server.app.jobs.lease.assert_current_lease` runs
    **before** the UPDATE and inside the same transaction, so a stale beat leaves
    ``expires_at`` untouched. Fixture
    ``collection/f-two-workers-claim-same-assignment.json`` event 2 pins exactly that: worker
    A at epoch 1 gets 409 ``STALE_LEASE`` and "KHÔNG gia hạn lease, KHÔNG đổi dữ liệu".

    The response's ``directive`` is how a cancelled run reaches a worker that is still
    running: ``run.cancel`` cannot stop a process, so T-RUN-17b's effect is delivered on the
    next beat as ``stop_cancelled``.
    """
    request = dict(body.get("heartbeat_request") or body)
    lease_id = _required(request, "lease_id", OperationId.WORKER_HEARTBEAT)
    epoch = int(request.get("lease_epoch", -1))
    now = ctx.now()
    with session_scope(ctx.engine) as connection:
        lease = _lease_by_id(connection, ctx.owner_id, lease_id)
        assert_current_lease(
            lease,
            presented_epoch=epoch,
            job_id=str(lease.job_id) if lease else "",
            now=now,
            restore_pending=ctx.restore_pending,
            operation_id=OperationId.WORKER_HEARTBEAT.value,
        )
        assert lease is not None  # noqa: S101 - assert_current_lease raised otherwise
        run = _run_row(connection, ctx.owner_id, lease.run_id)
        if run is not None and run["status"] == "cancelled":
            return {
                "heartbeat_response": {
                    "lease_valid": False,
                    "directive": "stop_cancelled",
                }
            }
        expires_at = expiry_from(now, ttl_seconds=LEASE_TTL_COLLECTOR_SECONDS)
        connection.execute(
            text("UPDATE assignment_lease SET expires_at = :e WHERE id = :id"),
            {"e": timestamp_utc_ms(expires_at), "id": lease.id},
        )
        connection.execute(
            text(
                "UPDATE worker_registration SET last_heartbeat_at = :hb, online_state = 'online' "
                "WHERE owner_id = :o AND worker_identity = :w"
            ),
            {"hb": timestamp_utc_ms(now), "o": ctx.owner_id, "w": lease.worker_identity},
        )
    return {
        "heartbeat_response": {
            "lease_valid": True,
            "lease_expires_at": timestamp_utc_ms(expires_at),
            "directive": "continue",
        }
    }


def report_stop(ctx: JobContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``worker.report_stop`` — report and halt. Never a prelude to a retry.

    The ``stop_reason`` the collector sends chooses nothing on its own:
    :data:`STOP_REASON_EFFECT` maps it to the ``(status, stop_reason)`` pair
    ``contracts/state/run.yaml`` assigns, which is what keeps T-RUN-09, T-RUN-16, T-RUN-24 and
    T-RUN-25 in one place. ``source_blocked`` records ``unblock_condition_vi`` and does **not**
    rotate an account or a proxy — ``ports.yaml`` says so in as many words.

    At most one alert intent per run (``REQ-AC04``, ``delivery_alert_per_run = 1``): the
    second ``report_stop`` for the same run reports ``alert_created: False``. The uniqueness
    lives on ``outbox_intent``; this only records the pointer.
    """
    ctx.assert_writable(OperationId.WORKER_REPORT_STOP)
    lease_id = _required(body, "lease_id", OperationId.WORKER_REPORT_STOP)
    epoch = int(body.get("lease_epoch", -1))
    reason = _required(body, "stop_reason", OperationId.WORKER_REPORT_STOP)
    if reason not in STOP_REASON_EFFECT:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.WORKER_REPORT_STOP.value,
                "field_path": "stop_reason",
                "violation_kind": "not_in_enum",
            },
        )
    now = ctx.now()
    status, stored_reason = STOP_REASON_EFFECT[reason]
    with session_scope(ctx.engine) as connection:
        lease = _lease_by_id(connection, ctx.owner_id, lease_id)
        assert_current_lease(
            lease,
            presented_epoch=epoch,
            job_id=str(lease.job_id) if lease else "",
            now=now,
            restore_pending=ctx.restore_pending,
            operation_id=OperationId.WORKER_REPORT_STOP.value,
        )
        assert lease is not None  # noqa: S101 - assert_current_lease raised otherwise
        run = _run_row(connection, ctx.owner_id, lease.run_id)
        if run is None:
            raise JobError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.WORKER_REPORT_STOP.value,
                    "resource_kind": "run",
                },
            )
        unblock = (
            "X đang chặn truy cập; cần bạn xác nhận đã xử lý trước khi chạy lại."
            if status == "blocked"
            else None
        )
        connection.execute(
            text(
                "UPDATE run SET status = :s, stop_reason = :r, unblock_condition_vi = :u, "
                "rate_limited_at = CASE WHEN :r = 'rate_limited' THEN :now "
                "ELSE rate_limited_at END WHERE owner_id = :o AND id = :id"
            ),
            {
                "s": status,
                "r": stored_reason,
                "u": unblock,
                "now": timestamp_utc_ms(now),
                "o": ctx.owner_id,
                "id": run["id"],
            },
        )
        alert_created = False
        if (
            status in OWNER_WAIT_STATUSES
            and ctx.alert_port is not None
            and run["alert_intent_id"] is None
        ):
            intent_id = ctx.alert_port.create_alert_intent(
                run_id=str(run["id"]), stop_reason=stored_reason
            )
            if intent_id is not None:
                connection.execute(
                    text("UPDATE run SET alert_intent_id = :i WHERE owner_id = :o AND id = :id"),
                    {"i": intent_id, "o": ctx.owner_id, "id": run["id"]},
                )
                alert_created = True
    return {"run_status": status, "stop_reason": stored_reason, "alert_created": alert_created}


def release_assignment(ctx: JobContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``worker.release_assignment`` — revoke the lease and bump the epoch (LM-06).

    Idempotent on ``assignment_id``: releasing twice does not change state after the first,
    which is why the second call reports ``released: False`` rather than failing. Un-ACKed
    work is **not** treated as saved — this module writes no research row, and the ACKed
    watermark is ``MOD-ingest-service``'s checkpoint, so "released" says nothing about data.
    """
    ctx.assert_writable(OperationId.WORKER_RELEASE_ASSIGNMENT)
    request = dict(body.get("release_request") or body)
    lease_id = _required(request, "lease_id", OperationId.WORKER_RELEASE_ASSIGNMENT)
    epoch = int(request.get("lease_epoch", -1))
    now = ctx.now()
    with session_scope(ctx.engine) as connection:
        lease = _lease_by_id(connection, ctx.owner_id, lease_id)
        if lease is not None and lease.state is not LeaseState.HELD:
            return {"released": False, "lease_epoch": lease.lease_epoch}
        assert_current_lease(
            lease,
            presented_epoch=epoch,
            job_id=str(lease.job_id) if lease else "",
            now=now,
            restore_pending=ctx.restore_pending,
            operation_id=OperationId.WORKER_RELEASE_ASSIGNMENT.value,
        )
        assert lease is not None  # noqa: S101 - assert_current_lease raised otherwise
        state, new_epoch = revoke(lease, to=LeaseState.RELEASED)
        connection.execute(
            text("UPDATE assignment_lease SET state = :s WHERE id = :id"),
            {"s": state.value, "id": lease.id},
        )
        connection.execute(
            text("UPDATE assignment SET state = 'available' WHERE owner_id = :o AND id = :id"),
            {"o": ctx.owner_id, "id": lease.job_id},
        )
        connection.execute(
            text("UPDATE run SET current_lease_epoch = :e WHERE owner_id = :o AND id = :id"),
            {"e": new_epoch, "o": ctx.owner_id, "id": lease.run_id},
        )
    return {"released": True, "lease_epoch": new_epoch}


def sweep_expired_leases(ctx: JobContext) -> dict[str, Any]:
    """T-RUN-14 / T-RUN-15 / T-RUN-20 — the ``lease_expiry_sweep_interval`` pass.

    A lease past ``expires_at + heartbeat_grace`` is retired, its epoch bumped, and the run
    returned to ``queued`` — **unless** ``worker.report_stop`` already committed
    ``needs_user`` or ``blocked``, in which case T-RUN-15 keeps the stored state. That
    exception is the whole difference between "the worker died" and "the Owner has to act",
    and getting it wrong would silently discard a challenge the Owner still has to clear.
    """
    now = ctx.now()
    expired = 0
    requeued = 0
    with session_scope(ctx.engine) as connection:
        rows = (
            connection.execute(
                text(
                    f"SELECT {_LEASE_COLUMNS} FROM assignment_lease "
                    "WHERE owner_id = :o AND state = 'held'"
                ),
                {"o": ctx.owner_id},
            )
            .mappings()
            .fetchall()
        )
        for row in rows:
            lease = Lease(
                id=row["id"],
                owner_id=row["owner_id"],
                run_id=row["run_id"],
                job_id=row["job_id"],
                worker_identity=row["worker_identity"],
                lease_epoch=int(row["lease_epoch"]),
                expires_at=parse_timestamp_utc_ms(row["expires_at"]),
                state=LeaseState(row["state"]),
            )
            if not is_expired(lease, now):
                continue
            state, new_epoch = revoke(lease, to=LeaseState.EXPIRED)
            connection.execute(
                text("UPDATE assignment_lease SET state = :s WHERE id = :id"),
                {"s": state.value, "id": lease.id},
            )
            connection.execute(
                text("UPDATE assignment SET state = 'available' WHERE owner_id = :o AND id = :id"),
                {"o": ctx.owner_id, "id": lease.job_id},
            )
            expired += 1
            run = _run_row(connection, ctx.owner_id, lease.run_id)
            if run is None:
                continue
            connection.execute(
                text("UPDATE run SET current_lease_epoch = :e WHERE owner_id = :o AND id = :id"),
                {"e": new_epoch, "o": ctx.owner_id, "id": run["id"]},
            )
            if run["status"] in OWNER_WAIT_STATUSES or run["status"] in TERMINAL_RUN_STATUSES:
                continue  # T-RUN-15: the stored stop wins.
            connection.execute(
                text(
                    "UPDATE run SET status = 'queued', stop_reason = 'worker_lost' "
                    "WHERE owner_id = :o AND id = :id"
                ),
                {"o": ctx.owner_id, "id": run["id"]},
            )
            requeued += 1
    return {"leases_expired": expired, "runs_requeued": requeued}


# --------------------------------------------------------------------------------------
# run.* -- the Owner-facing operations
# --------------------------------------------------------------------------------------


def _run_view(row: Mapping[str, Any]) -> dict[str, Any]:
    """The read model of ``run.list``/``run.get``.

    The three states ``I13`` requires to look different — empty period, stopped at a limit,
    failed — are carried as the **triple** ``(status, outcome, stop_reason)`` rather than
    flattened into one label here. Flattening is the UI's job (card ``TC-ui-runs-three-states``)
    and doing it in the read model would decide the distinction in the wrong place.
    """
    return {
        "run_id": row["id"],
        "trigger_type": row["trigger_type"],
        "phase": row["phase"],
        "status": row["status"],
        "outcome": row["outcome"],
        "stop_reason": row["stop_reason"],
        "created_at": row["created_at"],
        "attempt_count": row["attempt_count"],
        "schedule_occurrence_ids": json.loads(row["schedule_occurrence_ids"]),
        "catch_up_window": (
            None
            if row["catch_up_window_from"] is None
            else {"from": row["catch_up_window_from"], "to": row["catch_up_window_to"]}
        ),
        "posts_observed_total": row["posts_observed_total"],
        "posts_ingested_new": row["posts_ingested_new"],
        "limit_hit": bool(row["limit_hit"]),
        "limit_kind": row["limit_kind"],
        "cursor_invalidated": bool(row["cursor_invalidated"]),
        "x_coverage_note_vi": row["x_coverage_note_vi"],
        "unblock_condition_vi": row["unblock_condition_vi"],
        "last_error_code": row["last_error_code"],
    }


def list_runs(ctx: JobContext, *, limit: int = 50) -> dict[str, Any]:
    """``run.list`` — read-only. B10: the Telegram ``status`` command mutates nothing."""
    with ctx.engine.connect() as connection:
        rows = (
            connection.execute(
                text(
                    f"SELECT {_RUN_COLUMNS} FROM run WHERE owner_id = :o "
                    "ORDER BY created_at DESC, id DESC LIMIT :n"
                ),
                {"o": ctx.owner_id, "n": max(1, min(limit, 200))},
            )
            .mappings()
            .fetchall()
        )
    return {"runs": [_run_view(dict(row)) for row in rows]}


def get_run(ctx: JobContext, *, run_id: str) -> dict[str, Any]:
    """``run.get`` — read-only, and redacted by construction.

    ``ports.yaml`` asks for the log "đã che secrets". This read model carries no log field at
    all: there is no redaction step to forget, because there is nothing to redact.
    """
    with ctx.engine.connect() as connection:
        row = _run_row(connection, ctx.owner_id, run_id)
    if row is None:
        raise JobError(
            ErrorCode.NOT_FOUND,
            details_safe={"operation_id": OperationId.RUN_GET.value, "resource_kind": "run"},
        )
    view = _run_view(row)
    view["applied_config"] = json.loads(row["applied_config"])
    return view


def run_now(ctx: JobContext, *, request_id: str) -> dict[str, Any]:
    """``run.run_now`` — coalesce onto the active run, never create a second one.

    ``run_now_active_run_policy = coalesce`` and ``ports.yaml``'s "bấm lặp trả run đang có".
    T-RUN-21 makes this a **no-op transition**: status, phase, outcome and stop_reason are all
    unchanged, which is why this function does not write when a run is active.

    B10/AMD-B10 is the sharp edge: pressing "run now" while the run is ``needs_user`` must not
    resume it. Fixture ``collection/i-run-now-while-active.json`` presses five times from two
    different channels and pins ``run_created_by_these_events: 0`` with every response
    carrying the same ``run_id``; ``forbidden_effects`` lists both "tạo run thứ hai" and
    "resume một run đang needs_user". Returning early — before any UPDATE — is what makes the
    transition log empty rather than merely idempotent.
    """
    ctx.assert_writable(OperationId.RUN_RUN_NOW)
    if not request_id:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.RUN_RUN_NOW.value,
                "field_path": "request_id",
                "violation_kind": "missing_or_empty",
            },
        )
    now = ctx.now()
    with session_scope(ctx.engine) as connection:
        active = _active_run(connection, ctx.owner_id)
        if active is not None:
            return {
                "run_id": active["id"],
                "created": False,
                "reason": f"run_already_{active['status']}",
                "status": active["status"],
            }
        run_id = ctx.id_factory()
        _insert_run(
            connection,
            run_id=run_id,
            owner_id=ctx.owner_id,
            trigger_type="manual",
            created_at=timestamp_utc_ms(now),
            occurrence_ids=[],
            window=None,
            applied_config=_applied_config(ctx),
        )
        _open_assignment(connection, ctx, run_id=run_id, now=now)
    return {"run_id": run_id, "created": True, "reason": None, "status": "queued"}


def resume_run(
    ctx: JobContext, *, run_id: str, unblock_reason: str | None = None
) -> dict[str, Any]:
    """``run.resume`` — T-RUN-10 from ``needs_user``, T-RUN-23 from ``blocked``.

    **T-RUN-23 exists.** Card §10 ``SG-01`` says no operation may take a run out of
    ``blocked`` except ``run.cancel``, and cites ``CR-PC03-02`` as open. The pinned
    ``contracts/state/run.yaml`` disagrees: T-RUN-23 moves ``blocked → queued`` on
    ``owner_declares_unblocked``, and ``ports.yaml`` ``run.resume`` documents the mandatory
    ``unblock_reason`` for exactly that path. The Coordinator ruled the pinned contract wins,
    so this implements it and the stale card prose is ``CR-TC-SCHED-02``. No operation is
    invented here — the one being implemented is in both contract files.

    ``unblock_reason`` is **mandatory** from ``blocked`` and refused as ``VALIDATION_ERROR``
    when absent: the Owner is declaring a fact about the outside world, and an empty
    declaration would let a blocked run loop forever with nothing recorded about why anyone
    thought it would work this time.

    LM-07: resume never continues on the old lease. Any held lease is revoked here (epoch +1),
    so the worker must claim again and receives a fresh one.
    """
    ctx.assert_writable(OperationId.RUN_RESUME)
    with session_scope(ctx.engine) as connection:
        run = _run_row(connection, ctx.owner_id, run_id)
        if run is None:
            raise JobError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.RUN_RESUME.value,
                    "resource_kind": "run",
                },
            )
        status = str(run["status"])
        if status not in OWNER_WAIT_STATUSES:
            raise JobError(
                ErrorCode.CONFLICT,
                details_safe={"resource_kind": "run", "attempt_number": run["attempt_count"]},
            )
        if status == "blocked" and not (unblock_reason or "").strip():
            raise JobError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.RUN_RESUME.value,
                    "field_path": "unblock_reason",
                    "violation_kind": "missing_or_empty",
                },
            )
        epoch = _revoke_leases_of_run(connection, ctx, run_id=run_id)
        connection.execute(
            text(
                "UPDATE run SET status = 'queued', stop_reason = NULL, "
                "unblock_condition_vi = NULL, next_attempt_at = NULL, current_lease_epoch = :e "
                "WHERE owner_id = :o AND id = :id"
            ),
            {"e": epoch, "o": ctx.owner_id, "id": run_id},
        )
    return {"run_id": run_id, "status": "queued", "current_lease_epoch": epoch}


def cancel_run(ctx: JobContext, *, run_id: str) -> dict[str, Any]:
    """``run.cancel`` — T-RUN-17a/b/c: cancellable from **every** non-terminal status.

    Fixture ``collection/k-cancel-from-every-non-terminal.json`` cancels five runs, one in
    each non-terminal status, and pins ``run_cancelled: 5``, ``post_deleted: 0``,
    ``analysis_deleted: 0``, ``assignment_lease_held: 0``. This function therefore does three
    things and no more: set ``(cancelled, cancelled)``, revoke every lease of the run (LM-06,
    epoch +1), and close the assignment. **It deletes nothing** — the fixture's first
    forbidden effect is "Xóa dữ liệu đã commit khi cancel", and committed research data
    outlives the run that collected it.

    Idempotent: cancelling an already-cancelled run returns the same answer without a second
    transition, which is ``ports.yaml``'s "Hủy lại run đã cancelled trả kết quả idempotent".
    """
    ctx.assert_writable(OperationId.RUN_CANCEL)
    with session_scope(ctx.engine) as connection:
        run = _run_row(connection, ctx.owner_id, run_id)
        if run is None:
            raise JobError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.RUN_CANCEL.value,
                    "resource_kind": "run",
                },
            )
        if run["status"] == "cancelled":
            return {
                "run_id": run_id,
                "status": "cancelled",
                "outcome": "cancelled",
                "already_cancelled": True,
            }
        if run["status"] in TERMINAL_RUN_STATUSES:
            raise JobError(
                ErrorCode.CONFLICT,
                details_safe={"resource_kind": "run", "attempt_number": run["attempt_count"]},
            )
        epoch = _revoke_leases_of_run(connection, ctx, run_id=run_id)
        connection.execute(
            text(
                "UPDATE run SET status = 'cancelled', outcome = 'cancelled', "
                "next_attempt_at = NULL, unblock_condition_vi = NULL, current_lease_epoch = :e "
                "WHERE owner_id = :o AND id = :id"
            ),
            {"e": epoch, "o": ctx.owner_id, "id": run_id},
        )
        connection.execute(
            text(
                "UPDATE assignment SET state = 'abandoned' WHERE owner_id = :o AND run_id = :r "
                "AND state IN ('available', 'claimed')"
            ),
            {"o": ctx.owner_id, "r": run_id},
        )
    return {
        "run_id": run_id,
        "status": "cancelled",
        "outcome": "cancelled",
        "already_cancelled": False,
    }


def _revoke_leases_of_run(connection: Connection, ctx: JobContext, *, run_id: str) -> int:
    """Revoke every ``held`` lease of a run and return the new epoch (LM-06/LM-07).

    Returns the highest new epoch so the caller can write it to ``run.current_lease_epoch``,
    which is what makes a later beat from the old holder land behind the current epoch and be
    refused by :func:`~server.app.jobs.lease.assert_current_lease`.
    """
    rows = connection.execute(
        text(
            "SELECT id, lease_epoch FROM assignment_lease "
            "WHERE owner_id = :o AND run_id = :r AND state = 'held'"
        ),
        {"o": ctx.owner_id, "r": run_id},
    ).fetchall()
    highest = 0
    for lease_id, epoch in rows:
        new_epoch = next_epoch(int(epoch))
        connection.execute(
            text("UPDATE assignment_lease SET state = 'revoked' WHERE id = :id"),
            {"id": lease_id},
        )
        highest = max(highest, new_epoch)
    if highest:
        return highest
    current = connection.execute(
        text("SELECT current_lease_epoch FROM run WHERE owner_id = :o AND id = :id"),
        {"o": ctx.owner_id, "id": run_id},
    ).scalar_one()
    return int(current)


def get_worker_status(ctx: JobContext) -> dict[str, Any]:
    """``worker.get_status`` — read-only; ``online``/``offline``/``unknown``, never two.

    I13: ``unknown`` is a third answer and must not be rendered as ``offline``. It is what a
    worker that has never sent a heartbeat gets — "we have not heard from it" is not the same
    claim as "it is down", and collapsing them would report a fact nobody measured.
    The online threshold is ``contracts/ops/deployment.md``'s 90 s.
    """
    now = ctx.now()
    with ctx.engine.connect() as connection:
        rows = (
            connection.execute(
                text(
                    "SELECT worker_identity, worker_kind, capabilities, last_heartbeat_at, "
                    "online_state, last_run_at FROM worker_registration WHERE owner_id = :o "
                    "ORDER BY worker_identity"
                ),
                {"o": ctx.owner_id},
            )
            .mappings()
            .fetchall()
        )
    workers = []
    for row in rows:
        last = row["last_heartbeat_at"]
        if last is None:
            state = "unknown"
        else:
            age = (now - parse_timestamp_utc_ms(last)).total_seconds()
            state = "online" if age <= ONLINE_THRESHOLD_SECONDS else "offline"
        capabilities = json.loads(row["capabilities"])
        workers.append(
            {
                "worker_identity": row["worker_identity"],
                "worker_kind": STORED_TO_WIRE_WORKER_KIND[row["worker_kind"]],
                "online_state": state,
                "last_seen_at": last,
                "last_run_at": row["last_run_at"],
                "x_session_state": capabilities.get("x_session_state", "unknown"),
                "capabilities": capabilities,
            }
        )
    return {"workers": workers}


#: ``contracts/ops/deployment.md`` §6: a worker is ``online`` if its last heartbeat is within
#: 90 s. Referenced, not redefined -- ``lease_ttl_collector`` (120 s) is deliberately larger,
#: so a worker can read as ``offline`` while its lease is still valid, and that is correct:
#: the two answer different questions.
ONLINE_THRESHOLD_SECONDS: int = 90


__all__ = [
    "NON_TERMINAL_RUN_STATUSES",
    "NO_WORK_REASONS",
    "ONLINE_THRESHOLD_SECONDS",
    "STOP_REASON_EFFECT",
    "TERMINAL_RUN_STATUSES",
    "WIRE_TO_STORED_WORKER_KIND",
    "AlertIntentPort",
    "CheckpointPort",
    "JobContext",
    "RunLimits",
    "StorageGuardPort",
    "cancel_run",
    "claim_assignment",
    "coalesce_overdue",
    "enqueue_scheduled_run",
    "get_run",
    "get_worker_status",
    "heartbeat",
    "list_runs",
    "record_stale_occurrences",
    "register_capabilities",
    "release_assignment",
    "report_stop",
    "resume_run",
    "run_now",
    "sweep_expired_leases",
]
