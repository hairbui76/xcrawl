"""Initial empty baseline.

Revision ID: 0001
Revises:
Create Date: 2026-09-07

This revision creates NOTHING. It exists so the migration chain has a root and so
``alembic upgrade head`` is a meaningful command on a fresh checkout before any table
exists.

The real schema is written by the Phase 1 cards from ``contracts/data/entities.yaml``
(60 entities, ``TXN-*`` transaction map). Inventing tables here would put a second,
un-reviewed source of schema truth next to the entity contract.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """No-op: the baseline is an empty database."""


def downgrade() -> None:
    """No-op."""
