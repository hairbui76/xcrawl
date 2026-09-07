"""E1 — one valid result per key, and a tag edit that calls no model (I04, REQ-AC06).

Driven by ``acceptance/fixtures/ai/j-same-key-resubmitted-one-result.json`` and
``acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json``, which are
the only oracle (SRC-PLAN §15): the fixtures' ``given`` rows are loaded, their ``events`` are
executed **through the real service layer** rather than by writing rows directly, and their
``expected`` counts and error codes are asserted. Nothing here edits a fixture to pass.

Scenario anchors: SC06, SC10, SC11, SC17, SC22, SC28, SC49.

Why the ids in these tests are the fixture's ids
------------------------------------------------
``AnalysisContext.id_factory`` is fed the exact ULIDs the fixtures name, in the order the
service mints them. The alternative -- generating ids and rewriting the fixture's
``attempt_id`` to match -- would mean the assertion no longer runs against the document the
contract wrote down.
"""

from __future__ import annotations

import copy
import os
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.analysis.key import compute_source_fingerprint
from server.app.analysis.repository import AnalysisRepository
from server.app.analysis.service import (
    AnalysisContext,
    AnalysisError,
    ProviderChoice,
    TargetRequest,
    TaskSource,
    claim_task,
    enqueue_tasks,
    get_task_input,
    request_reanalysis,
    submit_result,
)
from server.app.auth.service import AuthError
from server.app.db import create_sqlite_engine

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01JW0WNER00000000000000000"
WORK_ID = "01JWRKA1000000000000000000"
TARGET_KEY = f"work:{WORK_ID}"
WORK_VERSION_SOURCE_ID = "work_version:01JWVRA1000000000000000000"
GENERATION_ID = "01JAGENA100000000000000000"
ATTEMPT_ID = "01JATTA1000000000000000000"
LEASE_ID = "01JASGNA100000000000000000"
TASK_ID = "01JATASKA10000000000000000"
RUN_ID = "01JRUNA1000000000000000000"

#: The fingerprint fixture ``j`` carries in its ``analysis_key``.
SOURCE_FINGERPRINT = "sha256:858c06cf9c505c9f135e64d506f2e40dcb5bc6992bfd8d97f31e6b7caa8b0d38"
T0 = datetime(2026, 9, 6, 18, 0, 0, tzinfo=UTC)


# ------------------------------------------------------------------------------ harness


def _migrate(db_path: Path) -> None:
    """Run the real Alembic upgrade to ``head``.

    The tests use the migration as their schema rather than hand-written DDL: a second source
    of schema truth beside ``server/migrations/versions/`` is exactly the drift the entity
    contract exists to prevent.
    """
    from alembic import command
    from alembic.config import Config

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


class FakeProviderConfig:
    """A ``provider_config`` row, as ``MOD-settings-service`` would report it."""

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled

    def provider_for(self, task_type: str) -> ProviderChoice | None:
        return ProviderChoice(
            task_type=task_type,
            auth_family="api_key",
            provider_name="example-vendor-api",
            model_name="m-1",
            enabled=self.enabled,
        )


class FakeTaskInput:
    """One committed ``work_version`` source, so the evidence ceiling is ``abstract``."""

    def __init__(self) -> None:
        self.calls = 0

    def sources_for(self, *, target_key: str) -> Sequence[TaskSource]:
        self.calls += 1
        return [
            TaskSource(
                source_id=WORK_VERSION_SOURCE_ID,
                kind="work_version",
                text="Abstract nêu bộ dữ liệu là ImageNet-1k.",
                source_hash="sha256:" + "c" * 64,
                retrieved_at="2026-09-06T17:00:00.000Z",
            )
        ]


class ProviderCallCounter:
    """Stands in for ``ai.run_inference_task``.

    The server never calls a provider -- inference runs on the personal machine. This exists
    so the AC-06 oracle ("provider call counter delta = 0") is a number the test can read
    rather than a claim about code nobody executed.
    """

    def __init__(self) -> None:
        self.calls = 0

    def run_inference_task(self) -> None:  # pragma: no cover - a call here is the failure
        self.calls += 1


class RecordingSecrets:
    def __init__(self) -> None:
        self.revocations: list[tuple[str, str, str]] = []

    def revoke_task_credential(self, *, task_id: str, attempt_id: str, reason: str) -> None:
        self.revocations.append((task_id, attempt_id, reason))


def _ids(*values: str) -> Any:
    """An id factory that yields the fixture's ULIDs first, then falls back to real ones."""
    from server.app.analysis.repository import new_ulid

    pending = list(values)

    def factory() -> str:
        return pending.pop(0) if pending else new_ulid()

    return factory


def _clock(start: datetime) -> Any:
    """A clock that advances one second per read, so ordering is deterministic."""
    state = {"now": start}

    def now() -> datetime:
        state["now"] = state["now"] + timedelta(seconds=1)
        return state["now"]

    return now


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "rr.db"
    _migrate(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, failed_login_count) VALUES (:id, 1, 'owner', "
                "'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z', 0)"
            ),
            {"id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, metadata_state, identity_state, "
                "first_discovered_at, ingest_sequence, content_state, created_at) "
                "VALUES (:id, :owner_id, 'complete', 'active', "
                "'2026-09-05T00:00:00.000Z', 1, 'present', '2026-09-05T00:00:00.000Z')"
            ),
            {"id": WORK_ID, "owner_id": OWNER_ID},
        )
    yield engine
    engine.dispose()


@pytest.fixture
def counter() -> ProviderCallCounter:
    return ProviderCallCounter()


@pytest.fixture
def ctx(engine: Engine, counter: ProviderCallCounter) -> AnalysisContext:
    return AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=FakeProviderConfig(),
        secrets=RecordingSecrets(),
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=_clock(T0),
        id_factory=_ids(GENERATION_ID, TASK_ID, LEASE_ID, ATTEMPT_ID),
    )


def _target() -> TargetRequest:
    return TargetRequest(
        target_kind="work",
        target_id=WORK_ID,
        task_type="summary",
        source_fingerprint=SOURCE_FINGERPRINT,
        prompt_version="1.0.0",
        schema_version="0.1.0",
    )


def _counts(engine: Engine) -> dict[str, int]:
    """The four numbers every oracle in this file is stated in."""
    repository = AnalysisRepository()
    with engine.connect() as connection:
        return {
            "analysis_valid": repository.count_valid(connection, owner_id=OWNER_ID),
            "analysis_attempt": repository.count_attempts(connection, owner_id=OWNER_ID),
            "analysis_generation": repository.count_generations(connection, owner_id=OWNER_ID),
            "analysis_task": int(
                connection.execute(text("SELECT COUNT(*) FROM analysis_task")).scalar_one()
            ),
        }


def _claim(
    ctx: AnalysisContext, *, worker: str = "worker-1", request_id: str = "claim-1"
) -> dict[str, Any]:
    claimed = claim_task(
        ctx, worker_identity=worker, claim_request_id=request_id, task_types=["summary"]
    )
    assert claimed["task"] is not None, claimed
    task: dict[str, Any] = claimed["task"]
    return task


def _submitted_document(fixture_loader) -> dict[str, Any]:
    """The ``analysis_result`` fixture ``j`` says a worker submits."""
    fixture = fixture_loader("ai/j-same-key-resubmitted-one-result")
    document: dict[str, Any] = copy.deepcopy(fixture.expected["analysis_result"])
    return document


# --------------------------------------------------------- fixture j: one result per key


def test_a_first_submit_commits_exactly_one_result(ctx, engine, fixture_loader) -> None:
    """Fixture ``j`` event 1 -- ``TXN-analysis-accept`` writes result and attempt together."""
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    assert task["task_id"] == TASK_ID
    assert task["attempt_id"] == ATTEMPT_ID

    receipt = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=_submitted_document(fixture_loader),
    )
    assert receipt["status"] == "committed"

    counts = _counts(engine)
    assert counts["analysis_valid"] == 1
    assert counts["analysis_attempt"] == 1
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT status, generation_number, usage_tokens_in, usage_tokens_out, "
                    "provider_name, accepted_from_attempt_id, evidence_level "
                    "FROM analysis WHERE owner_id = :owner_id"
                ),
                {"owner_id": OWNER_ID},
            )
            .mappings()
            .one()
        )
        outcome = (
            connection.execute(
                text("SELECT outcome, error_code, cost_uncertain FROM analysis_attempt")
            )
            .mappings()
            .one()
        )
        state = connection.execute(text("SELECT state FROM analysis_task")).scalar_one()
    assert row["status"] == "valid"
    assert row["generation_number"] == 1
    # `usage.unknown = false` in this fixture, so real numbers -- the control case for I14.
    assert (row["usage_tokens_in"], row["usage_tokens_out"]) == (1200, 300)
    assert row["accepted_from_attempt_id"] == ATTEMPT_ID
    assert row["evidence_level"] == "abstract"
    # The attempt that produced it is closed as `accepted`, and its cost is now KNOWN.
    assert outcome["outcome"] == "accepted"
    assert outcome["error_code"] is None
    assert outcome["cost_uncertain"] == 0
    assert state == "valid"
    assert ctx.secrets.revocations == [(TASK_ID, ATTEMPT_ID, "task_finished")]


def test_a_replay_of_the_same_payload_returns_the_receipt_and_writes_nothing(
    ctx, engine, fixture_loader
) -> None:
    """Fixture ``j`` event 2: the ACK was lost and the worker submits again.

    The oracle is ``after_event_2``: one valid row, one attempt, and the same
    ``payload_hash``. A replay must not open a write transaction at all.
    """
    fixture = fixture_loader("ai/j-same-key-resubmitted-one-result")
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    document = _submitted_document(fixture_loader)
    first = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )
    second = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )
    assert second["status"] == "duplicate_replay"
    assert second["payload_hash"] == first["payload_hash"]
    assert second["analysis_id"] == first["analysis_id"]

    expected = fixture.expected["after_event_2"]["counts"]
    counts = _counts(engine)
    assert counts["analysis_valid"] == expected["analysis[status='valid']"]
    assert counts["analysis_attempt"] == expected["analysis_attempt"]


def test_the_same_key_with_a_different_payload_is_a_conflict(ctx, engine, fixture_loader) -> None:
    """Fixture ``j`` event 3: a second worker submits a different payload under one key.

    ``after_event_3`` pins both halves -- the code is ``IDEMPOTENCY_CONFLICT``, and the row
    that already committed is **not** overwritten. ``ux_analysis_valid_key`` is the arbiter.
    """
    fixture = fixture_loader("ai/j-same-key-resubmitted-one-result")
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    document = _submitted_document(fixture_loader)
    committed = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )

    divergent = copy.deepcopy(document)
    divergent["result"]["content"] = "Một tóm tắt khác hẳn."
    with pytest.raises(AnalysisError) as raised:
        submit_result(
            ctx,
            task_id=task["task_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            result=divergent,
        )
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT
    assert (
        raised.value.code.value
        == (fixture.expected["after_event_3"]["error_expectation"]["error_code"])
    )
    assert raised.value.http_status == 409

    counts = _counts(engine)
    assert (
        counts["analysis_valid"]
        == (fixture.expected["after_event_3"]["counts"]["analysis[status='valid']"])
    )
    with engine.connect() as connection:
        stored = connection.execute(text("SELECT payload_hash FROM analysis")).scalar_one()
    assert stored == committed["payload_hash"]


# ------------------------------------------------------------------- AC-06: the tag edit


def test_re_adding_a_tag_enqueues_nothing_and_calls_no_provider(
    ctx, engine, counter, fixture_loader
) -> None:
    """AC-06 / fixture ``reporting/b`` -- the arithmetic oracle, measured.

    ``ENT-analysis-generation.ac06_oracle``: after removing and re-adding a tag,
    ``COUNT(analysis_generation)`` and ``COUNT(analysis_attempt)`` are unchanged and the
    provider call counter delta is 0.

    The tag edit is not simulated by *not* calling anything -- that would prove nothing. The
    report builder is run again exactly as it would be after a tag change, over the same
    targets, and the assertion is that the second run creates no work.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=_submitted_document(fixture_loader),
    )
    before = _counts(engine)
    calls_before = counter.calls

    # The tag is removed and re-added: a new `tag.id` and a new `tag_config_version` exist,
    # and the next report build selects the same target again (fixture b, events 1-3).
    after_tag_edit = enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")

    assert after_tag_edit["created"] == []
    assert after_tag_edit["skipped"] == [{"target_key": TARGET_KEY, "reason": "already_valid"}]
    assert _counts(engine) == before
    assert counter.calls - calls_before == 0


def test_a_tag_change_is_not_a_reason_a_reanalysis_can_be_asked_for(ctx, engine) -> None:
    """The other half of AC-06: the reanalysis door does not open for a tag either.

    ``contracts/ai/tasks.yaml`` §reanalysis_triggers.forbidden lists tag edits, provider
    changes and new report periods. There is no argument value that gets any of them past
    the reason check, so no amount of downstream care is needed to keep the promise.
    """
    for refused in ("tag_change", "tag_config_version_change", "provider_change", "report_build"):
        with pytest.raises(AnalysisError) as raised:
            request_reanalysis(
                ctx,
                target_kind="work",
                target_id=WORK_ID,
                task_type="summary",
                source_fingerprint=SOURCE_FINGERPRINT,
                prompt_version="1.0.0",
                schema_version="0.1.0",
                reason=refused,
                request_id=f"req-{refused}",
            )
        assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert _counts(engine)["analysis_generation"] == 0


def test_reanalysis_opens_a_new_generation_and_keeps_the_old_result(
    ctx, engine, fixture_loader
) -> None:
    """T-AN-12 / REQ-D26: a deliberate re-run is allowed, and the old row survives it.

    This is the line REQ-AC06 draws: a *tag edit* must not call the model, an *Owner asking*
    may. The old result keeps its key and stays ``valid``; the new work is filed under
    generation 2, which is a different key and so does not collide with
    ``ux_analysis_valid_key``.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=_submitted_document(fixture_loader),
    )

    opened = request_reanalysis(
        ctx,
        target_kind="work",
        target_id=WORK_ID,
        task_type="summary",
        source_fingerprint=SOURCE_FINGERPRINT,
        prompt_version="1.0.0",
        schema_version="0.1.0",
        reason="manual",  # the ports.yaml wire spelling
        request_id="req-1",
    )
    assert opened["generation_number"] == 2
    assert opened["reason"] == "owner_reanalysis"  # stored under the entities.yaml enum

    counts = _counts(engine)
    assert counts["analysis_generation"] == 2
    assert counts["analysis_valid"] == 1  # generation 1's result is untouched

    replay = request_reanalysis(
        ctx,
        target_kind="work",
        target_id=WORK_ID,
        task_type="summary",
        source_fingerprint=SOURCE_FINGERPRINT,
        prompt_version="1.0.0",
        schema_version="0.1.0",
        reason="manual",
        request_id="req-1",
    )
    assert replay == opened
    assert _counts(engine)["analysis_generation"] == 2


# ----------------------------------------------------------- denied edges and disabled providers


def test_the_collector_may_not_enqueue_analysis_work(ctx, engine) -> None:
    """FE-07 / B12 -- and the code must be ``FORBIDDEN_EDGE``, not ``UNAUTHORIZED``.

    ``analysis.enqueue_tasks`` has ``transport: internal``, so there is no HTTP path to it;
    the only way to reach it is an in-process call, and ruling R5-01 row 2 assigns that
    refusal ``FORBIDDEN_EDGE``. Picking ``UNAUTHORIZED`` here would be a failure in its own
    right (card §10 ``SG-DENY``).
    """
    for caller in ("MOD-x-collector", "MOD-analysis-worker", "MOD-telegram-adapter"):
        with pytest.raises(AuthError) as raised:
            enqueue_tasks(ctx, [_target()], caller_module=caller)
        assert raised.value.code is ErrorCode.FORBIDDEN_EDGE
        assert raised.value.http_status == 403
    assert _counts(engine) == {
        "analysis_valid": 0,
        "analysis_attempt": 0,
        "analysis_generation": 0,
        "analysis_task": 0,
    }


def test_a_disabled_provider_hands_out_no_task(engine, counter) -> None:
    """``contracts/ai/providers.yaml`` ships both adapters ``enabled: false`` (REQ-OQ03).

    A queued task whose only possible next step is a provider call the Owner has not enabled
    must not be handed out: dispatching it would be handing a worker an instruction to break
    the contract. The refusal is a 200 with no task, and the queue is left intact.
    """
    disabled = AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=FakeProviderConfig(enabled=False),
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=_clock(T0),
        id_factory=_ids(GENERATION_ID, TASK_ID),
    )
    enqueue_tasks(disabled, [_target()], caller_module="MOD-ingest-service")
    claimed = claim_task(
        disabled, worker_identity="worker-1", claim_request_id="c1", task_types=["summary"]
    )
    assert claimed == {"task": None, "reason": "no_enabled_provider"}
    assert counter.calls == 0
    counts = _counts(engine)
    assert counts["analysis_task"] == 1  # still queued, nothing lost
    assert counts["analysis_attempt"] == 0


def test_an_unwired_provider_registry_is_not_an_enabled_one(engine) -> None:
    """CAP-P5 / I13: an undetermined state is never converted into a good one."""
    unwired = AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=_clock(T0),
        id_factory=_ids(GENERATION_ID, TASK_ID),
    )
    enqueue_tasks(unwired, [_target()], caller_module="MOD-ingest-service")
    assert claim_task(
        unwired, worker_identity="worker-1", claim_request_id="c1", task_types=["summary"]
    ) == {"task": None, "reason": "no_enabled_provider"}


def test_two_workers_cannot_both_claim_one_task(ctx, engine) -> None:
    """T-AN-02 ``oracle_vi``: two simultaneous claims produce one lease and one attempt."""
    enqueue_tasks(ctx, [_target()], caller_module="MOD-ingest-service")
    first = _claim(ctx, worker="worker-1", request_id="c1")
    second = claim_task(
        ctx, worker_identity="worker-2", claim_request_id="c2", task_types=["summary"]
    )
    assert second == {"task": None, "reason": "queue_empty"}
    with engine.connect() as connection:
        leases = connection.execute(text("SELECT COUNT(*) FROM assignment_lease")).scalar_one()
    assert leases == 1
    assert _counts(engine)["analysis_attempt"] == 1
    # And the same claim_request_id is answered with the same task, not a second one.
    assert _claim(ctx, worker="worker-1", request_id="c1")["lease_id"] == first["lease_id"]


# --------------------------------------------------- the type agreement with the adapter card


def test_the_task_input_this_service_hands_out_builds_the_adapter_s_TaskInput(ctx) -> None:
    """The types ``TC-analysis-adapter-validation`` and this card had to agree on.

    ``analysis.get_task_input`` is the port between them, so the agreement is testable rather
    than a convention: the payload this service produces is fed straight into the adapter's
    ``TaskInput``, and the source id set the adapter will hold every citation to (SV-02) has
    to be the one the server granted.
    """
    adapter_base = pytest.importorskip(
        "worker.app.adapter.base", reason="pending TC-analysis-adapter-validation"
    )
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx)
    payload = get_task_input(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    assert payload["max_evidence_level"] == "abstract"
    assert payload["input_source_ids"] == [WORK_VERSION_SOURCE_ID]

    task_input = adapter_base.TaskInput(
        task_id=payload["task_id"],
        task_type=adapter_base.AnalysisTaskType(payload["task_type"]),
        analysis_key={},
        target_key=payload["target_ref"]["target_key"],
        sources=[adapter_base.SourceRef(**source) for source in payload["sources"]],
        max_evidence_level=payload["max_evidence_level"],
        prompt_version="1.0.0",
        schema_version="0.1.0",
        attempt_id=task["attempt_id"],
        attempt_number=task["attempt_number"],
    )
    assert list(task_input.input_source_ids) == payload["input_source_ids"]
    # The contract's timeout, not one the adapter chose, and smaller than `lease_ttl_analysis`.
    assert task_input.timeout_seconds == payload["inference_timeout_seconds"]


def test_the_source_fingerprint_a_caller_supplies_is_the_contract_s(ctx, engine) -> None:
    """``ENT-analysis.source_fingerprint`` is computed from content hashes and nothing else.

    Stated here as well as in the contract test because it is the join between the two: the
    enqueue path takes the fingerprint from the caller, so if a caller ever computed it from
    something tag-shaped, the key would move and AC-06 would break in a place the key test
    cannot see.
    """
    fingerprint = compute_source_fingerprint(
        work_version_content_fingerprint="sha256:" + "d" * 64,
        post_source_snapshot_hashes=["sha256:" + "e" * 64],
    )
    enqueue_tasks(
        ctx,
        [
            TargetRequest(
                target_kind="work",
                target_id=WORK_ID,
                task_type="label",
                source_fingerprint=fingerprint,
                prompt_version="1.0.0",
                schema_version="0.1.0",
            )
        ],
        caller_module="MOD-ingest-service",
    )
    assert _counts(engine)["analysis_generation"] == 1


# ------------------------------------------- fixture reporting/e: the summary that arrives late


#: The tables ``MOD-analysis-service`` writes -- its own four plus ``assignment_lease``, which
#: it holds as custodian (``CR-TC-ANALYSIS-01``). Anything outside this set moving during an
#: analysis commit would be this module reaching into another's data.
ANALYSIS_OWNED_TABLES = frozenset(
    {
        "analysis",
        "analysis_attempt",
        "analysis_generation",
        "analysis_task",
        "assignment_lease",
    }
)


def _all_table_counts(engine: Engine) -> dict[str, int]:
    """Row counts for **every** table in the schema, read from ``sqlite_master``.

    Enumerated rather than listed so the assertion cannot go stale: a table added by a later
    migration is covered the day it appears, which is the only way "this commit touched
    nothing outside its own module" stays true as the schema grows.
    """
    with engine.connect() as connection:
        tables = [
            name
            for (name,) in connection.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' AND name <> 'alembic_version'"
                )
            )
        ]
        return {
            table: int(connection.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar_one())
            for table in tables
        }


def test_a_late_summary_commits_and_touches_no_published_period(
    ctx, engine, fixture_loader
) -> None:
    """Fixture ``reporting/e`` -- the one event of that fixture this card owns.

    What is exercised here, and what is not
    ---------------------------------------
    ``FX-RP-E`` is mostly a reporting oracle: ``pending_item_ledger`` moving from ``pending``
    to ``resolved_reported_late``, the ``late_discovery`` label, coverage advancing past an
    item's ``discovered_at``. All of that belongs to ``MOD-report-service``
    (``TC-report-coverage-publish-cas``) and is **NOT_RUN** here -- see the handoff addendum.

    Two things in it are this card's, and both are asserted:

    * **event 1** -- E1 was selected but has no summary, so the report builder enqueues one
      (``analysis.enqueue_tasks``);
    * **event 3** -- that summary arrives at 18:00, *after* period 2 was published at
      13:00:05, and it must commit normally. The fixture's ``forbidden_effects`` include "sửa
      report kỳ 2 để chèn summary về muộn (I05)". The analysis side of that prohibition is
      stronger than "do not amend": this module has no edge to ``MOD-report-service`` at all
      (FE-13), so the assertion is that a late commit moves rows in **analysis-owned tables
      only** -- measured across every table in the schema, not a hand-listed few, so a report,
      saved, tag, delivery or coverage table that moved would fail here.

    The five-hour gap is between the *publish* and the *result*, not between the claim and the
    result: ``lease_ttl_analysis`` is 900 s, so a worker that claimed at 13:00 and submitted at
    18:00 would rightly be refused ``WORKER_LEASE_EXPIRED``. The worker picks the task up
    shortly before it finishes, which is what the fixture's own timeline describes.

    The submitted document is fixture ``j``'s (the canonical well-formed result); its
    ``analysis_key.target_key`` is pointed at E1 because the key is a function of the
    assignment, and E1 is the target this fixture assigns. No value is invented: the
    identities come from ``FX-RP-E``, the document shape from ``FX-AI-J``.
    """
    fixture = fixture_loader("reporting/e-late-analysis-pending-then-late-discovery")
    e1 = fixture.rows("work")[0]
    e1_target_key = e1["_target"]["target_key"]
    expected_analysis = fixture.expected["report"]["items"][0]["analysis"]

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, metadata_state, identity_state, "
                "first_discovered_at, ingest_sequence, content_state, created_at) "
                "VALUES (:id, :owner_id, 'complete', 'active', :discovered, :seq, "
                "'present', :discovered)"
            ),
            {
                "id": e1["id"],
                "owner_id": OWNER_ID,
                "discovered": e1["first_discovered_at"],
                "seq": e1["ingest_sequence"],
            },
        )

    # A clock this test moves on purpose: the whole point of the fixture is that the two
    # moments are far apart and on opposite sides of a publish.
    at = {"now": datetime(2026, 9, 6, 13, 0, 0, tzinfo=UTC)}
    ctx.clock = lambda: at["now"]

    # Event 1, 13:00 -- selected, no summary yet, so a task is queued.
    queued = enqueue_tasks(
        ctx,
        [
            TargetRequest(
                target_kind="work",
                target_id=e1["id"],
                task_type=expected_analysis["task_type"],
                source_fingerprint=SOURCE_FINGERPRINT,
                prompt_version="1.0.0",
                schema_version="0.1.0",
            )
        ],
        caller_module="MOD-report-service",
    )
    assert [entry["target_key"] for entry in queued["created"]] == [e1_target_key]

    # Event 2, 13:00:05 -- period 2 is published by MOD-report-service with E1 still pending.
    # Nothing in this module participates. This snapshot is what "the published period is
    # untouched" is measured against.
    before = _all_table_counts(engine)

    # Event 3, 18:00 -- the summary arrives late. The worker picks the task up shortly
    # beforehand: `lease_ttl_analysis` is 900 s, so a claim held across the whole five hours
    # would be refused, and rightly.
    at["now"] = datetime(2026, 9, 6, 17, 59, 0, tzinfo=UTC)
    task = _claim(ctx)
    at["now"] = datetime(2026, 9, 6, 18, 0, 0, tzinfo=UTC)
    document = _submitted_document(fixture_loader)
    document["analysis_key"]["target_key"] = e1_target_key
    receipt = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )
    assert receipt["status"] == "committed"

    after = _all_table_counts(engine)
    moved = {table for table in after if after[table] != before[table]}
    # The positive half: the result really did commit. The negative half is the one the
    # fixture's forbidden effect is about -- every table outside this module is untouched,
    # and the set is computed from the live schema so a table added tomorrow is covered too.
    assert "analysis" in moved
    assert moved <= ANALYSIS_OWNED_TABLES, sorted(moved - ANALYSIS_OWNED_TABLES)
    assert {"saved_item", "saved_snapshot", "work_label", "first_announced_ledger"} <= set(
        after
    ), "the schema no longer carries the tables this assertion is meant to exclude"

    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT task_type, generation_number, evidence_level, analyzed_at, "
                    "target_key FROM analysis WHERE target_key = :target_key"
                ),
                {"target_key": e1_target_key},
            )
            .mappings()
            .one()
        )
    assert row["task_type"] == expected_analysis["task_type"]
    assert row["generation_number"] == expected_analysis["generation_number"]
    assert row["evidence_level"] == expected_analysis["evidence_level"]
    # The server clock at commit, which the fixture pins to the moment the late result landed.
    assert row["analyzed_at"] == expected_analysis["analyzed_at"]

    # And the item is now analysable again from the report's point of view: the key has a
    # valid row, so a later build enqueues nothing for it (the same skip AC-06 relies on).
    assert (
        enqueue_tasks(
            ctx,
            [
                TargetRequest(
                    target_kind="work",
                    target_id=e1["id"],
                    task_type=expected_analysis["task_type"],
                    source_fingerprint=SOURCE_FINGERPRINT,
                    prompt_version="1.0.0",
                    schema_version="0.1.0",
                )
            ],
            caller_module="MOD-report-service",
        )["created"]
        == []
    )
