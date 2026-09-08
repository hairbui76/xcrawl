"""``backup.create_snapshot`` — a WAL-safe snapshot plus the manifest that makes it checkable.

Why not ``cp``
--------------
``REQ-D58`` and SRC-SPEC §7.3 originally described backup as "copy the SQLite file". ``AMD-B11``
/ ``ADR-0005`` point 1 amended that, and the reason is the whole design of this module: under
WAL, committed transactions may still be sitting in the ``-wal`` file, so copying the ``.db``
alone drops them **silently** — the copy opens, ``PRAGMA integrity_check`` says ``ok``, and rows
are simply missing. Copying while a write is in flight can also catch a half-written
transaction. Both methods here (``sqlite3.Connection.backup`` — the Online Backup API — and
``VACUUM INTO``) read through the SQLite engine itself, so neither can observe either state.

The amendment did not drop the user's requirement; it changed the method, because the old
method could not deliver the requirement it was written for.

What a manifest is for
----------------------
A hash proves the artifact did not rot on disk. It proves nothing about whether the artifact
*contains the data*, and ``entities.yaml`` says so in as many words on
``ux_backup_snapshot_artifact``. That is why the manifest carries ``counts`` — row counts for
the tables ``contracts/ops/backup-restore.md`` §3 lists — and why :mod:`server.app.backup.verify`
re-queries them from inside the artifact. Condition (3) of the §3 oracle is the only one of the
three that catches a WAL-unsafe copy, and it is the reason fixture
``recovery/d-wal-unsafe-copy-detected`` exists.

Ordering, and one refusal
-------------------------
``backup-restore.md`` §7: ``backup.create_snapshot`` **must not run** while
``storage.health = write_blocked`` — a snapshot needs to write an artifact and needs a stable
database, and neither holds on a full disk. The guard is asked before anything is written, the
same way every mutating service in this repo asks it.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine

OWNER_MODULE: Final[str] = "MOD-backup-service"

#: ``contracts/modules.yaml``: ``backup.*`` has exactly one caller, and one auth scheme.
ALLOWED_CALLER: Final[str] = "MOD-backup-cli"

_CROCKFORD: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: Manifest shape version. Bumping it changes what ``manifest_sha256`` is computed over.
MANIFEST_VERSION: Final[str] = "0.1.0"


class SnapshotMethod(str, Enum):
    """``ENT-backup-snapshot.method``. There is no ``file_copy`` member, by amendment.

    ``AMD-B11`` removed it from the contract; leaving it out of the enum means a caller
    cannot record a method the contract forbids even by mistake.
    """

    ONLINE_BACKUP_API = "sqlite_online_backup_api"
    VACUUM_INTO = "vacuum_into"


class SnapshotState(str, Enum):
    """``ENT-backup-snapshot.state``.

    Fixture ``recovery/d`` writes ``invalid`` for the WAL-unsafe case; that value is not in
    the entity contract's enum and the Coordinator ruled ``entities.yaml`` wins, so a
    snapshot that fails verification becomes :attr:`FAILED`. ``CR-TC-BACKUP-02``.
    """

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


#: The tables whose row counts go into ``backup_manifest.counts``
#: (``contracts/ops/backup-restore.md`` §3, row "Đếm"). Plain counts.
COUNT_TABLES: Final[tuple[str, ...]] = (
    "saved_item",
    "saved_snapshot",
    "report",
    "report_item",
    "coverage_window",
    "first_announced_ledger",
    "backfill_ledger",
    "pending_item_ledger",
    "post",
    "work",
)

#: Counts that are grouped by a column rather than totalled, spelled ``<table>.<value>``.
#: ``outbox_intent`` by ``dispatch_state`` and ``delivery_part`` by ``state`` are named
#: explicitly by §3, and the ``unknown`` part count is clause 5 of ``reconciliation_complete``.
GROUPED_COUNTS: Final[tuple[tuple[str, str], ...]] = (
    ("outbox_intent", "dispatch_state"),
    ("delivery_part", "state"),
)

#: ``analysis`` is counted only in its ``valid`` rows (§3 says "analysis (valid)").
_FILTERED_COUNTS: Final[tuple[tuple[str, str, str], ...]] = (("analysis", "status", "valid"),)


class BackupError(Exception):
    """A refusal carrying one registered code from ``contracts/errors.yaml``."""

    def __init__(
        self,
        code: ErrorCode,
        *,
        message_safe: str | None = None,
        details_safe: Mapping[str, Any] | None = None,
        unmet_clauses: tuple[int, ...] = (),
    ) -> None:
        self.code = code
        self.message_safe = message_safe or _MESSAGE_SAFE.get(code, "Có lỗi không mong đợi.")
        self.details_safe = dict(details_safe or {})
        #: Which ``reconciliation_complete`` clauses are still unmet. Carried outside the
        #: envelope because ``details_safe_keys`` for ``RESTORE_UNVERIFIED`` does not list
        #: it, and inventing a key would break the envelope contract (fixture ``j`` still
        #: needs the numbers, so the CLI reads them from here).
        self.unmet_clauses = unmet_clauses
        unknown = set(self.details_safe) - DETAILS_SAFE_KEYS.get(code, frozenset())
        if unknown:
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
        }


#: ``details_safe_keys`` of ``contracts/errors.yaml`` for the codes this package raises.
DETAILS_SAFE_KEYS: Final[dict[ErrorCode, frozenset[str]]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.RESTORE_UNVERIFIED: frozenset({"restore_id", "storage_health"}),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.RESTORE_UNVERIFIED: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

_MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.VALIDATION_ERROR: "Yêu cầu không hợp lệ.",
    ErrorCode.UNAUTHORIZED: "Thao tác này chỉ chấp nhận backup operator token.",
    ErrorCode.FORBIDDEN_EDGE: "Lời gọi này không nằm trong các kết nối được phép.",
    ErrorCode.NOT_FOUND: "Không tìm thấy snapshot được yêu cầu.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Khóa chống trùng đã được dùng cho một yêu cầu khác.",
    ErrorCode.RESTORE_UNVERIFIED: "Bản khôi phục chưa được đối soát; side effect vẫn khóa.",
    ErrorCode.STORAGE_WRITE_FAILED: "Hệ thống đang không ghi được dữ liệu.",
    ErrorCode.INTERNAL: "Có lỗi không mong đợi.",
}


# --------------------------------------------------------------------------------------
# Small shared helpers (this package's only copy)
# --------------------------------------------------------------------------------------


def utc_now_ms() -> str:
    """Server clock, RFC 3339 UTC, milliseconds (``entities.yaml`` §conventions)."""
    moment = datetime.now(tz=UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp + 80 random bits, Crockford base32."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def canonical_json(value: Any) -> str:
    """RFC 8785 subset, as used everywhere else in this repo for hashed structures."""
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def sha256_of_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_of_file(path: Path, *, chunk: int = 1 << 20) -> str:
    """Streamed so a multi-hundred-MB artifact does not have to fit in memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def require_caller(operation: OperationId, caller_module: str) -> None:
    """Default deny. ``backup.*`` has exactly one registered caller."""
    if caller_module != ALLOWED_CALLER:
        raise BackupError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": OWNER_MODULE,
                "forbidden_edge_ref": None,
            },
        )


def assert_writable(guard: Any, operation: OperationId) -> None:
    """Ask the storage guard before writing, translating its envelope (``I02``)."""
    if guard is None:
        return
    try:
        guard.assert_writable(operation)
    except Exception as refused:  # StorageRefused, typed loosely to avoid an import cycle
        envelope = getattr(refused, "envelope", None)
        if not isinstance(envelope, dict):
            raise
        raise BackupError(
            ErrorCode(envelope["code"]),
            message_safe=envelope.get("message_safe"),
            details_safe=envelope.get("details_safe") or {},
        ) from refused


# --------------------------------------------------------------------------------------
# Counting
# --------------------------------------------------------------------------------------


def collect_counts(connection: sqlite3.Connection | Connection) -> dict[str, int]:
    """The ``counts`` block of the manifest, read from whichever database is given.

    Taken over the *same* key set whether it is read from the live database (when the
    manifest is written) or from inside a restored artifact (when it is verified). That
    symmetry is the entire detection mechanism for a WAL-unsafe copy: the two readings of an
    identical key set must agree, and for a ``cp`` of a live database they do not.

    A table that does not exist yet counts as absent rather than zero, and its key is
    omitted: recording ``0`` for a table this deployment has never created would later read
    as "the restore lost every row".
    """
    counts: dict[str, int] = {}
    existing = _table_names(connection)

    for table in COUNT_TABLES:
        if table in existing:
            counts[table] = _scalar(connection, f"SELECT COUNT(*) FROM {table}")

    for table, column, value in _FILTERED_COUNTS:
        if table in existing:
            counts[f"{table}.{value}"] = _scalar(
                connection, f"SELECT COUNT(*) FROM {table} WHERE {column} = '{value}'"
            )

    for table, column in GROUPED_COUNTS:
        if table not in existing:
            continue
        rows = _rows(connection, f"SELECT {column}, COUNT(*) FROM {table} GROUP BY {column}")
        for state_value, total in rows:
            counts[f"{table}.{state_value}"] = int(total)
    return counts


def _table_names(connection: sqlite3.Connection | Connection) -> set[str]:
    return {
        str(row[0])
        for row in _rows(connection, "SELECT name FROM sqlite_master WHERE type = 'table'")
    }


def _rows(connection: sqlite3.Connection | Connection, sql: str) -> list[tuple[Any, ...]]:
    if isinstance(connection, sqlite3.Connection):
        return list(connection.execute(sql).fetchall())
    return [tuple(row) for row in connection.exec_driver_sql(sql).fetchall()]


def _scalar(connection: sqlite3.Connection | Connection, sql: str) -> int:
    return int(_rows(connection, sql)[0][0])


# --------------------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SnapshotResult:
    """What ``backup.create_snapshot`` answers."""

    backup_snapshot_id: str
    manifest_id: str
    method: SnapshotMethod
    artifact_path: str
    artifact_sha256: str
    manifest_sha256: str
    counts: dict[str, int]
    state: SnapshotState
    started_at: str
    completed_at: str
    replayed: bool = False


# --------------------------------------------------------------------------------------
# backup.create_snapshot
# --------------------------------------------------------------------------------------


def create_snapshot(
    engine: Engine,
    *,
    owner_id: str,
    artifact_path: str | Path,
    snapshot_request_id: str,
    method: SnapshotMethod = SnapshotMethod.VACUUM_INTO,
    caller_module: str = ALLOWED_CALLER,
    guard: Any = None,
    alembic_revision: str | None = None,
    embedding_model_artifact_sha256: str | None = None,
    now: str | None = None,
) -> SnapshotResult:
    """``backup.create_snapshot`` — WAL-safe artifact + manifest, in that order.

    :param method: :attr:`SnapshotMethod.VACUUM_INTO` or the Online Backup API. Both read
        through the SQLite engine; neither is a file copy.
    :param alembic_revision: recorded in the manifest's schema block. ``ENT-schema-migration``
        is not implemented by any card, so ``backup_snapshot.schema_migration_version`` stays
        NULL and this string is what a later ``verify`` compares against
        (``CR-TC-BACKUP-04``).
    :raises BackupError: ``STORAGE_WRITE_FAILED`` while the store is blocked (§7),
        ``IDEMPOTENCY_CONFLICT`` when a previous attempt at this artifact path died before
        it committed a manifest.

    The row is written ``running`` *before* the copy starts and moved to ``completed`` after
    the artifact exists and has been hashed, so a crash mid-copy leaves a ``running`` row and
    an unusable artifact rather than a ``completed`` row that promises a backup nobody took.
    """
    require_caller(OperationId.BACKUP_CREATE_SNAPSHOT, caller_module)
    if not snapshot_request_id:
        raise _validation_error(
            OperationId.BACKUP_CREATE_SNAPSHOT, "snapshot_request_id", "required_field_missing"
        )
    assert_writable(guard, OperationId.BACKUP_CREATE_SNAPSHOT)

    target = Path(artifact_path)
    started_at = now or utc_now_ms()

    replay = _replay(engine, owner_id=owner_id, artifact_path=str(target))
    if replay is not None:
        return replay

    if target.exists():
        # `VACUUM INTO` refuses an existing file, and silently overwriting a previous
        # artifact would destroy a backup to make a backup.
        raise _validation_error(
            OperationId.BACKUP_CREATE_SNAPSHOT, "artifact_path", "already_exists"
        )
    target.parent.mkdir(parents=True, exist_ok=True)

    snapshot_id = new_ulid()
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO backup_snapshot (id, owner_id, method, started_at, artifact_path,"
            " state) VALUES (?, ?, ?, ?, ?, 'running')",
            (snapshot_id, owner_id, method.value, started_at, str(target)),
        )

    try:
        _write_artifact(engine, target, method)
    except Exception:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE backup_snapshot SET state = 'failed' WHERE id = ?", (snapshot_id,)
            )
        raise

    artifact_sha256 = sha256_of_file(target)
    with engine.connect() as connection:
        counts = collect_counts(connection)
    completed_at = utc_now_ms()

    manifest_body = build_manifest_body(
        backup_snapshot_id=snapshot_id,
        method=method,
        artifact_path=str(target),
        artifact_sha256=artifact_sha256,
        artifact_bytes=target.stat().st_size,
        created_at=started_at,
        completed_at=completed_at,
        counts=counts,
        alembic_revision=alembic_revision,
        embedding_model_artifact_sha256=embedding_model_artifact_sha256,
    )
    manifest_sha256 = sha256_of_json(manifest_body)
    manifest_id = new_ulid()

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE backup_snapshot SET state = 'completed', completed_at = ?,"
            " artifact_path = ?, artifact_sha256 = ?, schema_migration_version = NULL"
            " WHERE id = ?",
            (completed_at, str(target), artifact_sha256, snapshot_id),
        )
        connection.exec_driver_sql(
            "INSERT INTO backup_manifest (id, owner_id, backup_snapshot_id, entries,"
            " manifest_sha256, counts, embedding_model_artifact_sha256)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                manifest_id,
                owner_id,
                snapshot_id,
                canonical_json(manifest_body["entries"]),
                manifest_sha256,
                canonical_json(counts),
                embedding_model_artifact_sha256,
            ),
        )

    return SnapshotResult(
        backup_snapshot_id=snapshot_id,
        manifest_id=manifest_id,
        method=method,
        artifact_path=str(target),
        artifact_sha256=artifact_sha256,
        manifest_sha256=manifest_sha256,
        counts=counts,
        state=SnapshotState.COMPLETED,
        started_at=started_at,
        completed_at=completed_at,
    )


def build_manifest_body(
    *,
    backup_snapshot_id: str,
    method: SnapshotMethod,
    artifact_path: str,
    artifact_sha256: str,
    artifact_bytes: int,
    created_at: str,
    completed_at: str,
    counts: Mapping[str, int],
    alembic_revision: str | None,
    embedding_model_artifact_sha256: str | None,
) -> dict[str, Any]:
    """The manifest content that ``manifest_sha256`` is computed over.

    The manifest never contains an entry for itself (``entities.yaml``: "manifest KHÔNG tự
    chứa entry của mình") — a self-referential hash cannot be recomputed.

    ``not_in_backup`` is copied from ``backup-restore.md`` §6 rather than left implicit. A
    restore that quietly lacked the X session, the worker tokens or the secret master key
    would otherwise look complete; naming the gaps in the artifact itself is what lets a
    second person read the manifest and know what they still have to do by hand.
    """
    return {
        "manifest_version": MANIFEST_VERSION,
        "backup_snapshot_id": backup_snapshot_id,
        "snapshot": {
            "method": method.value,
            "artifact_sha256": artifact_sha256,
            "artifact_bytes": artifact_bytes,
            "created_at": created_at,
            "completed_at": completed_at,
        },
        "schema": {
            # ENT-schema-migration is unimplemented; the Alembic head is the real schema
            # identity of this deployment. CR-TC-BACKUP-04.
            "schema_migration_version": None,
            "alembic_revision": alembic_revision,
        },
        "entries": [
            {
                "path": artifact_path,
                "role": "database",
                "sha256": artifact_sha256,
                "bytes": artifact_bytes,
            }
        ],
        "counts": dict(counts),
        "embedding": {"model_artifact_sha256": embedding_model_artifact_sha256},
        "not_in_backup": [
            "chrome_profile_and_x_session",
            "collector_and_analysis_worker_tokens",
            "secret_store_master_key",
            "ai_provider_api_key_values",
            "embedding_model_artifact",
        ],
        "secret_recovery_plan_ref": "contracts/ops/secrets.md#4.1",
    }


def _write_artifact(engine: Engine, target: Path, method: SnapshotMethod) -> None:
    """Produce the artifact by one of the two WAL-safe methods, and nothing else.

    Both go through the engine's own connection. There is deliberately no branch that opens
    the database file directly or shells out to ``cp``: the absence of that branch is what
    makes the ``AMD-B11`` amendment true of this code rather than only of its documentation.
    """
    raw_connection = engine.raw_connection()
    try:
        driver = raw_connection.driver_connection
        if not isinstance(driver, sqlite3.Connection):  # pragma: no cover - defensive
            raise BackupError(
                ErrorCode.INTERNAL,
                details_safe={"operation_id": OperationId.BACKUP_CREATE_SNAPSHOT.value},
            )
        if method is SnapshotMethod.VACUUM_INTO:
            driver.execute("VACUUM INTO ?", (str(target),))
        else:
            destination = sqlite3.connect(str(target))
            try:
                driver.backup(destination)
            finally:
                destination.close()
    finally:
        raw_connection.close()


def _replay(engine: Engine, *, owner_id: str, artifact_path: str) -> SnapshotResult | None:
    """Return the committed snapshot for this artifact path, if there is one.

    ``ports.yaml`` scopes this operation's idempotency to ``snapshot_request_id``, and
    ``entities.yaml`` gives ``backup_snapshot`` **no column** to store one. Shipping a column
    the entity contract does not declare is exactly what
    ``tests/contract/test_schema_matches_entities.py`` refuses -- in both directions, and
    rightly -- so the replay key is the artifact path instead: a declared column, and the thing
    a repeated CLI invocation actually repeats.

    What that buys and what it does not, stated plainly: re-running the same command is safe
    and returns the first result. Two *different* request ids aimed at one path collapse into
    one snapshot, and one request id aimed at two paths produces two. Closing that gap needs
    the column; raised as ``CR-TC-BACKUP-07``.
    """
    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT s.id, s.method, s.artifact_path, s.artifact_sha256, s.state,"
                "       s.started_at, s.completed_at, m.id AS manifest_id,"
                "       m.manifest_sha256, m.counts"
                "  FROM backup_snapshot AS s"
                "  LEFT JOIN backup_manifest AS m ON m.backup_snapshot_id = s.id"
                " WHERE s.owner_id = ? AND s.artifact_path = ?",
                (owner_id, artifact_path),
            )
            .mappings()
            .first()
        )
    if row is None:
        return None
    if row["state"] == SnapshotState.RUNNING.value or row["manifest_sha256"] is None:
        # A previous attempt died mid-copy. Returning it as a success would report a backup
        # that does not exist; a new artifact path is the way forward.
        raise BackupError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            details_safe={"idempotency_key": artifact_path},
        )
    return SnapshotResult(
        backup_snapshot_id=str(row["id"]),
        manifest_id=str(row["manifest_id"]),
        method=SnapshotMethod(str(row["method"])),
        artifact_path=str(row["artifact_path"]),
        artifact_sha256=str(row["artifact_sha256"]),
        manifest_sha256=str(row["manifest_sha256"]),
        counts=dict(json.loads(str(row["counts"]))),
        state=SnapshotState(str(row["state"])),
        started_at=str(row["started_at"]),
        completed_at=str(row["completed_at"]),
        replayed=True,
    )


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
    "ALLOWED_CALLER",
    "COUNT_TABLES",
    "DETAILS_SAFE_KEYS",
    "GROUPED_COUNTS",
    "MANIFEST_VERSION",
    "OWNER_MODULE",
    "BackupError",
    "SnapshotMethod",
    "SnapshotResult",
    "SnapshotState",
    "assert_writable",
    "build_manifest_body",
    "canonical_json",
    "collect_counts",
    "create_snapshot",
    "new_ulid",
    "require_caller",
    "sha256_of_file",
    "sha256_of_json",
    "utc_now_ms",
]
