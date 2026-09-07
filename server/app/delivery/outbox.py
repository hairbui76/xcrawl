"""Committed outbox intents, the delivery/part/attempt/receipt rows, and the sender lease.

Repository port for ``MOD-delivery-service``. Exactly the five tables
``contracts/data/entities.yaml`` marks ``owner_module: MOD-delivery-service`` are touched
here: ``outbox_intent``, ``delivery``, ``delivery_part``, ``delivery_attempt``,
``delivery_receipt``. Nothing in this file reads or writes ``report``, ``run``,
``telegram_link``, ``owner`` or any other module's table -- those arrive through ports on
:mod:`server.app.delivery.service`, which is what ``contracts/modules.yaml``'s default deny
means in code rather than in prose.

Every method takes an already-open :class:`~sqlalchemy.Connection` and never commits. The
transaction boundaries are contract facts (``T-DL-00`` commits the intent *with the source
content*; ``T-DL-01`` commits the attempt row *before* the network call) and they are named
in :mod:`server.app.delivery.service`, where the commit point can be read next to the send.

SQLAlchemy 2 Core with explicit SQL per ADR-0011, matching the DDL in
``server/migrations/versions/0009_tc_telegram_unknown_delivery.py``.

The sender lease
----------------
``contracts/state/delivery.yaml`` §sender_lease requires that only one process moves a part
to ``sending``, with the same epoch/fencing rule as ``assignment_lease`` and a TTL from
``contracts/retry-policy.yaml`` (``delivery_sender_lease_ttl`` = 120 s). ``entities.yaml``
declares **no** table or column for it: the only durable claim it offers is
``outbox_intent.dispatch_state`` (``ready | claimed | done | held_for_review``). So
exclusivity here is the compare-and-set on that column -- one UPDATE, one winner, decided by
the database -- and :class:`SenderLease` carries the holder, epoch and expiry that make a
late writer detectable (``STALE_LEASE``). A durable cross-process lease record would need a
new entity, which is change control's business and not this card's (``SG-EDGE``); see
``CR-TC-DELIVERY-03`` in the handoff.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from rr_contracts.generated.states import (
    DeliveryIntentKind,
    DeliveryPartState,
    DeliveryState,
)
from sqlalchemy import Connection, text

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: ``contracts/retry-policy.yaml`` §budgets ``delivery_sender_lease_ttl`` (120 s,
#: ``PROVISIONAL`` there -- "not yet calibrated", not "not yet approved").
SENDER_LEASE_TTL_SECONDS = 120

#: ``entities.yaml`` ``ENT-outbox-intent.intent_type`` spells the two kinds
#: ``telegram_digest | telegram_alert``; ``contracts/state/delivery.yaml`` §enums and
#: ``contracts/ports.yaml`` ``delivery.create_intent`` spell the same two
#: ``report_digest | run_alert``. Storing the column's vocabulary and mapping at the edge
#: keeps both contracts satisfied without either being rewritten (``CR-TC-DELIVERY-05``).
INTENT_TYPE_OF_KIND: dict[DeliveryIntentKind, str] = {
    DeliveryIntentKind.REPORT_DIGEST: "telegram_digest",
    DeliveryIntentKind.RUN_ALERT: "telegram_alert",
}


def new_ulid() -> str:
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions/id_type)."""
    timestamp = int(time.time() * 1000)
    randomness = int.from_bytes(os.urandom(10), "big")
    value = (timestamp << 80) | randomness
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def rfc3339(moment: datetime) -> str:
    """UTC RFC 3339 with millisecond precision -- the only shape the CHECKs accept."""
    return moment.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_rfc3339(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")


# --------------------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class OutboxIntentRow:
    """``ENT-outbox-intent``."""

    id: str
    owner_id: str
    intent_type: str
    subject_ref: dict[str, Any]
    created_in_transaction_at: str
    dispatch_state: str
    restore_generation: int


@dataclass(frozen=True)
class DeliveryRow:
    """``ENT-delivery``. ``state`` is stored but derived (``DP-03``)."""

    id: str
    owner_id: str
    report_id: str
    channel: str
    state: DeliveryState
    attempt_count: int
    telegram_link_generation: int
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class DeliveryPartRow:
    """``ENT-delivery-part``."""

    id: str
    owner_id: str
    delivery_id: str
    part_index: int
    payload_hash: str
    state: DeliveryPartState
    provider_message_id: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class DeliveryAttemptRow:
    """``ENT-delivery-attempt`` -- the row that must exist *before* the network call."""

    id: str
    owner_id: str
    delivery_id: str
    delivery_part_id: str | None
    attempt_number: int
    started_at: str
    outcome: str
    error_code: str | None


@dataclass(frozen=True)
class SenderLease:
    """Holder, epoch and expiry for one claimed intent (``sender_lease`` §epoch_rule_vi).

    ``epoch`` is monotonic per delivery: every claim increments it, so a writer holding an
    older epoch is detectably stale even if its wall clock disagrees about the TTL.
    """

    delivery_id: str
    intent_id: str
    holder: str
    epoch: int
    expires_at: datetime

    def expired(self, now: datetime) -> bool:
        return now >= self.expires_at


class SenderLeaseRegistry:
    """Epoch bookkeeping for sender leases, held in process memory.

    Durable exclusivity comes from :meth:`DeliveryRepository.claim_intent`'s compare-and-set;
    this registry adds the fencing token that turns "a second writer exists" into
    ``STALE_LEASE`` rather than a silent double send. One registry per process, like
    :class:`~server.app.storage.guard.StorageGuard`.
    """

    def __init__(self, *, ttl_seconds: int = SENDER_LEASE_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._epochs: dict[str, int] = {}

    def issue(self, *, delivery_id: str, intent_id: str, holder: str, now: datetime) -> SenderLease:
        epoch = self._epochs.get(delivery_id, 0) + 1
        self._epochs[delivery_id] = epoch
        return SenderLease(
            delivery_id=delivery_id,
            intent_id=intent_id,
            holder=holder,
            epoch=epoch,
            expires_at=now + timedelta(seconds=self._ttl),
        )

    def current_epoch(self, delivery_id: str) -> int:
        return self._epochs.get(delivery_id, 0)

    def is_current(self, lease: SenderLease, *, now: datetime) -> bool:
        """A lease may write only while it is both the newest epoch and unexpired."""
        return not lease.expired(now) and self._epochs.get(lease.delivery_id) == lease.epoch


# --------------------------------------------------------------------------------------
# Repository
# --------------------------------------------------------------------------------------


class DeliveryRepository:
    """SQL for the five delivery-owned tables. No transaction control, no network."""

    # -- outbox ------------------------------------------------------------------------

    def insert_intent(
        self,
        connection: Connection,
        *,
        owner_id: str,
        kind: DeliveryIntentKind,
        subject_ref: dict[str, Any],
        restore_generation: int,
        now: datetime,
    ) -> OutboxIntentRow:
        row = OutboxIntentRow(
            id=new_ulid(),
            owner_id=owner_id,
            intent_type=INTENT_TYPE_OF_KIND[kind],
            subject_ref=subject_ref,
            created_in_transaction_at=rfc3339(now),
            dispatch_state="ready",
            restore_generation=restore_generation,
        )
        connection.execute(
            text(
                "INSERT INTO outbox_intent (id, owner_id, intent_type, subject_ref, "
                "created_in_transaction_at, dispatch_state, restore_generation) VALUES "
                "(:id, :owner_id, :intent_type, :subject_ref, :created, :dispatch_state, :gen)"
            ),
            {
                "id": row.id,
                "owner_id": row.owner_id,
                "intent_type": row.intent_type,
                "subject_ref": json.dumps(row.subject_ref, sort_keys=True),
                "created": row.created_in_transaction_at,
                "dispatch_state": row.dispatch_state,
                "gen": row.restore_generation,
            },
        )
        return row

    def find_intent_for_subject(
        self, connection: Connection, *, owner_id: str, intent_type: str, subject_ref: str
    ) -> OutboxIntentRow | None:
        result = connection.execute(
            text(
                "SELECT id, owner_id, intent_type, subject_ref, created_in_transaction_at, "
                "dispatch_state, restore_generation FROM outbox_intent WHERE owner_id = :o "
                "AND intent_type = :t AND subject_ref = :s"
            ),
            {"o": owner_id, "t": intent_type, "s": subject_ref},
        ).mappings()
        row = result.first()
        return None if row is None else _intent_row(row)

    def claim_intent(
        self, connection: Connection, *, owner_id: str, restore_generation: int
    ) -> OutboxIntentRow | None:
        """Compare-and-set one ``ready`` intent to ``claimed``; ``None`` if there is none.

        The generation filter is ``I15``'s positive form: fixtures
        ``recovery/a`` and ``recovery/m`` both require that an intent carrying an older
        ``restore_generation`` is *not eligible*, even after the dispatcher is unlocked --
        unlocking dispatch is not permission to replay history.

        Only one caller can win the UPDATE, which is the durable half of the sender lease.
        """
        candidate = connection.execute(
            text(
                "SELECT id FROM outbox_intent WHERE owner_id = :o AND dispatch_state = 'ready' "
                "AND restore_generation = :g ORDER BY created_in_transaction_at, id LIMIT 1"
            ),
            {"o": owner_id, "g": restore_generation},
        ).scalar()
        if candidate is None:
            return None
        updated = connection.execute(
            text(
                "UPDATE outbox_intent SET dispatch_state = 'claimed' "
                "WHERE id = :id AND dispatch_state = 'ready'"
            ),
            {"id": candidate},
        )
        if updated.rowcount != 1:
            return None
        return self.get_intent(connection, intent_id=str(candidate))

    def get_intent(self, connection: Connection, *, intent_id: str) -> OutboxIntentRow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, intent_type, subject_ref, created_in_transaction_at, "
                    "dispatch_state, restore_generation FROM outbox_intent WHERE id = :id"
                ),
                {"id": intent_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _intent_row(row)

    def set_intent_dispatch_state(
        self, connection: Connection, *, intent_id: str, dispatch_state: str
    ) -> None:
        connection.execute(
            text("UPDATE outbox_intent SET dispatch_state = :s WHERE id = :id"),
            {"s": dispatch_state, "id": intent_id},
        )

    def count_intents(self, connection: Connection, *, owner_id: str, intent_type: str) -> int:
        return int(
            connection.execute(
                text("SELECT COUNT(*) FROM outbox_intent WHERE owner_id = :o AND intent_type = :t"),
                {"o": owner_id, "t": intent_type},
            ).scalar_one()
        )

    # -- delivery ----------------------------------------------------------------------

    def insert_delivery(
        self,
        connection: Connection,
        *,
        owner_id: str,
        report_id: str,
        channel: str,
        telegram_link_generation: int,
        now: datetime,
    ) -> DeliveryRow:
        stamp = rfc3339(now)
        row = DeliveryRow(
            id=new_ulid(),
            owner_id=owner_id,
            report_id=report_id,
            channel=channel,
            state=DeliveryState.PENDING,
            attempt_count=0,
            telegram_link_generation=telegram_link_generation,
            created_at=stamp,
            updated_at=stamp,
        )
        connection.execute(
            text(
                "INSERT INTO delivery (id, owner_id, report_id, channel, state, attempt_count, "
                "telegram_link_generation, created_at, updated_at) VALUES "
                "(:id, :owner_id, :report_id, :channel, :state, 0, :gen, :created, :updated)"
            ),
            {
                "id": row.id,
                "owner_id": row.owner_id,
                "report_id": row.report_id,
                "channel": row.channel,
                "state": row.state.value,
                "gen": row.telegram_link_generation,
                "created": row.created_at,
                "updated": row.updated_at,
            },
        )
        return row

    def get_delivery(self, connection: Connection, *, delivery_id: str) -> DeliveryRow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, report_id, channel, state, attempt_count, "
                    "telegram_link_generation, created_at, updated_at FROM delivery WHERE id = :id"
                ),
                {"id": delivery_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _delivery_row(row)

    def find_delivery(
        self,
        connection: Connection,
        *,
        owner_id: str,
        report_id: str,
        channel: str,
        telegram_link_generation: int,
    ) -> DeliveryRow | None:
        """The ``logical_delivery_key`` lookup: one delivery per report/channel/generation."""
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, report_id, channel, state, attempt_count, "
                    "telegram_link_generation, created_at, updated_at FROM delivery "
                    "WHERE owner_id = :o AND report_id = :r AND channel = :c "
                    "AND telegram_link_generation = :g"
                ),
                {"o": owner_id, "r": report_id, "c": channel, "g": telegram_link_generation},
            )
            .mappings()
            .first()
        )
        return None if row is None else _delivery_row(row)

    def find_delivery_for_report(
        self, connection: Connection, *, owner_id: str, report_id: str, channel: str = "telegram"
    ) -> DeliveryRow | None:
        """The delivery an outbox intent points at, whatever generation it captured.

        The dispatcher looks a delivery up by its *subject*, not by the current link
        generation: ``T-DL-08`` is precisely the comparison between the generation this row
        captured and the one in force now, so keying the lookup on the current generation
        would make the mismatch invisible.
        """
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, report_id, channel, state, attempt_count, "
                    "telegram_link_generation, created_at, updated_at FROM delivery "
                    "WHERE owner_id = :o AND report_id = :r AND channel = :c "
                    "ORDER BY created_at DESC, id DESC LIMIT 1"
                ),
                {"o": owner_id, "r": report_id, "c": channel},
            )
            .mappings()
            .first()
        )
        return None if row is None else _delivery_row(row)

    def set_delivery_state(
        self, connection: Connection, *, delivery_id: str, state: DeliveryState, now: datetime
    ) -> None:
        connection.execute(
            text("UPDATE delivery SET state = :s, updated_at = :u WHERE id = :id"),
            {"s": state.value, "u": rfc3339(now), "id": delivery_id},
        )

    def bump_attempt_count(
        self, connection: Connection, *, delivery_id: str, now: datetime
    ) -> None:
        connection.execute(
            text(
                "UPDATE delivery SET attempt_count = attempt_count + 1, updated_at = :u "
                "WHERE id = :id"
            ),
            {"u": rfc3339(now), "id": delivery_id},
        )

    # -- parts -------------------------------------------------------------------------

    def insert_part(
        self,
        connection: Connection,
        *,
        owner_id: str,
        delivery_id: str,
        part_index: int,
        payload_hash: str,
        now: datetime,
    ) -> DeliveryPartRow:
        stamp = rfc3339(now)
        row = DeliveryPartRow(
            id=new_ulid(),
            owner_id=owner_id,
            delivery_id=delivery_id,
            part_index=part_index,
            payload_hash=payload_hash,
            state=DeliveryPartState.PENDING,
            provider_message_id=None,
            created_at=stamp,
            updated_at=stamp,
        )
        connection.execute(
            text(
                "INSERT INTO delivery_part (id, owner_id, delivery_id, part_index, payload_hash, "
                "state, provider_message_id, created_at, updated_at) VALUES "
                "(:id, :owner_id, :delivery_id, :ix, :hash, :state, NULL, :created, :updated)"
            ),
            {
                "id": row.id,
                "owner_id": row.owner_id,
                "delivery_id": row.delivery_id,
                "ix": row.part_index,
                "hash": row.payload_hash,
                "state": row.state.value,
                "created": row.created_at,
                "updated": row.updated_at,
            },
        )
        return row

    def list_parts(self, connection: Connection, *, delivery_id: str) -> list[DeliveryPartRow]:
        rows = (
            connection.execute(
                text(
                    "SELECT id, owner_id, delivery_id, part_index, payload_hash, state, "
                    "provider_message_id, created_at, updated_at FROM delivery_part "
                    "WHERE delivery_id = :d ORDER BY part_index"
                ),
                {"d": delivery_id},
            )
            .mappings()
            .all()
        )
        return [_part_row(row) for row in rows]

    def get_part(self, connection: Connection, *, part_id: str) -> DeliveryPartRow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, delivery_id, part_index, payload_hash, state, "
                    "provider_message_id, created_at, updated_at FROM delivery_part WHERE id = :id"
                ),
                {"id": part_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _part_row(row)

    def set_part_state(
        self,
        connection: Connection,
        *,
        part_id: str,
        state: DeliveryPartState,
        provider_message_id: str | None,
        now: datetime,
    ) -> None:
        """Set part state. ``provider_message_id`` is written only with ``sent``.

        ``entities.yaml`` ``ENT-delivery-part.provider_message_id`` says NULL for every state
        but ``sent``, and fixture ``telegram/b`` forbids writing one when nothing came back.
        Passing the id in with any other state is a programming error, so it is asserted
        rather than quietly dropped.
        """
        if provider_message_id is not None and state is not DeliveryPartState.SENT:
            raise AssertionError(
                "provider_message_id may only accompany state 'sent' "
                "(entities.yaml ENT-delivery-part.provider_message_id)"
            )
        connection.execute(
            text(
                "UPDATE delivery_part SET state = :s, provider_message_id = :m, updated_at = :u "
                "WHERE id = :id"
            ),
            {"s": state.value, "m": provider_message_id, "u": rfc3339(now), "id": part_id},
        )

    # -- attempts and receipts ---------------------------------------------------------

    def next_attempt_number(self, connection: Connection, *, part_id: str) -> int:
        current = connection.execute(
            text("SELECT MAX(attempt_number) FROM delivery_attempt WHERE delivery_part_id = :p"),
            {"p": part_id},
        ).scalar()
        return 1 if current is None else int(current) + 1

    def insert_attempt(
        self,
        connection: Connection,
        *,
        owner_id: str,
        delivery_id: str,
        part_id: str,
        attempt_number: int,
        now: datetime,
    ) -> DeliveryAttemptRow:
        """The row ``T-DL-01`` commits **before** the network call.

        It is born with ``outcome = 'unknown'``. ``entities.yaml`` declares the column NOT
        NULL over ``sent | retryable_error | permanent_error | unknown``, and "we do not know
        yet" is exactly what ``unknown`` means -- so a crash between this INSERT and any
        result leaves the truth already written, instead of a NULL that a later reader could
        mistake for "never attempted". See ``CR-TC-DELIVERY-01``.
        """
        row = DeliveryAttemptRow(
            id=new_ulid(),
            owner_id=owner_id,
            delivery_id=delivery_id,
            delivery_part_id=part_id,
            attempt_number=attempt_number,
            started_at=rfc3339(now),
            outcome="unknown",
            error_code=None,
        )
        connection.execute(
            text(
                "INSERT INTO delivery_attempt (id, owner_id, delivery_id, delivery_part_id, "
                "attempt_number, started_at, outcome, error_code) VALUES "
                "(:id, :owner_id, :delivery_id, :part_id, :n, :started, :outcome, NULL)"
            ),
            {
                "id": row.id,
                "owner_id": row.owner_id,
                "delivery_id": row.delivery_id,
                "part_id": row.delivery_part_id,
                "n": row.attempt_number,
                "started": row.started_at,
                "outcome": row.outcome,
            },
        )
        return row

    def set_attempt_outcome(
        self,
        connection: Connection,
        *,
        attempt_id: str,
        outcome: str,
        error_code: str | None,
    ) -> None:
        connection.execute(
            text("UPDATE delivery_attempt SET outcome = :o, error_code = :e WHERE id = :id"),
            {"o": outcome, "e": error_code, "id": attempt_id},
        )

    def get_attempt(
        self, connection: Connection, *, part_id: str, attempt_number: int
    ) -> DeliveryAttemptRow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, delivery_id, delivery_part_id, attempt_number, "
                    "started_at, outcome, error_code FROM delivery_attempt "
                    "WHERE delivery_part_id = :p AND attempt_number = :n"
                ),
                {"p": part_id, "n": attempt_number},
            )
            .mappings()
            .first()
        )
        return None if row is None else _attempt_row(row)

    def list_attempts(
        self, connection: Connection, *, delivery_id: str
    ) -> list[DeliveryAttemptRow]:
        rows = (
            connection.execute(
                text(
                    "SELECT id, owner_id, delivery_id, delivery_part_id, attempt_number, "
                    "started_at, outcome, error_code FROM delivery_attempt "
                    "WHERE delivery_id = :d ORDER BY started_at, attempt_number"
                ),
                {"d": delivery_id},
            )
            .mappings()
            .all()
        )
        return [_attempt_row(row) for row in rows]

    def insert_receipt(
        self,
        connection: Connection,
        *,
        owner_id: str,
        attempt_id: str,
        provider_message_id: str,
        payload_hash: str,
        now: datetime,
    ) -> str:
        receipt_id = new_ulid()
        connection.execute(
            text(
                "INSERT INTO delivery_receipt (id, owner_id, delivery_attempt_id, "
                "provider_message_id, received_at, payload_hash) VALUES "
                "(:id, :owner_id, :attempt_id, :message_id, :received, :hash)"
            ),
            {
                "id": receipt_id,
                "owner_id": owner_id,
                "attempt_id": attempt_id,
                "message_id": provider_message_id,
                "received": rfc3339(now),
                "hash": payload_hash,
            },
        )
        return receipt_id

    def find_receipt_for_part(
        self, connection: Connection, *, part_id: str
    ) -> dict[str, Any] | None:
        """The stored receipt of a ``sent`` part, or ``None``.

        ``T-DL-02``: a later dispatch of a part that already has one must *return* it and
        open no connection. This lookup is how the service can tell.
        """
        row = (
            connection.execute(
                text(
                    "SELECT r.id AS id, r.provider_message_id AS provider_message_id, "
                    "r.received_at AS received_at, r.payload_hash AS payload_hash "
                    "FROM delivery_receipt r JOIN delivery_attempt a "
                    "ON a.id = r.delivery_attempt_id WHERE a.delivery_part_id = :p "
                    "ORDER BY r.received_at LIMIT 1"
                ),
                {"p": part_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else dict(row)


def _intent_row(row: Any) -> OutboxIntentRow:
    return OutboxIntentRow(
        id=row["id"],
        owner_id=row["owner_id"],
        intent_type=row["intent_type"],
        subject_ref=json.loads(row["subject_ref"]),
        created_in_transaction_at=row["created_in_transaction_at"],
        dispatch_state=row["dispatch_state"],
        restore_generation=int(row["restore_generation"]),
    )


def _delivery_row(row: Any) -> DeliveryRow:
    return DeliveryRow(
        id=row["id"],
        owner_id=row["owner_id"],
        report_id=row["report_id"],
        channel=row["channel"],
        state=DeliveryState(row["state"]),
        attempt_count=int(row["attempt_count"]),
        telegram_link_generation=int(row["telegram_link_generation"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _part_row(row: Any) -> DeliveryPartRow:
    return DeliveryPartRow(
        id=row["id"],
        owner_id=row["owner_id"],
        delivery_id=row["delivery_id"],
        part_index=int(row["part_index"]),
        payload_hash=row["payload_hash"],
        state=DeliveryPartState(row["state"]),
        provider_message_id=row["provider_message_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _attempt_row(row: Any) -> DeliveryAttemptRow:
    return DeliveryAttemptRow(
        id=row["id"],
        owner_id=row["owner_id"],
        delivery_id=row["delivery_id"],
        delivery_part_id=row["delivery_part_id"],
        attempt_number=int(row["attempt_number"]),
        started_at=row["started_at"],
        outcome=row["outcome"],
        error_code=row["error_code"],
    )


def part_states(parts: Sequence[DeliveryPartRow]) -> list[DeliveryPartState]:
    return [part.state for part in parts]
