"""E1/E2 — SC12: the snapshot survives the source disappearing, a restart and a restore.

Oracle fixtures: ``identity/e-source-deleted-snapshot-intact``,
``telegram/k-save-then-source-deleted``, ``recovery/e-saved-snapshot-hash-preserved`` and
``recovery/k-delete-target-preserves-saved``. SC12's own oracle is one sentence:

    ``saved_snapshot.content_hash`` before step 2 == after step 2 == after step 3 == after
    step 4 == H, and H is recomputable from the payload by the canonical-JSON rule of
    ``saved-snapshot.schema.json``; ``COUNT(saved_item active WHERE target=T) = 1`` at every
    moment; reading Saved after step 3 returns content, not ``NOT_FOUND``.

Every test below is that sentence applied to one event. The *recomputation* half matters as
much as the equality: a hash that merely stayed equal to itself would also be satisfied by an
implementation that stored a constant, so each checkpoint recomputes H from the stored payload
bytes with :func:`server.app.saved.snapshot.hash_matches`. That the recomputation agrees with
the **contract** is established separately, in
``tests/contract/test_saved_snapshot_schema.py``, against the literal hex the two positive
fixtures carry.

Deliberately out of scope: ``data.delete_target`` itself. It belongs to
``MOD-data-admin-service`` and card §1 lists it as a non-goal. What is in scope, and is tested
here, is the half of ``recovery/k`` this module owns — that deleting a target's source content
cannot reach the snapshot, and that the foreign key which makes that oracle checkable exists.
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector
from server.app.saved import service, snapshot
from server.app.saved.service import SavedError, TargetRef

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01J0WNER100000000000000000"
WORK_ID = "01JW0RKE100000000000000000"
POST_ID = "01JP0STE100000000000000000"
X_POST_ID = "1900000000000000030"
ANALYSIS_ID = "01JANA1YE10000000000000000"
RECEIPT_ID = "01JRECPTE10000000000000000"
CHECKPOINT_ID = "01JCHKPTE10000000000000000"
RUN_ID = "01JRUN00E10000000000000000"

SAVED_AT = "2026-09-05T21:00:00.000Z"
DELETED_OBSERVED_AT = "2026-09-08T08:00:01.000Z"

WORK_TARGET = TargetRef(kind="work", identifier=WORK_ID)
POST_TARGET = TargetRef(kind="post", identifier=POST_ID)

POST_TEXT = "Bài này thú vị (ảnh chụp trang đầu)."

ANALYSIS_PAYLOAD: dict[str, Any] = {
    "schema_version": "0.1.0",
    "task_type": "summary",
    "result": {
        "content": "Nội dung đọc được từ chính post.",
        "difference_from_existing": {
            "text": "Suy luận: có thể là hướng mới.",
            "comparator": {"kind": "unknown", "note": "Chỉ có post."},
        },
        "limitation_line": "Chỉ có post, không có abstract.",
        "statements": [{"kind": "ai_inference", "text": "Suy luận."}],
    },
}


# --------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------


def _migrate(database: Path) -> None:
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(database)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture()
def database(tmp_path: Path) -> Path:
    """The database file itself, so a test can close it, copy it and open it again."""
    path = tmp_path / "research-radar.db"
    _migrate(path)
    engine = create_sqlite_engine(path)
    try:
        _seed(engine)
    finally:
        engine.dispose()
    return path


@pytest.fixture()
def engine(database: Path) -> Iterator[Engine]:
    built = create_sqlite_engine(database)
    yield built
    built.dispose()


def _seed(engine: Engine) -> None:
    """Fixture ``identity/e``'s ``given`` rows: a post, a work behind it, one valid analysis.

    The ``checkpoint`` and ``ingest_receipt`` rows exist only because ``post`` has real foreign
    keys to them. Seeding them rather than switching the foreign keys off keeps the test
    running against the constraints production runs against.
    """
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at,"
            " failed_login_count) VALUES (?, 1, 'owner', 'Asia/Ho_Chi_Minh', ?, 0)",
            (OWNER_ID, SAVED_AT),
        )
        connection.exec_driver_sql(
            'INSERT INTO checkpoint (id, owner_id, run_id, phase, "sequence", cursor_token,'
            " cursor_state, acked_through_ingest_sequence, items_ingested_total, created_at)"
            " VALUES (?, ?, ?, 'collecting', 1, NULL, 'valid', 1, 1, ?)",
            (CHECKPOINT_ID, OWNER_ID, RUN_ID, SAVED_AT),
        )
        connection.exec_driver_sql(
            "INSERT INTO ingest_receipt (id, owner_id, receipt_kind, idempotency_key, request_id,"
            " payload_hash, schema_version, run_id, job_id, lease_id, lease_epoch,"
            " items_received, posts_inserted, posts_duplicate, items_rejected, works_linked,"
            " checkpoint_id, max_ingest_sequence, committed_at, receipt_hash)"
            " VALUES (?, ?, 'batch_ingest', 'seed-idempotency-key-0001',"
            " '01JREQ0000000000000000000A', ?, '0.1.0', ?, '01JJOB000E10000000000000000',"
            " '01JLEASE0E10000000000000000', 1, 1, 1, 0, 0, 1, ?, 1, ?, ?)",
            (
                RECEIPT_ID,
                OWNER_ID,
                "sha256:" + "a" * 64,
                RUN_ID,
                CHECKPOINT_ID,
                SAVED_AT,
                "sha256:" + "b" * 64,
            ),
        )
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES (?, ?, '2506.06666', 'Một công trình ví dụ', 'partial', 'active', ?, 1,"
            " 'present', ?)",
            (WORK_ID, OWNER_ID, SAVED_AT, SAVED_AT),
        )
        connection.exec_driver_sql(
            "INSERT INTO post (id, owner_id, x_post_id, author_handle, url, text, published_at,"
            " discovered_at, ingest_sequence, discovered_by_run_id, ingest_receipt_id,"
            " is_author_thread_member, media_refs, referenced_links, identity_resolution,"
            " source_snapshot_hash, content_state, source_deleted_observed_at)"
            " VALUES (?, ?, ?, 'alice', ?, ?, '2026-09-05T09:00:00.000Z',"
            " '2026-09-05T11:00:01.000Z', 1, ?, ?, 0, '[]', '[]', 'resolved_linked', ?,"
            " 'present', NULL)",
            (
                POST_ID,
                OWNER_ID,
                X_POST_ID,
                f"https://x.com/alice/status/{X_POST_ID}",
                POST_TEXT,
                RUN_ID,
                RECEIPT_ID,
                "sha256:" + "c" * 64,
            ),
        )
        connection.exec_driver_sql(
            "INSERT INTO post_work (id, owner_id, post_id, work_id, link_evidence, linked_at)"
            " VALUES ('01JPW00E100000000000000000', ?, ?, ?, 'explicit_url_in_post', ?)",
            (OWNER_ID, POST_ID, WORK_ID, SAVED_AT),
        )
        connection.exec_driver_sql(
            "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
            " target_work_id, task_type, source_fingerprint, prompt_version, schema_version,"
            " generation_number, status, payload, payload_hash, evidence_level, provider_name,"
            " model_name, analyzed_at, accepted_from_attempt_id)"
            " VALUES (?, ?, '01JGEN00E10000000000000000', 'work', ?, 'summary', 'fp-e', 'p-1',"
            " '0.1.0', 1, 'valid', ?, ?, 'abstract', 'anthropic', 'claude-opus-5', ?,"
            " '01JATT00E10000000000000000')",
            (
                ANALYSIS_ID,
                OWNER_ID,
                WORK_ID,
                json.dumps(ANALYSIS_PAYLOAD, ensure_ascii=False),
                "sha256:" + "d" * 64,
                SAVED_AT,
            ),
        )


def _stored(engine: Engine) -> dict[str, Any]:
    """The one ``saved_snapshot`` row as stored, plus the active-item count (the SC12 oracle)."""
    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT id, target_kind, target_key_at_save, analysis_id_at_save, payload,"
                "       content_hash, created_at FROM saved_snapshot"
            )
            .mappings()
            .one()
        )
        active = int(
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM saved_item WHERE state = 'active' AND target_key = ?",
                (WORK_TARGET.key,),
            ).scalar_one()
        )
    stored = dict(row)
    stored["_active_for_target"] = active
    return stored


def _assert_intact(stored: dict[str, Any], baseline: dict[str, Any]) -> None:
    """Every column equal, and the hash recomputed from the stored bytes."""
    for column in ("id", "target_kind", "target_key_at_save", "analysis_id_at_save", "created_at"):
        assert stored[column] == baseline[column], column
    assert stored["payload"] == baseline["payload"]
    assert stored["content_hash"] == baseline["content_hash"]
    assert snapshot.hash_matches(str(stored["payload"]), str(stored["content_hash"]))


@pytest.fixture()
def saved(engine: Engine) -> dict[str, Any]:
    """SC12 step 1: ``save.create`` -> one ``saved_item`` + one ``saved_snapshot(hash=H)``."""
    result = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=WORK_TARGET,
        save_channel="app",
        analysis_id=ANALYSIS_ID,
        matched_tags=[{"tag_text": "graph neural networks", "similarity": 0.74}],
        now=SAVED_AT,
    )
    assert result.status == "created"
    baseline = _stored(engine)
    assert baseline["content_hash"] == result.content_hash
    assert baseline["_active_for_target"] == 1
    # The post's text is inside the snapshot -- that is what makes it readable later.
    assert POST_TEXT in str(baseline["payload"])
    return baseline


# --------------------------------------------------------------------------------------
# SC12 steps 2, 3 and 4
# --------------------------------------------------------------------------------------


def test_snapshot_survives_the_source_post_being_deleted_on_x(
    engine: Engine, saved: dict[str, Any], fixture_loader: Any
) -> None:
    """Step 3 of SC12 / fixture ``identity/e``: the observation is written, the snapshot is not.

    ``post.source_deleted_observed_at`` is the only column a duplicate ingest item may write,
    and it is written to the ``post`` row — never to the snapshot. Retention is indefinite
    (REQ-D58), so the post row itself also stays.
    """
    fixture = fixture_loader("identity/e-source-deleted-snapshot-intact")
    expected = fixture.data["expected"]["counts"]

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE post SET source_deleted_observed_at = ?"
            " WHERE id = ? AND source_deleted_observed_at IS NULL",
            (DELETED_OBSERVED_AT, POST_ID),
        )

    _assert_intact(_stored(engine), saved)
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one())
            == expected["saved_snapshot"]
        )
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM post").scalar_one())
            == (expected["post"])
        )

    # And it still reads -- content, not NOT_FOUND (SC12 oracle, REQ-AC12).
    wire = service.read_saved(engine, owner_id=OWNER_ID, target=WORK_TARGET)
    assert wire is not None
    assert wire["snapshot"]["content"]["source_posts"][0]["text"] == POST_TEXT


def test_snapshot_survives_a_restart(database: Path, engine: Engine, saved: dict[str, Any]) -> None:
    """Step 2 of SC12: close everything, reopen the file, H is still H.

    A genuinely new engine on the same file, not a new session on the same engine: the
    question is whether the bytes on disk carry the snapshot, and a warm connection pool
    could answer it from memory.
    """
    engine.dispose()
    restarted = create_sqlite_engine(database)
    try:
        _assert_intact(_stored(restarted), saved)
        assert _stored(restarted)["_active_for_target"] == 1
        wire = service.read_saved(restarted, owner_id=OWNER_ID, target=WORK_TARGET)
        assert wire is not None
        assert wire["snapshot"]["content_hash"] == saved["content_hash"]
    finally:
        restarted.dispose()


def test_snapshot_survives_backup_and_restore(
    database: Path, engine: Engine, saved: dict[str, Any], tmp_path: Path
) -> None:
    """Step 4 of SC12 / fixture ``recovery/e``: hash unchanged across a restore.

    The backup is taken with ``VACUUM INTO``, the WAL-safe consistent-snapshot method
    ``contracts/ops/backup-restore.md`` names; a plain file copy of a WAL database is the
    defect fixture ``recovery/d-wal-unsafe-copy-detected`` exists to catch, so it is not what
    a test of "restore preserves the hash" should be doing. The restore is a copy of that
    artifact into a clean path, opened as a fresh database.

    ``recovery/e``'s forbidden effects are the point: the snapshot must not be *recomputed*
    from current data during restore (the hash would move) and item SI-02 must not be lost
    because its source is gone from X.
    """
    backup = tmp_path / "backup.db"
    with engine.begin() as connection:
        connection.exec_driver_sql("VACUUM INTO ?", (str(backup),))
    engine.dispose()

    restored_path = tmp_path / "restored" / "research-radar.db"
    restored_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup, restored_path)

    restored = create_sqlite_engine(restored_path)
    try:
        _assert_intact(_stored(restored), saved)
        listed = service.list_saved(restored, owner_id=OWNER_ID)
        assert len(listed) == 1
        assert listed[0]["snapshot"]["content_hash"] == saved["content_hash"]
        assert listed[0]["snapshot"]["content"]["source_posts"][0]["text"] == POST_TEXT
    finally:
        restored.dispose()


def test_hash_is_identical_across_all_four_checkpoints(
    database: Path, engine: Engine, saved: dict[str, Any], tmp_path: Path
) -> None:
    """SC12's oracle as one assertion: H before == after restart == after deletion == after
    restore, and H recomputes from the payload at each of them."""
    observed = [saved["content_hash"]]

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE post SET source_deleted_observed_at = ? WHERE id = ?",
            (DELETED_OBSERVED_AT, POST_ID),
        )
    observed.append(_stored(engine)["content_hash"])

    engine.dispose()
    restarted = create_sqlite_engine(database)
    observed.append(_stored(restarted)["content_hash"])

    backup = tmp_path / "backup-2.db"
    with restarted.begin() as connection:
        connection.exec_driver_sql("VACUUM INTO ?", (str(backup),))
    restarted.dispose()
    restored = create_sqlite_engine(backup)
    try:
        final = _stored(restored)
        observed.append(final["content_hash"])
        assert snapshot.hash_matches(str(final["payload"]), str(final["content_hash"]))
    finally:
        restored.dispose()

    assert len(set(observed)) == 1, observed


# --------------------------------------------------------------------------------------
# recovery/k — the half of "delete the source data" this module owns
# --------------------------------------------------------------------------------------


def test_deleting_the_source_posts_leaves_the_snapshot_untouched(
    engine: Engine, saved: dict[str, Any]
) -> None:
    """The posts behind the target are deleted; the snapshot keeps their text and its hash.

    This is REQ-D55's reason for existing, stated as an experiment: the content is *inside*
    the snapshot, so removing the rows it was built from cannot change it.
    """
    with engine.begin() as connection:
        connection.exec_driver_sql("DELETE FROM post_work WHERE work_id = ?", (WORK_ID,))
        connection.exec_driver_sql("DELETE FROM post WHERE id = ?", (POST_ID,))

    _assert_intact(_stored(engine), saved)
    wire = service.read_saved(engine, owner_id=OWNER_ID, target=WORK_TARGET)
    assert wire is not None
    assert wire["snapshot"]["content"]["source_posts"][0]["text"] == POST_TEXT


def test_the_cited_analysis_cannot_be_deleted_out_from_under_a_snapshot(
    engine: Engine, saved: dict[str, Any]
) -> None:
    """``TXN-delete-target``'s oracle: "checked by FK, must be 0 violations".

    ``entities.yaml`` narrows the deletable ``analysis`` rows to those **not** referenced by a
    ``saved_snapshot``. That narrowing is only checkable if the reference is a real foreign
    key, which is what revision ``0008_tc_saved_snapshot`` adds. Here the delete is attempted
    and must be refused.
    """
    assert saved["analysis_id_at_save"] == ANALYSIS_ID
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql("DELETE FROM analysis WHERE id = ?", (ANALYSIS_ID,))
    _assert_intact(_stored(engine), saved)

    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall() == []


def test_removing_the_save_does_not_touch_the_snapshot(
    engine: Engine, saved: dict[str, Any]
) -> None:
    """``save.remove`` is the *first* operation of SRC-SPEC §7.3, and it deletes nothing.

    Card §12 asks the reviewer to look for any path where the snapshot is modified or deleted
    when a tag is dropped or a Save is undone. This is that path, and it does neither.
    """
    result = service.remove_save(engine, owner_id=OWNER_ID, target=WORK_TARGET)
    assert result.removed is True
    stored = _stored(engine)
    _assert_intact(stored, saved)
    assert stored["_active_for_target"] == 0

    still_there = service.read_saved(engine, owner_id=OWNER_ID, target=WORK_TARGET)
    assert still_there is not None
    assert still_there["snapshot"]["content_hash"] == saved["content_hash"]


# --------------------------------------------------------------------------------------
# I17 — a merge moves pointers, never evidence
# --------------------------------------------------------------------------------------


def test_identity_merge_moves_the_pointer_and_leaves_the_snapshot(
    engine: Engine, saved: dict[str, Any]
) -> None:
    """I17: after ``identity.merge_works`` the snapshot is byte-identical.

    Run against the real ``MOD-identity-service``, not a simulation of it — the invariant is
    about what *that* transaction does to *these* rows. ``saved_item.target_work_id`` follows
    the winning work; ``saved_snapshot.target_key_at_save`` does not, because it is historical
    evidence of what was saved and not a pointer to what exists now.
    """
    identity = pytest.importorskip(
        "server.app.identity.service", reason="pending TC-canonical-identity-merge"
    )
    loser = "01JW0RKE200000000000000000"
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES (?, ?, NULL, 'Bản trùng', 'partial', 'active', ?, 2, 'present', ?)",
            (loser, OWNER_ID, SAVED_AT, SAVED_AT),
        )

    merge = identity.merge_works(
        engine,
        owner_id=OWNER_ID,
        work_ids=(WORK_ID, loser),
        linking_evidence={
            "id_scheme": "arxiv",
            "id_value_normalized": "2506.06666",
            "evidence_source": "post_link",
        },
    )
    assert merge.preserved_counts["saved_snapshot"] >= 1

    _assert_intact(_stored(engine), saved)
    assert _stored(engine)["target_key_at_save"] == WORK_TARGET.key

    with engine.connect() as connection:
        pointer = (
            connection.exec_driver_sql(
                "SELECT target_work_id, state FROM saved_item WHERE owner_id = ?", (OWNER_ID,)
            )
            .mappings()
            .one()
        )
    assert pointer["target_work_id"] == merge.winner_work_id
    assert pointer["state"] == "active"


# --------------------------------------------------------------------------------------
# E2 — the write path under a storage fault
# --------------------------------------------------------------------------------------


def test_a_write_fault_during_save_commits_nothing(engine: Engine) -> None:
    """Disk full mid-transaction ⇒ no ``saved_item``, no ``saved_snapshot``, no half state.

    ``TXN-save-target``'s failure timeline names this case: "crash after creating the
    snapshot, before inserting saved_item -> rollback: no snapshot, no saved_item ... no
    orphan snapshot". The injector produces the exact ``OperationalError`` SQLite raises when
    it cannot write, so the rollback under test is SQLite's, not a mock's.
    """
    injector = WriteFaultInjector(engine)
    with injector.disk_full(), pytest.raises(Exception) as failure:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=WORK_TARGET,
            save_channel="app",
            analysis_id=ANALYSIS_ID,
        )
    assert "disk is full" in str(failure.value)

    with engine.connect() as connection:
        assert int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_item").scalar_one()) == 0
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one()) == 0
        )


def test_save_create_is_not_in_the_storage_refusal_list_today(engine: Engine) -> None:
    """A documented contract divergence, pinned so it cannot be forgotten — ``CR-TC-SAVED-09``.

    ``contracts/http/openapi.yaml`` declares a 503 ``STORAGE_WRITE_FAILED`` on ``save.create``
    and says in as many words: "``storage.health = write_blocked`` hoặc ``maintenance``:
    mutation KHÔNG được ACK và KHÔNG có gì được ghi". ``contracts/state/storage.yaml``'s
    ``write_blocked.refuses`` list — the closed list the state machine is built from — does
    **not** name ``save.create``.

    This module does not resolve that by itself. It calls ``guard.assert_writable`` on the
    normal path like every other mutating service, so ``save.create`` starts being refused the
    moment the contract lists it; and until then the substantive requirement is still met,
    because a write that cannot commit rolls the whole transaction back and ACKs nothing
    (asserted by the test above). What is asserted here is the divergence itself, so that
    closing the CR makes this test fail and be revisited rather than silently drift.
    """
    from rr_contracts.generated.states import StorageHealth

    from server.app.storage.guard import StorageGuard
    from server.app.storage.health import REFUSALS

    assert OperationId.SAVE_CREATE not in REFUSALS[StorageHealth.WRITE_BLOCKED]
    assert OperationId.SAVE_CREATE not in REFUSALS[StorageHealth.MAINTENANCE]

    guard = StorageGuard()
    guard.record_write_failure()
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED
    # Consequence of the two assertions above, spelled out: the guard admits the call today.
    guard.assert_writable(OperationId.SAVE_CREATE)


def test_a_blocked_store_still_leaves_nothing_written(engine: Engine) -> None:
    """openapi's substantive requirement for the 503 case: no ACK, and nothing written.

    The guard is in ``write_blocked`` *and* the store genuinely cannot write. Whichever of the
    two refuses first, the caller must not get a saved item and the tables must not move --
    which is the half of the requirement that does not depend on ``CR-TC-SAVED-09``.
    """
    from server.app.storage.guard import StorageGuard

    guard = StorageGuard()
    guard.record_write_failure()
    injector = WriteFaultInjector(engine)

    with injector.disk_full(), pytest.raises(Exception) as failure:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=WORK_TARGET,
            save_channel="app",
            analysis_id=ANALYSIS_ID,
            guard=guard,
        )
    assert isinstance(failure.value, SavedError) or "disk is full" in str(failure.value)

    with engine.connect() as connection:
        assert int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_item").scalar_one()) == 0
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one()) == 0
        )


def test_the_guard_is_asked_before_the_transaction_opens(engine: Engine) -> None:
    """``I02``: ``assert_writable`` runs *before* any write is attempted, not around it.

    Asserted by making the guard raise and counting the writes the engine saw: zero. An
    implementation that opened the transaction first and caught the failure afterwards would
    show a non-zero count here even though the row counts would look identical.
    """
    from server.app.storage.guard import StorageRefused, error_envelope

    class _RefusingGuard:
        def assert_writable(self, operation_id: OperationId) -> None:
            raise StorageRefused(
                error_envelope(
                    ErrorCode.STORAGE_WRITE_FAILED,
                    details_safe={
                        "storage_health": "write_blocked",
                        "failed_operation_id": operation_id.value,
                    },
                    retry_after_ms=30_000,
                )
            )

    injector = WriteFaultInjector(engine)
    injector.reset_counters()

    with pytest.raises(SavedError) as refused:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=WORK_TARGET,
            save_channel="app",
            analysis_id=ANALYSIS_ID,
            guard=_RefusingGuard(),
        )
    assert refused.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert refused.value.http_status == 503
    assert refused.value.retry_after_ms == 30_000
    assert injector.writes_attempted == 0
    with engine.connect() as connection:
        assert int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_item").scalar_one()) == 0
