"""E1 — the allowlist is exactly three, the refusals carry the right codes, and the
plain-text scope is not quietly exceeded.

Oracles: ``contracts/telegram/commands.yaml`` (§1 ingress rules, §3 the three commands, §4
error map), ``contracts/data/entities.yaml``, ``contracts/errors.yaml``,
``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` (the six edges that
touch ``MOD-telegram-adapter``) and ``acceptance/fixtures/telegram/l-run-now-while-needs-user
.json``. Scenarios ``SC18``, ``SC45``, ``SC46``, ``SC49``; card §8 oracles 4 and 5, and card
§10 ``SG-DENY`` (the wrong code is a FAIL in its own right).

Two of the assertions here are about what the code does **not** contain
-----------------------------------------------------------------------
``test_the_package_sends_no_markup_and_no_parse_mode`` and
``test_the_package_imports_no_module_it_has_no_edge_to`` read the package source. Both facts
-- "plain text only while ``CR-PC07-04`` is open" and "no edge to tag, settings, secrets or
the data store" -- are absences, and an absence that is only maintained by review comes back.

Paths this card deliberately did not run
-----------------------------------------
The ``callback_data`` validation of ``CMD-save`` (fixture ``f-stale-callback-no-save``,
``SC46``) is ``NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)``: the ``callback_data`` length limit,
the parse-mode escape table and the buttons-per-keyboard limit are still ``KC`` in
``contracts/telegram/delivery.md`` §3.4, and building the five-step validator against a
guessed 64-byte budget would be exactly the guess card §10 ``SG-01`` forbids. The
non-implementation is asserted (a callback is dropped, never acted on) and the contract path
is marked, not skipped silently.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.main import create_app
from server.app.telegram import commands as commands_module
from server.app.telegram.commands import (
    ALLOWED_COMMANDS,
    COMMAND_OPERATION,
    MAX_MESSAGE_CHARS,
    REPLY_COMMAND_REMINDER,
    REPLY_RUN_NOW_NEEDS_USER,
    TRIGGERS,
    CommandId,
    CommandPorts,
    RunNowResult,
    RunSnapshot,
    SaveResult,
    assert_no_resume_path,
    parse_command,
    split_plain_text,
)
from server.app.telegram.ingress import (
    HTTP_STATUS,
    TELEGRAM_SECRET_HEADER,
    Disposition,
    RecordingSender,
    TelegramContext,
    TelegramError,
    classify_update,
    receive_update,
    verify_webhook_secret,
)
from server.app.telegram.linking import DEFAULT_LINKING_POLICY

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = REPO_ROOT / "server" / "app" / "telegram"
OWNER_ID = "01J0WNER100000000000000000"
LINKED_CHAT = "111111111"
STRANGER_CHAT = "999999999"
WEBHOOK_SECRET = "a-webhook-secret-of-sufficient-length"
WIRE_HEADERS = {"X-Schema-Version": "0.3.0", "X-Request-Id": "01J0000000000000000000000Z"}


@pytest.fixture(scope="module")
def commands_contract() -> dict[str, Any]:
    document = yaml.safe_load(
        (REPO_ROOT / "contracts" / "telegram" / "commands.yaml").read_text("utf-8")
    )
    assert isinstance(document, dict)
    return document


@pytest.fixture(scope="module")
def openapi() -> dict[str, Any]:
    document = yaml.safe_load(
        (REPO_ROOT / "contracts" / "http" / "openapi.yaml").read_text("utf-8")
    )
    assert isinstance(document, dict)
    return document


def _migrate(db_path: Path) -> None:
    """``alembic upgrade heads`` — see the note in the integration suite's own helper."""
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
        connection.execute(
            text(
                "INSERT INTO telegram_link (id, owner_id, chat_id, generation, state, "
                "linked_at) VALUES ('01JTG11NK10000000000000000', :owner_id, :chat_id, 1, "
                "'active', '2026-09-05T00:00:00.000Z')"
            ),
            {"owner_id": OWNER_ID, "chat_id": LINKED_CHAT},
        )
    yield built
    built.dispose()


class NeedsUserRunNowPort:
    """``run.run_now`` on a run that is ``needs_user`` (fixture ``l``).

    ``RN-01``: the port refuses to pass it, and records that it was asked so the test can
    tell "the adapter did not call" from "the port declined".
    """

    def __init__(self) -> None:
        self.calls = 0

    def run_now(self, *, owner_id: str, request_id: str) -> RunNowResult:
        self.calls += 1
        return RunNowResult(
            run_id="01JRVN10000000000000000000",
            queued=False,
            blocked_needs_user=True,
            status_label="Chờ xác minh",
        )


class RefusingPorts:
    """Every port raises. Used where the oracle is that no operation was called at all."""

    def list_runs(self, *, owner_id: str) -> RunSnapshot:
        raise AssertionError("run.list must not be called")

    def run_now(self, *, owner_id: str, request_id: str) -> RunNowResult:
        raise AssertionError("run.run_now must not be called")

    def create_save(
        self, *, owner_id: str, report_item_id: str, idempotency_key: str
    ) -> SaveResult:
        raise AssertionError("save.create must not be called")


def _message(update_id: int, chat_id: str, body: str) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": int(datetime(2026, 9, 7, tzinfo=UTC).timestamp()),
            "chat": {"id": int(chat_id), "type": "private"},
            "text": body,
        },
    }


def _rows(engine: Engine, sql: str) -> list[tuple[Any, ...]]:
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(sql))]


# --------------------------------------------------------------------------------------
# The allowlist is exactly the contract's
# --------------------------------------------------------------------------------------


def test_the_allowlist_is_the_three_commands_of_the_contract(commands_contract) -> None:
    """``§3``: three ids, three operations, and no fourth of either."""
    contract_ids = [entry["id"] for entry in commands_contract["commands"]["list"]]
    assert len(contract_ids) == 3
    assert {command.value for command in ALLOWED_COMMANDS} == set(contract_ids)
    assert {command.value for command in CommandId} == set(contract_ids)

    contract_operations = {
        entry["id"]: entry["operation_id"] for entry in commands_contract["commands"]["list"]
    }
    for command, operation in COMMAND_OPERATION.items():
        assert operation.value == contract_operations[command.value]


def test_there_is_no_fourth_command_and_no_path_to_resume() -> None:
    """``AMD-B10`` / ``FE-33`` / ``DC-TGC-01``: no resume, no unlink, no tag, no settings."""
    assert_no_resume_path()
    assert len(TRIGGERS) == 3
    for absent in ("/resume", "/unlink", "/tag", "/settings", "/help", "/start", "/stop"):
        assert absent not in TRIGGERS
        assert parse_command(absent) is None
    assert parse_command("/status") is not None
    # Telegram's `@botname` suffix in groups is still the same command, not a fourth one.
    assert parse_command("/status@rr_bot") == parse_command("/status")


def test_the_forbidden_edge_to_run_resume_is_refused_with_forbidden_edge() -> None:
    """``FE-33`` at the edge level: ``require_edge`` answers ``FORBIDDEN_EDGE``.

    ``UNAUTHORIZED_COMMAND`` is the *path*-level code the boundary fixture pins for the same
    edge (its ``two_level_note_vi``), and it is asserted separately below. The two describe
    two layers; conflating them is the ``SG-DENY`` failure.
    """
    from server.app.auth.middleware import require_edge
    from server.app.auth.service import AuthError

    with pytest.raises(AuthError) as raised:
        require_edge(OperationId.RUN_RESUME, "MOD-telegram-adapter", edge_ref="FE-33")
    assert raised.value.code is ErrorCode.FORBIDDEN_EDGE

    # And the three edges the adapter *is* granted stay granted.
    for operation in (OperationId.RUN_LIST, OperationId.RUN_RUN_NOW, OperationId.SAVE_CREATE):
        require_edge(operation, "MOD-telegram-adapter")


def test_the_boundary_sweep_rows_for_this_module_carry_the_codes_this_card_uses(
    fixture_loader,
) -> None:
    """``SC49``: the six sweep events whose caller or callee is the Telegram adapter.

    The fixture is the oracle for **which** code each edge answers with; this test asserts
    the mapping the implementation actually holds, rather than restating the fixture.
    """
    fixture = fixture_loader("boundary/a-default-deny-sweep-36-edges")
    by_ref = {event["forbidden_edge_ref"]: event for event in fixture.events}

    # Edge-class refusals, decided in-process by the module registry.
    for edge_ref in ("FE-29", "FE-32"):
        assert by_ref[edge_ref]["expected_error_code"] == ErrorCode.FORBIDDEN_EDGE.value

    # Path-level refusals through the Telegram ingress: the code is UNAUTHORIZED_COMMAND and
    # the chat is told nothing (`telegram_ingress_vi`).
    for edge_ref in ("FE-30", "FE-31", "FE-33"):
        event = by_ref[edge_ref]
        assert event["expected_error_code"] == ErrorCode.UNAUTHORIZED_COMMAND.value
        assert event["expected_error_code_edge_class"] == ErrorCode.UNAUTHORIZED.value

    # FE-36: the network reaching a domain service directly is an HTTP principal-class
    # refusal, which is not this module's decision but must not be confused with the above.
    assert by_ref["FE-36"]["expected_error_code"] == ErrorCode.UNAUTHORIZED.value


def test_a_linked_chat_asking_for_tags_or_settings_gets_the_allowlist_refusal(engine) -> None:
    """``FE-30``/``FE-31``, ``EDGE-05``, ``ING-09``: refused by the allowlist, no mutation.

    The reply is the three-command reminder, which ``commands.yaml``
    ``silent_drop_summary`` prescribes for a **linked** chat -- silence is the rule for
    unlinked ones. The audit code is ``UNAUTHORIZED_COMMAND``, which is what the boundary
    fixture pins for these edges.
    """
    sender = RecordingSender()
    ports = RefusingPorts()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(run_list=ports, run_now=ports, save_create=ports),
    )
    for index, body in enumerate(
        ("/tag add ai", "/settings set provider anthropic", "/resume", "/unlink")
    ):
        outcome = receive_update(context, _message(600 + index, LINKED_CHAT, body))
        assert outcome.disposition is Disposition.DROPPED_INVALID
        assert outcome.audit_code is ErrorCode.UNAUTHORIZED_COMMAND
        assert outcome.replies == (REPLY_COMMAND_REMINDER,)
        assert outcome.command is None

    commands_logged = [row[0] for row in _rows(engine, "SELECT command FROM telegram_update_log")]
    assert set(commands_logged) == {None}, "a refused string was logged as a command"


def test_the_package_imports_no_module_it_has_no_edge_to() -> None:
    """``FE-29``, ``FE-30``, ``FE-31``, ``FE-32`` as an import rule.

    ``enforcement: ENF-import-rule`` in ``contracts/modules.yaml`` is exactly this: the edge
    is refused by there being no import to make the call through. The one import into another
    card's package is ``server.app.auth`` (owner session and CSRF for the two app routes),
    which is an allowed edge for ``MOD-web-ui``-facing operations.
    """
    forbidden_imports = (
        "server.app.tag",
        "server.app.settings",
        "server.app.secret",
        "server.app.delivery",
        "server.app.saved",
        "server.app.report",
    )
    for module in sorted(PACKAGE.glob("*.py")):
        body = module.read_text("utf-8")
        for forbidden in forbidden_imports:
            assert forbidden not in body, f"{module.name} imports {forbidden}"


# --------------------------------------------------------------------------------------
# The plain-text scope (OD-20260908-09, CR-PC07-04)
# --------------------------------------------------------------------------------------


def test_the_package_sends_no_markup_and_no_parse_mode() -> None:
    """Card §10 ``SG-01``: three formatting facts are ``KC``, so none of them may be used.

    Searched over the package source rather than asserted on one call: the stop condition is
    that the capability is absent, and a single well-behaved call site would not prove that.
    Occurrences inside a docstring naming the forbidden thing are excluded by looking only at
    code lines.
    """
    forbidden = ("parse_mode", "reply_markup", "inline_keyboard", "answerCallbackQuery")
    for module in sorted(PACKAGE.glob("*.py")):
        for number, line in enumerate(module.read_text("utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith(("#", "*", '"', "'", ":", "|", "-")) or "``" in line:
                continue  # prose: the modules discuss these names to say they are refused
            for name in forbidden:
                assert name not in stripped, f"{module.name}:{number} uses {name}"


def test_a_callback_query_is_never_acted_on(engine) -> None:
    """``SC46`` in the only form this scope can prove: a callback does nothing at all.

    This system sends no buttons, so no callback it produced can exist. The five-step
    validation of ``commands.yaml`` §3 ``CMD-save`` and fixture ``f-stale-callback-no-save``
    are ``NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)``; what *is* proved is that the blocked
    path cannot be reached by accident -- no ``save.create`` call, no row, no reply.
    """
    sender = RecordingSender()
    ports = RefusingPorts()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(run_list=ports, run_now=ports, save_create=ports),
    )
    outcome = receive_update(
        context,
        {
            "update_id": 700,
            "callback_query": {
                "id": "cb-1",
                "data": "1:01JREP0RT10000000000000000:01JR1TEM100000000000000000:3:aabbccdd",
                "message": {"chat": {"id": int(LINKED_CHAT)}},
            },
        },
    )
    assert outcome.disposition is Disposition.DROPPED_INVALID
    assert outcome.audit_code is ErrorCode.VALIDATION_ERROR
    assert outcome.replies == ()
    assert sender.send_message_count == 0
    assert _rows(engine, "SELECT COUNT(*) FROM saved_item")[0][0] == 0


@pytest.mark.xfail(
    run=False,
    reason=(
        "NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04): fixture telegram/f-stale-callback-no-save "
        "needs the callback_data format, whose length limit, escape table and keyboard "
        "limits are still KC in contracts/telegram/delivery.md §3.4. Implementing the "
        "five-step validator against a guessed 64-byte budget is what card §10 SG-01 forbids."
    ),
)
def test_fixture_f_stale_callback_validation_order() -> None:  # pragma: no cover - NOT_RUN
    raise AssertionError("not implemented under the plain-text scope")


def test_a_reply_is_split_by_the_raw_4096_character_rule() -> None:
    """``delivery.md`` §3.4/§3.5: 4096 characters, counted on the raw string.

    Only the resolved half of §3.4 is used. No escaping happens, so there is nothing to keep
    balanced across a cut, and the "count the raw string" rule is a one-way safe reading
    under either counting semantics.
    """
    assert MAX_MESSAGE_CHARS == 4096
    assert split_plain_text("ngắn") == ("ngắn",)
    long_text = " ".join(["từ"] * 4000)
    parts = split_plain_text(long_text)
    assert len(parts) > 1
    assert all(len(part) <= MAX_MESSAGE_CHARS for part in parts)
    assert "".join(part.replace(" ", "") for part in parts) == long_text.replace(" ", "")


# --------------------------------------------------------------------------------------
# The working parameters are the contract's
# --------------------------------------------------------------------------------------


def test_the_linking_policy_defaults_equal_the_contract(commands_contract) -> None:
    """``SG-02``: the three PROVISIONAL parameters are read from settings, not hard-coded.

    Read from the contract here so that changing ``commands.yaml`` breaks the build rather
    than leaving the code quietly one revision behind.
    """
    linking = commands_contract["linking"]
    assert DEFAULT_LINKING_POLICY.code_regex == linking["code_format"]["regex"]
    assert linking["expiry"]["unit"] == "minutes"
    assert DEFAULT_LINKING_POLICY.code_ttl_seconds == int(linking["expiry"]["value"]) * 60
    assert linking["rate_limit"]["unit"] == "attempts_per_chat_per_hour"
    assert DEFAULT_LINKING_POLICY.rate_limit_attempts == int(linking["rate_limit"]["value"])
    assert DEFAULT_LINKING_POLICY.rate_limit_window_seconds == 3600

    # ING-06's max age, still PROVISIONAL as CR-PC07-05 (card §10 SG-03).
    ing_06 = next(
        rule for rule in commands_contract["ingress"]["replay_and_dedup"] if rule["id"] == "ING-06"
    )
    assert "86400" in ing_06["rule_vi"]
    assert DEFAULT_LINKING_POLICY.update_max_age_seconds == 86400


# --------------------------------------------------------------------------------------
# ING-01: the webhook secret
# --------------------------------------------------------------------------------------


def test_the_webhook_secret_is_compared_constant_time_and_denies_by_default() -> None:
    """``ING-01`` + ``contracts/ops/secrets.md`` §7.

    The constant-time property is asserted on the implementation -- the comparison is
    ``hmac.compare_digest`` -- because timing itself is not measurable in a unit test without
    making the suite flaky. The behavioural half (every mismatch is ``UNAUTHORIZED``,
    including a correct prefix) is asserted directly.
    """
    source = (PACKAGE / "ingress.py").read_text("utf-8")
    assert "hmac.compare_digest" in source
    assert "presented == expected" not in source

    verify_webhook_secret(WEBHOOK_SECRET, WEBHOOK_SECRET)
    for presented in (None, "", WEBHOOK_SECRET[:-1], WEBHOOK_SECRET + "x", "wrong"):
        with pytest.raises(TelegramError) as raised:
            verify_webhook_secret(presented, WEBHOOK_SECRET)
        assert raised.value.code is ErrorCode.UNAUTHORIZED
        assert raised.value.http_status == 401
    # Unconfigured server: deny, never allow.
    with pytest.raises(TelegramError):
        verify_webhook_secret(WEBHOOK_SECRET, None)


def test_a_wrong_secret_processes_nothing_at_all(engine) -> None:
    """``ING-01``/``ING-02``: 401 and **no** audit row, because nothing was authenticated.

    The payload claims to be from the linked chat; that claim means nothing before the
    secret matches, which is ING-02 in one assertion.
    """
    context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET, sender=RecordingSender()
    )
    app = create_app()
    app.state.telegram_context = context
    client = TestClient(app, base_url="https://testserver")

    response = client.post(
        "/v1/telegram/webhook",
        json=_message(800, LINKED_CHAT, "/status"),
        headers={**WIRE_HEADERS, TELEGRAM_SECRET_HEADER: "not-the-secret"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == ErrorCode.UNAUTHORIZED.value
    assert body["correlation_id"]
    assert WEBHOOK_SECRET not in response.text
    assert _rows(engine, "SELECT COUNT(*) FROM telegram_update_log")[0][0] == 0


def test_the_webhook_answers_204_even_when_it_stays_silent(engine) -> None:
    """openapi: *"LUÔN 204 với mọi update hợp lệ về mặt transport"*.

    A distinguishable status for a dropped update would be a reply by another channel: it
    would tell whoever posted it that this address is a bot and that the message mattered.
    """
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET, sender=sender
    )
    app = create_app()
    app.state.telegram_context = context
    client = TestClient(app, base_url="https://testserver")

    for update_id, chat in ((900, STRANGER_CHAT), (901, LINKED_CHAT)):
        response = client.post(
            "/v1/telegram/webhook",
            json=_message(update_id, chat, "một tin nhắn"),
            headers={**WIRE_HEADERS, TELEGRAM_SECRET_HEADER: WEBHOOK_SECRET},
        )
        assert response.status_code == 204, response.text
    # The stranger got nothing; the linked chat got the reminder. One send in total.
    assert sender.send_message_count == 1


def test_only_message_and_callback_query_are_recognised() -> None:
    """``ING-03``: every other update type is unsupported, and an id-less body is invalid."""
    assert classify_update(_message(1, LINKED_CHAT, "hi")).kind.value == "message"
    callback = classify_update(
        {"update_id": 2, "callback_query": {"id": "x", "message": {"chat": {"id": 1}}}}
    )
    assert callback.kind.value == "callback_query"
    for payload in (
        {"update_id": 3, "channel_post": {"chat": {"id": 1}, "text": "hi"}},
        {"update_id": 4, "inline_query": {"query": "x"}},
        {"update_id": 5, "poll": {"id": "p"}},
        {"update_id": 6, "edited_message": {"chat": {"id": 1}, "text": "hi"}},
    ):
        assert classify_update(payload).kind.value == "unsupported"
    with pytest.raises(TelegramError) as raised:
        classify_update({"message": {"text": "no update_id"}})
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


# --------------------------------------------------------------------------------------
# RN-01 — fixture l
# --------------------------------------------------------------------------------------


def test_fixture_l_run_now_does_not_pass_a_needs_user_run(engine, fixture_loader) -> None:
    """Fixture ``l``: ``/run_now`` while a run is ``needs_user`` → no resume, one reply.

    The reply is the contract's verbatim text and it points into the app, which is the only
    place the resume action exists (``AMD-B10``, ``screens.yaml`` ``NC-UI-04``). The run row
    itself lives in ``TC-scheduler-lease-claim``'s schema, so the "run__status_changes: 0"
    half of the fixture is asserted at the port: it is asked once and it refuses, and nothing
    downstream of it is called.
    """
    fixture = fixture_loader("telegram/l-run-now-while-needs-user")
    expected = fixture.data["expected"]["after_event_2"]

    port = NeedsUserRunNowPort()
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(run_now=port),
    )

    outcome = receive_update(context, _message(1000, LINKED_CHAT, "/run_now"))

    assert outcome.command == CommandId.RUN_NOW.value
    assert outcome.replies == (REPLY_RUN_NOW_NEEDS_USER,)
    assert expected["reply_vi"] == REPLY_RUN_NOW_NEEDS_USER
    assert (
        sender.send_message_count == expected["outbound_call_counts"]["telegram.sendMessage"] == 1
    )
    assert port.calls == 1
    assert "resume" not in REPLY_RUN_NOW_NEEDS_USER.lower()


def test_the_run_now_reply_templates_are_the_contracts(commands_contract) -> None:
    """``reply_templates_vi`` of ``CMD-run-now`` and ``CMD-status``, compared verbatim."""
    by_id = {entry["id"]: entry for entry in commands_contract["commands"]["list"]}
    run_now = by_id["CMD-run-now"]["reply_templates_vi"]
    assert run_now["queued"] == commands_module.REPLY_RUN_NOW_QUEUED
    assert run_now["already_running"] == commands_module.REPLY_RUN_NOW_ALREADY_RUNNING
    assert run_now["blocked_needs_user"] == commands_module.REPLY_RUN_NOW_NEEDS_USER

    status = by_id["CMD-status"]["reply_templates_vi"]
    assert status["no_matching_content"] == commands_module.REPLY_STATUS_NO_MATCHING_CONTENT
    assert status["stopped_early"] == commands_module.REPLY_STATUS_STOPPED_EARLY
    assert status["run_failed"] == commands_module.REPLY_STATUS_RUN_FAILED
    assert status["delivery_unknown_suffix"] == commands_module.REPLY_DELIVERY_UNKNOWN_SUFFIX

    save = by_id["CMD-save"]["reply_templates_vi"]
    assert save["saved_new"] == commands_module.REPLY_SAVED_NEW
    assert save["saved_already"] == commands_module.REPLY_SAVED_ALREADY


def test_status_never_mutates_and_never_uses_the_forbidden_phrase(engine) -> None:
    """``ST-01``/``ST-02``: read-only, and the three states read differently.

    The forbidden phrase check is ``ST-02``'s own: "Không có nghiên cứu mới" must not appear,
    because an empty period is a *result*, not an absence of research.
    """

    class StubRunList:
        def __init__(self, snapshot: RunSnapshot) -> None:
            self.snapshot = snapshot

        def list_runs(self, *, owner_id: str) -> RunSnapshot:
            return self.snapshot

    snapshots = [
        RunSnapshot(run_id="r1", status="completed", outcome="empty"),
        RunSnapshot(run_id="r2", status="completed", stop_reason_vi="đạt giới hạn thời gian"),
        RunSnapshot(run_id="r3", status="failed", error_summary_safe="nguồn không phản hồi"),
    ]
    replies: list[str] = []
    for index, snapshot in enumerate(snapshots):
        sender = RecordingSender()
        context = TelegramContext(
            engine=engine,
            owner_id=OWNER_ID,
            webhook_secret=WEBHOOK_SECRET,
            sender=sender,
            ports=CommandPorts(run_list=StubRunList(snapshot)),
        )
        before = _rows(engine, "SELECT COUNT(*) FROM telegram_link")[0][0]
        outcome = receive_update(context, _message(1100 + index, LINKED_CHAT, "/status"))
        assert _rows(engine, "SELECT COUNT(*) FROM telegram_link")[0][0] == before
        assert outcome.command == CommandId.STATUS.value
        replies.append(outcome.replies[0])

    assert len(set(replies)) == 3, "the three run states must read differently (REQ-AC15)"
    for reply in replies:
        assert commands_module.FORBIDDEN_STATUS_PHRASE not in reply


def test_a_delivery_unknown_is_reported_as_its_own_sentence(engine) -> None:
    """``ST-03``/``I13``: never "đã gửi" while a part is ``unknown``."""

    class StubRunList:
        def list_runs(self, *, owner_id: str) -> RunSnapshot:
            return RunSnapshot(
                run_id="r1",
                status="completed",
                outcome="empty",
                delivery_unknown=True,
                collector_state="offline",
                as_of="2026-09-07T00:00:00.000Z",
            )

    sender = RecordingSender()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(run_list=StubRunList()),
    )
    outcome = receive_update(context, _message(1200, LINKED_CHAT, "/status"))
    reply = outcome.replies[0]
    assert commands_module.REPLY_DELIVERY_UNKNOWN_SUFFIX in reply
    assert "đã gửi" not in reply
    assert "offline" in reply and "2026-09-07" in reply


# --------------------------------------------------------------------------------------
# R5-01 code boundary, and the wire contract
# --------------------------------------------------------------------------------------


def test_the_http_status_map_matches_the_openapi_responses(openapi) -> None:
    """Every status this module can return is one openapi declares for that path.

    The gap that is **not** covered is recorded rather than papered over:
    ``telegram.receive_update`` declares no 503, yet card §7 lists ``STORAGE_WRITE_FAILED``
    for the operation, so the webhook reports a storage refusal as ``INTERNAL`` (500) and the
    divergence is raised as ``CR-TC-TGAUTH-03``.
    """
    declared: dict[str, set[int]] = {}
    for item in openapi["paths"].values():
        for operation in item.values():
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId", "")
            if operation_id.startswith("telegram.") and operation_id != "telegram.send_payload":
                declared[operation_id] = {int(code) for code in operation["responses"]}

    assert 503 not in declared["telegram.receive_update"], (
        "openapi grew a 503 for the webhook; CR-TC-TGAUTH-03 can be closed and the INTERNAL "
        "mapping in ingress.HTTP_STATUS replaced"
    )
    for code, status in HTTP_STATUS.items():
        if code in (ErrorCode.STORAGE_WRITE_FAILED,):
            continue
        assert status in (
            declared["telegram.receive_update"]
            | declared["telegram.issue_link_code"]
            | declared["telegram.unlink"]
        ), code


def test_the_three_routes_are_mounted_and_no_internal_operation_is(engine) -> None:
    """``telegram.execute_command`` and ``telegram.consume_link_code`` are ``internal``.

    Exposing either would create an edge the registry does not grant and would put the B09
    exception on the open internet.
    """
    app = create_app()
    app.state.telegram_context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET
    )
    mounted = {
        getattr(route, "operation_id", None)
        for route in app.routes
        if getattr(route, "operation_id", None)
    }
    assert OperationId.TELEGRAM_RECEIVE_UPDATE.value in mounted
    assert OperationId.TELEGRAM_ISSUE_LINK_CODE.value in mounted
    assert OperationId.TELEGRAM_UNLINK.value in mounted
    assert OperationId.TELEGRAM_EXECUTE_COMMAND.value not in mounted
    assert OperationId.TELEGRAM_CONSUME_LINK_CODE.value not in mounted
    assert OperationId.TELEGRAM_SEND_PAYLOAD.value not in mounted


def test_the_owner_routes_refuse_without_a_session(engine) -> None:
    """``owner_session`` **AND** ``ownerCsrfToken`` in one requirement, so cookie alone fails.

    On the bare app there is no auth service, so the answer is ``UNAUTHORIZED`` -- default
    deny, and 401 rather than 500 (the same property ``CR-03`` asked of every card).
    """
    app = create_app()
    app.state.telegram_context = TelegramContext(
        engine=engine, owner_id=OWNER_ID, webhook_secret=WEBHOOK_SECRET
    )
    client = TestClient(app, base_url="https://testserver")

    created = client.post("/v1/telegram/link-codes", json={}, headers=WIRE_HEADERS)
    assert created.status_code == 401
    assert created.json()["code"] == ErrorCode.UNAUTHORIZED.value

    removed = client.request("DELETE", "/v1/telegram/link", json={}, headers=WIRE_HEADERS)
    assert removed.status_code == 401
    assert removed.json()["code"] == ErrorCode.UNAUTHORIZED.value
    assert _rows(engine, "SELECT COUNT(*) FROM telegram_link_code")[0][0] == 0


@pytest.mark.xfail(
    strict=True,
    run=True,
    reason=(
        "pending TC-scheduler-lease-claim (Phase 6): server.app.job.service does not exist, "
        "so run.list and run.run_now are exercised through the ports.yaml signature with a "
        "double. The end-to-end proof that a real needs_user run is not resumed is NOT_RUN. "
        "strict=True so the day that card lands this XPASSes loudly instead of staying a "
        "quiet green -- an xfail nobody notices going stale is how a NOT_RUN becomes a lie."
    ),
)
def test_run_now_against_the_real_job_service() -> None:
    import server.app.job.service  # noqa: F401


# --------------------------------------------------------------------------------------
# CMD-save against the real saved service (TC-saved-snapshot landed in this wave)
# --------------------------------------------------------------------------------------

WORK_ID = "01JW0RKD100000000000000000"
ANALYSIS_ID = "01JANA1YD10000000000000000"
SEED_AT = "2026-09-05T20:10:00.000Z"


def _analysis_payload() -> dict[str, Any]:
    """A minimal schema-valid ``summary`` payload, the shape W5B's own suite uses."""
    return {
        "schema_version": "0.1.0",
        "task_type": "summary",
        "result": {
            "content": "Nội dung tóm tắt.",
            "difference_from_existing": {
                "text": "Điểm khác so với cái đã có.",
                "comparator": {"kind": "unknown"},
            },
            "limitation_line": "Một dòng hạn chế.",
            "statements": [{"kind": "ai_inference", "text": "Suy luận."}],
        },
    }


def _seed_savable_work(engine: Engine) -> None:
    """One ``work`` with one ``valid`` summary analysis — the minimum ``save.create`` needs."""
    import json

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES (?, ?, '2505.05555', 'Một công trình ví dụ', 'partial', 'active', ?, 1,"
            " 'present', ?)",
            (WORK_ID, OWNER_ID, SEED_AT, SEED_AT),
        )
        connection.exec_driver_sql(
            "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
            " target_work_id, task_type, source_fingerprint, prompt_version, schema_version,"
            " generation_number, status, payload, payload_hash, evidence_level,"
            " provider_name, model_name, analyzed_at, accepted_from_attempt_id)"
            " VALUES (?, ?, '01JGEN00000000000000000001', 'work', ?, 'summary', 'fp-1',"
            " 'p-1', '0.1.0', 1, 'valid', ?, ?, 'abstract', 'anthropic', 'claude-opus-5',"
            " ?, '01JATT00000000000000000001')",
            (
                ANALYSIS_ID,
                OWNER_ID,
                WORK_ID,
                json.dumps(_analysis_payload(), ensure_ascii=False),
                "sha256:" + "1" * 64,
                SEED_AT,
            ),
        )


def _telegram_save_adapter(engine: Engine) -> Any:
    """``TC-saved-snapshot``'s own adapter — the wiring a deployment uses, not a local copy.

    Using W5B's `TelegramSaveAdapter` rather than a double written here is the whole point:
    it is the object that binds this card's `SaveCreatePort` to the real
    ``server.app.saved.service.create_save``, and a copy of it in this file would prove only
    that the copy works.
    """
    from server.app.saved.service import TelegramSaveAdapter

    return TelegramSaveAdapter(engine)


def test_save_from_chat_against_the_real_saved_service(engine) -> None:
    """``/save <target>`` from the linked chat, end to end into W5B's service.

    Real service, real ``TXN-save-target``, real database: two presses leave **one**
    ``saved_item`` and **one** ``saved_snapshot`` with no orphan, and both presses get an
    answer -- the plain-text half of ``REQ-D38`` / ``EDGE-03`` ("5 lần bấm ⇒ 1 bản ghi, 5 phản
    hồi"). The first reply is ``Đã lưu.``; the second is ``Mục này đã có trong Saved.``.

    **Where this stops, exactly.** The contract's ``CMD-save`` carries ``ii`` -- a
    ``report_item_id`` -- inside ``callback_data``. Two things are missing for that: the
    callback path itself (``CR-PC07-04``, still ``KC``) and the ``report_item`` table, which
    belongs to ``TC-report-coverage-publish-cas`` in Phase 4 and does not exist in this
    schema. So the argument carried here is the target reference the saved service already
    understands, and the step **not** proved is ``report_item_id → target`` resolution plus
    the ``rv``/``lg`` staleness checks that sit around it (``CR-TC-TGAUTH-06``).
    """
    _seed_savable_work(engine)
    adapter = _telegram_save_adapter(engine)
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(save_create=adapter),
    )

    first = receive_update(context, _message(1300, LINKED_CHAT, f"/save work:{WORK_ID}"))
    second = receive_update(context, _message(1301, LINKED_CHAT, f"/save work:{WORK_ID}"))

    assert first.command == CommandId.SAVE.value
    assert first.replies == (commands_module.REPLY_SAVED_NEW,)
    assert second.replies == (commands_module.REPLY_SAVED_ALREADY,)
    assert sender.send_message_count == 2, "both presses are answered (REQ-D38)"

    assert _rows(engine, "SELECT COUNT(*) FROM saved_item")[0][0] == 1
    assert _rows(engine, "SELECT COUNT(*) FROM saved_snapshot")[0][0] == 1
    assert (
        _rows(
            engine,
            "SELECT COUNT(*) FROM saved_snapshot AS ss WHERE NOT EXISTS "
            "(SELECT 1 FROM saved_item AS si WHERE si.saved_snapshot_id = ss.id)",
        )[0][0]
        == 0
    ), "a snapshot with no pointer means the two writes were not one transaction"
    channel = _rows(engine, "SELECT save_channel FROM saved_item")[0][0]
    assert channel == "telegram"


def test_the_adapter_forwards_a_bad_target_instead_of_parsing_it(engine) -> None:
    """The saved service owns the target grammar; the adapter does not second-guess it.

    A second parser here would be a second definition of a valid target, and the two would
    drift. The refusal that comes back is ``VALIDATION_ERROR`` from ``save.create`` itself.
    """
    from server.app.saved.service import SavedError

    adapter = _telegram_save_adapter(engine)
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=RecordingSender(),
        ports=CommandPorts(save_create=adapter),
    )
    with pytest.raises(SavedError) as raised:
        receive_update(context, _message(1310, LINKED_CHAT, "/save không-phải-target"))
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert _rows(engine, "SELECT COUNT(*) FROM saved_item")[0][0] == 0


def test_the_sender_returns_the_provider_message_id(engine) -> None:
    """``CR-TC-DELIVERY-09``: a send hands back the provider id it was given.

    ``MOD-delivery-service`` records that id in ``delivery_receipt``; a sender that returned
    nothing left "sent, id 4711" and "sent, unknown" indistinguishable, which is the very
    distinction ``ADR-0003`` refuses to blur. The ids surface on the outcome in send order.
    """
    sender = RecordingSender()
    context = TelegramContext(
        engine=engine,
        owner_id=OWNER_ID,
        webhook_secret=WEBHOOK_SECRET,
        sender=sender,
        ports=CommandPorts(),
    )
    first = receive_update(context, _message(1320, LINKED_CHAT, "không phải lệnh"))
    second = receive_update(context, _message(1321, LINKED_CHAT, "cũng không phải lệnh"))

    assert first.message_ids == ("rec-1",)
    assert second.message_ids == ("rec-2",)
    assert sender.message_ids == ["rec-1", "rec-2"]
    # A silent path returns no ids at all -- absence of a receipt, not an empty one.
    silent = receive_update(context, _message(1322, STRANGER_CHAT, "/status"))
    assert silent.message_ids == ()
    assert silent.replies == ()
