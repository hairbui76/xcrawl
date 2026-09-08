"""E1/E2 -- SC08/SC15/SC22: the coverage chain has no gap, including across an empty period.

The oracle is ``acceptance/fixtures/reporting/d-empty-period-coverage-only.json``, used as
data, plus the ledger-level oracle O-4.1 of ``contracts/reporting/time-and-tags.md`` §4.9
applied to every window this file creates:

    ``window_from[n] == window_to[n-1]``  **and**
    ``ingest_sequence_from[n] == ingest_sequence_to[n-1]``  **and**
    exactly one window with ``predecessor_window_id IS NULL``.

Both axes, every time. Checking only the timestamps would pass for an implementation that
loses items sharing a millisecond with a period boundary, which is the whole reason §4.3 puts
membership on the sequence axis.

The three shapes a period can take
-----------------------------------
1. **Content.** Items selected, a report published, coverage advances.
2. **Empty** (``T-RP-07``). Nothing matched, and that is a *valid outcome*: a coverage row with
   ``report_id = NULL`` appears, the build is ``aborted`` with ``abort_reason = 'empty_period'``
   -- distinguishable from a broken build, which is I13 -- and **no** delivery intent is
   created (REQ-D57). Skipping the row is what would put a hole in the chain.
3. **Failed to commit** (E2). The write is refused mid-transaction by
   ``server/app/db/faults.py``. Coverage does **not** advance, no ``report_item`` survives, and
   the backfill entitlement is **not** consumed -- AMD-B04's "do not consume backfill because
   the builder crashed", asserted by counting rows rather than by reading a log.

The empty-period replay
------------------------
Fixture ``d``'s negative oracle is the reason §4.7.1 chose to keep a ``report`` row for an
empty period at all: replaying the same ``report_build_id`` must return the old result, not
create a second window and not answer ``CONFLICT``. Without the row there is no receipt to
find, and a lost ACK would push the pointer twice.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector
from server.app.embedding.generation import (
    DeterministicHashEncoder,
    GenerationFingerprint,
    Normalization,
    Vector,
)
from server.app.embedding.service import EmbeddingService
from server.app.report.backfill import consumed_count
from server.app.report.builder import (
    BuildSnapshot,
    SelectionSettings,
    ServiceBackfill,
    TagConfigVersion,
    build_report,
)
from server.app.report.coverage import (
    CoverageRepository,
    ReportError,
    contiguity_violations,
    parse_timestamp_utc_ms,
)
from server.app.report.publisher import PublishContext, publish_report, record_build

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "reporting"

OWNER_ID = "01JW0WNER00000000000000000"
GENERATION_ID = "01JEMBGEN10000000000000000"
MODEL_NAME = "multilingual-e5-small"
MODEL_VERSION = "1.0.0"
DIMENSION = 4
MOD_JOB = "MOD-job-service"

FINGERPRINT = GenerationFingerprint(
    generation_id=GENERATION_ID,
    model_name=MODEL_NAME,
    model_version=MODEL_VERSION,
    dimension=DIMENSION,
    normalization=Normalization.L2,
)

TAG_ID = "01JTAGPFD00000000000000000"
#: The tag the owner adds *after* the pointer has already passed the old item (D28).
TAG_ID_LATE = "01JTAGNEW00000000000000000"
TCV1 = "01JTCV10000000000000000000"
TCV2 = "01JTCV20000000000000000000"


# --- harness ----------------------------------------------------------------------------------


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
    try:
        yield built
    finally:
        built.dispose()


def _ulid() -> str:
    from server.app.report.coverage import new_ulid

    return new_ulid()


def unit(x: float, y: float) -> Vector:
    norm = (x * x + y * y) ** 0.5
    return Vector(fingerprint=FINGERPRINT, values=(x / norm, y / norm, 0.0, 0.0))


def seed_tag_vector(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, 'tag', :subject, :generation, :vector)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "subject": TAG_ID,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
            },
        )


def seed_matching_work(
    engine: Engine, work_id: str, *, sequence: int, discovered_at: str, matches: bool = True
) -> str:
    """A work with a summary and a label -- matching the tag, or deliberately far from it."""
    target_key = f"work:{work_id}"
    analysis_id = _ulid()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, canonical_doi, canonical_arxiv_id, title,"
                " paper_url, code_url, current_work_version_id, metadata_state,"
                " identity_state, merged_into_work_id, first_discovered_at, ingest_sequence,"
                " content_state, created_at)"
                " VALUES (:id, :owner, NULL, NULL, 'w', NULL, NULL, NULL, 'partial', 'active',"
                " NULL, :at, :seq, 'present', :at)"
            ),
            {"id": work_id, "owner": OWNER_ID, "at": discovered_at, "seq": sequence},
        )
        connection.execute(
            text(
                "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                " target_work_id, target_post_id, task_type, source_fingerprint,"
                " prompt_version, schema_version, generation_number, status, payload,"
                " payload_hash, evidence_level, provider_name, model_name, usage_tokens_in,"
                " usage_tokens_out, analyzed_at, accepted_from_attempt_id, moved_by_merge_id)"
                " VALUES (:id, :owner, :gen, 'work', :work, NULL, 'summary', 'fp', '1.0.0',"
                " '0.1.0', 1, 'valid', '{}', :hash, 'abstract', 'anthropic', 'm', NULL, NULL,"
                " :at, 'attempt', NULL)"
            ),
            {
                "id": analysis_id,
                "owner": OWNER_ID,
                "gen": _ulid(),
                "work": work_id,
                "hash": "sha256:" + "0" * 64,
                "at": discovered_at,
            },
        )
        vector = unit(1.0, 0.05) if matches else unit(0.0, 1.0)
        connection.execute(
            text(
                "INSERT INTO work_label (id, owner_id, target_kind, target_work_id,"
                " target_post_id, label_text, analysis_id, embedding_generation_id, vector,"
                " created_at) VALUES (:id, :owner, 'work', :work, NULL, :label, :analysis,"
                " :generation, :vector, :at)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "work": work_id,
                "label": f"label-{work_id}",
                "analysis": analysis_id,
                "generation": GENERATION_ID,
                "vector": vector.to_blob(),
                "at": discovered_at,
            },
        )
    return target_key


class FakeTagPort:
    """One active tag, no aliases, no exclusions. See ``test_publish_cas.py`` for why a fake."""

    def __init__(self) -> None:
        self.current = TagConfigVersion(
            id=TCV1,
            sequence=1,
            content_hash="sha256:" + "1" * 64,
            payload={
                "tags": [{"id": TAG_ID, "text": "protein folding", "similarity_threshold": None}],
                "tag_aliases": [],
                "tag_exclusions": [],
            },
            created_at="2026-09-01T02:00:00.000Z",
        )
        self.frozen: dict[str, TagConfigVersion] = {}

    def add_tag(self, tag_id: str, tag_text: str) -> None:
        """Publish a new config version carrying one more tag.

        Adding a subscription is the whole premise of the backfill entitlement (D28): items
        already past the coverage pointer never matched the new tag, so without a widening
        they are unreachable forever.
        """
        payload = json.loads(json.dumps(self.current.payload))
        payload["tags"].append({"id": tag_id, "text": tag_text, "similarity_threshold": None})
        self.current = TagConfigVersion(
            id=TCV2,
            sequence=self.current.sequence + 1,
            content_hash="sha256:" + "2" * 64,
            payload=payload,
            created_at="2026-09-06T02:00:00.000Z",
        )

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion:
        return self.current

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion:
        return self.current

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion:
        self.frozen.setdefault(report_build_id, self.current)
        return self.frozen[report_build_id]


class RecordingDelivery:
    """A stand-in for ``delivery.create_intent`` that only counts.

    Counting is the assertion: REQ-D57's rule is "an empty period creates **no** intent", and
    the honest way to check it is that the port was never reached, not that some row is absent
    for an unrelated reason.
    """

    def __init__(self) -> None:
        self.calls: list[str] = []

    def create_report_intent(
        self, *, connection: Any, owner_id: str, report_id: str
    ) -> dict[str, Any]:
        self.calls.append(report_id)
        return {"intent_id": _ulid(), "delivery_id": None, "state": None, "created": True}


def context_for(engine: Engine, tag_port: FakeTagPort, delivery: Any = None) -> PublishContext:
    return PublishContext(
        engine=engine,
        tag_port=tag_port,
        embedding_port=EmbeddingService(
            engine,
            encoder=DeterministicHashEncoder(
                MODEL_NAME, MODEL_VERSION, DIMENSION, Normalization.L2
            ),
        ),
        delivery=delivery,
    )


def build(engine: Engine, tag_port: FakeTagPort, *, backfill_port: Any = None) -> BuildSnapshot:
    return build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id=str(uuid.uuid4()),
        tag_port=tag_port,
        embedding_port=EmbeddingService(
            engine,
            encoder=DeterministicHashEncoder(
                MODEL_NAME, MODEL_VERSION, DIMENSION, Normalization.L2
            ),
        ),
        settings=SelectionSettings(),
        backfill_port=backfill_port,
    )


def windows(engine: Engine) -> list[Any]:
    with engine.connect() as connection:
        return CoverageRepository().windows_in_order(connection, OWNER_ID)


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar() or 0)


# --- fixture d, read as data -------------------------------------------------------------------


@pytest.fixture(scope="module")
def fixture_d() -> dict[str, Any]:
    return json.loads((FIXTURES / "d-empty-period-coverage-only.json").read_text("utf-8"))


def test_fixture_d_pins_the_empty_period_shape(fixture_d: dict[str, Any]) -> None:
    """The fixture, not this file, is the authority on what an empty period leaves behind.

    Asserted against the file so that an edit to the oracle fails here rather than drifting
    silently: ``abort_reason='empty_period'`` on a row that is **not** published, exactly one
    coverage window with ``report_id IS NULL``, and zero intents.
    """
    expected = fixture_d["expected"]
    report_row = expected["rows"]["report"][0]
    assert report_row["status"] == "aborted"
    assert report_row["abort_reason"] == "empty_period"
    assert report_row["published_at"] is None
    assert expected["counts"]["coverage_window[report_id IS NULL]"] == 1
    assert expected["counts"]["outbox_intent added by event 2"] == 0
    empty_window = expected["rows"]["coverage_window"][0]
    assert empty_window["ingest_sequence_from"] == empty_window["ingest_sequence_to"]
    assert empty_window["report_id"] is None


# --- the three period shapes -------------------------------------------------------------------


def test_a_period_with_content_advances_coverage(engine: Engine) -> None:
    seed_tag_vector(engine)
    seed_matching_work(
        engine, "01JWRK01000000000000000000", sequence=1, discovered_at="2026-09-06T01:00:00.000Z"
    )
    tag_port = FakeTagPort()
    delivery = RecordingDelivery()
    context = context_for(engine, tag_port, delivery)

    snapshot = build(engine, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)
    result = publish_report(context, snapshot)

    assert result.published
    assert len(windows(engine)) == 1
    assert contiguity_violations(windows(engine)) == []
    assert delivery.calls == [result.report_id]


def test_an_empty_period_writes_coverage_but_no_report_and_no_intent(engine: Engine) -> None:
    """``T-RP-07``, fixture ``d`` and AMD-B04, all at once.

    "Nothing matched" is a **valid** outcome and it still advances the pointer. The delivery
    port must not be touched (REQ-D57): a digest with nothing in it is worse than no message.
    """
    seed_tag_vector(engine)
    tag_port = FakeTagPort()
    delivery = RecordingDelivery()
    context = context_for(engine, tag_port, delivery)

    snapshot = build(engine, tag_port)
    assert snapshot.is_empty_period
    record_build(context, snapshot, caller_module=MOD_JOB)
    result = publish_report(context, snapshot)

    assert result.published is False
    assert result.abort_reason == "empty_period"
    assert delivery.calls == []
    assert count(engine, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 0
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE status = 'aborted'"
            " AND abort_reason = 'empty_period'",
        )
        == 1
    )
    ledger = windows(engine)
    assert len(ledger) == 1
    assert ledger[0].report_id is None
    assert ledger[0].spans_no_items
    # CHECK (window_to > window_from) still holds for a degenerate span (§4.3 rule 3).
    assert parse_timestamp_utc_ms(ledger[0].window_to) > parse_timestamp_utc_ms(
        ledger[0].window_from
    )


def test_replaying_an_empty_period_returns_the_receipt(engine: Engine) -> None:
    """Fixture ``d``'s negative oracle -- the reason §4.7.1 kept a ``report`` row.

    A second call with the same ``report_build_id`` creates no second window and does **not**
    answer ``CONFLICT``. That is only possible because the empty period left a receipt.
    """
    seed_tag_vector(engine)
    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())
    snapshot = build(engine, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)
    first = publish_report(context, snapshot)

    again = publish_report(context, snapshot)

    assert again.replayed is True
    assert again.report_id == first.report_id
    assert again.abort_reason == "empty_period"
    assert len(windows(engine)) == 1


def test_three_periods_with_an_empty_one_in_the_middle_have_no_gap(engine: Engine) -> None:
    """O-4.2 and ``empty_period_behaviour.oracle_vi``: A(content) -> B(empty) -> C(content).

    The assertion that matters is the *pair* across B: ``C.window_from == B.window_to`` and
    ``C.ingest_sequence_from == B.ingest_sequence_to``. An implementation that skipped the
    empty period would give ``C.window_from == A.window_to`` and silently drop the interval,
    which is fixture ``d``'s third forbidden effect.
    """
    seed_tag_vector(engine)
    tag_port = FakeTagPort()
    delivery = RecordingDelivery()
    context = context_for(engine, tag_port, delivery)

    seed_matching_work(
        engine, "01JWRK01000000000000000000", sequence=1, discovered_at="2026-09-06T01:00:00.000Z"
    )
    first = build(engine, tag_port)
    record_build(context, first, caller_module=MOD_JOB)
    publish_report(context, first)

    empty = build(engine, tag_port)
    assert empty.is_empty_period
    record_build(context, empty, caller_module=MOD_JOB)
    publish_report(context, empty)

    seed_matching_work(
        engine, "01JWRK03000000000000000000", sequence=2, discovered_at="2026-09-07T01:00:00.000Z"
    )
    third = build(engine, tag_port)
    record_build(context, third, caller_module=MOD_JOB)
    publish_report(context, third)

    ledger = windows(engine)
    assert [window.sequence for window in ledger] == [1, 2, 3]
    assert contiguity_violations(ledger) == []
    assert ledger[1].report_id is None
    assert ledger[2].window_from == ledger[1].window_to
    assert ledger[2].ingest_sequence_from == ledger[1].ingest_sequence_to
    # One digest for each non-empty period, none for the empty one.
    assert len(delivery.calls) == 2


def test_a_run_that_fell_short_cannot_become_a_successful_empty_period(engine: Engine) -> None:
    """§4.4: "Run thất bại thu thập KHÔNG tự biến thành một kỳ rỗng thành công."

    The caller says the run was incomplete; an empty selection is then a ``builder_failure``,
    not a valid empty period, and coverage does **not** advance.
    """
    seed_tag_vector(engine)
    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())
    snapshot = build(engine, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)

    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot, empty_period_allowed=False)

    assert caught.value.code is ErrorCode.VALIDATION_ERROR
    assert windows(engine) == []
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE status = 'aborted'"
            " AND abort_reason = 'builder_failure'",
        )
        == 1
    )


# --- E2: the write is refused mid-transaction ---------------------------------------------------


def test_a_refused_write_advances_nothing_and_consumes_no_backfill(engine: Engine) -> None:
    """AMD-B04 / O-6.3 / SC22, with the fault injected rather than a real full disk.

    The publish transaction is opened and then refused, so the interesting question is what
    survives. The answer has to be: nothing. No coverage row (the pointer must not move,
    §4.4), no ``report_item``, and -- the one the contract calls out by name -- the backfill
    entitlement is still unconsumed, because "the builder crashed" is never a reason to burn a
    once-per-lifetime entitlement.
    """
    seed_tag_vector(engine)
    seed_matching_work(
        engine, "01JWRK01000000000000000000", sequence=1, discovered_at="2026-09-06T01:00:00.000Z"
    )
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO backfill_ledger (id, owner_id, tag_id, activation_sequence,"
                " subscription_identity_hash, entitlement, entitlement_reason, backfill_days,"
                " consumed_in_report_id, consumed_at)"
                " VALUES (:id, :owner, :tag, 1, :hash, 'granted', NULL, 7, NULL, NULL)"
            ),
            {"id": _ulid(), "owner": OWNER_ID, "tag": TAG_ID, "hash": "a" * 64},
        )

    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())
    snapshot = build(engine, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)

    injector = WriteFaultInjector(engine)
    with injector.disk_full(), pytest.raises(ReportError) as caught:
        publish_report(context, snapshot)

    assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert windows(engine) == []
    assert count(engine, "SELECT COUNT(*) FROM report_item") == 0
    assert count(engine, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 0
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM backfill_ledger WHERE consumed_in_report_id IS NOT NULL",
        )
        == 0
    )


def test_the_period_after_a_refused_write_is_still_contiguous(engine: Engine) -> None:
    """The recovery half of the previous test: the same data is reconsidered, not lost.

    §4.4's promise is that an aborted build leaves the pointer where it was, so the next build
    covers the same interval. Asserting only "nothing was written" would also pass for an
    implementation that dropped the items on the floor.
    """
    seed_tag_vector(engine)
    seed_matching_work(
        engine, "01JWRK01000000000000000000", sequence=1, discovered_at="2026-09-06T01:00:00.000Z"
    )
    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())

    failing = build(engine, tag_port)
    record_build(context, failing, caller_module=MOD_JOB)
    injector = WriteFaultInjector(engine)
    with injector.disk_full(), pytest.raises(ReportError):
        publish_report(context, failing)

    retried = build(engine, tag_port)
    record_build(context, retried, caller_module=MOD_JOB)
    result = publish_report(context, retried)

    assert result.published
    ledger = windows(engine)
    assert len(ledger) == 1
    assert ledger[0].sequence == 1
    assert ledger[0].predecessor_window_id is None
    assert contiguity_violations(ledger) == []
    assert count(engine, "SELECT COUNT(*) FROM report_item") == 1


def test_the_ledger_never_has_two_bootstrap_windows(engine: Engine) -> None:
    """O-4.1's third clause, enforced by ``ux_coverage_window_bootstrap``.

    SQLite treats NULLs as distinct in a UNIQUE index, so the contract's
    ``UNIQUE(owner_id, predecessor_window_id)`` alone would let two first windows exist. The
    partial index closes that, and this test is the reason it is not merely defensive.
    """
    seed_tag_vector(engine)
    seed_matching_work(
        engine, "01JWRK01000000000000000000", sequence=1, discovered_at="2026-09-06T01:00:00.000Z"
    )
    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())
    snapshot = build(engine, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)
    publish_report(context, snapshot)

    with pytest.raises(Exception) as caught, engine.begin() as connection:  # noqa: B017, PT011
        connection.execute(
            text(
                "INSERT INTO coverage_window (id, owner_id, sequence, window_from, window_to,"
                " ingest_sequence_from, ingest_sequence_to, predecessor_window_id, report_id,"
                " advanced_at) VALUES (:id, :owner, 99, '2026-09-01T00:00:00.000Z',"
                " '2026-09-02T00:00:00.000Z', 0, 1, NULL, NULL, '2026-09-02T00:00:00.000Z')"
            ),
            {"id": _ulid(), "owner": OWNER_ID},
        )
    assert "UNIQUE constraint failed" in str(caught.value)
    assert len([window for window in windows(engine) if window.predecessor_window_id is None]) == 1


# --- §6.3/§6.4: the widening, and the one entitlement it spends ---------------------------------


def seed_late_tag_vector(engine: Engine) -> None:
    """The subject vector of the newly added tag, at the pinned generation.

    Seeded because §5.3 refuses a selection whose tag set has a subject with no vector in the
    active generation -- and refusing is right: a silently skipped tag reads as "nothing
    matched", which is the failure the guard exists to prevent.

    ``seed_matching_work(matches=False)`` puts the old item's label at ``(0, 1)``; this tag
    sits there too, so the item matches the new tag and only the new tag.
    """
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, 'tag', :subject, :generation, :vector)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "subject": TAG_ID_LATE,
                "generation": GENERATION_ID,
                "vector": unit(0.0, 1.0).to_blob(),
            },
        )


def seed_backfill_entitlement(engine: Engine, tag_id: str, *, days: int = 7) -> str:
    """A ``granted`` row plus the ``reporting.backfill_days`` setting it is read against.

    The setting is seeded rather than defaulted: ``TC-backfill-pending-ledger`` §10 ``SG-03``
    forbids a code-side default for N, so an unconfigured deployment must fail loudly instead
    of quietly reaching seven days back. This test therefore has to configure it, which is the
    point.
    """
    ledger_id = _ulid()
    with engine.begin() as connection:
        connection.execute(
            text(
                'INSERT INTO settings (id, owner_id, "key", value_json, updated_at)'
                " VALUES (:id, :owner, 'reporting.backfill_days', :value, :at)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "value": str(days),
                "at": "2026-09-06T01:30:00.000Z",
            },
        )
        connection.execute(
            text(
                "INSERT INTO backfill_ledger (id, owner_id, tag_id, activation_sequence,"
                " subscription_identity_hash, entitlement, entitlement_reason, backfill_days,"
                " consumed_in_report_id, consumed_at)"
                " VALUES (:id, :owner, :tag, 1, :hash, 'granted', NULL, :days, NULL, NULL)"
            ),
            {
                "id": ledger_id,
                "owner": OWNER_ID,
                "tag": tag_id,
                "hash": "b" * 64,
                "days": days,
            },
        )
    return ledger_id


def test_an_entitled_tag_reaches_back_once_and_the_entitlement_is_spent_at_publish(
    engine: Engine,
) -> None:
    """``CR-TC-BACKFILL-05`` closed: §6.3 widens the candidate set, §6.4 spends the row.

    The scenario is the one D28 exists for, and it cannot be shortened. An item is ingested,
    the pointer passes it without selecting it (no tag matched at the time), and only *then*
    does the owner add the tag. On the sequence axis that item is gone: it belongs to a window
    already closed, so no later period's membership predicate can reach it. The entitlement is
    the one mechanism that can, and it may fire once, ever.

    Four things are asserted, and the second and third are the ones a wrong implementation
    passes without:

    1. the old item **is** in the new report -- the widening actually happened;
    2. it is there **exactly once** -- unioned, not appended, so a target that is also inside
       the window does not become two rows;
    3. the report says *why* -- ``selected_via_backfill`` with the ledger id, which is what
       lets a reader ask why an item older than the period is present, and which
       ``report.schema.json`` requires whenever the flag is true;
    4. the entitlement is ``consumed`` and points at this report -- written by
       ``publisher._consume_backfill`` inside ``TXN-report-publish``, never by the builder,
       because §6.4 condition 1 is the COMMIT.
    """
    seed_tag_vector(engine)
    # Ingested first, discovered five days before the period that will reach back for it.
    old_target = seed_matching_work(
        engine,
        "01JWRKOLD0000000000000000",
        sequence=1,
        discovered_at="2026-09-01T00:00:00.000Z",
        matches=False,
    )
    seed_matching_work(
        engine, "01JWRK02000000000000000000", sequence=2, discovered_at="2026-09-06T01:00:00.000Z"
    )

    tag_port = FakeTagPort()
    delivery = RecordingDelivery()
    context = context_for(engine, tag_port, delivery)

    # Period 1: the pointer passes the old item without selecting it.
    first = build(engine, tag_port)
    record_build(context, first, caller_module=MOD_JOB)
    first_result = publish_report(context, first)
    assert first_result.published
    assert [item.candidate.target_key for item in first.items] == [
        "work:01JWRK02000000000000000000"
    ]

    # The owner adds a tag that the old item *does* match, and is granted one backfill.
    seed_late_tag_vector(engine)
    tag_port.add_tag(TAG_ID_LATE, "structural biology")
    ledger_id = seed_backfill_entitlement(engine, TAG_ID_LATE)

    # Period 2: on the sequence axis it is empty; only the widening can find anything.
    without_backfill = build(engine, tag_port)
    assert (
        without_backfill.is_empty_period
    ), "the old item is past the pointer, so a build with no backfill port must find nothing"

    second = build(engine, tag_port, backfill_port=ServiceBackfill())
    selected = [item.candidate.target_key for item in second.items]

    assert selected.count(old_target) == 1, selected
    assert selected == [old_target]
    item = second.items[0]
    assert item.candidate.selected_via_backfill is True
    assert item.candidate.backfill_ledger_id == ledger_id
    assert second.backfill_ledger_ids_applied == (ledger_id,)
    assert second.coverage_note["backfill_applied_tag_ids"] == [TAG_ID_LATE]

    with engine.connect() as connection:
        assert (
            consumed_count(connection, owner_id=OWNER_ID) == 0
        ), "the builder must not spend the entitlement; only the publish COMMIT may"

    record_build(context, second, caller_module=MOD_JOB)
    result = publish_report(context, second)
    assert result.published

    with engine.connect() as connection:
        assert consumed_count(connection, owner_id=OWNER_ID) == 1
        row = (
            connection.execute(
                text(
                    "SELECT entitlement, consumed_in_report_id, consumed_at FROM backfill_ledger"
                    " WHERE id = :id"
                ),
                {"id": ledger_id},
            )
            .mappings()
            .one()
        )
    assert row["entitlement"] == "consumed"
    assert row["consumed_in_report_id"] == result.report_id
    assert row["consumed_at"] is not None

    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report_item WHERE report_id = :r AND target_key = :k",
            r=result.report_id,
            k=old_target,
        )
        == 1
    ), "the entitled item must appear exactly once"
    assert result.read_model is not None
    assert result.read_model["coverage_note"]["backfill_applied_tag_ids"] == [TAG_ID_LATE]


def test_a_widening_that_finds_nothing_does_not_spend_the_entitlement(engine: Engine) -> None:
    """§6.4 condition 3, fixture ``k``'s ``variant_empty_extension``.

    Re-reading an empty range costs no AI, so there is nothing to pay for. Without this the
    previous test would also pass for an implementation that spends the entitlement the moment
    a widening is *planned* -- burning a once-per-lifetime grant on a no-op.

    Period 1 is an **empty** period, so the pointer advances over a store with no targets in
    it at all; the seven days period 2 may reach back over are therefore genuinely empty.
    """
    seed_tag_vector(engine)
    tag_port = FakeTagPort()
    context = context_for(engine, tag_port, RecordingDelivery())
    first = build(engine, tag_port)
    assert first.is_empty_period
    record_build(context, first, caller_module=MOD_JOB)
    publish_report(context, first)

    seed_late_tag_vector(engine)
    tag_port.add_tag(TAG_ID_LATE, "structural biology")
    seed_backfill_entitlement(engine, TAG_ID_LATE)

    second = build(engine, tag_port, backfill_port=ServiceBackfill())
    assert second.backfill_ledger_ids_applied == ()
    assert second.coverage_note["backfill_applied_tag_ids"] == []
    with engine.connect() as connection:
        assert consumed_count(connection, owner_id=OWNER_ID) == 0
