"""Delivery tables for ``TC-telegram-unknown-delivery`` (``MOD-delivery-service``).

Revision ID: 0009_tc_telegram_unknown_delivery
Revises: 0008_tc_saved_snapshot
Create Date: 2026-09-08

Five tables, and exactly the five that ``contracts/data/entities.yaml`` marks
``owner_module: MOD-delivery-service``: ``outbox_intent`` (``ENT-outbox-intent``),
``delivery`` (``ENT-delivery``), ``delivery_part`` (``ENT-delivery-part``),
``delivery_attempt`` (``ENT-delivery-attempt``) and ``delivery_receipt``
(``ENT-delivery-receipt``). Column names, types, nullability, enums, UNIQUE keys and the
partial index all come from those entries.

``delivery.report_id`` carries no ``REFERENCES`` clause
-------------------------------------------------------
``entities.yaml`` requires ``delivery.report_id -> report(id)``, and ``report`` belongs to
``TC-report-coverage-publish-cas``, which has not landed. SQLite rejects every INSERT into a
table whose foreign key names a missing table, so a clause here would make the whole module
unusable until that card ships. The precedent is ``0002b_shared_move_set_tables``, which
kept ``analysis.analysis_generation_id`` as a plain column for the same reason: the column
keeps its name, type and NOT NULL, and the reference is added by the revision that owns the
referenced table. ``CR-TC-DELIVERY-08`` carries that request forward.

``ux_outbox_alert_per_run``
---------------------------
Partial UNIQUE on ``(owner_id, intent_type, subject_ref) WHERE intent_type =
'telegram_alert'``. This index **is** ``REQ-AC04``: a second ``worker.report_stop`` for the
same run cannot create a second alert intent, because the database refuses it -- not because
a code path remembers to check.

``delivery_attempt.outcome`` is NOT NULL, and starts at ``unknown``
-------------------------------------------------------------------
``entities.yaml`` declares the column NOT NULL over
``sent | retryable_error | permanent_error | unknown``, while the attempt row must be
committed *before* the network call, when the outcome is by definition not yet known. The
two are reconciled by writing ``unknown`` at INSERT: that is what "we do not know" means, and
it makes a crash between COMMIT and any response leave the correct value already stored
rather than a NULL a later reader could mistake for "never attempted". See
``CR-TC-DELIVERY-01``.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0009_tc_telegram_unknown_delivery"
down_revision: str | None = "0008_tc_saved_snapshot"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §conventions).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

#: ``entities.yaml`` §conventions/hashes: ``sha256:`` + 64 lowercase hex -- 71 characters
#: in total. The GLOB pins the prefix and the alphabet; the length pins the digest size.
_SHA256_CHECK = "{col} GLOB 'sha256:*' AND length({col}) = 71"

_STATEMENTS: tuple[str, ...] = (
    # -- outbox_intent (ENT-outbox-intent) ---------------------------------------------
    f"""
    CREATE TABLE outbox_intent (
        id                        TEXT NOT NULL PRIMARY KEY,
        owner_id                  TEXT NOT NULL REFERENCES owner (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        intent_type               TEXT NOT NULL
                                       CHECK (intent_type IN
                                              ('telegram_digest', 'telegram_alert')),
        subject_ref               TEXT NOT NULL,
        created_in_transaction_at TEXT NOT NULL
                                       CHECK (created_in_transaction_at
                                              GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        dispatch_state            TEXT NOT NULL
                                       CHECK (dispatch_state IN
                                              ('ready', 'claimed', 'done', 'held_for_review')),
        restore_generation        INTEGER NOT NULL CHECK (restore_generation >= 0),

        CHECK (length(id) = 26)
    )
    """,
    # REQ-AC04, enforced by the database rather than by a code path that must remember.
    """
    CREATE UNIQUE INDEX ux_outbox_alert_per_run ON outbox_intent
        (owner_id, intent_type, subject_ref)
        WHERE intent_type = 'telegram_alert'
    """,
    """
    CREATE INDEX ix_outbox_ready ON outbox_intent
        (owner_id, restore_generation, created_in_transaction_at)
        WHERE dispatch_state = 'ready'
    """,
    # -- delivery (ENT-delivery) --------------------------------------------------------
    f"""
    CREATE TABLE delivery (
        id                       TEXT NOT NULL PRIMARY KEY,
        owner_id                 TEXT NOT NULL REFERENCES owner (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        report_id                TEXT NOT NULL,
        channel                  TEXT NOT NULL CHECK (channel IN ('telegram')),
        state                    TEXT NOT NULL
                                      CHECK (state IN ('pending', 'sending', 'sent',
                                                       'retry_wait', 'unknown', 'failed',
                                                       'cancelled')),
        attempt_count            INTEGER NOT NULL CHECK (attempt_count >= 0),
        telegram_link_generation INTEGER NOT NULL CHECK (telegram_link_generation >= 0),
        created_at               TEXT NOT NULL
                                      CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        updated_at               TEXT NOT NULL
                                      CHECK (updated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_delivery_report_channel_generation ON delivery
        (owner_id, report_id, channel, telegram_link_generation)
    """,
    # -- delivery_part (ENT-delivery-part) ----------------------------------------------
    #
    # The CHECK on `provider_message_id` is invariant AMD-B03 point 3 written as a
    # constraint: `sent` is the only state that may carry a message id, so a code path that
    # tried to record a receipt for an `unknown` part would be refused by the database.
    f"""
    CREATE TABLE delivery_part (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        delivery_id         TEXT NOT NULL REFERENCES delivery (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        part_index          INTEGER NOT NULL CHECK (part_index >= 0),
        payload_hash        TEXT NOT NULL
                                 CHECK ({_SHA256_CHECK.format(col='payload_hash')}),
        state               TEXT NOT NULL
                                 CHECK (state IN ('pending', 'sending', 'sent',
                                                  'unknown', 'failed')),
        provider_message_id TEXT NULL,
        created_at          TEXT NOT NULL
                                 CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        updated_at          TEXT NOT NULL
                                 CHECK (updated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26),
        CHECK (provider_message_id IS NULL OR state = 'sent')
    )
    """,
    """
    CREATE UNIQUE INDEX ux_delivery_part_index ON delivery_part
        (owner_id, delivery_id, part_index)
    """,
    # -- delivery_attempt (ENT-delivery-attempt) ----------------------------------------
    f"""
    CREATE TABLE delivery_attempt (
        id               TEXT NOT NULL PRIMARY KEY,
        owner_id         TEXT NOT NULL REFERENCES owner (id)
                              ON DELETE RESTRICT ON UPDATE RESTRICT,
        delivery_id      TEXT NOT NULL REFERENCES delivery (id)
                              ON DELETE RESTRICT ON UPDATE RESTRICT,
        delivery_part_id TEXT NULL REFERENCES delivery_part (id)
                              ON DELETE RESTRICT ON UPDATE RESTRICT,
        attempt_number   INTEGER NOT NULL CHECK (attempt_number >= 1),
        started_at       TEXT NOT NULL CHECK (started_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        outcome          TEXT NOT NULL
                              CHECK (outcome IN ('sent', 'retryable_error',
                                                 'permanent_error', 'unknown')),
        error_code       TEXT NULL,

        CHECK (length(id) = 26)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_delivery_attempt_number ON delivery_attempt
        (owner_id, delivery_id, delivery_part_id, attempt_number)
    """,
    # -- delivery_receipt (ENT-delivery-receipt) ----------------------------------------
    #
    # One receipt per attempt. It does NOT prove exactly-once outside the system: Telegram
    # takes no client idempotency key (SRC-PLAN §3.1), and an attempt in `unknown` has no
    # receipt -- a missing receipt does not mean nothing was sent.
    f"""
    CREATE TABLE delivery_receipt (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        delivery_attempt_id TEXT NOT NULL REFERENCES delivery_attempt (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        provider_message_id TEXT NOT NULL,
        received_at         TEXT NOT NULL
                                 CHECK (received_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        payload_hash        TEXT NOT NULL
                                 CHECK ({_SHA256_CHECK.format(col='payload_hash')}),

        CHECK (length(id) = 26)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_delivery_receipt_attempt ON delivery_receipt
        (owner_id, delivery_attempt_id)
    """,
)

#: Reverse dependency order, so the drops succeed with foreign keys on.
_DROPS: tuple[str, ...] = (
    "DROP TABLE IF EXISTS delivery_receipt",
    "DROP TABLE IF EXISTS delivery_attempt",
    "DROP TABLE IF EXISTS delivery_part",
    "DROP TABLE IF EXISTS delivery",
    "DROP TABLE IF EXISTS outbox_intent",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drops only what this revision created."""
    for statement in _DROPS:
        op.execute(statement)
