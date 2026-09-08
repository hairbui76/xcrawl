"""E1/E2 — SC43: a copy taken while the database was writing is refused as a backup.

Fixture ``recovery/d-wal-unsafe-copy-detected`` is the oracle, and its point is narrow and
sharp: the bad artifact **passes** the two checks an implementer reaches for first.

* ``sha256(artifact) == artifact_sha256`` — true. The file was hashed after it was copied;
  nothing rotted.
* ``PRAGMA integrity_check`` — ``ok``. The file is a structurally valid SQLite database. It
  is not corrupt; it is *incomplete*.
* counts queried from inside the artifact vs. the manifest — **this** is where it fails.

The fixture says so itself: "Điều kiện (1) và (2) một mình KHÔNG phát hiện được lỗi này."

The defect is manufactured, not simulated
-----------------------------------------
:func:`_wal_unsafe_copy` reproduces the real failure rather than a stand-in for it: rows are
committed into a WAL-mode database and left un-checkpointed, so they physically live in the
``-wal`` sidecar, and then only the ``.db`` file is copied — which is what ``cp`` on a running
database does. Nothing is deleted from the copy and no count is doctored; the rows are missing
because WAL is part of the durable state and the copy left it behind. That is exactly the
scenario ``AMD-B11`` amended ``REQ-D58`` to prevent, so the test would still hold if the
detection logic were rewritten from scratch.

The control case matters as much: ``VACUUM INTO`` over the *same* database at the *same*
moment produces an artifact that verifies clean. Without it, "counts mismatch" could be an
artefact of the harness rather than of the copy method.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from server.app.backup import verify
from server.app.backup.restore import restore_snapshot
from server.app.backup.snapshot import (
    BackupError,
    SnapshotMethod,
    SnapshotState,
    build_manifest_body,
    canonical_json,
    collect_counts,
    create_snapshot,
    new_ulid,
    sha256_of_file,
    sha256_of_json,
)
from server.app.db import create_sqlite_engine
from server.app.storage.guard import StorageGuard

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01J0WNER100000000000000000"
NOW = "2026-09-08T03:00:00.000Z"

#: Rows committed and checkpointed into the `.db` file before the copy.
CHECKPOINTED_WORKS = 3
#: Rows committed *after* the checkpoint. These live in the `-wal` file and are what a
#: `.db`-only copy silently loses.
WAL_RESIDENT_WORKS = 4


@pytest.fixture()
def database(tmp_path: Path) -> Path:
    path = tmp_path / "research-radar.db"
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(path)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous
    return path


@pytest.fixture()
def engine(database: Path) -> Iterator[Engine]:
    built = create_sqlite_engine(database)
    _seed_owner(built)
    yield built
    built.dispose()


def _seed_owner(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at,"
            " failed_login_count) VALUES (?, 1, 'owner', 'Asia/Ho_Chi_Minh', ?, 0)",
            (OWNER_ID, NOW),
        )


def _insert_works(engine: Engine, count: int, *, prefix: str, first_sequence: int) -> None:
    """``work.ingest_sequence`` is UNIQUE per owner, so each batch continues the sequence."""
    with engine.begin() as connection:
        for index in range(count):
            sequence = first_sequence + index
            connection.exec_driver_sql(
                "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
                " identity_state, first_discovered_at, ingest_sequence, content_state,"
                " created_at) VALUES (?, ?, ?, ?, 'partial', 'active', ?, ?, 'present', ?)",
                (
                    f"01JWRK{prefix}{sequence:019d}"[:26],
                    OWNER_ID,
                    f"25{prefix}.{sequence:05d}",
                    f"Work {prefix}-{sequence}",
                    NOW,
                    sequence,
                    NOW,
                ),
            )


def _checkpoint(engine: Engine) -> None:
    """Force everything in the WAL into the main file, so the next writes are WAL-resident."""
    with engine.begin() as connection:
        connection.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")


def _wal_unsafe_copy(database: Path, destination: Path) -> None:
    """What ``cp research-radar.db backup.db`` does on a live WAL database.

    Only the main file is copied; ``-wal`` and ``-shm`` are left behind. This is the method
    ``AMD-B11`` removed from the contract, reproduced here so the detector has something real
    to detect.
    """
    shutil.copy2(database, destination)


def _register_artifact(
    engine: Engine, *, artifact: Path, counts: dict[str, int], method: SnapshotMethod
) -> str:
    """Register a hand-made artifact with a manifest, as an operator with a copy would.

    ``create_snapshot`` cannot produce a WAL-unsafe artifact -- it has no such branch, which
    is the point of that module -- so the defective input is constructed here and handed to
    ``verify`` exactly as a registered snapshot.
    """
    snapshot_id = new_ulid()
    manifest_body = build_manifest_body(
        backup_snapshot_id=snapshot_id,
        method=method,
        artifact_path=str(artifact),
        artifact_sha256=sha256_of_file(artifact),
        artifact_bytes=artifact.stat().st_size,
        created_at=NOW,
        completed_at=NOW,
        counts=counts,
        alembic_revision=None,
        embedding_model_artifact_sha256=None,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO backup_snapshot (id, owner_id, method, started_at, completed_at,"
            " artifact_path, artifact_sha256, state)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 'completed')",
            (
                snapshot_id,
                OWNER_ID,
                method.value,
                NOW,
                NOW,
                str(artifact),
                sha256_of_file(artifact),
            ),
        )
        connection.exec_driver_sql(
            "INSERT INTO backup_manifest (id, owner_id, backup_snapshot_id, entries,"
            " manifest_sha256, counts, embedding_model_artifact_sha256)"
            " VALUES (?, ?, ?, ?, ?, ?, NULL)",
            (
                new_ulid(),
                OWNER_ID,
                snapshot_id,
                canonical_json(manifest_body["entries"]),
                sha256_of_json(manifest_body),
                canonical_json(counts),
            ),
        )
    return snapshot_id


@pytest.fixture()
def wal_unsafe(engine: Engine, database: Path, tmp_path: Path) -> dict[str, Any]:
    """A registered snapshot whose artifact is a ``.db``-only copy of a live WAL database."""
    _insert_works(engine, CHECKPOINTED_WORKS, prefix="A", first_sequence=1)
    _checkpoint(engine)
    _insert_works(
        engine, WAL_RESIDENT_WORKS, prefix="B", first_sequence=CHECKPOINTED_WORKS + 1
    )  # these stay in the -wal file

    artifact = tmp_path / "wal-unsafe.db"
    _wal_unsafe_copy(database, artifact)

    with engine.connect() as connection:
        live_counts = collect_counts(connection)

    snapshot_id = _register_artifact(
        engine, artifact=artifact, counts=live_counts, method=SnapshotMethod.VACUUM_INTO
    )
    return {"snapshot_id": snapshot_id, "artifact": artifact, "counts": live_counts}


# --------------------------------------------------------------------------------------
# The three conditions, individually
# --------------------------------------------------------------------------------------


def test_the_copy_passes_conditions_one_and_two(wal_unsafe: dict[str, Any]) -> None:
    """The premise of fixture ``d``: hash matches and ``integrity_check`` says ``ok``.

    Asserted before the detection test so that a later failure cannot be mistaken for "the
    artifact was obviously broken". It is not obviously broken. That is the danger.
    """
    artifact: Path = wal_unsafe["artifact"]
    probe = sqlite3.connect(str(artifact))
    try:
        assert probe.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        probe.close()
    # Condition (1) is trivially true and is asserted through the module that checks it.
    assert sha256_of_file(artifact).startswith("sha256:")


def test_wal_unsafe_copy_is_detected_by_the_counts(
    engine: Engine, wal_unsafe: dict[str, Any], fixture_loader: Any
) -> None:
    """Condition (3) fails: rows committed into the WAL are absent from the copy.

    The fixture's ``artifact_actual_counts`` are lower than its ``manifest_counts`` for
    exactly this reason; here the shortfall is the number of rows written after the
    checkpoint, which the test controls and can therefore assert exactly.
    """
    fixture = fixture_loader("recovery/d-wal-unsafe-copy-detected")
    assert fixture.data["expected"]["checks"]["artifact_sha256_matches"] is True
    assert fixture.data["expected"]["checks"]["pragma_integrity_check"] == "ok"
    assert fixture.data["expected"]["checks"]["counts_match"] is False

    result = verify.verify_snapshot(
        engine,
        owner_id=OWNER_ID,
        backup_snapshot_id=wal_unsafe["snapshot_id"],
        raise_on_failure=False,
    )
    assert result.artifact_sha256_matches is True
    assert result.integrity_check == "ok"
    assert result.counts_match is False
    assert result.failures == ("counts",)

    by_key = {m.key: m for m in result.mismatches}
    assert "work" in by_key, result.mismatches
    assert by_key["work"].expected == CHECKPOINTED_WORKS + WAL_RESIDENT_WORKS
    assert by_key["work"].observed == CHECKPOINTED_WORKS


def test_verify_refuses_with_restore_unverified(engine: Engine, wal_unsafe: dict[str, Any]) -> None:
    """``backup.verify_snapshot`` ⇒ ``RESTORE_UNVERIFIED``, and the row is not ``verified``.

    Fixture ``d``'s forbidden effects: do not write ``state='verified'``, and do not conclude
    "backup is valid" from the hash alone.
    """
    with pytest.raises(BackupError) as refused:
        verify.verify_snapshot(
            engine, owner_id=OWNER_ID, backup_snapshot_id=wal_unsafe["snapshot_id"]
        )
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED

    with engine.connect() as connection:
        state = connection.exec_driver_sql(
            "SELECT state FROM backup_snapshot WHERE id = ?", (wal_unsafe["snapshot_id"],)
        ).scalar_one()
    assert state != SnapshotState.VERIFIED.value


def test_a_failed_snapshot_cannot_be_restored(engine: Engine, wal_unsafe: dict[str, Any]) -> None:
    """Fixture ``d`` forbidden effect #1: this snapshot must not reach ``restore_snapshot``.

    Enforced by requiring ``verified`` rather than by asking the operator not to — the
    refusal happens before the artifact is copied anywhere and before the store is locked.
    """
    verify.verify_snapshot(
        engine,
        owner_id=OWNER_ID,
        backup_snapshot_id=wal_unsafe["snapshot_id"],
        raise_on_failure=False,
    )
    guard = StorageGuard()
    guard.enter_maintenance()
    with pytest.raises(BackupError) as refused:
        restore_snapshot(
            engine,
            owner_id=OWNER_ID,
            backup_snapshot_id=wal_unsafe["snapshot_id"],
            restore_request_id="RR-wal-unsafe",
            confirmation_phrase="RESTORE",
            guard=guard,
        )
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED
    # Still only in the maintenance window the operator opened: the refusal came before
    # step 1 of §5.2, so nothing moved to `recovery_required`.
    assert guard.current_health().value == "maintenance"
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM restore_record").scalar_one()) == 0
        )


# --------------------------------------------------------------------------------------
# The control: a WAL-safe snapshot of the same database verifies clean
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("method", [SnapshotMethod.VACUUM_INTO, SnapshotMethod.ONLINE_BACKUP_API])
def test_wal_safe_methods_capture_the_wal_resident_rows(
    engine: Engine, tmp_path: Path, method: SnapshotMethod
) -> None:
    """Both approved methods see the rows the ``.db``-only copy lost, and verify clean.

    This is what makes the previous tests meaningful: the mismatch is a property of the copy
    *method*, not of the harness. Both methods read through the SQLite engine, so the WAL is
    part of what they read.
    """
    _insert_works(engine, CHECKPOINTED_WORKS, prefix="A", first_sequence=1)
    _checkpoint(engine)
    _insert_works(engine, WAL_RESIDENT_WORKS, prefix="B", first_sequence=CHECKPOINTED_WORKS + 1)

    result = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / f"safe-{method.value}.db",
        snapshot_request_id=f"REQ-{method.value}",
        method=method,
    )
    assert result.counts["work"] == CHECKPOINTED_WORKS + WAL_RESIDENT_WORKS

    verified = verify.verify_snapshot(
        engine, owner_id=OWNER_ID, backup_snapshot_id=result.backup_snapshot_id
    )
    assert verified.verified is True
    assert verified.counts_match is True
    assert verified.mismatches == ()
    assert verified.observed_counts["work"] == CHECKPOINTED_WORKS + WAL_RESIDENT_WORKS


def test_no_file_copy_method_exists(engine: Engine, tmp_path: Path) -> None:
    """``AMD-B11``: ``file_copy`` is not a method, at any layer.

    Not in the enum, and not accepted by the table either — so a snapshot taken the forbidden
    way cannot even be recorded as having happened.
    """
    assert "file_copy" not in {m.value for m in SnapshotMethod}
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO backup_snapshot (id, owner_id, method, started_at, state)"
            " VALUES (?, ?, 'file_copy', ?, 'running')",
            (new_ulid(), OWNER_ID, NOW),
        )


def test_manifest_does_not_contain_its_own_entry(engine: Engine, tmp_path: Path) -> None:
    """``entities.yaml``: the manifest never lists itself — a self-hash cannot be recomputed."""
    result = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "self.db",
        snapshot_request_id="REQ-self",
    )
    with engine.connect() as connection:
        entries = json.loads(
            str(
                connection.exec_driver_sql(
                    "SELECT entries FROM backup_manifest WHERE backup_snapshot_id = ?",
                    (result.backup_snapshot_id,),
                ).scalar_one()
            )
        )
    assert {entry["role"] for entry in entries} == {"database"}
    assert all(entry["sha256"] != result.manifest_sha256 for entry in entries)


def test_rerunning_the_same_snapshot_command_does_not_copy_twice(
    engine: Engine, tmp_path: Path
) -> None:
    """A retried CLI invocation replays instead of taking a second copy.

    ``ports.yaml`` scopes idempotency to ``snapshot_request_id``; ``entities.yaml`` declares no
    column for it, so the replay key is the artifact path (``CR-TC-BACKUP-07``). What that
    covers is the case that actually happens — the operator runs the same command again — and
    the test asserts exactly that, not a stronger claim.
    """
    first = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "once.db",
        snapshot_request_id="REQ-once",
    )
    second = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "once.db",
        snapshot_request_id="REQ-once",
    )
    assert second.replayed is True
    assert second.backup_snapshot_id == first.backup_snapshot_id
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM backup_snapshot").scalar_one())
            == 1
        )


# --------------------------------------------------------------------------------------
# Pinned contract divergences (CR-TC-BACKUP-02)
# --------------------------------------------------------------------------------------


def test_entity_enums_do_not_carry_the_fixture_vocabulary(engine: Engine) -> None:
    """``CR-TC-BACKUP-02``, pinned so that closing it forces this code to be revisited.

    Fixture ``recovery/d`` expects ``backup_snapshot.state == 'invalid'`` and
    ``integrity_check_outcome == 'mismatch'``; ``backup-restore.md`` §5.6 clause 1 says
    ``'ok'``. ``entities.yaml`` has none of those three values, and the Coordinator ruled the
    entity contract wins — so this package writes ``failed`` and ``passed``. The mapping is
    asserted here rather than left in prose: if the enums are ever widened, this test fails
    and the mapping gets looked at instead of silently diverging.
    """
    assert {s.value for s in SnapshotState} == {"running", "completed", "failed", "verified"}
    for forbidden in ("invalid", "mismatch", "ok"):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO backup_snapshot (id, owner_id, method, started_at, state)"
                " VALUES (?, ?, 'vacuum_into', ?, ?)",
                (new_ulid(), OWNER_ID, NOW, forbidden),
            )
