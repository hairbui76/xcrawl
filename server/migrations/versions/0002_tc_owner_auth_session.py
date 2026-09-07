"""session table (TC-owner-auth-session).

Revision ID: 0002_tc_owner_auth_session
Revises: 0002_base_entities
Create Date: 2026-09-07

This revision creates **one** table: ``session`` (``ENT-session``, owned by
``MOD-auth-service``).

``token_hash`` stores ``sha256:<hex>`` and never the token. ``revoked_at`` makes revocation
a write rather than a delete, as the entity requires ("thu hồi là ghi, không xóa").
``UNIQUE(owner_id, token_hash)`` is the contract's ``ux_session_token_hash``.

What this revision used to do, and no longer does (``F-A3R1-01`` / ``F-A3R1-02``)
--------------------------------------------------------------------------------
It used to ``CREATE TABLE IF NOT EXISTS owner`` and then ``ALTER TABLE owner ADD COLUMN``
the two credential columns, on a branch parallel to ``0002_base_entities`` which also
created ``owner``. Both were guarded by ``IF NOT EXISTS``, so whichever branch Alembic
traversed first won and the other statement was a no-op -- and the two definitions differed
by a ``CHECK``. The shipped schema was therefore a function of traversal order rather than
of ``contracts/data/entities.yaml``.

Both halves of that are now gone:

* ``0002_base_entities`` is the **sole** ``CREATE TABLE owner``, carrying the full
  ``ENT-owner`` constraint set including the four columns added by amendment
  ``AMD-ENT-owner-01`` (``password_hash``, ``password_updated_at``, ``failed_login_count``,
  ``locked_until``) that resolve ``CR-TC-AUTH-02`` and ``CR-TC-AUTH-03``;
* this revision ``Revises: 0002_base_entities`` instead of ``0001``, so ``owner`` always
  exists, complete, before ``session`` references it -- the order is a property of the
  chain, not of the walk.

``tests/contract/test_schema_matches_entities.py`` is the permanent guard: it compares the
post-``upgrade head`` schema against ``entities.yaml`` column by column and constraint by
constraint, and asserts the two traversal orders produce byte-identical DDL.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0002_tc_owner_auth_session"
down_revision: str | None = "0002_base_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

#: `contracts/data/entities.yaml` `conventions.timestamps`: RFC 3339 UTC, millisecond
#: precision mandatory. Same GLOB the base revision applies to `owner.created_at`.
TIMESTAMP_UTC_MS_GLOB = (
    "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T"
    "[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z"
)


def upgrade() -> None:
    op.execute(
        f"""
        CREATE TABLE session (
            id                  TEXT NOT NULL PRIMARY KEY,
            owner_id            TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
            token_hash          TEXT NOT NULL,
            issued_at           TEXT NOT NULL
                                     CHECK (issued_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
            expires_at          TEXT NOT NULL
                                     CHECK (expires_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
            revoked_at          TEXT
                                     CHECK (revoked_at IS NULL
                                            OR revoked_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
            user_agent_redacted TEXT,
            CONSTRAINT ck_session_token_hash_shape
                CHECK (token_hash LIKE 'sha256:%' AND length(token_hash) = 71)
        )
        """
    )
    # `ux_session_token_hash` (entities.yaml `ENT-session.keys.unique`): "Không hai phiên
    # cùng token hash." Created as a named index so the constraint carries the contract's
    # own name on disk, which is what the schema test looks for.
    op.execute("CREATE UNIQUE INDEX ux_session_token_hash ON session (owner_id, token_hash)")
    # Every authenticated request resolves a session by token hash alone.
    op.execute("CREATE INDEX ix_session_token_hash ON session (token_hash)")


def downgrade() -> None:
    """Drops only what this revision created."""
    op.execute("DROP INDEX IF EXISTS ix_session_token_hash")
    op.execute("DROP INDEX IF EXISTS ux_session_token_hash")
    op.execute("DROP TABLE IF EXISTS session")
