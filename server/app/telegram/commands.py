"""The closed allowlist of three commands, and the ports they are allowed to reach.

``contracts/telegram/commands.yaml`` §3: *"Đúng BA lệnh. Không có lệnh thứ tư (AMD-B10)."*
The allowlist below is that sentence as data. It is an **allowlist, not a blocklist**
(ING-09): a string from a linked chat that is not one of the three is refused because it is
not in the list, so no new command can appear by being forgotten in a filter.

Scope of this file under the Phase 5 plain-text decision (``OD-20260908-09``)
----------------------------------------------------------------------------
Three of the five Telegram formatting facts are still ``KC`` in
``contracts/telegram/delivery.md`` §3.4 -- ``callback_data`` length, the parse-mode escape
table, and buttons per row/keyboard -- and they are ``BLOCKED_DEPENDENCY`` under
``CR-PC07-04`` (card §10 ``SG-01``). This module therefore:

* sends **plain text only**: no ``parse_mode``, no ``reply_markup``, no inline keyboard;
* recognises ``CMD-save`` as a **typed** command, not as a callback button;
* implements **no** ``callback_data`` parser. The contract's five-step callback validation
  (``§3 → CMD-save → validation_order``) and fixture ``f-stale-callback-no-save`` cover a
  path this scope cannot build against a guessed 64-byte limit, so they are reported
  ``NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`` rather than approximated.

The typed trigger for ``CMD-save`` (``/save <target>``) is the adapter-level mapping the
contract already anticipates for ``CMD-run-now`` (*"và biến thể ngôn ngữ tự nhiên được ánh xạ
ở tầng adapter"*). It is recorded as ``CR-TC-TGAUTH-02`` so the Owner can confirm or replace
it when the callback path is unblocked; it changes no contract and adds no command. The
argument it carries is, in this scope, the target reference ``save.create`` already
understands rather than the contract's ``report_item_id``: resolving one needs both the
blocked callback and the ``report_item`` table of Phase 4 -- see :class:`SaveCreatePort` and
``CR-TC-TGAUTH-06``.

What this module must never do
------------------------------
``run.resume`` is not reachable from here. ``contracts/modules.yaml`` ``FE-33`` forbids the
edge ``MOD-telegram-adapter → MOD-job-service`` scoped to ``run.resume``, and
``capabilities.yaml`` ``DC-TGC-01`` prices a fourth command at ``UNAUTHORIZED_COMMAND``.
:func:`assert_no_resume_path` asserts the absence structurally rather than by review.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

# --------------------------------------------------------------------------------------
# The allowlist
# --------------------------------------------------------------------------------------


class CommandId(str, Enum):
    """``contracts/telegram/commands.yaml`` §3 ``commands.list[].id``, verbatim."""

    SAVE = "CMD-save"
    RUN_NOW = "CMD-run-now"
    STATUS = "CMD-status"


#: Exactly three. A fourth member of this set is a contract change, not a code change.
ALLOWED_COMMANDS: Final[frozenset[CommandId]] = frozenset(
    {CommandId.SAVE, CommandId.RUN_NOW, CommandId.STATUS}
)

#: The operation each command is permitted to call -- ``commands.yaml`` ``operation_id``.
#: Nothing else in this package may call an operation on behalf of a chat.
COMMAND_OPERATION: Final[dict[CommandId, OperationId]] = {
    CommandId.STATUS: OperationId.RUN_LIST,
    CommandId.RUN_NOW: OperationId.RUN_RUN_NOW,
    CommandId.SAVE: OperationId.SAVE_CREATE,
}

#: Typed triggers. ``/status`` and ``/run_now`` are the contract's own strings; ``/save`` is
#: the plain-text stand-in for the blocked callback button (CR-TC-TGAUTH-02).
TRIGGERS: Final[dict[str, CommandId]] = {
    "/status": CommandId.STATUS,
    "/run_now": CommandId.RUN_NOW,
    "/save": CommandId.SAVE,
}

#: ``contracts/telegram/delivery.md`` §3.4, ``DOCS_derived`` 2026-09-08: 1..4096 characters
#: for ``sendMessage.text``. Counted on the **raw** string, per §3.5's locked rule -- the
#: counting semantics after entity parsing have no source, and raw ≤ 4096 implies parsed
#: ≤ 4096 under either reading.
MAX_MESSAGE_CHARS: Final[int] = 4096

#: Reply text, verbatim from ``commands.yaml`` ``reply_templates_vi``. Kept as data so the
#: contract test can compare them with the contract rather than trusting the prose here.
REPLY_LINKED_CONFIRMATION: Final[str] = (
    "Đã liên kết. Ba lệnh khả dụng: /status, /run_now, /save. "
    "Hủy liên kết là hành động trong ứng dụng."
)
REPLY_COMMAND_REMINDER: Final[str] = "Ba lệnh khả dụng: /status, /run_now, /save."
REPLY_RUN_NOW_QUEUED: Final[str] = "Đã xếp hàng một đợt chạy."
REPLY_RUN_NOW_ALREADY_RUNNING: Final[str] = "Đang có một đợt chạy. Trạng thái: {status_label}."
REPLY_RUN_NOW_NEEDS_USER: Final[str] = (
    "Đợt đang chờ xác minh trên máy cá nhân. "
    "Mở ứng dụng, vào Runs và bấm Tiếp tục sau khi xử lý xong."
)
REPLY_STATUS_NO_MATCHING_CONTENT: Final[str] = (
    "Đợt gần nhất: không có nội dung phù hợp " "(đã thu thập xong, không bài nào khớp tag)."
)
REPLY_STATUS_STOPPED_EARLY: Final[str] = "Đợt gần nhất: dừng sớm — {stop_reason_vi}."
REPLY_STATUS_RUN_FAILED: Final[str] = "Đợt gần nhất: thất bại — {error_summary_safe}."
REPLY_DELIVERY_UNKNOWN_SUFFIX: Final[str] = (
    "Lần gửi gần nhất chưa xác định; mở ứng dụng để quyết định."
)
REPLY_SAVED_NEW: Final[str] = "Đã lưu."
REPLY_SAVED_ALREADY: Final[str] = "Mục này đã có trong Saved."
REPLY_STORAGE_WRITE_BLOCKED: Final[str] = (
    "Hệ thống hiện không ghi được dữ liệu, nên chưa nhận yêu cầu này. Thử lại sau."
)

#: The phrase ``ST-02`` forbids in a ``/status`` reply. Asserted, not merely avoided.
FORBIDDEN_STATUS_PHRASE: Final[str] = "Không có nghiên cứu mới"


def assert_no_resume_path() -> None:
    """``FE-33``: no command, and no trigger, reaches ``run.resume``.

    Raises :class:`AssertionError` at import time of the test that calls it. Written as a
    function rather than a comment because "there is no fourth command" is exactly the kind
    of claim that decays silently.
    """
    assert OperationId.RUN_RESUME not in COMMAND_OPERATION.values()
    assert set(COMMAND_OPERATION) == ALLOWED_COMMANDS
    assert set(TRIGGERS.values()) == ALLOWED_COMMANDS


# --------------------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedCommand:
    """One recognised command and its single optional argument."""

    command: CommandId
    argument: str | None = None


def parse_command(message_text: str) -> ParsedCommand | None:
    """``None`` for anything that is not one of the three.

    ``None`` is not an error and not a refusal on its own: what happens next depends on
    whether the chat is linked. An unlinked chat gets silence (ING-08); a linked one gets
    the three-command reminder (``silent_drop_summary``, ING-09). Deciding that here would
    put an authorisation question in a parser.
    """
    stripped = message_text.strip()
    if not stripped.startswith("/"):
        return None
    head, _, rest = stripped.partition(" ")
    # Telegram appends `@botname` to commands in groups; the trailing part is not an argument.
    head = head.split("@", 1)[0]
    command = TRIGGERS.get(head)
    if command is None:
        return None
    argument = rest.strip() or None
    return ParsedCommand(command=command, argument=argument)


def split_plain_text(text: str, *, limit: int = MAX_MESSAGE_CHARS) -> tuple[str, ...]:
    """Slice a plain-text reply at the 4096-character ceiling, counting the raw string.

    No escaping and no parse mode are involved, so there is nothing to keep balanced across
    a cut. Splitting on the last newline or space before the limit keeps words intact; a
    single run longer than the limit is cut at the limit rather than truncated away, because
    dropping text silently is worse than an awkward break.
    """
    if len(text) <= limit:
        return (text,)
    parts: list[str] = []
    rest = text
    while len(rest) > limit:
        window = rest[:limit]
        cut = max(window.rfind("\n"), window.rfind(" "))
        if cut <= 0:
            cut = limit
        parts.append(rest[:cut].rstrip())
        rest = rest[cut:].lstrip()
    if rest:
        parts.append(rest)
    return tuple(parts)


# --------------------------------------------------------------------------------------
# Ports -- the three operations this module consumes (card §4)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class RunSnapshot:
    """What ``run.list`` returns to a Telegram caller, reduced to what a reply needs.

    ``contracts/ports.yaml`` ``run.list``: *"với caller Telegram chỉ lấy N run gần nhất"*.
    The three ``REQ-AC15`` states are carried as separate fields because ``ST-02`` requires
    three **distinguishable** sentences; collapsing them into one status string here would
    make that impossible downstream.
    """

    run_id: str | None
    status: str | None
    outcome: str | None = None
    stop_reason_vi: str | None = None
    error_summary_safe: str | None = None
    status_label: str | None = None
    delivery_unknown: bool = False
    collector_state: str | None = None
    as_of: str | None = None


class RunListPort(Protocol):
    """``run.list`` — ``mutation: false``. ``ST-01``: absolutely read-only."""

    def list_runs(self, *, owner_id: str) -> RunSnapshot: ...  # pragma: no cover - protocol


@dataclass(frozen=True)
class RunNowResult:
    """``run.run_now``: queued, or the non-terminal run that already exists (``RN-02``)."""

    run_id: str
    queued: bool
    blocked_needs_user: bool = False
    status_label: str | None = None


class RunNowPort(Protocol):
    """``run.run_now``. ``RN-01``: the port itself must refuse to pass a ``needs_user`` run.

    The guard lives on both sides on purpose. The adapter refuses to *ask* when it can see
    the run is blocked, and the job service refuses to *act* if asked anyway; either one
    alone would be a single point of failure for ``AMD-B10``.
    """

    def run_now(self, *, owner_id: str, request_id: str) -> RunNowResult: ...  # pragma: no cover


@dataclass(frozen=True)
class SaveResult:
    """``save.create``: ``created`` or ``already_saved`` (``ports.yaml`` response summary)."""

    saved_item_id: str
    already_saved: bool


class SaveCreatePort(Protocol):
    """``save.create`` with ``save_channel = 'telegram'`` (``TC-saved-snapshot``).

    ``report_item_id`` keeps the contract's name for the field ``CMD-save`` carries (``ii``),
    and the chat argument is passed through it **verbatim** -- this port parses nothing.

    In the plain-text scope the token in it is a *target* reference (``work:<ulid>`` /
    ``post:<ulid>``), not a report item id, and that is a limitation rather than a design:
    the contract carries ``ii`` inside ``callback_data`` (blocked, ``CR-PC07-04``), and
    resolving one to a target needs the ``report_item`` table, which belongs to
    ``TC-report-coverage-publish-cas`` in Phase 4 and does not exist yet.
    ``TC-saved-snapshot``'s ``TelegramSaveAdapter`` reads the argument exactly this way and
    reached the same conclusion independently (its ``CR-TC-SAVED-07``, this card's
    ``CR-TC-TGAUTH-06``); when ``report_item`` lands, that adapter is the one place that
    changes and this signature does not.
    """

    def create_save(
        self, *, owner_id: str, report_item_id: str, idempotency_key: str
    ) -> SaveResult: ...  # pragma: no cover - protocol declaration


class CommandPortUnavailable(Exception):
    """A port the command needs is not wired into this deployment.

    Surfaces as ``INTERNAL``, never as a refusal to the chat and never as a fabricated
    answer: a ``/status`` that invented "everything is fine" because the job service was
    missing would be the exact conversion of *unknown* into *good* that ``I13`` forbids.
    """


# --------------------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CommandPorts:
    """The three ports, each optional so a partially wired deployment fails loudly."""

    run_list: RunListPort | None = None
    run_now: RunNowPort | None = None
    save_create: SaveCreatePort | None = None


@dataclass(frozen=True)
class CommandResult:
    """The plain-text replies a command produced, and whether it mutated anything.

    ``replies`` is a tuple because the 4096 rule can turn one logical answer into several
    ``sendMessage`` calls. It is **never** accompanied by markup: the object carries no
    ``parse_mode`` and no ``reply_markup`` field, so a sender cannot be handed one.
    """

    command: CommandId
    replies: tuple[str, ...]
    mutated: bool = False
    details: dict[str, Any] | None = None


def execute_command(
    parsed: ParsedCommand,
    *,
    owner_id: str,
    request_id: str,
    ports: CommandPorts,
    storage_writable: bool = True,
) -> CommandResult:
    """``telegram.execute_command`` — dispatch one allowlisted command.

    :param storage_writable: ``EDGE-06``. A read-only command still answers while the store
        refuses writes; a mutating one says plainly that nothing was accepted rather than
        implying it was received.
    :raises CommandPortUnavailable: when the port this command needs is not installed.
    """
    if parsed.command not in ALLOWED_COMMANDS:  # pragma: no cover - unreachable by parser
        raise ValueError(f"{parsed.command} is not in the allowlist")

    if parsed.command is CommandId.STATUS:
        return _status(owner_id=owner_id, ports=ports)
    if not storage_writable:
        # UI-02/UI-03, SRC-PLAN §8.4: never acknowledge a mutation the store did not take.
        return CommandResult(
            command=parsed.command,
            replies=(REPLY_STORAGE_WRITE_BLOCKED,),
            mutated=False,
            details={"error_code": ErrorCode.STORAGE_WRITE_FAILED.value},
        )
    if parsed.command is CommandId.RUN_NOW:
        return _run_now(owner_id=owner_id, request_id=request_id, ports=ports)
    return _save(parsed, owner_id=owner_id, request_id=request_id, ports=ports)


def _status(*, owner_id: str, ports: CommandPorts) -> CommandResult:
    """``CMD-status`` → ``run.list``. Read-only; ``ST-01`` allows no mutation at all."""
    if ports.run_list is None:
        raise CommandPortUnavailable("run.list is not wired (pending TC-scheduler-lease-claim)")
    snapshot = ports.run_list.list_runs(owner_id=owner_id)
    reply = _render_status(snapshot)
    return CommandResult(command=CommandId.STATUS, replies=split_plain_text(reply), mutated=False)


def _render_status(snapshot: RunSnapshot) -> str:
    """The three ``REQ-AC15`` states as three different sentences (``ST-02``…``ST-04``).

    Delivery is a separate sentence from the run (``ST-03``, ``I13``): an ``unknown`` send
    must not be reported as "đã gửi", and the two facts are independent, so they are two
    lines rather than one merged verdict.
    """
    lines: list[str] = []
    if snapshot.status is None:
        lines.append("Chưa có đợt chạy nào.")
    elif snapshot.status == "failed":
        lines.append(
            REPLY_STATUS_RUN_FAILED.format(
                error_summary_safe=snapshot.error_summary_safe or "không rõ nguyên nhân"
            )
        )
    elif snapshot.stop_reason_vi:
        lines.append(REPLY_STATUS_STOPPED_EARLY.format(stop_reason_vi=snapshot.stop_reason_vi))
    elif snapshot.outcome == "empty":
        lines.append(REPLY_STATUS_NO_MATCHING_CONTENT)
    else:
        lines.append(f"Đợt gần nhất: {snapshot.status_label or snapshot.status}.")
    if snapshot.delivery_unknown:
        lines.append(REPLY_DELIVERY_UNKNOWN_SUFFIX)
    if snapshot.collector_state is not None:
        # ST-04: collector online/offline/unknown plus `as_of` (REQ-D11, UI-01).
        as_of = f" (tính đến {snapshot.as_of})" if snapshot.as_of else ""
        lines.append(f"Máy thu thập: {snapshot.collector_state}{as_of}.")
    return "\n".join(lines)


def _run_now(*, owner_id: str, request_id: str, ports: CommandPorts) -> CommandResult:
    """``CMD-run-now`` → ``run.run_now``, with ``RN-01`` in front of it."""
    if ports.run_now is None:
        raise CommandPortUnavailable("run.run_now is not wired (pending TC-scheduler-lease-claim)")
    result = ports.run_now.run_now(owner_id=owner_id, request_id=request_id)
    if result.blocked_needs_user:
        # RN-01: not a resume, not a second run. One reply, pointing into the app.
        return CommandResult(
            command=CommandId.RUN_NOW,
            replies=(REPLY_RUN_NOW_NEEDS_USER,),
            mutated=False,
            details={"run_id": result.run_id},
        )
    if not result.queued:
        return CommandResult(
            command=CommandId.RUN_NOW,
            replies=(
                REPLY_RUN_NOW_ALREADY_RUNNING.format(
                    status_label=result.status_label or "đang chạy"
                ),
            ),
            mutated=False,
            details={"run_id": result.run_id},
        )
    return CommandResult(
        command=CommandId.RUN_NOW,
        replies=(REPLY_RUN_NOW_QUEUED,),
        mutated=True,
        details={"run_id": result.run_id},
    )


def _save(
    parsed: ParsedCommand, *, owner_id: str, request_id: str, ports: CommandPorts
) -> CommandResult:
    """``CMD-save`` → ``save.create``, plain-text form.

    Five presses produce one ``saved_item`` and five replies (``REQ-D38``, ``EDGE-03``): the
    idempotency key is scoped to the target rather than to the press, so the second call reads
    the row the first committed and still answers. The ``already_saved`` reply is the
    contract's, not an error.

    The argument is forwarded verbatim -- see :class:`SaveCreatePort` on what it actually
    carries in this scope. No shape is parsed here: the saved service owns the target grammar
    and answers ``VALIDATION_ERROR`` for anything else, and a second parser in the adapter
    would be a second, drifting definition of a valid target.

    The idempotency key is scoped to the **target**, not to the press
    (``ports.yaml save.create``: ``owner_id + target_ref``), so five presses carry one key and
    the 2nd..5th read the row the first committed -- "5 lần bấm ⇒ 1 bản ghi, 5 phản hồi".
    """
    if ports.save_create is None:
        raise CommandPortUnavailable("save.create is not wired (pending TC-saved-snapshot)")
    if not parsed.argument:
        return CommandResult(
            command=CommandId.SAVE,
            replies=("Cần mục để lưu. Ví dụ: /save work:<ID>.",),
            mutated=False,
            details={"error_code": ErrorCode.VALIDATION_ERROR.value},
        )
    result = ports.save_create.create_save(
        owner_id=owner_id,
        report_item_id=parsed.argument,
        idempotency_key=f"tg-cmd:{parsed.argument}",
    )
    reply = REPLY_SAVED_ALREADY if result.already_saved else REPLY_SAVED_NEW
    return CommandResult(
        command=CommandId.SAVE,
        replies=(reply,),
        mutated=not result.already_saved,
        details={"saved_item_id": result.saved_item_id},
    )
