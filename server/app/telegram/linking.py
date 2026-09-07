"""Link codes and link generations — the B09 exception, and nothing wider than it.

``contracts/telegram/commands.yaml`` § linking is the whole of this module's mandate. Two
sentences from it decide most of the code below:

* *"Một tin nhắn từ chat CHƯA liên kết được xử lý CHỈ KHI toàn bộ nội dung (sau trim) khớp
  regex."* — the format test is the gate, and it runs **before** any database lookup. A
  string that does not match is never compared against a stored code, so the bot is not a
  code-guessing oracle for arbitrary text.
* *"khớp ⇒ liên kết thành công + phản hồi xác nhận; không khớp ⇒ bỏ im lặng."* — there is
  exactly one reply an unlinked chat can ever receive, and it is the confirmation of a
  **correct** code. Wrong, expired, already-used and rate-limited all end in silence, and
  they are indistinguishable from outside.

Why the four outcomes are still recorded separately
---------------------------------------------------
``telegram_link_attempt.outcome`` distinguishes ``format_match_code_invalid`` from
``…_expired`` and ``…_consumed`` even though all three look identical to the sender. The
row is for the owner's own forensics and for the rate-limit counter; the distinction never
leaves the database. Keeping the counter honest is why the row is written even in the
silent branches.

What is *not* written
---------------------
A message from an unlinked chat that does not match the code format writes **no**
``telegram_link_attempt`` row. ``contracts/data/entities.yaml`` ``ENT-telegram-link-attempt``
``forbidden`` says why: a row per stranger message would turn the counter table into a log
of everyone who has ever messaged the bot. The raw ``chat_id`` of an unlinked chat is never
stored either -- only ``sha256(chat_id)``.

Working parameters, and where they come from
--------------------------------------------
The code format, the 15-minute expiry and the 5-per-hour rate limit are the PC08 parameter
package the Owner accepted (``OD-20260907-01`` item 23; card §10 ``SG-02``), and they are
still ``PROVISIONAL`` in the contract. They are therefore **settings**
(:class:`LinkingPolicy`), injected and overridable, not literals spread through the logic;
``tests/contract/test_telegram_command_allowlist.py`` asserts the defaults equal the values
in ``contracts/telegram/commands.yaml``, so a contract change fails the build instead of
drifting.

Transactions
------------
Every function here takes a :class:`~sqlalchemy.Connection` that is **already** inside a
transaction opened by the caller. Consuming a code is a compare-and-set: the code row moves
to ``consumed`` and the new ``telegram_link`` row appears in the same ``BEGIN…COMMIT``, so
the partial unique index ``ux_telegram_link_active`` can arbitrate two chats racing on one
code. The loser's UPDATE matches zero rows and it links nothing (fixture ``g``).
"""

from __future__ import annotations

import hashlib
import os
import re
import secrets
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Final

from sqlalchemy import Connection, text

# --------------------------------------------------------------------------------------
# Working parameters (PROVISIONAL in the contract; accepted as working values by SG-02)
# --------------------------------------------------------------------------------------

#: ``contracts/telegram/commands.yaml`` § linking → code_format → regex, verbatim.
#: Crockford base32 without I, L, O, U; the fixed ``RR-`` prefix is what lets the adapter
#: recognise "this string has the *shape* of a link code" without knowing any real code --
#: which is the precondition of the B09 exception itself.
LINK_CODE_REGEX: Final[str] = "^RR-[0-9A-HJKMNP-TV-Z]{8}$"

#: The alphabet the regex admits, for minting.
_CODE_ALPHABET: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_CODE_BODY_LENGTH: Final[int] = 8

#: Crockford base32 for ULIDs (``contracts/data/entities.yaml`` §conventions.id_type).
_CROCKFORD: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


@dataclass(frozen=True)
class LinkingPolicy:
    """The three PROVISIONAL parameters of ``CR-PC07-01``, as settings.

    :param code_regex: ``§ linking → code_format → regex``.
    :param code_ttl_seconds: ``§ linking → expiry`` (15 minutes).
    :param rate_limit_attempts: ``§ linking → rate_limit`` (5 per chat).
    :param rate_limit_window_seconds: the window that count is taken over (1 hour).
    :param update_max_age_seconds: ``ING-06`` ``telegram_update_max_age``, PROVISIONAL
        86400 s and still open as ``CR-PC07-05`` (card §10 ``SG-03``).
    """

    code_regex: str = LINK_CODE_REGEX
    code_ttl_seconds: int = 15 * 60
    rate_limit_attempts: int = 5
    rate_limit_window_seconds: int = 60 * 60
    update_max_age_seconds: int = 24 * 60 * 60


#: The default instance. A deployment overrides it through ``TelegramContext``; nothing in
#: this package reads a bare literal for any of these five numbers.
DEFAULT_LINKING_POLICY: Final[LinkingPolicy] = LinkingPolicy()


class LinkAttemptOutcome(str, Enum):
    """``telegram_link_attempt.outcome`` — the closed enum of ``entities.yaml``."""

    FORMAT_MATCH_CODE_INVALID = "format_match_code_invalid"
    FORMAT_MATCH_CODE_EXPIRED = "format_match_code_expired"
    FORMAT_MATCH_CODE_CONSUMED = "format_match_code_consumed"
    FORMAT_MATCH_CODE_VALID = "format_match_code_valid"
    RATE_LIMITED_NOT_CHECKED = "rate_limited_not_checked"


class LinkCodeState(str, Enum):
    """``telegram_link_code.state``."""

    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class LinkState(str, Enum):
    """``telegram_link.state``."""

    ACTIVE = "active"
    REVOKED = "revoked"


# --------------------------------------------------------------------------------------
# Small helpers: ids, clocks, hashes
# --------------------------------------------------------------------------------------


def format_timestamp(moment: datetime) -> str:
    """``2026-09-07T00:31:00.000Z`` — the only timestamp shape this schema stores."""
    moment = moment.astimezone(UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def parse_timestamp(value: str) -> datetime:
    """Inverse of :func:`format_timestamp`, for comparing a stored expiry with a clock."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp + 80 random bits, Crockford base32.

    Minted here rather than imported from another module's repository: an import into
    ``server.app.identity`` or ``server.app.ingest`` would be an in-process edge that
    ``contracts/modules.yaml`` does not grant to ``MOD-telegram-adapter``.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def hash_chat_id(chat_id: str) -> str:
    """``sha256(chat_id)``, lowercase hex.

    The one function that decides an unlinked stranger's chat id never reaches the disk.
    ``entities.yaml`` ``ENT-telegram-link-attempt.forbidden`` and ``ENT-telegram-update-log
    .forbidden`` both name storing the raw id as a defect, and ``errors.yaml``
    ``UNAUTHORIZED_COMMAND.redaction_vi`` repeats it for logs.
    """
    return hashlib.sha256(chat_id.encode("utf-8")).hexdigest()


def hash_link_code(code: str) -> str:
    """``sha256(mã thô)`` — ``entities.yaml``: the plaintext code is never stored."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def matches_code_format(message_text: str, policy: LinkingPolicy) -> bool:
    """Whether the **whole** trimmed message is a link code, per B09-EXCEPTION.

    Whole, not "contains": the exception is for a message that *is* a code. A rule that
    searched inside the text would open the comparison path to arbitrary prose, which the
    contract's ``forbidden_vi`` calls out as needlessly widening the attack surface.
    """
    return re.fullmatch(policy.code_regex, message_text.strip()) is not None


def mint_link_code() -> str:
    """A fresh code matching :data:`LINK_CODE_REGEX`, from ``secrets``.

    ``secrets``, not ``random``: this value is a credential for the duration of its 15
    minutes, and the whole point of an 8-character code is that guessing it is infeasible.
    """
    body = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_BODY_LENGTH))
    return f"RR-{body}"


# --------------------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LinkRow:
    """One row of ``telegram_link``."""

    id: str
    owner_id: str
    chat_id: str
    generation: int
    state: str
    linked_at: str


@dataclass(frozen=True)
class IssuedLinkCode:
    """The result of ``telegram.issue_link_code``.

    ``code`` is the **plaintext**, and it exists only in this object: the row holds the
    hash. ``contracts/telegram/commands.yaml`` § linking → issue_flow says the code is shown
    once in the app and never sent over Telegram, so it is returned to the caller and never
    logged, never echoed in an error, never persisted.
    """

    code_id: str
    code: str
    expires_at: str


class ConsumeOutcome(str, Enum):
    """What the B09 branch did. Only :attr:`LINKED` produces a reply."""

    NO_FORMAT_MATCH = "no_format_match"
    RATE_LIMITED_NOT_CHECKED = "rate_limited_not_checked"
    CODE_INVALID = "code_invalid"
    CODE_EXPIRED = "code_expired"
    CODE_CONSUMED = "code_consumed"
    LINKED = "linked"


@dataclass(frozen=True)
class ConsumeResult:
    """Outcome of :func:`consume_link_code` plus the link it created, if any."""

    outcome: ConsumeOutcome
    link: LinkRow | None = None
    previous_generation: int | None = None

    @property
    def is_silent(self) -> bool:
        """True for every outcome except a successful link (REQ-S11.3-02)."""
        return self.outcome is not ConsumeOutcome.LINKED


# --------------------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------------------


def active_link(connection: Connection, *, owner_id: str) -> LinkRow | None:
    """The link in force, or ``None``. At most one row can match (``ux_telegram_link_active``)."""
    row = (
        connection.execute(
            text(
                "SELECT id, owner_id, chat_id, generation, state, linked_at "
                "FROM telegram_link WHERE owner_id = :owner_id AND state = 'active'"
            ),
            {"owner_id": owner_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return LinkRow(
        id=str(row["id"]),
        owner_id=str(row["owner_id"]),
        chat_id=str(row["chat_id"]),
        generation=int(row["generation"]),
        state=str(row["state"]),
        linked_at=str(row["linked_at"]),
    )


def is_linked_chat(connection: Connection, *, owner_id: str, chat_id: str) -> bool:
    """``ING-07``: linked **and** the chat id matches.

    Two conditions, not one. Knowing the chat id is not authority (REQ-S11.3-03), and a
    linked owner does not make some *other* chat linked.
    """
    link = active_link(connection, owner_id=owner_id)
    return link is not None and link.chat_id == chat_id


def _current_generation(connection: Connection, *, owner_id: str) -> int:
    """Highest generation ever issued, including revoked rows.

    Read across **all** states on purpose: generations must never be reused, because a
    delivery pins one (``delivery.md`` §2) and a reused number would silently re-target a
    cancelled payload at a new recipient.
    """
    value = connection.execute(
        text("SELECT COALESCE(MAX(generation), 0) FROM telegram_link WHERE owner_id = :owner_id"),
        {"owner_id": owner_id},
    ).scalar_one()
    return int(value)


def count_recent_attempts(
    connection: Connection,
    *,
    owner_id: str,
    chat_id_hash: str,
    now: datetime,
    policy: LinkingPolicy,
) -> int:
    """The B09 rate-limit counter: format-matching attempts that did **not** link.

    ``contracts/telegram/commands.yaml`` § linking → rate_limit: *"Đếm theo chat_id_hash các
    lần khớp định dạng nhưng sai mã"*. Successful links are excluded because they are not
    probes, and ``rate_limited_not_checked`` rows are excluded because counting the refusals
    would make the window self-extending -- one burst would lock the chat out for far longer
    than the contract's hour.
    """
    window_start = format_timestamp(now - timedelta(seconds=policy.rate_limit_window_seconds))
    value = connection.execute(
        text(
            "SELECT COUNT(*) FROM telegram_link_attempt "
            "WHERE owner_id = :owner_id AND chat_id_hash = :chat_id_hash "
            "AND attempted_at > :window_start "
            "AND outcome IN ('format_match_code_invalid', 'format_match_code_expired', "
            "'format_match_code_consumed')"
        ),
        {"owner_id": owner_id, "chat_id_hash": chat_id_hash, "window_start": window_start},
    ).scalar_one()
    return int(value)


# --------------------------------------------------------------------------------------
# Writes
# --------------------------------------------------------------------------------------


def record_attempt(
    connection: Connection,
    *,
    owner_id: str,
    chat_id_hash: str,
    now: datetime,
    outcome: LinkAttemptOutcome,
    link_code_id: str | None,
) -> str:
    """Append one ``telegram_link_attempt`` row. Only ever called on a format match."""
    attempt_id = new_ulid()
    connection.execute(
        text(
            "INSERT INTO telegram_link_attempt "
            "(id, owner_id, chat_id_hash, attempted_at, outcome, link_code_id) VALUES "
            "(:id, :owner_id, :chat_id_hash, :attempted_at, :outcome, :link_code_id)"
        ),
        {
            "id": attempt_id,
            "owner_id": owner_id,
            "chat_id_hash": chat_id_hash,
            "attempted_at": format_timestamp(now),
            "outcome": outcome.value,
            "link_code_id": link_code_id,
        },
    )
    return attempt_id


def issue_link_code(
    connection: Connection,
    *,
    owner_id: str,
    now: datetime,
    policy: LinkingPolicy,
    code: str | None = None,
) -> IssuedLinkCode:
    """``telegram.issue_link_code`` — mint one code and revoke any predecessor.

    Commit point: the caller's transaction. The revoke and the insert are one statement pair
    because ``ux_telegram_link_code_active`` permits only one active code per owner; doing
    them in two transactions would leave a window where the insert fails.

    :param code: injectable **only** so a test can pin a known plaintext. Production passes
        ``None`` and the code comes from :func:`mint_link_code`.
    """
    plaintext = code if code is not None else mint_link_code()
    connection.execute(
        text(
            "UPDATE telegram_link_code SET state = 'revoked' "
            "WHERE owner_id = :owner_id AND state = 'active'"
        ),
        {"owner_id": owner_id},
    )
    code_id = new_ulid()
    expires_at = format_timestamp(now + timedelta(seconds=policy.code_ttl_seconds))
    connection.execute(
        text(
            "INSERT INTO telegram_link_code "
            "(id, owner_id, code_hash, issued_at, expires_at, consumed_at, "
            " consumed_by_chat_id, state) VALUES "
            "(:id, :owner_id, :code_hash, :issued_at, :expires_at, NULL, NULL, 'active')"
        ),
        {
            "id": code_id,
            "owner_id": owner_id,
            "code_hash": hash_link_code(plaintext),
            "issued_at": format_timestamp(now),
            "expires_at": expires_at,
        },
    )
    return IssuedLinkCode(code_id=code_id, code=plaintext, expires_at=expires_at)


def consume_link_code(
    connection: Connection,
    *,
    owner_id: str,
    chat_id: str,
    message_text: str,
    now: datetime,
    policy: LinkingPolicy,
) -> ConsumeResult:
    """``telegram.consume_link_code`` — the entire B09 exception, in order.

    The order is the contract's and it is load-bearing:

    1. **format** — no match, no lookup, no row, no reply;
    2. **rate limit** — over the threshold, record ``rate_limited_not_checked`` and stop
       *before* the lookup (the point of the limit is to shrink the guessing window);
    3. **lookup by hash** of the presented code among this owner's codes;
    4. **expiry / already-consumed / unknown** — one row each, all silent;
    5. **link** — CAS the code to ``consumed`` and open a new generation.

    Step 5 is a compare-and-set: the ``UPDATE … WHERE state = 'active'`` is what makes the
    code single-use under concurrency. If it matches zero rows another chat won the race and
    this call links nothing, which is fixture ``g``'s second event.
    """
    chat_id_hash = hash_chat_id(chat_id)
    if not matches_code_format(message_text, policy):
        return ConsumeResult(ConsumeOutcome.NO_FORMAT_MATCH)

    attempts = count_recent_attempts(
        connection, owner_id=owner_id, chat_id_hash=chat_id_hash, now=now, policy=policy
    )
    if attempts >= policy.rate_limit_attempts:
        record_attempt(
            connection,
            owner_id=owner_id,
            chat_id_hash=chat_id_hash,
            now=now,
            outcome=LinkAttemptOutcome.RATE_LIMITED_NOT_CHECKED,
            link_code_id=None,
        )
        return ConsumeResult(ConsumeOutcome.RATE_LIMITED_NOT_CHECKED)

    code_hash = hash_link_code(message_text.strip())
    row = (
        connection.execute(
            text(
                "SELECT id, state, expires_at FROM telegram_link_code "
                "WHERE owner_id = :owner_id AND code_hash = :code_hash"
            ),
            {"owner_id": owner_id, "code_hash": code_hash},
        )
        .mappings()
        .first()
    )

    if row is None:
        record_attempt(
            connection,
            owner_id=owner_id,
            chat_id_hash=chat_id_hash,
            now=now,
            outcome=LinkAttemptOutcome.FORMAT_MATCH_CODE_INVALID,
            link_code_id=None,
        )
        return ConsumeResult(ConsumeOutcome.CODE_INVALID)

    code_id = str(row["id"])
    if str(row["state"]) != LinkCodeState.ACTIVE.value:
        # Consumed, revoked (superseded by a newer code) or already marked expired. All
        # three are "not usable" and all three are silent; the row keeps them apart for the
        # owner, not for the sender.
        outcome = (
            LinkAttemptOutcome.FORMAT_MATCH_CODE_CONSUMED
            if str(row["state"]) == LinkCodeState.CONSUMED.value
            else LinkAttemptOutcome.FORMAT_MATCH_CODE_INVALID
        )
        record_attempt(
            connection,
            owner_id=owner_id,
            chat_id_hash=chat_id_hash,
            now=now,
            outcome=outcome,
            link_code_id=code_id,
        )
        return ConsumeResult(
            ConsumeOutcome.CODE_CONSUMED
            if outcome is LinkAttemptOutcome.FORMAT_MATCH_CODE_CONSUMED
            else ConsumeOutcome.CODE_INVALID
        )

    if parse_timestamp(str(row["expires_at"])) <= now:
        # Not rewritten to 'expired' here: this path runs for an **unlinked** chat, and
        # fixture (i) pins `domain_rows_changed: 0` for it. Expiry is a fact about the
        # clock, not a state a stranger's message may change.
        record_attempt(
            connection,
            owner_id=owner_id,
            chat_id_hash=chat_id_hash,
            now=now,
            outcome=LinkAttemptOutcome.FORMAT_MATCH_CODE_EXPIRED,
            link_code_id=code_id,
        )
        return ConsumeResult(ConsumeOutcome.CODE_EXPIRED)

    consumed = connection.execute(
        text(
            "UPDATE telegram_link_code SET state = 'consumed', consumed_at = :now, "
            "consumed_by_chat_id = :chat_id "
            "WHERE id = :id AND owner_id = :owner_id AND state = 'active'"
        ),
        {"now": format_timestamp(now), "chat_id": chat_id, "id": code_id, "owner_id": owner_id},
    ).rowcount
    if consumed != 1:  # pragma: no cover - the losing side of a race; asserted by fixture g
        record_attempt(
            connection,
            owner_id=owner_id,
            chat_id_hash=chat_id_hash,
            now=now,
            outcome=LinkAttemptOutcome.FORMAT_MATCH_CODE_CONSUMED,
            link_code_id=code_id,
        )
        return ConsumeResult(ConsumeOutcome.CODE_CONSUMED)

    link, previous = _open_new_generation(connection, owner_id=owner_id, chat_id=chat_id, now=now)
    record_attempt(
        connection,
        owner_id=owner_id,
        chat_id_hash=chat_id_hash,
        now=now,
        outcome=LinkAttemptOutcome.FORMAT_MATCH_CODE_VALID,
        link_code_id=code_id,
    )
    return ConsumeResult(ConsumeOutcome.LINKED, link=link, previous_generation=previous)


def _open_new_generation(
    connection: Connection, *, owner_id: str, chat_id: str, now: datetime
) -> tuple[LinkRow, int | None]:
    """Revoke the link in force and insert its successor, one generation higher.

    REQ-D37 / REQ-S11.3-04: a new link invalidates the old one. The revoke happens first so
    ``ux_telegram_link_active`` never sees two live rows; the deliveries pinned to the old
    generation are cancelled by ``MOD-delivery-service`` when it next reads them
    (``delivery.yaml`` T-DL-08, fixture ``e``) -- this module does not touch delivery rows,
    because ``contracts/modules.yaml`` gives it no edge to do so.
    """
    previous = active_link(connection, owner_id=owner_id)
    if previous is not None:
        connection.execute(
            text("UPDATE telegram_link SET state = 'revoked' WHERE id = :id"),
            {"id": previous.id},
        )
    generation = _current_generation(connection, owner_id=owner_id) + 1
    link = LinkRow(
        id=new_ulid(),
        owner_id=owner_id,
        chat_id=chat_id,
        generation=generation,
        state=LinkState.ACTIVE.value,
        linked_at=format_timestamp(now),
    )
    connection.execute(
        text(
            "INSERT INTO telegram_link (id, owner_id, chat_id, generation, state, linked_at) "
            "VALUES (:id, :owner_id, :chat_id, :generation, 'active', :linked_at)"
        ),
        {
            "id": link.id,
            "owner_id": link.owner_id,
            "chat_id": link.chat_id,
            "generation": link.generation,
            "linked_at": link.linked_at,
        },
    )
    return link, (None if previous is None else previous.generation)


@dataclass(frozen=True)
class UnlinkResult:
    """Outcome of ``telegram.unlink``. Idempotent: unlinking twice is not an error."""

    was_linked: bool
    revoked_generation: int | None


def unlink(connection: Connection, *, owner_id: str, now: datetime) -> UnlinkResult:
    """``telegram.unlink`` — an **app** action, never a fourth chat command (AMD-B10).

    Commit point: the caller's transaction. Cancelling the deliveries pinned to the revoked
    generation is ``MOD-delivery-service``'s transition ``T-DL-08``; this function does not
    reach into ``delivery`` rows, and a caller that needs that cancellation drives it through
    the delivery port (``TC-telegram-unknown-delivery``).

    ``now`` is accepted for symmetry with the rest of the module and to keep the call site
    honest about which clock decides; the revoke itself writes no timestamp, because
    ``telegram_link`` has no ``revoked_at`` column in ``entities.yaml`` and inventing one
    here would put the schema and the contract out of step.
    """
    del now
    link = active_link(connection, owner_id=owner_id)
    if link is None:
        return UnlinkResult(was_linked=False, revoked_generation=None)
    connection.execute(
        text("UPDATE telegram_link SET state = 'revoked' WHERE id = :id"), {"id": link.id}
    )
    return UnlinkResult(was_linked=True, revoked_generation=link.generation)


def link_snapshot(connection: Connection, *, owner_id: str) -> dict[str, Any]:
    """The safe view of the link state for an owner-facing response.

    Carries the generation and the linked-at timestamp but **not** the chat id: the API
    response is read in a browser, and echoing the recipient there adds no capability the
    owner does not already have while widening where the identifier appears.
    """
    link = active_link(connection, owner_id=owner_id)
    return {
        "linked": link is not None,
        "generation": None if link is None else link.generation,
        "linked_at": None if link is None else link.linked_at,
    }
