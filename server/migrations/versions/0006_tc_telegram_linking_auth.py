"""The four tables ``MOD-telegram-adapter`` owns: link, link code, update log, link attempt.

Revision ID: 0006_tc_telegram_linking_auth
Revises: 0005_tc_research_connector_metadata
Create Date: 2026-09-08

Card: ``agent-tasks/TC-telegram-linking-auth.md`` §4 (state effects).
Source of truth: ``contracts/data/entities.yaml`` entities ``telegram_link``
(``ENT-telegram-link``), ``telegram_link_code`` (``ENT-telegram-link-code``),
``telegram_update_log`` (``ENT-telegram-update-log``) and ``telegram_link_attempt``
(``ENT-telegram-link-attempt``) -- all four ``owner_module: MOD-telegram-adapter``.

Column sets are exactly what the contract declares: six, eight, seven and six fields.
``tests/contract/test_schema_matches_entities.py`` compares both directions, so a helpful
extra column here would be a failure there rather than a convenience.

Three constraints carry rules that would otherwise live only in Python
--------------------------------------------------------------------
``ux_telegram_link_active``
    A **partial** unique index on ``owner_id`` restricted to ``state = 'active'``. This is
    what makes "exactly one link in force" (REQ-D37) a property of the database: a relink
    that forgot to revoke the previous row is rejected by the index rather than producing
    two live recipients. Revoked rows stay, so the generation history survives.

``ux_telegram_link_generation``
    ``(owner_id, generation)`` unique, total. A delivery pins the generation it was built
    for (``contracts/telegram/delivery.md`` §2); a repeated generation number would make
    that pin ambiguous.

``ux_telegram_link_code_active``
    Partial unique on ``owner_id`` where ``state = 'active'``: at most one code in force
    (entities.yaml ``guarantees``). Issuing a new code therefore has to revoke the old one
    in the same transaction, which is the behaviour ``linking.issue_link_code`` implements.

``telegram_link_attempt`` deliberately carries **no** unique key -- it is a counter, and
``ix_link_attempt_chat_window`` exists to serve the sliding-window ``COUNT`` of the B09
rate limit. entities.yaml says so in as many words ("KHÔNG phải UNIQUE").

Both hash columns are ``hash_sha256`` in the contract, so both carry the 64-lowercase-hex
CHECK. ``chat_id_hash`` is the column that keeps an unlinked stranger's chat id out of the
database: the contract's ``forbidden`` list for both log tables says the raw id must never
be stored, and a hash column with a shape CHECK is how that survives a careless caller.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_tc_telegram_linking_auth"
down_revision: str | None = "0005_tc_research_connector_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_SHA256 = "length({col}) = 64 AND {col} NOT GLOB '*[^0-9a-f]*'"

_STATEMENTS: tuple[str, ...] = (
    f"""
    CREATE TABLE telegram_link (
        id         TEXT NOT NULL PRIMARY KEY,
        owner_id   TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
        chat_id    TEXT NOT NULL,
        generation INTEGER NOT NULL,
        state      TEXT NOT NULL,
        linked_at  TEXT NOT NULL,

        CHECK (length(id) = 26),
        CHECK (generation >= 1),
        CHECK (state IN ('active', 'revoked')),
        CHECK (linked_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
    )
    """,
    # REQ-D37: one link in force. Partial, so revoked generations may accumulate.
    """
    CREATE UNIQUE INDEX ux_telegram_link_active
        ON telegram_link (owner_id) WHERE state = 'active'
    """,
    """
    CREATE UNIQUE INDEX ux_telegram_link_generation
        ON telegram_link (owner_id, generation)
    """,
    f"""
    CREATE TABLE telegram_link_code (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
        code_hash           TEXT NOT NULL,
        issued_at           TEXT NOT NULL,
        expires_at          TEXT NOT NULL,
        consumed_at         TEXT NULL,
        consumed_by_chat_id TEXT NULL,
        state               TEXT NOT NULL,

        CHECK (length(id) = 26),
        -- entities.yaml: "Hash của mã; KHÔNG lưu mã gốc." The shape CHECK is what stops a
        -- caller storing the code itself in this column by accident.
        CHECK ({_SHA256.format(col='code_hash')}),
        CHECK (state IN ('active', 'consumed', 'expired', 'revoked')),
        CHECK (issued_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        CHECK (expires_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        CHECK (consumed_at IS NULL OR consumed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        -- "dùng MỘT lần": the consumed state and its timestamp move together, so a row can
        -- never claim to be spent without recording when.
        CHECK ((state = 'consumed') = (consumed_at IS NOT NULL))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_telegram_link_code_active
        ON telegram_link_code (owner_id) WHERE state = 'active'
    """,
    f"""
    CREATE TABLE telegram_update_log (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
        provider_update_id  TEXT NOT NULL,
        received_at         TEXT NOT NULL,
        chat_id_hash        TEXT NOT NULL,
        disposition         TEXT NOT NULL,
        command             TEXT NULL,

        CHECK (length(id) = 26),
        CHECK ({_SHA256.format(col='chat_id_hash')}),
        CHECK (disposition IN
               ('executed', 'dropped_unlinked', 'dropped_invalid', 'link_code_attempt')),
        -- entities.yaml: "Chỉ 3 lệnh của REQ-D36; NULL khi bị bỏ im lặng." The allowlist is
        -- a CHECK and not a convention, so a fourth command cannot be logged into
        -- existence (AMD-B10).
        CHECK (command IS NULL OR command IN ('CMD-status', 'CMD-run-now', 'CMD-save')),
        CHECK (received_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
    )
    """,
    """
    CREATE UNIQUE INDEX ux_telegram_update_id
        ON telegram_update_log (owner_id, provider_update_id)
    """,
    f"""
    CREATE TABLE telegram_link_attempt (
        id           TEXT NOT NULL PRIMARY KEY,
        owner_id     TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
        chat_id_hash TEXT NOT NULL,
        attempted_at TEXT NOT NULL,
        outcome      TEXT NOT NULL,
        link_code_id TEXT NULL REFERENCES telegram_link_code (id) ON DELETE RESTRICT,

        CHECK (length(id) = 26),
        CHECK ({_SHA256.format(col='chat_id_hash')}),
        CHECK (outcome IN ('format_match_code_invalid', 'format_match_code_expired',
                           'format_match_code_consumed', 'format_match_code_valid',
                           'rate_limited_not_checked')),
        CHECK (attempted_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
    )
    """,
    # Serves COUNT(... WHERE chat_id_hash = H AND attempted_at IN window). NOT unique: two
    # attempts from one chat in one window are the very thing being counted.
    """
    CREATE INDEX ix_link_attempt_chat_window
        ON telegram_link_attempt (owner_id, chat_id_hash, attempted_at)
    """,
)

_DOWN: tuple[str, ...] = (
    "DROP INDEX IF EXISTS ix_link_attempt_chat_window",
    "DROP TABLE IF EXISTS telegram_link_attempt",
    "DROP INDEX IF EXISTS ux_telegram_update_id",
    "DROP TABLE IF EXISTS telegram_update_log",
    "DROP INDEX IF EXISTS ux_telegram_link_code_active",
    "DROP TABLE IF EXISTS telegram_link_code",
    "DROP INDEX IF EXISTS ux_telegram_link_generation",
    "DROP INDEX IF EXISTS ux_telegram_link_active",
    "DROP TABLE IF EXISTS telegram_link",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DOWN:
        op.execute(statement)
