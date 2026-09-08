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

from server.app.backup import reconcile, restore, verify
from server.app.backup.snapshot import (
    BackupError,
    SnapshotMethod,
    create_snapshot,
    new_ulid,
)
from server.app.db import create_sqlite_engine

#: Environment variable holding the operator token. ``secrets.md`` §3 keeps it in a 0600 file
#: on the server; the deployment exports it into this process and nowhere else.
TOKEN_ENV = "RR_BACKUP_OPERATOR_TOKEN"
#: The value the presented token is checked against.
EXPECTED_TOKEN_ENV = "RR_BACKUP_OPERATOR_TOKEN_EXPECTED"

EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_UNAUTHORIZED = 3

CALLER_MODULE = "MOD-backup-cli"


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


def _emit(payload: dict[str, Any]) -> None:
    """Print one JSON object. Never includes a token, a cookie or a file path outside var/."""
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _guard(engine: Any, owner_id: str) -> Any:
    """The process's storage guard, wired to this package's reconciliation predicate.

    This is the injection ``StorageGuard.reconciliation_complete`` documents as belonging to
    ``TC-backup-restore-drill``: until it is supplied the guard answers ``False`` for every
    restore, which keeps dispatch locked but also means nothing could ever unlock.
    """
    from server.app.storage.guard import StorageGuard

    return StorageGuard(
        reconciliation_check=reconcile.reconciliation_complete(engine, owner_id=owner_id)
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
    if owner_id:
        return owner_id
    with engine.connect() as connection:
        row = connection.exec_driver_sql("SELECT id FROM owner LIMIT 1").first()
    if row is None:
        raise BackupError.__new__(BackupError)  # pragma: no cover - unreachable in practice
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
        payload = refused.envelope(new_ulid())
        if refused.unmet_clauses:
            payload["unmet_clauses"] = list(refused.unmet_clauses)
        _emit(payload)
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
            transition = guard.enter_maintenance()
        else:
            transition = guard.leave_maintenance(snapshot_verified=args.snapshot_verified)
        _emit({"transition": transition, "storage_health": guard.current_health().value})
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
