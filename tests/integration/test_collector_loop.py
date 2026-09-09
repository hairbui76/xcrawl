"""E1 -- the collector process loop against the real server, end to end.

``PKT-TC-COLLECTOR-FIX2`` / gap ``G-7a``: until now `collector/app/main.py` was a Phase-0 stub
that printed a payload shape, and the collector's own tests drove a `WorkerStub` because
``worker.*`` had no implementation. Both halves are now real. This module runs
:class:`~collector.app.loop.CollectorLoop` against the **real** FastAPI application with the
**real** ``jobs`` and ``ingest`` routers over a **real** SQLite database, and asserts on the
rows those services write: ``assignment_lease``, ``run``, ``checkpoint``, ``post``.

What is still not real, and why that is correct
-----------------------------------------------
The X source. There is no live driver in this repository -- opening Chrome belongs to
``TC-x-feasibility-probe`` behind gate SP1, and ``contracts/ops/collector-probe.md`` §0 still
records the probe as ``NOT_RUN``. So the loop is handed a
:class:`~collector.app.reader.RecordedSource` over synthetic pages. No browser, no network,
no X session, and nothing here is evidence about X's real behaviour.

The clock is fake in both senses the system needs: a ``FakeClock`` drives the server's lease
arithmetic, and a separate monotonic counter drives the collector's budget and heartbeat.
They are separate because the contracts treat them separately -- a wall-clock adjustment must
not lengthen a segment.

The two cycles this file proves
-------------------------------
1. **A full cycle.** register (no lease -- LM-01) → claim (one ``held`` lease, epoch 1, run
   ``running/collecting``) → collect → ``ingest.submit_batch`` → ``ingest.commit_checkpoint``
   → release. Measured on rows: ``post``, ``checkpoint.acked_through_ingest_sequence``,
   ``assignment_lease.state``, and the epoch bump on release.
2. **A challenge cycle.** The same start, then a challenge mid-segment → the buffered posts
   are never written → ``worker.report_stop`` → the *server* moves the run to ``needs_user``
   with ``stop_reason = captcha`` and creates exactly one alert intent → the loop stops
   claiming. That last assertion is the one the earlier packet could only corroborate with a
   stub; here the alert cap is enforced by ``server/app/jobs/service.py`` reading
   ``run.alert_intent_id``, so it is the server's guarantee that is being measured.

Wiring note (``CR-TC-COLLECTOR-08``)
------------------------------------
Three adapters live in this file because no composition root exists yet
(``WIRING-wave-1.md`` gap G-2; ``server/app/wiring.py`` had not landed when this was
written): ingest's ``AssignmentPort`` over ``assignment_lease``, jobs' ``CheckpointPort``
over ``ingest.get_checkpoint``, and jobs' ``AlertIntentPort``. They are three-line bridges
between two services that already exist, not reimplementations of either, and the real
deployment needs all three.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from collector.app.client import CollectorClient, WireStopReason
from collector.app.loop import (
    CollectorConfig,
    CollectorLoop,
    ConfigError,
    CycleKind,
    LoopExitReason,
    load_config,
)
from collector.app.reader import Completion, FeedPage, RecordedSource, SourceSignal
from collector.app.session import ChromeProfile, XSessionState
from server.app.auth.service import hash_bearer_token
from server.app.db import create_sqlite_engine
from server.app.jobs.service import run_now
from server.app.main import create_app
from server.app.settings import Settings
from server.app.wiring import upgrade_database, wire

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01JW0WNER00000000000000000"
COLLECTOR_TOKEN = "collector-token-for-tests-only-not-a-secret"
WORKER_ID = "01JWORKERC0000000000000000"

#: Small enough that one synthetic page fills a batch, so the second page's posts are still
#: in memory when the challenge arrives -- the shape ``c-challenge-mid-batch`` describes.
BATCH_SIZE = 20
DOWNLOADED_NOT_INGESTED = 7


# --------------------------------------------------------------------------- the real server


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """The real :class:`Settings` object, built directly rather than from the environment.

    ``load_settings()`` reads ``RR_*`` variables; constructing the dataclass gives the same
    object without a test mutating the process environment. The collector token is configured
    the way a deployment configures it -- as a **digest**, never as the token
    (``contracts/ops/secrets.md`` §3: "server lưu sha256, không lưu bản rõ"). The digest is
    produced by the shipped :func:`hash_bearer_token`, not by a second spelling of sha256
    here: the ``sha256:`` prefix is part of the stored form, and a bare hex digest silently
    matches nothing.
    """
    return Settings(
        database_path=tmp_path / "radar.db",
        data_dir=tmp_path / "data",
        timezone_iana="Asia/Ho_Chi_Minh",
        schedule_slots=("08:00", "20:00"),
        provider_config_path=tmp_path / "providers.yaml",
        telegram_webhook_secret=None,
        collector_token_sha256=hash_bearer_token(COLLECTOR_TOKEN),
        collector_token=COLLECTOR_TOKEN,
        analysis_worker_token_sha256=None,
        backup_operator_token_sha256=None,
    )


class FakeClock:
    """The server's clock. Moves only when a test moves it."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now = self.now + timedelta(**delta)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 9, 7, 8, 0, tzinfo=UTC))


@pytest.fixture
def app(settings: Settings, clock: FakeClock) -> Iterator[FastAPI]:
    """The real application through the real composition root, and nothing else.

    ``upgrade_database`` + ``wire`` are ``server/app/wiring.py``'s own entry points. After
    ``P0-FIX5`` there is nothing left to patch around: the composition root builds the
    assignment port, sets ``app.state.collector_token`` from settings, and installs an alert
    adapter that joins the caller's transaction. The three workarounds this fixture carried
    -- a hand-written ``LeaseReader``, a manually set token, and ``alert_port=None`` -- are
    all gone (``CR-TC-COLLECTOR-09``, ``-10``, ``-11``, closed).

    The only adjustment left is determinism: a fake clock and deterministic ids on
    ``job_context``, because lease expiry and catch-up are statements about time and a test
    that cannot move the clock cannot check them.

    The engine ``wire()`` builds is **disposed on teardown**. That is not tidiness: every
    test in this module builds a whole runtime, each runtime holds a SQLAlchemy pool, and
    leaving sixteen of them open leaked enough SQLite file handles to make an unrelated test
    fail later in a full-suite run — while this file passed on its own and the suite passed
    without it. A fixture that builds a composition root has to take it down again.
    """
    upgrade_database(settings.database_path)
    engine = create_sqlite_engine(settings.database_path)
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
    engine.dispose()

    application = create_app()
    runtime = wire(application, settings)
    assert runtime.owner_id == OWNER_ID, "the owner row must be visible to the wiring"

    counter = {"n": 0}

    def ids() -> str:
        counter["n"] += 1
        return f"01JTEST{counter['n']:019d}"[:26]

    assert (
        application.state.ingest_context.assignment is not None
    ), "the composition root must build the assignment port (CR-TC-COLLECTOR-09)"
    assert (
        application.state.collector_token == COLLECTOR_TOKEN
    ), "the composition root must set app.state.collector_token (CR-TC-COLLECTOR-10)"
    # The alert port stays exactly as the composition root built it: the wired adapter now
    # joins the caller's transaction, so the alert path works and is asserted below rather
    # than disabled.
    application.state.job_context = replace(
        application.state.job_context, clock=clock, id_factory=ids
    )
    try:
        yield application
    finally:
        runtime.engine.dispose()


@pytest.fixture
def engine(app: FastAPI) -> Engine:
    """The engine the wired application is actually using."""
    return app.state.engine


# --------------------------------------------------------------------------- harness


@pytest.fixture
def wire_log() -> list[dict[str, Any]]:
    """Every HTTP exchange the collector made, captured at the transport.

    The client returns typed objects and drops the raw body, which is the right shape for
    production and the wrong one for asserting what the *server* actually said. Recording at
    the transport keeps ``collector/app/client.py`` untouched (it is outside this lease) while
    still letting a test read the wire.
    """
    return []


@pytest.fixture
def client(app: FastAPI, wire_log: list[dict[str, Any]]) -> Iterator[CollectorClient]:
    """A real :class:`CollectorClient` reaching the real app in-process.

    ``httpx.MockTransport`` forwards to Starlette's ``TestClient``, so the collector object
    under test is the production one: same headers, same bearer, same error parsing.
    """
    server = TestClient(app)

    def handler(request: httpx.Request) -> httpx.Response:
        response = server.request(
            request.method,
            request.url.raw_path.decode(),
            content=request.content,
            headers={
                key: value
                for key, value in request.headers.items()
                if key.lower() not in {"host", "content-length"}
            },
        )
        body = response.json()
        wire_log.append({"path": request.url.path, "status": response.status_code, "body": body})
        return httpx.Response(response.status_code, json=body)

    collector_client = CollectorClient(
        base_url="https://server.local",
        token=COLLECTOR_TOKEN,
        transport=httpx.MockTransport(handler),
        sleep=lambda _seconds: None,
    )
    yield collector_client
    collector_client.close()
    server.close()


@pytest.fixture
def config(tmp_path: Path) -> CollectorConfig:
    profile_dir = tmp_path / "rr-chrome-profile"
    profile_dir.mkdir()
    return CollectorConfig(
        server_url="https://server.local",
        token=COLLECTOR_TOKEN,
        profile=ChromeProfile(user_data_dir=profile_dir, ready=True),
        worker_instance_id=WORKER_ID,
    )


def raw_post(index: int) -> dict[str, Any]:
    post_id = f"19000000000000000{index:02d}"
    return {
        "x_post_id": post_id,
        "author": {"handle": "acc1", "x_user_id": "1234567890"},
        "url": f"https://x.com/acc1/status/{post_id}",
        "text": f"bài nghiên cứu số {index}",
        "published_at": "2026-09-07T07:50:00.000Z",
        "collected_at": "2026-09-07T08:00:00.000Z",
        "media_refs": [],
        "referenced_links": [],
    }


def build_loop(
    config: CollectorConfig,
    client: CollectorClient,
    source: RecordedSource,
    *,
    session_state: XSessionState = XSessionState.OK,
) -> CollectorLoop:
    loop = CollectorLoop(
        config=config,
        client=client,
        source=source,
        clock=lambda: datetime(2026, 9, 7, 8, 0, tzinfo=UTC),
        monotonic=lambda: 0.0,
        sleep=lambda _seconds: None,
        batch_size=BATCH_SIZE,
    )
    loop.session = loop.session.observing(session_state)
    return loop


def start_run(app: FastAPI) -> str:
    """Create the queued run a collector can claim (``run.run_now``)."""
    return str(run_now(app.state.job_context, request_id="01JREQ0000000000000000000A")["run_id"])


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar_one())


def scalar(engine: Engine, sql: str, **params: Any) -> Any:
    with engine.connect() as connection:
        return connection.execute(text(sql), params).scalar()


def alert_rows(engine: Engine) -> int:
    """``COUNT(outbox_intent WHERE intent_type='telegram_alert')`` -- the fixture's oracle.

    ``ux_outbox_alert_per_run`` is a partial unique index over
    ``(owner_id, intent_type, subject_ref)``, so "at most one alert per run" is a property of
    the schema rather than of a code path. Rows only appear here once ``CR-TC-COLLECTOR-11``
    is fixed; until then :class:`AlertRecorder` stands in for the write and this counts zero.
    """
    return count(
        engine,
        "SELECT COUNT(*) FROM outbox_intent WHERE intent_type = 'telegram_alert'",
    )


# --------------------------------------------------------------------------- configuration


def test_the_process_refuses_to_start_without_configuration() -> None:
    """Every refusal names which variable is missing, not just "misconfigured"."""
    with pytest.raises(ConfigError) as raised:
        load_config({})
    assert raised.value.reason == "missing_server_url"

    with pytest.raises(ConfigError) as raised:
        load_config({"RR_SERVER_URL": "https://server.local"})
    assert raised.value.reason == "missing_collector_token"

    with pytest.raises(ConfigError) as raised:
        load_config({"RR_SERVER_URL": "https://server.local", "RR_COLLECTOR_TOKEN": "t"})
    assert raised.value.reason == "missing_chrome_profile_dir"

    with pytest.raises(ConfigError) as raised:
        load_config(
            {
                "RR_SERVER_URL": "server.local",
                "RR_COLLECTOR_TOKEN": "t",
                "RR_CHROME_PROFILE_DIR": "/srv/rr",
            }
        )
    assert raised.value.reason == "server_url_not_absolute"


def test_the_machine_default_chrome_profile_is_refused_by_configuration(tmp_path: Path) -> None:
    """REQ-D09 enforced at the point where the path enters the process."""
    default = tmp_path / ".config" / "google-chrome"
    default.mkdir(parents=True)
    with pytest.raises(ConfigError) as raised:
        load_config(
            {
                "RR_SERVER_URL": "https://server.local",
                "RR_COLLECTOR_TOKEN": "t",
                "RR_CHROME_PROFILE_DIR": str(default),
            }
        )
    assert raised.value.reason == "chrome_profile_is_the_machine_default"


def test_a_token_file_wider_than_0600_is_refused(tmp_path: Path) -> None:
    """``contracts/ops/secrets.md`` §3: refuse to start, because a silent warning is useless."""
    token_file = tmp_path / "collector-token"
    token_file.write_text("a-token", encoding="utf-8")
    token_file.chmod(0o644)
    profile = tmp_path / "profile"
    profile.mkdir()

    env = {
        "RR_SERVER_URL": "https://server.local",
        "RR_COLLECTOR_TOKEN_FILE": str(token_file),
        "RR_CHROME_PROFILE_DIR": str(profile),
    }
    with pytest.raises(ConfigError) as raised:
        load_config(env)
    assert raised.value.reason == "token_file_permissions_too_open"

    token_file.chmod(0o600)
    assert load_config(env).token == "a-token"


def test_the_configuration_summary_never_carries_the_token(config: CollectorConfig) -> None:
    """The redacted view is what gets printed by ``--check-config``."""
    rendered = repr(config.redacted)
    assert COLLECTOR_TOKEN not in rendered
    assert config.redacted["token"] == "<redacted>"


# --------------------------------------------------------------------------- cycle 1: full run


def test_one_full_cycle_against_the_real_server(
    app: FastAPI, engine: Engine, client: CollectorClient, config: CollectorConfig
) -> None:
    """register → claim → collect → ingest → checkpoint → release, measured on rows.

    Every assertion below reads a table the real services wrote. The collector is the real
    :class:`CollectorLoop`; only the X source is synthetic.
    """
    start_run(app)
    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, BATCH_SIZE + 1)),
                next_cursor=None,
                signal=SourceSignal.END_OF_FEED,
            )
        ]
    )
    loop = build_loop(config, client, source)

    registration = loop.register()
    assert registration["lease_granted"] is False, "registration is not work (LM-01)"
    assert count(engine, "SELECT COUNT(*) FROM assignment_lease") == 0

    result = loop.run_cycle()

    assert result.kind is CycleKind.SEGMENT
    outcome = result.outcome
    assert outcome is not None
    assert outcome.completion is Completion.FEED_EXHAUSTED
    assert outcome.stop_reason is None, "an exhausted feed is not a stop reason (I13)"

    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE
    assert scalar(engine, "SELECT MAX(acked_through_ingest_sequence) FROM checkpoint") == BATCH_SIZE
    assert outcome.acked_through_ingest_sequence == BATCH_SIZE
    assert count(engine, "SELECT COUNT(*) FROM ingest_receipt") >= 1
    assert scalar(engine, "SELECT status FROM run") == "running"
    assert (
        count(engine, "SELECT COUNT(*) FROM assignment_lease WHERE state = 'held'") == 0
    ), "the runner released the lease when it closed the feed"
    assert scalar(engine, "SELECT state FROM assignment_lease") == "released"
    # LM-06's epoch bump lands on the *run*, not on the retired lease row: a released lease
    # keeps the epoch it was issued under, and `run.current_lease_epoch` is what a later call
    # is checked against. Asserting it on the lease row would only pass if the service
    # rewrote history.
    assert scalar(engine, "SELECT current_lease_epoch FROM run") == 2


def test_no_work_is_an_idle_cycle_not_a_failure(
    app: FastAPI, client: CollectorClient, config: CollectorConfig
) -> None:
    """I13 at the loop level: with no queued run the cycle is ``no_work`` and the loop waits.

    The wait uses the server's own ``retry_after_ms`` (``claim_idle_backoff``), not a number
    the collector chose.
    """
    slept: list[float] = []
    source = RecordedSource([])
    loop = build_loop(config, client, source)
    loop.sleep = slept.append

    exit_state = loop.run_forever(max_cycles=2)

    assert exit_state.reason is LoopExitReason.CYCLE_BUDGET
    assert [cycle.kind for cycle in exit_state.cycles] == [CycleKind.NO_WORK, CycleKind.NO_WORK]
    assert exit_state.cycles[0].no_work_reason in {
        "no_due_occurrence",
        "run_needs_user",
        "run_blocked",
        "storage_not_healthy",
        "capability_not_met",
        "assignment_already_held",
    }
    assert slept and all(delay > 0 for delay in slept)
    assert source.read_count == 0, "no source read happens when there is no assignment"


# --------------------------------------------------------------------------- cycle 2: challenge


def challenge_pages() -> list[FeedPage]:
    """One full batch, then 7 posts still in memory, then the verification page."""
    return [
        FeedPage(
            raw_posts=tuple(raw_post(i) for i in range(1, BATCH_SIZE + 1)),
            next_cursor="cursor-page-2",
            signal=SourceSignal.OK,
        ),
        FeedPage(
            raw_posts=tuple(
                raw_post(i) for i in range(BATCH_SIZE + 1, BATCH_SIZE + DOWNLOADED_NOT_INGESTED + 1)
            ),
            next_cursor="cursor-page-3",
            signal=SourceSignal.OK,
        ),
        FeedPage(signal=SourceSignal.CHALLENGE),
    ]


def test_a_challenge_cycle_against_the_real_server(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
) -> None:
    """The whole of SC04, with the server doing the deciding.

    I02 is measured on rows; the ``needs_user`` transition and the single alert intent are
    produced by ``server/app/jobs/service.py`` -- the half the previous packet could only
    corroborate with a stub.
    """
    start_run(app)
    source = RecordedSource(challenge_pages())
    loop = build_loop(config, client, source)
    loop.register()

    result = loop.run_cycle()

    outcome = result.outcome
    assert outcome is not None
    assert outcome.stop_reason is WireStopReason.CHALLENGE_REQUIRED
    assert outcome.error_code is ErrorCode.X_CHALLENGE_REQUIRED

    # I02: 20 durable, 7 downloaded and never written, checkpoint unmoved.
    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE
    assert scalar(engine, "SELECT MAX(acked_through_ingest_sequence) FROM checkpoint") == BATCH_SIZE
    assert outcome.posts_discarded_unsubmitted == DOWNLOADED_NOT_INGESTED

    # T-RUN-09, decided by the server.
    assert scalar(engine, "SELECT status FROM run") == "needs_user"
    assert scalar(engine, "SELECT stop_reason FROM run") == "captcha"
    # The alert row itself is asserted in `test_the_alert_intent_lands_in_the_callers_
    # transaction`; here it is enough that the stop produced exactly one, because that is the
    # observable consequence for the Owner of the collector reporting once.
    assert alert_rows(engine) == 1

    # I10: the observed session state is recorded, and it is not ``ok``.
    assert loop.session.x_session_state is XSessionState.CHALLENGE


def test_a_late_repeat_report_is_refused_because_the_lease_was_given_back(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
) -> None:
    """After the stop the loop releases the lease, so it cannot keep talking about it.

    This started life as a "report the same stop twice, get one alert" test, which is what
    ``c-challenge-mid-batch`` pins. It cannot be written that way *through the loop*: the
    loop hands the lease back as soon as the segment ends, ``release_assignment`` bumps
    ``run.current_lease_epoch`` (LM-06), and a second report carrying the old epoch is then
    correctly refused. The idempotent-repeat case is covered one layer down, in
    ``tests/integration/test_collector_resume_after_challenge.py``, where the runner is
    driven directly and the lease is still held.

    What this pins instead is worth having: a collector that has finished and released cannot
    go on mutating the run. ``STALE_LEASE`` with nothing changed is the whole of I10's
    single-writer guarantee at the end of a segment.
    """
    from collector.app.client import ServerError

    start_run(app)
    loop = build_loop(config, client, RecordedSource(challenge_pages()))
    loop.register()
    result = loop.run_cycle()
    assert result.outcome is not None
    assert result.released is True

    status_before = scalar(engine, "SELECT status FROM run")
    stop_reason_before = scalar(engine, "SELECT stop_reason FROM run")
    posts_before = count(engine, "SELECT COUNT(*) FROM post")

    lease_id = scalar(engine, "SELECT id FROM assignment_lease ORDER BY rowid DESC LIMIT 1")
    stale_epoch = scalar(
        engine, "SELECT lease_epoch FROM assignment_lease ORDER BY rowid DESC LIMIT 1"
    )
    with pytest.raises(ServerError) as raised:
        client.report_stop(
            assignment_id=str(result.assignment_id),
            stop_report_id="01JSTOPREPORT0000000000001",
            lease_id=str(lease_id),
            lease_epoch=int(stale_epoch),
            stop_reason=WireStopReason.CHALLENGE_REQUIRED,
            last_acked_ingest_sequence=BATCH_SIZE,
        )

    assert raised.value.code is ErrorCode.STALE_LEASE
    assert scalar(engine, "SELECT status FROM run") == status_before == "needs_user"
    assert scalar(engine, "SELECT stop_reason FROM run") == stop_reason_before == "captcha"
    assert count(engine, "SELECT COUNT(*) FROM post") == posts_before


def test_after_a_challenge_the_loop_stops_claiming(
    app: FastAPI, engine: Engine, client: CollectorClient, config: CollectorConfig
) -> None:
    """I10 at the loop level: no second claim, no second source read, no self-resume.

    ``run_forever`` is given a budget of five cycles and uses one. The exit reason is
    ``SESSION_NEEDS_OWNER``: clearing a challenge happens in the Chrome window, and the run
    leaves ``needs_user`` only through ``run.resume`` in the app (T-RUN-10).
    """
    start_run(app)
    source = RecordedSource(challenge_pages())
    loop = build_loop(config, client, source)
    loop.register()

    exit_state = loop.run_forever(max_cycles=5)

    assert exit_state.reason is LoopExitReason.SESSION_NEEDS_OWNER
    assert len(exit_state.cycles) == 1, "one cycle ran; the loop did not go round again"
    assert source.read_count == 3, "three pages read, and nothing after the stop"
    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE
    assert scalar(engine, "SELECT status FROM run") == "needs_user"


def test_the_loop_will_not_claim_while_its_session_is_not_ok(
    app: FastAPI, engine: Engine, client: CollectorClient, config: CollectorConfig
) -> None:
    """A collector that knows its session is in ``challenge`` does not ask for work.

    ``assignment.capability_requirements.requires_x_session_ok`` is ``const: true``, so the
    server would refuse anyway -- but asking would still be wrong, and the measurement here
    is that no lease row is ever created.
    """
    start_run(app)
    source = RecordedSource([])
    loop = build_loop(config, client, source, session_state=XSessionState.CHALLENGE)

    exit_state = loop.run_forever(max_cycles=3)

    assert exit_state.reason is LoopExitReason.SESSION_NEEDS_OWNER
    assert exit_state.cycles == ()
    assert count(engine, "SELECT COUNT(*) FROM assignment_lease") == 0
    assert source.read_count == 0


def test_a_limit_stop_releases_the_lease_and_leaves_the_run_running(
    app: FastAPI, engine: Engine, client: CollectorClient, config: CollectorConfig
) -> None:
    """T-RUN-02 end to end: a budget stop is not a failure and does not need a person.

    The run stays ``running`` and moves to ``enriching``; the loop releases the lease and is
    free to keep cycling, which is what ``LoopExitReason.CYCLE_BUDGET`` records.
    """
    run_id = start_run(app)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE run SET applied_config = :c WHERE id = :id"),
            {
                "c": '{"per_run_post_limit": 20, "per_run_duration_limit_s": 1800}',
                "id": run_id,
            },
        )
    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, BATCH_SIZE + 1)),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            ),
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(BATCH_SIZE + 1, BATCH_SIZE + 21)),
                next_cursor="cursor-page-3",
                signal=SourceSignal.OK,
            ),
        ]
    )
    loop = build_loop(config, client, source)
    loop.register()

    result = loop.run_cycle()

    outcome = result.outcome
    assert outcome is not None
    assert outcome.stop_reason is WireStopReason.LIMIT_REACHED
    assert outcome.error_code is None, "a budget is not an error (AMD-B02)"
    assert outcome.x_coverage_note_vi.strip()
    assert result.released is True
    assert scalar(engine, "SELECT status FROM run") == "running"
    assert scalar(engine, "SELECT stop_reason FROM run") == "limit_reached"
    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE
    assert source.read_count == 1, "no read after the limit was reached"
    assert alert_rows(engine) == 0, "a limit needs no person, so no alert (T-RUN-02)"


def test_a_second_cycle_resumes_from_the_server_checkpoint(
    app: FastAPI, engine: Engine, client: CollectorClient, config: CollectorConfig
) -> None:
    """The claim payload carries the ACKed watermark, and the collector starts from it.

    Measured as a row count -- the re-read of 7 known posts adds nothing, the 3 new ones do.
    """
    start_run(app)
    first = build_loop(config, client, RecordedSource(challenge_pages()))
    first.register()
    first.run_cycle()
    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE

    # The Owner clears the challenge and resumes: run.resume is an app action (T-RUN-10).
    from server.app.jobs.service import resume_run

    resume_run(app.state.job_context, run_id=str(scalar(engine, "SELECT id FROM run")))

    reread = [
        FeedPage(
            raw_posts=tuple(
                raw_post(i) for i in range(BATCH_SIZE + 1, BATCH_SIZE + DOWNLOADED_NOT_INGESTED + 4)
            ),
            next_cursor=None,
            signal=SourceSignal.END_OF_FEED,
        )
    ]
    second = build_loop(config, client, RecordedSource(reread))
    result = second.run_cycle()

    outcome = result.outcome
    assert outcome is not None
    assert outcome.completion is Completion.FEED_EXHAUSTED
    assert count(engine, "SELECT COUNT(*) FROM post") == BATCH_SIZE + DOWNLOADED_NOT_INGESTED + 3
    assert (
        scalar(engine, "SELECT MAX(acked_through_ingest_sequence) FROM checkpoint")
        == BATCH_SIZE + DOWNLOADED_NOT_INGESTED + 3
    )


def test_an_unknown_session_is_never_reported_as_ok(
    app: FastAPI, client: CollectorClient, config: CollectorConfig
) -> None:
    """CAP-P5 at the process boundary: the loop starts ``unknown`` and says so."""
    loop = CollectorLoop(
        config=config,
        client=client,
        source=RecordedSource([]),
        clock=lambda: datetime(2026, 9, 7, 8, 0, tzinfo=UTC),
        monotonic=lambda: 0.0,
        sleep=lambda _seconds: None,
    )
    assert loop.session.x_session_state is XSessionState.UNKNOWN
    assert loop.session.capabilities()["x_session_state"] == "unknown"
    assert loop.session.capabilities()["embedding_supported"] is False
    assert not loop.session.may_claim()


class RecordingAlertPort:
    """Wraps the **wired** adapter and records the connection it was handed.

    Not a substitute for it: every call is delegated to the real
    ``wiring._AlertIntentAdapter``, so what runs is production code. The wrapper exists only
    to make one thing observable that otherwise is not -- whether ``jobs.report_stop`` passed
    its open transaction down, which is the whole substance of ``CR-TC-COLLECTOR-11``.
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.connections: list[Any] = []
        self.results: list[str | None] = []

    def create_alert_intent(
        self, *, run_id: str, stop_reason: str, connection: Any = None
    ) -> str | None:
        self.connections.append(connection)
        result = self._inner.create_alert_intent(
            run_id=run_id, stop_reason=stop_reason, connection=connection
        )
        self.results.append(result)
        return result


def test_the_alert_intent_lands_in_the_callers_transaction(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
) -> None:
    """``CR-TC-COLLECTOR-11``, closed: the run-needs-you alert is written, exactly once.

    This was a strict xfail. The wired adapter used to open a second SQLite connection from
    inside ``jobs.report_stop``'s own transaction and get ``database is locked``, so on a real
    deployment the first challenge of the first run would have raised inside ``report_stop``
    and the Owner would never have been told. ``P0-FIX5`` threads the caller's connection
    through ``AlertIntentPort``, and this asserts the outcome instead of pinning the defect.

    Three things are measured, and the first is the one that was broken: the port is handed a
    live connection, the call completes rather than deadlocking, and exactly one
    ``telegram_alert`` intent exists for the run afterwards.
    """
    app.state.job_context = replace(
        app.state.job_context,
        alert_port=RecordingAlertPort(app.state.job_context.alert_port),
    )
    port = app.state.job_context.alert_port
    start_run(app)
    loop = build_loop(config, client, RecordedSource(challenge_pages()))
    loop.register()

    result = loop.run_cycle()

    assert result.outcome is not None
    assert result.outcome.stop_reason is WireStopReason.CHALLENGE_REQUIRED
    assert len(port.connections) == 1, "report_stop asked for exactly one alert"
    assert (
        port.connections[0] is not None
    ), "the port must receive the caller's open transaction (CR-TC-COLLECTOR-11)"
    assert alert_rows(engine) == 1, "exactly one run_alert intent (REQ-AC04)"
    assert scalar(engine, "SELECT subject_ref FROM outbox_intent") is not None
    assert scalar(engine, "SELECT status FROM run") == "needs_user"


def test_the_run_points_at_the_alert_intent_it_caused(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
    wire_log: list[dict[str, Any]],
) -> None:
    """``CR-TC-COLLECTOR-15``, closed: the run points at the alert, and the report says so.

    This was a strict xfail. ``server/app/wiring.py`` line 198 read
    ``result.get("delivery_intent_id") or result.get("id")`` while
    ``server/app/delivery/service.py`` returns ``intent_id`` on all three of its paths -- the
    key sets did not intersect, so the adapter always answered ``None``,
    ``jobs.report_stop`` correctly skipped its ``UPDATE run SET alert_intent_id``, and
    ``alert_created`` came back ``False`` on a report that had just created an alert. The
    outbox row existed; the run never learned about it. ``PKT-P0-FIX7`` fixed the one line.

    Two things are asserted, and the second is the one that was silently wrong:

    * ``run.alert_intent_id`` names the ``outbox_intent`` row -- and since
      ``run.alert_intent_id`` is ``REFERENCES outbox_intent (id)`` with ``foreign_keys`` ON,
      that UPDATE could not have committed unless the intent was already there in the same
      transaction. "One commit" is measured, not inferred.
    * the ``report_stop`` response says an alert was created, read from the wire.
      ``StopAck``'s own view of the same fact is asserted by
      :func:`test_stop_ack_carries_the_servers_answer_on_a_200`.
    """
    start_run(app)
    loop = build_loop(config, client, RecordedSource(challenge_pages()))
    loop.register()

    loop.run_cycle()

    assert alert_rows(engine) == 1
    intent_id = scalar(engine, "SELECT id FROM outbox_intent WHERE intent_type = 'telegram_alert'")
    assert intent_id is not None
    assert scalar(engine, "SELECT alert_intent_id FROM run") == intent_id

    stops = [call for call in wire_log if call["path"].endswith("/stop")]
    assert len(stops) == 1, "the segment reported its stop exactly once"
    body = stops[0]["body"]
    created = body.get("alert_intent_created", body.get("alert_created"))
    assert created is True, (
        "report_stop must report that it created the alert; got " f"{sorted(body)} -> {created!r}"
    )


def test_stop_ack_carries_the_servers_answer_on_a_200(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
    wire_log: list[dict[str, Any]],
) -> None:
    """``CR-TC-COLLECTOR-16``, closed on the 200 path: ``StopAck`` is no longer blank.

    The shape was disputed three ways -- the pinned fixture
    ``collection/c-challenge-mid-batch.json`` said ``{run{status, phase, outcome,
    stop_reason}, alert_intent_created, alert_intent_id}``, the service answered
    ``{run_status, stop_reason, alert_created}``, and this client parsed the fixture. The
    ruling made the fixture canonical and ``PKT-TC-SCHED-FIX2`` moved the service to it, so
    all three now agree.

    The assertion is on the **typed object**, against the **wire**: every field of
    :class:`StopAck` is compared with the body that actually came back. Asserting on DB rows
    instead -- which is what these tests did while the shapes disagreed -- would have gone on
    passing with a ``StopAck`` whose three fields were empty, and a collector process that
    cannot tell whether the Owner was alerted is exactly the failure this pins.
    """
    start_run(app)
    loop = build_loop(config, client, RecordedSource(challenge_pages()))
    loop.register()

    outcome = loop.run_cycle().outcome

    assert outcome is not None
    ack = outcome.stop_ack
    assert ack is not None

    stops = [call for call in wire_log if call["path"].endswith("/stop")]
    assert len(stops) == 1
    assert stops[0]["status"] == 200
    body = stops[0]["body"]

    assert ack.run == body["run"], "StopAck.run is the server's run object, verbatim"
    assert ack.run["status"] == "needs_user"
    assert ack.run["stop_reason"] == "captcha", "the server stores captcha (T-RUN-09)"
    assert ack.alert_intent_created is body["alert_intent_created"] is True
    assert ack.alert_intent_id == body["alert_intent_id"]
    assert ack.alert_intent_id == scalar(
        engine, "SELECT alert_intent_id FROM run"
    ), "and it is the id the run points at"
    assert ack.echoed_code is None, "a 200 echoes no error code"


def test_stop_ack_carries_the_servers_answer_on_a_409(
    app: FastAPI,
    engine: Engine,
    client: CollectorClient,
    config: CollectorConfig,
    wire_log: list[dict[str, Any]],
) -> None:
    """``CR-TC-SCHED-08``: on the 409 echo the extra fields sit *beside* ``error``.

    ``a-feed-layout-changed`` answers a **successful** report with 409 and
    ``{error, run, alert_intent_created, alert_intent_id}``. Those three are siblings of
    ``error``, not entries in ``details_safe`` -- ``contracts/errors.yaml`` closes that object
    to each code's own ``details_safe_keys``, and ``run`` is not among them for any code, so
    reading them from there was a contract violation as well as a wrong answer.

    This client used to do exactly that and therefore returned a blank ``StopAck`` on the one
    path where a person has to be told something. The fix reads the siblings; this asserts it
    against the real 409.
    """
    start_run(app)
    readable = [raw_post(i) for i in range(1, 13)]
    unreadable = [
        {"x_post_id": f"19000000000000001{i:02d}", "author": {}, "url": "", "text": ""}
        for i in range(28)
    ]
    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(readable + unreadable),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            )
        ]
    )
    loop = build_loop(config, client, source)
    loop.register()

    outcome = loop.run_cycle().outcome

    assert outcome is not None
    assert outcome.stop_reason is WireStopReason.SOURCE_LAYOUT_CHANGED
    ack = outcome.stop_ack
    assert ack is not None

    stops = [call for call in wire_log if call["path"].endswith("/stop")]
    assert len(stops) == 1
    body = stops[0]["body"]
    assert stops[0]["status"] == 409, "the echo is a 409 on a report that was accepted"
    assert "error" in body

    # The three fields are siblings of `error`, and details_safe does not carry them.
    assert set(body) >= {"error", "run", "alert_intent_created", "alert_intent_id"}
    assert "run" not in (body["error"].get("details_safe") or {})

    assert ack.echoed_code is ErrorCode.SOURCE_LAYOUT_CHANGED
    assert ack.run == body["run"]
    assert ack.run["status"] == "blocked"
    assert ack.alert_intent_created is body["alert_intent_created"] is True
    assert ack.alert_intent_id == body["alert_intent_id"]

    # And the run really did land there: 12 of 40 parsed, one alert, blocked.
    assert count(engine, "SELECT COUNT(*) FROM post") == 12
    assert alert_rows(engine) == 1
    assert scalar(engine, "SELECT stop_reason FROM run") == "source_layout_changed"


def test_the_claim_response_validates_against_its_own_schema(
    app: FastAPI, client: CollectorClient, config: CollectorConfig
) -> None:
    """``CR-TC-COLLECTOR-12``, closed -- checked against the live response, not a copy.

    ``contracts/ports.yaml`` names ``worker-assignment.schema.json`` as both the request and
    the response schema of ``worker.claim_assignment``, and the schema is
    ``additionalProperties: false`` with an explicit ``required`` list. The payload used to
    fail it in seven places -- ``x_coverage_note_vi`` absent,
    ``search_config.source_limits`` an empty object where five ``const`` fields are required,
    ``tag_config_version_id`` null where a ULID is declared -- and ``SCHED-FIX1`` fixed all of
    them. Validating the **live body** rather than a hand-built copy is the point: this card's
    own contract test was green throughout, because it validated payloads it constructed
    itself.

    None of that is cosmetic for this card. ``source_limits`` is precisely the block
    ``contracts/ops/collector-probe.md`` §8 says is sent "để collector không phải suy diễn" --
    author-thread-only, no external replies, no id guessing, Chrome scoped to X. An empty
    object means the collector is told none of it, and the one place those limits are stated
    is a contract nobody is currently honouring on the wire. ``x_coverage_note_vi`` is the
    sentence AMD-B05 requires so that "completed" is never read as "all of X was swept".

    Still absent, and still worth saying: ``job_id``. The collector needs one for
    ``ingest-batch.schema.json``, and the schema's ``assignment`` does not carry it.
    ``SegmentRunner`` uses ``assignment_id``, which *is* the right value -- the jobs service
    sets ``assignment_lease.job_id`` to exactly that -- but the contract leaves it to be
    deduced rather than stating it (``CR-TC-COLLECTOR-14``).
    """
    import json as _json

    from jsonschema import Draft202012Validator

    schema = _json.loads(
        (REPO_ROOT / "contracts" / "schemas" / "worker-assignment.schema.json").read_text(
            encoding="utf-8"
        )
    )
    start_run(app)
    loop = build_loop(config, client, RecordedSource([]))
    loop.register()
    answer = client.claim_assignment(
        claim_request_id="claim-schema-check-0001",
        worker_instance_id=WORKER_ID,
        capabilities=loop.session.capabilities(),
    )
    assert "assignment" in answer, "the run is queued, so a claim must return work"

    errors = sorted(Draft202012Validator(schema).iter_errors(answer), key=lambda e: list(e.path))
    assert errors == [], "\n".join(f"{list(e.path)}: {e.message}" for e in errors)
