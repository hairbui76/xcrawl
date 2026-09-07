"""E1/E2 tests for ``TXN-identity-merge``: the move-set, the audit trail, I03 and I17.

The oracles are the accepted fixtures, used as data and not paraphrased: ``given.rows`` is
loaded into an empty database created by the real Alembic migrations, ``events`` are executed
through the real service layer (never by writing the expected rows directly), and then
``expected.rows``, ``expected.counts``, ``expected.hash_oracles`` and -- the part that actually
catches defects -- ``forbidden_effects`` are asserted.

Fixtures used here:

``identity/a-merge-doi-arxiv``            merge on DOI<->arXiv evidence; I03, I17
``identity/b-post-only-missing-ids``      no identifier -> a post target, no work invented
``identity/c-identity-conflict``          contradictory DOIs -> quarantine, zero merges
``identity/g-arxiv-version-v1-v2``        v1 then v2 -> one work, two versions
``identity/h-five-posts-thread-one-target`` six spellings of one arXiv id -> one work
``reporting/i-identity-merge-single-first-announced`` first-announcement after a merge

Hashes are computed, never hard-coded: the fixtures assert RELATIONS between hashes
(``content_hash`` after a merge equals the one before), so this file materialises a payload for
each symbolic hash and recomputes ``sha256(JCS(payload))`` -- which makes "the snapshot did not
change" a measurement rather than a claim.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.identity import service
from server.app.identity.normalization import IdScheme
from server.app.identity.repository import IdentityRepository
from server.app.identity.service import ALLOWED_CALLERS, Identifier, IdentityError

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "acceptance" / "fixtures"

#: This card's own revision. The test upgrades to it by name rather than to ``head``: three
#: Phase 1 cards added a revision on top of ``0001`` in parallel, so ``head`` is ambiguous until
#: the Coordinator merges the branches (see the handoff's change requests).
MIGRATION_REVISION = "0003_tc_canonical_identity_merge"

MOD_INGEST = "MOD-ingest-service"
MOD_IDENTITY = "MOD-identity-service"


# --- harness ----------------------------------------------------------------------------------


def load_fixture(ref: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURE_ROOT / f"{ref}.json").read_text(encoding="utf-8"))
    return data


def _jcs(payload: Any) -> bytes:
    """Canonical JSON, close enough to RFC 8785 for the ASCII payloads the fixtures use."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_of(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(_jcs(payload)).hexdigest()


#: Columns a fixture may leave out because they are irrelevant to what it proves. Filling them
#: here (rather than making them nullable in the migration) keeps the schema faithful to
#: entities.yaml while letting each fixture state only the columns it is about.
DEFAULTS: dict[str, dict[str, Any]] = {
    "owner": {
        "singleton_guard": 1,
        "display_name": "owner",
        "timezone_iana": "Asia/Ho_Chi_Minh",
        "created_at": "2026-09-01T00:00:00.000Z",
    },
    "work": {
        "canonical_doi": None,
        "canonical_arxiv_id": None,
        "title": None,
        "paper_url": None,
        "code_url": None,
        "current_work_version_id": None,
        "metadata_state": "none",
        "identity_state": "active",
        "merged_into_work_id": None,
        "first_discovered_at": "2026-09-01T00:00:00.000Z",
        "ingest_sequence": 1,
        "content_state": "present",
        "created_at": "2026-09-01T00:00:00.000Z",
    },
    "work_version": {
        "version_scheme": "arxiv",
        "announced_at": None,
        "observed_at": "2026-09-01T00:00:00.000Z",
        "abstract_text": None,
        "content_fingerprint": "sha256:" + "0" * 64,
        "is_current": 1,
    },
    "post": {
        "author_handle": "someone",
        "author_display_name": None,
        "author_x_user_id": None,
        "url": "https://x.com/someone/status/1",
        "text": "",
        "lang": None,
        "published_at": None,
        "discovered_at": "2026-09-01T00:00:00.000Z",
        "ingest_sequence": 1,
        "collected_at_client": None,
        "discovered_by_run_id": "01JRUN00000000000000000000",
        "ingest_receipt_id": "01JRECE1PT000000000000000",
        "thread_root_x_post_id": None,
        "is_author_thread_member": 0,
        "media_refs": "[]",
        "referenced_links": "[]",
        "identity_resolution": "resolved_linked",
        "source_snapshot_hash": "sha256:" + "0" * 64,
        "content_state": "present",
        "source_deleted_observed_at": None,
    },
    "post_work": {
        "link_evidence": "explicit_url_in_post",
        "linked_at": "2026-09-01T00:00:00.000Z",
        "moved_by_merge_id": None,
    },
    "identity_alias": {
        "id_value_raw": "",
        "evidence_source": "post_link",
        "evidence_ref": "{}",
        "confidence": "asserted_by_source",
        "created_at": "2026-09-01T00:00:00.000Z",
        "superseded_by_merge_id": None,
    },
    "saved_snapshot": {"analysis_id_at_save": None, "created_at": "2026-09-01T00:00:00.000Z"},
    "saved_item": {
        "state": "active",
        "saved_at": "2026-09-01T00:00:00.000Z",
        "unsaved_at": None,
        "save_channel": "app",
        "source_report_item_id": None,
        "idempotency_key": None,
        "moved_by_merge_id": None,
    },
    "analysis": {
        "analysis_generation_id": "01JAGEN0000000000000000000",
        "task_type": "summary",
        "source_fingerprint": "sha256:" + "0" * 64,
        "prompt_version": "1.0.0",
        "schema_version": "0.1.0",
        "generation_number": 1,
        "status": "valid",
        "evidence_level": "abstract",
        "provider_name": "test-provider",
        "model_name": "test-model",
        "usage_tokens_in": None,
        "usage_tokens_out": None,
        "analyzed_at": "2026-09-01T00:00:00.000Z",
        "accepted_from_attempt_id": "01JATT00000000000000000000",
        "moved_by_merge_id": None,
    },
    "work_label": {"created_at": "2026-09-01T00:00:00.000Z", "vector": None},
    "first_announced_ledger": {"merge_audit_id": None, "superseded_by_merge_id": None},
}

#: The order rows are inserted in, so foreign keys resolve without deferring anything.
INSERT_ORDER = (
    "work",
    "work_version",
    "post",
    "post_work",
    "identity_alias",
    "saved_snapshot",
    "analysis",
    "saved_item",
    "work_label",
    "identity_conflict",
    "first_announced_ledger",
    "identity_merge_audit",
)


def _table_columns(connection: Any, table: str) -> list[str]:
    return [str(row[1]) for row in connection.exec_driver_sql(f"PRAGMA table_info({table})")]


def _table_exists(connection: Any, table: str) -> bool:
    return (
        connection.exec_driver_sql(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
        ).first()
        is not None
    )


def _prepare_row(table: str, row: dict[str, Any], owner_id: str) -> dict[str, Any]:
    """Turn one fixture row into one database row.

    Three fixture conventions are honoured here and nowhere else: keys starting with ``_`` are
    annotations (ruling R4-01) and are dropped, ``_target`` carries the tagged union, and a
    ``{"symbolic": ...}`` hash is materialised into a payload plus its real sha256.
    """
    prepared: dict[str, Any] = dict(DEFAULTS.get(table, {}))
    prepared["owner_id"] = owner_id
    for key, value in row.items():
        if key == "_target":
            target = value
            prepared["target_kind"] = target["kind"]
            if target["kind"] == "work":
                prepared["target_work_id"] = target["work_id"]
                prepared["target_post_id"] = None
            else:
                prepared["target_post_id"] = target["post_id"]
                prepared["target_work_id"] = None
            continue
        if key.startswith("_"):
            continue
        if isinstance(value, dict) and "symbolic" in value:
            payload = {"symbolic": value["symbolic"]}
            prepared["payload"] = json.dumps(payload, sort_keys=True)
            prepared[key] = sha256_of(payload)
            continue
        if isinstance(value, dict | list):
            prepared[key] = json.dumps(value, sort_keys=True)
            continue
        if isinstance(value, bool):
            prepared[key] = int(value)
            continue
        prepared[key] = value
    return prepared


def load_given(engine: Engine, fixture: dict[str, Any]) -> None:
    """Load ``given.rows`` into an empty database, in dependency order.

    Tables a fixture mentions that this card's migrations do not create (``report``,
    ``report_item``, ``coverage_window``, ``analysis_generation``) are skipped: they belong to
    cards that have not run. Every skip is visible in the assertions that depend on them, which
    are marked ``xfail`` rather than quietly dropped.
    """
    owner_id = str(fixture["owner_id"])
    rows = fixture.get("given", {}).get("rows", {})
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at) "
                "VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z')"
            ),
            {"id": owner_id},
        )
        # `work.current_work_version_id` points forward at `work_version`, which points back at
        # `work`. The rows are inserted with the pointer NULL and it is set afterwards, which is
        # what the application does too: a version exists before it becomes the current one.
        deferred: list[tuple[str, str]] = []
        sequences = {"work": 0, "post": 0}
        for table in INSERT_ORDER:
            if table not in rows or not _table_exists(connection, table):
                continue
            columns = set(_table_columns(connection, table))
            for row in rows[table]:
                prepared = {
                    key: value
                    for key, value in _prepare_row(table, row, owner_id).items()
                    if key in columns
                }
                if table in sequences and "ingest_sequence" not in row:
                    # UNIQUE(owner_id, ingest_sequence); a fixture that does not care about the
                    # order still needs distinct values.
                    sequences[table] += 1
                    prepared["ingest_sequence"] = sequences[table]
                if table == "work" and prepared.get("current_work_version_id") is not None:
                    deferred.append((str(prepared["id"]), str(prepared["current_work_version_id"])))
                    prepared["current_work_version_id"] = None
                names = ", ".join(sorted(prepared))
                binds = ", ".join(f":{name}" for name in sorted(prepared))
                connection.execute(
                    text(f"INSERT INTO {table} ({names}) VALUES ({binds})"),  # noqa: S608
                    prepared,
                )
        for work_id, version_id in deferred:
            connection.execute(
                text("UPDATE work SET current_work_version_id = :version WHERE id = :work"),
                {"version": version_id, "work": work_id},
            )


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    """A database created by the real migrations -- not by ``CREATE TABLE`` in a test."""
    database = tmp_path / "research-radar.db"
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(database)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, MIGRATION_REVISION)
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous
    engine = create_sqlite_engine(database)
    yield engine
    engine.dispose()


def rows_of(
    engine: Engine, table: str, columns: str = "*", order: str = "id"
) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        if not _table_exists(connection, table):
            return []
        result = (
            connection.execute(text(f"SELECT {columns} FROM {table} ORDER BY {order}"))  # noqa: S608
            .mappings()
            .all()
        )
    return [dict(row) for row in result]


def row_by_id(engine: Engine, table: str, row_id: str) -> dict[str, Any]:
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(f"SELECT * FROM {table} WHERE id = :id"),  # noqa: S608
                {"id": row_id},
            )
            .mappings()
            .first()
        )
    assert row is not None, f"{table}:{row_id} is missing"
    return dict(row)


def count_of(engine: Engine, table: str, where: str = "1 = 1") -> int:
    with engine.connect() as connection:
        if not _table_exists(connection, table):
            return 0
        return int(
            connection.execute(
                text(f"SELECT COUNT(*) FROM {table} WHERE {where}")  # noqa: S608
            ).scalar_one()
        )


def snapshot_digest(engine: Engine) -> list[tuple[str, str, str]]:
    """``(id, target_key_at_save, content_hash)`` for every snapshot -- the I17 measurement."""
    return [
        (str(row["id"]), str(row["target_key_at_save"]), str(row["content_hash"]))
        for row in rows_of(engine, "saved_snapshot")
    ]


# --- fixture (a): merge on DOI<->arXiv evidence -------------------------------------------------

FIXTURE_A = load_fixture("identity/a-merge-doi-arxiv")
W1 = "01JW0RKA100000000000000000"  # arXiv only, discovered 08:00
W2 = "01JW0RKA200000000000000000"  # DOI only, discovered 09:00 -> the winner
OWNER_A = str(FIXTURE_A["owner_id"])
EVIDENCE_A = {
    "id_scheme": "openalex",
    "id_value_normalized": "W2741809807",
    "evidence_source": "openalex_api",
    "confidence": "confirmed_by_two_sources",
}


def merge_fixture_a(engine: Engine) -> service.MergeResult:
    return service.merge_works(
        engine,
        owner_id=OWNER_A,
        work_ids=(W1, W2),
        linking_evidence=EVIDENCE_A,
        caller_module=MOD_INGEST,
        now="2026-09-05T10:31:00.000Z",
    )


def test_fixture_a_winner_is_the_only_candidate_with_a_doi(engine: Engine) -> None:
    """identity.md §6.2 rule 2. The fixture pins both the winner and the rule name."""
    load_given(engine, FIXTURE_A)
    result = merge_fixture_a(engine)
    assert result.winner_work_id == FIXTURE_A["expected"]["winner_work_id"] == W2
    assert result.winner_selection_rule == FIXTURE_A["expected"]["winner_selection_rule"]


def test_fixture_a_expected_rows(engine: Engine) -> None:
    """Every row the fixture states after the merge, column by column."""
    load_given(engine, FIXTURE_A)
    result = merge_fixture_a(engine)

    winner = row_by_id(engine, "work", W2)
    assert winner["identity_state"] == "active"
    assert winner["canonical_doi"] == "10.1000/xyz"
    assert winner["canonical_arxiv_id"] == "2501.01234"
    # MIN of the two discovery times, not the winner's own: the pair was first seen at 08:00.
    assert winner["first_discovered_at"] == "2026-09-05T08:00:00.000Z"
    assert winner["metadata_state"] == "complete"
    assert winner["current_work_version_id"] == "01JWVERA100000000000000000"

    loser = row_by_id(engine, "work", W1)
    assert loser["identity_state"] == "merged"
    assert loser["merged_into_work_id"] == W2
    # The losing row KEEPS its canonical value as evidence; the partial index excludes it.
    assert loser["canonical_arxiv_id"] == "2501.01234"
    assert loser["canonical_doi"] is None

    moved_alias = row_by_id(engine, "identity_alias", "01JA11ASA10000000000000000")
    assert moved_alias["work_id"] == W2
    assert moved_alias["superseded_by_merge_id"] == result.merge_id
    assert moved_alias["id_value_raw"] == "arXiv:2501.01234v1"

    untouched_alias = row_by_id(engine, "identity_alias", "01JA11ASA20000000000000000")
    assert untouched_alias["work_id"] == W2
    assert untouched_alias["superseded_by_merge_id"] is None

    linking = [row for row in rows_of(engine, "identity_alias") if row["id_scheme"] == "openalex"]
    assert len(linking) == 1, "the identifier that proved the merge becomes an alias of the winner"
    assert linking[0]["work_id"] == W2
    assert linking[0]["id_value_normalized"] == "W2741809807"
    assert linking[0]["evidence_source"] == "openalex_api"
    assert linking[0]["confidence"] == "confirmed_by_two_sources"

    version = row_by_id(engine, "work_version", "01JWVERA100000000000000000")
    assert version["work_id"] == W2
    assert version["version_label"] == "v1"
    assert version["is_current"] == 1

    moved_edge = row_by_id(engine, "post_work", "01JPWA10000000000000000000")
    assert moved_edge["work_id"] == W2
    assert moved_edge["moved_by_merge_id"] == result.merge_id
    other_edge = row_by_id(engine, "post_work", "01JPWA20000000000000000000")
    assert other_edge["work_id"] == W2
    assert other_edge["moved_by_merge_id"] is None

    moved_analysis = row_by_id(engine, "analysis", "01JANA1YA10000000000000000")
    assert moved_analysis["target_work_id"] == W2
    assert moved_analysis["target_key"] == f"work:{W2}"
    assert moved_analysis["status"] == "valid"
    assert moved_analysis["moved_by_merge_id"] == result.merge_id

    other_analysis = row_by_id(engine, "analysis", "01JANA1YA20000000000000000")
    assert other_analysis["status"] == "valid"
    assert other_analysis["moved_by_merge_id"] is None

    saved = row_by_id(engine, "saved_item", "01JSAVEDA10000000000000000")
    assert saved["target_work_id"] == W2
    assert saved["state"] == "active"
    assert saved["moved_by_merge_id"] == result.merge_id
    assert saved["saved_at"] == "2026-09-05T10:00:00.000Z"

    audit = row_by_id(engine, "identity_merge_audit", result.merge_id)
    assert audit["winner_work_id"] == W2
    assert audit["loser_work_id"] == W1
    assert audit["winner_selection_rule"] == "only_candidate_with_canonical_doi"
    assert audit["performed_by"] == "system_automatic_on_evidence"
    assert json.loads(audit["linking_evidence"])["id_value_normalized"] == "W2741809807"
    assert audit["merged_at"] == "2026-09-05T10:31:00.000Z"


def test_fixture_a_moved_and_preserved_counts(engine: Engine) -> None:
    """``moved_counts`` and ``preserved_counts`` are the oracle of I03 and I17."""
    load_given(engine, FIXTURE_A)
    result = merge_fixture_a(engine)
    expected = FIXTURE_A["expected"]["rows"]["identity_merge_audit"][0]
    for key in (
        "identity_alias",
        "post_work",
        "work_version",
        "work_label",
        "analysis",
        "saved_item",
        "report_item_pointer",
    ):
        assert result.moved_counts[key] == expected["moved_counts"][key], key
    assert result.preserved_counts == expected["preserved_counts"]


def test_fixture_a_counts(engine: Engine) -> None:
    """The fixture's ``expected.counts`` block, measured on the database."""
    load_given(engine, FIXTURE_A)
    merge_fixture_a(engine)
    counts = FIXTURE_A["expected"]["counts"]
    assert count_of(engine, "work") == counts["work__total"]
    assert (
        count_of(engine, "work", "identity_state = 'active'")
        == counts["work__identity_state_active"]
    )
    assert (
        count_of(engine, "work", "identity_state = 'merged'")
        == counts["work__identity_state_merged"]
    )
    assert count_of(engine, "identity_alias") == counts["identity_alias__total"]
    assert (
        count_of(
            engine,
            "identity_alias",
            "work_id IN (SELECT id FROM work WHERE identity_state = 'merged')",
        )
        == counts["identity_alias__pointing_to_merged_work"]
    )
    assert count_of(engine, "post") == counts["post"]
    assert count_of(engine, "post_work") == counts["post_work"]
    assert count_of(engine, "analysis", "status = 'valid'") == counts["analysis__status_valid"]
    assert count_of(engine, "saved_item", "state = 'active'") == counts["saved_item__state_active"]
    assert count_of(engine, "saved_snapshot") == counts["saved_snapshot"]
    assert count_of(engine, "identity_merge_audit") == counts["identity_merge_audit"]
    assert (
        count_of(engine, "identity_conflict", "state = 'open'")
        == counts["identity_conflict__state_open"]
    )


def test_fixture_a_hash_oracles_snapshot_unchanged(engine: Engine) -> None:
    """I17: the set of ``(id, target_key_at_save, content_hash)`` is identical across the merge.

    ``target_key_at_save`` still names the LOSING work afterwards. That is not staleness: a
    snapshot is historical evidence of what was read, not a live pointer.
    """
    load_given(engine, FIXTURE_A)
    before = snapshot_digest(engine)
    payload_before = rows_of(engine, "saved_snapshot")[0]["payload"]
    merge_fixture_a(engine)
    after = snapshot_digest(engine)

    assert after == before
    assert before[0][1] == f"work:{W1}"
    snapshot = rows_of(engine, "saved_snapshot")[0]
    assert snapshot["payload"] == payload_before
    assert snapshot["content_hash"] == sha256_of(json.loads(snapshot["payload"]))


def test_fixture_a_analysis_payload_hash_unchanged(engine: Engine) -> None:
    """``analysis[AN1].payload_hash`` after the merge equals the one before (hash oracle 3)."""
    load_given(engine, FIXTURE_A)
    before = row_by_id(engine, "analysis", "01JANA1YA10000000000000000")["payload_hash"]
    merge_fixture_a(engine)
    after = row_by_id(engine, "analysis", "01JANA1YA10000000000000000")
    assert after["payload_hash"] == before
    assert after["payload_hash"] == sha256_of(json.loads(after["payload"]))


def test_fixture_a_forbidden_effects(engine: Engine) -> None:
    """Each line of the fixture's ``forbidden_effects``, asserted as an absence."""
    load_given(engine, FIXTURE_A)
    posts_before = count_of(engine, "post")
    merge_fixture_a(engine)

    # "DELETE work W1 or any identity_alias" / "create a third work"
    assert count_of(engine, "work") == 2
    assert row_by_id(engine, "work", W1) is not None
    assert count_of(engine, "identity_alias", "id = '01JA11ASA10000000000000000'") == 1
    assert count_of(engine, "post") == posts_before

    # "leave an identity_alias pointing at a work whose identity_state is 'merged'"
    assert (
        count_of(
            engine,
            "identity_alias",
            "work_id IN (SELECT id FROM work WHERE identity_state = 'merged')",
        )
        == 0
    )
    # "point merged_into_work_id at a work that is itself merged" (depth is exactly 1)
    assert (
        count_of(
            engine,
            "work",
            "merged_into_work_id IN (SELECT id FROM work WHERE identity_state = 'merged')",
        )
        == 0
    )
    # "merge when linking_evidence is empty or comes from AI inference"
    audit = rows_of(engine, "identity_merge_audit")[0]
    assert json.loads(audit["linking_evidence"])
    assert audit["performed_by"] in {"system_automatic_on_evidence", "owner_manual"}


def test_merge_without_evidence_is_refused(engine: Engine) -> None:
    """No evidence, no merge (identity.md §6.1). Nothing is written."""
    load_given(engine, FIXTURE_A)
    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_A,
            work_ids=(W1, W2),
            linking_evidence={},
            caller_module=MOD_INGEST,
        )
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert count_of(engine, "identity_merge_audit") == 0
    assert count_of(engine, "work", "identity_state = 'active'") == 2


def test_merge_replay_is_idempotent_and_conflicting_evidence_is_refused(engine: Engine) -> None:
    """ports.yaml idempotency: same pair + same evidence -> the committed result; different
    evidence -> ``CONFLICT`` and no second merge."""
    load_given(engine, FIXTURE_A)
    first = merge_fixture_a(engine)
    replay = merge_fixture_a(engine)
    assert replay.merge_id == first.merge_id
    assert replay.already_merged is True
    assert count_of(engine, "identity_merge_audit") == 1

    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_A,
            work_ids=(W1, W2),
            linking_evidence={**EVIDENCE_A, "id_value_normalized": "W9999999999"},
            caller_module=MOD_INGEST,
        )
    assert raised.value.code is ErrorCode.CONFLICT
    assert count_of(engine, "identity_merge_audit") == 1


def test_merge_of_a_missing_work_is_not_found(engine: Engine) -> None:
    load_given(engine, FIXTURE_A)
    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_A,
            work_ids=(W1, "01JW0RKZZ00000000000000000"),
            linking_evidence=EVIDENCE_A,
            caller_module=MOD_INGEST,
        )
    assert raised.value.code is ErrorCode.NOT_FOUND
    assert count_of(engine, "identity_merge_audit") == 0


def test_crash_between_the_moves_and_the_audit_rolls_everything_back(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """E2 fault injection at the failure point entities.yaml names ("crash mid-transaction").

    The audit row is written INSIDE the transaction, so a failure there must leave two active
    works and no half-merged state -- "rollback: both works still active, no audit".
    """
    load_given(engine, FIXTURE_A)

    def explode(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("simulated storage failure at the commit point")

    monkeypatch.setattr(IdentityRepository, "insert_merge_audit", explode)
    with pytest.raises(RuntimeError):
        merge_fixture_a(engine)

    assert count_of(engine, "identity_merge_audit") == 0
    assert count_of(engine, "work", "identity_state = 'active'") == 2
    assert count_of(engine, "work", "identity_state = 'merged'") == 0
    assert row_by_id(engine, "identity_alias", "01JA11ASA10000000000000000")["work_id"] == W1
    assert row_by_id(engine, "post_work", "01JPWA10000000000000000000")["work_id"] == W1
    assert snapshot_digest(engine)[0][1] == f"work:{W1}"


def test_merge_is_deterministic_across_runs(engine: Engine, tmp_path: Path) -> None:
    """Same data, same winner -- the reason §6.2 is a total order and not a preference."""
    load_given(engine, FIXTURE_A)
    first = merge_fixture_a(engine)

    second_db = tmp_path / "again.db"
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(second_db)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, MIGRATION_REVISION)
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous
    other = create_sqlite_engine(second_db)
    try:
        load_given(other, FIXTURE_A)
        # The two works are offered in the OPPOSITE order this time.
        second = service.merge_works(
            other,
            owner_id=OWNER_A,
            work_ids=(W2, W1),
            linking_evidence=EVIDENCE_A,
            caller_module=MOD_INGEST,
            now="2026-09-05T10:31:00.000Z",
        )
    finally:
        other.dispose()
    assert (second.winner_work_id, second.loser_work_id) == (
        first.winner_work_id,
        first.loser_work_id,
    )
    assert second.winner_selection_rule == first.winner_selection_rule


# --- fixture (c): contradictory canonical values -> quarantine ----------------------------------

FIXTURE_C = load_fixture("identity/c-identity-conflict")
W1C = "01JW0RKC100000000000000000"
W2C = "01JW0RKC200000000000000000"
OWNER_C = str(FIXTURE_C["owner_id"])


def test_fixture_c_conflicting_dois_quarantine_instead_of_merging(engine: Engine) -> None:
    """B15: contradiction is quarantined with both sources kept. Zero merges, zero guesses."""
    load_given(engine, FIXTURE_C)
    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_C,
            work_ids=(W1C, W2C),
            linking_evidence={
                "id_scheme": "openalex",
                "id_value_normalized": "W3000000001",
                "evidence_source": "openalex_api",
            },
            caller_module=MOD_INGEST,
            now="2026-09-05T12:00:01.000Z",
        )
    assert raised.value.code is ErrorCode.IDENTITY_CONFLICT

    counts = FIXTURE_C["expected"]["counts"]
    assert count_of(engine, "identity_merge_audit") == counts["identity_merge_audit"] == 0
    assert count_of(engine, "identity_conflict", "state = 'open'") == 1
    assert (
        count_of(engine, "work", "identity_state = 'quarantined'")
        == counts["work__identity_state_quarantined"]
    )
    assert count_of(engine, "work", "identity_state = 'active'") == 0
    assert count_of(engine, "identity_alias") == counts["identity_alias__total"] == 3
    # The openalex alias is NOT created: it would point at two works and break I03. The evidence
    # survives inside `involved_identifiers` instead of being thrown away.
    assert count_of(engine, "identity_alias", "id_scheme = 'openalex'") == 0

    conflict = rows_of(engine, "identity_conflict")[0]
    assert conflict["conflict_type"] == "canonical_value_mismatch"
    assert conflict["state"] == "open"
    assert conflict["resolution_note"] is None
    assert conflict["resolved_at"] is None
    involved = json.loads(conflict["involved_identifiers"])
    values = {item["id_value_normalized"] for item in involved}
    assert {"10.1000/aaa", "10.1000/bbb", "2502.02222", "W3000000001"} <= values
    assert sorted(json.loads(conflict["involved_work_ids"])) == sorted([W1C, W2C])

    # Existing aliases are untouched: nothing is deleted, nothing is repointed.
    assert row_by_id(engine, "identity_alias", "01JA11ASC10000000000000000")["work_id"] == W1C
    assert row_by_id(engine, "identity_alias", "01JA11ASC20000000000000000")["work_id"] == W2C
    assert row_by_id(engine, "identity_alias", "01JA11ASC30000000000000000")["work_id"] == W2C


def test_fixture_c_quarantine_is_idempotent(engine: Engine) -> None:
    """The same contradiction seen twice does not create a second quarantine row."""
    load_given(engine, FIXTURE_C)
    for _ in range(2):
        with pytest.raises(IdentityError):
            service.merge_works(
                engine,
                owner_id=OWNER_C,
                work_ids=(W1C, W2C),
                linking_evidence={
                    "id_scheme": "openalex",
                    "id_value_normalized": "W3000000001",
                    "evidence_source": "openalex_api",
                },
                caller_module=MOD_INGEST,
                now="2026-09-05T12:00:01.000Z",
            )
    assert count_of(engine, "identity_conflict") == 1


def test_fixture_c_conflict_does_not_expire_into_a_merge(engine: Engine) -> None:
    """identity.md §5.5: there is no timeout that resolves a conflict. Only the owner does."""
    load_given(engine, FIXTURE_C)
    with pytest.raises(IdentityError):
        service.merge_works(
            engine,
            owner_id=OWNER_C,
            work_ids=(W1C, W2C),
            linking_evidence={
                "id_scheme": "openalex",
                "id_value_normalized": "W3000000001",
                "evidence_source": "openalex_api",
            },
            caller_module=MOD_INGEST,
        )
    conflict_id = rows_of(engine, "identity_conflict")[0]["id"]

    # A quarantined work is not `active`, so any further automatic merge attempt fails CAS.
    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_C,
            work_ids=(W1C, W2C),
            linking_evidence={
                "id_scheme": "openalex",
                "id_value_normalized": "W3000000002",
                "evidence_source": "openalex_api",
            },
            caller_module=MOD_INGEST,
        )
    assert raised.value.code in {ErrorCode.IDENTITY_CONFLICT, ErrorCode.CONFLICT}
    assert count_of(engine, "identity_merge_audit") == 0

    # The owner keeps them separate: both works return to `active`, both DOIs survive.
    resolution = service.resolve_conflict(
        engine,
        owner_id=OWNER_C,
        conflict_id=str(conflict_id),
        decision="keep_separate",
        resolution_note="hai công trình khác nhau",
        caller_module="MOD-web-ui",
    )
    assert resolution.state == "resolved_distinct"
    assert count_of(engine, "work", "identity_state = 'active'") == 2
    assert row_by_id(engine, "work", W1C)["canonical_doi"] == "10.1000/aaa"
    assert row_by_id(engine, "work", W2C)["canonical_doi"] == "10.1000/bbb"
    assert count_of(engine, "identity_merge_audit") == 0


def test_owner_resolution_to_merge_is_the_only_merge_path_out_of_a_conflict(
    engine: Engine,
) -> None:
    """``identity.resolve_conflict(decision='merge')`` runs the same transaction, and records
    ``performed_by = 'owner_manual'`` so the audit trail says who decided."""
    load_given(engine, FIXTURE_A)
    conflict = service.quarantine_conflict(
        engine,
        owner_id=OWNER_A,
        conflict_type="alias_points_to_two_works",
        involved_work_ids=[W1, W2],
        involved_identifiers=[{"id_scheme": "openalex", "id_value_normalized": "W2741809807"}],
        caller_module=MOD_INGEST,
    )
    assert count_of(engine, "work", "identity_state = 'quarantined'") == 2

    resolution = service.resolve_conflict(
        engine,
        owner_id=OWNER_A,
        conflict_id=conflict.id,
        decision="merge",
        linking_evidence=EVIDENCE_A,
        winner_work_id=W1,
        resolution_note="owner xác nhận cùng một công trình",
        caller_module="MOD-web-ui",
    )
    assert resolution.state == "resolved_merged"
    assert resolution.merge is not None
    assert resolution.merge.winner_work_id == W1
    assert resolution.merge.winner_selection_rule == "owner_choice"

    audit = rows_of(engine, "identity_merge_audit")[0]
    assert audit["performed_by"] == "owner_manual"
    closed = row_by_id(engine, "identity_conflict", conflict.id)
    assert closed["state"] == "resolved_merged"
    assert closed["resolution_merge_id"] == resolution.merge.merge_id
    assert closed["resolved_at"] is not None


def test_resolving_an_already_resolved_conflict_differently_is_an_idempotency_conflict(
    engine: Engine,
) -> None:
    load_given(engine, FIXTURE_C)
    conflict = service.quarantine_conflict(
        engine,
        owner_id=OWNER_C,
        conflict_type="canonical_value_mismatch",
        involved_work_ids=[W1C, W2C],
        involved_identifiers=[{"id_scheme": "doi", "id_value_normalized": "10.1000/aaa"}],
        caller_module=MOD_INGEST,
    )
    service.resolve_conflict(
        engine,
        owner_id=OWNER_C,
        conflict_id=conflict.id,
        decision="keep_separate",
        caller_module="MOD-web-ui",
    )
    again = service.resolve_conflict(
        engine,
        owner_id=OWNER_C,
        conflict_id=conflict.id,
        decision="keep_separate",
        caller_module="MOD-web-ui",
    )
    assert again.state == "resolved_distinct"

    with pytest.raises(IdentityError) as raised:
        service.resolve_conflict(
            engine,
            owner_id=OWNER_C,
            conflict_id=conflict.id,
            decision="merge",
            linking_evidence={
                "id_scheme": "openalex",
                "id_value_normalized": "W3000000001",
                "evidence_source": "openalex_api",
            },
            caller_module="MOD-web-ui",
        )
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT


# --- fixture (b): no identifier -> a post target ------------------------------------------------

FIXTURE_B = load_fixture("identity/b-post-only-missing-ids")
OWNER_B = str(FIXTURE_B["owner_id"])
POST_B = "01JP0STB100000000000000000"


def test_fixture_b_post_only_target_creates_no_work(engine: Engine) -> None:
    """REQ-D33: a photo of a paper is not an identifier. No work, no guess, no OCR."""
    load_given(engine, FIXTURE_B)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO post (id, owner_id, x_post_id, author_handle, url, text, "
                "                  discovered_at, ingest_sequence, collected_at_client, "
                "                  discovered_by_run_id, ingest_receipt_id, "
                "                  is_author_thread_member, media_refs, referenced_links, "
                "                  identity_resolution, source_snapshot_hash, content_state) "
                "VALUES (:id, :owner_id, '1900000000000000010', 'someone', "
                "        'https://x.com/someone/status/1900000000000000010', 'ảnh chụp', "
                "        '2026-09-05T11:00:01.000Z', 200, '2026-09-05T10:59:58.000Z', "
                "        '01JRUN00000000000000000000', '01JRECE1PTB100000000000000', 0, "
                "        '[]', '[]', 'resolved_post_only', :hash, 'present')"
            ),
            {"id": POST_B, "owner_id": OWNER_B, "hash": "sha256:" + "0" * 64},
        )

    resolution = service.resolve_target(
        engine,
        owner_id=OWNER_B,
        identifiers=[
            # A caption with no identifier in it: normalisation REJECTs, the set becomes empty.
            Identifier(scheme=IdScheme.DOI, raw="Bài này thú vị (ảnh chụp trang đầu)."),
        ],
        post_id=POST_B,
        caller_module=MOD_INGEST,
    )
    expected_target = FIXTURE_B["expected"]["target_usage"]["savable_target"]
    assert resolution.target["kind"] == "post"
    assert resolution.target["post_id"] == expected_target["post_id"]
    assert resolution.target["target_key"] == expected_target["target_key"]
    assert resolution.target["identity_resolution"] == "resolved_post_only"
    assert resolution.work_id is None

    counts = FIXTURE_B["expected"]["counts"]
    assert count_of(engine, "work") == counts["work"] == 0
    assert count_of(engine, "identity_alias") == counts["identity_alias"] == 0
    assert count_of(engine, "post_work") == counts["post_work"] == 0
    assert count_of(engine, "identity_conflict", "state = 'open'") == 0


def test_an_alias_only_scheme_cannot_create_a_work(engine: Engine) -> None:
    """identity.md §2.3: an OpenAlex id or a landing URL bridges, it never defines a work."""
    load_given(engine, FIXTURE_B)
    with pytest.raises(IdentityError) as raised:
        service.record_alias(
            engine,
            owner_id=OWNER_B,
            identifier=Identifier(
                scheme=IdScheme.OPENALEX, raw="W2741809807", evidence_source="openalex_api"
            ),
            caller_module=MOD_INGEST,
        )
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert count_of(engine, "work") == 0


# --- fixture (g): arXiv v1 -> v2 ----------------------------------------------------------------

FIXTURE_G = load_fixture("identity/g-arxiv-version-v1-v2")
OWNER_G = str(FIXTURE_G["owner_id"])
WG = "01JW0RKG100000000000000000"


def test_fixture_g_v2_resolves_to_the_same_work(engine: Engine) -> None:
    """A new version is not a new work and not a merge: one work, one alias, two versions."""
    load_given(engine, FIXTURE_G)
    resolution = service.resolve_target(
        engine,
        owner_id=OWNER_G,
        identifiers=[Identifier(scheme=IdScheme.ARXIV, raw="https://arxiv.org/abs/2503.03333v2")],
        caller_module=MOD_INGEST,
    )
    assert resolution.work_id == WG
    assert resolution.target["canonical"]["arxiv_base"] == "2503.03333"

    # Recording the v2 spelling adds NO second alias: the version suffix is not an identifier.
    alias = service.record_alias(
        engine,
        owner_id=OWNER_G,
        identifier=Identifier(scheme=IdScheme.ARXIV, raw="https://arxiv.org/abs/2503.03333v2"),
        caller_module=MOD_INGEST,
    )
    assert alias.created is False
    assert alias.work_id == WG

    counts = FIXTURE_G["expected"]["counts"]
    assert count_of(engine, "work") == counts["work__total"] == 1
    assert (
        count_of(engine, "identity_alias", "id_scheme = 'arxiv'")
        == counts["identity_alias__scheme_arxiv"]
    )
    assert count_of(engine, "identity_merge_audit") == counts["identity_merge_audit"] == 0
    assert count_of(engine, "identity_conflict", "state = 'open'") == 0
    assert row_by_id(engine, "work", WG)["canonical_arxiv_id"] == "2503.03333"
    assert count_of(engine, "identity_alias", "id_value_normalized LIKE '%v2'") == 0


def test_fixture_g_two_versions_one_current(engine: Engine) -> None:
    """``ux_work_version_current``: exactly one version per work may be current."""
    load_given(engine, FIXTURE_G)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE work_version SET is_current = 0 WHERE id = '01JWVERG100000000000000000'")
        )
        connection.execute(
            text(
                "INSERT INTO work_version (id, owner_id, work_id, version_label, version_scheme, "
                "                          observed_at, content_fingerprint, is_current) "
                "VALUES ('01JWVERG200000000000000000', :owner_id, :work_id, 'v2', 'arxiv', "
                "        '2026-09-10T07:05:00.000Z', 'F_2503.03333_v2', 1)"
            ),
            {"owner_id": OWNER_G, "work_id": WG},
        )
    assert count_of(engine, "work_version") == FIXTURE_G["expected"]["counts"]["work_version"] == 2
    assert count_of(engine, "work_version", "is_current = 1") == 1

    detail = service.get_detail(engine, owner_id=OWNER_G, work_id=WG, caller_module="MOD-web-ui")
    assert [version["version_label"] for version in detail.work_versions] == ["v1", "v2"]
    assert detail.target["canonical"] == {"arxiv_base": "2503.03333"}


# --- fixture (h): six spellings, one work -------------------------------------------------------

FIXTURE_H = load_fixture("identity/h-five-posts-thread-one-target")
OWNER_H = str(FIXTURE_H["owner_id"])


def test_fixture_h_every_spelling_lands_on_one_work_and_one_alias(engine: Engine) -> None:
    """REQ-AC07: one work item, with the posts listed under it as sources.

    The fixture's batch carries SIX items (five independent posts plus one post from the
    author's own thread); the card's §8 prose says "5 post". The fixture is the oracle, so six
    it is -- the divergence is raised as a change request in the handoff.
    """
    load_given(engine, FIXTURE_H)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at) "
                "SELECT :id, 1, 'owner', 'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z' "
                " WHERE NOT EXISTS (SELECT 1 FROM owner WHERE id = :id)"
            ),
            {"id": OWNER_H},
        )

    items = FIXTURE_H["batch"]["items"]
    assert len(items) == 6
    work_ids: set[str] = set()
    for index, item in enumerate(items, start=1):
        raw = item["referenced_links"][0]["url"]
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO post (id, owner_id, x_post_id, author_handle, url, text, "
                    "                  discovered_at, ingest_sequence, discovered_by_run_id, "
                    "                  ingest_receipt_id, is_author_thread_member, media_refs, "
                    "                  referenced_links, identity_resolution, "
                    "                  source_snapshot_hash, content_state) "
                    "VALUES (:id, :owner_id, :x_post_id, :handle, :url, :text, "
                    "        '2026-09-06T08:05:01.000Z', :sequence, "
                    "        '01JRUN00000000000000000000', '01JRECE1PTH100000000000000', "
                    "        :thread, '[]', '[]', 'resolved_linked', :hash, 'present')"
                ),
                {
                    "id": f"01JP0STH{index:018d}",
                    "owner_id": OWNER_H,
                    "x_post_id": item["x_post_id"],
                    "handle": item["author"]["handle"],
                    "url": item["url"],
                    "text": item["text"],
                    "sequence": 300 + index,
                    "thread": 1 if "thread_context" in item else 0,
                    "hash": "sha256:" + "0" * 64,
                },
            )
        alias = service.record_alias(
            engine,
            owner_id=OWNER_H,
            identifier=Identifier(scheme=IdScheme.ARXIV, raw=raw),
            caller_module=MOD_INGEST,
        )
        work_ids.add(alias.work_id)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO post_work (id, owner_id, post_id, work_id, link_evidence, "
                    "                       linked_at) "
                    "VALUES (:id, :owner_id, :post_id, :work_id, 'explicit_url_in_post', "
                    "        '2026-09-06T08:05:01.000Z')"
                ),
                {
                    "id": f"01JPWH0000{index:016d}",
                    "owner_id": OWNER_H,
                    "post_id": f"01JP0STH{index:018d}",
                    "work_id": alias.work_id,
                },
            )

    counts = FIXTURE_H["expected"]["counts"]
    assert len(work_ids) == 1, "six spellings resolved to more than one work"
    assert count_of(engine, "work") == counts["work__total"] == 1
    assert count_of(engine, "identity_alias") == counts["identity_alias__total"] == 1
    assert count_of(engine, "post") == counts["post"] == 6
    assert count_of(engine, "post_work") == counts["post_work"] == 6
    assert count_of(engine, "identity_merge_audit") == counts["identity_merge_audit"] == 0
    assert count_of(engine, "identity_conflict", "state = 'open'") == 0

    work_id = next(iter(work_ids))
    assert row_by_id(engine, "work", work_id)["canonical_arxiv_id"] == "2504.04444"
    detail = service.get_detail(
        engine, owner_id=OWNER_H, work_id=work_id, caller_module="MOD-web-ui"
    )
    assert (
        len(detail.source_posts) == FIXTURE_H["expected"]["read_model"]["work_detail_source_posts"]
    )
    alias_row = rows_of(engine, "identity_alias")[0]
    # The raw value is the FIRST spelling observed; the normalised key is shared by all six.
    assert alias_row["id_value_raw"] == items[0]["referenced_links"][0]["url"]
    assert alias_row["id_value_normalized"] == "2504.04444"


# --- fixture (i): first-announcement after a merge ----------------------------------------------

FIXTURE_I = load_fixture("reporting/i-identity-merge-single-first-announced")
OWNER_I = str(FIXTURE_I["owner_id"])
WA_I = "01JWRKA0000000000000000000"  # has the DOI -> winner
WB_I = "01JWRKB0000000000000000000"  # announced first (2026-09-01)


def merge_fixture_i(engine: Engine) -> service.MergeResult:
    return service.merge_works(
        engine,
        owner_id=OWNER_I,
        work_ids=(WA_I, WB_I),
        linking_evidence={
            "id_scheme": "openalex",
            "id_value_normalized": "W4000000001",
            "evidence_source": "openalex_api",
        },
        caller_module=MOD_IDENTITY,
        now="2026-09-03T02:00:01.000Z",
    )


def test_fixture_i_winner_inherits_the_earliest_first_announcement(engine: Engine) -> None:
    """``contracts/reporting/time-and-tags.md`` §8.3, which closes ``CR-PC02-06``.

    Both works were already announced, so the winner takes the EARLIER pair and the losing row
    is kept as evidence with ``superseded_by_merge_id`` set. Taking the later date would tell the
    owner a story they know is false; deleting the losing row would destroy the evidence B15
    exists to protect.
    """
    load_given(engine, FIXTURE_I)
    result = merge_fixture_i(engine)
    expected = FIXTURE_I["expected"]["after_event_2"]["rows"]

    assert result.winner_work_id == WA_I
    assert result.moved_counts["first_announced"] == 2

    winner_row = row_by_id(engine, "first_announced_ledger", "01JFANNA000000000000000000")
    expected_winner = expected["first_announced_ledger"][0]
    assert winner_row["canonical_work_id"] == expected_winner["canonical_work_id"] == WA_I
    assert winner_row["first_report_id"] == expected_winner["first_report_id"]
    assert winner_row["first_announced_at"] == expected_winner["first_announced_at"]
    assert winner_row["merge_audit_id"] == result.merge_id
    assert winner_row["superseded_by_merge_id"] is None

    loser_row = row_by_id(engine, "first_announced_ledger", "01JFANNB000000000000000000")
    assert loser_row["canonical_work_id"] == WB_I, "historical evidence keeps pointing at B"
    assert loser_row["superseded_by_merge_id"] == result.merge_id

    # I07 at schema level: exactly one row in force for the surviving work.
    assert (
        count_of(
            engine,
            "first_announced_ledger",
            f"superseded_by_merge_id IS NULL AND canonical_work_id = '{WA_I}'",
        )
        == 1
    )
    assert count_of(engine, "first_announced_ledger") == 2


def test_first_announced_only_on_the_loser_moves_to_the_winner(engine: Engine) -> None:
    """§8.3 row 3: the winner inherits the losing row itself, dates unchanged, count 1."""
    load_given(engine, FIXTURE_I)
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM first_announced_ledger WHERE id = '01JFANNA000000000000000000'")
        )
    result = merge_fixture_i(engine)
    assert result.moved_counts["first_announced"] == 1
    row = row_by_id(engine, "first_announced_ledger", "01JFANNB000000000000000000")
    assert row["canonical_work_id"] == WA_I
    assert row["first_announced_at"] == "2026-09-01T13:00:00.000Z"
    assert row["merge_audit_id"] == result.merge_id


def test_first_announced_absent_on_both_sides_is_zero_not_null(engine: Engine) -> None:
    """§8.3 row 1 and its explicit note: ``0`` is a valid outcome and differs from ``null``,
    which PC02 used only while the policy was open."""
    load_given(engine, FIXTURE_A)
    result = merge_fixture_a(engine)
    assert result.moved_counts["first_announced"] == 0


@pytest.mark.xfail(
    reason=(
        "Fixture (a) predates contracts/reporting/time-and-tags.md §8.3 and still expects the "
        "placeholder null for moved_counts.first_announced; §8.3 replaced it with a number. "
        "CR-TC-IDENTITY-02 in the handoff."
    ),
    strict=True,
)
def test_fixture_a_first_announced_literal_null(engine: Engine) -> None:
    load_given(engine, FIXTURE_A)
    result = merge_fixture_a(engine)
    expected = FIXTURE_A["expected"]["rows"]["identity_merge_audit"][0]["moved_counts"]
    assert result.moved_counts["first_announced"] == expected["first_announced"]


@pytest.mark.xfail(
    reason=(
        "preserved_counts.published_report_item needs the `report` and `report_item` tables, "
        "owned by the reporting card (not in Phase 1 M1). CR-TC-IDENTITY-03."
    ),
    strict=True,
)
def test_fixture_i_preserved_published_report_items(engine: Engine) -> None:
    load_given(engine, FIXTURE_I)
    result = merge_fixture_i(engine)
    expected = FIXTURE_I["expected"]["after_event_2"]["rows"]["identity_merge_audit"][0]
    assert (
        result.preserved_counts["published_report_item"]
        == expected["preserved_counts"]["published_report_item"]
    )


# --- default deny (SC49) and the HTTP surface ---------------------------------------------------


def test_allowed_callers_match_contracts_modules_yaml() -> None:
    """The in-code edge table is checked against ``contracts/modules.yaml``, not trusted.

    A module calling itself in-process crosses no boundary, so ``MOD-identity-service`` may be
    present here without a matching row; every OTHER caller must come from ``allowed_edges``.
    """
    modules = yaml.safe_load((REPO_ROOT / "contracts" / "modules.yaml").read_text(encoding="utf-8"))
    contract: dict[str, set[str]] = {}
    for edge in modules["allowed_edges"]:
        if edge.get("callee") == MOD_IDENTITY:
            contract.setdefault(str(edge["operation"]), set()).add(str(edge["caller"]))

    assert set(contract) == {operation.value for operation in ALLOWED_CALLERS}
    for operation, callers in ALLOWED_CALLERS.items():
        declared = contract[operation.value]
        assert declared <= callers, operation.value
        assert callers - declared <= {MOD_IDENTITY}, operation.value


@pytest.mark.parametrize(
    ("operation", "call"),
    [
        (OperationId.IDENTITY_MERGE_WORKS, "merge_works"),
        (OperationId.IDENTITY_RESOLVE_TARGET, "resolve_target"),
        (OperationId.IDENTITY_RECORD_ALIAS, "record_alias"),
        (OperationId.IDENTITY_QUARANTINE_CONFLICT, "quarantine_conflict"),
    ],
)
def test_a_caller_outside_the_registry_is_forbidden_edge_not_unauthorized(
    engine: Engine, operation: OperationId, call: str
) -> None:
    """Ruling R5-01: a call over an edge the registry does not declare is ``FORBIDDEN_EDGE``.

    The distinction is the point: ``UNAUTHORIZED`` would say "prove who you are", which is the
    wrong instruction when the edge itself does not exist.
    """
    load_given(engine, FIXTURE_A)
    kwargs: dict[str, Any] = {"owner_id": OWNER_A, "caller_module": "MOD-analysis-worker"}
    if call == "merge_works":
        kwargs |= {"work_ids": (W1, W2), "linking_evidence": EVIDENCE_A}
    elif call == "record_alias":
        kwargs |= {"identifier": Identifier(scheme=IdScheme.DOI, raw="10.1000/xyz")}
    elif call == "quarantine_conflict":
        kwargs |= {
            "conflict_type": "canonical_value_mismatch",
            "involved_work_ids": [W1, W2],
            "involved_identifiers": [],
        }
    with pytest.raises(IdentityError) as raised:
        getattr(service, call)(engine, **kwargs)
    assert raised.value.code is ErrorCode.FORBIDDEN_EDGE
    assert raised.value.http_status == 403
    assert raised.value.envelope("01JCORREL00000000000000000")["retry_class"] == "none"


def test_error_envelope_shape_matches_the_contract(engine: Engine) -> None:
    """errors.yaml ``error_envelope``: the six mandatory fields, and no leaked internals."""
    load_given(engine, FIXTURE_A)
    with pytest.raises(IdentityError) as raised:
        service.merge_works(
            engine,
            owner_id=OWNER_A,
            work_ids=(W1, "01JW0RKZZ00000000000000000"),
            linking_evidence=EVIDENCE_A,
            caller_module=MOD_INGEST,
        )
    envelope = raised.value.envelope("01JCORREL00000000000000000")
    assert set(envelope) == {
        "code",
        "scope",
        "retry_class",
        "message_safe",
        "correlation_id",
        "details_safe",
    }
    assert envelope["code"] == "NOT_FOUND"
    assert envelope["scope"] == "request"
    assert envelope["retry_class"] == "none"
    assert len(envelope["message_safe"]) <= 300
    serialised = json.dumps(envelope, ensure_ascii=False)
    for forbidden in ("SELECT", "sqlite", "Traceback", "identity_alias"):
        assert forbidden not in serialised


class _StubOwnerSession:
    """Stands in for ``TC-owner-auth-session``: accepts one cookie, enforces CSRF on writes."""

    def __init__(self, owner_id: str) -> None:
        self._owner_id = owner_id

    def authenticate(
        self,
        *,
        session_cookie: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        mutation: bool,
    ) -> str:
        if session_cookie != "valid-session":
            raise IdentityError(ErrorCode.UNAUTHORIZED)
        if mutation and (csrf_header is None or csrf_header != csrf_cookie):
            raise IdentityError(ErrorCode.CSRF_REJECTED)
        return self._owner_id


def _client(engine: Engine, authenticator: Any | None) -> TestClient:
    from server.app.main import create_app

    app = create_app()
    app.state.engine = engine
    if authenticator is not None:
        app.state.owner_session_authenticator = authenticator
    return TestClient(app)


def test_work_detail_requires_a_session(engine: Engine) -> None:
    """No authenticator installed -> 401, never a default owner."""
    load_given(engine, FIXTURE_A)
    with _client(engine, None) as client:
        response = client.get(f"/v1/works/{W2}")
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_work_detail_returns_a_target_object(engine: Engine) -> None:
    """The 200 body validates against ``target.schema.json`` (openapi pins that schema)."""
    import jsonschema

    load_given(engine, FIXTURE_A)
    schema = json.loads(
        (REPO_ROOT / "contracts" / "schemas" / "target.schema.json").read_text(encoding="utf-8")
    )
    with _client(engine, _StubOwnerSession(OWNER_A)) as client:
        response = client.get(f"/v1/works/{W2}", cookies={"rr_session": "valid-session"})
    assert response.status_code == 200
    body = response.json()
    jsonschema.validate(body, schema)
    assert body["kind"] == "work"
    assert body["work_id"] == W2


def test_work_detail_follows_a_merged_work_to_the_survivor(engine: Engine) -> None:
    """A link to a merged work keeps working and shows the surviving identity (I03d)."""
    load_given(engine, FIXTURE_A)
    merge_fixture_a(engine)
    with _client(engine, _StubOwnerSession(OWNER_A)) as client:
        response = client.get(f"/v1/works/{W1}", cookies={"rr_session": "valid-session"})
    assert response.status_code == 200
    assert response.json()["work_id"] == W2


def test_work_detail_unknown_work_is_404(engine: Engine) -> None:
    load_given(engine, FIXTURE_A)
    with _client(engine, _StubOwnerSession(OWNER_A)) as client:
        response = client.get(
            "/v1/works/01JW0RKZZ00000000000000000", cookies={"rr_session": "valid-session"}
        )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_resolve_conflict_requires_cookie_and_csrf_together(engine: Engine) -> None:
    """openapi: cookie AND CSRF in ONE security requirement. A missing token is 403
    ``CSRF_REJECTED`` -- and the session is NOT destroyed by it."""
    load_given(engine, FIXTURE_A)
    conflict = service.quarantine_conflict(
        engine,
        owner_id=OWNER_A,
        conflict_type="alias_points_to_two_works",
        involved_work_ids=[W1, W2],
        involved_identifiers=[{"id_scheme": "openalex", "id_value_normalized": "W2741809807"}],
        caller_module=MOD_INGEST,
    )
    path = f"/v1/identity/conflicts/{conflict.id}/resolve"
    with _client(engine, _StubOwnerSession(OWNER_A)) as client:
        anonymous = client.post(path, json={"decision": "keep_separate"})
        assert anonymous.status_code == 401

        no_csrf = client.post(
            path, json={"decision": "keep_separate"}, cookies={"rr_session": "valid-session"}
        )
        assert no_csrf.status_code == 403
        assert no_csrf.json()["code"] == "CSRF_REJECTED"

        accepted = client.post(
            path,
            json={"decision": "keep_separate", "reason": "khác nhau"},
            cookies={"rr_session": "valid-session", "rr_csrf": "token-token-token-token-token"},
            headers={"X-CSRF-Token": "token-token-token-token-token"},
        )
    assert accepted.status_code == 200
    assert accepted.json()["state"] == "resolved_distinct"
    assert count_of(engine, "identity_merge_audit") == 0


# --- migration chain ---------------------------------------------------------------------------


def test_boundary_sweep_names_no_edge_of_this_module() -> None:
    """``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` is in this card's §2.

    It is exercised here as the claim it actually supports for this module: **none** of the 36
    forbidden edges touches ``MOD-identity-service``, so the card's SG-DENY duty reduces to
    refusing callers that are not in ``allowed_edges`` -- which the ``FORBIDDEN_EDGE`` tests
    above do. Asserting the absence keeps the reduction honest: if a later edit adds an edge
    that names this module, this test fails and the duty grows back.
    """
    fixture = load_fixture("boundary/a-default-deny-sweep-36-edges")
    events = fixture["events"]
    assert len(events) == 36
    touching = [
        event for event in events if MOD_IDENTITY in {event.get("actor"), event.get("callee")}
    ]
    assert touching == [], touching
    modules = yaml.safe_load((REPO_ROOT / "contracts" / "modules.yaml").read_text(encoding="utf-8"))
    forbidden = [
        edge
        for edge in modules["forbidden_edges"]
        if MOD_IDENTITY in {edge.get("caller"), edge.get("callee")}
    ]
    assert forbidden == [], forbidden


def test_migration_chain_resolves_to_a_single_head() -> None:
    """``alembic upgrade head`` must be unambiguous.

    Four Phase 1 cards added revisions in parallel; ``0004_merge_phase1_heads`` joins them, and
    the chain is ``0001 -> 0002_base_entities -> 0002b_shared_move_set_tables ->
    0003_tc_canonical_identity_merge`` on this card's side. A second head would make
    ``upgrade head`` fail on a fresh deployment -- the kind of breakage that only shows up on
    the machine that has no database yet.

    The assertion is on the COUNT, not on which revision is the head: every later card adds a
    revision and moves the head, and that is correct. Naming the current head here would turn
    this test into a tripwire that fails every card but the one that wrote it
    (``CR-TC-research-01``).
    """
    from alembic.script import ScriptDirectory

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads


def test_upgrade_head_creates_every_table_this_card_owns(tmp_path: Path) -> None:
    """The whole chain, from an empty file, creates each table exactly once.

    ``owner`` is the one table two revisions touch (base + auth); both use ``IF NOT EXISTS``,
    so this also proves the two orders do not collide.
    """
    database = tmp_path / "head.db"
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
    engine = create_sqlite_engine(database)
    try:
        with engine.connect() as connection:
            for table in (
                "owner",
                "work",
                "post",
                "post_work",
                "identity_alias",
                "identity_conflict",
                "identity_merge_audit",
                "work_version",
                "first_announced_ledger",
                "saved_snapshot",
                "saved_item",
                "analysis",
                "work_label",
            ):
                assert _table_exists(connection, table), table
    finally:
        engine.dispose()


def test_owner_table_has_one_definition_with_the_full_contract_set(engine: Engine) -> None:
    """``F-A3R1-01`` / ``F-A3R1-14``: one ``CREATE TABLE owner``, carrying every constraint.

    The shipped ``owner`` schema used to depend on which Alembic branch ran first. It is
    asserted here on the DDL text, because that is what actually reaches a deployment: the four
    credential columns of ``AMD-ENT-owner-01``, the singleton guard, the display-name length
    rule and the millisecond timestamp shape.
    """
    with engine.connect() as connection:
        sql = str(
            connection.exec_driver_sql(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'owner'"
            ).scalar_one()
        )
    for column in (
        "password_hash",
        "password_updated_at",
        "failed_login_count",
        "locked_until",
    ):
        assert column in sql, column
    assert "CHECK (singleton_guard = 1)" in sql
    assert "length(display_name) BETWEEN 1 AND 120" in sql
    assert "created_at GLOB" in sql
    assert "failed_login_count  INTEGER NOT NULL DEFAULT 0" in sql

    # And the amended contract is the source of those columns, not this test's opinion.
    entities = yaml.safe_load(
        (REPO_ROOT / "contracts" / "data" / "entities.yaml").read_text(encoding="utf-8")
    )
    owner = next(e for e in entities["entities"] if e["name"] == "owner")
    with engine.connect() as connection:
        columns = {str(row[1]) for row in connection.exec_driver_sql("PRAGMA table_info(owner)")}
    assert columns == {field["name"] for field in owner["fields"]}


def test_timestamp_check_rejects_a_second_precision_value(engine: Engine) -> None:
    """A timestamp without milliseconds is refused by the database, not just by convention."""
    import sqlalchemy.exc

    with pytest.raises(sqlalchemy.exc.IntegrityError), engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at)"
                " VALUES ('01JOWNERBAD0000000000000000', 1, 'x', 'Asia/Ho_Chi_Minh',"
                "         '2026-09-05T10:00:00Z')"
            )
        )


def test_ingest_call_site_binds_to_resolve_target() -> None:
    """The ingest card calls this module across a card boundary; the shape is checked here.

    ``TC-ingest-idempotent-ack-lost`` calls ``resolve_target(connection, owner_id=...,
    identifiers=[...], caller_module=...)``. Binding the signature is a compile-time check that
    a rename on either side is caught by a test rather than by a production traceback.
    """
    import inspect

    signature = inspect.signature(service.resolve_target)
    signature.bind(
        "connection-placeholder",
        owner_id=OWNER_A,
        identifiers=[Identifier(scheme=IdScheme.ARXIV, raw="2501.01234")],
        caller_module=MOD_INGEST,
    )
    # The ingest module builds identifiers from THESE two names on this module.
    assert hasattr(service, "Identifier")
    assert hasattr(service, "IdScheme")
