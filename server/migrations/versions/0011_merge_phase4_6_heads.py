"""Merge the two revisions that branched off ``0009`` in the Phase 4/6 wave. No DDL.

Revision ID: 0011_merge_phase4_6_heads
Revises: 0010_tc_report_coverage_publish_cas, 0010_tc_scheduler_lease_claim
Create Date: 2026-09-08

Two cards in the same wave each added one revision on top of
``0009_tc_telegram_unknown_delivery``:

``0010_tc_report_coverage_publish_cas``   ``report``, ``coverage_window``, ``report_item``,
                                          ``emerging_direction``, ``pending_item_ledger``,
                                          ``backfill_ledger`` (``TC-report-coverage-publish-cas``)
``0010_tc_scheduler_lease_claim``         ``run``, ``assignment``, ``schedule_occurrence``,
                                          ``worker_registration``, plus two indexes on the
                                          custodian ``assignment_lease``
                                          (``TC-scheduler-lease-claim``)

They create disjoint sets of tables, so the merge is a pure graph join: **this revision
issues no DDL at all**, and both ``upgrade`` and ``downgrade`` are deliberately empty.

Why a merge revision rather than re-pointing one branch
--------------------------------------------------------
Re-parenting ``0010_tc_scheduler_lease_claim`` onto the report revision would be quieter in
``alembic history`` but would rewrite a revision that has already been applied to any
database following that branch, and it would hide the fact that the two ran in parallel. A
merge point records what actually happened and leaves both revisions' recorded parents
truthful, which is the same reason ``0004_merge_phase1_heads`` and
``0007_merge_phase3_5_heads`` exist.

``tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head`` and
``tests/integration/test_lease_two_claimants.py::test_the_migration_graph_has_exactly_one_head``
both assert ``len(heads) == 1`` **structurally**, never against a literal revision id, so a
third card landing in this wave adds another merge rather than an edit to a test.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0011_merge_phase4_6_heads"
down_revision: str | tuple[str, ...] | None = (
    "0010_tc_report_coverage_publish_cas",
    "0010_tc_scheduler_lease_claim",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """No schema change: the two branches touch disjoint tables."""


def downgrade() -> None:
    """No schema change to undo."""
