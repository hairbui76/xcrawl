"""``backup.verify_snapshot`` — the three-condition oracle, and the WAL-unsafe detector.

``contracts/ops/backup-restore.md`` §3 states the oracle for a valid manifest, and it is
deliberately three conditions rather than one:

1. ``sha256(artifact at artifact_path) == artifact_sha256``;
2. ``PRAGMA integrity_check`` on a **copy** of the artifact returns ``ok``;
3. for **every** key in ``counts``, the count queried from inside the artifact equals the
   value recorded in the manifest.

Why the third condition carries the weight
------------------------------------------
Conditions (1) and (2) are the ones an implementer reaches for first, and together they miss
the failure this card exists to catch. A ``cp`` of a live WAL database produces a file whose
bytes hash consistently and whose B-tree is structurally sound — ``integrity_check`` says
``ok`` — while the transactions still sitting in the ``-wal`` file are simply absent. Only
re-counting the rows inside the artifact and comparing them to what the live database held at
snapshot time notices that. Fixture ``recovery/d-wal-unsafe-copy-detected`` is exactly this
case, and it spells out that (1) and (2) alone do **not** detect it.

So verification is not "is the file intact" but "does the file contain the data we said it
contained". Those are different questions and only the second one is a backup.

Failure is a refusal, not a warning
-----------------------------------
Any failed condition ⇒ ``RESTORE_UNVERIFIED``, and the snapshot must not be usable for
restore. The forbidden effects of fixture ``d`` are explicit: do not use it for
``backup.restore_snapshot``, do not conclude "backup is valid" from the hash alone, and do not
mark it ``verified``. :func:`verify_snapshot` therefore moves the row to ``failed`` and
:func:`server.app.backup.restore.restore_snapshot` refuses any snapshot that is not
``verified``.

Fixture ``d`` labels that end state ``invalid`` and the outcome ``mismatch``; neither value is
in ``entities.yaml``'s enums (``running|completed|failed|verified`` and
``passed|failed|not_run``). Per the Coordinator's ruling the entity contract wins, so this
module writes ``failed`` and records the divergence as ``CR-TC-BACKUP-02``. The mapping is
asserted in ``tests/integration/test_wal_unsafe_detected.py`` so that closing the CR makes the
test fail rather than letting the two drift apart quietly.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.backup.snapshot import (
    ALLOWED_CALLER,
    BackupError,
    SnapshotState,
    collect_counts,
    require_caller,
    sha256_of_file,
)


@dataclass(frozen=True)
class CountMismatch:
    """One key on which the artifact and the manifest disagree."""

    key: str
    expected: int | None
    observed: int | None


@dataclass(frozen=True)
class VerifyResult:
    """The outcome of all three conditions, reported together rather than short-circuited.

    Reporting every condition matters for a drill: an operator who is told only "condition 2
    failed" cannot tell a corrupt file from a stale one. ``§5.7`` requires the whole table of
    expected/observed counts as drill evidence, so it is collected even when an earlier
    condition already failed.
    """

    backup_snapshot_id: str
    artifact_sha256_matches: bool
    integrity_check: str
    counts_match: bool
    expected_counts: dict[str, int]
    observed_counts: dict[str, int]
    mismatches: tuple[CountMismatch, ...] = ()
    state: SnapshotState = SnapshotState.FAILED
    alembic_revision_expected: str | None = None
    alembic_revision_observed: str | None = None
    failures: tuple[str, ...] = field(default_factory=tuple)

    @property
    def verified(self) -> bool:
        return self.state is SnapshotState.VERIFIED


def verify_snapshot(
    engine: Engine,
    *,
    owner_id: str,
    backup_snapshot_id: str,
    caller_module: str = ALLOWED_CALLER,
    raise_on_failure: bool = True,
) -> VerifyResult:
    """``backup.verify_snapshot`` — run §3's three conditions against a stored snapshot.

    :param raise_on_failure: when ``True`` (the operation's own behaviour) a failing
        snapshot raises ``RESTORE_UNVERIFIED`` after the row has been moved to ``failed``.
        The CLI passes ``False`` when it wants to *print* the full comparison table before
        exiting non-zero, which is what §5.7 asks a drill to record.

    The row is updated before the raise, not after: a snapshot that just failed verification
    must not still look ``completed`` to the next reader if the caller swallows the
    exception.
    """
    require_caller(OperationId.BACKUP_VERIFY_SNAPSHOT, caller_module)

    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT s.id, s.artifact_path, s.artifact_sha256, s.state,"
                "       m.counts, m.entries"
                "  FROM backup_snapshot AS s"
                "  LEFT JOIN backup_manifest AS m ON m.backup_snapshot_id = s.id"
                " WHERE s.owner_id = ? AND s.id = ?",
                (owner_id, backup_snapshot_id),
            )
            .mappings()
            .first()
        )
    if row is None:
        raise BackupError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.BACKUP_VERIFY_SNAPSHOT.value,
                "resource_kind": "backup_snapshot",
            },
        )
    if row["counts"] is None or row["artifact_sha256"] is None:
        # No manifest, or a snapshot that never completed: condition (3) has nothing to
        # compare against, so the snapshot cannot be verified. That is a refusal, not a pass.
        raise BackupError(
            ErrorCode.RESTORE_UNVERIFIED,
            details_safe={"restore_id": backup_snapshot_id},
        )

    expected_counts = {str(k): int(v) for k, v in json.loads(str(row["counts"])).items()}
    artifact = Path(str(row["artifact_path"]))
    failures: list[str] = []

    if not artifact.exists():
        raise BackupError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.BACKUP_VERIFY_SNAPSHOT.value,
                "resource_kind": "backup_artifact",
            },
        )

    # (1) the bytes are the bytes we recorded.
    sha_matches = sha256_of_file(artifact) == str(row["artifact_sha256"])
    if not sha_matches:
        failures.append("artifact_sha256")

    # (2) and (3) run against a COPY. §3 says "PRAGMA integrity_check trên bản sao": opening
    # the artifact in place would let SQLite create `-wal`/`-shm` sidecars next to it and, on
    # a crash-recovery path, modify it -- verification must not be able to change the thing
    # it is verifying.
    with tempfile.TemporaryDirectory(prefix="rr-verify-") as scratch:
        working = Path(scratch) / "artifact.db"
        shutil.copy2(artifact, working)
        probe = sqlite3.connect(str(working))
        try:
            integrity = str(probe.execute("PRAGMA integrity_check").fetchone()[0])
            observed_counts = collect_counts(probe)
            revision = _alembic_revision(probe)
        finally:
            probe.close()

    if integrity != "ok":
        failures.append("integrity_check")

    mismatches = tuple(
        CountMismatch(key=key, expected=expected_counts.get(key), observed=observed_counts.get(key))
        for key in sorted(set(expected_counts) | set(observed_counts))
        if expected_counts.get(key) != observed_counts.get(key)
    )
    counts_match = not mismatches
    if not counts_match:
        failures.append("counts")

    state = SnapshotState.VERIFIED if not failures else SnapshotState.FAILED
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE backup_snapshot SET state = ? WHERE owner_id = ? AND id = ?",
            (state.value, owner_id, backup_snapshot_id),
        )

    result = VerifyResult(
        backup_snapshot_id=backup_snapshot_id,
        artifact_sha256_matches=sha_matches,
        integrity_check=integrity,
        counts_match=counts_match,
        expected_counts=expected_counts,
        observed_counts=observed_counts,
        mismatches=mismatches,
        state=state,
        alembic_revision_observed=revision,
        failures=tuple(failures),
    )
    if failures and raise_on_failure:
        raise BackupError(
            ErrorCode.RESTORE_UNVERIFIED,
            details_safe={"restore_id": backup_snapshot_id},
        )
    return result


def _alembic_revision(connection: sqlite3.Connection) -> str | None:
    """The artifact's Alembic head — this deployment's real schema identity.

    ``backup-restore.md`` §5.3 step 3 wants the snapshot's schema version checked against the
    application that will run it. ``ENT-schema-migration`` is unimplemented, so the Alembic
    version table is the only thing that actually records the schema generation.
    ``CR-TC-BACKUP-04``.
    """
    try:
        row = connection.execute("SELECT version_num FROM alembic_version").fetchone()
    except sqlite3.Error:
        return None
    return str(row[0]) if row else None


def artifact_revision(artifact: Path) -> str | None:
    """The Alembic head recorded inside an artifact, read from a copy."""
    with tempfile.TemporaryDirectory(prefix="rr-rev-") as scratch:
        working = Path(scratch) / "artifact.db"
        shutil.copy2(artifact, working)
        probe = sqlite3.connect(str(working))
        try:
            return _alembic_revision(probe)
        finally:
            probe.close()


def describe(result: VerifyResult) -> dict[str, Any]:
    """The §5.7 evidence block for one verification, safe to print or store."""
    return {
        "backup_snapshot_id": result.backup_snapshot_id,
        "artifact_sha256_matches": result.artifact_sha256_matches,
        "pragma_integrity_check": result.integrity_check,
        "counts_match": result.counts_match,
        "mismatches": [
            {"key": m.key, "expected": m.expected, "observed": m.observed}
            for m in result.mismatches
        ],
        "state": result.state.value,
        "failed_conditions": list(result.failures),
    }


__all__ = [
    "CountMismatch",
    "VerifyResult",
    "artifact_revision",
    "describe",
    "verify_snapshot",
]
