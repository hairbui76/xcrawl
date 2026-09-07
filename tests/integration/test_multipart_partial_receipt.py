"""E1 -- a two-part digest where part 2 goes ``unknown`` and part 1 stays sent.

Fixture ``telegram/a-multipart-part2-unknown-no-resend`` is the case ``DP-02`` was written
for. Its event 6 is the trap: the outbox sweep wakes up, sees an aggregate that is not
``sent``, and must send nothing. The fixture's own counts are the oracle --
``telegram.sendMessage = 2`` with the note *"Sự kiện 6 KHÔNG sinh lời gọi thứ ba"*,
``automatic_resend_of_unknown_part = 0``, ``delivery_attempt__total = 2``.

The splitting rule of ``contracts/telegram/delivery.md`` §3.5 is exercised here too, in the
only shape ``OD-20260908-09`` permits: **plain text**, split at item boundaries by the 4096
limit. No ``parse_mode``, no inline keyboard, no ``callback_data`` -- those depend on the
three facts §3.4 leaves at ``KC``, and the tests that would need them are recorded
``NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`` in the handoff rather than written against a
guessed number.
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
)
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.delivery import parts as parts_module
from server.app.delivery.outbox import SenderLeaseRegistry
from server.app.delivery.service import (
    DeliveryContext,
    DeliveryError,
    LinkSnapshot,
    PublishedDigest,
    SendOutcome,
    Sent,
    UncertainOutcome,
    create_intent,
    dispatch_next,
    get_status,
    record_receipt,
)
from server.app.storage.guard import StorageGuard

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
REPORT_ID = "01JREP0RT10000000000000000"
CHAT_ID = "111111111"
LINK_GENERATION = 3


def build_database(path: Path) -> Engine:
    """``alembic upgrade head`` plus the single ``owner`` row. No DDL is declared here."""
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


@dataclass
class FakeLinkPort:
    generation: int = LINK_GENERATION
    active: bool = True
    chat_id: str = CHAT_ID

    def current_link(self, *, owner_id: str) -> LinkSnapshot | None:
        return LinkSnapshot(chat_id=self.chat_id, generation=self.generation, active=self.active)


@dataclass
class FakeReportPort:
    """Two blocks, each just over half the limit, so the digest splits into exactly two parts."""

    blocks: tuple[str, ...] = (
        "Kỳ 2026-09-06 — hướng đang nổi\n" + "A" * 2400,
        "Mục 1 — tiêu đề\n" + "B" * 2400,
    )

    def published_digest(self, *, owner_id: str, report_id: str) -> PublishedDigest | None:
        return PublishedDigest(
            report_id=report_id, content_hash="sha256:" + "c" * 64, blocks=self.blocks
        )


class RecordingTransport:
    """Counts calls and answers from a script. The counts are the oracle."""

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


def build_context(engine: Engine, transport: RecordingTransport) -> DeliveryContext:
    return DeliveryContext(
        engine=engine,
        storage=StorageGuard(),
        transport=transport,
        link_port=FakeLinkPort(),
        report_port=FakeReportPort(),
        restore_generation=1,
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
    return str(result["delivery_id"])


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_database(tmp_path / "rr.db")


# ======================================================================================
# Fixture telegram/a
# ======================================================================================


def test_part_two_unknown_does_not_resend_part_one(engine: Engine, fixture_loader) -> None:
    """The fixture, end to end, measured with its own counts.

    Four ``dispatch_next`` turns are run, not two: turns 3 and 4 are event 6, the sweep that
    a naive implementation turns into a third and fourth ``sendMessage``.
    """
    fixture = fixture_loader("telegram/a-multipart-part2-unknown-no-resend")
    expected = fixture.data["expected"]

    transport = RecordingTransport([Sent("1001"), UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)

    first = dispatch_next(context, owner_id=OWNER_ID)
    assert first.reason == "sent" and first.part_index == 0
    second = dispatch_next(context, owner_id=OWNER_ID)
    assert second.reason == "unknown" and second.part_index == 1

    for _ in range(2):
        sweep = dispatch_next(context, owner_id=OWNER_ID)
        assert sweep.reason in {"no_eligible_intent", "held_unknown_awaiting_operator"}

    assert len(transport.calls) == expected["outbound_call_counts"]["telegram.sendMessage"]

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.UNKNOWN.value, "DP-03: unknown outranks sent"
    assert status["parts"][0]["state"] == DeliveryPartState.SENT.value
    assert status["parts"][0]["provider_message_id"] == "1001"
    assert status["parts"][1]["state"] == DeliveryPartState.UNKNOWN.value
    assert status["parts"][1]["provider_message_id"] is None

    with engine.begin() as connection:
        counts = {
            "delivery_part__state_sent": connection.execute(
                text("SELECT COUNT(*) FROM delivery_part WHERE state = 'sent'")
            ).scalar_one(),
            "delivery_part__state_unknown": connection.execute(
                text("SELECT COUNT(*) FROM delivery_part WHERE state = 'unknown'")
            ).scalar_one(),
            "delivery_attempt__total": connection.execute(
                text("SELECT COUNT(*) FROM delivery_attempt")
            ).scalar_one(),
        }
    for key, value in counts.items():
        assert value == expected["counts"][key], key


def test_aggregate_never_reads_as_sent_while_a_part_is_unknown(
    engine: Engine, fixture_loader
) -> None:
    """``I13`` -- the two labels fixture ``telegram/a`` forbids must not be produced.

    ``ui_labels.forbidden_labels`` names them in Vietnamese; the server side of that promise
    is the aggregate state, so the assertion is on the state and on the label key
    ``get_status`` returns, which the UI maps.
    """
    fixture = fixture_loader("telegram/a-multipart-part2-unknown-no-resend")
    forbidden = fixture.data["expected"]["ui_labels"]["forbidden_labels"]
    assert forbidden == ["Đã gửi Telegram", "Không gửi được"]

    transport = RecordingTransport([Sent("1001"), UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)
    dispatch_next(context, owner_id=OWNER_ID)

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] not in {DeliveryState.SENT.value, DeliveryState.FAILED.value}
    assert status["status_label"] == "unknown"


def test_a_sent_part_is_never_sent_twice(engine: Engine) -> None:
    """``T-DL-02``: a second ``record_receipt`` returns the stored receipt and writes nothing.

    The row count of ``delivery_receipt`` is the measurement, because "returned the same
    value" would also be true of an implementation that wrote a second row.
    """
    transport = RecordingTransport([Sent("1001"), UncertainOutcome("timeout")])
    context = build_context(engine, transport)
    delivery_id = seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)

    part_id = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)["parts"][0][
        "delivery_part_id"
    ]
    replay = record_receipt(
        context,
        owner_id=OWNER_ID,
        delivery_part_id=part_id,
        attempt_number=1,
        provider_message_id="9999",
    )
    assert replay["created"] is False
    assert replay["provider_message_id"] == "1001", "a replay must not overwrite the receipt"

    with engine.begin() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM delivery_receipt")).scalar_one() == 1
    assert len(transport.calls) == 1


def test_a_stale_sender_lease_is_refused(engine: Engine) -> None:
    """``sender_lease`` §epoch_rule_vi: an older epoch writes nothing (``STALE_LEASE``).

    Two dispatchers race for the same delivery. The registry hands the second one a higher
    epoch, which makes the first one's lease detectably stale -- the condition that stops two
    processes from sending the same part, since Telegram itself cannot tell us it happened.
    """
    registry = SenderLeaseRegistry()
    now = __import__("datetime").datetime.now(tz=__import__("datetime").UTC)
    first = registry.issue(delivery_id="D-1", intent_id="I-1", holder="a", now=now)
    second = registry.issue(delivery_id="D-1", intent_id="I-1", holder="b", now=now)

    assert registry.is_current(second, now=now) is True
    assert registry.is_current(first, now=now) is False

    transport = RecordingTransport([Sent("1001")])
    context = build_context(engine, transport)
    context.leases = registry
    from server.app.delivery.service import _require_lease

    with pytest.raises(DeliveryError) as refused:
        _require_lease(context, first, now)
    assert refused.value.code is ErrorCode.STALE_LEASE


# ======================================================================================
# §3.5 -- splitting, in plain text only
# ======================================================================================


def test_split_never_cuts_an_item_and_never_exceeds_the_limit() -> None:
    """§3.5: item boundaries only, and every part within 4096 under **both** count readings.

    The blocks carry an astral-plane character on purpose. It counts once as a Unicode
    scalar and twice as a UTF-16 code unit, and §3.4(c) says which of the two Telegram means
    is unsourced -- so the limit is applied to the larger, and the assertion checks the
    larger too.
    """
    blocks = tuple(f"Mục {i} 𝄞 " + "x" * 1500 for i in range(6))
    split = parts_module.split_plain_text(blocks)

    assert len(split) > 1, "the sample must actually exercise splitting"
    for piece in split:
        assert parts_module.message_length(piece.text) <= parts_module.MAX_MESSAGE_LENGTH
        assert piece.text.startswith(f"Phần {piece.part_index + 1}/{len(split)}")

    # Every block appears whole, in one part, in order: nothing halved, nothing lost.
    rejoined = "".join(piece.text for piece in split)
    for block in blocks:
        assert rejoined.count(block) == 1


def test_a_block_that_cannot_fit_is_refused_rather_than_halved() -> None:
    """§3.5 assigns truncation to the builder, with a deep link. The sender refuses instead."""
    with pytest.raises(parts_module.PartTooLarge):
        parts_module.split_plain_text(("y" * (parts_module.MAX_MESSAGE_LENGTH + 1),))


def test_no_parse_mode_and_no_keyboard_reach_the_transport(engine: Engine) -> None:
    """``OD-20260908-09`` and §3.4: the send call has four fields and none of them is markup.

    This is a structural assertion, not a style preference: ``callback_data`` length, the
    escape table and buttons-per-row are all ``KC``/``BLOCKED_DEPENDENCY``, so a payload
    carrying any of them would be built on a guessed number.
    """
    transport = RecordingTransport([Sent("1001"), Sent("1002")])
    context = build_context(engine, transport)
    seed_intent(context)
    dispatch_next(context, owner_id=OWNER_ID)

    call = transport.calls[0]
    assert set(call) == {"delivery_part_id", "chat_id", "link_generation", "text"}
    assert isinstance(call["text"], str)


def test_aggregate_precedence_matches_dp03() -> None:
    """``DP-03``: the state needing most attention wins, so the UI can never overstate."""
    assert (
        parts_module.aggregate_state([DeliveryPartState.SENT, DeliveryPartState.UNKNOWN])
        is DeliveryState.UNKNOWN
    )
    assert (
        parts_module.aggregate_state([DeliveryPartState.SENT, DeliveryPartState.FAILED])
        is DeliveryState.FAILED
    )
    assert (
        parts_module.aggregate_state([DeliveryPartState.UNKNOWN, DeliveryPartState.FAILED])
        is DeliveryState.UNKNOWN
    )
    assert (
        parts_module.aggregate_state([DeliveryPartState.SENT, DeliveryPartState.SENT])
        is DeliveryState.SENT
    )
    assert (
        parts_module.aggregate_state([DeliveryPartState.SENT], cancelled=True)
        is DeliveryState.CANCELLED
    )


# ======================================================================================
# Integration with TC-telegram-linking-auth (W5A), which has landed
# ======================================================================================


def test_link_generation_comes_from_the_adapters_own_table(engine: Engine) -> None:
    """The real ``telegram_link`` row, read through ``TC-telegram-linking-auth``'s function.

    The adapter below lives in the *test*, not in ``server/app/delivery/``: the delivery
    package imports nothing from ``server.app.telegram`` because ``contracts/ports.yaml``
    grants it exactly two outward operations, and reading another module's table is not one
    of them. Wiring the two together is the deployment's job, and this is that wiring.
    """
    from server.app.telegram import linking

    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO telegram_link (id, owner_id, chat_id, generation, state, linked_at) "
                "VALUES ('01JTG11NK10000000000000000', :owner, :chat, :gen, 'active', "
                "'2026-09-06T00:00:00.000Z')"
            ),
            {"owner": OWNER_ID, "chat": CHAT_ID, "gen": LINK_GENERATION},
        )

    class LinkingAdapter:
        def current_link(self, *, owner_id: str) -> LinkSnapshot | None:
            with engine.begin() as connection:
                row = linking.active_link(connection, owner_id=owner_id)
            if row is None:
                return None
            return LinkSnapshot(
                chat_id=row.chat_id, generation=row.generation, active=row.state == "active"
            )

    transport = RecordingTransport([Sent("1001"), Sent("1002")])
    context = build_context(engine, transport)
    context.link_port = LinkingAdapter()
    seed_intent(context)

    dispatch_next(context, owner_id=OWNER_ID)
    assert transport.calls[0]["chat_id"] == CHAT_ID
    assert transport.calls[0]["link_generation"] == LINK_GENERATION


def test_each_part_receipt_records_the_id_the_adapters_sender_returned(engine: Engine) -> None:
    """``T-DL-02`` end to end over the seam a deployment really uses (``DP-01``).

    ``PKT-TC-TGAUTH-FIX1`` gave ``TelegramSender.send_message`` a return type of ``str``, so
    the provider message id now travels the whole way: ``RecordingSender`` mints ``rec-1``,
    ``rec-2``, … per call, the adapter below turns each into :class:`Sent`, and
    ``delivery.record_receipt`` stores it against that part. The assertion is per part and by
    identity, not by count: with two parts a receipt could be right in number and still be
    filed against the wrong part, and ``DP-01`` ("mỗi part có receipt RIÊNG") is exactly the
    claim that would hide behind a count.

    ``rec-`` is deliberately not a Telegram id shape, so no assertion here can pass by
    mistaking a recorded id for a real receipt -- this proves the *plumbing*, and ``E3``
    stays ``NOT_RUN``.
    """
    from server.app.telegram.ingress import RecordingSender

    sender = RecordingSender()

    class SenderAdapter:
        """``telegram.send_payload`` implemented over ``MOD-telegram-adapter``'s sender.

        It lives in the test, not in ``server/app/delivery/``: the delivery package imports
        nothing from ``server.app.telegram``, because wiring two modules together is the
        deployment's job and ``contracts/ports.yaml`` grants delivery exactly two outward
        operations.
        """

        def __init__(self) -> None:
            self.calls: list[dict[str, object]] = []

        def send_payload(
            self, *, delivery_part_id: str, chat_id: str, link_generation: int, text: str
        ) -> SendOutcome:
            self.calls.append({"delivery_part_id": delivery_part_id, "text": text})
            return Sent(sender.send_message(chat_id=chat_id, text=text))

    adapter = SenderAdapter()
    context = build_context(engine, RecordingTransport([]))
    context.transport = adapter
    delivery_id = seed_intent(context)

    first = dispatch_next(context, owner_id=OWNER_ID)
    second = dispatch_next(context, owner_id=OWNER_ID)
    assert (first.reason, second.reason) == ("sent", "sent")

    assert sender.send_message_count == 2
    assert sender.message_ids == ["rec-1", "rec-2"]

    status = get_status(context, owner_id=OWNER_ID, delivery_id=delivery_id)
    assert status["state"] == DeliveryState.SENT.value
    # Part i carries the id returned by the i-th call, and the pairing is checked against the
    # adapter's own call log rather than against the order the parts happen to be listed in.
    sent_for_part = {
        str(call["delivery_part_id"]): message_id
        for call, message_id in zip(adapter.calls, sender.message_ids, strict=True)
    }
    assert {
        part["delivery_part_id"]: part["provider_message_id"] for part in status["parts"]
    } == sent_for_part

    with engine.begin() as connection:
        receipts = connection.execute(
            text(
                "SELECT a.delivery_part_id AS part_id, r.provider_message_id AS message_id "
                "FROM delivery_receipt r JOIN delivery_attempt a ON a.id = r.delivery_attempt_id"
            )
        ).all()
    assert {row.part_id: row.message_id for row in receipts} == sent_for_part
