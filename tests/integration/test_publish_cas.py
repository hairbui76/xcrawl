"""E1/E2 -- SC08/SC05/SC24: two publishers, one predecessor, exactly one winner.

The oracle is ``acceptance/fixtures/reporting/g-concurrent-publishers-cas.json``, used as
data: ``given.rows`` seeds a database created by the **real** Alembic migrations, the six
``events`` run through the **real** service layer (never by writing the expected rows
directly), and ``expected.counts``, ``expected.row_oracles``, ``expected.error_expectation``
and -- the part that catches defects -- ``forbidden_effects`` are asserted.

Why the loser is the interesting half
--------------------------------------
"Exactly one window with predecessor ``P``" is easy to satisfy by never publishing twice. The
fixture's ``forbidden_effects`` are what make the test mean something: the loser must leave
**no** ``report_item`` row, must **not** consume backfill, must be told ``CONFLICT`` rather
than ``IDEMPOTENCY_CONFLICT``, and must rebuild rather than retry the same item set against a
new predecessor. Each of those is asserted below by counting rows, not by reading a log.

Three neighbouring refusals live here too, because they are the other five checks of the same
CAS: ``TAG_VERSION_STALE`` (check 2, fixture ``a``/``c``'s freeze point),
``EMBEDDING_GENERATION_MISMATCH`` (check 3), and the replay of a committed publish (the
idempotency rule ``publish_cas.idempotency_rule_vi`` case 1).

``test_the_generation_guard_blocks_before_the_publish_commit`` is this card's side of
``tests/integration/test_generation_activation.py``'s ``xfail``. That test imports
``server.app.report.service``, a module name this card's §3 does not create, so it stays
``xfail`` and ``CR-TC-REPORT-08`` asks for it to be re-pointed. The claim it makes is proven
here instead, against the real publish transaction.
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
from server.app.embedding.generation import (
    DeterministicHashEncoder,
    GenerationFingerprint,
    Normalization,
    Vector,
)
from server.app.embedding.service import EmbeddingService
from server.app.report.builder import (
    BuildSnapshot,
    SelectionSettings,
    TagConfigVersion,
    build_report,
)
from server.app.report.coverage import CoverageRepository, ReportError, contiguity_violations
from server.app.report.publisher import (
    PublishContext,
    publish_report,
    read_model,
    record_build,
    verify_content_hash,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "reporting"

OWNER_ID = "01JW0WNER00000000000000000"
GENERATION_ID = "01JEMBGEN10000000000000000"
MODEL_NAME = "multilingual-e5-small"
MODEL_VERSION = "1.0.0"
DIMENSION = 4
MOD_JOB = "MOD-job-service"
MOD_REPORT = "MOD-report-service"

FINGERPRINT = GenerationFingerprint(
    generation_id=GENERATION_ID,
    model_name=MODEL_NAME,
    model_version=MODEL_VERSION,
    dimension=DIMENSION,
    normalization=Normalization.L2,
)

TAG_ID = "01JTAGPFD00000000000000000"
TCV1 = "01JTCV10000000000000000000"
TCV2 = "01JTCV20000000000000000000"


# --- harness ----------------------------------------------------------------------------------


def _upgrade(db_path: Path) -> None:
    """``alembic upgrade head`` -- the migrations a fresh deployment runs, in order.

    ``head`` rather than this card's revision id: once the sibling cards of this wave land
    there is one head again, and a test pinned to a revision name would stop exercising the
    merged graph without saying so.
    """
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


def unit(x: float, y: float) -> Vector:
    """A unit vector in the first two components -- hand-checkable, like ``selection.md`` §8.7."""
    norm = (x * x + y * y) ** 0.5
    return Vector(fingerprint=FINGERPRINT, values=(x / norm, y / norm, 0.0, 0.0))


def seed_tag_vector(engine: Engine, subject_type: str, subject_id: str, vector: Vector) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, :type, :subject, :generation, :vector)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "type": subject_type,
                "subject": subject_id,
                "generation": GENERATION_ID,
                "vector": vector.to_blob(),
            },
        )


def seed_work(engine: Engine, work_id: str, *, sequence: int, discovered_at: str) -> str:
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
    return f"work:{work_id}"


def seed_summary(engine: Engine, target_key: str, work_id: str, *, at: str) -> str:
    analysis_id = _ulid()
    with engine.begin() as connection:
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
                "at": at,
            },
        )
    return analysis_id


def seed_label(
    engine: Engine, target_key: str, work_id: str, analysis_id: str, text_value: str, vector: Vector
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work_label (id, owner_id, target_kind, target_work_id,"
                " target_post_id, label_text, analysis_id, embedding_generation_id, vector,"
                " created_at) VALUES (:id, :owner, 'work', :work, NULL, :label, :analysis,"
                " :generation, :vector, '2026-09-06T01:30:00.000Z')"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "work": work_id,
                "label": text_value,
                "analysis": analysis_id,
                "generation": GENERATION_ID,
                "vector": vector.to_blob(),
            },
        )


def _ulid() -> str:
    from server.app.report.coverage import new_ulid

    return new_ulid()


class FakeTagPort:
    """``MOD-tag-service``'s two operations, plus the immutable-snapshot read.

    A fake and not a stub of somebody else's package: no card in the 19 creates the ``tag`` /
    ``tag_config_version`` tables (``CR-TC-REPORT-01``), so there is no real implementation to
    integrate with. What it does implement is the *contract*: ``freeze_config_version`` is
    idempotent on ``report_build_id`` (``ports.yaml``) and raises ``TAG_VERSION_STALE`` when
    the live version has moved on (§3.3 step 3), which is the behaviour the CAS depends on.
    """

    def __init__(self, version: TagConfigVersion) -> None:
        self.versions: dict[str, TagConfigVersion] = {version.id: version}
        self.current = version
        self.frozen: dict[str, TagConfigVersion] = {}

    def publish_new_version(self, version: TagConfigVersion) -> None:
        self.versions[version.id] = version
        self.current = version

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion:
        return self.current

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion:
        return self.versions[tag_config_version_id]

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion:
        if report_build_id in self.frozen:
            return self.frozen[report_build_id]
        if self.current.id != expected_tag_config_version_id:
            raise ReportError(
                ErrorCode.TAG_VERSION_STALE,
                details_safe={
                    "report_build_id": report_build_id,
                    "expected_tag_config_version_id": expected_tag_config_version_id,
                    "current_tag_config_version_id": self.current.id,
                    "rebuild_attempt": 1,
                },
            )
        self.frozen[report_build_id] = self.current
        return self.current


def tag_version(version_id: str, sequence: int) -> TagConfigVersion:
    return TagConfigVersion(
        id=version_id,
        sequence=sequence,
        content_hash="sha256:" + f"{sequence:064d}",
        payload={
            "tags": [{"id": TAG_ID, "text": "protein folding", "similarity_threshold": None}],
            "tag_aliases": [],
            "tag_exclusions": [],
        },
        created_at="2026-09-01T02:00:00.000Z",
    )


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


def build(engine: Engine, tag_port: FakeTagPort, *, build_id: str | None = None) -> BuildSnapshot:
    return build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id=build_id or str(uuid.uuid4()),
        tag_port=tag_port,
        embedding_port=context_for(engine, tag_port).embedding_port,
        settings=SelectionSettings(),
    )


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar() or 0)


@pytest.fixture
def seeded(engine: Engine) -> Engine:
    """One matching work, its summary and its label, plus the tag's own subject vector."""
    seed_tag_vector(engine, "tag", TAG_ID, unit(1.0, 0.0))
    work_id = "01JWRKB1000000000000000000"
    target_key = seed_work(engine, work_id, sequence=901, discovered_at="2026-09-06T01:00:04.000Z")
    analysis_id = seed_summary(engine, target_key, work_id, at="2026-09-06T01:30:00.000Z")
    seed_label(engine, target_key, work_id, analysis_id, "protein structure", unit(1.0, 0.05))
    return engine


# --- the fixture, as data ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def fixture_g() -> dict[str, Any]:
    return json.loads((FIXTURES / "g-concurrent-publishers-cas.json").read_text("utf-8"))


def test_fixture_g_pins_the_error_code_this_module_raises(fixture_g: dict[str, Any]) -> None:
    """The fixture's ``error_expectation`` is the contract; the code below must match it.

    Read from the file rather than restated, so that an edit to the fixture is a failing test
    here instead of a silent divergence. ``CONFLICT`` and not ``IDEMPOTENCY_CONFLICT``: the
    fixture spells out why -- "cùng key khác payload là chuyện khác".
    """
    expectation = fixture_g["expected"]["error_expectation"]
    assert expectation["operation"] == "report.publish"
    assert expectation["error_code"] == ErrorCode.CONFLICT.value


# --- SC08: two publishers, one predecessor ----------------------------------------------------


def test_two_publishers_on_one_predecessor_leave_exactly_one_window(seeded: Engine) -> None:
    """Fixture ``g`` events 1-4 and its ``counts``/``forbidden_effects``.

    Both builders read the same predecessor (here: none -- the bootstrap window), both try to
    commit, and the UNIQUE index decides. The loser is then checked against every one of the
    fixture's forbidden effects.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)

    snapshot_a = build(seeded, tag_port)
    snapshot_b = build(seeded, tag_port)
    record_build(context, snapshot_a, caller_module=MOD_JOB)
    record_build(context, snapshot_b, caller_module=MOD_JOB)

    result_a = publish_report(context, snapshot_a)
    assert result_a.published

    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot_b)

    assert caught.value.code is ErrorCode.CONFLICT
    assert caught.value.code is not ErrorCode.IDEMPOTENCY_CONFLICT
    assert count(seeded, "SELECT COUNT(*) FROM coverage_window") == 1
    assert count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 1
    assert (
        count(
            seeded,
            "SELECT COUNT(*) FROM report WHERE status = 'aborted'"
            " AND abort_reason = 'cas_conflict'",
        )
        == 1
    )
    # forbidden_effects: "Để lại report_item của bản dựng thất bại."
    assert (
        count(
            seeded,
            "SELECT COUNT(*) FROM report_item WHERE report_id ="
            " (SELECT id FROM report WHERE status = 'aborted')",
        )
        == 0
    )
    # forbidden_effects: "Tiêu thụ backfill trong bản dựng thất bại của B."
    assert (
        count(
            seeded,
            "SELECT COUNT(*) FROM backfill_ledger WHERE consumed_in_report_id IS NOT NULL",
        )
        == 0
    )


def test_the_loser_rebuilds_and_the_two_windows_are_contiguous(seeded: Engine) -> None:
    """Fixture ``g`` events 5-6: B re-reads the pointer, rebuilds, and chains after A.

    The rebuild is a **new** ``report_build_id``: ``forbidden_transitions`` makes
    ``aborted -> published`` impossible, so reviving the old build is not merely discouraged,
    it is refused. Contiguity is then asserted on both axes at once.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)

    snapshot_a = build(seeded, tag_port)
    snapshot_b = build(seeded, tag_port)
    record_build(context, snapshot_a, caller_module=MOD_JOB)
    record_build(context, snapshot_b, caller_module=MOD_JOB)
    publish_report(context, snapshot_a)
    with pytest.raises(ReportError):
        publish_report(context, snapshot_b)

    # A second work arrives, so the rebuilt period is not empty.
    work_id = "01JWRKB2000000000000000000"
    target_key = seed_work(seeded, work_id, sequence=902, discovered_at="2026-09-06T02:00:00.000Z")
    analysis_id = seed_summary(seeded, target_key, work_id, at="2026-09-06T02:30:00.000Z")
    seed_label(seeded, target_key, work_id, analysis_id, "protein folding", unit(1.0, 0.02))

    snapshot_b2 = build(seeded, tag_port)
    record_build(context, snapshot_b2, caller_module=MOD_JOB)
    result = publish_report(context, snapshot_b2)
    assert result.published

    with seeded.connect() as connection:
        windows = CoverageRepository().windows_in_order(connection, OWNER_ID)
    assert len(windows) == 2
    assert contiguity_violations(windows) == []
    assert windows[1].window_from == windows[0].window_to
    assert windows[1].ingest_sequence_from == windows[0].ingest_sequence_to


def test_reviving_an_aborted_build_is_refused(seeded: Engine) -> None:
    """``forbidden_transitions``: ``aborted -> published`` is ``CONFLICT``, always."""
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot_a = build(seeded, tag_port)
    snapshot_b = build(seeded, tag_port)
    record_build(context, snapshot_a, caller_module=MOD_JOB)
    record_build(context, snapshot_b, caller_module=MOD_JOB)
    publish_report(context, snapshot_a)
    with pytest.raises(ReportError):
        publish_report(context, snapshot_b)

    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot_b)
    assert caught.value.code is ErrorCode.CONFLICT


# --- the idempotency rule ---------------------------------------------------------------------


def test_replaying_a_committed_publish_returns_the_same_report(seeded: Engine) -> None:
    """``publish_cas.replay_oracle_vi``: nothing moves, and ``content_hash`` is unchanged.

    This is the lost-ACK case. A caller that timed out cannot know whether the commit
    happened, so it replays; the receipt (``ux_report_owner_build_id``) has to answer instead
    of a second coverage advance.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)
    first = publish_report(context, snapshot)

    windows_before = count(seeded, "SELECT COUNT(*) FROM coverage_window")
    again = publish_report(context, snapshot)

    assert again.replayed is True
    assert again.report_id == first.report_id
    assert again.content_hash == first.content_hash
    assert count(seeded, "SELECT COUNT(*) FROM coverage_window") == windows_before
    assert count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 1


def test_publishing_a_build_that_was_never_opened_is_not_found(seeded: Engine) -> None:
    """``idempotency_rule_vi`` case 4: publish does not create a build."""
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot)
    assert caught.value.code is ErrorCode.NOT_FOUND


# --- check 2: the tag freeze point (B01, SC05/SC19) --------------------------------------------


def test_a_tag_edit_between_build_and_cas_aborts_the_build(seeded: Engine) -> None:
    """§3.2 row 2: the version moved, so the build is abandoned rather than published mixed.

    The published set is unchanged and no coverage row appears -- §3.4's "abort does not create
    a coverage row", which is what stops a failed build from advancing the pointer.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)

    tag_port.publish_new_version(tag_version(TCV2, 2))

    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot)
    assert caught.value.code is ErrorCode.TAG_VERSION_STALE
    assert count(seeded, "SELECT COUNT(*) FROM coverage_window") == 0
    assert count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 0
    assert (
        count(
            seeded,
            "SELECT COUNT(*) FROM report WHERE status = 'aborted'"
            " AND abort_reason = 'tag_version_stale'",
        )
        == 1
    )


def test_a_published_report_keeps_its_hash_when_the_tag_set_changes(seeded: Engine) -> None:
    """Fixture ``c`` / O-3.2 / I05: publish, then edit tags, then re-read.

    The hash is recomputed from the stored rows, so this asserts the read path cannot re-derive
    content from today's tag set. That is the failure the assertion exists for: it would pass
    trivially if ``report.get`` returned a cached blob, and it is only meaningful because the
    read model is rebuilt each time.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)
    result = publish_report(context, snapshot)

    tag_port.publish_new_version(tag_version(TCV2, 2))

    with seeded.connect() as connection:
        body = read_model(connection, context, owner_id=OWNER_ID, report_id=result.report_id)
    assert body is not None
    assert body["content_hash"] == result.content_hash
    assert verify_content_hash(body) is True
    assert body["tag_config_version"]["tag_config_version_id"] == TCV1


# --- check 3: the embedding generation guard (SC24, I12) ---------------------------------------


def test_the_generation_guard_blocks_before_the_publish_commit(seeded: Engine) -> None:
    """T-RP-04 / ``CR-TC-REPORT-08``: this card's side of W3C's ordering claim.

    ``embedding.activate_generation`` switches the active generation after the build pinned
    the old one. The publish must refuse **before** committing anything: the published count
    does not move, and no coverage row appears.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)

    second = "01JEMBGEN20000000000000000"
    with seeded.begin() as connection:
        connection.execute(
            text("UPDATE embedding_generation SET state = 'retired' WHERE id = :id"),
            {"id": GENERATION_ID},
        )
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version,"
                " dimension, normalization, state, expected_vector_count, built_vector_count,"
                " created_at, activated_at) VALUES (:id, :owner, 'multilingual-e5-base',"
                " '2.0.0', 8, 'l2', 'active', 1, 1, '2026-09-06T12:00:00.000Z',"
                " '2026-09-06T12:30:00.000Z')"
            ),
            {"id": second, "owner": OWNER_ID},
        )

    published_before = count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'")
    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot)

    assert caught.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert (
        count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'") == published_before
    )
    assert count(seeded, "SELECT COUNT(*) FROM coverage_window") == 0
    assert (
        count(
            seeded,
            "SELECT COUNT(*) FROM report WHERE status = 'aborted'"
            " AND abort_reason = 'embedding_generation_mismatch'",
        )
        == 1
    )
    # No cosine was ever taken across the two generations -- the ledger of the *build*, which
    # is where selection happens, records zero cross-generation comparisons (I12).
    assert snapshot.comparison_ledger.cross_generation_performed == 0


# --- default deny (SG-DENY, FE-13) -------------------------------------------------------------


def test_the_analysis_worker_cannot_publish(seeded: Engine) -> None:
    """``FE-13``: a worker neither publishes nor decides that a work has been reported.

    ``FORBIDDEN_EDGE`` and not ``UNAUTHORIZED``: ``report.publish`` is ``transport: internal``,
    so there is no HTTP identity to reject -- the call is an in-process edge the registry does
    not have (ruling R5-01 row 2). Choosing the other code is a FAIL by card §10 ``SG-DENY``.
    """
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    record_build(context, snapshot, caller_module=MOD_JOB)

    with pytest.raises(ReportError) as caught:
        publish_report(context, snapshot, caller_module="MOD-analysis-worker")
    assert caught.value.code is ErrorCode.FORBIDDEN_EDGE
    assert caught.value.details_safe["forbidden_edge_ref"] == "FE-13"
    assert count(seeded, "SELECT COUNT(*) FROM report WHERE status = 'published'") == 0


def test_the_report_service_cannot_be_asked_to_build_by_itself(seeded: Engine) -> None:
    """``report.build``'s only caller is ``MOD-job-service`` (``allowed_edges``)."""
    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(seeded, tag_port)
    snapshot = build(seeded, tag_port)
    with pytest.raises(ReportError) as caught:
        record_build(context, snapshot, caller_module=MOD_REPORT)
    assert caught.value.code is ErrorCode.FORBIDDEN_EDGE


# --- F-A3-P4-01 / CR-TC-BACKFILL-09: a pending item is not announced yet -----------------------


def seed_label_only_analysis(engine: Engine, work_id: str, *, at: str) -> str:
    """A ``label`` analysis, so ``work_label.analysis_id`` resolves and no summary exists.

    ``work_label.analysis_id`` is NOT NULL, so a target cannot carry a label vector without
    *some* analysis row; but the summary is a different task type, and its absence is exactly
    the state fixture ``e`` is about. Seeding a ``label`` row keeps the two apart instead of
    faking a target with no labels at all, which would drop out of selection for the wrong
    reason.
    """
    analysis_id = _ulid()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                " target_work_id, target_post_id, task_type, source_fingerprint,"
                " prompt_version, schema_version, generation_number, status, payload,"
                " payload_hash, evidence_level, provider_name, model_name, usage_tokens_in,"
                " usage_tokens_out, analyzed_at, accepted_from_attempt_id, moved_by_merge_id)"
                " VALUES (:id, :owner, :gen, 'work', :work, NULL, 'label', 'fp', '1.0.0',"
                " '0.1.0', 1, 'valid', '{}', :hash, 'post_only', 'anthropic', 'm', NULL, NULL,"
                " :at, 'attempt', NULL)"
            ),
            {
                "id": analysis_id,
                "owner": OWNER_ID,
                "gen": _ulid(),
                "work": work_id,
                "hash": "sha256:" + "1" * 64,
                "at": at,
            },
        )
    return analysis_id


def announcements(engine: Engine, work_id: str) -> int:
    return count(
        engine,
        "SELECT COUNT(*) FROM first_announced_ledger WHERE owner_id = :o"
        "  AND canonical_work_id = :w AND superseded_by_merge_id IS NULL",
        o=OWNER_ID,
        w=work_id,
    )


def test_a_pending_item_is_not_announced_and_is_announced_once_when_its_summary_lands(
    engine: Engine,
) -> None:
    """``F-A3-P4-01`` / ``CR-TC-BACKFILL-09``, closed. Oracle: fixture ``e``'s row oracle.

    ``time-and-tags.md`` §5.3 promises that a late discovery *"chưa từng được công bố vẫn là
    ``new_discovery``"*, and §8.2 rule 2 is total: anything with an effective ledger row **must**
    be ``prior_reference``. Both can only hold if a still-pending item is not announced. Before
    the fix the publisher announced every ``new_discovery`` work, so the item came back in the
    next period as ``prior_reference`` — REQ-D29 / REQ-AC09 / I07 broken by one missing
    condition.

    The two halves are asserted separately on purpose. "Not announced while pending" alone
    would also pass for an implementation that never announces anything; "announced when the
    summary lands" alone would pass for the buggy one. Together they pin the transition.
    """
    seed_tag_vector(engine, "tag", TAG_ID, unit(1.0, 0.0))

    # E1: selected, label present, **no summary** -> summary_state 'pending'.
    pending_work = "01JWRKE1000000000000000000"
    pending_key = seed_work(
        engine, pending_work, sequence=901, discovered_at="2026-09-06T02:00:00.000Z"
    )
    label_analysis = seed_label_only_analysis(engine, pending_work, at="2026-09-06T02:05:00.000Z")
    seed_label(
        engine, pending_key, pending_work, label_analysis, "protein folding", unit(1.0, 0.02)
    )

    # E2: selected and complete, so period 1 has an item whose announcement must still happen.
    ready_work = "01JWRKE2000000000000000000"
    ready_key = seed_work(
        engine, ready_work, sequence=902, discovered_at="2026-09-06T02:00:01.000Z"
    )
    ready_analysis = seed_summary(engine, ready_key, ready_work, at="2026-09-06T02:30:00.000Z")
    seed_label(engine, ready_key, ready_work, ready_analysis, "protein structure", unit(1.0, 0.03))

    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(engine, tag_port)

    first = build(engine, tag_port)
    record_build(context, first, caller_module=MOD_JOB)
    first_result = publish_report(context, first)
    assert first_result.published
    assert first_result.quality == "partial", "an item without a summary makes the period partial"

    states = {item.candidate.target_key: item.summary_state for item in first.items}
    assert states == {pending_key: "pending", ready_key: "present"}
    # AMD-B17 / §7.3: the pending item is shown, not hidden.
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report_item WHERE report_id = :r",
            r=first_result.report_id,
        )
        == 2
    )

    # THE FIX: the complete item is announced, the pending one is not.
    assert announcements(engine, ready_work) == 1
    assert announcements(engine, pending_work) == 0
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM pending_item_ledger WHERE target_key = :k AND state = 'pending'",
            k=pending_key,
        )
        == 1
    )

    # The summary arrives late. Period 1 is untouched (I05).
    hash_before = first_result.content_hash
    seed_summary(engine, pending_key, pending_work, at="2026-09-06T18:00:00.000Z")

    second = build(engine, tag_port)
    record_build(context, second, caller_module=MOD_JOB)
    second_result = publish_report(context, second)
    assert second_result.published

    late = [item for item in second.items if item.candidate.target_key == pending_key]
    assert len(late) == 1
    # Fixture `e` row oracle: still `new_discovery`; "phát hiện muộn" is a display label.
    assert late[0].item_type == "new_discovery"
    assert late[0].summary_state == "present"
    assert late[0].candidate.from_pending is True

    assert announcements(engine, pending_work) == 1, "announced exactly once, and only now"
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM pending_item_ledger WHERE target_key = :k"
            "  AND state = 'resolved_reported_late'",
            k=pending_key,
        )
        == 1
    )
    assert count(engine, "SELECT COUNT(*) FROM pending_item_ledger") == 1, "no row is ever deleted"
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE id = :r AND content_hash = :h",
            r=first_result.report_id,
            h=hash_before,
        )
        == 1
    ), "period 1 was not rewritten when the late summary landed (I05)"


def test_an_item_that_stays_pending_across_two_periods_is_still_not_announced(
    engine: Engine,
) -> None:
    """The counter-case: waiting is not a timeout that eventually announces anyway.

    Without this, a fix that merely *delayed* the announcement by one period would pass the
    test above. The condition is the summary, not the wait.
    """
    seed_tag_vector(engine, "tag", TAG_ID, unit(1.0, 0.0))
    pending_work = "01JWRKE1000000000000000000"
    pending_key = seed_work(
        engine, pending_work, sequence=901, discovered_at="2026-09-06T02:00:00.000Z"
    )
    label_analysis = seed_label_only_analysis(engine, pending_work, at="2026-09-06T02:05:00.000Z")
    seed_label(
        engine, pending_key, pending_work, label_analysis, "protein folding", unit(1.0, 0.02)
    )

    tag_port = FakeTagPort(tag_version(TCV1, 1))
    context = context_for(engine, tag_port)

    for _ in range(2):
        snapshot = build(engine, tag_port)
        record_build(context, snapshot, caller_module=MOD_JOB)
        result = publish_report(context, snapshot)
        assert result.published
        assert result.quality == "partial"

    assert announcements(engine, pending_work) == 0
    assert count(engine, "SELECT COUNT(*) FROM first_announced_ledger") == 0
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM pending_item_ledger WHERE target_key = :k AND state = 'pending'",
            k=pending_key,
        )
        == 1
    )
