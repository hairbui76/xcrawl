"""E1 + E2 -- a timeout after the point of possible send, and what must NOT follow it.

Fixture ``telegram/b-response-lost-unknown-operator-decides`` is the spine: Telegram
received the request, the response was lost, and the system has no way to know. Its oracle
is a pair of counts -- ``automatic_retry_from_unknown = 0`` and
``elapsed_before_auto_action_seconds = ∞`` -- so the tests below measure calls and row
states, never a log line.

Also here, because they are the same claim seen from other sides:

* ``recovery/a-restore-old-outbox-nothing-sent`` -- after a restore the dispatcher is locked
  and the count of outbound sends is 0 (``I15``, ``SC27``).
* ``recovery/j-restore-verification-incomplete-dispatch-locked`` -- integrity ``ok`` and
  every count matching the manifest is still not reconciliation. ``TC-backup-restore-drill``
  has landed, so this is no longer an ``xfail``: the clause list is read from the real
  ``server.app.backup.reconcile.evaluate`` and asserted to be exactly clauses 4 and 7.
* ``boundary/a-default-deny-sweep-36-edges`` seq 24 and seq 34 -- ``FE-24`` and ``FE-34``,
  the two forbidden edges that end at ``MOD-delivery-service``.

Nothing in this file opens a socket. ``telegram.send_payload`` is a recording fake, which is
the whole point: the oracle is *how many times it was called*, and a real call could not be
counted honestly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import (
    DeliveryIntentKind,
    DeliveryPartState,
    DeliveryState,
    DeliveryUnknownDecision,
)
from sqlalchemy import Engine, text
from sqlalchemy import text as sql_text

from server.app.db import create_sqlite_engine
from server.app.delivery.service import (
    DeliveryContext,
    DeliveryError,
    LinkSnapshot,
    PublishedDigest,
    SendOutcome,
    Sent,
    UncertainOutcome,
    create_intent,
    decide_unknown,
    dispatch_next,
    get_status,
)
from server.app.storage.guard import StorageGuard

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
REPORT_ID = "01JREP0RT10000000000000000"
CHAT_ID = "111111111"
LINK_GENERATION = 3
#: 36 characters -- ``report.report_build_id`` is CHECKed for exactly that length (UUIDv4).
REPORT_BUILD_ID = "8c1f0c96-0f4a-4a2e-9f4a-0d1d9e5b7c31"
EMBEDDING_GENERATION_ID = "01JEMBGEN10000000000000000"
REPORT_HASH = "sha256:" + "a" * 64
#: Fixture ``recovery/j``'s restore: generation 6, integrity ok, counts matching, no ack.
SNAPSHOT_ID = "01JBACKSNAP000000000000030"
MANIFEST_ID = "01JBACKMANJFEST00000000300"
RESTORE_ID = "01JREST0REREC0RD0000000300"
RESTORE_GENERATION = 6


def build_database(path: Path) -> Engine:
    """A WAL SQLite database carrying the real schema, plus the single ``owner`` row.

    The schema comes from ``alembic upgrade head``, never from DDL re-declared in a test: a
    second source of schema truth beside ``server/migrations/versions/`` is exactly the drift
    these tests exist to catch, and running the real upgrade also proves the chain has one
    head, since Alembic refuses ``head`` outright when it does not.
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


def seed_published_report(engine: Engine) -> None:
    """One ``published`` row in the **real** ``report`` table (``ENT-report``, revision 0010).

    ``TC-report-coverage-publish-cas`` has landed, so the three-column stand-in this file used
    to create is gone: the row below satisfies the shipped schema -- ``owner_id``, the
    half-open coverage window, a 36-character ``report_build_id``, ``selection_version`` and
    ``published_at`` (both required once ``status = 'published'``), and the
    ``embedding_generation`` row its foreign key points at.

    It is seeded with SQL rather than through ``report.publisher.publish_report`` on purpose,
    and the purpose is the oracle. What these tests measure is that **delivery writes nothing
    here**: the row's bytes before and after, plus a statement watcher. Driving the real
    publisher would make the setup depend on a build snapshot, a tag config version and a
    selection -- none of which this card's assertions read -- while proving nothing extra
    about delivery. The end-to-end publish→dispatch path belongs to an integration packet that
    owns both sides; ``server.app.report.publisher.PublishedDigestPort`` already implements
    this card's ``ReportPayloadPort``, so it is a small step, but it is not this card's.
    """
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                "dimension, normalization, state, expected_vector_count, built_vector_count, "
                "created_at, activated_at) "
                "VALUES (:id, :owner, 'multilingual-e5-small', '1.0.0', 4, 'l2', 'active', 0, 0, "
                "'2026-09-06T00:00:00.000Z', '2026-09-06T00:00:00.000Z')"
            ),
            # `expected_vector_count` is written explicitly although the column is nullable:
            # `server.app.backup.reconcile._embedding_ok` calls `int()` on it unguarded, so a
            # legitimately NULL value raises TypeError instead of answering clause 6. That is
            # another card's file and is reported as CR-TC-DELIVERY-11 rather than worked
            # around silently -- the value here is the honest one for a generation with no
            # vectors, not a value chosen to dodge the crash.
            {"id": EMBEDDING_GENERATION_ID, "owner": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO report (id, owner_id, coverage_from, coverage_to, "
                "tag_config_version_id, embedding_generation_id, report_build_id, status, "
                "quality, published_at, content_hash, selection_version, created_at, updated_at) "
                "VALUES (:id, :owner, '2026-09-05T00:00:00.000Z', '2026-09-06T00:00:00.000Z', "
                "'CTCV-1', :generation, :build_id, 'published', 'complete', "
                "'2026-09-06T00:00:00.000Z', :hash, 'sel-1', '2026-09-06T00:00:00.000Z', "
                "'2026-09-06T00:00:00.000Z')"
            ),
            {
                "id": REPORT_ID,
                "owner": OWNER_ID,
                "generation": EMBEDDING_GENERATION_ID,
                "build_id": REPORT_BUILD_ID,
                "hash": REPORT_HASH,
            },
        )


def report_content_hash(engine: Engine) -> str:
    with engine.begin() as connection:
        return str(
            connection.execute(
                text("SELECT content_hash FROM report WHERE id = :id"), {"id": REPORT_ID}
            ).scalar_one()
        )


@dataclass
class FakeLinkPort:
    """Stands in for the link generation read, not for the linking state machine."""

    generation: int = LINK_GENERATION
    active: bool = True
    chat_id: str = CHAT_ID

    def current_link(self, *, owner_id: str) -> LinkSnapshot | None:
        return LinkSnapshot(chat_id=self.chat_id, generation=self.generation, active=self.active)


@dataclass
class FakeReportPort:
    """The published digest, frozen. One short block, so the digest is a single part."""

    blocks: tuple[str, ...] = ("Kỳ 2026-09-06\n\nHướng đang nổi: (không có)", "Mục 1 — tiêu đề")

    def published_digest(self, *, owner_id: str, report_id: str) -> PublishedDigest | None:
        return PublishedDigest(report_id=report_id, content_hash=REPORT_HASH, blocks=self.blocks)


class RecordingTransport:
    """``telegram.send_payload`` that records and answers from a script.

    Every oracle in this file is a count of :attr:`calls`, so the fake exists to be counted,
    not to simulate Telegram.
    """

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


def build_context(
    engine: Engine, transport: RecordingTransport, **kwargs: object
) -> DeliveryContext:
    guard = kwargs.pop("storage", None) or StorageGuard()
    return DeliveryContext(
        engine=engine,
        storage=guard,  # type: ignore[arg-type]
        transport=transport,
        link_port=kwargs.pop("link_port", None) or FakeLinkPort(),  # type: ignore[arg-type]
        report_port=FakeReportPort(),
        restore_generation=int(kwargs.pop("restore_generation", 1)),  # type: ignore[call-overload]
    )


def seed_intent(context: DeliveryContext) -> str:
    result = create_intent(
        context,
        owner_id=OWNER_ID,
        kind=DeliveryIntentKind.REPORT_DIGEST,
        caller_module="MOD-report-service",
        report_id=REPORT_ID,
        telegram_link_generation=LINK_GENERATION,
    )
    assert result["created"] is True
    return str(result["delivery_id"])


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    engine = build_database(tmp_path / "rr.db")
    seed_published_report(engine)
    return engine


# ======================================================================================
# Fixture telegram/b -- the response was lost
# ======================================================================================


def test_timeout_after_possible_send_becomes_unknown_and_never_resends(
    engine: Engine, fixture_loader
) -> None:
    """``T-DL-04`` + AMD-B03: one send, then ``unknown``, then **nothing**.

    The second and third ``dispatch_next`` calls are the ones that matter. They are the
    outbox sweep of fixture ``telegram/a`` event 6 -- the moment a naive dispatcher sees an
    aggregate that is not ``sent`` and helpfully sends again. The oracle is that the outbound
    call count does not move.
    """
    fixture = fixture_loader("telegram/b-response-lost-unknown-operator-decides")
    expected = fixture.data["expected"]["after_event_3"]

    transport = RecordingTransport([UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)

    first = dispatch_next(context, owner_id=OWNER_ID)
    assert first.reason == "unknown"
    assert first.error_code is ErrorCode.TELEGRAM_SEND_UNCERTAIN
    assert len(transport.calls) == expected["outbound_call_counts"]["telegram.sendMessage"]

    for _ in range(3):
        again = dispatch_next(context, owner_id=OWNER_ID)
        assert again.reason in {"no_eligible_intent", "held_unknown_awaiting_operator"}
    assert len(transport.calls) == 1, "a part in `unknown` was resent automatically"

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.UNKNOWN.value
    assert [part["state"] for part in status["parts"]] == [DeliveryPartState.UNKNOWN.value]
    assert (
        status["parts"][0]["provider_message_id"] is None
    ), "fixture telegram/b forbids recording a message id that never came back"


def test_unknown_has_no_timeout_out_of_it(engine: Engine) -> None:
    """§5.2: *"Không có timeout tự chuyển unknown sang trạng thái khác."*

    Time is advanced past every budget in ``contracts/retry-policy.yaml`` -- the 6-hour
    ``telegram_send_max_window`` included -- by overriding the context clock. The part stays
    ``unknown`` and the outbound count stays 1.
    """
    from datetime import timedelta

    transport = RecordingTransport([UncertainOutcome("connection_lost")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)

    real_now = context.now()
    context.now = lambda: real_now + timedelta(days=7)  # type: ignore[method-assign]
    for _ in range(5):
        dispatch_next(context, owner_id=OWNER_ID)

    assert len(transport.calls) == 1
    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.UNKNOWN.value


def test_only_the_owner_moves_a_part_out_of_unknown(engine: Engine, fixture_loader) -> None:
    """``T-DL-06`` -- the three decisions, and what each does to the outbound count.

    ``mark_not_delivered`` is the fixture's own choice, and its oracle is that
    ``sendMessage`` stays at 1. ``resend_accepting_duplicate_risk`` is the other branch the
    fixture names: exactly one more attempt, and only because a person said so.
    """
    fixture = fixture_loader("telegram/b-response-lost-unknown-operator-decides")
    assert fixture.data["expected"]["decision_options"] == [
        decision.value for decision in DeliveryUnknownDecision
    ]

    transport = RecordingTransport([UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)
    part_id = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["parts"][0][
        "delivery_part_id"
    ]

    decided = decide_unknown(
        context,
        owner_id=OWNER_ID,
        delivery_part_id=part_id,
        decision=DeliveryUnknownDecision.MARK_NOT_DELIVERED,
        decision_request_id="DR-1",
    )
    assert decided["state"] == DeliveryPartState.FAILED.value
    assert decided["delivery_state"] == DeliveryState.FAILED.value
    assert len(transport.calls) == 1, "mark_not_delivered must not send anything"

    # A replay of the same decision is a read, not a second effect.
    replay = decide_unknown(
        context,
        owner_id=OWNER_ID,
        delivery_part_id=part_id,
        decision=DeliveryUnknownDecision.MARK_NOT_DELIVERED,
        decision_request_id="DR-1",
    )
    assert replay["applied"] is False
    assert len(transport.calls) == 1

    # A different decision on a part that already left `unknown` is a conflict, not a
    # silent overwrite of the operator's earlier answer.
    with pytest.raises(DeliveryError) as conflict:
        decide_unknown(
            context,
            owner_id=OWNER_ID,
            delivery_part_id=part_id,
            decision=DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK,
            decision_request_id="DR-2",
            duplicate_risk_accepted=True,
        )
    assert conflict.value.code is ErrorCode.IDEMPOTENCY_CONFLICT

    # `abandon` replayed here does NOT conflict, and that is a reported gap rather than a
    # design choice: `delivery_part_state` has no `cancelled` member, so `abandon` and
    # `mark_not_delivered` both land the part in `failed` and become indistinguishable at
    # part level once applied. See CR-TC-DELIVERY-02.
    ambiguous = decide_unknown(
        context,
        owner_id=OWNER_ID,
        delivery_part_id=part_id,
        decision=DeliveryUnknownDecision.ABANDON,
        decision_request_id="DR-2b",
    )
    assert ambiguous["applied"] is False
    assert len(transport.calls) == 1


def test_resend_requires_the_duplicate_risk_to_be_accepted(engine: Engine) -> None:
    """§5.2: the UI must state the duplicate risk, so the server requires the acceptance.

    Without it the resend is refused (``VALIDATION_ERROR``, 0 further sends). With it the
    part goes back to ``pending``, the intent is un-parked, and exactly one more attempt
    happens -- a duplicate at the recipient is then an accepted outcome, not a defect (§5.1).
    """
    transport = RecordingTransport([UncertainOutcome("timeout"), Sent("1002")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)
    part_id = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["parts"][0][
        "delivery_part_id"
    ]

    with pytest.raises(DeliveryError) as refused:
        decide_unknown(
            context,
            owner_id=OWNER_ID,
            delivery_part_id=part_id,
            decision=DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK,
            decision_request_id="DR-3",
        )
    assert refused.value.code is ErrorCode.VALIDATION_ERROR
    assert len(transport.calls) == 1

    decide_unknown(
        context,
        owner_id=OWNER_ID,
        delivery_part_id=part_id,
        decision=DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK,
        decision_request_id="DR-3",
        duplicate_risk_accepted=True,
    )
    outcome = dispatch_next(context, owner_id=OWNER_ID)
    assert outcome.reason == "sent"
    assert len(transport.calls) == 2

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.SENT.value
    assert status["parts"][0]["provider_message_id"] == "1002"


def test_attempt_row_is_committed_before_the_network_call(engine: Engine) -> None:
    """``T-DL-01``, SRC-PLAN §8.3, measured as an ordering rather than as a log line.

    The transport reads the database *while the send is in flight*. The attempt row it sees
    was committed by a transaction that had already closed, which is the only way this
    assertion can pass: had the INSERT still been inside an open transaction, this separate
    connection would not see it.
    """
    observed: dict[str, object] = {}

    class InspectingTransport(RecordingTransport):
        def send_payload(
            self, *, delivery_part_id: str, chat_id: str, link_generation: int, text: str
        ) -> SendOutcome:
            # `text` is this method's own parameter, so the SQL helper is aliased on import.
            with engine.begin() as connection:
                observed["attempts"] = connection.execute(
                    sql_text("SELECT COUNT(*) FROM delivery_attempt WHERE delivery_part_id = :p"),
                    {"p": delivery_part_id},
                ).scalar_one()
                observed["part_state"] = connection.execute(
                    sql_text("SELECT state FROM delivery_part WHERE id = :p"),
                    {"p": delivery_part_id},
                ).scalar_one()
                observed["receipts"] = connection.execute(
                    sql_text("SELECT COUNT(*) FROM delivery_receipt")
                ).scalar_one()
            return super().send_payload(
                delivery_part_id=delivery_part_id,
                chat_id=chat_id,
                link_generation=link_generation,
                text=text,
            )

    transport = InspectingTransport([UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)

    assert observed["attempts"] == 1, "the attempt row was not durable before the send"
    assert observed["part_state"] == DeliveryPartState.SENDING.value
    assert observed["receipts"] == 0, "a receipt existed before Telegram answered"


# ======================================================================================
# I15 -- restore, and the dispatcher that stays shut
# ======================================================================================


def test_restore_locks_the_dispatcher_and_sends_nothing(engine: Engine, fixture_loader) -> None:
    """``recovery/a`` + ``T-DL-09``: ``RESTORE_UNVERIFIED``, and ``messages_sent = 0``.

    ``StorageGuard.reconciliation_complete`` answers ``False`` for every restore until
    ``TC-backup-restore-drill`` injects a real check, so this exercises the safe default as
    well as the lock: there is no path from ``recovery_required`` back to dispatching that
    does not go through ``backup.reconcile_after_restore``.
    """
    fixture = fixture_loader("recovery/a-restore-old-outbox-nothing-sent")
    assert fixture.data["expected"]["seq2_result"]["error_code"] == "RESTORE_UNVERIFIED"

    transport = RecordingTransport([Sent("1001")])
    guard = StorageGuard()
    context = build_context(engine, transport, storage=guard)
    seed_intent(context)
    # T-ST-03 then T-ST-05: a restore is executed inside a maintenance window. The machine
    # has no `healthy --restore_executed-->` edge, and going through the real edges is what
    # makes this test exercise the contract rather than a convenience setter.
    guard.enter_maintenance()
    guard.mark_recovery_required("RR-01")

    with pytest.raises(DeliveryError) as refused:
        dispatch_next(context, owner_id=OWNER_ID)
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED
    assert len(transport.calls) == fixture.data["expected"]["seq2_result"]["messages_sent"]
    assert guard.reconciliation_complete("RR-01") is False


def test_an_intent_from_an_older_restore_generation_is_not_eligible(engine: Engine) -> None:
    """``recovery/a`` and ``recovery/m``: unlocking dispatch is not permission to replay.

    The intent is created while generation 4 is in force and the dispatcher then runs at
    generation 5, exactly as the fixture describes. It is skipped, and it is skipped without
    being modified -- ``recovery/m`` asserts the old row is unchanged after the unlock.
    """
    transport = RecordingTransport([Sent("1001")])
    context = build_context(engine, transport, restore_generation=4)
    seed_intent(context)

    context.restore_generation = 5
    outcome = dispatch_next(context, owner_id=OWNER_ID)
    assert outcome.reason == "no_eligible_intent"
    assert len(transport.calls) == 0

    with engine.begin() as connection:
        row = connection.execute(
            text("SELECT dispatch_state, restore_generation FROM outbox_intent")
        ).one()
    assert row.dispatch_state == "ready"
    assert row.restore_generation == 4


def seed_restore_awaiting_review(engine: Engine) -> None:
    """Fixture ``recovery/j``'s ``given``, in the real tables ``TC-backup-restore-drill`` ships.

    Integrity ``passed``, every count matching the manifest, no lease still held -- and two
    things missing: one ``outbox_intent`` at the current generation nobody has looked at
    (clause 4) and no operator acknowledgement (clause 7). That is the whole point of the
    fixture: the machine-checkable half can be perfect and reconciliation still be incomplete.
    """
    counts = '{"saved_item": 40, "report": 12, "first_announced_ledger": 31}'
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO backup_snapshot (id, owner_id, method, started_at, completed_at, "
                "artifact_path, artifact_sha256, state) VALUES "
                "(:id, :owner, 'vacuum_into', '2026-09-06T00:00:00.000Z', "
                "'2026-09-06T00:01:00.000Z', '/tmp/bs-03.sqlite', :artifact, 'verified')"
            ),
            {"id": SNAPSHOT_ID, "owner": OWNER_ID, "artifact": "sha256:" + "b" * 64},
        )
        connection.execute(
            text(
                "INSERT INTO backup_manifest (id, owner_id, backup_snapshot_id, entries, "
                "manifest_sha256, counts) VALUES (:id, :owner, :snapshot, '[]', :hash, :counts)"
            ),
            {
                "id": MANIFEST_ID,
                "owner": OWNER_ID,
                "snapshot": SNAPSHOT_ID,
                "hash": "sha256:" + "c" * 64,
                "counts": counts,
            },
        )
        connection.execute(
            text(
                "INSERT INTO restore_record (id, owner_id, backup_snapshot_id, restored_at, "
                "new_restore_generation, integrity_check_outcome, counts_observed, "
                "leases_revoked) VALUES (:id, :owner, :snapshot, '2026-09-06T00:02:00.000Z', "
                ":generation, 'passed', :counts, 2)"
            ),
            {
                "id": RESTORE_ID,
                "owner": OWNER_ID,
                "snapshot": SNAPSHOT_ID,
                "generation": RESTORE_GENERATION,
                "counts": counts,
            },
        )


def test_reconciliation_reports_which_clauses_are_unmet(engine: Engine, fixture_loader) -> None:
    """``recovery/j``: the refusal must name clauses 4 and 7, not merely say "not yet".

    This was an ``xfail`` while ``TC-backup-restore-drill`` was absent. That card has landed,
    so the clause list now comes from the real predicate,
    ``server.app.backup.reconcile.evaluate`` -- read-only, as ``storage.yaml`` §7 requires --
    and is compared against the fixture's own ``unmet_clauses``.

    The intent this card creates is the clause-4 subject: ``create_intent`` leaves it ``ready``
    at the current restore generation, which is precisely "an intent the dispatcher would pick
    up that no operator has decided about". Nothing is stubbed; the delivery side of the
    fixture is produced by the delivery service itself.
    """
    from server.app.backup import reconcile

    fixture = fixture_loader("recovery/j-restore-verification-incomplete-dispatch-locked")
    expected_clauses = fixture.data["expected"]["seq1"]["unmet_clauses"]
    assert expected_clauses == [4, 7]

    transport = RecordingTransport([Sent("1001")])
    context = build_context(engine, transport, restore_generation=RESTORE_GENERATION)
    seed_intent(context)
    seed_restore_awaiting_review(engine)

    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=RESTORE_ID)
    assert list(report.unmet) == expected_clauses
    assert report.complete is False
    assert set(report.met) == {1, 2, 3, 5, 6}

    # seq2 of the fixture: the dispatcher is still shut, and shut for the *state* reason.
    guard = StorageGuard(
        reconciliation_check=reconcile.reconciliation_complete(engine, owner_id=OWNER_ID)
    )
    guard.enter_maintenance()
    guard.mark_recovery_required(RESTORE_ID)
    context.storage = guard
    with pytest.raises(DeliveryError) as refused:
        dispatch_next(context, owner_id=OWNER_ID)
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED
    assert len(transport.calls) == fixture.data["expected"]["seq2"]["messages_sent"]
    assert guard.reconciliation_complete(RESTORE_ID) is False

    with engine.begin() as connection:
        unlocked = connection.execute(
            text("SELECT dispatcher_unlocked_at FROM restore_record WHERE id = :id"),
            {"id": RESTORE_ID},
        ).scalar_one()
    assert unlocked is None, "the fixture requires dispatcher_unlocked_at to stay null"


# ======================================================================================
# SC49 -- the two forbidden edges that end at MOD-delivery-service
# ======================================================================================


@pytest.mark.parametrize("caller", ["MOD-scheduler", "MOD-backup-cli"])
def test_forbidden_callers_of_dispatch_next_are_refused(engine: Engine, caller: str) -> None:
    """``FE-24`` (NC-09) and ``FE-34`` (NC-10), both ``FORBIDDEN_EDGE`` at the edge level.

    The boundary fixture gives ``FE-34`` two codes: ``FORBIDDEN_EDGE`` for the edge class and
    ``RESTORE_UNVERIFIED`` for the operational reason the same operation is refused while
    storage is ``recovery_required``. They describe two layers, and the fixture says so; the
    edge answer must not depend on the storage state, which is what this asserts.
    """
    transport = RecordingTransport([Sent("1001")])
    context = build_context(engine, transport)
    seed_intent(context)

    with pytest.raises(DeliveryError) as refused:
        dispatch_next(context, owner_id=OWNER_ID, caller_module=caller)
    assert refused.value.code is ErrorCode.FORBIDDEN_EDGE
    assert refused.value.details_safe == {
        "caller_module": caller,
        "callee_module": "MOD-delivery-service",
    }
    assert len(transport.calls) == 0


def test_create_intent_is_closed_to_callers_outside_its_two(engine: Engine) -> None:
    """``contracts/ports.yaml``: only ``MOD-report-service`` and ``MOD-job-service`` may call it.

    The collector is on another runtime, so ruling R5-01 makes its refusal
    ``CAPABILITY_DENIED`` rather than ``FORBIDDEN_EDGE`` -- a different fact, and the fixture
    sweep asserts the code, not merely the refusal.
    """
    transport = RecordingTransport([Sent("1001")])
    context = build_context(engine, transport)

    with pytest.raises(DeliveryError) as refused:
        create_intent(
            context,
            owner_id=OWNER_ID,
            kind=DeliveryIntentKind.REPORT_DIGEST,
            caller_module="MOD-x-collector",
            report_id=REPORT_ID,
            telegram_link_generation=LINK_GENERATION,
        )
    assert refused.value.code is ErrorCode.CAPABILITY_DENIED


# ======================================================================================
# I09 -- the run and the report are not part of this story
# ======================================================================================


def test_unknown_delivery_leaves_the_report_row_untouched(engine: Engine) -> None:
    """``I05``/``I09``: whatever happens to the send, the published content does not move."""
    before = report_content_hash(engine)
    transport = RecordingTransport([UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)
    assert report_content_hash(engine) == before
