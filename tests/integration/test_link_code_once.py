"""E1 — a link code is spent exactly once, and relinking opens a new generation.

Fixtures ``telegram/g-link-code-used-twice``, ``telegram/i-unknown-chat-valid-code-format``
and ``telegram/e-relink-old-generation-cancelled`` are the oracles. Scenarios ``SC18``,
``SC47`` and ``SC25``; card §8 oracles 2 and 3.

The interesting assertion in all three is negative
--------------------------------------------------
The second use of a code, a wrong code and an expired code are all **silent**, and they are
silent in the same way, which is the point: a bot that said "mã đã dùng" would confirm that
the string was once a real code and turn itself into an oracle for guessing. So every test
below checks the sender's call count as well as the rows, and the two have to agree.

Row-level arbitration, not application-level
--------------------------------------------
"Used once" is enforced by ``UPDATE … WHERE state = 'active'`` returning ``rowcount == 1``
and by the partial unique index ``ux_telegram_link_active``. The second chat loses at the
row, not at an ``if``: an ``if`` that read the state and then wrote would be a race, and the
race is exactly what fixture ``g``'s second event describes.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.telegram.commands import REPLY_LINKED_CONFIRMATION
from server.app.telegram.ingress import (
    Disposition,
    RecordingSender,
    TelegramContext,
    receive_update,
)
from server.app.telegram.linking import (
    DEFAULT_LINKING_POLICY,
    ConsumeOutcome,
    LinkAttemptOutcome,
    active_link,
    consume_link_code,
    hash_link_code,
    issue_link_code,
    matches_code_format,
    mint_link_code,
    unlink,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
CHAT_A = "111111111"
CHAT_B = "222222222"
WEBHOOK_SECRET = "a-webhook-secret-of-sufficient-length"


def _migrate(db_path: Path) -> None:
    """``alembic upgrade heads`` — see the note in ``test_unknown_chat_silent.py``."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "heads")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "telegram.db"
    _migrate(db_path)
    built = create_sqlite_engine(db_path)
    with built.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', "
                "'2026-09-01T00:00:00.000Z')"
            ),
            {"id": OWNER_ID},
        )
    yield built
    built.dispose()


def _message(update_id: int, chat_id: str, body: str, *, at: datetime) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": int(at.timestamp()),
            "chat": {"id": int(chat_id), "type": "private"},
            "text": body,
        },
    }


def _context(engine: Engine, sender: RecordingSender) -> TelegramContext:
    return TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET, sender=sender
    )


def _scalar(engine: Engine, sql: str, **params: Any) -> Any:
    with engine.connect() as connection:
        return connection.execute(text(sql), params).scalar_one()


# --------------------------------------------------------------------------------------
# Fixture g — a code used twice
# --------------------------------------------------------------------------------------


def test_fixture_g_a_code_used_twice_links_once_and_says_nothing_the_second_time(
    engine, fixture_loader
) -> None:
    """Fixture ``g``: chat A links; chat B sends the same code and gets absolute silence.

    ``after_event_2`` pins ``telegram_link__total: 1`` and ``domain_rows_changed: 0``, so the
    second event must leave the code, the link and every other business row exactly as event
    one left them.
    """
    fixture = fixture_loader("telegram/g-link-code-used-twice")
    given_code = fixture.rows("telegram_link_code")[0]
    expires_at = datetime.fromisoformat(str(given_code["expires_at"]).replace("Z", "+00:00"))
    issued_at = expires_at - timedelta(seconds=DEFAULT_LINKING_POLICY.code_ttl_seconds)

    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=issued_at, policy=DEFAULT_LINKING_POLICY
        )

    sender = RecordingSender()
    context = _context(engine, sender)
    first_at = datetime(2026, 9, 6, 23, 30, tzinfo=UTC)
    second_at = datetime(2026, 9, 6, 23, 31, tzinfo=UTC)

    first = receive_update(context, _message(1, CHAT_A, issued.code, at=first_at), now=first_at)
    after_first_calls = sender.send_message_count
    second = receive_update(context, _message(2, CHAT_B, issued.code, at=second_at), now=second_at)

    expected_1 = fixture.data["expected"]["after_event_1"]
    expected_2 = fixture.data["expected"]["after_event_2"]

    # after_event_1: one link, code consumed, exactly one confirmation message.
    assert first.consume_outcome is ConsumeOutcome.LINKED
    assert after_first_calls == expected_1["outbound_call_counts"]["telegram.sendMessage"] == 1
    assert first.replies == (REPLY_LINKED_CONFIRMATION,)
    assert _scalar(engine, "SELECT state FROM telegram_link_code") == "consumed"

    # after_event_2: absolute silence, and nothing moved.
    assert second.replies == ()
    assert second.consume_outcome is ConsumeOutcome.CODE_CONSUMED
    assert second.disposition is Disposition.LINK_CODE_ATTEMPT
    assert (
        sender.send_message_count - after_first_calls
        == expected_2["outbound_call_counts"]["telegram.sendMessage"]
        == 0
    )
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link")
        == expected_2["counts"]["telegram_link__total"]
        == 1
    )
    with engine.connect() as connection:
        link = active_link(connection, owner_id=OWNER_ID)
    assert link is not None and link.chat_id == CHAT_A, "chat B took over the link"
    assert _scalar(engine, "SELECT consumed_by_chat_id FROM telegram_link_code") == CHAT_A

    # The log records the attempt without recording who made it in the clear.
    dispositions = [
        row[0] for row in _all(engine, "SELECT disposition FROM telegram_update_log ORDER BY id")
    ]
    assert dispositions.count(Disposition.LINK_CODE_ATTEMPT.value) == 2


def _all(engine: Engine, sql: str) -> list[tuple[Any, ...]]:
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(sql))]


# --------------------------------------------------------------------------------------
# Fixture i — the B09 exception, all three events
# --------------------------------------------------------------------------------------


def test_fixture_i_only_a_format_match_is_ever_compared(engine, fixture_loader) -> None:
    """Fixture ``i`` seq 1..3: prose is not compared; a wrong code is compared and silent;
    the right code links and replies once.

    The strongest assertion is ``after_event_1``'s ``code_lookup_performed: 0``. It is
    measured here by the absence of a ``telegram_link_attempt`` row, which the contract makes
    the observable trace of a comparison: the row is written on **every** format match and on
    no other message, so zero rows is zero comparisons.
    """
    fixture = fixture_loader("telegram/i-unknown-chat-valid-code-format")
    events = fixture.events
    at_1 = datetime.fromisoformat(str(events[0]["at"]).replace("Z", "+00:00"))
    at_2 = datetime.fromisoformat(str(events[1]["at"]).replace("Z", "+00:00"))
    at_3 = datetime.fromisoformat(str(events[2]["at"]).replace("Z", "+00:00"))

    with engine.begin() as connection:
        issued = issue_link_code(
            connection,
            owner_id=OWNER_ID,
            now=at_1 - timedelta(minutes=5),
            policy=DEFAULT_LINKING_POLICY,
        )

    sender = RecordingSender()
    context = _context(engine, sender)
    expected = fixture.data["expected"]

    # seq 1: "xin chào" -- no format match, no lookup, no row.
    first = receive_update(
        context, _message(1, CHAT_B, str(events[0]["message_text"]), at=at_1), now=at_1
    )
    assert first.consume_outcome is ConsumeOutcome.NO_FORMAT_MATCH
    assert first.disposition.value == expected["after_event_1"]["log_disposition"]
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link_attempt")
        == expected["after_event_1"]["counts"]["telegram_link_attempt__total"]
        == 0
    )
    assert sender.send_message_count == 0

    # seq 2: format matches, code does not. Compared, recorded, silent.
    second = receive_update(
        context, _message(2, CHAT_B, str(events[1]["message_text"]), at=at_2), now=at_2
    )
    assert second.consume_outcome is ConsumeOutcome.CODE_INVALID
    assert second.disposition.value == expected["after_event_2"]["log_disposition"]
    counts_2 = expected["after_event_2"]["counts"]
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link_attempt")
        == (counts_2["telegram_link_attempt__total"])
    )
    assert _scalar(engine, "SELECT COUNT(*) FROM telegram_link") == counts_2["telegram_link__total"]
    assert sender.send_message_count == 0
    attempt = _all(engine, "SELECT outcome, link_code_id FROM telegram_link_attempt")[0]
    assert attempt[0] == LinkAttemptOutcome.FORMAT_MATCH_CODE_INVALID.value
    assert attempt[1] is None, "no code matched, so link_code_id must be NULL"

    # seq 3: the real code. One link, one reply.
    third = receive_update(context, _message(3, CHAT_B, issued.code, at=at_3), now=at_3)
    counts_3 = expected["after_event_3"]["counts"]
    assert third.consume_outcome is ConsumeOutcome.LINKED
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link WHERE state = 'active'")
        == counts_3["telegram_link__state_active"]
    )
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link_attempt")
        == counts_3["telegram_link_attempt__total"]
    )
    assert (
        sender.send_message_count
        == expected["after_event_3"]["outbound_call_counts"]["telegram.sendMessage"]
        == 1
    )
    outcomes = [row[0] for row in _all(engine, "SELECT outcome FROM telegram_link_attempt")]
    assert LinkAttemptOutcome.FORMAT_MATCH_CODE_VALID.value in outcomes


def test_the_code_format_is_the_contracts_and_the_plaintext_is_never_stored(engine) -> None:
    """``code_format`` accepts what the contract's regex accepts, and only the hash lands.

    ``entities.yaml``: *"Hash của mã; KHÔNG lưu mã gốc."* The DDL enforces the hash shape, so
    a stored plaintext would fail the CHECK -- this asserts the value as well, because a
    64-character plaintext would satisfy the shape.
    """
    assert matches_code_format("RR-7QK2M4XB", DEFAULT_LINKING_POLICY)
    assert matches_code_format("  RR-7QK2M4XB  ", DEFAULT_LINKING_POLICY), "trim before matching"
    for rejected in (
        "RR-7QK2M4X",  # too short
        "RR-7QK2M4XBB",  # too long
        "rr-7qk2m4xb",  # lowercase
        "RR-7QK2M4XI",  # I is excluded from Crockford base32
        "RR-7QK2M4XU",  # so is U
        "hello RR-7QK2M4XB",  # not the whole message
        "",
    ):
        assert not matches_code_format(rejected, DEFAULT_LINKING_POLICY), rejected

    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=datetime.now(tz=UTC), policy=DEFAULT_LINKING_POLICY
        )
    stored = _scalar(engine, "SELECT code_hash FROM telegram_link_code")
    assert stored == hash_link_code(issued.code)
    assert issued.code not in stored
    assert matches_code_format(mint_link_code(), DEFAULT_LINKING_POLICY)


def test_an_expired_code_is_refused_and_stays_silent(engine) -> None:
    """``expiry``: 15 minutes. Past it the code links nothing, and the chat is told nothing.

    The code row is deliberately **not** rewritten to ``expired`` on this path: fixture (i)
    pins ``domain_rows_changed: 0`` for an unlinked chat, and expiry is a fact about the
    clock rather than a state a stranger's message may change.
    """
    issued_at = datetime(2026, 9, 7, 0, 0, tzinfo=UTC)
    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=issued_at, policy=DEFAULT_LINKING_POLICY
        )
    too_late = issued_at + timedelta(seconds=DEFAULT_LINKING_POLICY.code_ttl_seconds + 1)

    sender = RecordingSender()
    outcome = receive_update(
        _context(engine, sender), _message(1, CHAT_B, issued.code, at=too_late), now=too_late
    )

    assert outcome.consume_outcome is ConsumeOutcome.CODE_EXPIRED
    assert outcome.replies == ()
    assert sender.send_message_count == 0
    assert _scalar(engine, "SELECT COUNT(*) FROM telegram_link") == 0
    assert _scalar(engine, "SELECT state FROM telegram_link_code") == "active"
    assert (
        _scalar(engine, "SELECT outcome FROM telegram_link_attempt")
        == LinkAttemptOutcome.FORMAT_MATCH_CODE_EXPIRED.value
    )


def test_issuing_a_new_code_revokes_the_previous_one(engine) -> None:
    """``ux_telegram_link_code_active``: at most one code in force, enforced by the index.

    The superseded code then behaves like any other unusable string: refused, and silent.
    """
    now = datetime(2026, 9, 7, tzinfo=UTC)
    with engine.begin() as connection:
        first = issue_link_code(
            connection, owner_id=OWNER_ID, now=now, policy=DEFAULT_LINKING_POLICY
        )
    with engine.begin() as connection:
        second = issue_link_code(
            connection, owner_id=OWNER_ID, now=now, policy=DEFAULT_LINKING_POLICY
        )
    assert first.code != second.code
    states = dict(_all(engine, "SELECT id, state FROM telegram_link_code"))
    assert states[first.code_id] == "revoked"
    assert states[second.code_id] == "active"

    sender = RecordingSender()
    outcome = receive_update(
        _context(engine, sender), _message(1, CHAT_B, first.code, at=now), now=now
    )
    assert outcome.replies == () and sender.send_message_count == 0
    assert _scalar(engine, "SELECT COUNT(*) FROM telegram_link") == 0


# --------------------------------------------------------------------------------------
# Fixture e — relink opens a new generation and revokes the old link
# --------------------------------------------------------------------------------------


def test_fixture_e_relinking_revokes_the_old_link_and_increments_the_generation(
    engine, fixture_loader
) -> None:
    """Fixture ``e``: chat B links with a fresh code; generation 3 → 4, old row ``revoked``.

    ``delivery__auto_created_for_new_generation: 0`` is the other half of the fixture and it
    belongs to ``MOD-delivery-service`` (``T-DL-08``). What this card can prove -- and does,
    below -- is that the adapter creates no delivery row itself: cancelling generation 3's
    payloads is the dispatcher's transition, and re-sending them to the new recipient is
    forbidden outright (I11).
    """
    fixture = fixture_loader("telegram/e-relink-old-generation-cancelled")
    given_link = fixture.rows("telegram_link")[0]
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO telegram_link (id, owner_id, chat_id, generation, state, "
                "linked_at) VALUES (:id, :owner_id, :chat_id, :generation, 'active', "
                "'2026-09-05T00:00:00.000Z')"
            ),
            {
                "id": str(given_link["id"]),
                "owner_id": OWNER_ID,
                "chat_id": str(given_link["chat_id"]),
                "generation": int(given_link["generation"]),
            },
        )

    issued_at = datetime(2026, 9, 6, 22, 30, tzinfo=UTC)
    linked_at = datetime(2026, 9, 6, 22, 31, tzinfo=UTC)
    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=issued_at, policy=DEFAULT_LINKING_POLICY
        )

    sender = RecordingSender()
    outcome = receive_update(
        _context(engine, sender), _message(1, CHAT_B, issued.code, at=linked_at), now=linked_at
    )

    expected = fixture.data["expected"]
    assert outcome.consume_outcome is ConsumeOutcome.LINKED
    rows = dict(_all(engine, "SELECT generation, state FROM telegram_link"))
    assert rows[3] == "revoked"
    assert rows[4] == "active"
    assert (
        _scalar(engine, "SELECT COUNT(*) FROM telegram_link WHERE state = 'active'")
        == expected["counts"]["telegram_link__state_active"]
        == 1
    )
    assert _scalar(engine, "SELECT consumed_by_chat_id FROM telegram_link_code") == CHAT_B
    assert (
        sender.send_message_count == expected["outbound_call_counts"]["telegram.sendMessage"] == 1
    ), "exactly one confirmation, and no re-send of the old generation's digest"


def test_the_adapter_writes_no_delivery_row_of_its_own() -> None:
    """Fixture ``e`` ``delivery__auto_created_for_new_generation: 0``, structurally.

    ``contracts/modules.yaml`` gives ``MOD-telegram-adapter`` no edge that would let it move
    a payload to a new recipient, and ``I11`` forbids source content deciding a recipient.
    The absence is asserted on the package source: no statement in it names a delivery table.
    """
    package = REPO_ROOT / "server" / "app" / "telegram"
    for module in sorted(package.glob("*.py")):
        body = module.read_text("utf-8")
        for table in ("delivery_part", "delivery_attempt", "outbox_intent"):
            assert f"FROM {table}" not in body and f"INTO {table}" not in body, module.name


def test_unlink_is_idempotent_and_leaves_the_generation_history(engine) -> None:
    """``telegram.unlink``: an app action (``AMD-B10``), safe to repeat.

    The revoked row stays. Generations must never be reused -- a delivery pins one -- so the
    history is what makes the next generation number honest.
    """
    now = datetime(2026, 9, 7, tzinfo=UTC)
    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=now, policy=DEFAULT_LINKING_POLICY
        )
        result = consume_link_code(
            connection,
            owner_id=OWNER_ID,
            chat_id=CHAT_A,
            message_text=issued.code,
            now=now,
            policy=DEFAULT_LINKING_POLICY,
        )
    assert result.link is not None and result.link.generation == 1

    with engine.begin() as connection:
        first = unlink(connection, owner_id=OWNER_ID, now=now)
    with engine.begin() as connection:
        second = unlink(connection, owner_id=OWNER_ID, now=now)

    assert first.was_linked and first.revoked_generation == 1
    assert not second.was_linked and second.revoked_generation is None
    assert _scalar(engine, "SELECT COUNT(*) FROM telegram_link") == 1
    assert _scalar(engine, "SELECT state FROM telegram_link") == "revoked"

    # An unlinked chat is a stranger again: EDGE-07, silent from here on.
    sender = RecordingSender()
    outcome = receive_update(
        _context(engine, sender), _message(9, CHAT_A, "/status", at=now), now=now
    )
    assert outcome.replies == () and sender.send_message_count == 0
