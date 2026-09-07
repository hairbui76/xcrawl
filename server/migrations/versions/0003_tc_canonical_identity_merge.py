"""Identity: alias table, conflict quarantine, merge audit and work versions.

Revision ID: 0003_tc_canonical_identity_merge
Revises: 0002b_shared_move_set_tables
Create Date: 2026-09-07

Card: ``agent-tasks/TC-canonical-identity-merge.md`` §4 (state effects) and §6 (TXN-identity-merge).
Source of truth: ``contracts/data/entities.yaml`` entities ``identity_alias``,
``identity_conflict``, ``identity_merge_audit``, ``work_version`` and the transaction
``TXN-identity-merge``; ``contracts/data/identity.md`` §3, §5, §6.

The tables this card does NOT own live in ``0002b_shared_move_set_tables``
------------------------------------------------------------------------
``TXN-identity-merge`` rewrites pointers in ``work_label``, ``analysis`` and ``saved_item``,
reads ``saved_snapshot`` to prove I17, and rewrites ``first_announced_ledger`` per
``contracts/reporting/time-and-tags.md`` §8.3. Those five tables belong to
``MOD-analysis-service``, ``MOD-saved-service`` and ``MOD-report-service``. They were created
here in the first version of this revision and are now created by ``0002b_shared_move_set_tables``
instead (finding ``F-A3R1-04``): the merge still needs them, but the migration that creates a
table should not imply ownership of it. This revision creates identity's own four tables only.

Deferred references to ``identity_merge_audit``
-----------------------------------------------
Every ``moved_by_merge_id`` / ``superseded_by_merge_id`` / ``merge_audit_id`` column is
``DEFERRABLE INITIALLY DEFERRED``. ``TXN-identity-merge`` rewrites the pointers and writes the
audit row inside ONE transaction, and the audit row is the commit point; checking these
constraints at COMMIT rather than per statement is what makes "no merge without an audit row"
a database guarantee instead of a coding convention.

``target_key`` is a STORED generated column
-------------------------------------------
``entities.yaml`` → ``target_union`` allows either a stored generated column or a plain column
written by the domain layer. The generated form is chosen because it makes the merge move-set
unable to desynchronise: rewriting ``target_work_id`` rewrites ``target_key`` by derivation, so
"``target_key`` was moved" cannot be true while "``target_work_id`` was moved" is false.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0003_tc_canonical_identity_merge"
down_revision: str | None = "0002b_shared_move_set_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps). The
#: same shape the ingest revision enforces; `F-A3R1-14` asked for it everywhere a contract
#: types a column `timestamp_utc_ms`, so a wrongly-shaped timestamp is refused at the row, not
#: discovered later by a report that sorts strings.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_OWNED_BY_THIS_CARD: tuple[str, ...] = (
    # -- work_version ------------------------------------------------------------------
    # arXiv v1/v2 are ONE work with TWO versions (identity.md §2.2); `is_current` is unique
    # per work, so "the current version" is a database fact, not a convention.
    f"""
    CREATE TABLE work_version (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        work_id             TEXT NOT NULL REFERENCES work (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        version_label       TEXT NOT NULL,
        version_scheme      TEXT NOT NULL CHECK (version_scheme IN ('arxiv', 'publisher')),
        announced_at        TEXT NULL
                                 CHECK (announced_at IS NULL
                                        OR announced_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        observed_at         TEXT NOT NULL
                                 CHECK (observed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        abstract_text       TEXT NULL,
        content_fingerprint TEXT NOT NULL,
        is_current          INTEGER NOT NULL CHECK (is_current IN (0, 1))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_work_version_owner_work_label
        ON work_version (owner_id, work_id, version_label)
    """,
    """
    CREATE UNIQUE INDEX ux_work_version_current ON work_version (owner_id, work_id)
        WHERE is_current = 1
    """,
    # -- identity_merge_audit ----------------------------------------------------------
    # Immutable after commit. `ux_merge_audit_owner_loser` is what makes "a work is merged
    # once, for ever" a constraint rather than an intention.
    f"""
    CREATE TABLE identity_merge_audit (
        id                    TEXT NOT NULL PRIMARY KEY,
        owner_id              TEXT NOT NULL REFERENCES owner (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        winner_work_id        TEXT NOT NULL REFERENCES work (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        loser_work_id         TEXT NOT NULL REFERENCES work (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        winner_selection_rule TEXT NOT NULL
                                   CHECK (winner_selection_rule IN
                                          ('earliest_first_discovered_at', 'owner_choice',
                                           'only_candidate_with_canonical_doi')),
        linking_evidence      TEXT NOT NULL,
        moved_counts          TEXT NOT NULL,
        preserved_counts      TEXT NOT NULL,
        merged_at             TEXT NOT NULL
                                   CHECK (merged_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        performed_by          TEXT NOT NULL
                                   CHECK (performed_by IN
                                          ('system_automatic_on_evidence', 'owner_manual')),
        reversal_of_merge_id  TEXT NULL REFERENCES identity_merge_audit (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT
                                   DEFERRABLE INITIALLY DEFERRED,
        CHECK (loser_work_id <> winner_work_id)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_merge_audit_owner_loser
        ON identity_merge_audit (owner_id, loser_work_id)
    """,
    # -- identity_alias ----------------------------------------------------------------
    # The UNIQUE below is what turns lookup into a function: (scheme, value) -> at most one
    # work (I03a). `id_value_raw` is kept for ever so §8 can recompute normalisation.
    f"""
    CREATE TABLE identity_alias (
        id                     TEXT NOT NULL PRIMARY KEY,
        owner_id               TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        id_scheme              TEXT NOT NULL
                                    CHECK (id_scheme IN
                                           ('doi', 'arxiv', 'openalex', 'pmid', 'landing_url')),
        id_value_normalized    TEXT NOT NULL,
        id_value_raw           TEXT NOT NULL,
        work_id                TEXT NOT NULL REFERENCES work (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        evidence_source        TEXT NOT NULL
                                    CHECK (evidence_source IN
                                           ('post_link', 'arxiv_api', 'openalex_api',
                                            'manual_owner')),
        evidence_ref           TEXT NOT NULL,
        confidence             TEXT NOT NULL
                                    CHECK (confidence IN
                                           ('asserted_by_source', 'confirmed_by_two_sources',
                                            'owner_confirmed')),
        created_at             TEXT NOT NULL
                                    CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        superseded_by_merge_id TEXT NULL REFERENCES identity_merge_audit (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED
    )
    """,
    """
    CREATE UNIQUE INDEX ux_identity_alias_owner_scheme_value
        ON identity_alias (owner_id, id_scheme, id_value_normalized)
    """,
    "CREATE INDEX ix_identity_alias_work ON identity_alias (work_id)",
    # -- identity_conflict -------------------------------------------------------------
    # Quarantine, not a guess. `state` leaves 'open' only through identity.resolve_conflict:
    # there is no timeout that turns a conflict into a merge (identity.md §5.5).
    f"""
    CREATE TABLE identity_conflict (
        id                   TEXT NOT NULL PRIMARY KEY,
        owner_id             TEXT NOT NULL REFERENCES owner (id)
                                  ON DELETE RESTRICT ON UPDATE RESTRICT,
        conflict_type        TEXT NOT NULL
                                  CHECK (conflict_type IN
                                         ('cross_scheme_disagreement', 'alias_points_to_two_works',
                                          'canonical_value_mismatch', 'merge_cycle_detected')),
        involved_work_ids    TEXT NOT NULL,
        involved_identifiers TEXT NOT NULL,
        detected_at          TEXT NOT NULL
                                  CHECK (detected_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        detected_in_run_id   TEXT NULL,
        state                TEXT NOT NULL
                                  CHECK (state IN
                                         ('open', 'resolved_merged', 'resolved_distinct',
                                          'resolved_data_error')),
        resolution_note      TEXT NULL,
        resolved_at          TEXT NULL
                                  CHECK (resolved_at IS NULL
                                         OR resolved_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        resolution_merge_id  TEXT NULL REFERENCES identity_merge_audit (id)
                                  ON DELETE RESTRICT ON UPDATE RESTRICT
                                  DEFERRABLE INITIALLY DEFERRED,
        CHECK ((state = 'open') = (resolved_at IS NULL))
    )
    """,
    "CREATE INDEX ix_identity_conflict_state ON identity_conflict (owner_id, state)",
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE identity_conflict",
    "DROP TABLE identity_alias",
    "DROP TABLE identity_merge_audit",
    "DROP TABLE work_version",
)


def upgrade() -> None:
    """Create the four tables ``MOD-identity-service`` owns."""
    for statement in _OWNED_BY_THIS_CARD:
        op.execute(statement)


def downgrade() -> None:
    """Drop everything this revision created, in reverse dependency order."""
    for statement in _DROPS:
        op.execute(statement)
