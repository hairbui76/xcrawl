"""Merge the three Phase 1 migration branches into one head.

Revision ID: 0004_merge_phase1_heads
Revises: 0002_tc_owner_auth_session, 0003_tc_canonical_identity_merge,
         0003_tc_ingest_idempotent_ack_lost
Create Date: 2026-09-07

Four Phase 1 cards were implemented in parallel and each added a revision, which left the
chain with three heads. ``alembic upgrade head`` fails on an ambiguous head, so a deployment
would have had to know which branches to name -- exactly the kind of knowledge that lives in
someone's memory and then does not. This revision creates NO schema; it only states that the
three branches are one line of history from here on.

Who owns which table, so no card creates a table twice:

============================  ==============================================================
``0002_base_entities``        ``owner``, ``work``, ``post``, ``post_work`` (shared base)
``0002_tc_owner_auth_session`` ``session``; adds ``owner.password_hash`` /
                              ``owner.password_updated_at`` if the base revision ran first
``0003_tc_canonical_identity_merge`` ``identity_alias``, ``identity_conflict``,
                              ``identity_merge_audit``, ``work_version``, and the tables the
                              merge move-set rewrites (``analysis``, ``saved_item``,
                              ``saved_snapshot``, ``work_label``, ``first_announced_ledger``)
``0003_tc_ingest_idempotent_ack_lost`` ``checkpoint``, ``ingest_receipt``
============================  ==============================================================

``owner`` is the one table two revisions touch: the base revision creates it with
``IF NOT EXISTS`` and the auth revision does the same before adding its two credential columns,
so either order produces the same schema. Written by ``TC-canonical-identity-merge`` on the
Coordinator's instruction; it is a coordination artefact and belongs to no single card.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0004_merge_phase1_heads"
down_revision: str | tuple[str, ...] | None = (
    "0002_tc_owner_auth_session",
    "0003_tc_canonical_identity_merge",
    "0003_tc_ingest_idempotent_ack_lost",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """No-op: a merge point creates nothing."""


def downgrade() -> None:
    """No-op."""
