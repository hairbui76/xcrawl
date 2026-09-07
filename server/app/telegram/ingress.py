"""Webhook ingress: authenticate, deduplicate, and decide whether to be silent.

``contracts/telegram/commands.yaml`` §1 is this module, in order:

``ING-01``  the webhook secret token, compared **constant-time**; wrong or missing ⇒
            ``UNAUTHORIZED``, no content answered, one ``dropped_invalid`` audit line.
``ING-02``  ``chat_id`` and ``from.id`` in the payload are not identity until ING-01 passed:
            anyone who learns the webhook URL can post arbitrary JSON.
``ING-03``  only ``message`` and ``callback_query`` are accepted; every other update type is
            dropped silently.
``ING-04``  ``update_id`` is the replay key (``ux_telegram_update_id``); a repeat returns the
            first result and re-runs **no** side effect -- notably it sends nothing.
``ING-06``  updates older than ``telegram_update_max_age`` are dropped: a ``/run_now`` from
            a backlog replayed after an outage is not a statement of present intent.
``ING-07``  only the linked chat may command; knowing the chat id is not authority.
``ING-08``  an unlinked chat gets **absolute silence** -- not even "không có quyền", because
            a refusal confirms the bot exists at this address (REQ-S11.3-02, AC-18).

The single exception is B09, and it lives in :mod:`server.app.telegram.linking`.

Plain text only (``OD-20260908-09``)
------------------------------------
:class:`TelegramSender` sends ``sendMessage`` with ``text`` and nothing else. There is no
``parse_mode`` argument, no ``reply_markup`` argument and no ``answerCallbackQuery`` call
anywhere in this package, because three of the five formatting facts in
``contracts/telegram/delivery.md`` §3.4 are still ``KC`` (``CR-PC07-04``, card §10
``SG-01``). A ``callback_query`` from a linked chat is therefore logged ``dropped_invalid``
and answered with nothing: this system sends no buttons, so no callback it could have
produced exists, and the contract's ``EDGE-01`` reply is recorded ``NOT_RUN``.

Ordering of the write and the send
----------------------------------
The database work is one ``BEGIN…COMMIT`` (``session_scope``) and **every** outbound call
happens after it returns. SRC-PLAN §5.1 forbids a network call inside a SQLite transaction,
and the ordering is also what makes the oracle measurable: an unlinked chat produces zero
sender calls because the code path that would build a reply never runs, not because a send
was attempted and suppressed.
"""

from __future__ import annotations

import hmac
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError

from server.app.db import session_scope
from server.app.telegram.commands import (
    REPLY_COMMAND_REMINDER,
    REPLY_LINKED_CONFIRMATION,
    CommandPorts,
    CommandPortUnavailable,
    CommandResult,
    parse_command,
)
from server.app.telegram.commands import execute_command as _execute_command
from server.app.telegram.linking import (
    DEFAULT_LINKING_POLICY,
    ConsumeOutcome,
    LinkingPolicy,
    active_link,
    consume_link_code,
    format_timestamp,
    hash_chat_id,
    new_ulid,
)

#: ``contracts/http/openapi.yaml`` ``components.parameters.TelegramSecretHeader``.
TELEGRAM_SECRET_HEADER: Final[str] = "X-Telegram-Bot-Api-Secret-Token"

#: HTTP status per code, from the responses openapi declares on the three telegram paths.
#: ``telegram.receive_update`` declares 204/401/403/409/422/429/500 and **no** 503, so a
#: storage refusal on the webhook is reported as ``INTERNAL`` -- see ``CR-TC-TGAUTH-03``.
HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.UNAUTHORIZED_COMMAND: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}


class TelegramError(Exception):
    """A registered error code plus the safe envelope fields it must be reported with.

    Carries no chat id, no message text, no bot token and no webhook secret.
    ``contracts/errors.yaml`` ``UNAUTHORIZED_COMMAND.redaction_vi`` requires the raw chat id
    to stay out of logs entirely, so the exception that reaches a log formatter never holds
    one.
    """

    def __init__(
        self,
        code: ErrorCode,
        message_safe: str,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {message_safe}")
        self.code = code
        self.message_safe = message_safe
        self.details_safe: dict[str, Any] | None = (
            None if details_safe is None else dict(details_safe)
        )
        self.retry_after_ms = retry_after_ms

    @property
    def http_status(self) -> int:
        return HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The ``ErrorEnvelope`` of ``contracts/errors.yaml``."""
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe,
            "retry_after_ms": self.retry_after_ms,
        }


# --------------------------------------------------------------------------------------
# ING-01: the webhook secret
# --------------------------------------------------------------------------------------


def verify_webhook_secret(presented: str | None, expected: str | None) -> None:
    """``ING-01``. Constant-time comparison; anything but an exact match is ``UNAUTHORIZED``.

    :func:`hmac.compare_digest` rather than ``==``: a byte-by-byte comparison that returns
    early leaks the length of the matching prefix, and the secret is the only thing standing
    between the webhook URL and the command surface. ``contracts/ops/secrets.md`` §7 also
    says the hard-to-guess path is *not* authentication on its own.

    An **unconfigured** server refuses every update. That is the default-deny direction: a
    deployment that forgot to install the secret must accept nobody, not everybody.
    """
    if expected is None or presented is None:
        raise TelegramError(
            ErrorCode.UNAUTHORIZED,
            "Không có quyền thực hiện thao tác này.",
            details_safe={
                "operation_id": OperationId.TELEGRAM_RECEIVE_UPDATE.value,
                "required_auth_scope": "telegram_ingress_secret",
            },
        )
    if not hmac.compare_digest(presented, expected):
        raise TelegramError(
            ErrorCode.UNAUTHORIZED,
            "Không có quyền thực hiện thao tác này.",
            details_safe={
                "operation_id": OperationId.TELEGRAM_RECEIVE_UPDATE.value,
                "required_auth_scope": "telegram_ingress_secret",
            },
        )


# --------------------------------------------------------------------------------------
# ING-03: update shape
# --------------------------------------------------------------------------------------


class UpdateKind(str, Enum):
    """The two accepted kinds, plus everything else."""

    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"
    UNSUPPORTED = "unsupported"


class Disposition(str, Enum):
    """``telegram_update_log.disposition`` — the closed enum of ``entities.yaml``."""

    EXECUTED = "executed"
    DROPPED_UNLINKED = "dropped_unlinked"
    DROPPED_INVALID = "dropped_invalid"
    LINK_CODE_ATTEMPT = "link_code_attempt"


@dataclass(frozen=True)
class ParsedUpdate:
    """The three fields an update is reduced to before any decision is taken.

    Nothing else from the payload survives this step. ``entities.yaml``
    ``ENT-telegram-update-log.forbidden`` prohibits storing a stranger's message text, and
    the simplest way to keep that promise is for the text never to leave this object.
    """

    update_id: str
    kind: UpdateKind
    chat_id: str | None
    message_text: str
    sent_at: datetime | None


def classify_update(payload: Mapping[str, Any]) -> ParsedUpdate:
    """``ING-03``: recognise ``message`` and ``callback_query``; classify all else unsupported.

    :raises TelegramError: ``VALIDATION_ERROR`` when the body carries no ``update_id`` --
        that is not a Telegram update at all, so there is nothing to deduplicate on and the
        request is malformed rather than merely uninteresting.
    """
    raw_update_id = payload.get("update_id")
    if raw_update_id is None or isinstance(raw_update_id, bool):
        raise TelegramError(
            ErrorCode.VALIDATION_ERROR,
            "Dữ liệu gửi lên không hợp lệ.",
            details_safe={
                "operation_id": OperationId.TELEGRAM_RECEIVE_UPDATE.value,
                "field_path": "update_id",
                "violation_kind": "required_field_missing",
            },
        )
    update_id = str(raw_update_id)

    message = payload.get("message")
    if isinstance(message, dict):
        chat = message.get("chat")
        chat_id = str(chat.get("id")) if isinstance(chat, dict) and "id" in chat else None
        raw_text = message.get("text")
        sent = message.get("date")
        return ParsedUpdate(
            update_id=update_id,
            kind=UpdateKind.MESSAGE if isinstance(raw_text, str) else UpdateKind.UNSUPPORTED,
            chat_id=chat_id,
            message_text=raw_text if isinstance(raw_text, str) else "",
            sent_at=_from_unix(sent),
        )

    callback = payload.get("callback_query")
    if isinstance(callback, dict):
        callback_message = callback.get("message")
        chat = callback_message.get("chat") if isinstance(callback_message, dict) else None
        chat_id = str(chat.get("id")) if isinstance(chat, dict) and "id" in chat else None
        return ParsedUpdate(
            update_id=update_id,
            kind=UpdateKind.CALLBACK_QUERY,
            chat_id=chat_id,
            message_text="",
            sent_at=None,
        )

    # channel_post, inline_query, poll, edited_message, … -- ING-03 drops all of them.
    return ParsedUpdate(
        update_id=update_id,
        kind=UpdateKind.UNSUPPORTED,
        chat_id=None,
        message_text="",
        sent_at=None,
    )


def _from_unix(value: Any) -> datetime | None:
    """Telegram's ``date`` is Unix seconds. Anything else is treated as absent, not as now."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return datetime.fromtimestamp(value, tz=UTC)


# --------------------------------------------------------------------------------------
# Outbound
# --------------------------------------------------------------------------------------


class TelegramSender(Protocol):
    """The only way out of this package. Plain text, one chat, one string.

    The signature is the enforcement: there is no ``parse_mode`` parameter and no
    ``reply_markup`` parameter to pass, so the blocked formatting facts of ``CR-PC07-04``
    cannot be reached from any call site even by mistake.

    :returns: the provider's ``message_id`` for the message that was accepted, as a string.

    The return value exists for ``CR-TC-DELIVERY-09``: ``delivery_receipt`` records the
    provider id of a message that was observed to arrive, and a sender that returned nothing
    left ``MOD-delivery-service`` with no way to tell "sent, id 4711" from "sent, unknown".
    That is precisely the distinction ``ADR-0003`` refuses to blur, so the id is returned
    rather than logged. A send that does **not** produce an id raises instead of returning a
    placeholder: an invented id would be a receipt for a message nobody saw.
    """

    def send_message(self, *, chat_id: str, text: str) -> str: ...  # pragma: no cover


class RecordingSender:
    """A sender that records instead of sending. Used by tests; never by a deployment.

    Kept in the module it mirrors so the count the oracles are written against
    (``outbound_call_counts['telegram.sendMessage']``) is produced by the same seam
    production uses, rather than by a test-local stub of a different shape.

    The ids it hands back are deterministic (``rec-1``, ``rec-2``, …) so a test can assert
    *which* id came back from *which* call, and are visibly not Telegram ids so no test can
    pass by accidentally treating a recorded id as a real receipt.
    """

    #: Prefix that marks an id as recorded rather than provider-issued.
    ID_PREFIX: Final[str] = "rec-"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self.message_ids: list[str] = []

    def send_message(self, *, chat_id: str, text: str) -> str:
        self.calls.append((chat_id, text))
        message_id = f"{self.ID_PREFIX}{len(self.calls)}"
        self.message_ids.append(message_id)
        return message_id

    @property
    def send_message_count(self) -> int:
        return len(self.calls)


class HttpxTelegramSender:
    """``sendMessage`` over ``httpx`` (ADR-0011). Constructed only by a real deployment.

    No test builds one: there is no live Bot API call anywhere in this card's evidence, and
    ``E3`` stays ``NOT_RUN``. The bot token is held here and nowhere else -- it is not
    logged, not put in an error envelope and not returned to any caller
    (``contracts/ops/secrets.md`` §7).

    The request body is ``{"chat_id": …, "text": …}`` and nothing more: no ``parse_mode``,
    no ``reply_markup``, no ``entities``. Payloads longer than 4096 characters are split by
    the caller (:func:`server.app.telegram.commands.split_plain_text`) before they arrive.

    ``result.message_id`` is read out of the 200 response and returned. A 200 whose body does
    not carry one raises :class:`TelegramError` ``INTERNAL``: the caller asked for a receipt
    and there is none, and answering with an empty string would put an unusable value into
    ``delivery_receipt`` (``CR-TC-DELIVERY-09``).
    """

    #: The one host ``capabilities.yaml`` grants this actor (``network_scope``).
    BASE_URL: Final[str] = "https://api.telegram.org"

    def __init__(self, bot_token: str, *, timeout_seconds: float = 10.0) -> None:
        self._bot_token = bot_token
        self._timeout_seconds = timeout_seconds

    def send_message(self, *, chat_id: str, text: str) -> str:  # pragma: no cover - live path
        import httpx

        response = httpx.post(
            f"{self.BASE_URL}/bot{self._bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        result = body.get("result") if isinstance(body, dict) else None
        message_id = result.get("message_id") if isinstance(result, dict) else None
        if message_id is None:
            raise TelegramError(
                ErrorCode.INTERNAL,
                "Lỗi nội bộ. Yêu cầu chưa được xử lý.",
                details_safe=None,
            )
        return str(message_id)


# --------------------------------------------------------------------------------------
# Context and outcome
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TelegramContext:
    """Everything ``telegram.receive_update`` needs, injected rather than discovered.

    ``webhook_secret`` defaults to ``None`` so an unconfigured deployment denies every
    update instead of accepting them (see :func:`verify_webhook_secret`). ``sender``
    defaults to ``None`` for the same reason in the other direction: with no sender wired,
    the adapter can still receive, log and link, and it simply produces no outbound call --
    which is the safe failure, not a crash mid-transaction.
    """

    engine: Engine
    owner_id: str
    webhook_secret: str | None = None
    policy: LinkingPolicy = DEFAULT_LINKING_POLICY
    sender: TelegramSender | None = None
    ports: CommandPorts = field(default_factory=CommandPorts)
    storage_guard: Any | None = None


@dataclass(frozen=True)
class IngressOutcome:
    """What one update did, in the terms the fixtures assert.

    :param replies: the plain-text messages actually sent, in order. Empty for every silent
        path -- and *empty* is the oracle: ``len(outcome.replies) == 0`` and the sender's own
        call count agree only if nothing was attempted.
    :param audit_code: the ``contracts/errors.yaml`` code this refusal is recorded under, or
        ``None`` when the update was not a refusal. It is an **audit** value: it never
        reaches the chat and never becomes an HTTP status on the webhook, which always
        answers 204. Carrying it explicitly is what makes ruling R5-01 measurable -- card
        §10 ``SG-DENY`` makes the wrong code a FAIL in its own right, so the code has to be
        observable rather than implied by a log line.
    """

    disposition: Disposition
    replies: tuple[str, ...] = ()
    command: str | None = None
    linked: bool = False
    replayed: bool = False
    consume_outcome: ConsumeOutcome | None = None
    audit_code: ErrorCode | None = None
    message_ids: tuple[str, ...] = ()


# --------------------------------------------------------------------------------------
# telegram.receive_update
# --------------------------------------------------------------------------------------


def receive_update(
    context: TelegramContext, payload: Mapping[str, Any], *, now: datetime | None = None
) -> IngressOutcome:
    """``telegram.receive_update`` — the whole ingress pipeline.

    Commit point: the single ``session_scope`` block below. Every row this update writes --
    the ``telegram_update_log`` line, any ``telegram_link_attempt`` row, the consumed code
    and the new link -- commits together or not at all, so a crash cannot leave a code spent
    with no link to show for it.

    Outbound calls happen strictly **after** that commit and only from
    :attr:`IngressOutcome.replies`.

    :param now: server clock, injectable so a fixture's timestamps drive expiry and age.
    """
    moment = now or datetime.now(tz=UTC)
    parsed = classify_update(payload)

    if not _storage_writable(context):
        # EDGE-06. Reads still work while writes are blocked, so a linked chat still gets an
        # answer; nothing at all is written, including the audit line, and that limitation is
        # reported rather than papered over (CR-TC-TGAUTH-03).
        return _handle_write_blocked(context, parsed, moment)

    try:
        with session_scope(context.engine) as connection:
            previous = _replayed_disposition(connection, context.owner_id, parsed.update_id)
            if previous is not None:
                # ING-04: same result, no side effect -- in particular, no second reply.
                return IngressOutcome(disposition=previous, replayed=True)
            outcome = _dispatch(connection, context, parsed, moment)
            _log_update(connection, context, parsed, outcome, moment)
    except IntegrityError:
        # Two copies of one update in flight at once: the SELECT above missed the other
        # copy, `ux_telegram_update_id` did not. The transaction rolled back whole, so this
        # copy applied nothing, and the reply belongs to the copy that won -- ING-04 again,
        # arrived at through the index instead of through the read.
        replay = _replayed_disposition_committed(context, parsed.update_id)
        if replay is None:
            raise
        return IngressOutcome(disposition=replay, replayed=True)

    message_ids = _send(context, parsed.chat_id, outcome.replies)
    return replace(outcome, message_ids=message_ids)


def _storage_writable(context: TelegramContext) -> bool:
    """Whether the store will accept a write, asked **before** the transaction opens.

    ``server.app.storage.guard.StorageGuard.assert_writable`` raises; a boolean is what the
    branch here needs, and asking first is rule 1 of the guard's own call contract.
    """
    guard = context.storage_guard
    if guard is None:
        return True
    try:
        guard.assert_writable(OperationId.TELEGRAM_RECEIVE_UPDATE)
    except Exception:
        return False
    return True


def _handle_write_blocked(
    context: TelegramContext, parsed: ParsedUpdate, now: datetime
) -> IngressOutcome:
    """``EDGE-06``: read-only commands still answer; mutations say plainly they were not taken.

    An unlinked chat stays silent here as everywhere else -- the storage state changes what a
    linked owner is told, never whether a stranger is answered.
    """
    del now
    if parsed.kind is not UpdateKind.MESSAGE or parsed.chat_id is None:
        return IngressOutcome(disposition=Disposition.DROPPED_INVALID)
    with context.engine.connect() as connection:
        link = active_link(connection, owner_id=context.owner_id)
    if link is None or link.chat_id != parsed.chat_id:
        return IngressOutcome(disposition=Disposition.DROPPED_UNLINKED)
    command = parse_command(parsed.message_text)
    if command is None:
        replies: tuple[str, ...] = (REPLY_COMMAND_REMINDER,)
        result_disposition = Disposition.DROPPED_INVALID
        command_id: str | None = None
    else:
        result = _execute_command(
            command,
            owner_id=context.owner_id,
            request_id=parsed.update_id,
            ports=context.ports,
            storage_writable=False,
        )
        replies = result.replies
        result_disposition = Disposition.EXECUTED
        command_id = result.command.value
    message_ids = _send(context, parsed.chat_id, replies)
    return IngressOutcome(
        disposition=result_disposition,
        replies=replies,
        command=command_id,
        linked=True,
        message_ids=message_ids,
    )


def _replayed_disposition(
    connection: Connection, owner_id: str, update_id: str
) -> Disposition | None:
    """``ING-04``: has this ``update_id`` been seen? Returns the first result's disposition."""
    row = connection.execute(
        text(
            "SELECT disposition FROM telegram_update_log "
            "WHERE owner_id = :owner_id AND provider_update_id = :update_id"
        ),
        {"owner_id": owner_id, "update_id": update_id},
    ).first()
    return None if row is None else Disposition(str(row[0]))


def _replayed_disposition_committed(context: TelegramContext, update_id: str) -> Disposition | None:
    """The same question as :func:`_replayed_disposition`, on a fresh connection.

    Needed after a rollback: the connection the failed transaction used cannot be trusted to
    read committed state any more.
    """
    with context.engine.connect() as connection:
        return _replayed_disposition(connection, context.owner_id, update_id)


def _dispatch(
    connection: Connection, context: TelegramContext, parsed: ParsedUpdate, now: datetime
) -> IngressOutcome:
    """Decide what this update does, having authenticated it and found it new."""
    if parsed.kind is UpdateKind.UNSUPPORTED:
        return IngressOutcome(disposition=Disposition.DROPPED_INVALID)

    if _too_old(parsed, now, context.policy):
        # ING-06: a `/run_now` replayed from yesterday's backlog is not present intent.
        return IngressOutcome(disposition=Disposition.DROPPED_INVALID)

    if parsed.chat_id is None:
        return IngressOutcome(disposition=Disposition.DROPPED_INVALID)

    link = active_link(connection, owner_id=context.owner_id)
    linked = link is not None and link.chat_id == parsed.chat_id

    if not linked:
        return _unlinked(connection, context, parsed, now)

    if parsed.kind is UpdateKind.CALLBACK_QUERY:
        # No button this system sends exists (plain-text scope), so no callback it produced
        # can arrive. Logged and dropped; the contract's empty `answerCallbackQuery` reply
        # and the five-step validation of `CMD-save` are NOT_RUN (BLOCKED_DEPENDENCY
        # CR-PC07-04) rather than implemented against an unresolved callback_data limit.
        return IngressOutcome(
            disposition=Disposition.DROPPED_INVALID,
            linked=True,
            audit_code=ErrorCode.VALIDATION_ERROR,
        )

    return _linked_message(context, parsed)


def _too_old(parsed: ParsedUpdate, now: datetime, policy: LinkingPolicy) -> bool:
    """``ING-06``. An update with no ``date`` is **not** treated as old; it is simply unaged."""
    if parsed.sent_at is None:
        return False
    return (now - parsed.sent_at).total_seconds() > policy.update_max_age_seconds


def _unlinked(
    connection: Connection, context: TelegramContext, parsed: ParsedUpdate, now: datetime
) -> IngressOutcome:
    """``ING-08`` plus the one exception, ``B09``.

    Everything from an unlinked chat is silent. A message whose whole text is a link code is
    the sole path that may compare anything against stored state, and only a *correct*,
    unexpired, unconsumed code produces the single confirmation reply.
    """
    if parsed.kind is not UpdateKind.MESSAGE:
        return IngressOutcome(
            disposition=Disposition.DROPPED_UNLINKED,
            audit_code=ErrorCode.UNAUTHORIZED_COMMAND,
        )

    result = consume_link_code(
        connection,
        owner_id=context.owner_id,
        chat_id=parsed.chat_id or "",
        message_text=parsed.message_text,
        now=now,
        policy=context.policy,
    )
    if result.outcome is ConsumeOutcome.NO_FORMAT_MATCH:
        # No lookup was performed and no `telegram_link_attempt` row was written -- fixture
        # (i) after_event_1 pins both counts at zero.
        return IngressOutcome(
            disposition=Disposition.DROPPED_UNLINKED,
            consume_outcome=result.outcome,
            audit_code=ErrorCode.UNAUTHORIZED_COMMAND,
        )
    if result.outcome is not ConsumeOutcome.LINKED:
        return IngressOutcome(
            disposition=Disposition.LINK_CODE_ATTEMPT,
            consume_outcome=result.outcome,
            audit_code=ErrorCode.UNAUTHORIZED_COMMAND,
        )
    return IngressOutcome(
        disposition=Disposition.LINK_CODE_ATTEMPT,
        replies=(REPLY_LINKED_CONFIRMATION,),
        linked=True,
        consume_outcome=result.outcome,
    )


def _linked_message(context: TelegramContext, parsed: ParsedUpdate) -> IngressOutcome:
    """A text message from the linked chat: allowlist, or the three-command reminder.

    ``ING-09``: a string that looks like a configuration command is refused because it is not
    in the allowlist, not because it matched a blocklist. There is no tag path and no
    settings path from a chat at all -- ``FE-30`` and ``FE-31`` -- and the absence is
    structural: this module imports neither service.
    """
    command = parse_command(parsed.message_text)
    if command is None:
        return IngressOutcome(
            disposition=Disposition.DROPPED_INVALID,
            replies=(REPLY_COMMAND_REMINDER,),
            linked=True,
            audit_code=ErrorCode.UNAUTHORIZED_COMMAND,
        )
    result: CommandResult = _execute_command(
        command,
        owner_id=context.owner_id,
        request_id=parsed.update_id,
        ports=context.ports,
        storage_writable=True,
    )
    return IngressOutcome(
        disposition=Disposition.EXECUTED,
        replies=result.replies,
        command=result.command.value,
        linked=True,
    )


def _log_update(
    connection: Connection,
    context: TelegramContext,
    parsed: ParsedUpdate,
    outcome: IngressOutcome,
    now: datetime,
) -> None:
    """One ``telegram_update_log`` row per update, including the silent ones.

    The silent rows are the point: ``REQ-AC18`` is proved by showing the update was received
    **and** that nothing followed it, and a log that only recorded the interesting updates
    could not show the second half. ``chat_id_hash`` is a hash, never the raw id; the message
    text is not stored at all.
    """
    connection.execute(
        text(
            "INSERT INTO telegram_update_log "
            "(id, owner_id, provider_update_id, received_at, chat_id_hash, disposition, "
            " command) VALUES "
            "(:id, :owner_id, :update_id, :received_at, :chat_id_hash, :disposition, :command)"
        ),
        {
            "id": new_ulid(),
            "owner_id": context.owner_id,
            "update_id": parsed.update_id,
            "received_at": format_timestamp(now),
            "chat_id_hash": hash_chat_id(parsed.chat_id or ""),
            "disposition": outcome.disposition.value,
            "command": outcome.command,
        },
    )


def _send(
    context: TelegramContext, chat_id: str | None, replies: tuple[str, ...]
) -> tuple[str, ...]:
    """Deliver the replies, after the commit. Nothing to send is the common case.

    :returns: the provider ``message_id`` of each message accepted, in order -- empty when
        nothing was sent. The tuple is the caller's evidence of *what actually left*, which is
        a different fact from what it intended to send, and ``CR-TC-DELIVERY-09`` needs the
        first one.
    """
    if not replies or chat_id is None or context.sender is None:
        return ()
    return tuple(context.sender.send_message(chat_id=chat_id, text=reply) for reply in replies)


__all__ = [
    "TELEGRAM_SECRET_HEADER",
    "CommandPortUnavailable",
    "Disposition",
    "HttpxTelegramSender",
    "IngressOutcome",
    "ParsedUpdate",
    "RecordingSender",
    "TelegramContext",
    "TelegramError",
    "TelegramSender",
    "UpdateKind",
    "classify_update",
    "receive_update",
    "verify_webhook_secret",
]
