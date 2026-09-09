"""E1 — the analysis worker loop against the real server, in one process.

Gap **G-7b** of `…/packets/WIRING-wave-1.md`: the adapter could refuse correctly and the
analysis service could hand out work correctly, but nothing joined them. This file drives
the join.

The server here is the **real FastAPI app** with the **real** `analysis` router, the real
service functions and a real migrated SQLite database — composed the way
`tests/integration/test_analysis_once_per_key.py` composes its context, and reached through
an in-process client. That matters for one specific reason: `contracts/modules.yaml` types
every `MOD-analysis-worker -> MOD-analysis-service` edge `transport: http`, so a test that
called the service functions directly would prove the loop on an edge that does not exist in
deployment. Every assertion below therefore travels through a route, a bearer token and the
three required wire headers.

What is fake, and only these: the AI provider transport (no live call — both adapters are
`enabled: false` anyway), the secret service (it has no code yet — gap **G-6**), the clock,
and the `post`/`work_version` rows behind `TaskInputPort`. The oracles are rows in
`analysis_task`, `analysis_attempt` and `analysis`, read back with SQL after the loop has
run.

Scenario anchors: SC16, SC17, SC28.
"""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisTaskType
from sqlalchemy import Engine, text

from server.app.analysis.service import (
    AnalysisContext,
    ProviderChoice,
    TargetRequest,
    TaskSource,
    enqueue_tasks,
)
from server.app.auth.middleware import PrincipalKind, TokenRegistry
from server.app.auth.service import hash_bearer_token
from server.app.db import create_sqlite_engine
from server.app.main import create_app
from tests.conftest import load_fixture
from worker.app import main as worker_main
from worker.app.adapter.api_provider import (
    ApiProviderAdapter,
    ProviderRequest,
    ProviderResponse,
    ProviderUnavailable,
)
from worker.app.adapter.base import (
    AdapterEntry,
    AdapterError,
    AuthFamily,
    CallAudit,
    IsolationStatus,
    JsonExtractionMethod,
    ProbeReasonCode,
    TaskCredential,
    TaskInput,
    TermsOutcome,
    UsageReporting,
    load_registered_adapters,
)
from worker.app.loop import (
    CLAIM_IDLE_BACKOFF_SECONDS,
    HEARTBEAT_INTERVAL_ANALYSIS_SECONDS,
    LEASE_TTL_ANALYSIS_SECONDS,
    PROVIDER_UNAVAILABLE_BACKOFF_SECONDS,
    AbsentSecretService,
    AnalysisServerPort,
    AnalysisWorkerLoop,
    CredentialRefused,
    CycleOutcome,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01JW0WNER00000000000000000"
WORK_ID = "01JWRKA1000000000000000000"
TARGET_KEY = f"work:{WORK_ID}"
WORK_VERSION_SOURCE_ID = "work_version:01JWVRA1000000000000000000"
RUN_ID = "01JRUNA1000000000000000000"
WORKER_TOKEN = "analysis-worker-token"
WORKER_ID = "analysis-worker-1"
SOURCE_FINGERPRINT = "sha256:858c06cf9c505c9f135e64d506f2e40dcb5bc6992bfd8d97f31e6b7caa8b0d38"
T0 = datetime(2026, 9, 6, 18, 0, 0, tzinfo=UTC)


# ------------------------------------------------------------------------------ harness
def _migrate(db_path: Path) -> None:
    """The real Alembic chain, not hand-written DDL — same rule as every other card's test."""
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
    """A `provider_config` row as `MOD-settings-service` would report it (it has no code yet).

    Enabled here so the server hands work out at all. On a real deployment today it is not:
    `analysis.claim_task` refuses with `no_enabled_provider` because both entries in
    `contracts/ai/providers.yaml` §2.1 are disabled — asserted separately in
    :func:`test_a_wired_app_hands_out_no_work_because_no_provider_is_enabled`.
    """

    def provider_for(self, task_type: str) -> ProviderChoice:
        return ProviderChoice(
            task_type=task_type,
            auth_family="api_key",
            provider_name="example-vendor-api",
            model_name="m-1",
            enabled=True,
        )


class FakeTaskInput:
    """One committed `work_version`, so the server-computed evidence ceiling is `abstract`."""

    def sources_for(self, *, target_key: str) -> Sequence[TaskSource]:
        return [
            TaskSource(
                source_id=WORK_VERSION_SOURCE_ID,
                kind="work_version",
                text="Abstract nêu bộ dữ liệu là QM9.",
                source_hash="sha256:" + "c" * 64,
                retrieved_at="2026-09-06T17:00:00.000Z",
            )
        ]


@dataclass
class RecordedTransport:
    """The provider. Answers from a recorded body; never opens a socket."""

    body: str = "{}"
    #: Builds the answer at send time. The happy-path document has to name the `attempt_id`
    #: the server minted during `claim_task`, and that row does not exist until the cycle is
    #: already running — so the answer cannot be a literal fixed before the loop starts.
    body_factory: Any = None
    tokens_in: int | None = 812
    tokens_out: int | None = 96
    unavailable: ProbeReasonCode | None = None
    seen: list[ProviderRequest] | None = None

    def __post_init__(self) -> None:
        self.seen = []

    def send(self, request: ProviderRequest, *, credential: TaskCredential) -> ProviderResponse:
        assert self.seen is not None
        self.seen.append(request)
        if self.unavailable is not None:
            raise ProviderUnavailable(self.unavailable)
        body = self.body_factory() if self.body_factory is not None else self.body
        return ProviderResponse(body=body, tokens_in=self.tokens_in, tokens_out=self.tokens_out)


class StubSecretService:
    """What `secret.issue_task_credential` will return once `MOD-secret-service` exists (G-6).

    Named a stub rather than a fake because it does not decide anything: the real refusal
    (ISO-05, a worker without the lease) belongs to the secret service and is out of reach
    from here. This only lets the *rest* of the cycle be exercised.
    """

    def __init__(self) -> None:
        self.issued: list[tuple[str, str]] = []

    def issue_task_credential(
        self, *, task_id: str, attempt_id: str, lease_id: str, lease_epoch: int
    ) -> TaskCredential:
        self.issued.append((task_id, attempt_id))
        return TaskCredential(
            value="per-task-credential",
            provider_config_id="01JPRVCFG10000000000000000",
            task_id=task_id,
            expires_at="2026-09-06T18:15:00.000Z",
        )


def probed_entry(*, task_types: frozenset[AnalysisTaskType] | None = None) -> AdapterEntry:
    """An entry that has passed its probe — a state no real adapter is in (test-only).

    Isolated in this helper so a reader can see in one place exactly which assumption the
    happy-path tests make, and that it is never made about a registered adapter.
    """
    return AdapterEntry(
        adapter_id="example-vendor@1.0.0",
        auth_family=AuthFamily.API_KEY,
        task_support=task_types or frozenset(AnalysisTaskType),
        max_concurrency=1,
        request_timeout_seconds=300,
        cancellation_support="cooperative",
        json_extraction_method=JsonExtractionMethod.NATIVE_JSON,
        usage_reporting=UsageReporting.EXACT,
        isolation=dict.fromkeys(
            (
                "tools_disabled",
                "filesystem_scope",
                "network_egress",
                "telegram_blocked",
                "credential_scope",
            ),
            IsolationStatus.VERIFIED,
        ),
        terms_outcome=TermsOutcome.PERMITTED_FOR_THIS_USE,
        enabled=True,
        disabled_reason=None,
        provider_name="example-vendor-api",
        model_name="m-1",
        endpoint_allowlist=frozenset({"provider.example.invalid"}),
    )


def _clock(start: datetime, *, step_seconds: int = 1) -> Any:
    state = {"now": start}

    def now() -> datetime:
        state["now"] = state["now"] + timedelta(seconds=step_seconds)
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
def ctx(engine: Engine) -> AnalysisContext:
    return AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=FakeProviderConfig(),
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=_clock(T0),
    )


@pytest.fixture
def client(ctx: AnalysisContext) -> Iterator[TestClient]:
    """The real app with the real analysis router, reached over HTTP in-process."""
    app = create_app()
    app.state.analysis_context = ctx
    app.state.token_registry = TokenRegistry({WORKER_TOKEN: PrincipalKind.ANALYSIS_WORKER})
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def server(client: TestClient) -> AnalysisServerPort:
    return AnalysisServerPort(client, token=WORKER_TOKEN)


def enqueue_one(ctx: AnalysisContext, *, task_type: str = "summary") -> None:
    """Queue one task the way a real caller does, supplying **no** key components.

    `source_fingerprint`, `prompt_version` and `schema_version` are all optional on
    `TargetRequest` and all advisory: `PKT-TC-ANALYSIS-FIX4` made the service derive the
    fingerprint from the sources the task-input port will actually serve, because that is what
    `ENT-analysis.source_fingerprint` is defined to be and because the key must be one value
    across enqueue, task input and commit or REQ-AC06 stops holding. Passing a literal here
    would only test that two constants in this file agree with each other.
    """
    enqueue_tasks(
        ctx,
        [
            TargetRequest(
                target_kind="work",
                target_id=WORK_ID,
                task_type=task_type,
                max_evidence_level="abstract",
            )
        ],
        caller_module="MOD-report-service",
    )


def rows(engine: Engine) -> dict[str, Any]:
    """The oracles, read back with SQL after the loop has run."""
    with engine.connect() as connection:
        task = connection.execute(text("SELECT id, state FROM analysis_task LIMIT 1")).fetchone()
        attempts = connection.execute(
            text(
                "SELECT id, outcome, error_code, cost_uncertain, ended_at "
                "FROM analysis_attempt ORDER BY attempt_number"
            )
        ).fetchall()
        analyses = connection.execute(text("SELECT id, status FROM analysis")).fetchall()
        lease = connection.execute(
            text("SELECT id, expires_at, state FROM assignment_lease ORDER BY lease_epoch DESC")
        ).fetchone()
    return {
        "task_state": None if task is None else task[1],
        "attempts": [tuple(row) for row in attempts],
        "analyses": [tuple(row) for row in analyses],
        "lease": None if lease is None else tuple(lease),
    }


def submitted_document(task: TaskInput) -> dict[str, Any]:
    """The `analysis_result` a well-behaved model returns for **this** assignment.

    Built from the :class:`TaskInput` the adapter was handed, which is the only thing a real
    model is given: the key, the attempt, the granted source ids and the server-computed
    evidence ceiling all come from `analysis.get_task_input`. Nothing is read out of the
    database here and nothing is a literal — SV-01 compares the key in the answer against the
    key of the assignment, and two constants written in this file would agree for no reason.
    """
    fixture = load_fixture("ai/k-zero-api-key-all-tasks-via-cli")
    document: dict[str, Any] = json.loads(json.dumps(fixture.expected["analysis_result_summary"]))
    document["analysis_key"] = dict(task.analysis_key)
    document["attempt_id"] = task.attempt_id
    document["evidence_level"] = task.max_evidence_level
    document["input_source_ids"] = list(task.input_source_ids)
    document["provider"] = {
        "auth_family": "api_key",
        "provider_name": "example-vendor-api",
        "model_name": "m-1",
    }
    document["usage"] = {
        "unknown": False,
        "tokens_in": 812,
        "tokens_out": 96,
        "cost_micro_usd": None,
    }
    result = document["result"]
    result["difference_from_existing"]["comparator"] = {
        "kind": "ref",
        "source_ref": WORK_VERSION_SOURCE_ID,
    }
    result["statements"] = [
        {
            "kind": "source_verified",
            "text": "Abstract nêu bộ dữ liệu là QM9.",
            "citation_refs": [WORK_VERSION_SOURCE_ID],
        }
    ]
    return document


class CapturingAdapter:
    """Wraps the real adapter and remembers the assignment it was handed.

    The fake provider has to answer *this* task — its key and its attempt id — and neither
    exists until the cycle is already running. Capturing the `TaskInput` on the way in is how
    the recorded answer stays a function of the real assignment rather than of a literal.
    """

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.last_task: TaskInput | None = None

    def run_inference_task(
        self, task: TaskInput, *, credential: TaskCredential | None = None
    ) -> Any:
        self.last_task = task
        return self.inner.run_inference_task(task, credential=credential)

    def answer(self) -> str:
        assert self.last_task is not None, "the adapter was not called"
        return json.dumps(submitted_document(self.last_task), ensure_ascii=False)


# ---------------------------------------------------- cycle 1: credential refused (G-6)
def test_a_credential_refusal_ends_the_cycle_without_inventing_anything(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """`MOD-secret-service` does not exist, so the cycle stops at a **named** outcome.

    The three things this asserts are the three ways the loop could have cheated:

    * it does not fake a success — zero `analysis` rows;
    * it does not file `analysis.report_attempt_unknown` — no provider call happened, so
      writing `cost_uncertain = true` would record an uncertainty the system does not have.
      The opening attempt is still open, exactly as `claim_task` left it;
    * it does not retry — the transport is never reached, because the refusal comes first.
    """
    enqueue_one(ctx)
    transport = RecordedTransport()
    audit = CallAudit()
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=ApiProviderAdapter(
            probed_entry(),
            transport=transport,
            endpoint="https://provider.example.invalid/v1/messages",
            audit=audit,
        ),
        worker_instance_id=WORKER_ID,
        credentials=AbsentSecretService(),
        task_types=["summary"],
        clock=_clock(T0),
    )

    report = loop.run_once()

    assert report.outcome is CycleOutcome.CREDENTIAL_REFUSED
    assert report.reason == "secret_service_absent"
    assert report.backoff_seconds == PROVIDER_UNAVAILABLE_BACKOFF_SECONDS[0] == 60
    assert report.claimed

    observed = rows(engine)
    assert observed["analyses"] == []
    assert len(observed["attempts"]) == 1
    # `claim_task` opens the attempt as `timeout_unknown` / `cost_uncertain = 1` on purpose:
    # from the moment work is handed out until an outcome is reported, the server genuinely
    # does not know whether the model ran. So the row alone cannot say whether the worker
    # filed an unknown attempt. What distinguishes the two is the task and the lease:
    # `report_attempt_unknown` moves the task to `unknown_attempt` and expires the lease,
    # and neither happened here.
    assert observed["task_state"] == "running"
    assert observed["lease"][2] == "held"

    assert transport.seen == []
    assert audit.provider_calls == []
    assert audit.credentials_received == 0


def test_a_registered_adapter_refuses_the_dispatch_and_records_no_result(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """The `enabled: false` path, with the **real** registry entry rather than a copy.

    This is the disagreement that must never become a fake success: the provider registry the
    server consulted said enabled, and the adapter — reading
    `contracts/ai/providers.yaml` §2.1 — still refuses because isolation is unverified (B13).
    """
    enqueue_one(ctx)
    entry = next(e for e in load_registered_adapters() if e.adapter_id == "anthropic@claude-opus-5")
    transport = RecordedTransport()
    audit = CallAudit()
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=ApiProviderAdapter(entry, transport=transport, endpoint="", audit=audit),
        worker_instance_id=WORKER_ID,
        credentials=StubSecretService(),
        task_types=["summary"],
        clock=_clock(T0),
    )

    report = loop.run_once()

    assert report.outcome is CycleOutcome.DISPATCH_REFUSED
    assert report.error_code is ErrorCode.CAPABILITY_DENIED
    assert report.reason == ProbeReasonCode.ISOLATION_UNVERIFIED.value
    assert report.backoff_seconds == PROVIDER_UNAVAILABLE_BACKOFF_SECONDS[0]

    observed = rows(engine)
    assert observed["analyses"] == []
    assert observed["task_state"] == "running"
    assert observed["lease"][2] == "held", "no unknown attempt was filed: nothing ran"
    assert transport.seen == []
    assert audit.provider_calls == []


# -------------------------------------------------------------- cycle 2: submit, for real
def test_a_full_cycle_commits_one_analysis_row_through_the_real_routes(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """claim -> input -> credential -> dispatch -> submit, ending in committed rows.

    Every step is an HTTP call to the shipped router with the shipped bearer dependency; the
    only fake in the chain is the provider's answer. The oracle is the database: one `valid`
    `analysis`, its attempt closed `accepted`, the task terminal and the lease released.
    """
    enqueue_one(ctx)
    secrets = StubSecretService()
    audit = CallAudit()
    transport = RecordedTransport(body_factory=lambda: adapter.answer())
    adapter = CapturingAdapter(
        ApiProviderAdapter(
            probed_entry(),
            transport=transport,
            endpoint="https://provider.example.invalid/v1/messages",
            audit=audit,
        )
    )
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=adapter,
        worker_instance_id=WORKER_ID,
        credentials=secrets,
        task_types=["summary"],
        clock=_clock(T0),
    )

    report = loop.run_once()

    assert report.outcome is CycleOutcome.SUBMITTED, report
    # The key the model answered with is the one the SERVER sent, not one this test built:
    # `PKT-TC-ANALYSIS-FIX4` put the seven components in the `get_task_input` response, and
    # SV-01 passed against them.
    assert adapter.last_task is not None
    assert set(adapter.last_task.analysis_key) == {
        "owner_id",
        "target_key",
        "task_type",
        "source_fingerprint",
        "prompt_version",
        "schema_version",
        "generation_number",
    }
    observed = rows(engine)
    assert [status for _id, status in observed["analyses"]] == ["valid"]
    assert observed["task_state"] == "valid"
    assert observed["attempts"][0][1] == "accepted"
    assert observed["lease"][2] == "released"

    # The credential was issued for exactly this task and attempt (B13, per-task scope).
    assert secrets.issued == [(report.task_id, report.attempt_id)]
    # One provider call, and its request carried no tool definition (ISO-01).
    assert len(transport.seen) == 1
    assert transport.seen[0].tools == ()
    assert audit.calls == 1
    assert audit.outbound_hosts == ["provider.example.invalid"]


def test_the_server_and_not_the_worker_decides_the_evidence_ceiling(
    ctx: AnalysisContext, server: AnalysisServerPort, engine: Engine
) -> None:
    """`max_evidence_level` is copied from the server's answer, never recomputed.

    `contracts/ai/tasks.yaml` §3 makes the server derive it from the sources actually
    present. A worker that computed its own could raise the ceiling the model is checked
    against and quietly defeat SV-04.
    """
    enqueue_one(ctx)
    claimed = server.claim_task(
        worker_instance_id=WORKER_ID,
        task_types=["summary"],
        claim_request_id="claim-ceiling",
    )
    task = claimed["task"]
    payload = server.get_task_input(
        task_id=task["task_id"], lease_id=task["lease_id"], lease_epoch=task["lease_epoch"]
    )
    assert payload["max_evidence_level"] == "abstract"
    assert payload["input_source_ids"] == [WORK_VERSION_SOURCE_ID]


def test_get_task_input_now_carries_the_whole_analysis_key(
    ctx: AnalysisContext, server: AnalysisServerPort
) -> None:
    """`CR-TC-adapter-10`, closed by `PKT-TC-ANALYSIS-FIX4` — asserted, not assumed.

    This test used to assert the opposite: that the response carried no key, which is why
    :attr:`AnalysisWorkerLoop.analysis_key_resolver` had to exist. The server now computes all
    seven components — `source_fingerprint` from the sources it is about to serve — so the
    worker no longer invents anything, and the seam is vestigial.

    Asserted against a live response rather than the function's source, so it stays true of
    what the route actually returns.
    """
    enqueue_one(ctx)
    claimed = server.claim_task(
        worker_instance_id=WORKER_ID, task_types=["summary"], claim_request_id="claim-key"
    )
    task = claimed["task"]
    payload = server.get_task_input(
        task_id=task["task_id"], lease_id=task["lease_id"], lease_epoch=task["lease_epoch"]
    )
    key = payload["analysis_key"]
    assert set(key) == {
        "owner_id",
        "target_key",
        "task_type",
        "source_fingerprint",
        "prompt_version",
        "schema_version",
        "generation_number",
    }
    assert key["task_type"] == "summary"
    assert key["target_key"] == TARGET_KEY
    assert key["source_fingerprint"].startswith("sha256:")
    assert key["generation_number"] >= 1


# ------------------------------------------------------------------------ lease upkeep
def test_a_long_inference_is_heartbeated_and_never_outlives_its_lease(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """`heartbeat_interval_analysis` = 60 s inside `lease_ttl_analysis` = 900 s.

    The fake clock jumps two minutes per read, so the dispatch straddles the heartbeat
    interval without any wall-clock wait. The oracle is the lease row: `expires_at` must have
    moved forward, which only `analysis.heartbeat` does.
    """
    enqueue_one(ctx)
    with engine.connect() as connection:
        before = connection.execute(
            text("SELECT expires_at FROM assignment_lease LIMIT 1")
        ).fetchone()

    adapter = CapturingAdapter(
        ApiProviderAdapter(
            probed_entry(),
            transport=RecordedTransport(body_factory=lambda: adapter.answer()),
            endpoint="https://provider.example.invalid/v1/messages",
        )
    )
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=adapter,
        worker_instance_id=WORKER_ID,
        credentials=StubSecretService(),
        task_types=["summary"],
        clock=_clock(T0, step_seconds=120),
    )

    report = loop.run_once()

    assert report.heartbeats >= 1, "a dispatch past the interval must heartbeat"
    assert HEARTBEAT_INTERVAL_ANALYSIS_SECONDS < 120, "the clock step must straddle it"
    assert report.outcome is CycleOutcome.SUBMITTED
    observed = rows(engine)
    assert before is None or observed["lease"][1] >= before[0]
    assert LEASE_TTL_ANALYSIS_SECONDS == 900


# ------------------------------------------------------- the provider may have run (SC28)
def test_an_uncertain_attempt_is_filed_as_unknown_and_never_as_a_result(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """`AI_ATTEMPT_UNCERTAIN` is the one case where "unknown" is the honest record.

    I16 in the rows: `cost_uncertain` true, `ended_at` NULL — the system says what it does
    not know rather than claiming no cost was incurred — and **zero** `analysis` rows,
    because an attempt is never a result.
    """
    enqueue_one(ctx)

    class UncertainAdapter:
        def run_inference_task(
            self, task: TaskInput, *, credential: TaskCredential | None = None
        ) -> Any:
            raise AdapterError(
                ErrorCode.AI_ATTEMPT_UNCERTAIN,
                "Một lần phân tích không rõ kết quả. Chi phí có thể đã phát sinh.",
                details_safe={"task_id": task.task_id, "cost_uncertain": True},
            )

    loop = AnalysisWorkerLoop(
        server=server,
        adapter=UncertainAdapter(),
        worker_instance_id=WORKER_ID,
        credentials=StubSecretService(),
        task_types=["summary"],
        clock=_clock(T0),
    )

    report = loop.run_once()

    assert report.outcome is CycleOutcome.ATTEMPT_UNKNOWN
    assert report.error_code is ErrorCode.AI_ATTEMPT_UNCERTAIN
    observed = rows(engine)
    assert observed["analyses"] == []
    assert observed["task_state"] == "unknown_attempt"
    attempt = observed["attempts"][0]
    assert attempt[1] == "timeout_unknown"
    assert attempt[2] == ErrorCode.AI_ATTEMPT_UNCERTAIN.value
    assert attempt[3] == 1, "cost_uncertain must be true"
    assert attempt[4] is None, "ended_at must stay NULL: nobody knows when it finished"


def test_a_provider_that_will_not_start_burns_its_own_budget_and_backs_off(
    ctx: AnalysisContext, engine: Engine, server: AnalysisServerPort
) -> None:
    """`provider_unavailable_waits` = 3, on its own ladder, never mixed with schema retries.

    No inference ran, so this must not consume `analysis_attempts_per_item` — the two budgets
    are separate in `contracts/retry-policy.yaml` for exactly that reason.
    """
    enqueue_one(ctx)
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=ApiProviderAdapter(
            probed_entry(),
            transport=RecordedTransport(unavailable=ProbeReasonCode.BINARY_MISSING),
            endpoint="https://provider.example.invalid/v1/messages",
        ),
        worker_instance_id=WORKER_ID,
        credentials=StubSecretService(),
        task_types=["summary"],
        clock=_clock(T0),
    )

    report = loop.run_once()

    assert report.outcome is CycleOutcome.PROVIDER_UNAVAILABLE
    assert report.error_code is ErrorCode.AI_PROVIDER_UNAVAILABLE
    assert report.reason == "binary_missing"
    assert report.backoff_seconds == PROVIDER_UNAVAILABLE_BACKOFF_SECONDS[0]
    assert loop.provider_unavailable_budget_left == 2
    assert rows(engine)["analyses"] == []


def test_an_empty_queue_walks_the_idle_ladder_of_the_retry_policy(
    server: AnalysisServerPort,
) -> None:
    """`claim_idle_backoff` = 5, 15, 45 seconds, holding at the ceiling.

    Nothing was enqueued, so every cycle is a legitimate "no work": the ladder is the
    contract's, read from `retry-policy.yaml`, and 45 s is a ceiling rather than a last rung.
    """
    slept: list[int] = []
    loop = AnalysisWorkerLoop(
        server=server,
        adapter=ApiProviderAdapter(probed_entry(), transport=RecordedTransport(), endpoint=""),
        worker_instance_id=WORKER_ID,
        credentials=StubSecretService(),
        task_types=["summary"],
        clock=_clock(T0),
        sleeper=slept.append,
    )

    reports = loop.run_forever(max_cycles=4)

    assert {r.outcome for r in reports} == {CycleOutcome.NO_TASK}
    assert [r.backoff_seconds for r in reports] == [5, 15, 45, 45]
    assert slept == [5, 15, 45, 45]
    assert CLAIM_IDLE_BACKOFF_SECONDS == (5, 15, 45)


# ------------------------------------------------------------- the wired app, as deployed
def test_a_wired_app_hands_out_no_work_because_no_provider_is_enabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Through `server.app.wiring.create_wired_app` — the composition root, as it ships.

    `wire()` records `analysis_context.provider_config` as **unwired** (gap G-6), and
    `analysis.claim_task` therefore refuses with `no_enabled_provider` rather than handing out
    a task whose only next step is a call nobody has enabled. That refusal is the honest state
    of a real deployment today, so it is asserted rather than worked around.
    """
    from server.app.wiring import create_wired_app, upgrade_database

    db_path = tmp_path / "wired.db"
    upgrade_database(db_path)
    # `wire()` skips every owner-scoped context when there is no owner row, so the runbook's
    # §3 bootstrap step is a precondition of this assertion rather than an aside.
    bootstrap = create_sqlite_engine(db_path)
    with bootstrap.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, failed_login_count) VALUES (:id, 1, 'owner', "
                "'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z', 0)"
            ),
            {"id": OWNER_ID},
        )
    bootstrap.dispose()
    monkeypatch.setenv("RR_DATABASE_URL", str(db_path))
    monkeypatch.setenv("RR_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("RR_ANALYSIS_WORKER_TOKEN_SHA256", hash_bearer_token(WORKER_TOKEN))

    app = create_wired_app()
    with TestClient(app) as test_client:
        server = AnalysisServerPort(test_client, token=WORKER_TOKEN)
        claimed = server.claim_task(
            worker_instance_id=WORKER_ID,
            task_types=["summary"],
            claim_request_id="claim-wired",
        )
    assert claimed["task"] is None
    assert claimed["reason"] == "no_enabled_provider"


# ------------------------------------------------------------------ main.py: refuse to start
@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ({}, "server_url_not_configured"),
        ({"RR_SERVER_URL": "http://127.0.0.1:8080"}, "worker_token_file_missing"),
    ],
)
def test_the_worker_refuses_to_start_with_a_named_reason(
    env: dict[str, str], expected: str
) -> None:
    """One reason per cause. A single "bad config" message would hide the operator's next step."""
    with pytest.raises(worker_main.ConfigError) as raised:
        worker_main.load_config(env)
    assert raised.value.reason.value == expected


def test_a_token_file_wider_than_0600_is_a_refusal_not_a_warning(tmp_path: Path) -> None:
    """`contracts/ops/secrets.md` §3, in as many words: a silent warning would be useless."""
    token_file = tmp_path / "worker.token"
    token_file.write_text("a-token", encoding="utf-8")
    token_file.chmod(0o644)
    env = {"RR_SERVER_URL": "http://127.0.0.1:8080", "RR_WORKER_TOKEN_FILE": str(token_file)}

    with pytest.raises(worker_main.ConfigError) as raised:
        worker_main.load_config(env)
    assert raised.value.reason.value == "worker_token_file_permissions_too_wide"
    assert "a-token" not in str(raised.value), "the refusal must not echo the token"

    token_file.chmod(0o600)
    config = worker_main.load_config(env)
    assert config.token() == "a-token"
    assert stat.S_IMODE(token_file.stat().st_mode) == 0o600
    # The token never appears in a rendering of the config object.
    assert "a-token" not in repr(config) and "a-token" not in str(config)


def test_an_empty_token_file_is_refused(tmp_path: Path) -> None:
    token_file = tmp_path / "worker.token"
    token_file.write_text("   \n", encoding="utf-8")
    token_file.chmod(0o600)
    with pytest.raises(worker_main.ConfigError) as raised:
        worker_main.load_config(
            {"RR_SERVER_URL": "http://x", "RR_WORKER_TOKEN_FILE": str(token_file)}
        )
    assert raised.value.reason.value == "worker_token_empty"


def test_print_capabilities_output_is_still_the_one_the_runbook_pins(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`docs/owner-runbook.md` §4.3 records this exact JSON as a command already run.

    The loop landing does not change what the worker advertises: both adapters remain
    `enabled: false`, so `ai_providers` is still empty and the documented output still holds.
    """
    assert worker_main.main(["--print-capabilities"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == {
        "worker_kind": "analysis",
        "agent_version": "0.1.0",
        "schema_version": printed["schema_version"],
        "tasks_supported": ["label", "summary", "direction_phrasing"],
        "ai_providers": [],
    }


def test_print_adapters_explains_the_emptiness_without_enabling_anything(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The new command: why no provider is usable, read from the contract rather than guessed."""
    assert worker_main.main(["--print-adapters"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ac16"] == "BLOCKED", "never FAIL — ADR-0010 §Hệ quả"
    assert {row["adapter_id"] for row in printed["registered_adapters"]} == {
        "anthropic@claude-sonnet-5",
        "anthropic@claude-opus-5",
    }
    for row in printed["registered_adapters"]:
        assert row["enabled"] is False
        assert row["probe_outcome"] == "unknown", "unknown is never converted to usable"
        assert row["reason_code"] == "isolation_unverified"
        assert row["disabled_reason_present"] is True


def test_no_argument_still_refuses(capsys: pytest.CaptureFixture[str]) -> None:
    """Unchanged from Phase 0: a worker with nothing to do says so and exits non-zero."""
    with pytest.raises(SystemExit) as raised:
        worker_main.main([])
    assert raised.value.code == 2
    assert "--print-capabilities" in capsys.readouterr().err


def test_the_absent_secret_service_is_a_refusal_and_not_a_stub_that_pretends() -> None:
    """G-6 made explicit: the port refuses, with a reason, for every request."""
    with pytest.raises(CredentialRefused) as raised:
        AbsentSecretService().issue_task_credential(
            task_id="t", attempt_id="a", lease_id="l", lease_epoch=1
        )
    assert raised.value.reason == "secret_service_absent"
