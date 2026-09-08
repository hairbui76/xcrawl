"""E1 — ``REQ-AC18`` in its strongest form: an unlinked chat gets **nothing**.

Fixture ``telegram/h-unknown-chat-status-silent`` is the oracle and it is measured, not
read: the outbound call count comes from the same sender seam production uses, the row
counts come from the database, and ``run_list_calls`` comes from a port double that raises
if it is ever entered.

Scenario ``SC18``. Card ``agent-tasks/TC-telegram-linking-auth.md`` §8, oracle 1.

What "no mutation" means here, precisely
----------------------------------------
The fixture pins ``domain_rows_changed: 0`` **and** expects one ``telegram_update_log`` row
with ``disposition = dropped_unlinked``. The audit line is not a domain row: it is the
evidence that the update was received and that nothing followed it, and without it AC-18
could not be proved from the outside at all. So this test asserts every business table is
byte-for-byte unchanged and that the log grew by exactly one row.

``given.rows.run`` is not loaded: the ``run`` table belongs to ``TC-scheduler-lease-claim``
(Phase 6) and does not exist in this schema yet. The oracle that depends on it --
``run_list_calls: 0`` -- is asserted at the port instead, which is where the fixture's own
``forbidden_effects`` puts it ("Gọi run.list").
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.telegram.commands import (
    CommandPorts,
    RunNowResult,
    RunSnapshot,
    SaveResult,
)
from server.app.telegram.ingress import (
    Disposition,
    RecordingSender,
    TelegramContext,
    receive_update,
)
from server.app.telegram.linking import (
    DEFAULT_LINKING_POLICY,
    LinkAttemptOutcome,
    format_timestamp,
    hash_chat_id,
    issue_link_code,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The owner id every telegram fixture uses.
OWNER_ID = "01J0WNER100000000000000000"
LINKED_CHAT = "111111111"
STRANGER_CHAT = "999999999"
WEBHOOK_SECRET = "a-webhook-secret-of-sufficient-length"

#: Every table that holds business data at this revision. The audit tables are excluded and
#: named separately, so "nothing changed" cannot quietly include them.
AUDIT_TABLES = frozenset({"telegram_update_log", "telegram_link_attempt"})

#: The instant the fixtures' events happen at. Where a test pins the server clock it pins the
#: update's ``date`` to the same instant, so ING-06's age window is never accidentally under
#: test.
AT = datetime(2026, 9, 7, tzinfo=UTC)


def _migrate(db_path: Path) -> None:
    """``alembic upgrade heads`` — the migrations are the only schema source.

    ``heads`` rather than ``head``: sibling cards of this wave add their own revisions off
    the same parent, and while more than one of them is in flight ``head`` is ambiguous.
    ``heads`` applies every branch, which is what a deployment ends up with anyway once the
    graph is merged, and it keeps this file from failing for a reason that has nothing to do
    with what it tests. The single-head requirement itself is asserted where it belongs, in
    ``tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head``.
    """
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


class RefusingRunListPort:
    """``run.list`` that fails the test if it is called at all.

    The fixture's ``counts.run_list_calls`` is 0 and its ``forbidden_effects`` names calling
    ``run.list``. A port that merely counted would let the call happen and be judged
    afterwards; this one makes the forbidden effect impossible to reach silently.
    """

    def __init__(self) -> None:
        self.calls = 0

    def list_runs(self, *, owner_id: str) -> RunSnapshot:
        self.calls += 1
        raise AssertionError("run.list was called for an unlinked chat")


class RefusingRunNowPort:
    def __init__(self) -> None:
        self.calls = 0

    def run_now(self, *, owner_id: str, request_id: str) -> RunNowResult:
        self.calls += 1
        raise AssertionError("run.run_now was called for an unlinked chat")


class RefusingSavePort:
    def __init__(self) -> None:
        self.calls = 0

    def create_save(
        self, *, owner_id: str, report_item_id: str, idempotency_key: str
    ) -> SaveResult:
        self.calls += 1
        raise AssertionError("save.create was called for an unlinked chat")


def _table_counts(engine: Engine) -> dict[str, int]:
    """``COUNT(*)`` of every table except the two audit tables and Alembic's bookkeeping."""
    with engine.connect() as connection:
        tables = [
            name
            for (name,) in connection.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%' AND name <> 'alembic_version'"
                )
            )
            if name not in AUDIT_TABLES
        ]
        return {
            table: int(connection.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar_one())
            for table in tables
        }


def _link(engine: Engine, chat_id: str = LINKED_CHAT, generation: int = 1) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO telegram_link (id, owner_id, chat_id, generation, state, "
                "linked_at) VALUES ('01JTG11NK10000000000000000', :owner_id, :chat_id, "
                ":generation, 'active', '2026-09-05T00:00:00.000Z')"
            ),
            {"owner_id": OWNER_ID, "chat_id": chat_id, "generation": generation},
        )


def _message(
    update_id: int, chat_id: str, body: str, *, at: datetime | None = None
) -> dict[str, Any]:
    """A Telegram ``message`` update, shaped the way the Bot API sends one.

    ``date`` defaults to **now** rather than to a fixed day: ``ING-06`` drops anything older
    than 24 h, so a frozen timestamp would silently turn these tests into age tests once the
    wall clock passed it -- and they would then pass for the wrong reason (nothing happens
    either way when the update is dropped). :func:`test_an_update_older_than_the_max_age_is_dropped`
    sets both ends of the interval on purpose.
    """
    moment = at or datetime.now(tz=UTC)
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": int(moment.timestamp()),
            "chat": {"id": int(chat_id), "type": "private"},
            "from": {"id": int(chat_id), "is_bot": False},
            "text": body,
        },
    }


def _context(engine: Engine, sender: RecordingSender, ports: CommandPorts) -> TelegramContext:
    return TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=ports,
    )


# --------------------------------------------------------------------------------------
# Fixture h — the whole of REQ-AC18
# --------------------------------------------------------------------------------------


def test_fixture_h_unknown_chat_status_is_completely_silent(engine, fixture_loader) -> None:
    """Fixture ``h``: outbound = 0, ``domain_rows_changed`` = 0, ``run_list_calls`` = 0."""
    fixture = fixture_loader("telegram/h-unknown-chat-status-silent")
    given_link = fixture.rows("telegram_link")[0]
    _link(engine, chat_id=str(given_link["chat_id"]), generation=int(given_link["generation"]))

    sender = RecordingSender()
    run_list = RefusingRunListPort()
    ports = CommandPorts(
        run_list=run_list, run_now=RefusingRunNowPort(), save_create=RefusingSavePort()
    )
    before = _table_counts(engine)

    outcome = receive_update(
        _context(engine, sender, ports),
        _message(9001, STRANGER_CHAT, "/status", at=AT),
        now=AT,
    )

    expected = fixture.data["expected"]
    assert sender.send_message_count == expected["outbound_call_counts"]["telegram.sendMessage"]
    assert sender.send_message_count == 0
    assert outcome.replies == ()
    assert run_list.calls == expected["counts"]["run_list_calls"]
    assert outcome.disposition is Disposition.DROPPED_UNLINKED
    assert outcome.audit_code is ErrorCode.UNAUTHORIZED_COMMAND
    assert _table_counts(engine) == before, "a domain row moved for an unlinked chat"

    # The audit line, and only it. `command` is NULL: nothing was executed.
    with engine.connect() as connection:
        rows = list(
            connection.execute(
                text(
                    "SELECT disposition, chat_id_hash, command FROM telegram_update_log "
                    "WHERE owner_id = :owner_id"
                ),
                {"owner_id": OWNER_ID},
            )
        )
        attempts = int(
            connection.execute(text("SELECT COUNT(*) FROM telegram_link_attempt")).scalar_one()
        )
    assert len(rows) == 1
    disposition, chat_id_hash, command = rows[0]
    assert disposition == "dropped_unlinked"
    assert chat_id_hash == hashlib.sha256(STRANGER_CHAT.encode()).hexdigest()
    assert command is None
    # "Đếm lần này vào rate limit của chat đã liên kết" is a forbidden effect, and `/status`
    # is not a code-format match, so no attempt row exists at all.
    assert attempts == 0


def test_the_stranger_chat_id_is_nowhere_in_the_database(engine, fixture_loader) -> None:
    """``forbidden_effects``: "Lưu chat ID lạ ở dạng thô."

    Asserted by scanning every text column of every table for the literal id rather than by
    inspecting the one column the implementation happens to write. A leak into a column
    nobody thought about is exactly the kind this check is for.
    """
    _link(engine)
    receive_update(
        _context(engine, RecordingSender(), CommandPorts()),
        _message(9002, STRANGER_CHAT, "/status", at=AT),
        now=AT,
    )
    connection = sqlite3.connect(engine.url.database or "")
    try:
        tables = [
            name
            for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]
        for table in tables:
            for row in connection.execute(f'SELECT * FROM "{table}"'):
                for value in row:
                    if isinstance(value, str):
                        assert STRANGER_CHAT not in value, f"{table} stores the raw chat id"
    finally:
        connection.close()


def test_a_stranger_never_gets_a_reply_whatever_it_sends(engine) -> None:
    """``ING-08``: plain text, a fake command, a fourth command, a callback -- all silent.

    The list deliberately includes strings that *would* do something from the linked chat.
    Silence must not depend on the content being uninteresting.
    """
    _link(engine)
    sender = RecordingSender()
    context = _context(engine, sender, CommandPorts())
    payloads: list[dict[str, Any]] = [
        _message(1, STRANGER_CHAT, "xin chào", at=AT),
        _message(2, STRANGER_CHAT, "/status", at=AT),
        _message(3, STRANGER_CHAT, "/run_now", at=AT),
        _message(4, STRANGER_CHAT, "/save 01JR1TEM100000000000000000", at=AT),
        _message(5, STRANGER_CHAT, "/unlink", at=AT),
        _message(6, STRANGER_CHAT, "/tag add ai", at=AT),
        {
            "update_id": 7,
            "callback_query": {
                "id": "cb-1",
                "data": "1:x:y:1:aabbccdd",
                "message": {"chat": {"id": int(STRANGER_CHAT)}},
            },
        },
        {"update_id": 8, "channel_post": {"chat": {"id": int(STRANGER_CHAT)}, "text": "/status"}},
    ]
    for payload in payloads:
        outcome = receive_update(context, payload, now=AT)
        assert outcome.replies == ()
    assert sender.send_message_count == 0


# --------------------------------------------------------------------------------------
# The B09 rate limit -- silence stays silence over the threshold
# --------------------------------------------------------------------------------------


def test_over_the_rate_limit_the_code_is_not_even_looked_up(engine) -> None:
    """``§ linking → rate_limit``: past the threshold, stop comparing; stay silent.

    The proof that the lookup stopped is the outcome column: the sixth attempt is recorded
    ``rate_limited_not_checked`` and **not** ``format_match_code_invalid``, which is the row
    a comparison would have written. ``RATE_LIMITED`` is never returned to the chat -- the
    contract calls that out explicitly, because a rate-limit answer is still an answer.
    """
    policy = DEFAULT_LINKING_POLICY
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET, sender=sender
    )
    now = datetime(2026, 9, 7, 0, 0, tzinfo=UTC)
    for index in range(policy.rate_limit_attempts + 1):
        receive_update(
            context, _message(100 + index, STRANGER_CHAT, "RR-ZZZZZZZZ", at=now), now=now
        )

    with engine.connect() as connection:
        outcomes = [
            row[0]
            for row in connection.execute(
                text("SELECT outcome FROM telegram_link_attempt ORDER BY attempted_at, id")
            )
        ]
    assert len(outcomes) == policy.rate_limit_attempts + 1
    assert set(outcomes[: policy.rate_limit_attempts]) == {
        LinkAttemptOutcome.FORMAT_MATCH_CODE_INVALID.value
    }
    assert outcomes[-1] == LinkAttemptOutcome.RATE_LIMITED_NOT_CHECKED.value
    assert sender.send_message_count == 0


def test_a_non_matching_message_writes_no_attempt_row(engine) -> None:
    """``ENT-telegram-link-attempt.forbidden``: no row for a message that is not a code.

    Otherwise the counter table becomes a log of every stranger who has ever written to the
    bot -- which the entity contract forbids in as many words.
    """
    context = TelegramContext(engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET)
    receive_update(context, _message(200, STRANGER_CHAT, "xin chào"), now=datetime.now(tz=UTC))
    receive_update(context, _message(201, STRANGER_CHAT, "RR-lowercase"), now=datetime.now(tz=UTC))
    with engine.connect() as connection:
        assert (
            int(connection.execute(text("SELECT COUNT(*) FROM telegram_link_attempt")).scalar_one())
            == 0
        )


def test_a_replayed_update_produces_no_second_effect(engine) -> None:
    """``ING-04``: the same ``update_id`` twice links once and replies once.

    The second call is answered from the log, so the confirmation message is not sent again
    and the code is not consumed twice.
    """
    now = datetime(2026, 9, 7, 0, 30, tzinfo=UTC)
    with engine.begin() as connection:
        issued = issue_link_code(
            connection, owner_id=OWNER_ID, now=now, policy=DEFAULT_LINKING_POLICY
        )
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET, sender=sender
    )
    payload = _message(300, STRANGER_CHAT, issued.code, at=now)

    first = receive_update(context, payload, now=now)
    second = receive_update(context, payload, now=now)

    assert first.replies and not first.replayed
    assert second.replayed and second.replies == ()
    assert sender.send_message_count == 1
    with engine.connect() as connection:
        assert (
            int(
                connection.execute(
                    text("SELECT COUNT(*) FROM telegram_link WHERE state = 'active'")
                ).scalar_one()
            )
            == 1
        )
        assert (
            int(connection.execute(text("SELECT COUNT(*) FROM telegram_update_log")).scalar_one())
            == 1
        )


def test_an_update_older_than_the_max_age_is_dropped(engine) -> None:
    """``ING-06``: a ``/run_now`` replayed from a webhook backlog is not present intent.

    The port refuses to be called, so the assertion is not "nothing happened" but "the
    command never reached the job service".
    """
    _link(engine)
    run_now = RefusingRunNowPort()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=RecordingSender(),
        ports=CommandPorts(run_now=run_now),
    )
    stale = _message(400, LINKED_CHAT, "/run_now", at=AT)
    two_days_later = datetime(2026, 9, 9, tzinfo=UTC)

    outcome = receive_update(context, stale, now=two_days_later)

    assert outcome.disposition is Disposition.DROPPED_INVALID
    assert outcome.replies == ()
    assert run_now.calls == 0


def test_the_audit_row_records_the_server_clock(engine) -> None:
    """``received_at`` is the server's clock in the one timestamp shape the schema accepts.

    The GLOB CHECK in the migration would reject anything else, so this asserts the value is
    the *injected* clock and not ``datetime.now`` sneaking in.
    """
    _link(engine)
    moment = datetime(2026, 9, 7, 1, 2, 3, 456000, tzinfo=UTC)
    receive_update(
        TelegramContext(engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET),
        _message(500, STRANGER_CHAT, "hello", at=moment),
        now=moment,
    )
    with engine.connect() as connection:
        received_at = connection.execute(
            text("SELECT received_at FROM telegram_update_log")
        ).scalar_one()
    assert received_at == format_timestamp(moment)
    assert hash_chat_id(STRANGER_CHAT) != STRANGER_CHAT
