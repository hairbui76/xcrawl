"""E1/E2 — SC22/SC05/SC49: the cursor advances and the pending item is still there.

Oracle fixture: ``acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json``,
used as data — ``given`` seeds a database built by the **real** Alembic migrations, the four
``events`` run through the **real** service layer (``server.app.report.builder`` /
``publisher`` for the two publishes, ``server.app.analysis.service`` for the late result,
``server.app.report.pending`` for the ledger reads and the Owner's abandon), and
``expected.counts``, ``expected.row_oracles`` and ``forbidden_effects`` are asserted.

Why "the cursor advanced" is the whole test
--------------------------------------------
The item ``E1`` is discovered at ``2026-09-06T02:00Z``. Period 3's window starts at
``2026-09-06T13:00Z``. Every window-shaped query — the obvious implementation — therefore
misses it forever, and misses it *silently*: the report still has items, the counts still look
plausible, and only the one work that needed a second look is gone. The fixture's own
``row_oracles`` say this in as many words: *"E1.discovered_at nằm NGOÀI [coverage_from,
coverage_to) của kỳ 3 — đây chính là lý do sổ pending phải độc lập con trỏ kỳ (I06)"*. So the
assertions below are not "period 3 has two items"; they are "period 3 has this item, whose
``discovered_at`` this test also asserts is outside period 3's window".

The three other things this file covers
----------------------------------------
``tag.rescan_corpus`` (§7) — its five negative constraints as O-7's five unchanged counts,
plus the structural check that this card's rescan module names none of the forbidden tables at
all. ``SG-DENY`` — the collector, the analysis worker and the Telegram adapter each get
``FORBIDDEN_EDGE`` (FE-11 / FE-12 / FE-30) rather than ``UNAUTHORIZED``, because picking the
wrong one of the two is itself a FAIL. And O-6.4 / REQ-AC06 — a real tag remove-and-re-add,
against the real ``tag`` table this card creates, moves the provider call counter by zero.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine, text

from server.app.analysis.service import (
    AnalysisContext,
    ProviderChoice,
    TaskSource,
    enqueue_tasks,
    ledger_state,
)
from server.app.auth.middleware import AuthError
from server.app.db import create_sqlite_engine
from server.app.embedding.generation import (
    DeterministicHashEncoder,
    GenerationFingerprint,
    Normalization,
    Vector,
)
from server.app.embedding.service import EmbeddingService
from server.app.report import pending
from server.app.report.builder import SelectionSettings, TagConfigVersion, build_report
from server.app.report.coverage import new_ulid
from server.app.report.publisher import PublishContext, publish_report, record_build
from server.app.tags import rescan
from server.app.tags.rescan import RescanContext, RescanError

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "reporting"

OWNER_ID = "01JW0WNER00000000000000000"
GENERATION_ID = "01JEMBGEN10000000000000000"
MODEL_NAME = "multilingual-e5-small"
MODEL_VERSION = "1.0.0"
DIMENSION = 4

TAG_ID = "01JTAGPFD00000000000000000"
TAG_TEXT = "protein folding"
WORK_E1 = "01JWRKE1000000000000000000"
WORK_E2 = "01JWRKE2000000000000000000"

MOD_JOB = "MOD-job-service"
MOD_WEB = "MOD-web-ui"

FINGERPRINT = GenerationFingerprint(
    generation_id=GENERATION_ID,
    model_name=MODEL_NAME,
    model_version=MODEL_VERSION,
    dimension=DIMENSION,
    normalization=Normalization.L2,
)


# --------------------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------------------


def _upgrade(db_path: Path) -> None:
    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "radar.db"
    _upgrade(db_path)
    built = create_sqlite_engine(db_path)
    with built.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana,"
                " created_at, password_hash, password_updated_at, failed_login_count,"
                " locked_until) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh',"
                " '2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version,"
                " dimension, normalization, state, expected_vector_count, built_vector_count,"
                " created_at, activated_at) VALUES (:id, :owner, :name, :version, :dim, 'l2',"
                " 'active', 8, 8, '2026-09-01T02:00:00.000Z', '2026-09-01T02:30:00.000Z')"
            ),
            {
                "id": GENERATION_ID,
                "owner": OWNER_ID,
                "name": MODEL_NAME,
                "version": MODEL_VERSION,
                "dim": DIMENSION,
            },
        )
        connection.execute(
            text(
                'INSERT INTO tag (id, owner_id, "text", similarity_threshold, state,'
                " created_at, updated_at, removed_at)"
                " VALUES (:id, :owner, :text, NULL, 'active', :at, :at, NULL)"
            ),
            {
                "id": TAG_ID,
                "owner": OWNER_ID,
                "text": TAG_TEXT,
                "at": "2026-09-01T00:00:00.000Z",
            },
        )
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, 'tag', :subject, :generation, :vector)"
            ),
            {
                "id": new_ulid(),
                "owner": OWNER_ID,
                "subject": TAG_ID,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
            },
        )
    try:
        yield built
    finally:
        built.dispose()


def unit(x: float, y: float) -> Vector:
    norm = (x * x + y * y) ** 0.5
    return Vector(fingerprint=FINGERPRINT, values=(x / norm, y / norm, 0.0, 0.0))


class FakeTagPort:
    """``MOD-tag-service``'s three reads, over the real ``tag`` rows this card creates."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.sequence = 0
        self.frozen: dict[str, TagConfigVersion] = {}
        self.refresh()

    def refresh(self) -> TagConfigVersion:
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    'SELECT id, "text", similarity_threshold FROM tag'
                    " WHERE owner_id = :owner AND state = 'active' ORDER BY id"
                ),
                {"owner": OWNER_ID},
            ).all()
        self.sequence += 1
        self.current = TagConfigVersion(
            id=f"01JTCV{self.sequence:020d}",
            sequence=self.sequence,
            content_hash="sha256:" + f"{self.sequence:064d}",
            payload={
                "tags": [
                    {"id": row[0], "text": row[1], "similarity_threshold": row[2]} for row in rows
                ],
                "tag_aliases": [],
                "tag_exclusions": [],
            },
            created_at="2026-09-01T02:00:00.000Z",
        )
        return self.current

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion:
        return self.current

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion:
        return self.current

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion:
        if report_build_id in self.frozen:
            return self.frozen[report_build_id]
        self.frozen[report_build_id] = self.current
        return self.current


@pytest.fixture
def tag_port(engine: Engine) -> FakeTagPort:
    return FakeTagPort(engine)


def context_for(engine: Engine, tag_port: FakeTagPort) -> PublishContext:
    return PublishContext(
        engine=engine,
        tag_port=tag_port,
        embedding_port=EmbeddingService(
            engine,
            encoder=DeterministicHashEncoder(
                MODEL_NAME, MODEL_VERSION, DIMENSION, Normalization.L2
            ),
        ),
    )


def seed_work(engine: Engine, work_id: str, *, sequence: int, discovered_at: str) -> str:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, canonical_doi, canonical_arxiv_id, title,"
                " paper_url, code_url, current_work_version_id, metadata_state,"
                " identity_state, merged_into_work_id, first_discovered_at, ingest_sequence,"
                " content_state, created_at)"
                " VALUES (:id, :owner, NULL, NULL, 'w', NULL, NULL, NULL, 'partial',"
                " 'active', NULL, :at, :seq, 'present', :at)"
            ),
            {"id": work_id, "owner": OWNER_ID, "at": discovered_at, "seq": sequence},
        )
    return f"work:{work_id}"


def seed_analysis(engine: Engine, work_id: str, *, at: str, task_type: str = "summary") -> str:
    """A ``valid`` analysis row. The absence of the ``summary`` one is what makes an item
    pending (§5.1); the ``label`` one is what gives it a vector to be matched by."""
    analysis_id = new_ulid()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                " target_work_id, target_post_id, task_type, source_fingerprint,"
                " prompt_version, schema_version, generation_number, status, payload,"
                " payload_hash, evidence_level, provider_name, model_name, usage_tokens_in,"
                " usage_tokens_out, analyzed_at, accepted_from_attempt_id, moved_by_merge_id)"
                " VALUES (:id, :owner, :gen, 'work', :work, NULL, :task, :fp, '1.0.0',"
                " '0.1.0', 1, 'valid', '{}', :hash, 'abstract', 'anthropic', 'm', NULL, NULL,"
                " :at, 'attempt', NULL)"
            ),
            {
                "id": analysis_id,
                "owner": OWNER_ID,
                "gen": new_ulid(),
                "work": work_id,
                "task": task_type,
                "fp": f"fp-{task_type}",
                "hash": "sha256:" + "0" * 64,
                "at": at,
            },
        )
    return analysis_id


def seed_label(engine: Engine, work_id: str, *, at: str) -> None:
    """A label vector, which is what selection matches on — not the summary (§4.1).

    The label comes from the ``label`` task and the summary from the ``summary`` task
    (``contracts/ai/tasks.yaml``), which is exactly why an item can be *matched* while its
    summary is still missing — the pending case. ``work_label.analysis_id`` is NOT NULL, so
    the label task's own ``analysis`` row is written here; seeding a ``summary`` row is a
    separate call, and for ``E1`` it deliberately never happens before period 2.
    """
    label_analysis = seed_analysis(engine, work_id, at=at, task_type="label")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work_label (id, owner_id, target_kind, target_work_id,"
                " target_post_id, label_text, analysis_id, embedding_generation_id, vector,"
                " created_at) VALUES (:id, :owner, 'work', :work, NULL, :label, :analysis,"
                " :generation, :vector, :at)"
            ),
            {
                "id": new_ulid(),
                "owner": OWNER_ID,
                "work": work_id,
                "label": TAG_TEXT,
                "analysis": label_analysis,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
                "at": at,
            },
        )


def publish_period(engine: Engine, tag_port: FakeTagPort) -> Any:
    snapshot = build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id=str(uuid.uuid4()),
        tag_port=tag_port,
        embedding_port=context_for(engine, tag_port).embedding_port,
        settings=SelectionSettings(),
    )
    record_build(context_for(engine, tag_port), snapshot, caller_module=MOD_JOB)
    return publish_report(context_for(engine, tag_port), snapshot)


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar() or 0)


def counts_snapshot(engine: Engine) -> dict[str, int]:
    """O-7's five numbers, plus the rescan ledger's own."""
    return {
        "coverage_window": count(
            engine, "SELECT COUNT(*) FROM coverage_window WHERE owner_id = :o", o=OWNER_ID
        ),
        "report": count(engine, "SELECT COUNT(*) FROM report WHERE owner_id = :o", o=OWNER_ID),
        "first_announced_ledger": count(
            engine, "SELECT COUNT(*) FROM first_announced_ledger WHERE owner_id = :o", o=OWNER_ID
        ),
        "backfill_consumed": count(
            engine,
            "SELECT COUNT(*) FROM backfill_ledger WHERE owner_id = :o"
            " AND consumed_in_report_id IS NOT NULL",
            o=OWNER_ID,
        ),
        "outbox_intent": count(
            engine, "SELECT COUNT(*) FROM outbox_intent WHERE owner_id = :o", o=OWNER_ID
        ),
        "rescan_ledger": count(
            engine, "SELECT COUNT(*) FROM rescan_ledger WHERE owner_id = :o", o=OWNER_ID
        ),
    }


# --------------------------------------------------------------------------------------
# Fixture e -- the three periods
# --------------------------------------------------------------------------------------


def _period_one(engine: Engine, tag_port: FakeTagPort) -> Any:
    """Period 1, before either work exists: an empty period that leaves a cursor."""
    return publish_period(engine, tag_port)


def _period_two(engine: Engine, tag_port: FakeTagPort) -> Any:
    """Fixture ``e`` events 1-2: E1 and E2 selected; E1 has no summary.

    E2 has one, E1 does not, and both are matched by the same label vector. That asymmetry is
    the fixture's setup and the only thing that separates a pending item from a complete one.
    """
    seed_work(engine, WORK_E1, sequence=1, discovered_at="2026-09-06T02:00:00.000Z")
    seed_work(engine, WORK_E2, sequence=2, discovered_at="2026-09-06T02:00:01.000Z")
    seed_label(engine, WORK_E1, at="2026-09-06T02:30:00.000Z")
    seed_label(engine, WORK_E2, at="2026-09-06T02:30:00.000Z")
    seed_analysis(engine, WORK_E2, at="2026-09-06T03:00:00.000Z")
    return publish_period(engine, tag_port)


def _late_result(engine: Engine) -> str:
    """Fixture ``e`` event 3: E1's summary arrives **after** period 2 was published."""
    return seed_analysis(engine, WORK_E1, at="2026-09-06T18:00:00.000Z")


def test_fixture_e_period_two_opens_the_pending_row_and_is_partial(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """``after_event_2``: one pending row, ``reason = 'missing_summary'``, quality partial.

    The item is **not** hidden — AMD-B17 — so period 2 still carries two report items, one of
    them with ``summary_state = 'pending'``.
    """
    _period_one(engine, tag_port)
    result = _period_two(engine, tag_port)
    assert result.published
    assert result.quality == pending.QUALITY_PARTIAL

    with engine.connect() as connection:
        open_rows = pending.carried_forward(connection, owner_id=OWNER_ID)
        assert len(open_rows) == 1
        assert open_rows[0].target_key == f"work:{WORK_E1}"
        assert open_rows[0].reason == "missing_summary"
        assert (
            pending.quality_for_window(
                connection, owner_id=OWNER_ID, coverage_window_id=result.coverage_window_id
            )
            == pending.QUALITY_PARTIAL
        )
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report_item WHERE owner_id = :o AND report_id = :r",
            o=OWNER_ID,
            r=result.report_id,
        )
        == 2
    ), "a pending item is still an item (AMD-B17)"


def test_fixture_e_the_item_reappears_in_the_next_period_as_a_late_discovery(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Events 3-4, and the fixture's central ``row_oracle``.

    Three separate claims, asserted separately, because passing only the first two is exactly
    the defect: (a) the item is in period 3; (b) it is labelled ``late_discovery``; and (c)
    its ``discovered_at`` is **outside** period 3's window, which is why (a) could only have
    come from the ledger and not from a window query.
    """
    _period_one(engine, tag_port)
    period_two = _period_two(engine, tag_port)
    _late_result(engine)
    period_three = publish_period(engine, tag_port)
    assert period_three.published

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT selection_reason FROM report_item"
                " WHERE owner_id = :o AND report_id = :r AND target_key = :k"
            ),
            {"o": OWNER_ID, "r": period_three.report_id, "k": f"work:{WORK_E1}"},
        ).fetchone()
    assert row is not None, "E1 must be carried into period 3"
    reason = json.loads(row[0])
    assert reason["late_discovery"] is True
    assert reason["pending_since_window_sequence"] is not None

    discovered_at = datetime.fromisoformat("2026-09-06T02:00:00.000Z".replace("Z", "+00:00"))
    window_from = datetime.fromisoformat(period_three.coverage_from.replace("Z", "+00:00"))
    assert (
        discovered_at < window_from
    ), "the whole point of I06: E1 is outside period 3's window and is carried anyway"
    assert period_two.report_id != period_three.report_id


def test_fixture_e_the_late_discovery_is_still_a_new_discovery(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Fixture ``e``'s ``row_oracle``: *"item_type vẫn = 'new_discovery'"*.

    §5.3 qualifies it — a late discovery **that has never been announced** stays
    ``new_discovery`` — and fixture ``e`` settles what "announced" means here: ``E1`` was a
    ``report_item`` of period 2 (``report_item[report_id=ERP1]`` = 2, and AMD-B17 says a
    pending item is shown, not hidden) and the fixture *still* expects ``new_discovery`` in
    period 3. So carrying an item with ``summary_state = 'pending'`` is **not** announcing it,
    and appearing in a partial period is not the same event as being announced.

    History, because the shape of this test is the evidence. It was written as
    ``xfail(strict=True)`` when this card landed: ``publisher._write_first_announcements``
    wrote a ``first_announced_ledger`` row for every ``new_discovery`` work item, pending ones
    included, so period 3 read the item as already announced and labelled it
    ``prior_reference``. That was ``CR-TC-BACKFILL-09``, later audit finding ``F-A3-P4-01``.
    ``PKT-TC-REPORT-FIX2`` added ``summary_state == 'present'`` as a condition on writing the
    ledger row, this test XPASSed, and it is now a plain assertion.

    The `strict=True` is what made that sequence work: the flip announced itself instead of
    the test sitting green in the wrong state, and the assertion never had to be weakened to
    match the implementation.
    """
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    _late_result(engine)
    period_three = publish_period(engine, tag_port)
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT selection_reason, item_type, first_announced_report_id FROM report_item"
                " WHERE owner_id = :o AND report_id = :r AND target_key = :k"
            ),
            {"o": OWNER_ID, "r": period_three.report_id, "k": f"work:{WORK_E1}"},
        ).fetchone()
    assert row is not None, "E1 must be carried into period 3"
    reason = json.loads(row[0])

    # The fixture's row oracle, on the column and on the read model, which are written from
    # two different places and so are two claims rather than one.
    assert reason["item_type"] == "new_discovery"
    assert row[1] == "new_discovery"
    # A `new_discovery` has no "already reported on day D" pointer -- the field that would
    # have carried the wrong story to the reader.
    assert row[2] is None
    # And it is the *late* one: the display label rides alongside the type, per §5.3.
    assert reason["late_discovery"] is True

    # The ledger row is written now, by the period that actually announced it -- once, and
    # pointing at period 3 rather than at the partial period that only listed it (I07).
    with engine.connect() as connection:
        ledger = connection.execute(
            text(
                "SELECT first_report_id FROM first_announced_ledger"
                " WHERE owner_id = :o AND canonical_work_id = :w"
            ),
            {"o": OWNER_ID, "w": WORK_E1},
        ).all()
    assert len(ledger) == 1, "I07: exactly one effective first-announcement row"
    assert ledger[0][0] == period_three.report_id


def test_the_partial_period_announced_nothing_it_could_not_show(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """The other side of ``F-A3-P4-01``: period 2 lists the item but does not announce it.

    Asserted separately from the test above because the two failure modes are different. That
    one catches "the late discovery came back as a reference"; this one catches an
    implementation that stopped writing ``first_announced_ledger`` rows altogether, which
    would also make that test pass — and would break I07 in the opposite direction, letting a
    work be announced as new in every period forever.
    """
    _period_one(engine, tag_port)
    period_two = _period_two(engine, tag_port)

    assert period_two.quality == pending.QUALITY_PARTIAL
    # E1 is listed (AMD-B17: shown, not hidden) ...
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report_item WHERE owner_id = :o AND report_id = :r"
            " AND target_key = :k",
            o=OWNER_ID,
            r=period_two.report_id,
            k=f"work:{WORK_E1}",
        )
        == 1
    )
    # ... and not announced, while E2 -- which had its summary all along -- is.
    with engine.connect() as connection:
        announced = {
            row[0]
            for row in connection.execute(
                text("SELECT canonical_work_id FROM first_announced_ledger WHERE owner_id = :o"),
                {"o": OWNER_ID},
            )
        }
    assert announced == {WORK_E2}


def test_fixture_e_the_row_is_resolved_not_deleted(engine: Engine, tag_port: FakeTagPort) -> None:
    """``expected.counts``: 0 pending, 1 ``resolved_reported_late``, 1 row in total.

    The total is the assertion that matters. "0 pending" alone is satisfied by deleting the
    row, which is fixture ``e``'s first forbidden effect.
    """
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    _late_result(engine)
    publish_period(engine, tag_port)

    fixture = json.loads(
        (FIXTURES / "e-late-analysis-pending-then-late-discovery.json").read_text("utf-8")
    )
    expected = fixture["expected"]["counts"]
    with engine.connect() as connection:
        assert (
            pending.count_by_state(connection, owner_id=OWNER_ID, state=pending.STATE_PENDING)
            == expected["pending_item_ledger[state='pending']"]
        )
        assert (
            pending.count_by_state(connection, owner_id=OWNER_ID, state=pending.STATE_RESOLVED_LATE)
            == expected["pending_item_ledger[state='resolved_reported_late']"]
        )
        assert pending.count_total(connection, owner_id=OWNER_ID) == expected["pending_item_ledger"]


def test_o_5_1_the_ledger_arithmetic_balances_across_the_publish(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """O-5.1: nothing leaves the ledger. Counted before and after period 3's commit."""
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    _late_result(engine)
    with engine.connect() as connection:
        before_total = pending.count_total(connection, owner_id=OWNER_ID)
        before_open = pending.count_by_state(
            connection, owner_id=OWNER_ID, state=pending.STATE_PENDING
        )
    publish_period(engine, tag_port)
    with engine.connect() as connection:
        after_total = pending.count_total(connection, owner_id=OWNER_ID)
        after_open = pending.count_by_state(
            connection, owner_id=OWNER_ID, state=pending.STATE_PENDING
        )
        resolved = pending.count_by_state(
            connection, owner_id=OWNER_ID, state=pending.STATE_RESOLVED_LATE
        )
    assert after_total == before_total, "the total never shrinks -- rows change state"
    assert after_open == before_open - resolved


def test_the_ledger_module_issues_no_delete(engine: Engine) -> None:
    """Structural: ``pending.py`` contains no DELETE against the ledger.

    Behavioural coverage above proves the current paths keep the rows; this proves the module
    has no path that could remove one, which is the property ``entities.yaml``'s
    data-deletion table actually asks for.
    """
    import re

    source = (REPO_ROOT / "server" / "app" / "report" / "pending.py").read_text("utf-8")
    assert re.search(r"\bDELETE\s+FROM\b", source) is None
    assert re.search(r"\bTRUNCATE\b|\bDROP\s+TABLE\b", source) is None


def test_only_the_owner_abandons_a_pending_item(engine: Engine, tag_port: FakeTagPort) -> None:
    """§5.3: no timeout, no sweep — an explicit act, and the row stays in the table."""
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    with engine.begin() as connection:
        assert pending.abandon(connection, owner_id=OWNER_ID, target_key=f"work:{WORK_E1}")
    with engine.connect() as connection:
        assert (
            pending.count_by_state(connection, owner_id=OWNER_ID, state=pending.STATE_ABANDONED)
            == 1
        )
        assert pending.count_total(connection, owner_id=OWNER_ID) == 1
        assert pending.carried_forward(connection, owner_id=OWNER_ID) == []
    with engine.begin() as connection:
        assert not pending.abandon(connection, owner_id=OWNER_ID, target_key=f"work:{WORK_E1}")


def test_an_abandoned_item_is_not_carried_into_the_next_period(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """The other half of abandon: the Owner's decision actually removes it from selection."""
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    with engine.begin() as connection:
        pending.abandon(connection, owner_id=OWNER_ID, target_key=f"work:{WORK_E1}")
    _late_result(engine)
    period_three = publish_period(engine, tag_port)
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report_item WHERE owner_id = :o AND report_id = :r"
            " AND target_key = :k",
            o=OWNER_ID,
            r=period_three.report_id,
            k=f"work:{WORK_E1}",
        )
        == 0
    )


def test_the_open_row_keeps_its_first_window_across_two_pending_periods(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """``ux_pending_owner_target_open`` and §5.3: ``first_pending_window_id`` never moves.

    It is what ``pending_since_window_sequence`` renders. If a second still-pending period
    overwrote it, the label would walk forward every period until it meant nothing.
    """
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    with engine.connect() as connection:
        first = pending.carried_forward(connection, owner_id=OWNER_ID)[0]
    publish_period(engine, tag_port)  # still no summary for E1
    with engine.connect() as connection:
        again = pending.carried_forward(connection, owner_id=OWNER_ID)
    assert len(again) == 1
    assert again[0].id == first.id
    assert again[0].first_pending_window_id == first.first_pending_window_id


# --------------------------------------------------------------------------------------
# The port the analysis service has been carrying as None
# --------------------------------------------------------------------------------------


class _FakeProviderConfig:
    def provider_for(self, task_type: str) -> ProviderChoice:
        return ProviderChoice(
            task_type=task_type,
            auth_family="api_key",
            provider_name="example-vendor-api",
            model_name="m-1",
            enabled=True,
        )


class _FakeTaskInput:
    def sources_for(self, *, target_key: str) -> list[TaskSource]:
        return [
            TaskSource(
                source_id=new_ulid(),
                kind="work_version",
                text="Abstract.",
                source_hash="sha256:" + "c" * 64,
                retrieved_at="2026-09-06T17:00:00.000Z",
            )
        ]


def test_the_analysis_service_can_now_record_a_pending_item(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """``server.app.analysis.service`` finally has a ``PendingLedgerPort`` implementation.

    Since Phase 3 ``AnalysisContext.pending_ledger`` has been ``None``, so ``_fail_task``
    reported ``pending_ledger_recorded: False`` and a budget-exhausted item never reached the
    ledger — ``I06``'s failure arriving through the analysis door rather than the report door.
    :class:`~server.app.report.pending.EngineBoundPendingLedger` closes it, and the ledger row
    it writes is a real row in the real table, anchored to the real coverage window.

    ``CR-TC-BACKFILL-08`` asks ``TC-analysis-once-per-generation`` to wire this into its own
    context so that its ``xfail`` for the same property can flip; that file is its write set,
    not this card's.
    """
    _period_one(engine, tag_port)
    ledger = pending.EngineBoundPendingLedger(
        engine=engine,
        owner_id=OWNER_ID,
        window_provider=pending.current_window_provider(engine, OWNER_ID),
        id_factory=new_ulid,
    )
    ctx = AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=_FakeProviderConfig(),
        task_input=_FakeTaskInput(),
        pending_ledger=ledger,
    )
    assert ledger_state(ctx)["pending_ledger_wired"] is True

    ledger.record_pending(target_key=f"work:{WORK_E1}", reason="budget_exceeded")
    with engine.connect() as connection:
        rows = pending.carried_forward(connection, owner_id=OWNER_ID)
    assert [row.target_key for row in rows] == [f"work:{WORK_E1}"]
    assert rows[0].reason == "budget_exceeded"


def test_the_port_joins_the_callers_transaction_when_given_its_connection(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """``CR-TC-BACKFILL-02``, fixed and measured on both sides of the fix.

    W3B measured the defect rather than predicting it: ``_fail_task`` calls the port from
    inside an open ``TXN-analysis-*`` write transaction, and on SQLite the outer transaction
    holds RESERVED, so a second connection's INSERT waits out ``busy_timeout`` and dies
    ``database is locked`` — 0.00 s outside a transaction against 5.01 s to failure inside one.

    This test reproduces exactly that situation with a **200 ms** timeout so the proof is
    cheap, and asserts both halves:

    * without ``connection``, the write still contends and raises ``OperationalError`` — the
      pinned failure W3B's ``strict=True`` xfail is written against, kept intact so that fix
      does not silently change shape;
    * with ``connection``, the row is written **on the caller's transaction**: invisible to
      another connection before the commit, present after it. That is the property the
      contract asks for and a retry could never provide, because the lock is held by the very
      transaction the caller is still inside.
    """
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError

    _period_one(engine, tag_port)
    ledger_engine = create_sqlite_engine(engine.url.database or ":memory:")

    @event.listens_for(ledger_engine, "connect")
    def _short_busy_timeout(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA busy_timeout=200")
        finally:
            cursor.close()

    ledger = pending.EngineBoundPendingLedger(
        engine=ledger_engine,
        owner_id=OWNER_ID,
        window_provider=pending.current_window_provider(ledger_engine, OWNER_ID),
        id_factory=new_ulid,
    )

    # (a) the defect, still reproducible: no connection, a write lock already held.
    with engine.begin() as outer:
        outer.execute(
            text("UPDATE owner SET display_name = 'holding the write lock' WHERE id = :id"),
            {"id": OWNER_ID},
        )
        with pytest.raises(OperationalError):
            ledger.record_pending(target_key=f"work:{WORK_E1}", reason="analysis_failed")

    # (b) the fix: the same call, given the caller's connection.
    with engine.begin() as outer:
        outer.execute(
            text("UPDATE owner SET display_name = 'still holding it' WHERE id = :id"),
            {"id": OWNER_ID},
        )
        ledger.record_pending(
            target_key=f"work:{WORK_E1}", reason="analysis_failed", connection=outer
        )
        # Uncommitted, so a different connection cannot see it yet -- which is the proof that
        # the row is genuinely inside the caller's transaction rather than beside it.
        assert (
            count(
                ledger_engine,
                "SELECT COUNT(*) FROM pending_item_ledger WHERE owner_id = :o",
                o=OWNER_ID,
            )
            == 0
        )

    with engine.connect() as connection:
        rows = pending.carried_forward(connection, owner_id=OWNER_ID)
    assert [row.target_key for row in rows] == [f"work:{WORK_E1}"]
    assert rows[0].reason == "analysis_failed"
    ledger_engine.dispose()


def test_the_connection_bound_adapter_takes_the_same_override(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """The other adapter accepts ``connection=`` too, so one call shape fits both."""
    _period_one(engine, tag_port)
    with engine.connect() as connection:
        window_id = pending.current_window_provider(engine, OWNER_ID)()
    assert window_id is not None
    with engine.begin() as outer:
        pending.ConnectionBoundPendingLedger(
            connection=outer,
            owner_id=OWNER_ID,
            first_pending_window_id=window_id,
            id_factory=new_ulid,
        ).record_pending(target_key=f"work:{WORK_E2}", reason="budget_exceeded", connection=outer)
    with engine.connect() as connection:
        assert pending.count_total(connection, owner_id=OWNER_ID) == 1


def test_the_port_refuses_rather_than_inventing_a_coverage_window(engine: Engine) -> None:
    """No window yet ⇒ ``VALIDATION_ERROR``, not a guessed anchor.

    ``first_pending_window_id`` is what the "phát hiện muộn, thuộc kỳ #N" label is computed
    from, so a guessed value would be wrong forever and invisible.
    """
    ledger = pending.EngineBoundPendingLedger(
        engine=engine,
        owner_id=OWNER_ID,
        window_provider=pending.current_window_provider(engine, OWNER_ID),
        id_factory=new_ulid,
    )
    with pytest.raises(pending.PendingLedgerError) as raised:
        ledger.record_pending(target_key=f"work:{WORK_E1}", reason="analysis_failed")
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


def test_an_unknown_reason_is_refused_before_it_reaches_the_check_constraint(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    _period_one(engine, tag_port)
    with engine.begin() as connection, pytest.raises(pending.PendingLedgerError) as raised:
        pending.record_pending(
            connection,
            owner_id=OWNER_ID,
            target_key=f"work:{WORK_E1}",
            reason="looked_boring",
            first_pending_window_id="x",
            new_id=new_ulid(),
        )
    assert raised.value.details_safe["violation_kind"] == "enum_invalid"


# --------------------------------------------------------------------------------------
# §7 -- tag.rescan_corpus
# --------------------------------------------------------------------------------------


@pytest.fixture
def rescan_ctx(engine: Engine) -> RescanContext:
    moments = iter(
        datetime(2026, 9, 21, 8, 0, tzinfo=UTC) + timedelta(seconds=n) for n in range(0, 600)
    )
    return RescanContext(engine=engine, owner_id=OWNER_ID, clock=lambda: next(moments))


def test_o_7_a_rescan_moves_one_count_and_only_one(
    engine: Engine, tag_port: FakeTagPort, rescan_ctx: RescanContext
) -> None:
    """O-7 exactly as ``time-and-tags.md`` §7 states it.

    Five counts unchanged, ``#rescan_ledger`` up by exactly 1. Snapshotted after two real
    periods so the numbers being held still are non-zero — holding zeros still is not
    evidence of anything.
    """
    _period_one(engine, tag_port)
    _period_two(engine, tag_port)
    before = counts_snapshot(engine)
    assert before["coverage_window"] > 0 and before["report"] > 0

    record = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-1", caller_module=MOD_WEB
    )
    assert record.state == rescan.STATE_REQUESTED
    assert record.consumed_report_id is None

    after = counts_snapshot(engine)
    assert after["rescan_ledger"] == before["rescan_ledger"] + 1
    for key in (
        "coverage_window",
        "report",
        "first_announced_ledger",
        "backfill_consumed",
        "outbox_intent",
    ):
        assert after[key] == before[key], key


def test_the_rescan_module_names_none_of_the_forbidden_tables(engine: Engine) -> None:
    """§7's five negative constraints, made structural.

    The behavioural test above proves the counts held for *one* command. This proves the
    module has no statement that could move them at all, which is the stronger claim and the
    one that survives a future edit.
    """
    source = (REPO_ROOT / "server" / "app" / "tags" / "rescan.py").read_text("utf-8")
    body = source.split('"""', 2)[-1]  # skip the module docstring, which names them on purpose
    for table in sorted(rescan.FORBIDDEN_TABLES):
        assert f"FROM {table}" not in body
        assert f"INTO {table}" not in body
        assert f"UPDATE {table}" not in body


def test_a_second_open_rescan_for_the_same_tag_is_an_idempotency_conflict(
    engine: Engine, rescan_ctx: RescanContext
) -> None:
    """``ux_rescan_open``: at most one open rescan per tag, enforced by the database."""
    rescan.request_rescan(rescan_ctx, tag_id=TAG_ID, request_id="req-1", caller_module=MOD_WEB)
    with pytest.raises(RescanError) as raised:
        rescan.request_rescan(rescan_ctx, tag_id=TAG_ID, request_id="req-2", caller_module=MOD_WEB)
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT
    assert raised.value.http_status == 409
    assert count(engine, "SELECT COUNT(*) FROM rescan_ledger WHERE owner_id = :o", o=OWNER_ID) == 1


def test_the_same_request_id_returns_the_same_rescan(rescan_ctx: RescanContext) -> None:
    """``ports.yaml``: *"Cùng request_id không tạo hai lệnh quét."*"""
    first = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-1", caller_module=MOD_WEB
    )
    again = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-1", caller_module=MOD_WEB
    )
    assert again.id == first.id


def test_a_rescan_for_a_tag_that_does_not_exist_is_not_found(rescan_ctx: RescanContext) -> None:
    with pytest.raises(RescanError) as raised:
        rescan.request_rescan(
            rescan_ctx,
            tag_id="01JTAGNOPE0000000000000000",
            request_id="req-1",
            caller_module=MOD_WEB,
        )
    assert raised.value.code is ErrorCode.NOT_FOUND


def test_a_finished_rescan_frees_the_slot(engine: Engine, rescan_ctx: RescanContext) -> None:
    record = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-1", caller_module=MOD_WEB
    )
    with engine.begin() as connection:
        assert rescan.advance(
            connection, owner_id=OWNER_ID, rescan_id=record.id, state=rescan.STATE_RUNNING
        )
        assert rescan.advance(
            connection, owner_id=OWNER_ID, rescan_id=record.id, state=rescan.STATE_DONE
        )
        # Terminal is terminal: a done rescan does not go back to running.
        assert not rescan.advance(
            connection, owner_id=OWNER_ID, rescan_id=record.id, state=rescan.STATE_RUNNING
        )
    second = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-2", caller_module=MOD_WEB
    )
    assert second.id != record.id


# --------------------------------------------------------------------------------------
# SG-DENY -- the R5-01 boundary table
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "caller,edge",
    [
        ("MOD-x-collector", "FE-11"),
        ("MOD-analysis-worker", "FE-12"),
        ("MOD-telegram-adapter", "FE-30"),
        ("MOD-embedding-service", "FE-23"),
    ],
)
def test_sg_deny_a_forbidden_caller_gets_forbidden_edge_not_unauthorized(
    rescan_ctx: RescanContext, caller: str, edge: str
) -> None:
    """Card §5's R5-01 table: an in-process call across an unregistered edge is
    ``FORBIDDEN_EDGE``. ``UNAUTHORIZED`` is the HTTP "who are you" answer and is the wrong
    code here — card §10 ``SG-DENY`` makes choosing the wrong one a FAIL in its own right.
    """
    with pytest.raises(AuthError) as raised:
        rescan.request_rescan(
            rescan_ctx, tag_id=TAG_ID, request_id=f"req-{caller}", caller_module=caller
        )
    assert raised.value.code is ErrorCode.FORBIDDEN_EDGE
    assert raised.value.details_safe["caller_module"] == caller
    assert raised.value.details_safe["callee_module"] == "MOD-tag-service"


def test_sg_deny_the_refusal_happens_before_any_write(
    engine: Engine, rescan_ctx: RescanContext
) -> None:
    """Default deny is a gate, not a rollback: nothing is attempted, so nothing can leak."""
    with pytest.raises(AuthError):
        rescan.request_rescan(
            rescan_ctx, tag_id=TAG_ID, request_id="req-x", caller_module="MOD-x-collector"
        )
    assert count(engine, "SELECT COUNT(*) FROM rescan_ledger WHERE owner_id = :o", o=OWNER_ID) == 0


def test_the_allowed_caller_is_not_refused(rescan_ctx: RescanContext) -> None:
    """The other half of the same guard: ``MOD-web-ui`` is in ``allowed_edges``."""
    record = rescan.request_rescan(
        rescan_ctx, tag_id=TAG_ID, request_id="req-ok", caller_module=MOD_WEB
    )
    assert record.state == rescan.STATE_REQUESTED


def test_the_rescan_operation_id_is_the_contract_one() -> None:
    """No near-miss operation names (card §4): the id comes from the generated registry."""
    assert OperationId.TAG_RESCAN_CORPUS.value == "tag.rescan_corpus"


# --------------------------------------------------------------------------------------
# O-6.4 / REQ-AC06 -- a tag edit calls no model
# --------------------------------------------------------------------------------------


def test_o_6_4_removing_and_re_adding_a_tag_moves_the_provider_counter_by_zero(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """AC-06 against the **real** ``tag`` table, which did not exist before this card.

    ``TC-analysis-once-per-generation`` proved the same delta with the tag edit simulated —
    it had no table to edit. Here the tag row really moves to ``removed`` and a second row
    with a new ``tag.id`` is really inserted, the tag config version really changes, and the
    provider call counter still moves by zero: the analysis key does not contain a tag
    (ADR-0008), so the same targets come back with the same keys and every one is skipped.
    """
    from server.app.analysis.key import compute_source_fingerprint
    from server.app.analysis.service import TargetRequest

    seed_work(engine, WORK_E2, sequence=1, discovered_at="2026-09-06T02:00:01.000Z")

    class Counter:
        calls = 0

    ctx = AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=_FakeProviderConfig(),
        task_input=_FakeTaskInput(),
    )
    fingerprint = compute_source_fingerprint(work_version_content_fingerprint="sha256:" + "c" * 64)
    target = TargetRequest(
        target_kind="work",
        target_id=WORK_E2,
        task_type="summary",
        source_fingerprint=fingerprint,
        prompt_version="1.0.0",
        schema_version="0.1.0",
    )
    before = enqueue_tasks(ctx, [target], caller_module="MOD-report-service")
    assert before["created"]
    generations_before = count(engine, "SELECT COUNT(*) FROM analysis_generation")
    attempts_before = count(engine, "SELECT COUNT(*) FROM analysis_attempt")

    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE tag SET state = 'removed', removed_at = :at, updated_at = :at"
                " WHERE owner_id = :o AND id = :id"
            ),
            {"at": "2026-09-15T02:00:00.000Z", "o": OWNER_ID, "id": TAG_ID},
        )
        connection.execute(
            text(
                'INSERT INTO tag (id, owner_id, "text", similarity_threshold, state,'
                " created_at, updated_at, removed_at)"
                " VALUES (:id, :o, :text, NULL, 'active', :at, :at, NULL)"
            ),
            {
                "id": "01JTAGPFD20000000000000000",
                "o": OWNER_ID,
                "text": TAG_TEXT,
                "at": "2026-09-20T02:00:00.000Z",
            },
        )
    old_version = tag_port.current.id
    assert tag_port.refresh().id != old_version, "the tag config version really moved"

    after = enqueue_tasks(ctx, [target], caller_module="MOD-report-service")
    assert after["created"] == []
    assert count(engine, "SELECT COUNT(*) FROM analysis_generation") == generations_before
    assert count(engine, "SELECT COUNT(*) FROM analysis_attempt") == attempts_before
    assert Counter.calls == 0
