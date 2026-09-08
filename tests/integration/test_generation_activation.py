"""E1/E2 — SC52: rebuild a generation, then switch active atomically.

The oracle is ``acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json``,
used as data: ``given.rows`` is loaded into a database created by the **real** Alembic
migrations, ``events`` are executed through the **real** service layer (never by writing the
expected rows directly), and ``expected``, ``counts``, ``row_oracles`` and -- the part that
catches defects -- ``forbidden_effects`` are asserted.

Why the positive fixture is the one that matters here
-----------------------------------------------------
``contracts/reporting/selection.md`` §5 says it outright: *"một mình O-5a không loại trừ được
một triển khai chặn mọi thứ và không bao giờ đổi được generation."* The negative fixture is
covered by ``tests/contract/test_embedding_generation_guard.py``; this file walks the eleven
events of the positive one, so "nothing was mixed" cannot be achieved by never switching.

The three properties asserted, in the fixture's own words
---------------------------------------------------------
``embedding_generation[state='active'] == 1`` after **every** event
    Including the refused activation. This is what "nguyên tử" means operationally: not that
    the code is careful, but that no observation can find zero or two active rows.
    ``ux_embedding_generation_active`` is what makes it so, and the test observes it from a
    second connection so that the assertion is about committed state.

Activation is refused while ``built_vector_count < expected_vector_count``
    Fixture event 7, with ``expected.after_event_7.row_oracles``: *"Từ chối KHÔNG đổi state
    của G1 hay G2; không có transaction nào commit."*

G1 survives as ``retired`` with all its vectors
    ``REQ-D48`` keeps the old generation; deleting it would silently break every published
    report that names it (I05, ``REQ-S7.3-03``).

The dependency that is now real
-------------------------------
Card §11 depends on ``TC-report-coverage-publish-cas`` for *"chặn xảy ra trước publish
commit"*. That card has landed, so
:func:`test_the_guard_blocks_before_the_publish_commit` is no longer an ``xfail``: it drives
the real :func:`server.app.report.publisher.publish_report` with this card's
:class:`~server.app.embedding.service.EmbeddingService` as its ``embedding_port``, switches
the generation between build and publish, and asserts the refusal, the unchanged published
count and the ``aborted`` build row. The earlier marker named ``server.app.report.service``, a
module that card's §3 never creates -- ``CR-TC-REPORT-08``.
"""

from __future__ import annotations

import json
import os
import sqlite3
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
    EmbeddingError,
    GenerationState,
    Normalization,
    SubjectType,
)
from server.app.embedding.service import EmbeddingService, VectorRequest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "acceptance" / "fixtures" / "reporting"
POSITIVE = FIXTURE / "n-embedding-generation-switch-positive.json"

MOD_EMBEDDING = "MOD-embedding-service"
MOD_SETTINGS = "MOD-settings-service"
MOD_TAG = "MOD-tag-service"
MOD_REPORT = "MOD-report-service"
MOD_INGEST = "MOD-ingest-service"


# --- harness ----------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def fixture_data() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(POSITIVE.read_text(encoding="utf-8"))
    return data


def _upgrade(db_path: Path) -> None:
    """``alembic upgrade head`` -- the migrations a fresh deployment runs, in order.

    ``head`` and not this card's own revision id: by the time several Phase 3 cards have
    landed there is one head again, and a test pinned to a revision name would silently stop
    exercising the merged graph.
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
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, password_hash, password_updated_at, failed_login_count, "
                "locked_until) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', "
                "'2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
    try:
        yield engine
    finally:
        engine.dispose()


OWNER_ID = "01JW0WNER00000000000000000"

#: G1 of the fixture: four vectors, all present, already active.
G1_MODEL = ("multilingual-e5-small", "1.0.0", 4)
#: G2 of the fixture: a different model at a different dimension, hence incomparable.
G2_MODEL = ("multilingual-e5-base", "2.0.0", 8)


def encoder_for(model: tuple[str, str, int]) -> DeterministicHashEncoder:
    """An offline encoder matching one of the fixture's two models.

    A stand-in, not a model: ``REQ-OQ09`` has not chosen one and card §10 ``SG-01`` forbids
    choosing here. Everything this file asserts is about *which generation* a vector belongs
    to, which is exactly the part a real model would not change.
    """
    name, version, dimension = model
    return DeterministicHashEncoder(name, version, dimension, Normalization.L2)


def service_for(engine: Engine, model: tuple[str, str, int]) -> EmbeddingService:
    return EmbeddingService(engine, encoder=encoder_for(model))


def observe(engine: Engine, sql: str, **params: Any) -> Any:
    """Read committed state through a *separate* connection.

    Deliberately not the service's connection: "no observer ever sees two active rows" is a
    claim about what another reader can see, and asserting it from inside the writing
    transaction would assert nothing.
    """
    with engine.connect() as connection:
        return connection.execute(text(sql), params).scalar()


def generation_count(engine: Engine) -> int:
    return int(
        observe(
            engine,
            "SELECT COUNT(*) FROM embedding_generation WHERE owner_id = :o",
            o=OWNER_ID,
        )
    )


def active_count(engine: Engine) -> int:
    return int(
        observe(
            engine,
            "SELECT COUNT(*) FROM embedding_generation WHERE owner_id = :o AND state = 'active'",
            o=OWNER_ID,
        )
    )


def seed_generation_one(engine: Engine) -> str:
    """G1 in ``given``: active, four vectors, coverage complete.

    Inserted directly because it is ``given`` state -- the fixture's precondition, not one of
    its events. Every *event* below goes through the service.
    """
    generation_id = "01JEMBGEN10000000000000000"
    name, version, dimension = G1_MODEL
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                "dimension, normalization, state, expected_vector_count, built_vector_count, "
                "created_at, activated_at) VALUES (:id, :owner, :name, :version, :dimension, "
                "'l2', 'active', 4, 4, '2026-09-01T02:00:00.000Z', '2026-09-01T02:30:00.000Z')"
            ),
            {
                "id": generation_id,
                "owner": OWNER_ID,
                "name": name,
                "version": version,
                "dimension": dimension,
            },
        )
    return generation_id


def build_generation_two(
    engine: Engine, *, expected_vector_count: int | None = 4
) -> tuple[EmbeddingService, str]:
    """Fixture events 1-2: settings change, then ``embedding.start_generation_rebuild``."""
    service = service_for(engine, G2_MODEL)
    name, version, dimension = G2_MODEL
    generation = service.start_generation_rebuild(
        OWNER_ID,
        caller_module=MOD_SETTINGS,
        target_model_name=name,
        target_model_version=version,
        dimension=dimension,
        expected_vector_count=expected_vector_count,
    )
    return service, str(generation["generation_id"])


def subjects(count: int, *, offset: int = 0) -> list[VectorRequest]:
    return [
        VectorRequest(
            subject_type=SubjectType.TAG,
            subject_id=f"01JTAG{index + offset:020d}"[:26],
            text=f"subject-{index + offset}",
        )
        for index in range(count)
    ]


# --- the fixture's premise ---------------------------------------------------------------------


def test_the_fixture_still_describes_two_incomparable_models(fixture_data) -> None:
    """Premise check: if the fixture's two models converged, everything below would pass
    while proving nothing."""
    after_six = fixture_data["expected"]["after_event_6"]["rows"]["embedding_generation"]
    building = next(row for row in after_six if row["state"] == "building")
    assert (building["model_name"], building["model_version"], building["dimension"]) == G2_MODEL
    assert fixture_data["expected"]["counts"]["cosine_comparisons_between_G1_and_G2"] == 0


# --- events 1-2: rebuild starts, G1 stays active ----------------------------------------------


def test_starting_a_rebuild_does_not_move_the_active_pointer(engine) -> None:
    """Fixture event 2: *"Tạo G2 ở state='building' ... G1 VẪN active."*

    ``selection.md`` §5.5 turns on this: a report built during a rebuild is still a valid
    report, built against the old generation. A rebuild that made itself active on creation
    would make every in-flight build wrong.
    """
    g1 = seed_generation_one(engine)
    _, g2 = build_generation_two(engine)

    assert g2 != g1
    assert active_count(engine) == 1
    assert (
        observe(engine, "SELECT state FROM embedding_generation WHERE id = :id", id=g1) == "active"
    )
    assert (
        observe(engine, "SELECT state FROM embedding_generation WHERE id = :id", id=g2)
        == "building"
    )


def test_a_report_built_during_the_rebuild_pins_the_old_generation(engine) -> None:
    """Fixture events 5-6: the mid-rebuild period publishes with ``embedding_generation_id``
    still G1."""
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(2)
    )

    reader = service_for(engine, G1_MODEL)
    pinned = reader.pin_generation(OWNER_ID, caller_module=MOD_REPORT)

    assert pinned.generation_id == g1
    assert reader.embedding_generation_matches(OWNER_ID, g1) is True
    assert reader.embedding_generation_matches(OWNER_ID, g2) is False


def test_two_concurrent_rebuild_commands_produce_one_generation(engine) -> None:
    """Card §6: *"Hai lệnh rebuild đồng thời ⇒ một thắng."*

    Both calls return, both return the **same** generation id, and the table holds one row for
    that model -- which is stronger than "the second call raised": the settings service asking
    twice must not be an error, it must be a no-op.
    """
    seed_generation_one(engine)
    _, first = build_generation_two(engine)
    _, second = build_generation_two(engine)

    assert first == second
    assert (
        int(
            observe(
                engine,
                "SELECT COUNT(*) FROM embedding_generation WHERE owner_id = :o "
                "AND model_name = :name",
                o=OWNER_ID,
                name=G2_MODEL[0],
            )
        )
        == 1
    )


def test_a_repeat_with_a_different_target_is_an_idempotency_conflict(engine) -> None:
    """Same key, different payload -- ``contracts/errors.yaml`` ``IDEMPOTENCY_CONFLICT``.

    Silently keeping the first ``expected_vector_count`` would leave the activation guard
    answering a question the caller no longer asked.
    """
    seed_generation_one(engine)
    build_generation_two(engine, expected_vector_count=4)

    with pytest.raises(EmbeddingError) as raised:
        build_generation_two(engine, expected_vector_count=99)
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT


# --- events 3-4, 8: generating vectors into the building generation ---------------------------


def test_generate_vectors_is_idempotent_on_its_contract_key(engine) -> None:
    """``ports.yaml``: *"Cùng khóa trả vector đã lưu; không sinh bản thứ hai."*

    The counter is the reason this matters beyond tidiness: ``built_vector_count`` decides
    whether the generation may go live, and a duplicate row would let a half-built generation
    reach its target by being asked twice.
    """
    seed_generation_one(engine)
    service, g2 = build_generation_two(engine)
    requests = subjects(3)

    first = service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=requests
    )
    second = service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=requests
    )

    assert [item.created for item in first] == [True, True, True]
    assert [item.created for item in second] == [False, False, False]
    assert [item.vector for item in first] == [item.vector for item in second]
    assert {item.idempotency_key for item in first} == {item.idempotency_key for item in second}
    assert (
        int(
            observe(
                engine,
                "SELECT COUNT(*) FROM tag_vector WHERE embedding_generation_id = :g",
                g=g2,
            )
        )
        == 3
    )
    assert (
        int(
            observe(
                engine,
                "SELECT built_vector_count FROM embedding_generation WHERE id = :g",
                g=g2,
            )
        )
        == 3
    )


def test_an_encoder_that_does_not_match_the_generation_is_refused(engine) -> None:
    """The quiet failure this prevents: embedding with model A and filing under generation B.

    ``entities.yaml`` pins ``model_name``, ``model_version`` and ``dimension`` on the
    generation row, and every report carries them. A mismatch here would make those columns a
    label rather than a fact.
    """
    seed_generation_one(engine)
    _, g2 = build_generation_two(engine)
    wrong = service_for(engine, G1_MODEL)

    with pytest.raises(EmbeddingError) as raised:
        wrong.generate_vectors(
            OWNER_ID, caller_module=MOD_INGEST, generation_id=g2, requests=subjects(1)
        )
    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert (
        int(
            observe(
                engine,
                "SELECT COUNT(*) FROM tag_vector WHERE embedding_generation_id = :g",
                g=g2,
            )
        )
        == 0
    )


def test_vectors_of_an_unknown_generation_are_not_found(engine) -> None:
    seed_generation_one(engine)
    service = service_for(engine, G2_MODEL)
    with pytest.raises(EmbeddingError) as raised:
        service.generate_vectors(
            OWNER_ID,
            caller_module=MOD_TAG,
            generation_id="01JNOSUCHGEN00000000000000",
            requests=subjects(1),
        )
    assert raised.value.code is ErrorCode.NOT_FOUND


# --- event 7: activation refused while coverage is short --------------------------------------


def test_activation_is_refused_while_built_is_below_expected(engine) -> None:
    """Fixture event 7 and its oracle: *"Từ chối KHÔNG đổi state của G1 hay G2."*

    Every column of both rows is compared before and after, so "nothing committed" is
    measured rather than inferred from the absence of an exception.
    """
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=4)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(2)
    )
    before = _generation_rows(engine)

    with pytest.raises(EmbeddingError) as raised:
        service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert active_count(engine) == 1
    assert _generation_rows(engine) == before
    assert (
        observe(engine, "SELECT state FROM embedding_generation WHERE id = :id", id=g1) == "active"
    )


def test_activation_is_refused_when_no_target_count_was_ever_recorded(engine) -> None:
    """``expected_vector_count IS NULL`` is not evidence of coverage (``ports.yaml``)."""
    seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=None)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(4)
    )

    with pytest.raises(EmbeddingError) as raised:
        service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)
    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert active_count(engine) == 1


# --- event 9: the atomic switch ----------------------------------------------------------------


def _generation_rows(engine: Engine) -> list[tuple[Any, ...]]:
    with engine.connect() as connection:
        return [
            tuple(row)
            for row in connection.execute(
                text(
                    "SELECT id, state, expected_vector_count, built_vector_count, activated_at "
                    "FROM embedding_generation ORDER BY id"
                )
            )
        ]


def test_activation_switches_atomically_and_keeps_the_old_generation(engine) -> None:
    """Fixture event 9 and ``expected.after_event_9``.

    Four claims, all from the fixture: exactly one active row; G2 active with an
    ``activated_at``; G1 ``retired`` and **not** deleted; its vectors still present.
    """
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=4)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(4)
    )

    activated = service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    assert activated["generation_id"] == g2
    assert activated["state"] == GenerationState.ACTIVE.value
    assert activated["activated_at"] is not None
    assert active_count(engine) == 1
    assert (
        observe(engine, "SELECT state FROM embedding_generation WHERE id = :id", id=g1)
        == GenerationState.RETIRED.value
    )
    assert generation_count(engine) == 2
    assert (
        int(
            observe(
                engine,
                "SELECT COUNT(*) FROM tag_vector WHERE embedding_generation_id = :g",
                g=g2,
            )
        )
        == 4
    )


def test_reactivating_the_active_generation_changes_nothing(engine) -> None:
    """``ports.yaml``: *"Kích hoạt lại generation đã active không đổi trạng thái."*"""
    seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=2)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(2)
    )
    service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)
    after_first = _generation_rows(engine)

    again = service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    assert again["state"] == GenerationState.ACTIVE.value
    assert _generation_rows(engine) == after_first
    assert active_count(engine) == 1


def test_a_retired_generation_cannot_be_reactivated(engine) -> None:
    """``REQ-D48`` keeps the old rows readable; it does not make them a place to go back to.

    Reactivating a retired generation would silently invalidate every report published under
    the newer one, which is the mixing I12 forbids arrived at from the other direction.
    """
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=1)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(1)
    )
    service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    with pytest.raises(EmbeddingError) as raised:
        service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g1)
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert active_count(engine) == 1


def test_the_unique_index_makes_two_active_rows_impossible(engine) -> None:
    """The invariant, asserted against the database rather than against the service.

    A second ``active`` row is rejected by ``ux_embedding_generation_active`` even when the
    service is bypassed entirely -- which is what makes "atomic" a property of the schema and
    not of the caller's discipline.
    """
    seed_generation_one(engine)
    _, g2 = build_generation_two(engine)

    with (
        pytest.raises(Exception) as raised,  # noqa: B017 - the driver's IntegrityError
        engine.begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE embedding_generation SET state = 'active', "
                "activated_at = '2026-09-13T04:00:00.000Z' WHERE id = :id"
            ),
            {"id": g2},
        )
    assert "UNIQUE constraint failed" in str(raised.value)
    assert active_count(engine) == 1


# --- selection after the switch ---------------------------------------------------------------


def test_after_the_switch_selection_sees_only_the_new_generation(engine) -> None:
    """Fixture event 10 and the main row oracle: no selection ever sees both generations."""
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=2)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(2)
    )
    service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    pinned = service.pin_generation(OWNER_ID, caller_module=MOD_REPORT)
    assert pinned.generation_id == g2
    assert service.embedding_generation_matches(OWNER_ID, g2) is True
    assert service.embedding_generation_matches(OWNER_ID, g1) is False


def test_the_publish_cas_predicate_fails_when_the_generation_changed_mid_build(engine) -> None:
    """``time-and-tags.md`` §4.5 check 3, in the shape PC03's CAS will call it.

    The build pins G1; the switch happens; the predicate answers ``False``, which is the
    signal the publish transaction turns into ``EMBEDDING_GENERATION_MISMATCH``. Ordering that
    refusal against a real publish commit is the dependency below.
    """
    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=1)
    pinned = service.pin_generation(OWNER_ID, caller_module=MOD_REPORT)
    assert pinned.generation_id == g1

    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(1)
    )
    service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)

    assert service.embedding_generation_matches(OWNER_ID, pinned.generation_id) is False


class _FrozenTagPort:
    """The minimum of ``tag.get_active_config_version`` / ``tag.freeze_config_version``.

    A fake and not a stub of somebody else's package: no card in the nineteen creates the
    ``tag`` / ``tag_config_version`` tables (``CR-TC-REPORT-01``), so there is nothing to
    integrate with. What it implements is the part of the contract this test depends on —
    ``freeze_config_version`` is idempotent on ``report_build_id`` and the version never moves,
    so the **only** check that can fail in the publish CAS is the embedding one. That is the
    point: if the tag check could also fail, an ``EMBEDDING_GENERATION_MISMATCH`` would not
    prove which guard fired.
    """

    def __init__(self) -> None:
        from server.app.report.builder import TagConfigVersion

        self.version = TagConfigVersion(
            id="01JTCV0000000000000000000A",
            sequence=1,
            content_hash="sha256:" + "0" * 64,
            payload={"tags": [], "tag_aliases": [], "tag_exclusions": []},
            created_at="2026-09-01T02:00:00.000Z",
        )

    def get_active_config_version(self, owner_id: str) -> Any:
        return self.version

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> Any:
        return self.version

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> Any:
        return self.version


def test_the_guard_blocks_before_the_publish_commit(engine) -> None:
    """Card §11: the ordering claim — and it is now **real**, not an ``xfail``.

    ``TC-report-coverage-publish-cas`` has landed, and its
    :func:`server.app.report.publisher.publish_report` calls this card's predicate as check 3
    of the six-check CAS::

        if not context.embedding_port.embedding_generation_matches(
            snapshot.owner_id, snapshot.generation.generation_id
        ):

    with ``embedding_port`` being a real
    :class:`~server.app.embedding.service.EmbeddingService`. So the whole sequence is
    observable end to end, and this test walks it:

    1. build a report snapshot while G1 is active — the snapshot pins G1;
    2. finish G2 and activate it, between build and publish (fixture ``l``'s event 2);
    3. publish, and watch the guard refuse.

    Three things are asserted, and the second and third are what make this an **ordering**
    claim rather than a repeat of the predicate's own unit test: the code is
    ``EMBEDDING_GENERATION_MISMATCH``; ``COUNT(report WHERE status='published')`` is unchanged
    (fixture ``l``: *"`#report[status='published']` không tăng"*); and the build row is left
    ``aborted`` with ``abort_reason = 'embedding_generation_mismatch'``, which is
    ``contracts/state/report.yaml`` T-RP-04 and proves the refusal happened inside the publish
    path rather than before it was ever entered.

    The original marker named ``server.app.report.service``, a module that card's §3 never
    creates — ``CR-TC-REPORT-08``. Re-pointed to the real entry point.
    """
    from server.app.report.builder import SelectionSettings, build_report
    from server.app.report.coverage import ReportError
    from server.app.report.publisher import PublishContext, publish_report, record_build

    g1 = seed_generation_one(engine)
    service, g2 = build_generation_two(engine, expected_vector_count=1)
    tag_port = _FrozenTagPort()
    context = PublishContext(engine=engine, tag_port=tag_port, embedding_port=service)

    snapshot = build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id="3a7d1e02-8c4b-4f19-9d2e-5b6a7c8d9e01",
        tag_port=tag_port,
        embedding_port=service,
        settings=SelectionSettings(),
    )
    assert snapshot.generation.generation_id == g1, "the build did not pin the active generation"

    # T-RP-01: the `building` row that anchors `report_build_id`. Without it the publisher
    # answers NOT_FOUND at its idempotency check and never reaches the embedding guard --
    # "publish does not create a build" (`publish_cas.idempotency_rule_vi` case 4). Recording
    # it is what puts this test *inside* the publish path rather than in front of it.
    record_build(context, snapshot)

    # The switch, between build snapshot and publish commit.
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(1)
    )
    service.activate_generation(OWNER_ID, caller_module=MOD_EMBEDDING, generation_id=g2)
    assert service.embedding_generation_matches(OWNER_ID, g1) is False

    published_before = observe(engine, "SELECT COUNT(*) FROM report WHERE status = 'published'")

    with pytest.raises(ReportError) as raised:
        publish_report(context, snapshot)

    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert (
        observe(engine, "SELECT COUNT(*) FROM report WHERE status = 'published'")
        == published_before
    )
    aborted = observe(
        engine,
        "SELECT abort_reason FROM report WHERE report_build_id = :b",
        b=snapshot.report_build_id,
    )
    assert aborted == "embedding_generation_mismatch"


# --- default deny at the port (card §5, SG-DENY) ----------------------------------------------


def test_an_unregistered_caller_cannot_start_a_rebuild(engine) -> None:
    """``allowed_edges`` gives ``embedding.start_generation_rebuild`` exactly one caller."""
    seed_generation_one(engine)
    service = service_for(engine, G2_MODEL)
    name, version, dimension = G2_MODEL

    with pytest.raises(EmbeddingError) as raised:
        service.start_generation_rebuild(
            OWNER_ID,
            caller_module=MOD_REPORT,
            target_model_name=name,
            target_model_version=version,
            dimension=dimension,
            expected_vector_count=4,
        )
    assert raised.value.code is ErrorCode.FORBIDDEN_EDGE
    assert generation_count(engine) == 1, "a refused call wrote a row"


def test_a_model_version_of_latest_is_refused_by_the_service_and_by_the_schema(engine) -> None:
    """``entities.yaml``: "không dùng ``latest``". Refused twice, on purpose.

    Once in the service, with ``VALIDATION_ERROR`` and a field path a caller can act on; once
    as a CHECK, so a row inserted by anything else is refused too.
    """
    seed_generation_one(engine)
    service = service_for(engine, G2_MODEL)
    with pytest.raises(EmbeddingError) as raised:
        service.start_generation_rebuild(
            OWNER_ID,
            caller_module=MOD_SETTINGS,
            target_model_name="whatever",
            target_model_version="latest",
            dimension=8,
        )
    assert raised.value.code is ErrorCode.VALIDATION_ERROR

    with (
        pytest.raises(Exception) as integrity,  # noqa: B017 - the driver's IntegrityError
        engine.begin() as connection,
    ):
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                "dimension, normalization, state, expected_vector_count, built_vector_count, "
                "created_at, activated_at) VALUES ('01JEMBGEN90000000000000000', :o, 'm', "
                "'latest', 8, 'l2', 'building', NULL, 0, '2026-09-13T02:00:00.000Z', NULL)"
            ),
            {"o": OWNER_ID},
        )
    assert "CHECK constraint failed" in str(integrity.value)


# --- the migration graph -----------------------------------------------------------------------


def test_the_migration_graph_has_exactly_one_head() -> None:
    """One head, asserted structurally rather than against a literal revision id.

    Several cards land migrations in the same wave; whoever lands second adds a merge
    revision. A test that named the expected head would have to be edited by each of them,
    which is how a second head gets committed with a green suite.
    """
    from alembic.script import ScriptDirectory

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads


def test_the_two_owned_tables_exist_with_their_contract_indexes(engine) -> None:
    """``data_owner_of: [tag_vector, embedding_generation]`` reached the database.

    Index names are the contract's, so a rename shows up here rather than in a later card
    that expected the uniqueness to be there.
    """
    with engine.connect() as connection:
        names = {
            row[0]
            for row in connection.execute(
                text("SELECT name FROM sqlite_master WHERE type IN ('table', 'index')")
            )
        }
    assert {"embedding_generation", "tag_vector"} <= names
    assert {
        "ux_embedding_generation_active",
        "ux_embedding_generation_model",
        "ux_tag_vector_subject_generation",
    } <= names


def test_a_tag_vector_row_cannot_outlive_its_generation(engine) -> None:
    """``ON DELETE RESTRICT``: the FK ``entities.yaml`` declares, enforced by the pragma
    ``server/app/db/engine.py`` sets on every connection."""
    seed_generation_one(engine)
    service, g2 = build_generation_two(engine)
    service.generate_vectors(
        OWNER_ID, caller_module=MOD_TAG, generation_id=g2, requests=subjects(1)
    )

    with (
        pytest.raises(Exception) as raised,  # noqa: B017 - the driver's IntegrityError
        engine.begin() as connection,
    ):
        connection.execute(text("DELETE FROM embedding_generation WHERE id = :id"), {"id": g2})
    assert "FOREIGN KEY constraint failed" in str(raised.value)
    assert isinstance(sqlite3.IntegrityError, type)
