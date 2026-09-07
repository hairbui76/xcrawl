"""Merge the three revisions that branched off ``0005`` in this wave. No DDL.

Revision ID: 0007_merge_phase3_5_heads
Revises: 0006_tc_analysis_once_per_generation, 0006_tc_embedding_generation_switch,
         0006_tc_telegram_linking_auth
Create Date: 2026-09-08

Written by ``TC-telegram-linking-auth`` because it landed last of the three and
``tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head`` is a
standing gate: with three heads, ``alembic upgrade head`` fails outright on a fresh
deployment, so the tree is broken for everyone until one revision joins them.

It creates nothing and drops nothing. The three branches touch disjoint tables --
``analysis*`` (``TC-analysis-once-per-generation``), ``embedding_generation`` /
``tag_vector`` (``TC-embedding-generation-switch``) and the four ``telegram_*`` tables
(this card) -- so their order of application does not change the resulting schema. That is
asserted rather than assumed: the traversal-order test in the same file upgrades a blank
database along several paths and compares the normalised DDL of every object.

A later card that adds a fourth branch off ``0005`` extends the graph past this point; it
does **not** edit this file, it chains onto it.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0007_merge_phase3_5_heads"
down_revision: str | tuple[str, ...] | None = (
    "0006_tc_analysis_once_per_generation",
    "0006_tc_embedding_generation_switch",
    "0006_tc_telegram_linking_auth",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """A merge point carries no schema change."""


def downgrade() -> None:
    """Splitting the graph again is a migration-graph edit, not a data operation."""
