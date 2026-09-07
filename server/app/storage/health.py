"""``storage.health`` state machine — ``T-ST-01`` .. ``T-ST-09``.

Oracle: ``contracts/state/storage.yaml`` (``CT-state-storage`` 0.3.0). Every constant,
transition and refusal below is a transcription of that file; where a number appears it
comes from ``contracts/retry-policy.yaml``. Nothing here is invented, and nothing here is
tuned: to change behaviour, change the contract and regenerate the card.

Why this module touches no database
-----------------------------------
``T-ST-01.transaction_vi`` is explicit: *"KHÔNG có transaction DB. Trạng thái này được giữ
TRONG BỘ NHỚ tiến trình"*. ``forbidden_transitions`` row 4 makes it a contract violation to
require a DB write before a state takes effect -- a system that waits to persist
``storage_health`` before refusing claims keeps granting leases while it waits, which is
exactly what invariant ``I02`` forbids. So this class holds its state in attributes, and
the health channel (``server/app/health/router.py``) reads it from memory.

The four states and what each refuses live in :data:`REFUSALS`; the nine legal edges live
in :data:`TRANSITIONS`. Any edge not in that tuple raises :class:`ForbiddenTransition` --
the machine is closed, not permissive, because the dangerous failures here are *extra*
edges (``recovery_required -> healthy`` without reconciliation replays a stale outbox).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth

# --------------------------------------------------------------------------------------
# Tuning values -- contracts/retry-policy.yaml, all three marked PROVISIONAL there
# (PROVISIONAL means "not yet calibrated against real data", not "not yet approved":
# contracts/state/storage.yaml `ratification.tuning_values_vi`).
# --------------------------------------------------------------------------------------

#: `storage_recovery_probe` -- seconds between write probes while `write_blocked`.
PROBE_INTERVAL_SECONDS: int = 30

#: `storage_recovery_probe_consecutive_success` -- probes needed to leave `write_blocked`.
#: One success on a nearly-full disk proves nothing; 3 x 30 s ~= 90 s is the contract's
#: answer to a disk that oscillates.
PROBE_CONSECUTIVE_SUCCESS: int = 3

#: `storage_write_blocked_grace_before_refusing_claims` -- deliberately zero. A positive
#: grace would grant a lease it cannot write to disk, which is what I02 forbids.
WRITE_BLOCKED_GRACE_SECONDS: int = 0


class StorageEvent(str, Enum):
    """The `event` column of ``contracts/state/storage.yaml`` §3."""

    WRITE_FAILURE_DETECTED = "write_failure_detected"
    PROBE_SUCCESS_STREAK = "probe_success_streak"
    OPERATOR_OPENS_MAINTENANCE = "operator_opens_maintenance"
    MAINTENANCE_WINDOW_CLOSED = "maintenance_window_closed"
    RESTORE_EXECUTED = "restore_executed"
    RECONCILE_COMPLETED = "reconcile_completed"
    WRITE_FAILURE_DURING_RECOVERY = "write_failure_during_recovery"
    PROBE_SUCCESS_WITH_PENDING_RESTORE = "probe_success_with_pending_restore"
    OPERATOR_OPENS_MAINTENANCE_TO_FIX = "operator_opens_maintenance_to_fix"


@dataclass(frozen=True)
class Transition:
    """One row of ``contracts/state/storage.yaml`` §3."""

    id: str
    source: StorageHealth
    event: StorageEvent
    target: StorageHealth


#: The nine legal transitions, in contract order. This tuple IS the allowlist.
TRANSITIONS: tuple[Transition, ...] = (
    Transition(
        "T-ST-01",
        StorageHealth.HEALTHY,
        StorageEvent.WRITE_FAILURE_DETECTED,
        StorageHealth.WRITE_BLOCKED,
    ),
    Transition(
        "T-ST-02",
        StorageHealth.WRITE_BLOCKED,
        StorageEvent.PROBE_SUCCESS_STREAK,
        StorageHealth.HEALTHY,
    ),
    Transition(
        "T-ST-03",
        StorageHealth.HEALTHY,
        StorageEvent.OPERATOR_OPENS_MAINTENANCE,
        StorageHealth.MAINTENANCE,
    ),
    Transition(
        "T-ST-04",
        StorageHealth.MAINTENANCE,
        StorageEvent.MAINTENANCE_WINDOW_CLOSED,
        StorageHealth.HEALTHY,
    ),
    Transition(
        "T-ST-05",
        StorageHealth.MAINTENANCE,
        StorageEvent.RESTORE_EXECUTED,
        StorageHealth.RECOVERY_REQUIRED,
    ),
    Transition(
        "T-ST-06",
        StorageHealth.RECOVERY_REQUIRED,
        StorageEvent.RECONCILE_COMPLETED,
        StorageHealth.HEALTHY,
    ),
    Transition(
        "T-ST-07",
        StorageHealth.RECOVERY_REQUIRED,
        StorageEvent.WRITE_FAILURE_DURING_RECOVERY,
        StorageHealth.WRITE_BLOCKED,
    ),
    Transition(
        "T-ST-08",
        StorageHealth.WRITE_BLOCKED,
        StorageEvent.PROBE_SUCCESS_WITH_PENDING_RESTORE,
        StorageHealth.RECOVERY_REQUIRED,
    ),
    Transition(
        "T-ST-09",
        StorageHealth.WRITE_BLOCKED,
        StorageEvent.OPERATOR_OPENS_MAINTENANCE_TO_FIX,
        StorageHealth.MAINTENANCE,
    ),
)

_TRANSITION_BY_EDGE: dict[tuple[StorageHealth, StorageEvent], Transition] = {
    (t.source, t.event): t for t in TRANSITIONS
}

# --------------------------------------------------------------------------------------
# What each state refuses -- contracts/state/storage.yaml §2 `refuses`
# --------------------------------------------------------------------------------------

_WRITE_BLOCKED_REFUSALS: tuple[OperationId, ...] = (
    # what: worker_claim -- granting a lease is a write (I02); grace = 0.
    OperationId.WORKER_CLAIM_ASSIGNMENT,
    OperationId.ANALYSIS_CLAIM_TASK,
    # what: mutation_ack -- never ACK a mutation that did not commit.
    OperationId.INGEST_SUBMIT_BATCH,
    OperationId.INGEST_COMMIT_CHECKPOINT,
    OperationId.ANALYSIS_SUBMIT_RESULT,
    OperationId.DELIVERY_RECORD_RECEIPT,
    # what: publish -- a multi-table transaction has no half-way.
    OperationId.REPORT_BUILD,
    OperationId.REPORT_PUBLISH,
    # what: dispatch -- the attempt must COMMIT before the network call.
    OperationId.DELIVERY_DISPATCH_NEXT,
    # what: schedule_enqueue -- creating a run is a write; overdue occurrences coalesce
    # after recovery (CU-01) rather than being lost.
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN,
    OperationId.JOB_COALESCE_OVERDUE,
)

_MAINTENANCE_REFUSALS: tuple[OperationId, ...] = (
    OperationId.WORKER_CLAIM_ASSIGNMENT,
    OperationId.ANALYSIS_CLAIM_TASK,
    OperationId.REPORT_PUBLISH,
    OperationId.DELIVERY_DISPATCH_NEXT,
)

_RECOVERY_REQUIRED_REFUSALS: tuple[OperationId, ...] = (
    OperationId.WORKER_CLAIM_ASSIGNMENT,
    OperationId.ANALYSIS_CLAIM_TASK,
    OperationId.DELIVERY_DISPATCH_NEXT,
    OperationId.REPORT_BUILD,
    OperationId.REPORT_PUBLISH,
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN,
    OperationId.JOB_COALESCE_OVERDUE,
)

#: state -> operation -> the code that operation must be refused with.
#:
#: Note the two codes are not interchangeable. ``write_blocked`` is transient and
#: ``retryable_with_budget``; ``recovery_required`` is ``operator_decision`` and no amount
#: of retrying leaves it. Returning the wrong one tells the caller the wrong thing about
#: whether to try again, so the fixtures assert the code, not just the refusal.
REFUSALS: dict[StorageHealth, dict[OperationId, ErrorCode]] = {
    StorageHealth.HEALTHY: {},
    StorageHealth.WRITE_BLOCKED: dict.fromkeys(
        _WRITE_BLOCKED_REFUSALS, ErrorCode.STORAGE_WRITE_FAILED
    ),
    StorageHealth.MAINTENANCE: dict.fromkeys(_MAINTENANCE_REFUSALS, ErrorCode.STORAGE_WRITE_FAILED),
    StorageHealth.RECOVERY_REQUIRED: dict.fromkeys(
        _RECOVERY_REQUIRED_REFUSALS, ErrorCode.RESTORE_UNVERIFIED
    ),
}

# --------------------------------------------------------------------------------------
# Readiness projection -- contracts/ops/deployment.md §5
# --------------------------------------------------------------------------------------

#: `storage` readiness row of contracts/ops/deployment.md §5. Three values, and
#: `maintenance` is deliberately NOT `down`: the operator opened that window on purpose and
#: must be able to tell their own maintenance from an incident (I13).
READINESS_OF_STORAGE: dict[StorageHealth, str] = {
    StorageHealth.HEALTHY: "ok",
    StorageHealth.MAINTENANCE: "degraded",
    StorageHealth.WRITE_BLOCKED: "down",
    StorageHealth.RECOVERY_REQUIRED: "down",
}


class ForbiddenTransition(RuntimeError):
    """Raised for an edge that ``contracts/state/storage.yaml`` §3 does not contain.

    Carries the attempted edge so a failure names its own contract row rather than only
    saying "invalid state".
    """

    def __init__(self, source: StorageHealth, event: StorageEvent, reason: str) -> None:
        super().__init__(f"{source.value} --{event.value}--> refused: {reason}")
        self.source = source
        self.event = event
        self.reason = reason


def _utc_now() -> datetime:
    return datetime.now(UTC)


class StorageHealthMachine:
    """In-memory ``storage.health``.

    :param clock: injected so tests can advance time without sleeping; the probe rules are
        defined in seconds and a real ``sleep`` would make the suite 90 s slower per case.
    :param initial: starting state. Production always starts ``healthy``
        (``contracts/state/storage.yaml`` ``initial_state``); tests use it to enter a
        fixture's ``given.storage_health`` directly.
    :param pending_restore_id: a restore that has not been reconciled yet. Present at
        construction only when a process restarts while a restore is outstanding -- which
        is precisely the case ``forbidden_transitions`` row 1 exists to catch.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] = _utc_now,
        initial: StorageHealth = StorageHealth.HEALTHY,
        pending_restore_id: str | None = None,
    ) -> None:
        self._clock = clock
        self._state = initial
        self._pending_restore_id = pending_restore_id
        self._observed_at = clock()
        self._consecutive_probe_successes = 0
        self._last_probe_at: datetime | None = None
        self._history: list[str] = []

    # -- observation ---------------------------------------------------------------

    @property
    def state(self) -> StorageHealth:
        return self._state

    @property
    def observed_at(self) -> datetime:
        """When the current state was last established or re-confirmed.

        This is the ``as_of`` the UI needs to label last-known data (``UI-01``): a screen
        that shows a state without saying when it was read cannot distinguish "no data"
        from "could not read" (``I13``).
        """
        return self._observed_at

    @property
    def pending_restore_id(self) -> str | None:
        return self._pending_restore_id

    @property
    def history(self) -> tuple[str, ...]:
        """Transition ids applied, in order. Test oracle; not a durable audit log."""
        return tuple(self._history)

    def refusal_for(self, operation_id: OperationId) -> ErrorCode | None:
        """The error code ``operation_id`` must be refused with now, or ``None`` if allowed.

        ``None`` means "this state does not refuse it", not "it will succeed": the
        operation can still fail for its own reasons.
        """
        return REFUSALS[self._state].get(operation_id)

    def readiness_of_storage(self) -> str:
        return READINESS_OF_STORAGE[self._state]

    def dispatcher_is_locked(self) -> bool:
        """``delivery_dispatcher`` readiness row: locked while recovery is outstanding (I15)."""
        return self._state is StorageHealth.RECOVERY_REQUIRED

    # -- transitions ---------------------------------------------------------------

    def _apply(self, event: StorageEvent) -> Transition:
        transition = _TRANSITION_BY_EDGE.get((self._state, event))
        if transition is None:
            raise ForbiddenTransition(
                self._state, event, "no such row in contracts/state/storage.yaml §3"
            )
        self._state = transition.target
        self._observed_at = self._clock()
        self._history.append(transition.id)
        return transition

    def record_write_failure(self) -> str | None:
        """A mutation failed with I/O error, no space, or DB unavailable.

        ``T-ST-01`` from ``healthy``; ``T-ST-07`` from ``recovery_required`` -- and note
        ``T-ST-07`` keeps :attr:`pending_restore_id`, because forgetting an unreconciled
        restore is exactly how a stale outbox gets replayed by accident.

        Already ``write_blocked`` is a no-op (returns ``None``): the same disk failing twice
        is one incident. From ``maintenance`` the contract has no edge, so the flag is
        recorded but the state is left alone -- an operator-opened window is not silently
        converted into an incident.

        :returns: the transition id applied, or ``None`` when nothing changed.
        """
        if self._state is StorageHealth.WRITE_BLOCKED:
            self._observed_at = self._clock()
            return None
        if self._state is StorageHealth.MAINTENANCE:
            # contracts/state/storage.yaml §3 has no maintenance -> write_blocked row.
            self._observed_at = self._clock()
            return None
        event = (
            StorageEvent.WRITE_FAILURE_DURING_RECOVERY
            if self._state is StorageHealth.RECOVERY_REQUIRED
            else StorageEvent.WRITE_FAILURE_DETECTED
        )
        self._consecutive_probe_successes = 0
        self._last_probe_at = None
        return self._apply(event).id

    def record_probe(self, *, success: bool, at: datetime | None = None) -> str | None:
        """Record one write probe while ``write_blocked``.

        The probe is a small write to a probe table, not a business mutation, so it is safe
        to repeat (``T-ST-02.guard_vi``).

        Two guards, both of which the contract states as forbidden transitions:

        * a probe closer than :data:`PROBE_INTERVAL_SECONDS` to the previous one does not
          count, so a caller cannot fire three probes in a millisecond and "recover";
        * leaving ``write_blocked`` needs :data:`PROBE_CONSECUTIVE_SUCCESS` successes, and
          a single failure resets the streak to zero.

        Where it lands depends on :attr:`pending_restore_id`: ``T-ST-02`` to ``healthy``
        when there is no outstanding restore, ``T-ST-08`` to ``recovery_required`` when
        there is. Going to ``healthy`` with a restore outstanding is ``forbidden_transitions``
        row 3.

        :returns: the transition id if the state changed, else ``None``.
        """
        if self._state is not StorageHealth.WRITE_BLOCKED:
            raise ForbiddenTransition(
                self._state,
                StorageEvent.PROBE_SUCCESS_STREAK,
                "probes are only meaningful while write_blocked",
            )
        now = at if at is not None else self._clock()
        if not success:
            self._consecutive_probe_successes = 0
            self._last_probe_at = now
            return None
        if self._last_probe_at is not None:
            elapsed = (now - self._last_probe_at).total_seconds()
            if elapsed < PROBE_INTERVAL_SECONDS:
                # Too soon to be independent evidence; not counted, not an error.
                return None
        self._last_probe_at = now
        self._consecutive_probe_successes += 1
        if self._consecutive_probe_successes < PROBE_CONSECUTIVE_SUCCESS:
            return None
        self._consecutive_probe_successes = 0
        event = (
            StorageEvent.PROBE_SUCCESS_WITH_PENDING_RESTORE
            if self._pending_restore_id is not None
            else StorageEvent.PROBE_SUCCESS_STREAK
        )
        return self._apply(event).id

    def open_maintenance(self) -> str:
        """Operator opens a maintenance window. ``T-ST-03`` / ``T-ST-09``.

        There is no automatic path in: ``forbidden_transitions`` row 5 makes an unattended
        cron opening maintenance a failure, because it would stop claims mid-run with no
        warning. ``T-ST-09`` (from ``write_blocked``) additionally requires that no restore
        is outstanding -- otherwise it becomes a laundering route to ``healthy`` via
        ``T-ST-04``.
        """
        if self._state is StorageHealth.WRITE_BLOCKED:
            if self._pending_restore_id is not None:
                raise ForbiddenTransition(
                    self._state,
                    StorageEvent.OPERATOR_OPENS_MAINTENANCE_TO_FIX,
                    "T-ST-09 requires no outstanding restore_record; reconcile first (I15)",
                )
            return self._apply(StorageEvent.OPERATOR_OPENS_MAINTENANCE_TO_FIX).id
        return self._apply(StorageEvent.OPERATOR_OPENS_MAINTENANCE).id

    def close_maintenance(self, *, snapshot_verified: bool) -> str:
        """``T-ST-04``. Closing before ``backup.verify_snapshot`` passes is forbidden."""
        if not snapshot_verified:
            raise ForbiddenTransition(
                self._state,
                StorageEvent.MAINTENANCE_WINDOW_CLOSED,
                "T-ST-04 forbids closing the window before verify passes",
            )
        return self._apply(StorageEvent.MAINTENANCE_WINDOW_CLOSED).id

    def record_restore(self, restore_id: str) -> str:
        """``T-ST-05``: a restore was executed, so reconciliation is now owed.

        Only from ``maintenance``. A restore into a live environment without the
        side-effect lock is what AMD-B11 forbids, and the lock is the maintenance window.
        """
        transition = self._apply(StorageEvent.RESTORE_EXECUTED)
        self._pending_restore_id = restore_id
        return transition.id

    def complete_reconciliation(
        self, restore_id: str, *, reconciliation_complete: Callable[[str], bool]
    ) -> str:
        """``T-ST-06`` -- the only gate that reopens side effects (``I15``).

        :param reconciliation_complete: the side-effect-free predicate that
            ``contracts/state/storage.yaml`` §7 ``interface_contract_vi`` requires PC08 to
            supply. This machine calls it; it never decides for itself that reconciliation
            happened, and there is no timeout and no attempt count that substitutes for it
            (``recovery_required.forbidden_vi``).
        """
        if self._state is not StorageHealth.RECOVERY_REQUIRED:
            raise ForbiddenTransition(
                self._state,
                StorageEvent.RECONCILE_COMPLETED,
                "reconciliation only applies to recovery_required",
            )
        if restore_id != self._pending_restore_id:
            raise ForbiddenTransition(
                self._state,
                StorageEvent.RECONCILE_COMPLETED,
                f"restore_id {restore_id!r} is not the outstanding restore",
            )
        if not reconciliation_complete(restore_id):
            raise ForbiddenTransition(
                self._state,
                StorageEvent.RECONCILE_COMPLETED,
                "reconciliation_complete() is false; dispatcher stays locked (I15)",
            )
        transition = self._apply(StorageEvent.RECONCILE_COMPLETED)
        self._pending_restore_id = None
        return transition.id
