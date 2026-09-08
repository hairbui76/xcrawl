"""E1 + E2 -- Telegram fails for good, and the app still has the whole report.

Fixture ``telegram/c-permanent-failure-report-intact`` is ``I09`` stated as counts:
``report__deleted = 0``, ``run_status_changes = 0``, ``telegram.sendMessage = 4`` ("4 =
telegram_send_attempts của retry-policy.yaml; hết budget ⇒ failed"), and a hash oracle
``report.content_hash sau sự kiện 2 == trước sự kiện 1``.

Three more cases belong with it because they are the same promise from other directions:

* ``reporting/c-tag-changed-after-publish-before-send`` -- the tag set changes between two
  attempts and the payload hash does not move (``I05``, AMD-B01).
* ``telegram/d-unlink-before-send-cancelled`` -- unlink before the first send: ``cancelled``,
  zero attempts, zero outbound calls.
* ``telegram/e-relink-old-generation-cancelled`` -- a new generation does not inherit the old
  generation's digest.

And one E2 case: with storage refusing writes, the attempt row cannot be committed, so the
network call must not happen at all (``STORAGE_WRITE_FAILED``, §7 of the card).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import (
    DeliveryIntentKind,
    DeliveryPartState,
    DeliveryState,
)
from sqlalchemy import Engine, event, text

from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector
from server.app.delivery.service import (
    DeliveryContext,
    DeliveryError,
    LinkSnapshot,
    PermanentFailure,
    PublishedDigest,
    RetryableFailure,
    SendOutcome,
    Sent,
    create_intent,
    dispatch_next,
    get_status,
)
from server.app.storage.guard import StorageGuard

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
REPORT_ID = "01JREP0RT10000000000000000"
RUN_ID = "01JRVN10000000000000000000"
CHAT_ID = "111111111"
LINK_GENERATION = 3
REPORT_HASH = "sha256:" + "d" * 64
#: 36 characters -- ``report.report_build_id`` is CHECKed for exactly that length (UUIDv4).
REPORT_BUILD_ID = "2f7b1d34-6c1a-4b0e-9a77-5c2e8f0b3d19"
EMBEDDING_GENERATION_ID = "01JEMBGEN20000000000000000"

#: Any statement that would write the two tables delivery must never touch. ``I05`` forbids
#: changing a published report; ``I09`` forbids delivery deciding a run's outcome.
_FORBIDDEN_WRITE = re.compile(
    r"^\s*(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+[\"'`\[]?(report|run)\b", re.IGNORECASE
)


def build_database(path: Path) -> Engine:
    """``alembic upgrade head`` plus the ``owner``, ``report`` and ``run`` rows this file reads.

    All three tables are now the shipped ones: ``report`` came with
    ``TC-report-coverage-publish-cas`` (revision 0010) and ``run`` with
    ``TC-scheduler-lease-claim``, so the three-column stand-ins this file used to create are
    gone and the ``I05``/``I09`` oracles below are measured against the **real** rows. That is
    strictly stronger: a delivery that wrote to either table would now hit real constraints and
    a real column set, not a test-local imitation of one.
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
        # `report.embedding_generation_id` is a real foreign key, so the generation it points
        # at is seeded first. `expected_vector_count` is written although the column is
        # nullable -- see CR-TC-DELIVERY-11.
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                "dimension, normalization, state, expected_vector_count, built_vector_count, "
                "created_at, activated_at) "
                "VALUES (:id, :owner, 'multilingual-e5-small', '1.0.0', 4, 'l2', 'active', 0, 0, "
                "'2026-09-06T00:00:00.000Z', '2026-09-06T00:00:00.000Z')"
            ),
            {"id": EMBEDDING_GENERATION_ID, "owner": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO report (id, owner_id, coverage_from, coverage_to, "
                "tag_config_version_id, embedding_generation_id, report_build_id, status, "
                "quality, published_at, content_hash, selection_version, created_at, updated_at) "
                "VALUES (:id, :owner, '2026-09-06T00:00:00.000Z', '2026-09-07T00:00:00.000Z', "
                "'CTCV-1', :generation, :build_id, 'published', 'complete', "
                "'2026-09-07T13:00:00.000Z', :hash, 'sel-1', '2026-09-07T13:00:00.000Z', "
                "'2026-09-07T13:00:00.000Z')"
            ),
            {
                "id": REPORT_ID,
                "owner": OWNER_ID,
                "generation": EMBEDDING_GENERATION_ID,
                "build_id": REPORT_BUILD_ID,
                "hash": REPORT_HASH,
            },
        )
        # Fixture `telegram/c`'s run: completed, outcome `complete`, no stop reason. The
        # counters are the zero state of a run that finished cleanly; `run` requires them.
        connection.execute(
            text(
                "INSERT INTO run (id, owner_id, trigger_type, phase, status, outcome, "
                "applied_config, created_at, schedule_occurrence_ids, current_lease_epoch, "
                "attempt_count, posts_observed_total, posts_ingested_new, limit_hit, "
                "cursor_invalidated) "
                "VALUES (:id, :owner, 'scheduled', 'reporting', 'completed', 'complete', "
                "'{}', '2026-09-06T00:00:00.000Z', '[]', 1, 1, 0, 0, 0, 0)"
            ),
            {"id": RUN_ID, "owner": OWNER_ID},
        )
    return engine


def snapshot_report_and_run(engine: Engine) -> tuple[tuple[str, ...], tuple[str, ...]]:
    with engine.begin() as connection:
        report = connection.execute(
            text("SELECT status, content_hash, tag_config_version_id FROM report WHERE id = :id"),
            {"id": REPORT_ID},
        ).one()
        run = connection.execute(
            text("SELECT status, outcome FROM run WHERE id = :id"), {"id": RUN_ID}
        ).one()
    return tuple(report), tuple(run)


class WriteWatcher:
    """Records every statement the engine executes, so "never wrote" is measurable.

    A count of rows before and after would miss an UPDATE that happened to write the same
    values. Watching the statements catches the attempt itself, which is what ``I05`` and
    ``I09`` actually forbid.
    """

    def __init__(self, engine: Engine) -> None:
        self.statements: list[str] = []
        event.listen(engine, "before_cursor_execute", self._record)

    def _record(self, _conn, _cursor, statement, _params, _context, _many) -> None:  # type: ignore[no-untyped-def]
        self.statements.append(statement)

    @property
    def forbidden_writes(self) -> list[str]:
        return [s for s in self.statements if _FORBIDDEN_WRITE.match(s)]


@dataclass
class FakeLinkPort:
    generation: int = LINK_GENERATION
    active: bool = True
    chat_id: str = CHAT_ID

    def current_link(self, *, owner_id: str) -> LinkSnapshot | None:
        return LinkSnapshot(chat_id=self.chat_id, generation=self.generation, active=self.active)


@dataclass
class FakeReportPort:
    """The published digest. ``rebuild_marker`` proves the payload is read, not re-derived.

    Fixture ``reporting/c`` changes the tag set between two attempts. A correct delivery
    re-reads the *published* content, so the blocks -- and therefore the payload hash -- are
    identical on both attempts. Flipping ``rebuild_marker`` simulates a builder that re-rendered
    from the current tags; the delivery must then refuse rather than send different bytes.
    """

    blocks: tuple[str, ...] = field(
        default_factory=lambda: ("Kỳ 2026-09-07 — hướng đang nổi", "Mục 1 — tiêu đề")
    )
    rebuild_marker: str = ""

    def published_digest(self, *, owner_id: str, report_id: str) -> PublishedDigest | None:
        blocks = tuple(block + self.rebuild_marker for block in self.blocks)
        return PublishedDigest(report_id=report_id, content_hash=REPORT_HASH, blocks=blocks)


class RecordingTransport:
    def __init__(self, script: list[SendOutcome]) -> None:
        self.script = script
        self.calls: list[dict[str, object]] = []

    def send_payload(
        self, *, delivery_part_id: str, chat_id: str, link_generation: int, text: str
    ) -> SendOutcome:
        self.calls.append(
            {
                "delivery_part_id": delivery_part_id,
                "chat_id": chat_id,
                "link_generation": link_generation,
                "text": text,
            }
        )
        return self.script[min(len(self.calls) - 1, len(self.script) - 1)]


class Clock:
    """A movable clock, so the backoff can be waited out without waiting."""

    def __init__(self) -> None:
        self.now = datetime.now(tz=UTC)

    def advance(self, seconds: float) -> None:
        self.now = self.now + timedelta(seconds=seconds)

    def __call__(self) -> datetime:
        return self.now


def build_context(
    engine: Engine,
    transport: RecordingTransport,
    *,
    link_port: FakeLinkPort | None = None,
    report_port: FakeReportPort | None = None,
    storage: StorageGuard | None = None,
    clock: Clock | None = None,
) -> DeliveryContext:
    context = DeliveryContext(
        engine=engine,
        storage=storage or StorageGuard(),
        transport=transport,
        link_port=link_port or FakeLinkPort(),
        report_port=report_port or FakeReportPort(),
        restore_generation=1,
    )
    if clock is not None:
        context.now = clock  # type: ignore[method-assign]
    return context


def seed_intent(context: DeliveryContext) -> str:
    result = create_intent(
        context,
        owner_id=OWNER_ID,
        kind=DeliveryIntentKind.REPORT_DIGEST,
        caller_module="MOD-report-service",
        report_id=REPORT_ID,
        telegram_link_generation=LINK_GENERATION,
    )
    return str(result["delivery_id"])


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_database(tmp_path / "rr.db")


# ======================================================================================
# Fixture telegram/c
# ======================================================================================


def test_budget_exhaustion_fails_the_delivery_and_leaves_report_and_run_alone(
    engine: Engine, fixture_loader
) -> None:
    """Four attempts, then ``failed`` -- and neither ``report`` nor ``run`` is written.

    ``telegram_send_attempts`` is 4 in ``contracts/retry-policy.yaml``; the test does not
    hard-code a second copy of that number, it reads the constant the service reads, so
    raising the budget to make a test pass (``SG-02``) would be visible as a contract change.
    """
    from server.app.delivery.service import TELEGRAM_SEND_ATTEMPTS

    fixture = fixture_loader("telegram/c-permanent-failure-report-intact")
    expected = fixture.data["expected"]
    assert expected["outbound_call_counts"]["telegram.sendMessage"] == TELEGRAM_SEND_ATTEMPTS

    before = snapshot_report_and_run(engine)
    watcher = WriteWatcher(engine)
    clock = Clock()
    transport = RecordingTransport(
        [
            RetryableFailure("5xx"),
            RetryableFailure("5xx"),
            RetryableFailure("5xx"),
            PermanentFailure("recipient_revoked"),
        ]
    )
    context = build_context(engine, transport, clock=clock)
    delivery_id = seed_intent(context)

    for _ in range(TELEGRAM_SEND_ATTEMPTS + 2):
        dispatch_next(context, owner_id=OWNER_ID)
        clock.advance(3600)  # past every backoff step, still inside the 6-hour window

    assert len(transport.calls) == TELEGRAM_SEND_ATTEMPTS

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.FAILED.value
    assert status["parts"][0]["state"] == DeliveryPartState.FAILED.value

    assert snapshot_report_and_run(engine) == before
    assert (
        watcher.forbidden_writes == []
    ), "delivery wrote to `report` or `run`; I05 and I09 forbid both"
    with engine.begin() as connection:
        assert (
            connection.execute(
                text("SELECT COUNT(*) FROM report WHERE id = :id"), {"id": REPORT_ID}
            ).scalar_one()
            == 1
        ), "expected report__deleted = 0"


def test_a_retryable_error_is_never_filed_as_unknown(engine: Engine) -> None:
    """``T-DL-03`` vs ``T-DL-04`` -- AMD-B03's most important boundary.

    A retryable error with a clear meaning goes to ``retry_wait`` and is retried on budget.
    An *uncertain* outcome goes to ``unknown`` and is never retried. Filing the second as the
    first is how duplicate messages get sent, so the two paths are asserted apart.
    """
    clock = Clock()
    transport = RecordingTransport([RetryableFailure("429", retry_after_seconds=1.0), Sent("1001")])
    context = build_context(engine, transport, clock=clock)
    delivery_id = seed_intent(context)

    first = dispatch_next(context, owner_id=OWNER_ID)
    assert first.reason == "retry_wait"
    assert get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["state"] == (
        DeliveryState.RETRY_WAIT.value
    )

    # Before the backoff is due, the dispatcher does not send.
    not_due = dispatch_next(context, owner_id=OWNER_ID)
    assert not_due.reason == "retry_not_due"
    assert len(transport.calls) == 1

    clock.advance(60)
    second = dispatch_next(context, owner_id=OWNER_ID)
    assert second.reason == "sent"
    assert len(transport.calls) == 2


# ======================================================================================
# Fixture reporting/c -- the tags moved, the payload did not
# ======================================================================================


def test_retry_sends_the_published_bytes_not_a_rebuild(engine: Engine, fixture_loader) -> None:
    """``h_payload`` at attempt 1 equals ``h_payload`` at attempt 2 (fixture ``reporting/c``).

    The tag change is represented by mutating the report row's ``tag_config_version_id``
    between the two attempts -- which the delivery must ignore, because it reads the frozen
    payload rather than the current tag set.
    """
    fixture = fixture_loader("reporting/c-tag-changed-after-publish-before-send")
    assertions = [oracle["assertion"] for oracle in fixture.data["expected"]["hash_oracles"]]
    assert any("h_payload" in assertion for assertion in assertions)

    clock = Clock()
    transport = RecordingTransport([RetryableFailure("5xx"), Sent("1001")])
    context = build_context(engine, transport, clock=clock)
    delivery_id = seed_intent(context)

    dispatch_next(context, owner_id=OWNER_ID)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE report SET tag_config_version_id = 'CTCV-2' WHERE id = :id"),
            {"id": REPORT_ID},
        )
    clock.advance(60)
    dispatch_next(context, owner_id=OWNER_ID)

    assert len(transport.calls) == 2
    assert (
        transport.calls[0]["text"] == transport.calls[1]["text"]
    ), "the retry sent different bytes than the first attempt"
    with engine.begin() as connection:
        rows = connection.execute(
            text("SELECT COUNT(*) FROM delivery WHERE report_id = :r"), {"r": REPORT_ID}
        ).scalar_one()
    assert rows == fixture.data["expected"]["counts"]["delivery[report_id=REP-C]"]
    assert get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["state"] == (
        DeliveryState.SENT.value
    )


def test_a_rebuilt_payload_is_refused_rather_than_sent(engine: Engine) -> None:
    """If the bytes no longer hash to the part's ``payload_hash``, nothing goes out.

    This is the negative half of the oracle above: a builder that re-rendered from the
    current tags produces a different payload, and ``I05`` says the published content is what
    ships -- so the send is refused instead of quietly delivering the newer text.
    """
    clock = Clock()
    transport = RecordingTransport([RetryableFailure("5xx"), Sent("1001")])
    report_port = FakeReportPort()
    context = build_context(engine, transport, report_port=report_port, clock=clock)
    seed_intent(context)

    dispatch_next(context, owner_id=OWNER_ID)
    report_port.rebuild_marker = " (nội dung dựng lại)"
    clock.advance(60)

    with pytest.raises(DeliveryError) as refused:
        dispatch_next(context, owner_id=OWNER_ID)
    assert refused.value.code is ErrorCode.CONFLICT
    assert len(transport.calls) == 1


# ======================================================================================
# Fixtures telegram/d and telegram/e -- the recipient changed
# ======================================================================================


def test_unlink_before_send_cancels_and_sends_nothing(engine: Engine, fixture_loader) -> None:
    """``T-DL-08`` / fixture ``telegram/d``: ``cancelled``, 0 attempts, 0 outbound calls."""
    fixture = fixture_loader("telegram/d-unlink-before-send-cancelled")
    expected = fixture.data["expected"]

    transport = RecordingTransport([Sent("1001")])
    link = FakeLinkPort()
    context = build_context(engine, transport, link_port=link)
    delivery_id = seed_intent(context)

    link.active = False  # the owner unlinked in the app (AMD-B10, not a chat command)
    outcome = dispatch_next(context, owner_id=OWNER_ID)
    assert outcome.reason == "cancelled_link_generation"

    assert len(transport.calls) == expected["outbound_call_counts"]["telegram.sendMessage"]
    with engine.begin() as connection:
        attempts = connection.execute(text("SELECT COUNT(*) FROM delivery_attempt")).scalar_one()
    assert attempts == expected["counts"]["delivery_attempt__total"]
    assert get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["state"] == (
        DeliveryState.CANCELLED.value
    )


def test_relink_does_not_hand_the_old_digest_to_the_new_chat(
    engine: Engine, fixture_loader
) -> None:
    """Fixture ``telegram/e``: generation 4 does not inherit generation 3's delivery.

    ``delivery__auto_created_for_new_generation`` is 0 in the fixture, and it is 0 here for
    the reason the fixture gives: a digest belongs to the recipient it was built for, and
    wanting the new chat to receive one means publishing a new period.
    """
    fixture = fixture_loader("telegram/e-relink-old-generation-cancelled")
    expected = fixture.data["expected"]

    transport = RecordingTransport([Sent("1001")])
    link = FakeLinkPort()
    context = build_context(engine, transport, link_port=link)
    seed_intent(context)

    link.generation = 4
    link.chat_id = "222222222"
    outcome = dispatch_next(context, owner_id=OWNER_ID)
    assert outcome.reason == "cancelled_link_generation"
    assert len(transport.calls) == 0, "the old digest was sent to the new chat"

    with engine.begin() as connection:
        deliveries = connection.execute(
            text("SELECT telegram_link_generation, state FROM delivery")
        ).all()
    assert len(deliveries) == 1 + expected["counts"]["delivery__auto_created_for_new_generation"]
    assert deliveries[0].telegram_link_generation == LINK_GENERATION
    assert deliveries[0].state == DeliveryState.CANCELLED.value


# ======================================================================================
# E2 -- storage cannot be written, so nothing may be sent
# ======================================================================================


def test_a_blocked_store_stops_the_send_before_it_starts(engine: Engine) -> None:
    """Card §7: ``STORAGE_WRITE_FAILED`` -- the attempt cannot commit, so nothing is called.

    Two mechanisms are checked at once, because either alone would let a defect through: the
    guard refuses ``delivery.dispatch_next`` while ``write_blocked``, and the injected fault
    proves that even if the guard were bypassed the attempt INSERT would fail before the
    network call rather than after it.
    """
    transport = RecordingTransport([Sent("1001")])
    guard = StorageGuard()
    context = build_context(engine, transport, storage=guard)
    seed_intent(context)

    guard.record_write_failure()
    with pytest.raises(DeliveryError) as refused:
        dispatch_next(context, owner_id=OWNER_ID)
    assert refused.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert len(transport.calls) == 0

    injector = WriteFaultInjector(engine)
    healthy_guard = StorageGuard()
    healthy_context = build_context(engine, transport, storage=healthy_guard)
    with injector.disk_full(), pytest.raises(Exception) as raised:
        dispatch_next(healthy_context, owner_id=OWNER_ID)
    assert "disk is full" in str(raised.value)
    assert len(transport.calls) == 0, "a send happened although the attempt row never committed"
