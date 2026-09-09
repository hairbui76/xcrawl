"""``MOD-backup-cli`` — the only way to reach ``backup.*``.

Authentication
--------------
``contracts/http/openapi.yaml`` (post-FIX1, ``CR-PC08-02``) and ``contracts/ops/secrets.md``
§147 agree: every ``backup.*`` route accepts ``backupOperatorToken`` and **nothing else**. An
owner browser session must not be able to start a restore — restore is a side-effect-locking
operation on the whole database, and a session cookie is exactly the credential an attacker
gets to borrow.

This CLI reads the token from ``RR_BACKUP_OPERATOR_TOKEN`` (or ``--token-file``, a
restricted-permission file per ``secrets.md`` §3) and compares it constant-time against the
configured value. Nothing is printed that could echo a token, and the token never reaches an
argument vector: ``--token`` deliberately does not exist, because process arguments are world
readable on a shared machine.

Why there is no HTTP router in this card
----------------------------------------
Card §3's write set names four service modules, this CLI and two tests — **no**
``server/app/backup/router.py``. openapi declares four HTTP paths for these operations, so the
contract and the write set disagree; the Coordinator ruled CLI-only and to record the
divergence rather than amend the write set (``CR-TC-BACKUP-01``).

The practical effect is stronger than what the contract asks for, not weaker: with no routes
registered there is no HTTP surface at all, so the "owner browser session activates restore"
path that ``CR-PC08-02`` forbids does not merely fail authentication — it does not exist.
``tests/integration/test_restore_side_effect_lock.py`` asserts that no route on the app
carries a ``backup.*`` operation id.

Usage::

    RR_BACKUP_OPERATOR_TOKEN=... python -m tools.backup_cli snapshot \\
        --database var/research-radar.db --artifact var/backups/2026-09-08.db

    ... verify   --snapshot-id <ULID>
    ... restore  --snapshot-id <ULID> --request-id RR-01 --confirm RESTORE
    ... review   --restore-id <ULID> --intent-id <ULID> --decision hold
    ... ack      --restore-id <ULID> --principal "ACT-backup-operator" --note "..."
    ... reconcile --restore-id <ULID>

Exit codes: ``0`` success, ``2`` a contract refusal (the error envelope is printed as JSON),
``3`` an authentication failure. A refusal is not a crash and is not reported as one.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from rr_contracts.generated.errors import ErrorCode

from server.app.backup import reconcile, restore, verify
from server.app.backup.snapshot import (
    BackupError,
    SnapshotMethod,
    create_snapshot,
    new_ulid,
)
from server.app.db import create_sqlite_engine
from server.app.storage.guard import MaintenanceWindowRequired, StorageRefused

# `ForbiddenTransition` is re-exported through `guard` but declared in `health`; importing it
# from its own module keeps `__all__` honest and mypy --strict quiet.
from server.app.storage.health import ForbiddenTransition

#: Environment variable holding the operator token. ``secrets.md`` §3 keeps it in a 0600 file
#: on the server; the deployment exports it into this process and nowhere else.
TOKEN_ENV = "RR_BACKUP_OPERATOR_TOKEN"
#: The value the presented token is checked against.
EXPECTED_TOKEN_ENV = "RR_BACKUP_OPERATOR_TOKEN_EXPECTED"

EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_UNAUTHORIZED = 3

CALLER_MODULE = "MOD-backup-cli"

#: Who is recorded as opening and closing a maintenance window. The actor id of
#: ``contracts/capabilities.yaml``; this CLI admits exactly one principal class, so there is
#: nothing to infer and nothing a caller could spoof by passing a different name.
OPERATOR_PRINCIPAL = "ACT-backup-operator"


def authenticate(*, presented: str | None, expected: str | None) -> None:
    """``backupOperatorToken``, compared constant-time.

    An unconfigured ``expected`` is a refusal, never a pass: a deployment that forgot to set
    the token must reject every operator, not accept every caller. That direction is the
    whole of ``contracts/modules.yaml`` ``default_deny`` applied to a CLI.
    """
    if not expected or not presented or not hmac.compare_digest(presented, expected):
        raise PermissionError("backup operator token missing or incorrect")


def _read_token(args: argparse.Namespace) -> str | None:
    if args.token_file:
        path = Path(args.token_file)
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8").strip()
    return os.environ.get(TOKEN_ENV)


#: ``message_safe`` for ``NOT_FOUND``, chosen by **what** was not found.
#:
#: ``F-A3-P5R2-01``: the per-code table in ``server/app/backup/snapshot.py`` has one string for
#: the whole code, and it reads "Không tìm thấy snapshot được yêu cầu." On a migrated but
#: un-bootstrapped database the missing thing is the *owner row*, so the tool sent the Owner
#: hunting for a snapshot when what they actually had to do was create the account. The
#: envelope was correct and the sentence was misleading, which is worse than a bare code: it
#: aims the reader somewhere specific and wrong.
#:
#: Keyed on ``details_safe.resource_kind``, which every ``NOT_FOUND`` in this package already
#: sets. The owner line names the exact command (`rr-admin bootstrap-owner`, a real console
#: script in ``pyproject.toml``) rather than describing it, because a message that says "run
#: the bootstrap command" leaves the reader looking for its name.
NOT_FOUND_MESSAGE: dict[str, str] = {
    "owner": (
        "Chưa có hàng `owner` nào: cơ sở dữ liệu đã migrate nhưng chưa bootstrap. "
        "Chạy `uv run rr-admin bootstrap-owner` rồi thử lại."
    ),
    "backup_snapshot": "Không tìm thấy snapshot được yêu cầu.",
    "backup_artifact": ("Bản ghi snapshot tồn tại nhưng file artifact không có ở `artifact_path`."),
    "restore_record": "Không tìm thấy bản ghi restore được yêu cầu.",
}


def _with_specific_message(payload: dict[str, Any]) -> dict[str, Any]:
    """Replace a ``NOT_FOUND`` envelope's message with one keyed on ``resource_kind``.

    Applied at the CLI boundary because ``server/app/backup/snapshot.py`` — where the per-code
    table lives and where this belongs — is not in this packet's lease. Raised as
    ``CR-TC-BACKUP-08``; the durable fix is for ``BackupError`` to pick the sentence when it
    builds the envelope, so every caller benefits rather than only this one.

    Only the sentence changes. ``code``, ``scope``, ``retry_class`` and ``details_safe`` are
    the contract's and are left exactly as the service produced them.
    """
    if payload.get("code") != ErrorCode.NOT_FOUND.value:
        return payload
    kind = (payload.get("details_safe") or {}).get("resource_kind")
    message = NOT_FOUND_MESSAGE.get(str(kind))
    return payload if message is None else {**payload, "message_safe": message}


def _emit(payload: dict[str, Any]) -> None:
    """Print one JSON object. Never includes a token, a cookie or a file path outside var/."""
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _guard(engine: Any, owner_id: str) -> Any:
    """The process's storage guard: persisted, and wired to this card's predicate.

    Two injections, and both matter for a CLI specifically.

    ``reconciliation_check`` is the seam ``StorageGuard`` documents as belonging to
    ``TC-backup-restore-drill``; without it the guard answers ``False`` for every restore, so
    dispatch stays locked but nothing could ever unlock.

    ``from_engine`` is the persisted constructor ``PKT-TC-STORAGE-FIX4`` added for gap
    ``G-3``. The bare ``StorageGuard()`` keeps its state in process memory, which is right for
    a unit test and wrong here: ``backup_cli maintenance --open`` and ``backup_cli restore``
    are **two processes**, so an in-memory window closes when the first one exits and the
    second sees ``healthy``. Since ``restore_snapshot`` refuses outside ``maintenance``
    (``T-ST-05``), the documented two-step runbook could not actually be run — the operator
    would open a window and then be told there wasn't one. ``CR-TC-storage-07``.
    """
    from server.app.storage.guard import StorageGuard

    return StorageGuard.from_engine(
        engine,
        owner_id=owner_id,
        reconciliation_check=reconcile.reconciliation_complete(engine, owner_id=owner_id),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backup_cli",
        description="MOD-backup-cli — backup.* operations (backupOperatorToken only).",
    )
    parser.add_argument("--database", required=True, help="path to the live SQLite database")
    parser.add_argument("--owner-id", default=None, help="owner ULID; defaults to the only owner")
    parser.add_argument(
        "--token-file",
        default=None,
        help="0600 file holding the operator token; otherwise $" + TOKEN_ENV,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    snapshot = sub.add_parser("snapshot", help="backup.create_snapshot")
    snapshot.add_argument("--artifact", required=True)
    snapshot.add_argument(
        "--method",
        choices=[m.value for m in SnapshotMethod],
        default=SnapshotMethod.VACUUM_INTO.value,
        help="both are WAL-safe; a file copy is not offered (AMD-B11)",
    )
    snapshot.add_argument("--request-id", default=None)

    verify_cmd = sub.add_parser("verify", help="backup.verify_snapshot")
    verify_cmd.add_argument("--snapshot-id", required=True)

    maintenance = sub.add_parser(
        "maintenance",
        help="open/close the maintenance window (T-ST-03/T-ST-05 require it before restore)",
    )
    maintenance.add_argument("--open", action="store_true")
    maintenance.add_argument("--close", action="store_true")
    # The choices come from the storage module's own constant, not from a literal here: the
    # set is closed by `entities.yaml`, and a copy in this file would be free to drift from it.
    from server.app.storage.guard import MAINTENANCE_REASONS

    maintenance.add_argument(
        "--reason",
        choices=sorted(MAINTENANCE_REASONS),
        default=None,
        help="why the window is being opened; REQUIRED with --open (maintenance_window, T-ST-03)",
    )
    maintenance.add_argument(
        "--snapshot-verified",
        action="store_true",
        help="closing after a restore drill asserts the snapshot was verified",
    )

    restore_cmd = sub.add_parser("restore", help="backup.restore_snapshot")
    restore_cmd.add_argument("--snapshot-id", required=True)
    restore_cmd.add_argument("--request-id", required=True)
    restore_cmd.add_argument("--confirm", required=True, help="type RESTORE to confirm")
    restore_cmd.add_argument("--target-database", default=None)

    review = sub.add_parser("review", help="operator decision on ONE recovered intent (§5.5)")
    review.add_argument("--restore-id", required=True)
    review.add_argument("--intent-id", required=True)
    review.add_argument("--decision", choices=["hold", "release"], required=True)

    ack = sub.add_parser("ack", help="operator acknowledgement (clause 7)")
    ack.add_argument("--restore-id", required=True)
    ack.add_argument("--principal", required=True)
    ack.add_argument("--note", required=True)

    status = sub.add_parser("status", help="reconciliation_complete(restore_id), read-only")
    status.add_argument("--restore-id", required=True)

    reconcile_cmd = sub.add_parser("reconcile", help="backup.reconcile_after_restore")
    reconcile_cmd.add_argument("--restore-id", required=True)

    return parser


def _resolve_owner(engine: Any, owner_id: str | None) -> str:
    """The owner this invocation acts for: the one given, or the single owner row.

    Both failure modes raise a fully constructed :class:`BackupError`, which is the point.
    The previous version did ``BackupError.__new__(BackupError)`` -- an instance with no
    ``code``, no ``message_safe`` and no ``details_safe`` -- so ``main``'s handler blew up with
    ``AttributeError`` while trying to render the envelope, and the operator got a traceback
    instead of the refusal the CLI documents. It also carried a "unreachable in practice"
    comment that was simply false: an empty ``owner`` table is a fresh deployment before
    ``bootstrap_owner``, and it is also what a restore target looks like before the artifact
    goes in -- exactly when someone runs this tool.

    An explicitly supplied id is checked too. Letting an unknown one through would push the
    failure down into a foreign key violation several steps later, at which point the message
    names a constraint rather than the mistake.
    """
    with engine.connect() as connection:
        if owner_id:
            found = connection.exec_driver_sql(
                "SELECT id FROM owner WHERE id = ?", (owner_id,)
            ).first()
            if found is None:
                raise BackupError(ErrorCode.NOT_FOUND, details_safe={"resource_kind": "owner"})
            return owner_id
        row = connection.exec_driver_sql("SELECT id FROM owner LIMIT 1").first()
    if row is None:
        raise BackupError(ErrorCode.NOT_FOUND, details_safe={"resource_kind": "owner"})
    return str(row[0])


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns an exit code rather than raising, so a refusal reads as a refusal."""
    args = build_parser().parse_args(argv)
    try:
        authenticate(presented=_read_token(args), expected=os.environ.get(EXPECTED_TOKEN_ENV))
    except PermissionError:
        _emit(
            {
                "code": "UNAUTHORIZED",
                "message_safe": "Thao tác này chỉ chấp nhận backup operator token.",
                "required_auth_scope": "backup_operator",
            }
        )
        return EXIT_UNAUTHORIZED

    engine = create_sqlite_engine(args.database)
    try:
        owner_id = _resolve_owner(engine, args.owner_id)
        guard = _guard(engine, owner_id)
        return _dispatch(args, engine=engine, owner_id=owner_id, guard=guard)
    except BackupError as refused:
        payload = _with_specific_message(refused.envelope(new_ulid()))
        if refused.unmet_clauses:
            payload["unmet_clauses"] = list(refused.unmet_clauses)
        _emit(payload)
        return EXIT_REFUSED
    except StorageRefused as refused:
        # The guard already built a contract envelope; it only lacks a correlation id, which
        # `errors.yaml` §EPR-01 requires on every one. Pass its own code through rather than
        # re-deciding: it knows whether this was STORAGE_WRITE_FAILED or RESTORE_UNVERIFIED.
        _emit({**refused.envelope, "correlation_id": new_ulid()})
        return EXIT_REFUSED
    except (MaintenanceWindowRequired, ForbiddenTransition) as refused:
        # Two operator-input mistakes the storage module raises as plain exceptions:
        # opening a window without its audit fields, and asking for a state transition the
        # machine has no edge for (`--close` with nothing open, `restore` from `healthy`).
        # Both are VALIDATION_ERROR here for the same reason `restore_snapshot` already
        # reports a wrong `storage.health` that way -- `ports.yaml` gives `backup.*` no code
        # for a bad precondition, which is `CR-TC-BACKUP-05`. The exception text is NOT
        # echoed: it is an internal message, and the envelope carries only declared keys.
        _emit(
            {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message_safe": "Yêu cầu không hợp lệ với trạng thái kho hiện tại.",
                "details_safe": {
                    "field_path": "storage_health",
                    "violation_kind": type(refused).__name__,
                },
                "correlation_id": new_ulid(),
            }
        )
        return EXIT_REFUSED
    except Exception as unexpected:  # noqa: BLE001 - the CLI must never print a traceback
        # Last line of defence. `F-A3-P5-01` was exactly this shape: an exception from a
        # layer below reached the terminal as a traceback, bypassing the envelope the tool
        # documents. The type name goes to STDERR so a developer keeps a thread to pull;
        # STDOUT stays a clean envelope, and no exception text is echoed anywhere, because it
        # can carry a path or a value the envelope contract does not admit.
        print(f"unexpected {type(unexpected).__name__}", file=sys.stderr)
        _emit(
            {
                "code": ErrorCode.INTERNAL.value,
                "message_safe": "Có lỗi không mong đợi.",
                "correlation_id": new_ulid(),
            }
        )
        return EXIT_REFUSED
    finally:
        engine.dispose()


def _dispatch(args: argparse.Namespace, *, engine: Any, owner_id: str, guard: Any) -> int:
    if args.command == "snapshot":
        result = create_snapshot(
            engine,
            owner_id=owner_id,
            artifact_path=args.artifact,
            snapshot_request_id=args.request_id or new_ulid(),
            method=SnapshotMethod(args.method),
            caller_module=CALLER_MODULE,
            guard=guard,
            alembic_revision=_alembic_head(engine),
        )
        _emit(
            {
                "backup_snapshot_id": result.backup_snapshot_id,
                "manifest_sha256": result.manifest_sha256,
                "artifact_sha256": result.artifact_sha256,
                "state": result.state.value,
                "counts": result.counts,
                "replayed": result.replayed,
            }
        )
        return EXIT_OK

    if args.command == "verify":
        verified = verify.verify_snapshot(
            engine,
            owner_id=owner_id,
            backup_snapshot_id=args.snapshot_id,
            caller_module=CALLER_MODULE,
            raise_on_failure=False,
        )
        _emit(verify.describe(verified))
        return EXIT_OK if verified.verified else EXIT_REFUSED

    if args.command == "maintenance":
        # `storage.yaml` forbids entering `maintenance` without an explicit operator action,
        # which is why this is its own command and not something `restore` does for you.
        if args.open == args.close:
            _emit({"code": "VALIDATION_ERROR", "field_path": "--open/--close"})
            return EXIT_REFUSED
        if args.open:
            # `reason` and `opened_by` are the T-ST-03 columns on `maintenance_window`, both
            # NOT NULL: a window with no recorded opener cannot be told apart afterwards from
            # one nothing opened. The guard therefore REQUIRES them, and this is where the
            # runbook's `maintenance --open` used to walk straight into a
            # `MaintenanceWindowRequired` traceback (`F-A3-P5-01`) -- `--reason` was optional
            # here while being mandatory one layer down.
            #
            # Refused as an envelope rather than by `argparse(required=True)` on purpose:
            # argparse writes a usage dump to stderr and leaves stdout empty, so a caller
            # parsing this tool's JSON would get nothing at all. An unknown reason IS left to
            # argparse, because `choices` is what rejects it and the operator needs to see
            # the valid set.
            if args.reason is None:
                _emit(
                    {
                        "code": ErrorCode.VALIDATION_ERROR.value,
                        "message_safe": "Mở cửa sổ bảo trì cần --reason.",
                        "details_safe": {
                            "field_path": "--reason",
                            "violation_kind": "required_field_missing",
                        },
                        "correlation_id": new_ulid(),
                    }
                )
                return EXIT_REFUSED
            transition = guard.enter_maintenance(reason=args.reason, opened_by=OPERATOR_PRINCIPAL)
        else:
            transition = guard.leave_maintenance(
                snapshot_verified=args.snapshot_verified, closed_by=OPERATOR_PRINCIPAL
            )
        _emit(
            {
                "transition": transition,
                "storage_health": guard.current_health().value,
                "window_id": guard.window_id,
            }
        )
        return EXIT_OK

    if args.command == "restore":
        outcome = restore.restore_snapshot(
            engine,
            owner_id=owner_id,
            backup_snapshot_id=args.snapshot_id,
            restore_request_id=args.request_id,
            confirmation_phrase=args.confirm,
            guard=guard,
            caller_module=CALLER_MODULE,
            target_database=args.target_database,
        )
        # AFTER the INSERT, never before: `maintenance_window.restore_record_id` is a foreign
        # key, and `restore_snapshot` calls `mark_recovery_required` before it writes the
        # `restore_record` row, so linking at mark time would reference a row that does not
        # exist yet. WR's `link_restore_record` docstring says the same from the other side.
        guard.link_restore_record(outcome.restore_id)
        _emit(
            {
                "restore_id": outcome.restore_id,
                "new_restore_generation": outcome.new_restore_generation,
                "leases_revoked": outcome.leases_revoked,
                "storage_health": outcome.storage_health,
                "integrity_check_outcome": outcome.integrity_check_outcome,
                "dispatcher_unlocked_at": None,
            }
        )
        return EXIT_OK

    if args.command == "review":
        state = reconcile.review_intent(
            engine,
            owner_id=owner_id,
            restore_id=args.restore_id,
            outbox_intent_id=args.intent_id,
            decision=args.decision,
            caller_module=CALLER_MODULE,
        )
        _emit({"outbox_intent_id": args.intent_id, "dispatch_state": state})
        return EXIT_OK

    if args.command == "ack":
        at = reconcile.acknowledge(
            engine,
            owner_id=owner_id,
            restore_id=args.restore_id,
            principal=args.principal,
            note=args.note,
            caller_module=CALLER_MODULE,
        )
        _emit({"restore_id": args.restore_id, "operator_ack_at": at})
        return EXIT_OK

    if args.command == "status":
        report = reconcile.evaluate(engine, owner_id=owner_id, restore_id=args.restore_id)
        _emit(report.as_evidence())
        return EXIT_OK if report.complete else EXIT_REFUSED

    if args.command == "reconcile":
        reconciled = reconcile.reconcile_after_restore(
            engine,
            owner_id=owner_id,
            restore_id=args.restore_id,
            guard=guard,
            caller_module=CALLER_MODULE,
        )
        _emit(
            {
                "restore_id": reconciled.restore_id,
                "storage_health": reconciled.storage_health,
                "dispatcher_unlocked_at": reconciled.dispatcher_unlocked_at,
                "clauses_met": list(reconciled.report.met),
                "replayed": reconciled.replayed,
            }
        )
        return EXIT_OK

    return EXIT_REFUSED  # pragma: no cover - argparse rejects unknown commands first


def _alembic_head(engine: Any) -> str | None:
    with engine.connect() as connection:
        try:
            row = connection.exec_driver_sql("SELECT version_num FROM alembic_version").first()
        except Exception:  # pragma: no cover - a database with no alembic table
            return None
    return str(row[0]) if row else None


if __name__ == "__main__":  # pragma: no cover - script entry
    sys.exit(main())
