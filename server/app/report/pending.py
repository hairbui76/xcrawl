"""``MOD-report-service`` — the pending-item ledger, away from the publish transaction.

The one sentence this module exists to make true
------------------------------------------------
*An item discovered in period N but missing its analysis is still reachable in period N+1,
even though its ``discovered_at`` is outside period N+1's window.* That is invariant ``I06``,
and the reason the ledger exists at all: a builder that only ever looks inside
``[coverage_from, coverage_to)`` can never see the item again, because the cursor has moved
past it. Fixture ``reporting/e-late-analysis-pending-then-late-discovery.json`` states the
case exactly — ``E1.discovered_at`` = ``2026-09-06T02:00Z`` sits outside period 3's window and
period 3 must still carry it, labelled ``late_discovery``.

Where this module sits relative to ``server.app.report.publisher``
-------------------------------------------------------------------
The publisher owns the *publish-time* half and writes it inline inside
``TXN-report-publish``: ``_write_pending`` opens the period's new rows and closes the ones the
period resolved. This module owns the three halves that live **outside** a publish:

* :class:`EngineBoundPendingLedger` / :class:`ConnectionBoundPendingLedger` — the
  ``PendingLedgerPort`` that ``server.app.analysis.service.AnalysisContext`` has been carrying
  as ``None`` since Phase 3. Without an implementation, ``_fail_task`` reports
  ``pending_ledger_recorded: False`` and an item that exhausted its analysis budget is lost to
  the ledger, which is the ``I06`` failure arriving through the other door. Both accept an
  optional ``connection``, so the ledger row joins the caller's transaction instead of
  contending with it for SQLite's single write lock (``CR-TC-BACKFILL-02``).
* :func:`abandon` — ``state = 'abandoned_by_owner'``, the Owner's explicit act and nothing
  else. §5.3: the system never abandons on its own and no timeout turns pending into
  abandoned. A sweep that expired old pending rows would satisfy every count in this file
  while losing exactly the items the ledger exists to keep.
* the read side and the oracles — :func:`carried_forward`, :func:`quality_for_window`,
  :func:`count_by_state`.

**Rows are never deleted.** Nothing in this module issues a DELETE against
``pending_item_ledger``, and ``entities.yaml``'s data-deletion table lists it among the
ledgers a deletion must not touch. "The cursor advanced, so the pending row is stale" is the
defect O-5.2 is the control for.

One call-site change is still needed — ``CR-TC-BACKFILL-02b``
--------------------------------------------------------------
``PendingLedgerPort.record_pending`` in ``server.app.analysis.service`` still declares
``(self, *, target_key, reason)`` and ``_fail_task`` still calls it without a connection, so
the deadlock stands until that one call passes the ``connection`` it already holds:

    ctx.pending_ledger.record_pending(
        target_key=task.target_key, reason=reason, connection=connection
    )

The parameter is optional here precisely so that change can be made on its own, without a
flag day: this module accepts both shapes today, and W3B's ``strict=True`` xfail keeps
failing in the pinned way until the call site moves.

``CR-TC-BACKFILL-06``: two insert sites
----------------------------------------
``publisher._write_pending`` and :func:`record_pending` both insert into
``pending_item_ledger`` with the same shape and the same ``ux_pending_owner_target_open``
arbiter. Two spellings of one write is how they drift. The publisher's file is W4A's write
set and not this card's to edit, so the duplication is reported rather than removed, with the
suggestion that the publisher call :func:`record_pending`.

Quality, not status
-------------------
:func:`quality_for_window` implements O-5.3: ``report.quality = 'complete'`` only when this
period opened no still-pending row. ``quality`` is a field distinct from ``status``
(SRC-PLAN §8.2): a period with pending items is ``published`` and ``partial``, not aborted,
and the items still appear (AMD-B17) with ``summary_state = 'pending'`` rather than hidden.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Connection, Engine, text

OWNER_MODULE: Final[str] = "MOD-report-service"

#: ``ENT-pending-item-ledger.state``.
STATE_PENDING: Final[str] = "pending"
STATE_RESOLVED_LATE: Final[str] = "resolved_reported_late"
STATE_ABANDONED: Final[str] = "abandoned_by_owner"

#: ``ENT-pending-item-ledger.reason``. The same four values as ``pending_item.reason`` in
#: ``contracts/schemas/report.schema.json``; the enum is closed in both places and in the
#: shipped CHECK.
REASONS: Final[frozenset[str]] = frozenset(
    {"missing_summary", "analysis_failed", "analysis_unknown", "budget_exceeded"}
)

#: ``report.quality`` (SRC-PLAN §8.2).
QUALITY_COMPLETE: Final[str] = "complete"
QUALITY_PARTIAL: Final[str] = "partial"

#: The partial unique index that decides "already open":
#: ``UNIQUE(owner_id, target_key) WHERE state = 'pending'``.
IX_OPEN: Final[str] = "ux_pending_owner_target_open"


class PendingLedgerError(Exception):
    """A refusal carrying a contract error code (``contracts/errors.yaml``)."""

    def __init__(self, code: ErrorCode, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.details_safe: dict[str, Any] = details


@dataclass(frozen=True)
class PendingItem:
    """One ``pending_item_ledger`` row."""

    id: str
    owner_id: str
    target_key: str
    reason: str
    first_pending_window_id: str
    state: str


_COLUMNS = "id, owner_id, target_key, reason, first_pending_window_id, state"


def _item(record: Any) -> PendingItem:
    return PendingItem(
        id=record[0],
        owner_id=record[1],
        target_key=record[2],
        reason=record[3],
        first_pending_window_id=record[4],
        state=record[5],
    )


# --------------------------------------------------------------------------------------
# Writes -- always on the caller's connection
# --------------------------------------------------------------------------------------


def record_pending(
    connection: Connection,
    *,
    owner_id: str,
    target_key: str,
    reason: str,
    first_pending_window_id: str,
    new_id: str,
) -> PendingItem:
    """Open — or return — the pending row for one target.

    Idempotent through the open-row read plus ``ux_pending_owner_target_open``: an already
    open row for the same ``target_key`` comes back unchanged, keeping
    ``first_pending_window_id`` at the window that *first* missed the item. That field is what
    ``report_item.selection_reason.pending_since_window_sequence`` renders ("phát hiện muộn,
    thuộc kỳ #12", §5.3), so overwriting it on the second sighting would walk the item's
    history forward every period until the label meant nothing.
    """
    if reason not in REASONS:
        raise PendingLedgerError(
            ErrorCode.VALIDATION_ERROR,
            "reason is not one of the four contract values",
            field_path="reason",
            violation_kind="enum_invalid",
        )
    existing = open_item(connection, owner_id=owner_id, target_key=target_key)
    if existing is not None:
        return existing
    connection.execute(
        text(
            "INSERT INTO pending_item_ledger "
            "(id, owner_id, target_key, reason, first_pending_window_id, state) "
            "VALUES (:id, :owner_id, :target_key, :reason, :window_id, :state)"
        ),
        {
            "id": new_id,
            "owner_id": owner_id,
            "target_key": target_key,
            "reason": reason,
            "window_id": first_pending_window_id,
            "state": STATE_PENDING,
        },
    )
    return PendingItem(
        id=new_id,
        owner_id=owner_id,
        target_key=target_key,
        reason=reason,
        first_pending_window_id=first_pending_window_id,
        state=STATE_PENDING,
    )


def abandon(connection: Connection, *, owner_id: str, target_key: str) -> bool:
    """``state = 'abandoned_by_owner'`` — an explicit Owner action and nothing else (§5.3).

    Returns whether a row moved. There is deliberately no ``reason``, no expiry parameter and
    no bulk form: every one of those would be a way for the system to abandon an item on its
    own, which §5.3 forbids in as many words.
    """
    result = connection.execute(
        text(
            "UPDATE pending_item_ledger SET state = :abandoned "
            "WHERE owner_id = :owner_id AND target_key = :target_key AND state = :pending"
        ),
        {
            "abandoned": STATE_ABANDONED,
            "owner_id": owner_id,
            "target_key": target_key,
            "pending": STATE_PENDING,
        },
    )
    return bool(result.rowcount)


# --------------------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------------------


def open_item(connection: Connection, *, owner_id: str, target_key: str) -> PendingItem | None:
    record = connection.execute(
        text(
            f"SELECT {_COLUMNS} FROM pending_item_ledger "
            "WHERE owner_id = :owner_id AND target_key = :target_key AND state = :pending"
        ),
        {"owner_id": owner_id, "target_key": target_key, "pending": STATE_PENDING},
    ).fetchone()
    return None if record is None else _item(record)


def carried_forward(connection: Connection, *, owner_id: str) -> list[PendingItem]:
    """Every open pending row — the set the next period unions into its candidates (§2).

    Deliberately **not** filtered by any window or timestamp. Filtering here by the current
    coverage window is precisely the defect ``I06`` names, and it would be invisible: the
    query would still return rows, just never the ones that have fallen behind the cursor.
    """
    result = connection.execute(
        text(
            f"SELECT {_COLUMNS} FROM pending_item_ledger "
            "WHERE owner_id = :owner_id AND state = :pending ORDER BY id"
        ),
        {"owner_id": owner_id, "pending": STATE_PENDING},
    ).fetchall()
    return [_item(record) for record in result]


def count_by_state(connection: Connection, *, owner_id: str, state: str) -> int:
    result = connection.execute(
        text(
            "SELECT COUNT(*) FROM pending_item_ledger "
            "WHERE owner_id = :owner_id AND state = :state"
        ),
        {"owner_id": owner_id, "state": state},
    )
    return int(result.scalar_one())


def count_total(connection: Connection, *, owner_id: str) -> int:
    result = connection.execute(
        text("SELECT COUNT(*) FROM pending_item_ledger WHERE owner_id = :owner_id"),
        {"owner_id": owner_id},
    )
    return int(result.scalar_one())


def quality_for_window(connection: Connection, *, owner_id: str, coverage_window_id: str) -> str:
    """O-5.3: ``complete`` only when this window opened no still-pending row.

    The condition is on ``first_pending_window_id``, not on "any pending row anywhere": an
    item that has been pending since an earlier period does not make *this* period incomplete
    — it made incomplete the period that first missed it, and it arrives here as a late
    discovery.
    """
    result = connection.execute(
        text(
            "SELECT COUNT(*) FROM pending_item_ledger WHERE owner_id = :owner_id "
            "AND state = :pending AND first_pending_window_id = :window_id"
        ),
        {"owner_id": owner_id, "pending": STATE_PENDING, "window_id": coverage_window_id},
    )
    return QUALITY_PARTIAL if int(result.scalar_one()) else QUALITY_COMPLETE


# --------------------------------------------------------------------------------------
# The port the analysis service has been holding as None
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ConnectionBoundPendingLedger:
    """``PendingLedgerPort`` for a caller that already has its transaction open.

    This is the shape the contract wants: the pending row commits with whatever the caller is
    committing, so a rollback cannot leave the two disagreeing. Prefer it wherever the caller
    can build one per transaction; :class:`EngineBoundPendingLedger` with an explicit
    ``connection=`` argument is the same guarantee for a caller that holds one long-lived port
    object instead.
    """

    connection: Connection
    owner_id: str
    first_pending_window_id: str
    id_factory: Callable[[], str]

    def record_pending(
        self, *, target_key: str, reason: str, connection: Connection | None = None
    ) -> None:
        record_pending(
            connection if connection is not None else self.connection,
            owner_id=self.owner_id,
            target_key=target_key,
            reason=reason,
            first_pending_window_id=self.first_pending_window_id,
            new_id=self.id_factory(),
        )


@dataclass(frozen=True)
class EngineBoundPendingLedger:
    """``PendingLedgerPort`` for ``server.app.analysis.service``.

    **Pass ``connection`` whenever you have one.** ``record_pending`` takes an optional
    ``connection``; when it is given, the pending row is written on that connection and
    therefore inside the caller's transaction — it commits and rolls back with the analysis
    write, which is what ``B04``/``B17`` mean by "the item also has to reach the ledger".

    ``CR-TC-BACKFILL-02``, measured rather than predicted. The port originally passed no
    connection and this adapter had to open its own. ``service._fail_task`` calls it from
    *inside* an open ``TXN-analysis-*`` write transaction, and on SQLite the outer transaction
    holds RESERVED, so the second connection's INSERT waits out ``busy_timeout`` and dies
    ``database is locked`` — W3B measured 0.00 s outside a transaction against 5.01 s to
    failure inside one. A retry cannot fix that: the lock is held by the very transaction the
    caller is still inside, so waiting longer only fails later.

    The engine-bound fallback is kept for the standalone case — a caller that genuinely has no
    transaction open, such as a maintenance path or a test — and its behaviour is unchanged.
    It is a fallback and not the recommended path: when it is used from inside somebody's
    transaction the row also commits **separately**, so an analysis rollback can leave a
    pending row behind. That is the safe direction (a spurious pending row is visible and the
    Owner can abandon it, while the reverse is the silent loss ``I06`` forbids), but it is
    still not what the contract asks for.

    ``window_provider`` supplies ``first_pending_window_id``, which the port also omits and
    which the column requires NOT NULL. It raises rather than inventing a window when there is
    none: an analysis failure before any coverage window exists is a state nobody has defined,
    and guessing one would point a ledger row at the wrong period forever. The provider is
    consulted **before** the connection is chosen, so the refusal costs no lock either way.
    """

    engine: Engine
    owner_id: str
    window_provider: Callable[[], str | None]
    id_factory: Callable[[], str]

    def record_pending(
        self, *, target_key: str, reason: str, connection: Connection | None = None
    ) -> None:
        window_id = self.window_provider()
        if window_id is None:
            raise PendingLedgerError(
                ErrorCode.VALIDATION_ERROR,
                "no coverage window exists to anchor a pending item",
                field_path="first_pending_window_id",
                violation_kind="required_missing",
            )
        if connection is not None:
            record_pending(
                connection,
                owner_id=self.owner_id,
                target_key=target_key,
                reason=reason,
                first_pending_window_id=window_id,
                new_id=self.id_factory(),
            )
            return
        with self.engine.begin() as own_connection:
            record_pending(
                own_connection,
                owner_id=self.owner_id,
                target_key=target_key,
                reason=reason,
                first_pending_window_id=window_id,
                new_id=self.id_factory(),
            )


def current_window_provider(engine: Engine, owner_id: str) -> Callable[[], str | None]:
    """The newest ``coverage_window`` id, or ``None`` before the first publish.

    Reads ``coverage_window`` through one statement rather than importing
    ``CoverageRepository``, so this module has no import edge into the coverage half of the
    package; the table itself is ``MOD-report-service``'s, which is this module's own module.
    """

    def provider() -> str | None:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT id FROM coverage_window WHERE owner_id = :owner_id "
                    'ORDER BY "sequence" DESC LIMIT 1'
                ),
                {"owner_id": owner_id},
            ).fetchone()
        return None if row is None else str(row[0])

    return provider
