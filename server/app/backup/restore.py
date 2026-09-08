"""``backup.restore_snapshot`` — restore into a side-effect-locked environment.

The order in ``contracts/ops/backup-restore.md`` §5.2 is a contract, not a suggestion, and this
module implements it literally:

.. code-block:: text

    1. restore artifact          -> storage.health = recovery_required
    2. revoke EVERY assignment_lease in the snapshot   (state -> revoked)
    3. raise lease_epoch for every non-terminal run    (old worker => STALE_LEASE)
    4. write restore_record.leases_revoked
    5. verify + counts            (verify.py)
    6. decide what to do with the old outbox   (reconcile.py)
    7. reconciliation_complete(restore_id) == true
    8. only then: backup.reconcile_after_restore -> healthy

Steps 1–4 are here; 5–8 are :mod:`server.app.backup.verify` and
:mod:`server.app.backup.reconcile`. The split follows the order: nothing in this module can
reopen a side effect, and there is no code path here that sets ``dispatcher_unlocked_at``.

Restore runs **inside a maintenance window**, and cannot open one
-----------------------------------------------------------------
``contracts/state/storage.yaml`` ``T-ST-05`` is ``maintenance --restore_executed-->
recovery_required``: there is no edge into ``recovery_required`` from ``healthy``. That is the
state-machine spelling of "restore into an environment with the side effects locked" — the
maintenance window *is* the lock, and it exists before the artifact is touched rather than
being created by touching it.

So :func:`restore_snapshot` **refuses** when the store is not already in ``maintenance``; it
does not open the window itself. ``storage.yaml`` lists "entering ``maintenance`` without an
explicit operator action" among its forbidden transitions, and a restore that quietly opened
its own window would be exactly that, with the added property that the one operation which
most needs a human in the loop would be the one that removed them. Opening the window is a
separate CLI step (``backup_cli maintenance --open``).

``ports.yaml`` gives ``backup.restore_snapshot`` no code for "wrong storage health"
(``data.purge_all`` uses ``CONFLICT`` for the identical precondition), so the refusal is
``VALIDATION_ERROR`` with ``field_path = storage_health`` and the gap is raised as
``CR-TC-BACKUP-05``.

Why the health flip comes first
-------------------------------
``recovery_required`` is entered **before** any lease is touched. If the process died between
restoring the artifact and revoking the leases, an implementation that flipped health last
would come back up ``healthy`` with a snapshot full of live-looking leases and a full outbox —
which is precisely the counterexample ``contracts/state/storage.yaml`` gives for ``I15``.
Entering the locked state first means every crash window is on the safe side of the lock.

Why every lease is stale, without exception
-------------------------------------------
A lease in the snapshot was granted before the snapshot was taken, and the world has moved on
since. There is no test that could tell a "still valid" one from the rest, so §5.2 revokes all
of them and raises the epoch. A worker that survived from before the backup still holds the
old epoch in memory and is refused with ``STALE_LEASE`` — fixture
``recovery/b-post-restore-stale-lease-rejected`` — and, separately, its claim is refused with
``RESTORE_UNVERIFIED`` because the store is locked. Those are two different refusals for two
different reasons and the fixture pins both.

No ``restore_request_id`` column, and why that is safe here
-----------------------------------------------------------
``ports.yaml`` scopes this operation's idempotency to ``restore_request_id``, and
``entities.yaml`` declares no column on ``restore_record`` to hold it. Rather than ship a field
the entity contract does not declare, the second-run protection comes from the state machine:
after a successful restore the store sits in ``recovery_required``, and ``T-ST-05`` only leaves
``maintenance`` -- so a repeated call is refused by the precondition above before it writes
anything. That is a stronger guarantee than a key lookup for the case that matters (a double
restore), and a weaker one for the case that does not (two ids for one intended restore).
``CR-TC-BACKUP-07``.

``restore_generation``
----------------------
Each restore mints a new, monotonically increasing generation
(``ux_restore_record_generation``). Every ``outbox_intent`` recovered from the snapshot carries
an older one, and the dispatcher only sends intents whose generation is current. That turns
"restore does not replay the old outbox" from a promise into a numeric comparison — see
``DeliveryContext.restore_generation`` in ``server/app/delivery/service.py``, which this
module's result is meant to be wired into.
"""

from __future__ import annotations

import hmac
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.backup.snapshot import (
    ALLOWED_CALLER,
    BackupError,
    SnapshotState,
    canonical_json,
    collect_counts,
    new_ulid,
    require_caller,
    utc_now_ms,
)

#: The phrase an operator must type back to run a restore (``ports.yaml``: "xác nhận gõ tay").
#: Compared constant-time for the same reason every other confirmation in this repo is: a
#: comparison that leaks position turns a confirmation into a guessing game.
CONFIRMATION_PHRASE: str = "RESTORE"

#: ``ENT-assignment-lease.state``. ``held`` is the only non-terminal value; the rest are
#: already finished and re-revoking them would inflate ``leases_revoked``, which clause 3 of
#: ``reconciliation_complete`` compares against a count.
LEASE_NON_TERMINAL: tuple[str, ...] = ("held",)

#: ``ENT-run.status`` values that are still live and therefore need a raised epoch.
RUN_NON_TERMINAL: tuple[str, ...] = (
    "queued",
    "running",
    "waiting_retry",
    "needs_user",
    "blocked",
)


@dataclass(frozen=True)
class RestoreResult:
    """What ``backup.restore_snapshot`` answers.

    ``dispatcher_unlocked_at`` is deliberately not a field: this operation cannot unlock
    anything, and offering the value here would invite a caller to read it as "done".
    """

    restore_id: str
    backup_snapshot_id: str
    new_restore_generation: int
    leases_revoked: int
    storage_health: str
    integrity_check_outcome: str
    counts_observed: dict[str, int]
    restored_at: str
    replayed: bool = False


def restore_snapshot(
    engine: Engine,
    *,
    owner_id: str,
    backup_snapshot_id: str,
    restore_request_id: str,
    confirmation_phrase: str,
    guard: Any,
    caller_module: str = ALLOWED_CALLER,
    target_database: str | Path | None = None,
    now: str | None = None,
) -> RestoreResult:
    """Restore ``backup_snapshot_id`` and leave the store in ``recovery_required``.

    :param guard: the process's :class:`~server.app.storage.guard.StorageGuard`. Required,
        not optional: a restore that could not lock the store would be the one operation in
        this system that must never run unguarded.
    :param target_database: where to place the artifact. ``None`` means "the artifact is
        already in place" — the drill case where an operator restored the file by hand and
        now needs the bookkeeping done. Nothing is copied in that case.
    :param restore_request_id: the idempotency key ``ports.yaml`` names. Validated but not
        stored -- ``entities.yaml`` declares no column for it (module docstring;
        ``CR-TC-BACKUP-07``); a second restore is stopped by the ``maintenance`` precondition.
    :raises BackupError: ``VALIDATION_ERROR`` for a wrong confirmation phrase or a store that
        is not in ``maintenance``, ``NOT_FOUND`` for an unknown snapshot,
        ``RESTORE_UNVERIFIED`` for a snapshot that is not ``verified``.

    A snapshot that has not passed :func:`server.app.backup.verify.verify_snapshot` is
    refused. Fixture ``recovery/d`` lists "use this snapshot for ``backup.restore_snapshot``"
    among its forbidden effects, and the only way to make that impossible rather than merely
    discouraged is to require the ``verified`` state here.
    """
    require_caller(OperationId.BACKUP_RESTORE_SNAPSHOT, caller_module)
    if not hmac.compare_digest(confirmation_phrase or "", CONFIRMATION_PHRASE):
        raise _validation_error(
            OperationId.BACKUP_RESTORE_SNAPSHOT, "confirmation_phrase", "confirmation_mismatch"
        )
    if not restore_request_id:
        raise _validation_error(
            OperationId.BACKUP_RESTORE_SNAPSHOT, "restore_request_id", "required_field_missing"
        )

    with engine.connect() as connection:
        snapshot_row = (
            connection.exec_driver_sql(
                "SELECT id, state, artifact_path FROM backup_snapshot"
                " WHERE owner_id = ? AND id = ?",
                (owner_id, backup_snapshot_id),
            )
            .mappings()
            .first()
        )
    if snapshot_row is None:
        raise BackupError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.BACKUP_RESTORE_SNAPSHOT.value,
                "resource_kind": "backup_snapshot",
            },
        )
    if str(snapshot_row["state"]) != SnapshotState.VERIFIED.value:
        raise BackupError(
            ErrorCode.RESTORE_UNVERIFIED,
            details_safe={"restore_id": backup_snapshot_id},
        )
    # `T-ST-05` starts at `maintenance`. Checked here, before the artifact is copied, so a
    # refusal leaves the filesystem as well as the database untouched.
    if guard.current_health().value != "maintenance":
        raise _validation_error(
            OperationId.BACKUP_RESTORE_SNAPSHOT, "storage_health", "precondition_not_met"
        )

    restored_at = now or utc_now_ms()
    restore_id = new_ulid()

    # ---- step 1: the artifact, then the lock -----------------------------------------
    if target_database is not None:
        destination = Path(target_database)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(str(snapshot_row["artifact_path"])), destination)

    guard.mark_recovery_required(restore_id)

    # ---- steps 2 and 3: every lease is stale ------------------------------------------
    with engine.begin() as connection:
        placeholders = ", ".join("?" for _ in LEASE_NON_TERMINAL)
        leases_revoked = int(
            connection.exec_driver_sql(
                f"UPDATE assignment_lease SET state = 'revoked'"
                f" WHERE owner_id = ? AND state IN ({placeholders})",
                (owner_id, *LEASE_NON_TERMINAL),
            ).rowcount
        )
        _raise_lease_epochs(connection, owner_id=owner_id)
        counts_observed = collect_counts(connection)
        generation = _next_generation(connection, owner_id=owner_id)

        # ---- step 4: the record, with the lock still on ------------------------------
        # `integrity_check_outcome` starts at `not_run`, which entities.yaml calls a valid
        # value that MUST block the dispatcher. Writing `passed` here -- before verify has
        # been run against the restored database -- would unlock on an unchecked restore.
        connection.exec_driver_sql(
            "INSERT INTO restore_record (id, owner_id, backup_snapshot_id, restored_at,"
            " new_restore_generation, integrity_check_outcome, counts_observed,"
            " leases_revoked, dispatcher_unlocked_at)"
            " VALUES (?, ?, ?, ?, ?, 'not_run', ?, ?, NULL)",
            (
                restore_id,
                owner_id,
                backup_snapshot_id,
                restored_at,
                generation,
                canonical_json(counts_observed),
                leases_revoked,
            ),
        )

    return RestoreResult(
        restore_id=restore_id,
        backup_snapshot_id=backup_snapshot_id,
        new_restore_generation=generation,
        leases_revoked=leases_revoked,
        storage_health=guard.current_health().value,
        integrity_check_outcome="not_run",
        counts_observed=counts_observed,
        restored_at=restored_at,
    )


def record_integrity_outcome(
    engine: Engine,
    *,
    owner_id: str,
    restore_id: str,
    outcome: str,
    counts_observed: dict[str, int] | None = None,
) -> None:
    """Write §5.3's verdict onto the restore record.

    ``outcome`` must be one of ``entities.yaml``'s three values. Fixture ``d`` uses
    ``mismatch`` and §5.6 clause 1 uses ``ok``; neither exists in the enum, and the mapping
    (``mismatch`` -> ``failed``, ``ok`` -> ``passed``) is applied by the caller and recorded
    as ``CR-TC-BACKUP-02`` rather than silently widened here.
    """
    if outcome not in {"passed", "failed", "not_run"}:
        raise _validation_error(
            OperationId.BACKUP_VERIFY_SNAPSHOT, "integrity_check_outcome", "enum_not_allowed"
        )
    with engine.begin() as connection:
        if counts_observed is None:
            connection.exec_driver_sql(
                "UPDATE restore_record SET integrity_check_outcome = ?"
                " WHERE owner_id = ? AND id = ?",
                (outcome, owner_id, restore_id),
            )
        else:
            connection.exec_driver_sql(
                "UPDATE restore_record SET integrity_check_outcome = ?, counts_observed = ?"
                " WHERE owner_id = ? AND id = ?",
                (outcome, canonical_json(counts_observed), owner_id, restore_id),
            )


def _raise_lease_epochs(connection: Any, *, owner_id: str) -> None:
    """Step 3: bump ``run.lease_epoch`` for every non-terminal run, if the column exists.

    Guarded on the column rather than assumed: ``ENT-run`` belongs to the scheduler card and
    a deployment mid-migration may not have it yet. Missing column means there is no epoch to
    raise, not that the step may be skipped once it exists -- so the absence is silent and
    the presence is honoured.
    """
    columns = {
        str(row[1]) for row in connection.exec_driver_sql("PRAGMA table_info(run)").fetchall()
    }
    if "lease_epoch" not in columns:
        return
    placeholders = ", ".join("?" for _ in RUN_NON_TERMINAL)
    connection.exec_driver_sql(
        f"UPDATE run SET lease_epoch = lease_epoch + 1"
        f" WHERE owner_id = ? AND status IN ({placeholders})",
        (owner_id, *RUN_NON_TERMINAL),
    )


def _next_generation(connection: Any, *, owner_id: str) -> int:
    """Strictly greater than anything already in play, per owner.

    Two maxima, not one. Taking only ``MAX(restore_record.new_restore_generation)`` gets the
    **first** restore wrong: with no prior restore that maximum is 0, the new generation is 1,
    and every ``outbox_intent`` recovered from the snapshot already carrying generation 1
    would come out of the restore *eligible to send*. That is the exact failure ``I15`` names,
    and it would appear only on the first restore a deployment ever performs -- the one nobody
    has rehearsed.

    So the new generation is one above the highest generation observed anywhere: previous
    restores and the restored intents themselves. ``ux_restore_record_generation`` then keeps
    it unique.
    """
    highest = int(
        connection.exec_driver_sql(
            "SELECT COALESCE(MAX(new_restore_generation), 0) FROM restore_record"
            " WHERE owner_id = ?",
            (owner_id,),
        ).scalar_one()
    )
    tables = {
        str(row[0])
        for row in connection.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    if "outbox_intent" in tables:
        highest = max(
            highest,
            int(
                connection.exec_driver_sql(
                    "SELECT COALESCE(MAX(restore_generation), 0) FROM outbox_intent"
                    " WHERE owner_id = ?",
                    (owner_id,),
                ).scalar_one()
            ),
        )
    return highest + 1


def _validation_error(operation: OperationId, field_path: str, violation_kind: str) -> BackupError:
    return BackupError(
        ErrorCode.VALIDATION_ERROR,
        details_safe={
            "operation_id": operation.value,
            "field_path": field_path,
            "violation_kind": violation_kind,
        },
    )


__all__ = [
    "CONFIRMATION_PHRASE",
    "LEASE_NON_TERMINAL",
    "RUN_NON_TERMINAL",
    "RestoreResult",
    "record_integrity_outcome",
    "restore_snapshot",
]
