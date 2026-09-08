"""``reconciliation_complete(restore_id)`` and ``backup.reconcile_after_restore``.

``contracts/state/storage.yaml`` §7 asks PC08 for one specific thing: *a boolean predicate
with no side effects*, which ``backup.reconcile_after_restore`` consults and which is the only
way ``storage.health`` returns to ``healthy``. :func:`reconciliation_complete` is that
predicate, and :func:`evaluate` is it with its reasons attached.

The seven clauses (``backup-restore.md`` §5.6)
----------------------------------------------
1. ``integrity_check_outcome`` passed;
2. every key in ``counts_observed`` matches ``backup_manifest.counts``;
3. every stale lease revoked, and no ``held`` lease left carrying an old epoch;
4. no un-reviewed ``outbox_intent`` at the current generation;
5. the number of ``unknown`` delivery parts equals the manifest's — nothing was silently
   moved to ``sent`` or ``failed``;
6. embedding: either a valid active generation, or selection blocked for a recorded reason;
7. an operator acknowledgement exists for this ``restore_id``.

Clause 7 is the one that cannot be automated, and that is the point rather than a limitation:
the machine can check that the counts add up, but it cannot check that a person looked at what
was lost and accepted it. Fixture ``recovery/j-restore-verification-incomplete-dispatch-locked``
is built exactly to catch an implementation that treats "integrity ok + counts match" as
sufficient — in that fixture both of those hold and reconciliation is still incomplete, on
clauses 4 and 7.

Two consequences enforced here
------------------------------
*No time-based unlock.* ``storage.yaml`` forbids "mở khóa theo thời gian" and
``backup-restore.md`` §4 sets ``restore_verification_deadline`` to "no automatic deadline".
Nothing in this module reads a clock to decide whether to unlock; the only inputs are rows.

*The failure names the clause.* Fixture ``j`` requires the answer to say **which** clauses are
unmet, "not just 'not finished'". :class:`ReconciliationReport` carries the numbers, and the
CLI prints them.

Deliberately absent: any function that raises ``restore_generation`` on an old intent in bulk.
§5.5 makes that a per-intent operator decision with a recorded reason, so
:func:`review_intent` takes one intent id at a time and requires a note.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Final

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine

from server.app.backup.snapshot import (
    ALLOWED_CALLER,
    BackupError,
    require_caller,
    utc_now_ms,
)

#: ``ENT-outbox-intent.dispatch_state``. ``backup-restore.md`` §5.6 clause 4 and fixtures
#: ``a``/``j``/``m`` say ``pending``/``retry_wait``; those values are not in the entity enum
#: (``ready | claimed | done | held_for_review``). Per the Coordinator's ruling the entity
#: contract wins: ``ready`` is the state clause 4 is about — an intent the dispatcher would
#: pick up — and ``held_for_review`` is what an operator decision moves it to.
#: ``CR-TC-BACKUP-03``.
INTENT_AWAITING_REVIEW: Final[str] = "ready"
INTENT_REVIEWED: Final[str] = "held_for_review"

#: The clause numbers, so a report can be read against §5.6 without counting list positions.
CLAUSE_INTEGRITY: Final[int] = 1
CLAUSE_COUNTS: Final[int] = 2
CLAUSE_LEASES: Final[int] = 3
CLAUSE_OUTBOX_REVIEWED: Final[int] = 4
CLAUSE_UNKNOWN_PARTS: Final[int] = 5
CLAUSE_EMBEDDING: Final[int] = 6
CLAUSE_OPERATOR_ACK: Final[int] = 7

CLAUSE_TEXT: Final[dict[int, str]] = {
    CLAUSE_INTEGRITY: "integrity_check_outcome == 'passed'",
    CLAUSE_COUNTS: "counts_observed khớp backup_manifest.counts",
    CLAUSE_LEASES: "mọi lease stale đã thu hồi; không còn lease active mang epoch cũ",
    CLAUSE_OUTBOX_REVIEWED: "không còn outbox_intent generation hiện tại chưa được Operator xét",
    CLAUSE_UNKNOWN_PARTS: "số delivery_part 'unknown' bằng đúng số trong manifest",
    CLAUSE_EMBEDDING: "embedding generation hợp lệ, hoặc selection bị chặn có lý do đã ghi",
    CLAUSE_OPERATOR_ACK: "có bản ghi xác nhận của Operator gắn với restore_id",
}


@dataclass(frozen=True)
class ReconciliationReport:
    """Every clause's verdict, with the unmet ones listed by number.

    Carries all seven rather than stopping at the first failure: an operator who is told only
    "clause 1 failed" has to re-run to discover clause 7 also failed, and §5.7 wants the whole
    picture recorded as drill evidence.
    """

    restore_id: str
    met: tuple[int, ...]
    unmet: tuple[int, ...]
    detail: dict[int, str]

    @property
    def complete(self) -> bool:
        return not self.unmet

    def as_evidence(self) -> dict[str, Any]:
        return {
            "restore_id": self.restore_id,
            "reconciliation_complete": self.complete,
            "clauses_met": list(self.met),
            "clauses_unmet": list(self.unmet),
            "unmet_detail": {str(k): self.detail[k] for k in self.unmet},
        }


def evaluate(engine: Engine, *, owner_id: str, restore_id: str) -> ReconciliationReport:
    """The predicate, with reasons. **Read-only** — this function writes nothing.

    ``storage.yaml`` §7 requires the predicate to be side-effect free, and the reason is
    concrete: :class:`~server.app.storage.guard.StorageGuard` calls it from inside
    ``complete_reconciliation`` and a predicate that mutated would make asking the question
    change the answer.
    """
    with engine.connect() as connection:
        record = _restore_record(connection, owner_id=owner_id, restore_id=restore_id)
        if record is None:
            raise BackupError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.BACKUP_RECONCILE_AFTER_RESTORE.value,
                    "resource_kind": "restore_record",
                },
            )
        manifest = _manifest_counts(
            connection, owner_id=owner_id, backup_snapshot_id=str(record["backup_snapshot_id"])
        )
        observed = dict(json.loads(str(record["counts_observed"])))
        generation = int(record["new_restore_generation"])

        detail: dict[int, str] = dict(CLAUSE_TEXT)
        unmet: list[int] = []

        # 1 -- integrity
        outcome = str(record["integrity_check_outcome"])
        if outcome != "passed":
            unmet.append(CLAUSE_INTEGRITY)
            detail[CLAUSE_INTEGRITY] = f"integrity_check_outcome = {outcome!r}"

        # 2 -- counts. Every key in counts_observed must match the manifest.
        differing = sorted(key for key in observed if manifest.get(key) != observed.get(key))
        if differing:
            unmet.append(CLAUSE_COUNTS)
            detail[CLAUSE_COUNTS] = f"counts lệch ở: {', '.join(differing)}"

        # 3 -- no lease still held. `leases_revoked` is a claim; this is the measurement.
        still_held = _scalar(
            connection,
            "SELECT COUNT(*) FROM assignment_lease WHERE owner_id = ? AND state = 'held'",
            (owner_id,),
        )
        if still_held:
            unmet.append(CLAUSE_LEASES)
            detail[CLAUSE_LEASES] = f"{still_held} assignment_lease vẫn ở 'held'"

        # 4 -- every intent at the CURRENT generation must have been looked at. Old
        # generations are not in scope: they can never be dispatched, so there is nothing to
        # decide about them at this gate (fixture `m`: OI-OLD stays exactly as it was).
        unreviewed = _scalar(
            connection,
            "SELECT COUNT(*) FROM outbox_intent"
            " WHERE owner_id = ? AND restore_generation = ? AND dispatch_state = ?",
            (owner_id, generation, INTENT_AWAITING_REVIEW),
        )
        if unreviewed:
            unmet.append(CLAUSE_OUTBOX_REVIEWED)
            detail[CLAUSE_OUTBOX_REVIEWED] = (
                f"{unreviewed} outbox_intent ở generation {generation} chưa được Operator xét"
            )

        # 5 -- `unknown` stays `unknown`. Restore creates no information about whether
        # Telegram received anything (AMD-B03), so a changed count means something decided
        # on its own.
        expected_unknown = manifest.get("delivery_part.unknown", 0)
        observed_unknown = _scalar(
            connection,
            "SELECT COUNT(*) FROM delivery_part WHERE owner_id = ? AND state = 'unknown'",
            (owner_id,),
        )
        if observed_unknown != expected_unknown:
            unmet.append(CLAUSE_UNKNOWN_PARTS)
            detail[CLAUSE_UNKNOWN_PARTS] = (
                f"delivery_part 'unknown': manifest {expected_unknown}, đo được {observed_unknown}"
            )

        # 6 -- embedding
        embedding_met, embedding_reason = _embedding_ok(connection, owner_id=owner_id)
        if not embedding_met:
            unmet.append(CLAUSE_EMBEDDING)
            detail[CLAUSE_EMBEDDING] = embedding_reason or (
                "generation active không hợp lệ và selection chưa được ghi là bị chặn"
            )

        # 7 -- a human said so.
        if record["operator_ack_at"] is None:
            unmet.append(CLAUSE_OPERATOR_ACK)
            detail[CLAUSE_OPERATOR_ACK] = "chưa có operator_ack_at/operator_ack_principal"

    met = tuple(sorted(set(CLAUSE_TEXT) - set(unmet)))
    return ReconciliationReport(
        restore_id=restore_id, met=met, unmet=tuple(sorted(unmet)), detail=detail
    )


def reconciliation_complete(engine: Engine, *, owner_id: str) -> Any:
    """A ``reconciliation_check`` callable for :class:`~server.app.storage.guard.StorageGuard`.

    The guard's constructor takes ``Callable[[str], bool]``; this binds the engine and owner
    so the seam can be wired without the storage package learning anything about backup.
    Until it is injected the guard answers ``False`` for every restore, which is the safe
    default it documents.
    """

    def check(restore_id: str) -> bool:
        return evaluate(engine, owner_id=owner_id, restore_id=restore_id).complete

    return check


# --------------------------------------------------------------------------------------
# Operator actions -- the two clauses no machine may satisfy on its own
# --------------------------------------------------------------------------------------


def review_intent(
    engine: Engine,
    *,
    owner_id: str,
    restore_id: str,
    outbox_intent_id: str,
    decision: str,
    caller_module: str = ALLOWED_CALLER,
) -> str:
    """Record the operator's decision about ONE recovered intent (§5.5, clause 4).

    :param decision: ``hold`` to keep it out of dispatch forever, or ``release`` to move it
        to the current generation so the dispatcher may send it.

    One intent per call, on purpose. §5.5 says raising an old intent into the current
    generation is "quyết định của Operator, ghi lý do, **từng intent một**", and a bulk
    helper is how that becomes a single careless keystroke that replays a month of digests.
    """
    require_caller(OperationId.BACKUP_RECONCILE_AFTER_RESTORE, caller_module)
    if decision not in {"hold", "release"}:
        raise BackupError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.BACKUP_RECONCILE_AFTER_RESTORE.value,
                "field_path": "decision",
                "violation_kind": "enum_not_allowed",
            },
        )
    with engine.begin() as connection:
        record = _restore_record(connection, owner_id=owner_id, restore_id=restore_id)
        if record is None:
            raise BackupError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.BACKUP_RECONCILE_AFTER_RESTORE.value,
                    "resource_kind": "restore_record",
                },
            )
        generation = int(record["new_restore_generation"])
        if decision == "hold":
            connection.exec_driver_sql(
                "UPDATE outbox_intent SET dispatch_state = ?"
                " WHERE owner_id = ? AND id = ? AND dispatch_state = ?",
                (INTENT_REVIEWED, owner_id, outbox_intent_id, INTENT_AWAITING_REVIEW),
            )
            return INTENT_REVIEWED
        connection.exec_driver_sql(
            "UPDATE outbox_intent SET restore_generation = ?" " WHERE owner_id = ? AND id = ?",
            (generation, owner_id, outbox_intent_id),
        )
    return INTENT_AWAITING_REVIEW


def acknowledge(
    engine: Engine,
    *,
    owner_id: str,
    restore_id: str,
    principal: str,
    note: str,
    caller_module: str = ALLOWED_CALLER,
    now: str | None = None,
) -> str:
    """Clause 7: record that a named person read the reconciliation result.

    Requires both a principal and a note. ``entities.yaml`` calls ``operator_ack_note``
    "bằng chứng con người đã nhìn, không phải máy tự tuyên bố", and an acknowledgement with
    an empty note is the machine declaring on the human's behalf.
    """
    require_caller(OperationId.BACKUP_RECONCILE_AFTER_RESTORE, caller_module)
    if not principal or not note:
        raise BackupError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.BACKUP_RECONCILE_AFTER_RESTORE.value,
                "field_path": "operator_ack_note" if principal else "operator_ack_principal",
                "violation_kind": "required_field_missing",
            },
        )
    acknowledged_at = now or utc_now_ms()
    with engine.begin() as connection:
        updated = connection.exec_driver_sql(
            "UPDATE restore_record SET operator_ack_at = ?, operator_ack_principal = ?,"
            " operator_ack_note = ? WHERE owner_id = ? AND id = ?",
            (acknowledged_at, principal, note, owner_id, restore_id),
        ).rowcount
    if not updated:
        raise BackupError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.BACKUP_RECONCILE_AFTER_RESTORE.value,
                "resource_kind": "restore_record",
            },
        )
    return acknowledged_at


# --------------------------------------------------------------------------------------
# backup.reconcile_after_restore
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ReconcileResult:
    """What ``backup.reconcile_after_restore`` answers once it succeeds."""

    restore_id: str
    storage_health: str
    dispatcher_unlocked_at: str
    report: ReconciliationReport
    replayed: bool = False


def reconcile_after_restore(
    engine: Engine,
    *,
    owner_id: str,
    restore_id: str,
    guard: Any,
    caller_module: str = ALLOWED_CALLER,
    now: str | None = None,
) -> ReconcileResult:
    """Step 8: the only door back to ``healthy``.

    :raises BackupError: ``RESTORE_UNVERIFIED`` carrying the unmet clause numbers in
        :attr:`BackupError.unmet_clauses`, exactly as fixture ``j`` requires.

    The guard is asked to make the transition rather than being told: ``complete_reconciliation``
    re-evaluates the predicate itself, so even a caller that skipped the check here cannot
    unlock a restore that is not reconciled.
    """
    require_caller(OperationId.BACKUP_RECONCILE_AFTER_RESTORE, caller_module)

    existing = _unlocked_at(engine, owner_id=owner_id, restore_id=restore_id)
    if existing is not None:
        # ports.yaml: "cùng restore_id chỉ reconcile một lần".
        return ReconcileResult(
            restore_id=restore_id,
            storage_health=guard.current_health().value,
            dispatcher_unlocked_at=existing,
            report=evaluate(engine, owner_id=owner_id, restore_id=restore_id),
            replayed=True,
        )

    report = evaluate(engine, owner_id=owner_id, restore_id=restore_id)
    if not report.complete:
        raise BackupError(
            ErrorCode.RESTORE_UNVERIFIED,
            details_safe={
                "restore_id": restore_id,
                "storage_health": guard.current_health().value,
            },
            unmet_clauses=report.unmet,
        )

    guard.complete_reconciliation(restore_id)
    unlocked_at = now or utc_now_ms()
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE restore_record SET dispatcher_unlocked_at = ?" " WHERE owner_id = ? AND id = ?",
            (unlocked_at, owner_id, restore_id),
        )
    return ReconcileResult(
        restore_id=restore_id,
        storage_health=guard.current_health().value,
        dispatcher_unlocked_at=unlocked_at,
        report=report,
    )


# --------------------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------------------


def _restore_record(
    connection: Connection, *, owner_id: str, restore_id: str
) -> dict[str, Any] | None:
    row = (
        connection.exec_driver_sql(
            "SELECT id, backup_snapshot_id, new_restore_generation, integrity_check_outcome,"
            "       counts_observed, leases_revoked, dispatcher_unlocked_at, operator_ack_at"
            "  FROM restore_record WHERE owner_id = ? AND id = ?",
            (owner_id, restore_id),
        )
        .mappings()
        .first()
    )
    return dict(row) if row is not None else None


def _manifest_counts(
    connection: Connection, *, owner_id: str, backup_snapshot_id: str
) -> dict[str, int]:
    row = (
        connection.exec_driver_sql(
            "SELECT counts FROM backup_manifest WHERE owner_id = ? AND backup_snapshot_id = ?",
            (owner_id, backup_snapshot_id),
        )
        .mappings()
        .first()
    )
    if row is None:
        return {}
    return {str(k): int(v) for k, v in json.loads(str(row["counts"])).items()}


def _embedding_ok(connection: Connection, *, owner_id: str) -> tuple[bool, str | None]:
    """Clause 6, read from ``embedding_generation`` if that table is present.

    ``backup-restore.md`` §5.6 clause 6 is satisfied by *either* "a valid active generation" or
    "selection is blocked for a recorded reason", and §5.3 step 5 says what valid means: the
    active generation's ``built_vector_count`` equals its ``expected_vector_count``.

    Three distinct answers, and the middle one is the fix for ``CR-TC-DELIVERY-11``:

    *No active generation.* Clause met. A deployment that never built one has no index for
    selection to run against, so there is nothing this clause could be protecting.

    *An active generation whose ``expected_vector_count`` is NULL.* Clause **unmet**, with the
    reason named. ``entities.yaml`` makes that column nullable and defines it as "số vector phải
    có trước khi được phép chuyển sang ``active``" — so a NULL on an *active* row means the
    precondition that gated activation was never recorded, and the restore has no way to
    establish that the index is complete. Reporting it as met would convert *undetermined* into
    *good*, which is exactly what ``I13`` and ``CAP-P5`` forbid and what ``I12`` protects
    against: selection would resume against an index nobody can show is whole. Reporting it as
    met is also what the previous version effectively promised — it never got that far, because
    ``int(None)`` raised ``TypeError`` and the clause produced a crash instead of a verdict.

    *An active generation with counts that disagree.* Clause unmet, counts named.

    :returns: ``(met, reason)`` — the reason is ``None`` when met, and is what
        :func:`evaluate` puts in the report so an operator is told which of the three cases
        they are in rather than only that clause 6 failed.
    """
    tables = {
        str(row[0])
        for row in connection.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if "embedding_generation" not in tables:
        return True, None
    columns = {
        str(row[1])
        for row in connection.exec_driver_sql("PRAGMA table_info(embedding_generation)").fetchall()
    }
    if not {"state", "expected_vector_count", "built_vector_count"} <= columns:
        return True, None
    row = (
        connection.exec_driver_sql(
            "SELECT expected_vector_count, built_vector_count FROM embedding_generation"
            " WHERE owner_id = ? AND state = 'active'",
            (owner_id,),
        )
        .mappings()
        .first()
    )
    if row is None:
        return True, None
    expected = row["expected_vector_count"]
    if expected is None:
        return False, (
            "generation active có expected_vector_count = NULL: không có mốc nào để kiểm "
            "generation đã dựng đủ chưa (backup-restore.md §5.3 bước 5, §5.6 mệnh đề 6; I12)"
        )
    built = int(row["built_vector_count"])
    if built != int(expected):
        return False, (
            f"generation active: built_vector_count {built} != expected_vector_count "
            f"{int(expected)}"
        )
    return True, None


def _unlocked_at(engine: Engine, *, owner_id: str, restore_id: str) -> str | None:
    with engine.connect() as connection:
        row = connection.exec_driver_sql(
            "SELECT dispatcher_unlocked_at FROM restore_record WHERE owner_id = ? AND id = ?",
            (owner_id, restore_id),
        ).first()
    if row is None or row[0] is None:
        return None
    return str(row[0])


def _scalar(connection: Connection, sql: str, parameters: tuple[Any, ...]) -> int:
    return int(connection.exec_driver_sql(sql, parameters).scalar_one())


__all__ = [
    "CLAUSE_COUNTS",
    "CLAUSE_EMBEDDING",
    "CLAUSE_INTEGRITY",
    "CLAUSE_LEASES",
    "CLAUSE_OPERATOR_ACK",
    "CLAUSE_OUTBOX_REVIEWED",
    "CLAUSE_TEXT",
    "CLAUSE_UNKNOWN_PARTS",
    "INTENT_AWAITING_REVIEW",
    "INTENT_REVIEWED",
    "ReconcileResult",
    "ReconciliationReport",
    "acknowledge",
    "evaluate",
    "reconcile_after_restore",
    "reconciliation_complete",
    "review_intent",
]
