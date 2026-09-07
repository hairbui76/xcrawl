"""E1 + E2 -- a challenge lands mid-segment: the checkpoint holds, one alert, no self-resume.

Scenario SC04 (with SC03, SC20, SC21 alongside), fixture
``acceptance/fixtures/collection/c-challenge-mid-batch.json``, invariants I02, I10, I13.

What is real here and what is not
---------------------------------
The **ingest half is real**: ``ingest.submit_batch``, ``ingest.commit_checkpoint`` and
``ingest.get_receipt`` are served by ``server/app/ingest`` over the app that
``create_app()`` builds, against a SQLite database created by ``alembic upgrade head``. So
"20 rows are durable and 7 are not" is measured with ``SELECT COUNT(*)`` on a real table
inside a real transaction, which is what ``c-challenge-mid-batch``'s
``durable_rows_expected`` asks for.

The **worker half is a stub**. ``worker.claim_assignment`` / ``heartbeat`` / ``report_stop``
/ ``release_assignment`` have no server implementation yet -- they belong to
``TC-scheduler-lease-claim``, which has not run -- so :class:`WorkerStub` replays the wire
contract from ``contracts/http/openapi.yaml`` and the fixture. That boundary matters when
reading the results, and the tests say so where it bites: the "exactly one alert intent"
count is produced by the stub applying the contract's idempotency rule, so what these tests
*establish* is the collector-side half of that oracle -- that the collector sends one
distinct ``stop_report_id`` and reuses it on every repeat. The server-side half is the
scheduler card's to prove.

The X source is a :class:`RecordedSource` built here from synthetic pages. No browser, no
network, no X session, and nothing in this file is evidence about X's real behaviour --
that is gated behind SP1 (``contracts/ops/collector-probe.md`` §6) and belongs to
``TC-x-feasibility-probe``.

The four things this file measures
----------------------------------
1. **I02.** ``checkpoint.acked_through_ingest_sequence`` in the database is the same before
   and after the challenge, and the 7 posts that were downloaded have no rows.
2. **I10.** The number of source reads does not increase after the stop is reported, the
   runner never calls ``claim_assignment`` again, and no code path touches a verification
   page.
3. **REQ-AC04.** Two reports of the same stop carry the same ``stop_report_id``, and the
   second creates no second alert.
4. **Resume comes from the server.** After the Owner resumes, the collector claims again and
   reads its cursor out of the *assignment's* checkpoint -- never out of anything this
   process remembered.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from collector.app.client import CollectorClient, WireStopReason
from collector.app.reader import (
    Completion,
    FeedPage,
    RecordedSource,
    SegmentRunner,
    SourceSignal,
    requires_owner_action,
    resume_position,
)
from collector.app.session import ChromeProfile, CollectorSession, XSessionState
from server.app.db import create_sqlite_engine
from server.app.ingest.service import IngestContext, LeaseSnapshot
from server.app.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "acceptance" / "fixtures" / "collection" / "c-challenge-mid-batch.json"

OWNER_ID = "01J0WNER100000000000000000"
RUN_ID = "6PNQ047XA29K4GVSEEXF8WFNJT"
JOB_ID = "DHMAQFP0HX86VVAWN9W2Z7YRSN"
ASSIGNMENT_ID = "KZA8XXCYQBY4190TVQJ05NMPZ3"
LEASE_ID = "08ZSTPHZ4MKNY25V807H2ESQCC"
WORKER_INSTANCE_ID = "FB6MS98AKQTGXNW6Q3EC11G2VF"
COLLECTOR_TOKEN = "collector-token-for-tests-only-not-a-secret"

#: Fixture ``c``: batch 1 is 20 posts, and 7 more are downloaded before the challenge.
BATCH_ONE_POSTS = 20
DOWNLOADED_NOT_INGESTED = 7


# --------------------------------------------------------------------------- the real server


def build_database(path: Path) -> Engine:
    """A WAL SQLite database carrying the shipped schema, plus the single ``owner`` row.

    The schema comes from ``alembic upgrade head``, not from DDL restated in a test: a
    second source of schema truth is the drift these tests exist to catch.
    """
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous

    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at) "
                "VALUES (:id, 1, 'Owner', 'Asia/Ho_Chi_Minh', '2026-09-06T00:00:00.000Z')"
            ),
            {"id": OWNER_ID},
        )
    return engine


class FakeAssignments:
    """The one question ingest asks about leases: what is the current epoch of this job.

    Not a reimplementation of the lease state machine -- that is
    ``TC-scheduler-lease-claim``'s domain and writing it here would be writing another
    card's logic inside this one's tests.
    """

    def __init__(self, epoch: int = 1) -> None:
        self.epoch = epoch
        self.revoked = False

    def lease_snapshot(self, *, job_id: str, lease_id: str) -> LeaseSnapshot | None:
        if lease_id != LEASE_ID:
            return None
        return LeaseSnapshot(run_id=RUN_ID, lease_epoch=self.epoch, revoked=self.revoked)


# --------------------------------------------------------------------------- the worker stub


class WorkerStub:
    """``worker.*`` as the wire contract describes it, with a call log.

    It implements exactly the parts the fixture pins: a claim returns an assignment carrying
    the *server's* checkpoint; a heartbeat validates the epoch; a stop report is idempotent
    on ``assignment_id + stop_report_id`` and therefore creates at most one alert intent per
    run (T-RUN-09, REQ-AC04).
    """

    def __init__(self, *, lease_epoch: int = 1, acked_through: int = 0) -> None:
        self.lease_epoch = lease_epoch
        self.acked_through = acked_through
        self.checkpoint_sequence = 0
        self.cursor_token: str | None = None
        self.cursor_state = "valid"
        self.calls: list[str] = []
        self.stop_reports: list[dict[str, Any]] = []
        self.alert_intents: set[str] = set()
        self.run = {
            "status": "running",
            "phase": "collecting",
            "outcome": None,
            "stop_reason": None,
        }

    # -- helpers -----------------------------------------------------------

    def assignment_body(self) -> dict[str, Any]:
        return {
            "assignment": {
                "assignment_id": ASSIGNMENT_ID,
                "run_id": RUN_ID,
                "job_id": JOB_ID,
                "phase": "collecting",
                "trigger_type": "scheduled",
                "catch_up_window": None,
                "lease": {
                    "lease_id": LEASE_ID,
                    "lease_epoch": self.lease_epoch,
                    "ttl_s": 120,
                    "heartbeat_interval_s": 30,
                    "expires_at": "2026-09-07T08:02:00.000Z",
                },
                "capability_requirements": {
                    "requires_chrome_profile": True,
                    "requires_x_session_ok": True,
                },
                "search_config": {
                    "tags": ["protein folding"],
                    "tag_config_version_id": "01JTAGCFG00000000000000000",
                    "source_limits": {
                        "author_thread_only": True,
                        "external_replies": "excluded",
                        "image_only_post_policy": "post_only_no_id_guess",
                        "chrome_scope": "x_only",
                        "paper_metadata_source": "server_api",
                        "max_thread_context_posts": 50,
                    },
                },
                "stop_conditions": {
                    "max_posts": 200,
                    "max_duration_s": 1800,
                    "evaluation": "first_of_either",
                    "on_challenge": "report_stop_and_halt",
                    "on_blocked": "report_stop_and_halt_no_rotation",
                },
                "checkpoint": {
                    "phase": "collecting",
                    "cursor_token": self.cursor_token,
                    "cursor_state": self.cursor_state,
                    "acked_through_ingest_sequence": self.acked_through,
                    "items_ingested_total": self.acked_through,
                    "checkpoint_sequence": self.checkpoint_sequence,
                },
                "is_resume": self.checkpoint_sequence > 0,
                "x_coverage_note_vi": (
                    "Đợt này chỉ quét phần feed mà phiên Chrome của dự án nhìn thấy; "
                    "'hoàn tất' KHÔNG có nghĩa đã quét đủ toàn bộ X."
                ),
            }
        }

    def _error(self, code: ErrorCode, status: int) -> httpx.Response:
        return httpx.Response(
            status,
            json={
                "code": code.value,
                "scope": "request",
                "retry_class": "none",
                "message_safe": "Yêu cầu dùng phiên làm việc đã cũ và bị từ chối.",
                "correlation_id": "01JBQZ9K7M3N4P5Q6R7S8T9VWX",
                "details_safe": {"lease_epoch_current": self.lease_epoch},
                "retry_after_ms": None,
            },
        )

    # -- routing -----------------------------------------------------------

    def handle(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = json.loads(request.content) if request.content else {}

        if path.endswith("/registrations"):
            self.calls.append("register")
            return httpx.Response(
                200,
                json={
                    "registered_at": "2026-09-07T08:00:01.000Z",
                    "heartbeat_interval_s": 30,
                    "lease_granted": False,
                },
            )

        if path.endswith("/assignments/claim"):
            self.calls.append("claim")
            return httpx.Response(200, json=self.assignment_body())

        if path.endswith("/heartbeat"):
            self.calls.append("heartbeat")
            beat = body["heartbeat_request"]
            if beat["lease_epoch"] < self.lease_epoch:
                return self._error(ErrorCode.STALE_LEASE, 409)
            return httpx.Response(
                200,
                json={
                    "lease_valid": True,
                    "lease_expires_at": "2026-09-07T08:04:00.000Z",
                    "directive": "continue",
                },
            )

        if path.endswith("/stop"):
            self.calls.append("stop")
            if body["lease_epoch"] < self.lease_epoch:
                return self._error(ErrorCode.STALE_LEASE, 409)
            self.stop_reports.append(dict(body))
            reason = body["stop_reason"]
            created = False
            # Idempotency scope from contracts/ports.yaml: assignment_id + stop_report_id.
            key = f"{body['assignment_id']}:{body['stop_report_id']}"
            if reason in {"challenge_required", "session_expired", "source_layout_changed"}:
                created = key not in self.alert_intents
                self.alert_intents.add(key)
            if reason in {"challenge_required", "session_expired"}:
                self.run = {
                    "status": "needs_user",
                    "phase": "collecting",
                    "outcome": None,
                    "stop_reason": "captcha" if reason == "challenge_required" else reason,
                }
            elif reason == "limit_reached":
                self.run = {
                    "status": "running",
                    "phase": "enriching",
                    "outcome": None,
                    "stop_reason": "limit_reached",
                }
            return httpx.Response(
                200,
                json={
                    "run": self.run,
                    "alert_intent_created": created,
                    "alert_intent_id": "YEDFRWZN2T1BW8KH66N70M7DAJ" if created else None,
                },
            )

        if path.endswith("/release"):
            self.calls.append("release")
            return httpx.Response(200, json={"released": True})

        raise AssertionError(f"the collector called an unexpected worker path: {path}")


# --------------------------------------------------------------------------- wiring


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_database(tmp_path / "rr.db")


@pytest.fixture
def assignments() -> FakeAssignments:
    """The lease epoch as *ingest* sees it.

    Shared with the test so a resume can move both halves at once: the server would raise
    the epoch in one transaction, and leaving ingest on the old one would make every
    resumed batch fail ``STALE_LEASE`` for a reason the collector did not cause.
    """
    return FakeAssignments()


@pytest.fixture
def app(engine: Engine, assignments: FakeAssignments) -> FastAPI:
    application = create_app()
    application.state.collector_token = COLLECTOR_TOKEN
    application.state.ingest_context = IngestContext(
        engine=engine, owner_id=OWNER_ID, assignment=assignments
    )
    return application


@pytest.fixture
def worker() -> WorkerStub:
    return WorkerStub()


@pytest.fixture
def client(app: FastAPI, worker: WorkerStub) -> Any:
    """A real :class:`CollectorClient` whose transport splits worker.* from ingest.*.

    ``ingest.*`` goes to the real application through ``TestClient``; ``worker.*`` goes to
    the stub. The collector under test cannot tell the difference, which is the point: it is
    the production client object, not a test double of one.
    """
    server = TestClient(app)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/v1/workers/"):
            return worker.handle(request)
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
        return httpx.Response(response.status_code, json=response.json())

    collector_client = CollectorClient(
        base_url="https://server.local",
        token=COLLECTOR_TOKEN,
        transport=httpx.MockTransport(handler),
        sleep=lambda _seconds: None,
    )
    yield collector_client
    collector_client.close()
    server.close()


def raw_post(index: int) -> dict[str, Any]:
    """A synthetic X post that parses cleanly. Not a recording of X; a shape."""
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


def challenge_pages() -> list[FeedPage]:
    """Fixture ``c``'s timeline as pages: 20 ingested, 7 downloaded, then the challenge."""
    return [
        FeedPage(
            raw_posts=tuple(raw_post(i) for i in range(1, BATCH_ONE_POSTS + 1)),
            next_cursor="cursor-page-2",
            signal=SourceSignal.OK,
        ),
        FeedPage(
            raw_posts=tuple(
                raw_post(i)
                for i in range(BATCH_ONE_POSTS + 1, BATCH_ONE_POSTS + DOWNLOADED_NOT_INGESTED + 1)
            ),
            next_cursor="cursor-page-3",
            signal=SourceSignal.OK,
        ),
        FeedPage(signal=SourceSignal.CHALLENGE),
    ]


def runner_for(
    client: CollectorClient, worker: WorkerStub, source: RecordedSource
) -> SegmentRunner:
    assignment = worker.assignment_body()["assignment"]
    return SegmentRunner(
        client=client,
        source=source,
        assignment=assignment,
        clock=lambda: "2026-09-07T08:00:00.000Z",
        monotonic=lambda: 0.0,
        batch_size=BATCH_ONE_POSTS,
    )


def row_count(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())


def checkpoint_high_water(engine: Engine) -> int:
    with engine.connect() as connection:
        value = connection.execute(
            text("SELECT MAX(acked_through_ingest_sequence) FROM checkpoint")
        ).scalar_one()
    return int(value or 0)


# --------------------------------------------------------------------------- the tests


def test_challenge_keeps_the_checkpoint_at_the_last_acked_batch(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """I02 measured in the database: 20 rows durable, 7 downloaded rows absent.

    ``c-challenge-mid-batch.durable_rows_expected``: "post: +20 hàng (lô 1). 7 bài của lô 2
    KHÔNG có hàng nào." and "checkpoint.acked_through_ingest_sequence = 20 tại mọi thời điểm
    của fixture này". Both are counted here with SQL against the real schema, not read off a
    log line.
    """
    source = RecordedSource(challenge_pages())
    outcome = runner_for(client, worker, source).run_segment()

    assert outcome.completion is Completion.STOPPED
    assert outcome.stop_reason is WireStopReason.CHALLENGE_REQUIRED
    assert outcome.error_code is ErrorCode.X_CHALLENGE_REQUIRED

    assert row_count(engine, "post") == BATCH_ONE_POSTS
    assert outcome.posts_ingested_new == BATCH_ONE_POSTS
    assert outcome.posts_discarded_unsubmitted == DOWNLOADED_NOT_INGESTED

    high_water = checkpoint_high_water(engine)
    assert high_water == BATCH_ONE_POSTS
    assert outcome.acked_through_ingest_sequence == high_water
    assert outcome.stop_ack is not None
    assert worker.stop_reports[0]["last_acked_ingest_sequence"] == high_water


def test_no_source_read_happens_after_the_stop_is_reported(
    client: CollectorClient, worker: WorkerStub
) -> None:
    """I10 and the fixture's oracle: "Số request thu thập mới giữa sự kiện 3 và 7 = 0".

    The counter belongs to the source, so this measures the collector's own behaviour rather
    than the server's tolerance of it. The stop is reported *after* the last read, and the
    runner returns instead of looping.
    """
    source = RecordedSource(challenge_pages())
    runner = runner_for(client, worker, source)
    outcome = runner.run_segment()

    reads_at_stop = source.read_count
    assert reads_at_stop == 3, "one read per page, and the challenge page is the last"
    assert worker.calls.count("stop") == 1
    assert source.read_count == reads_at_stop
    assert "claim" not in worker.calls, "the runner must not re-acquire work by itself"
    assert requires_owner_action(outcome)


def test_reporting_the_same_stop_twice_creates_one_alert(
    client: CollectorClient, worker: WorkerStub
) -> None:
    """REQ-AC04: "Báo lại CÙNG stop_report_id ... KHÔNG tạo alert thứ hai".

    The collector-side half -- the part this card owns -- is that the id is *stable*: the
    second report carries the same ``stop_report_id`` as the first. The alert count itself is
    produced by :class:`WorkerStub` applying the contract's idempotency rule, so it
    corroborates rather than proves; proving it server-side is ``TC-scheduler-lease-claim``'s
    job.
    """
    source = RecordedSource(challenge_pages())
    runner = runner_for(client, worker, source)
    runner.run_segment()

    first_id = runner.stop_report_id
    ack = client.report_stop(
        assignment_id=ASSIGNMENT_ID,
        stop_report_id=runner.stop_report_id,
        lease_id=LEASE_ID,
        lease_epoch=1,
        stop_reason=WireStopReason.CHALLENGE_REQUIRED,
        last_acked_ingest_sequence=BATCH_ONE_POSTS,
    )

    assert runner.stop_report_id == first_id
    assert {report["stop_report_id"] for report in worker.stop_reports} == {first_id}
    assert len(worker.stop_reports) == 2
    assert worker.stop_reports[0]["stop_reason"] == "challenge_required"
    assert ack.alert_intent_created is False
    assert len(worker.alert_intents) == 1


def test_the_server_moves_the_run_to_needs_user_not_the_collector(
    client: CollectorClient, worker: WorkerStub
) -> None:
    """T-RUN-09: the collector reports ``challenge_required``; the server stores ``captcha``.

    The collector owns no run state (card §4: "Collector KHÔNG sở hữu state nào của server"),
    so the transition is observed in the response, not asserted locally.
    """
    source = RecordedSource(challenge_pages())
    outcome = runner_for(client, worker, source).run_segment()

    assert outcome.stop_ack is not None
    assert outcome.stop_ack.run["status"] == "needs_user"
    assert outcome.stop_ack.run["stop_reason"] == "captcha"
    assert worker.stop_reports[0]["stop_reason"] == "challenge_required"
    assert outcome.x_session_state is XSessionState.CHALLENGE


def test_resume_takes_its_cursor_from_the_server_not_from_this_process(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """After an Owner resume, the collector claims again and reads the server's checkpoint.

    The re-claim is performed by the *test*, not by the runner: that separation is the
    point. ``run.resume`` (T-RUN-10) is an Owner action, the lease epoch increments, and only
    then does a collector claim -- so the collector picks up at
    ``acked_through_ingest_sequence`` because the assignment told it to, not because it
    remembered anything.
    """
    first = RecordedSource(challenge_pages())
    runner_for(client, worker, first).run_segment()
    durable_before = checkpoint_high_water(engine)

    # The Owner clears the challenge and resumes: the server revokes and re-issues.
    worker.lease_epoch += 1
    worker.acked_through = durable_before
    worker.checkpoint_sequence = 1
    worker.cursor_token = "cursor-page-2"

    answer = client.claim_assignment(
        claim_request_id="claim-2026-09-07-0002-aaaa",
        worker_instance_id=WORKER_INSTANCE_ID,
        capabilities=CollectorSession(
            worker_instance_id=WORKER_INSTANCE_ID,
            profile=ChromeProfile(user_data_dir=Path("/srv/rr/profile"), ready=True),
            x_session_state=XSessionState.OK,
        ).capabilities(),
    )
    assignment = answer["assignment"]

    assert assignment["lease"]["lease_epoch"] == 2, "a resume never continues on the old lease"
    assert assignment["is_resume"] is True
    assert assignment["checkpoint"]["acked_through_ingest_sequence"] == durable_before
    assert resume_position(assignment) == ("cursor-page-2", "valid")


def test_resumed_segment_ingests_only_the_posts_that_are_new(
    client: CollectorClient,
    worker: WorkerStub,
    engine: Engine,
    assignments: FakeAssignments,
) -> None:
    """``AMD-B05``: re-reading is allowed; the commitment is no duplicate *ingest*.

    The second segment re-reads the 7 posts the challenge interrupted plus 3 genuinely new
    ones, and the measurement is the row count -- the fixture is explicit that request count
    is *not* the oracle.
    """
    runner_for(client, worker, RecordedSource(challenge_pages())).run_segment()
    rows_after_first = row_count(engine, "post")

    worker.lease_epoch += 1
    assignments.epoch = worker.lease_epoch
    worker.acked_through = checkpoint_high_water(engine)
    worker.checkpoint_sequence = 1

    reread = [
        FeedPage(
            raw_posts=tuple(
                raw_post(i)
                for i in range(BATCH_ONE_POSTS + 1, BATCH_ONE_POSTS + DOWNLOADED_NOT_INGESTED + 4)
            ),
            next_cursor=None,
            signal=SourceSignal.END_OF_FEED,
        )
    ]
    second = RecordedSource(reread)
    outcome = SegmentRunner(
        client=client,
        source=second,
        assignment=worker.assignment_body()["assignment"],
        clock=lambda: "2026-09-07T08:10:00.000Z",
        monotonic=lambda: 0.0,
        batch_size=BATCH_ONE_POSTS,
    ).run_segment()

    assert outcome.completion is Completion.FEED_EXHAUSTED
    assert outcome.stop_reason is None, "an exhausted feed is not a stop reason (I13)"
    assert row_count(engine, "post") == rows_after_first + DOWNLOADED_NOT_INGESTED + 3
    assert "release" in worker.calls


def test_an_empty_feed_is_not_a_limit_and_not_a_failure(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """I13: three outcomes that must stay distinct.

    Nothing was found, nothing was stopped, nothing failed. The run must not report a stop
    reason, must not claim a limit, and must leave no post rows behind.
    """
    source = RecordedSource([FeedPage(signal=SourceSignal.END_OF_FEED)])
    outcome = runner_for(client, worker, source).run_segment()

    assert outcome.completion is Completion.FEED_EXHAUSTED
    assert outcome.is_empty
    assert outcome.stop_reason is None
    assert outcome.limit_kind is None
    assert row_count(engine, "post") == 0
    assert not requires_owner_action(outcome)


def test_hitting_the_post_limit_stops_with_a_coverage_note(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """SC03 / T-RUN-02 / fixture ``e``: a limit is a stop, not a failure, and the note is set."""
    assignment = worker.assignment_body()["assignment"]
    assignment["stop_conditions"]["max_posts"] = 20

    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, 21)),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            ),
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(21, 41)),
                next_cursor="cursor-page-3",
                signal=SourceSignal.OK,
            ),
        ]
    )
    outcome = SegmentRunner(
        client=client,
        source=source,
        assignment=assignment,
        clock=lambda: "2026-09-07T08:00:00.000Z",
        monotonic=lambda: 0.0,
        batch_size=20,
    ).run_segment()

    assert outcome.stop_reason is WireStopReason.LIMIT_REACHED
    assert outcome.error_code is None, "a budget is not an error (AMD-B02)"
    assert outcome.limit_kind is not None
    assert outcome.x_coverage_note_vi.strip()
    assert row_count(engine, "post") == 20
    assert source.read_count == 1, "no read happens after the limit is reached"
    assert worker.stop_reports[0]["x_coverage_note_vi"].strip()
    assert not requires_owner_action(outcome)


def test_a_layout_change_commits_what_parsed_and_stops(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """T-RUN-24 / fixture ``a``: the readable part is durable, the rest is never guessed.

    The distinction from a challenge is exactly this line: there the buffer is dropped,
    because the source could not be trusted; here the request succeeded and the parsed items
    are sound, so they commit and only the unreadable ones are refused.
    """
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
    outcome = runner_for(client, worker, source).run_segment()

    assert outcome.stop_reason is WireStopReason.SOURCE_LAYOUT_CHANGED
    assert outcome.error_code is ErrorCode.SOURCE_LAYOUT_CHANGED
    assert row_count(engine, "post") == 12, "12 of 40, exactly as the fixture says"
    assert "author.handle" in outcome.missing_required_fields
    assert source.read_count == 1
    report = worker.stop_reports[0]
    assert report["posts_seen"] == 40
    assert report["posts_parsed_ok"] == 12
    assert report["missing_required_fields"]
    assert len(worker.alert_intents) == 1


def test_a_rate_limit_stops_the_segment_without_blocking_the_run(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """Stop gate ``SG-RATE`` / T-RUN-25: ``rate_limited``, a coverage note naming the moment,
    no retry inside the run, and no alert intent."""
    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, 21)),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            ),
            FeedPage(signal=SourceSignal.RATE_LIMITED),
        ]
    )
    outcome = runner_for(client, worker, source).run_segment()

    assert outcome.stop_reason is WireStopReason.RATE_LIMITED
    assert outcome.error_code is ErrorCode.RATE_LIMITED
    assert row_count(engine, "post") == 20, "everything ACKed before the limit stays"
    assert source.read_count == 2, "no further read after the source asked us to slow down"
    report = worker.stop_reports[0]
    assert report["x_coverage_note_vi"].strip()
    assert report["rate_limited_at"], "T-RUN-25 requires the note to name the moment"
    assert worker.alert_intents == set(), "a rate limit needs no person (T-RUN-25)"
    assert not requires_owner_action(outcome)


def test_a_stale_lease_stops_the_segment_and_submits_nothing_further(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """SC20 / fixture ``f``: the epoch moved on, so the old worker writes nothing more.

    The heartbeat is what discovers it. No stop is reported: a report carrying the dead lease
    would be refused as well, and T-RUN-14 gives the transition to the server's sweep.
    """
    assignment = worker.assignment_body()["assignment"]
    ticks = iter([0.0, 0.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0])
    last = [0.0]

    def monotonic() -> float:
        last[0] = next(ticks, last[0])
        return last[0]

    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, 21)),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            ),
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(21, 41)),
                next_cursor="cursor-page-3",
                signal=SourceSignal.OK,
            ),
        ]
    )
    runner = SegmentRunner(
        client=client,
        source=source,
        assignment=assignment,
        clock=lambda: "2026-09-07T08:00:00.000Z",
        monotonic=monotonic,
        batch_size=20,
    )
    rows_before_revocation = 20
    worker.lease_epoch = 2  # another worker claimed; this segment holds epoch 1

    outcome = runner.run_segment()

    assert outcome.completion is Completion.LEASE_LOST
    assert outcome.error_code is ErrorCode.STALE_LEASE
    assert outcome.stop_reason is None, "a dead lease cannot carry a stop report"
    assert "stop" not in worker.calls
    assert row_count(engine, "post") <= rows_before_revocation


def test_the_collector_never_writes_the_database_directly(engine: Engine) -> None:
    """``SL-7``: the collector process has no DB driver and no path to the volume.

    Asserted on the package's imports rather than on behaviour: the check that matters is
    that nothing in ``collector/app`` can reach SQLAlchemy, the server package, or a
    database URL at all.
    """
    forbidden = ("sqlalchemy", "sqlite3", "server.app", "alembic")
    for module in sorted((REPO_ROOT / "collector" / "app").glob("*.py")):
        text_content = module.read_text(encoding="utf-8")
        import_lines = [
            line
            for line in text_content.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        ]
        for line in import_lines:
            for name in forbidden:
                assert name not in line, f"{module.name} imports {name}: {line}"


# --------------------------------------------------------------------------- E2: fault injection


def test_a_write_failure_leaves_the_cursor_where_it_was(
    client: CollectorClient, worker: WorkerStub, engine: Engine
) -> None:
    """E2 -- T-RUN-19: the server cannot write, so nothing is ACKed and nothing advances.

    The fault is injected at the SQLite layer with
    :class:`~server.app.db.faults.WriteFaultInjector`, not simulated by returning a canned
    error: the point of an E2 case is that the failure happens where a real one would, in
    the middle of ``TXN-ingest-batch``.

    What the collector must then do is *nothing clever*. T-RUN-19's forbidden list is short
    and blunt: do not ACK an uncommitted mutation, and do not advance the cursor or
    ``acked_through_ingest_sequence``. So the segment ends as ``STORAGE_UNAVAILABLE``, the
    checkpoint high-water mark stays at zero, and no stop is reported -- the server observed
    its own storage failure and does not need the collector to tell it.
    """
    from server.app.db.faults import WriteFaultInjector

    injector = WriteFaultInjector(engine)
    source = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, 21)),
                next_cursor="cursor-page-2",
                signal=SourceSignal.OK,
            )
        ]
    )
    runner = runner_for(client, worker, source)

    with injector.disk_full():
        outcome = runner.run_segment()

    assert outcome.completion is Completion.STORAGE_UNAVAILABLE
    assert outcome.error_code is ErrorCode.STORAGE_WRITE_FAILED
    assert outcome.acked_through_ingest_sequence == 0, "an unACKed batch advances nothing"
    assert row_count(engine, "post") == 0
    assert row_count(engine, "ingest_receipt") == 0
    assert checkpoint_high_water(engine) == 0
    assert "stop" not in worker.calls
    assert injector.writes_attempted > 0, "the fault must actually have been reached"


def test_recovery_after_a_write_failure_resumes_from_the_server_checkpoint(
    client: CollectorClient, worker: WorkerStub, engine: Engine, app: FastAPI
) -> None:
    """E2, second half: once storage is healthy again the work commits normally.

    T-RUN-19's own recovery note -- "nếu lease còn ⇒ worker tiếp tục từ checkpoint đã ACK" --
    and the measurement is that the retry produces exactly 20 rows, not 40: the first attempt
    wrote nothing, so there is nothing to deduplicate against.

    Storage is brought back through the guard's **own** public recovery path -- three spaced
    successful probes, the numbers ``server/app/storage/health.py`` takes from
    ``contracts/state/storage.yaml`` -- rather than by reaching in and setting a flag. The
    recovery machine belongs to ``TC-storage-write-blocked-readiness``; this test drives it,
    it does not reimplement it.
    """
    from datetime import UTC, datetime, timedelta

    from server.app.db.faults import WriteFaultInjector
    from server.app.storage.health import PROBE_CONSECUTIVE_SUCCESS, PROBE_INTERVAL_SECONDS

    injector = WriteFaultInjector(engine)
    pages = [
        FeedPage(
            raw_posts=tuple(raw_post(i) for i in range(1, 21)),
            next_cursor="cursor-page-2",
            signal=SourceSignal.OK,
        )
    ]
    with injector.disk_full():
        runner_for(client, worker, RecordedSource(list(pages))).run_segment()
    assert row_count(engine, "post") == 0

    guard = app.state.storage_guard
    moment = datetime.now(UTC)
    for _probe in range(PROBE_CONSECUTIVE_SUCCESS):
        moment += timedelta(seconds=PROBE_INTERVAL_SECONDS + 1)
        guard.record_probe(success=True, at=moment)
    assert guard.current_health().value == "healthy"

    second = RecordedSource(
        [
            FeedPage(
                raw_posts=tuple(raw_post(i) for i in range(1, 21)),
                next_cursor=None,
                signal=SourceSignal.END_OF_FEED,
            )
        ]
    )
    outcome = runner_for(client, worker, second).run_segment()

    assert outcome.completion is Completion.FEED_EXHAUSTED
    assert row_count(engine, "post") == 20
    assert checkpoint_high_water(engine) == 20
