"""``MOD-report-service`` — the backfill ledger: N days, exactly once per subscription.

The one sentence this module exists to make true
------------------------------------------------
*A subscription identity consumes its N-day backfill exactly once, for the whole life of the
system, and a crash never spends it.* Both halves are load-bearing and each is broken by an
obvious-looking implementation:

**"subscription identity", not "tag row".** ``ux_tag_owner_text_active`` is a partial unique
index on ``state = 'active'``, so removing a tag and adding the same words back mints a *new*
``tag.id``. An entitlement keyed on ``tag_id`` would therefore be granted again on every
re-add, and REQ-D28's "exactly once" would mean "once per add" — the defect fixture
``reporting/j-backfill-add-remove-readd.json`` exists to catch. The key is
:func:`subscription_identity_hash`, and the database enforces it:
``ux_backfill_subscription_consumed`` = ``UNIQUE(owner_id, subscription_identity_hash) WHERE
consumed_in_report_id IS NOT NULL`` (``contracts/data/entities.yaml`` ``ENT-backfill-ledger``,
``contracts/reporting/time-and-tags.md`` §6.2).

**"consumed at the publish commit", not "consumed at build".** ``time-and-tags.md`` §6.4 makes
consumption conditional on three facts. Condition 1 — *the publish transaction commits* — is
not this module's to decide, and deliberately so: the UPDATE that writes
``consumed_in_report_id`` lives in ``server.app.report.publisher._consume_backfill``, inside
``TXN-report-publish``. This module decides conditions 2 and 3 and hands the publisher a list
of ledger ids (:func:`entitlements_to_consume` → ``BuildSnapshot.backfill_ledger_ids_applied``).
A builder that dies before the commit never reaches that UPDATE, which is why
``reporting/k-builder-crash-backfill-not-consumed.json`` passes structurally rather than by
convention. **Nothing in this file writes ``consumed_in_report_id``**; a convenience helper
that did would be a second writer on the publish path and would make the crash oracle depend
on which one ran.

What this module owns, then
---------------------------
* the identity function (§6.2) and the activation ledger it keys — :func:`open_activation`;
* the candidate-range widening (§6.3) — :func:`candidate_range`, :func:`plan_extension`;
* conditions 2 and 3 of §6.4 — :func:`entitlements_to_consume`;
* the counting oracles O-6.1 and O-6.2 as queries.

And what it does not
--------------------
It does not move ``coverage_window.window_from``. Backfill widens a *query*, never the
coverage window (§6.3); the two are different statements and mixing them makes the window
chain overlap, which is exactly what ``I06`` forbids — fixture ``j``'s third forbidden effect.
It never touches ``first_announced_ledger`` (``I07``) and never reads or writes
``rescan_ledger``: rescan is a separate command with a separate ledger (§7). Its SQL names one
table, ``backfill_ledger``, plus one existence read of ``settings``.

``CR-TC-BACKFILL-05``: the builder does not apply the extension yet
-------------------------------------------------------------------
``contracts/reporting/selection.md`` §2 writes the candidate set as three unions, the third
being *"target nằm trong phần nới backfill"*. ``server.app.report.builder._candidates``
currently unions only the first two, and ``BuildSnapshot.backfill_ledger_ids_applied`` is
derived from ``Candidate.backfill_ledger_id``, which nothing sets. That file is W4A's and is
not this card's to edit, so the seam is offered here — :func:`plan_extension` and
:func:`entitlements_to_consume` compose with ``build_report``'s output — and the request to
wire it in as a ``backfill_port`` parameter is carried as ``CR-TC-BACKFILL-05``.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Connection, text

OWNER_MODULE: Final[str] = "MOD-report-service"

#: ``ENT-backfill-ledger.entitlement``. Three values, taken verbatim from
#: ``contracts/data/entities.yaml`` and from the CHECK ``0010_tc_report_coverage_publish_cas``
#: shipped. ``time-and-tags.md`` §6.5 O-6.2 spells the third one ``none`` instead, which is
#: not a member of the contract enum — raised as ``CR-TC-BACKFILL-01`` and resolved in favour
#: of ``entities.yaml``, which the same file's §6.2 table and fixture ``j`` both agree with.
ENTITLEMENT_GRANTED: Final[str] = "granted"
ENTITLEMENT_CONSUMED: Final[str] = "consumed"
ENTITLEMENT_DENIED: Final[str] = "denied_already_consumed"

#: ``entitlement_reason`` for the first activation of a subscription identity.
REASON_FIRST_ACTIVATION: Final[str] = "first_activation"

#: ``entitlement_reason`` for a re-add whose identity already spent its backfill. The text is
#: the one fixture ``reporting/j-backfill-add-remove-readd.json`` asserts, and the shipped
#: CHECK ``ck_backfill_denied_has_reason`` requires the field to be non-empty exactly here —
#: so that the Topics screen can explain why a re-added tag does not reach backwards.
REASON_ALREADY_CONSUMED: Final[str] = (
    "Subscription identity này đã tiêu thụ backfill ở activation trước; "
    "muốn đào sâu thì dùng tag.rescan_corpus (SRC-SPEC §8.2 hàng 4)."
)

#: ``settings`` key holding N (``time-and-tags.md`` §6.1). Read, never hard-coded: card §10
#: ``SG-03`` accepts 7 as the Owner's working value but requires it to come from settings, so
#: that changing it is a settings edit rather than a code change.
SETTING_BACKFILL_DAYS: Final[str] = "reporting.backfill_days"

#: ``settings`` key for the hard ceiling of §6.1. Unlike N it is a guard rather than a tuning
#: knob, so an absent row falls back to the contract number: a missing ceiling must not read
#: as "no ceiling".
SETTING_BACKFILL_MAX_EXTENSION: Final[str] = "reporting.backfill_max_extension"

#: ``time-and-tags.md`` §6.1, second row.
BACKFILL_MAX_EXTENSION_DAYS: Final[int] = 30


class BackfillError(Exception):
    """A refusal carrying a contract error code (``contracts/errors.yaml``)."""

    def __init__(self, code: ErrorCode, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.details_safe: dict[str, Any] = details


# --------------------------------------------------------------------------------------
# Subscription identity (§6.2)
# --------------------------------------------------------------------------------------

_WHITESPACE = re.compile(r"\s+")


def normalize_tag_text(value: str) -> str:
    """``time-and-tags.md`` §6.2 ``normalize_tag_text``: NFC → trim → casefold → collapse.

    Pure, deterministic, no network — the same discipline as ``contracts/data/identity.md``
    §2. The order is the contract's: casefolding before collapsing keeps the function
    idempotent for the Unicode spaces casefold does not touch.
    """
    folded = unicodedata.normalize("NFC", value).strip().casefold()
    return _WHITESPACE.sub(" ", folded)


def subscription_identity_hash(owner_id: str, tag_text: str) -> str:
    """64 lowercase hex of ``sha256(owner_id + "\\n" + normalize_tag_text(tag_text))``.

    The preimage is fixed by ``ENT-backfill-ledger.subscription_identity_hash`` and restated
    in §6.2, which also records that the earlier proposal (``sha256(JCS(...))``) is *not* the
    one ruled. The output is bare hex with **no** ``sha256:`` prefix, because the column's
    shipped CHECK is ``length(subscription_identity_hash) = 64``
    (``0010_tc_report_coverage_publish_cas``). The literal hashes in fixture ``j`` carry the
    prefix, but ``acceptance/fixtures/reporting/README.md`` §4 says those literals are
    shape-only ("fixture khẳng định quan hệ, không khẳng định một chuỗi hex bịa") and they are
    not recomputable from this preimage — so the oracle asserted against them is the
    *relation* (both activations share one identity), never the hex.

    Changing the *words* of a tag yields a different identity and therefore a fresh
    entitlement. §6.2 records that as deliberate: the system does not guess that two different
    strings are the same interest.
    """
    preimage = f"{owner_id}\n{normalize_tag_text(tag_text)}".encode()
    return hashlib.sha256(preimage).hexdigest()


# --------------------------------------------------------------------------------------
# Settings (SG-03)
# --------------------------------------------------------------------------------------


class SettingsPort(Protocol):
    """Read side of ``ENT-settings`` (owned by ``MOD-settings-service``)."""

    def get_int(self, key: str) -> int | None: ...


@dataclass(frozen=True)
class TableSettings:
    """Reads ``settings`` rows on the connection already in hand.

    Reading the table is not calling the operation: ``contracts/modules.yaml`` has no
    ``MOD-report-service → MOD-settings-service`` edge, and none is used. The shape is fixed
    by ``entities.yaml`` ``ENT-settings``.
    """

    owner_id: str
    connection: Connection

    def get_int(self, key: str) -> int | None:
        row = self.connection.execute(
            text('SELECT value_json FROM settings WHERE owner_id = :owner_id AND "key" = :key'),
            {"owner_id": self.owner_id, "key": key},
        ).fetchone()
        if row is None:
            return None
        raw = str(row[0]).strip().strip('"')
        try:
            return int(raw)
        except ValueError as exc:
            raise BackfillError(
                ErrorCode.VALIDATION_ERROR,
                "settings value is not an integer",
                field_path=key,
                violation_kind="type_invalid",
            ) from exc


def backfill_days(settings: SettingsPort) -> int:
    """N, from settings. Absent ⇒ ``VALIDATION_ERROR``, never a default.

    Card §10 ``SG-03``: N = 7 is the Owner's accepted **working value**, not a measured one,
    and it is read from settings. A code-side default would quietly reintroduce the constant
    the stop condition exists to keep out of the source, and would make an unconfigured
    deployment silently reach seven days back.
    """
    value = settings.get_int(SETTING_BACKFILL_DAYS)
    if value is None:
        raise BackfillError(
            ErrorCode.VALIDATION_ERROR,
            "reporting.backfill_days is not configured",
            field_path=SETTING_BACKFILL_DAYS,
            violation_kind="required_missing",
        )
    if value < 0:
        raise BackfillError(
            ErrorCode.VALIDATION_ERROR,
            "reporting.backfill_days must not be negative",
            field_path=SETTING_BACKFILL_DAYS,
            violation_kind="range_invalid",
        )
    return value


def backfill_max_extension_days(settings: SettingsPort) -> int:
    """The §6.1 ceiling. Absent ⇒ the contract's 30: a missing guard is not "no guard"."""
    value = settings.get_int(SETTING_BACKFILL_MAX_EXTENSION)
    return BACKFILL_MAX_EXTENSION_DAYS if value is None else value


# --------------------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Entitlement:
    """One ``backfill_ledger`` row, as this module reads it."""

    id: str
    owner_id: str
    tag_id: str
    activation_sequence: int
    subscription_identity_hash: str
    entitlement: str
    entitlement_reason: str | None
    backfill_days: int
    consumed_in_report_id: str | None
    consumed_at: str | None

    @property
    def is_spendable(self) -> bool:
        return self.entitlement == ENTITLEMENT_GRANTED and self.consumed_in_report_id is None


_ROW_COLUMNS = (
    "id, owner_id, tag_id, activation_sequence, subscription_identity_hash, entitlement, "
    "entitlement_reason, backfill_days, consumed_in_report_id, consumed_at"
)


def _row(record: Any) -> Entitlement:
    return Entitlement(
        id=record[0],
        owner_id=record[1],
        tag_id=record[2],
        activation_sequence=int(record[3]),
        subscription_identity_hash=record[4],
        entitlement=record[5],
        entitlement_reason=record[6],
        backfill_days=int(record[7]),
        consumed_in_report_id=record[8],
        consumed_at=record[9],
    )


def rows_for_identity(
    connection: Connection, *, owner_id: str, identity_hash: str
) -> list[Entitlement]:
    """Every activation of one subscription identity, oldest first."""
    result = connection.execute(
        text(
            f"SELECT {_ROW_COLUMNS} FROM backfill_ledger "
            "WHERE owner_id = :owner_id AND subscription_identity_hash = :identity "
            "ORDER BY activation_sequence"
        ),
        {"owner_id": owner_id, "identity": identity_hash},
    ).fetchall()
    return [_row(record) for record in result]


def rows_for_tag(connection: Connection, *, owner_id: str, tag_id: str) -> list[Entitlement]:
    result = connection.execute(
        text(
            f"SELECT {_ROW_COLUMNS} FROM backfill_ledger "
            "WHERE owner_id = :owner_id AND tag_id = :tag_id ORDER BY activation_sequence"
        ),
        {"owner_id": owner_id, "tag_id": tag_id},
    ).fetchall()
    return [_row(record) for record in result]


def spendable_for_tag(connection: Connection, *, owner_id: str, tag_id: str) -> Entitlement | None:
    """The oldest ``granted`` row of this tag that has not been consumed, or ``None``."""
    result = connection.execute(
        text(
            f"SELECT {_ROW_COLUMNS} FROM backfill_ledger "
            "WHERE owner_id = :owner_id AND tag_id = :tag_id "
            "AND entitlement = :granted AND consumed_in_report_id IS NULL "
            "ORDER BY activation_sequence LIMIT 1"
        ),
        {"owner_id": owner_id, "tag_id": tag_id, "granted": ENTITLEMENT_GRANTED},
    ).fetchone()
    return None if result is None else _row(result)


# --------------------------------------------------------------------------------------
# Activation (§6.2)
# --------------------------------------------------------------------------------------


def open_activation(
    connection: Connection,
    *,
    owner_id: str,
    tag_id: str,
    tag_text: str,
    days: int,
    new_id: str,
) -> Entitlement:
    """Record one activation of a subscription and decide its entitlement.

    Called from the ``tag.create`` transaction (``contracts/ports.yaml``: *"mở một backfill
    activation N ngày dùng đúng một lần"*). It writes on the caller's connection, so the
    activation row and the tag row commit together; a tag that existed without its ledger row
    would make "how many activations has this subscription had" unanswerable after the fact.

    ``activation_sequence`` counts activations of the **subscription identity**, not of the
    tag row: §6.2 defines it as increasing each time a tag carrying that normalized text
    becomes ``active``, and fixture ``j`` numbers the re-added tag 2 even though its
    ``tag.id`` is new.

    The decision is one question — *has this identity already consumed?* An unconsumed
    ``granted`` row from an earlier activation does not deny the new one; only a spent one
    does (§6.2). Granting twice is harmless because ``ux_backfill_subscription_consumed``
    makes the second *consumption* impossible, and that is where "exactly once" actually
    lives — in the database, not in this branch.

    ``days`` is copied onto the row rather than read back later, so that changing
    ``reporting.backfill_days`` afterwards does not rewrite history (§6.1).
    """
    identity_hash = subscription_identity_hash(owner_id, tag_text)
    history = rows_for_identity(connection, owner_id=owner_id, identity_hash=identity_hash)
    already_consumed = any(row.consumed_in_report_id is not None for row in history)
    activation_sequence = max((row.activation_sequence for row in history), default=0) + 1

    entitlement = ENTITLEMENT_DENIED if already_consumed else ENTITLEMENT_GRANTED
    reason = REASON_ALREADY_CONSUMED if already_consumed else REASON_FIRST_ACTIVATION

    connection.execute(
        text(
            "INSERT INTO backfill_ledger (id, owner_id, tag_id, activation_sequence, "
            "subscription_identity_hash, entitlement, entitlement_reason, backfill_days, "
            "consumed_in_report_id, consumed_at) VALUES (:id, :owner_id, :tag_id, :seq, "
            ":identity, :entitlement, :reason, :days, NULL, NULL)"
        ),
        {
            "id": new_id,
            "owner_id": owner_id,
            "tag_id": tag_id,
            "seq": activation_sequence,
            "identity": identity_hash,
            "entitlement": entitlement,
            "reason": reason,
            "days": days,
        },
    )
    return Entitlement(
        id=new_id,
        owner_id=owner_id,
        tag_id=tag_id,
        activation_sequence=activation_sequence,
        subscription_identity_hash=identity_hash,
        entitlement=entitlement,
        entitlement_reason=reason,
        backfill_days=days,
        consumed_in_report_id=None,
        consumed_at=None,
    )


# --------------------------------------------------------------------------------------
# Candidate range (§6.3)
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CandidateRange:
    """The half-open ``[start, end)`` one tag's candidate query runs over."""

    tag_id: str
    start: datetime
    end: datetime
    extended: bool
    entitlement_id: str | None


def candidate_range(
    *,
    tag_id: str,
    coverage_from: datetime,
    coverage_to: datetime,
    entitlement: Entitlement | None,
    days: int,
    max_extension_days: int = BACKFILL_MAX_EXTENSION_DAYS,
) -> CandidateRange:
    """``time-and-tags.md`` §6.3, transcribed.

    ``max(coverage_from − backfill_days, coverage_from − backfill_max_extension)`` is written
    the way the contract writes it. It is a ``max`` over two *instants*, so the wider of the
    two windows loses: the ceiling clamps N rather than extending it.

    The right edge is never widened, and the caller never writes ``start`` into
    ``coverage_window.window_from`` — fixture ``j``'s third forbidden effect. Backfill widens
    the query; coverage records the cursor.
    """
    if entitlement is None or not entitlement.is_spendable or days <= 0:
        return CandidateRange(
            tag_id=tag_id,
            start=coverage_from,
            end=coverage_to,
            extended=False,
            entitlement_id=None,
        )
    by_days = coverage_from - timedelta(days=days)
    by_ceiling = coverage_from - timedelta(days=max_extension_days)
    start = max(by_days, by_ceiling)
    return CandidateRange(
        tag_id=tag_id,
        start=start,
        end=coverage_to,
        extended=start < coverage_from,
        entitlement_id=entitlement.id,
    )


@dataclass(frozen=True)
class ExtensionPlan:
    """What the widening looks like for one period, per tag."""

    ranges: tuple[CandidateRange, ...]

    @property
    def extended(self) -> tuple[CandidateRange, ...]:
        return tuple(item for item in self.ranges if item.extended)

    def range_for(self, tag_id: str) -> CandidateRange | None:
        for item in self.ranges:
            if item.tag_id == tag_id:
                return item
        return None


def plan_extension(
    connection: Connection,
    *,
    owner_id: str,
    coverage_from: datetime,
    coverage_to: datetime,
    tags: Sequence[str],
    settings: SettingsPort,
) -> ExtensionPlan:
    """The §6.3 widening for every active tag of the period.

    Reads ``backfill_ledger`` and ``settings`` and nothing else — it returns *ranges*, not
    rows. Which targets fall inside a range is selection's question
    (``contracts/reporting/selection.md`` §2), and answering it here would put this module in
    the business of reading ``work`` and ``post``, which belong to other modules.
    """
    days = backfill_days(settings)
    ceiling = backfill_max_extension_days(settings)
    ranges = []
    for tag_id in tags:
        entitlement = spendable_for_tag(connection, owner_id=owner_id, tag_id=tag_id)
        ranges.append(
            candidate_range(
                tag_id=tag_id,
                coverage_from=coverage_from,
                coverage_to=coverage_to,
                entitlement=entitlement,
                days=days,
                max_extension_days=ceiling,
            )
        )
    return ExtensionPlan(ranges=tuple(ranges))


# --------------------------------------------------------------------------------------
# §6.4 conditions 2 and 3
# --------------------------------------------------------------------------------------


def entitlements_to_consume(
    plan: ExtensionPlan, produced_by_extension: Mapping[str, int]
) -> tuple[str, ...]:
    """The ledger ids ``BuildSnapshot.backfill_ledger_ids_applied`` should carry.

    Conditions 2 and 3 of §6.4, and only those two — condition 1 is the publish COMMIT, which
    belongs to ``server.app.report.publisher``:

    2. the widening was actually applied (``CandidateRange.extended``);
    3. it produced at least one candidate, which the caller reports per tag as a count of rows
       it is writing in this same commit — a ``report_item`` **or** a ``pending_item_ledger``
       row, because §6.4 counts both.

    That second clause is why a total model failure still spends the entitlement (everything
    found is in the pending ledger and is certain to come back next period, §5.2) while an
    *empty* extension does not: re-reading an empty range costs no AI, so there is nothing to
    spend. Fixture ``k``'s two variants are exactly these two branches.

    Ids come back sorted and de-duplicated, matching the shape ``build_report`` produces.
    """
    return tuple(
        sorted(
            {
                item.entitlement_id
                for item in plan.extended
                if item.entitlement_id is not None and produced_by_extension.get(item.tag_id, 0) > 0
            }
        )
    )


# --------------------------------------------------------------------------------------
# Oracles as queries
# --------------------------------------------------------------------------------------


def consumed_count(
    connection: Connection, *, owner_id: str, identity_hash: str | None = None
) -> int:
    """O-6.1's counter: consumed rows, optionally for one subscription identity."""
    if identity_hash is None:
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM backfill_ledger WHERE owner_id = :owner_id "
                "AND consumed_in_report_id IS NOT NULL"
            ),
            {"owner_id": owner_id},
        )
    else:
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM backfill_ledger WHERE owner_id = :owner_id "
                "AND subscription_identity_hash = :identity "
                "AND consumed_in_report_id IS NOT NULL"
            ),
            {"owner_id": owner_id, "identity": identity_hash},
        )
    return int(result.scalar_one())


def identities_with_multiple_consumptions(connection: Connection, *, owner_id: str) -> list[str]:
    """O-6.1 stated as a query: any identity group with more than one consumed row.

    Returned as data rather than asserted here so a failing test names the offending identity
    instead of only failing a boolean.
    """
    result = connection.execute(
        text(
            "SELECT subscription_identity_hash FROM backfill_ledger "
            "WHERE owner_id = :owner_id AND consumed_in_report_id IS NOT NULL "
            "GROUP BY subscription_identity_hash HAVING COUNT(*) > 1"
        ),
        {"owner_id": owner_id},
    ).fetchall()
    return [record[0] for record in result]
