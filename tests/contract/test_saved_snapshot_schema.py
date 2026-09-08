"""E1 — SC48: the Saved schema accepts the two valid payloads and rejects the five bad ones.

The oracle is ``contracts/schemas/saved-snapshot.schema.json`` and the seven fixtures SC48
names, read as data (SRC-PLAN §15). Nothing here is asserted against a hand-written expectation
and no fixture is edited to make a test pass.

Three questions, and they are not the same question
---------------------------------------------------
1. *Does the contract's schema accept/reject what the fixtures say it should?* — pure schema,
   two positives and five negatives (``test_positive_fixture_validates`` /
   ``test_negative_fixture_is_rejected``).
2. *Does this implementation's canonicalisation agree with the contract's?* — the two positive
   fixtures carry a **literal** ``content_hash`` computed outside this repository, and
   :func:`server.app.saved.snapshot.compute_content_hash` has to reproduce both hex strings
   exactly. This is the assertion that makes every later "the hash did not change" oracle
   mean something: without it, both sides of those comparisons could be wrong together.
3. *Can this implementation produce the five defects at all?* — for each negative, the guard
   that refuses it is exercised against a real database, and the row counts are asserted
   unchanged. A schema that rejects a payload the server would happily store is only half a
   defence.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from jsonschema import Draft202012Validator
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from server.app.db import create_sqlite_engine
from server.app.saved import service, snapshot
from server.app.saved.service import SavedError, TargetRef

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "saved-snapshot.schema.json"

#: SC48 calls these "hai ca dương" — both carry a literal ``content_hash``.
POSITIVE_FIXTURES = (
    "telegram/j-concurrent-save-app-telegram",
    "telegram/k-save-then-source-deleted",
)

#: SC48's five negatives, each pinned to the pointer the fixture declares.
NEGATIVE_FIXTURES = (
    "telegram/neg-saved-snapshot-missing-content-hash",
    "telegram/neg-saved-snapshot-bad-hash-format",
    "telegram/neg-saved-snapshot-item-without-snapshot",
    "telegram/neg-saved-snapshot-target-both-ids",
    "telegram/neg-saved-snapshot-summary-missing-limitation",
)

OWNER_ID = "01J0WNER100000000000000000"
WORK_ID = "01JW0RKD100000000000000000"
ANALYSIS_ID = "01JANA1YD10000000000000000"
NOW = "2026-09-08T10:00:00.000Z"

ANALYSIS_PAYLOAD: dict[str, Any] = {
    "schema_version": "0.1.0",
    "task_type": "summary",
    "result": {
        "content": "Nội dung tóm tắt.",
        "difference_from_existing": {
            "text": "Điểm khác so với cái đã có.",
            "comparator": {"kind": "unknown", "note": "Không có nguồn so sánh."},
        },
        "limitation_line": "Một dòng hạn chế.",
        "statements": [{"kind": "ai_inference", "text": "Suy luận."}],
    },
}


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    """The contract's schema, as a Draft 2020-12 validator with format checking on."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    """A database built by the real migration chain, not by ``CREATE TABLE`` in a test."""
    database = tmp_path / "research-radar.db"
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
    built = create_sqlite_engine(database)
    _seed_work_with_analysis(built)
    yield built
    built.dispose()


def _seed_work_with_analysis(engine: Engine) -> None:
    """One owner, one work, one valid summary analysis. No posts: an empty ``source_posts``
    array is explicitly valid for a work with no readable post (schema ``minItems: 0``)."""
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at,"
            " failed_login_count) VALUES (?, 1, 'owner', 'Asia/Ho_Chi_Minh', ?, 0)",
            (OWNER_ID, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES (?, ?, '2505.05555', 'Một công trình ví dụ', 'partial', 'active', ?, 1,"
            " 'present', ?)",
            (WORK_ID, OWNER_ID, NOW, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
            " target_work_id, task_type, source_fingerprint, prompt_version, schema_version,"
            " generation_number, status, payload, payload_hash, evidence_level, provider_name,"
            " model_name, analyzed_at, accepted_from_attempt_id)"
            " VALUES (?, ?, '01JGEN00000000000000000001', 'work', ?, 'summary', 'fp-1', 'p-1',"
            " '0.1.0', 1, 'valid', ?, ?, 'abstract', 'anthropic', 'claude-opus-5', ?,"
            " '01JATT00000000000000000001')",
            (
                ANALYSIS_ID,
                OWNER_ID,
                WORK_ID,
                json.dumps(ANALYSIS_PAYLOAD, ensure_ascii=False),
                "sha256:" + "0" * 64,
                NOW,
            ),
        )


def _counts(engine: Engine) -> tuple[int, int]:
    with engine.connect() as connection:
        items = connection.exec_driver_sql("SELECT COUNT(*) FROM saved_item").scalar_one()
        snapshots = connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one()
    return int(items), int(snapshots)


# --------------------------------------------------------------------------------------
# 1. The schema itself
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("ref", POSITIVE_FIXTURES)
def test_positive_fixture_validates(ref: str, fixture_loader: Any, validator: Any) -> None:
    """SC48: "hai ca dương: 0 lỗi schema"."""
    fixture = fixture_loader(ref)
    assert fixture.data["validation_target"].endswith("saved-snapshot.schema.json")
    assert fixture.data["expected_validation"] == "accept"
    errors = sorted(validator.iter_errors(fixture.data["saved"]), key=str)
    assert errors == [], [f"{list(e.absolute_path)}: {e.message}" for e in errors]


@pytest.mark.parametrize("ref", NEGATIVE_FIXTURES)
def test_negative_fixture_is_rejected(ref: str, fixture_loader: Any, validator: Any) -> None:
    """SC48: "năm ca âm: ≥ 1 lỗi tại con trỏ đã khai"."""
    fixture = fixture_loader(ref)
    assert fixture.data["expected_validation"] == "reject"
    errors = list(validator.iter_errors(fixture.data["saved"]))
    assert errors, f"{ref} was accepted by the schema; the negative case is not enforced"


# --------------------------------------------------------------------------------------
# 2. This implementation's canonicalisation vs. the contract's
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("ref", POSITIVE_FIXTURES)
def test_content_hash_reproduces_the_fixture_hex(ref: str, fixture_loader: Any) -> None:
    """``sha256(JCS(content))`` recomputed here equals the hex the fixture carries.

    The two hashes were computed from the contract, not from this code. Reproducing them is
    the only evidence that "the hash did not change" means anything in the other two test
    files — a canonicaliser that disagreed with the contract would still compare equal to
    itself.
    """
    stored = fixture_loader(ref).data["saved"]["snapshot"]
    assert snapshot.compute_content_hash(stored["content"]) == stored["content_hash"]


def test_hash_ignores_key_insertion_order(fixture_loader: Any) -> None:
    """Canonicalisation, not serialisation order, decides the hash.

    Re-inserting the same members in reverse order must not move the hash; if it did, a
    snapshot rewritten by any code path that happened to build the dict differently would
    look tampered with.
    """
    content = fixture_loader(POSITIVE_FIXTURES[0]).data["saved"]["snapshot"]["content"]
    reversed_order = dict(reversed(list(content.items())))
    assert snapshot.compute_content_hash(reversed_order) == snapshot.compute_content_hash(content)


def test_hash_matches_reads_the_stored_bytes(fixture_loader: Any) -> None:
    """:func:`hash_matches` verifies a stored payload string, and rejects a mutated one."""
    stored = fixture_loader(POSITIVE_FIXTURES[1]).data["saved"]["snapshot"]
    payload_json = snapshot.canonical_json(stored["content"])
    assert snapshot.hash_matches(payload_json, stored["content_hash"])
    tampered = dict(stored["content"], display_title="something else")
    assert not snapshot.hash_matches(snapshot.canonical_json(tampered), stored["content_hash"])


# --------------------------------------------------------------------------------------
# 3. What this implementation actually stores
# --------------------------------------------------------------------------------------


def test_stored_snapshot_validates_against_the_schema(engine: Engine, validator: Any) -> None:
    """A real ``save.create`` produces a wire object the contract's schema accepts.

    Round-trips through the database on purpose: the schema check is worth little if it runs
    on an in-memory object that the storage layer would have altered on the way in or out.
    """
    result = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TargetRef(kind="work", identifier=WORK_ID),
        save_channel="app",
        analysis_id=ANALYSIS_ID,
        matched_tags=[{"tag_text": "protein folding", "similarity": 0.81}],
    )
    assert result.status == "created"

    wire = service.read_saved(
        engine, owner_id=OWNER_ID, target=TargetRef(kind="work", identifier=WORK_ID)
    )
    assert wire is not None
    errors = sorted(validator.iter_errors(wire), key=str)
    assert errors == [], [f"{list(e.absolute_path)}: {e.message}" for e in errors]
    assert wire["snapshot"]["content_hash"] == result.content_hash
    assert snapshot.compute_content_hash(wire["snapshot"]["content"]) == result.content_hash
    # The tag array is a snapshot, not a live join: it is inside the hashed content.
    assert wire["snapshot"]["content"]["matched_tags"][0]["tag_text"] == "protein folding"


# --------------------------------------------------------------------------------------
# 4. Each negative's defect, against a real database — "0 hàng ghi" (card §8)
# --------------------------------------------------------------------------------------


def test_neg_summary_missing_limitation_is_refused(engine: Engine) -> None:
    """``neg-saved-snapshot-summary-missing-limitation``: a DEFECTIVE analysis ⇒ no save.

    Still a refusal after ``OD-20260908-10`` item 1, and the distinction is the point. That
    decision allows saving a target **nothing has analysed yet**. Here an analysis exists and
    is missing a line ``REQ-D20`` requires — a data defect. Marking it "not analysed yet" would
    file the defect under a label asserting the opposite and would make the marker useless for
    the case it exists for. Nothing is written either way.
    """
    before = _counts(engine)
    incomplete = json.loads(json.dumps(ANALYSIS_PAYLOAD))
    del incomplete["result"]["limitation_line"]
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE analysis SET payload = ? WHERE id = ?",
            (json.dumps(incomplete, ensure_ascii=False), ANALYSIS_ID),
        )
    with pytest.raises(SavedError) as refused:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=TargetRef(kind="work", identifier=WORK_ID),
            save_channel="app",
            analysis_id=ANALYSIS_ID,
        )
    assert refused.value.code is ErrorCode.VALIDATION_ERROR
    assert refused.value.details_safe["field_path"] == "snapshot.content.summary"
    assert _counts(engine) == before


def test_un_analysed_target_saves_with_the_missing_marker(engine: Engine, validator: Any) -> None:
    """``OD-20260908-10`` item 1, closing ``CR-TC-SAVED-04``: the save is ALLOWED.

    Three things have to hold together, and each is asserted:

    1. the snapshot validates against the unchanged contract schema — no field was invented;
    2. the summary is the fixed marker, identical in all three lines, so nothing in it can be
       read as a claim about the target (B16);
    3. ``analysis_id_at_save`` is NULL — the schema's own declared signal for "no valid
       analysis", and the field a consumer should branch on rather than string-matching the
       label.

    ``evidence_level`` is the lowest rung: with no analysis nothing supports a higher one
    (``REQ-D21``). The ``content_hash`` covers these bytes like any other snapshot, so an
    un-analysed save is immutable on the same terms.
    """
    before = _counts(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("DELETE FROM analysis WHERE id = ?", (ANALYSIS_ID,))

    result = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TargetRef(kind="work", identifier=WORK_ID),
        save_channel="app",
    )
    assert result.status == "created"
    assert _counts(engine) == (before[0] + 1, before[1] + 1)

    wire = service.read_saved(
        engine, owner_id=OWNER_ID, target=TargetRef(kind="work", identifier=WORK_ID)
    )
    assert wire is not None
    errors = sorted(validator.iter_errors(wire), key=str)
    assert errors == [], [f"{list(e.absolute_path)}: {e.message}" for e in errors]

    assert wire["snapshot"]["analysis_id_at_save"] is None
    content = wire["snapshot"]["content"]
    assert snapshot.is_missing_summary(content["summary"])
    assert set(
        [
            content["summary"]["content_vi"],
            content["summary"]["novelty_vi"],
            content["summary"]["limitation_vi"],
        ]
    ) == {snapshot.SUMMARY_NOT_ANALYSED}
    assert content["summary"]["comparator"] == "unknown"
    assert "claim_kinds" not in content["summary"]
    assert "analysis_ref" not in content
    assert content["evidence_level"] == snapshot.EVIDENCE_LEVEL_NOT_ANALYSED
    assert snapshot.compute_content_hash(content) == wire["snapshot"]["content_hash"]


def test_the_missing_marker_is_a_constant_not_derived_from_the_target(engine: Engine) -> None:
    """The marker must be the same for every target, or it is an inference (B16).

    Two different targets saved with no analysis must produce byte-identical summary blocks.
    A marker that varied with the target would be exactly the "invented text" the decision
    forbids, dressed as a label.
    """
    with engine.begin() as connection:
        connection.exec_driver_sql("DELETE FROM analysis WHERE id = ?", (ANALYSIS_ID,))
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES ('01JW0RK2000000000000000000', ?, '2505.09999', 'Công trình khác',"
            " 'partial', 'active', ?, 2, 'present', ?)",
            (OWNER_ID, NOW, NOW),
        )
    first = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TargetRef(kind="work", identifier=WORK_ID),
        save_channel="app",
    )
    second = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TargetRef(kind="work", identifier="01JW0RK2000000000000000000"),
        save_channel="app",
    )
    assert first.content_hash != second.content_hash  # different targets, different snapshots
    summaries = []
    for target_id in (WORK_ID, "01JW0RK2000000000000000000"):
        wire = service.read_saved(
            engine, owner_id=OWNER_ID, target=TargetRef(kind="work", identifier=target_id)
        )
        assert wire is not None
        summaries.append(wire["snapshot"]["content"]["summary"])
    assert summaries[0] == summaries[1]


def test_neg_target_both_ids_is_refused(engine: Engine) -> None:
    """``neg-saved-snapshot-target-both-ids``: the union is refused at the boundary…"""
    before = _counts(engine)
    with pytest.raises(SavedError) as refused:
        TargetRef.from_object(
            {"kind": "post", "post_id": "01JP0ST1000000000000000000", "work_id": WORK_ID},
            OperationId.SAVE_CREATE,
        )
    assert refused.value.code is ErrorCode.VALIDATION_ERROR
    assert _counts(engine) == before


def test_neg_target_both_ids_is_also_refused_by_the_table(engine: Engine) -> None:
    """…and again by the table, so a code path that skipped the check still cannot store it."""
    before = _counts(engine)
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO saved_item (id, owner_id, target_kind, target_work_id, target_post_id,"
            " state, saved_at, save_channel, saved_snapshot_id)"
            " VALUES ('01JBAD0000000000000000001', ?, 'work', ?, '01JP0ST1000000000000000000',"
            " 'active', ?, 'app', '01JSNAP1000000000000000000')",
            (OWNER_ID, WORK_ID, NOW),
        )
    assert _counts(engine) == before


def test_neg_item_without_snapshot_is_refused_by_the_table(engine: Engine) -> None:
    """``neg-saved-snapshot-item-without-snapshot``: ``saved_snapshot_id`` is NOT NULL.

    "There is no Saved without a snapshot" (REQ-D55) is a column constraint, not a
    convention, so no service bug can produce the row.
    """
    before = _counts(engine)
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO saved_item (id, owner_id, target_kind, target_work_id, state,"
            " saved_at, save_channel, saved_snapshot_id)"
            " VALUES ('01JBAD0000000000000000002', ?, 'work', ?, 'active', ?, 'app', NULL)",
            (OWNER_ID, WORK_ID, NOW),
        )
    assert _counts(engine) == before


def test_neg_missing_content_hash_is_refused_by_the_table(engine: Engine) -> None:
    """``neg-saved-snapshot-missing-content-hash``: ``content_hash`` is NOT NULL."""
    before = _counts(engine)
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO saved_snapshot (id, owner_id, target_kind, target_key_at_save,"
            " payload, content_hash, created_at)"
            " VALUES ('01JBAD0000000000000000003', ?, 'work', ?, '{}', NULL, ?)",
            (OWNER_ID, f"work:{WORK_ID}", NOW),
        )
    assert _counts(engine) == before


def test_neg_bad_hash_format_is_refused_by_the_table(engine: Engine) -> None:
    """``neg-saved-snapshot-bad-hash-format``: ``CHECK (content_hash GLOB 'sha256:*')``.

    ``deadbeef`` is what the fixture carries. A hash whose format is not fixed cannot be
    compared before and after a restart, which is the whole oracle of I08/I17.
    """
    before = _counts(engine)
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO saved_snapshot (id, owner_id, target_kind, target_key_at_save,"
            " payload, content_hash, created_at)"
            " VALUES ('01JBAD0000000000000000004', ?, 'work', ?, '{}', 'deadbeef', ?)",
            (OWNER_ID, f"work:{WORK_ID}", NOW),
        )
    assert _counts(engine) == before
    # And the producer side cannot emit that shape at all.
    assert snapshot.compute_content_hash({"a": 1}).startswith("sha256:")
    assert len(snapshot.compute_content_hash({"a": 1})) == len("sha256:") + 64
