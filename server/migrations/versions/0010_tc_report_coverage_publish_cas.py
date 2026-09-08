"""Reporting tables for ``TC-report-coverage-publish-cas`` (``MOD-report-service``).

Revision ID: 0010_tc_report_coverage_publish_cas
Revises: 0009_tc_telegram_unknown_delivery
Create Date: 2026-09-08

Six tables created, one table rebuilt. Every column name, type, nullability, enum, CHECK and
UNIQUE key is transcribed from ``contracts/data/entities.yaml``:

===========================  =====================================  ==========================
table                        entity                                 note
===========================  =====================================  ==========================
``report``                   ``ENT-report``                         created here
``report_item``              ``ENT-report-item``                    created here
``emerging_direction``       ``ENT-emerging-direction``             created here
``coverage_window``          ``ENT-coverage-window``                created here
``pending_item_ledger``      ``ENT-pending-item-ledger``            created here
``backfill_ledger``          ``ENT-backfill-ledger``                created here, custodian
``first_announced_ledger``   ``ENT-first-announced-ledger``         **rebuilt**, taken over
===========================  =====================================  ==========================

Taking over ``first_announced_ledger`` (0002b, ``CR-TC-IDENTITY-13``)
---------------------------------------------------------------------
``0002b_shared_move_set_tables`` created the table on this module's behalf and left
``first_report_id`` as a plain column because ``report`` did not exist -- SQLite resolves
foreign keys at DML time, so a clause naming a missing table turns every INSERT into an
error. ``report`` exists as of this revision, so the column gets its ``REFERENCES report (id)``
through a table rebuild (create/copy/drop/rename), which is the only way SQLite adds a foreign
key to an existing table. There is no second ``CREATE TABLE first_announced_ledger`` in the
graph: the old one is dropped in the same revision that replaces it.

``backfill_ledger`` is created here as **custodian** for ``TC-backfill-pending-ledger``
-----------------------------------------------------------------------------------------
``entities.yaml`` gives the table to ``MOD-report-service`` and ``contracts/reporting/
time-and-tags.md`` §4.5 item 7 puts ``consumed_in_report_id`` inside the publish transaction,
so the publisher cannot work without it. ``TC-backfill-pending-ledger`` owns the *semantics*
(entitlement granting, add->remove->re-add) and must **EXTEND** this definition -- a later
revision or a rebuild -- never issue a second ``CREATE TABLE``. That is the ``F-A3R1-01``
rule, and it is repeated here for the same reason 0002b repeated it for this card.

``pending_item_ledger`` follows the same logic: §4.5 item 6 writes it inside the publish
transaction, so it is created here and extended, not recreated, by the backfill card.

Three columns deliberately carry **no** ``REFERENCES`` clause
--------------------------------------------------------------
* ``report.tag_config_version_id -> tag_config_version(id)``
* ``backfill_ledger.tag_id -> tag(id)``
* ``pending_item_ledger.target_key`` (a union key, never a foreign key)

``tag``, ``tag_alias``, ``tag_exclusion`` and ``tag_config_version`` belong to
``MOD-tag-service``, and **no card in the 19 creates them**. The 0002b precedent applies
verbatim: the columns keep their name, type and NOT NULL, and the revision that creates the
referenced table adds the constraint. ``CR-TC-REPORT-01`` carries that request forward.

``ux_coverage_window_predecessor`` needs a second index to mean what the contract says
---------------------------------------------------------------------------------------
``entities.yaml`` declares ``UNIQUE(owner_id, predecessor_window_id)`` and
``contracts/reporting/time-and-tags.md`` §4.9 O-4.1 additionally requires
``#coverage_window[predecessor_window_id IS NULL] = 1``. In SQLite two NULLs are *distinct*
for the purpose of a UNIQUE index, so the declared index alone would let two bootstrap windows
exist side by side -- exactly the gap the CAS is supposed to close, one row earlier. The
partial index ``ux_coverage_window_bootstrap`` closes it. It adds no constraint the contract
does not already state; it makes the stated one enforceable.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0010_tc_report_coverage_publish_cas"
down_revision: str | None = "0009_tc_telegram_unknown_delivery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §conventions).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"


#: ``entities.yaml`` §conventions/hashes: ``sha256:`` + 64 lowercase hex = 71 characters.
def _sha256_check(column: str) -> str:
    return f"{column} GLOB 'sha256:*' AND length({column}) = 71"


#: ``entities.yaml`` §target_union allows either a stored generated column or a
#: domain-written one. ``report_item`` takes the **domain-written** form, with a CHECK that
#: makes disagreement impossible, for two reasons. First, ``report_item.target_key`` of a
#: published period is frozen (I05, I17: a merge explicitly does **not** rewrite it), and a
#: generated column would silently follow any later edit of ``target_work_id`` -- the value
#: has to be written once and then stay written. Second, ``analysis_generation`` in
#: ``0006_tc_analysis_once_per_generation`` already sets this precedent for exactly the rows
#: whose key must not move.
_TARGET_KEY = "target_key TEXT NOT NULL"
_TARGET_KEY_AGREES = (
    "CHECK (target_key = target_kind || ':' || COALESCE(target_work_id, target_post_id))"
)
_EXACTLY_ONE_TARGET = (
    "CHECK ((target_kind = 'work' AND target_work_id IS NOT NULL AND target_post_id IS NULL)"
    " OR (target_kind = 'post' AND target_post_id IS NOT NULL AND target_work_id IS NULL))"
)

_ABORT_REASONS = (
    "'empty_period', 'tag_version_stale', 'embedding_generation_mismatch', "
    "'cas_conflict', 'builder_failure', 'cancelled'"
)

_STATEMENTS: tuple[str, ...] = (
    # -- report (ENT-report) -------------------------------------------------------------
    # ck_report_abort_reason and ck_report_selection_version_published are transcribed from
    # entities.yaml `checks`. The third CHECK (published_at) is the field-level constraint
    # "NOT NULL khi status = 'published'" written as a table CHECK, which is the only place
    # SQLite can express it.
    f"""
    CREATE TABLE report (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        coverage_from           TEXT NOT NULL
                                     CHECK (coverage_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        coverage_to             TEXT NOT NULL
                                     CHECK (coverage_to GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        tag_config_version_id   TEXT NOT NULL,
        embedding_generation_id TEXT NOT NULL REFERENCES embedding_generation (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        report_build_id         TEXT NOT NULL CHECK (length(report_build_id) = 36),
        status                  TEXT NOT NULL
                                     CHECK (status IN ('building', 'published', 'aborted')),
        abort_reason            TEXT     NULL CHECK (abort_reason IN ({_ABORT_REASONS})),
        quality                 TEXT NOT NULL CHECK (quality IN ('complete', 'partial')),
        published_at            TEXT     NULL
                                     CHECK (published_at IS NULL
                                            OR published_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        content_hash            TEXT     NULL
                                     CHECK (content_hash IS NULL
                                            OR ({_sha256_check("content_hash")})),
        selection_version       TEXT     NULL,
        created_at              TEXT NOT NULL
                                     CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        updated_at              TEXT NOT NULL
                                     CHECK (updated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CONSTRAINT ck_report_coverage_half_open CHECK (coverage_to > coverage_from),
        CONSTRAINT ck_report_abort_reason
            CHECK ((status = 'aborted' AND abort_reason IS NOT NULL)
                   OR (status <> 'aborted' AND abort_reason IS NULL)),
        CONSTRAINT ck_report_selection_version_published
            CHECK (status <> 'published' OR selection_version IS NOT NULL),
        CONSTRAINT ck_report_published_at
            CHECK (status <> 'published' OR published_at IS NOT NULL)
    )
    """,
    "CREATE UNIQUE INDEX ux_report_owner_build_id ON report (owner_id, report_build_id)",
    "CREATE INDEX ix_report_owner_status ON report (owner_id, status, published_at)",
    # -- coverage_window (ENT-coverage-window) --------------------------------------------
    f"""
    CREATE TABLE coverage_window (
        id                    TEXT    NOT NULL PRIMARY KEY,
        owner_id              TEXT    NOT NULL REFERENCES owner (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        sequence              INTEGER NOT NULL CHECK (sequence >= 1),
        window_from           TEXT    NOT NULL
                                      CHECK (window_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        window_to             TEXT    NOT NULL
                                      CHECK (window_to GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        ingest_sequence_from  INTEGER NOT NULL CHECK (ingest_sequence_from >= 0),
        ingest_sequence_to    INTEGER NOT NULL,
        predecessor_window_id TEXT        NULL REFERENCES coverage_window (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        report_id             TEXT        NULL REFERENCES report (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        advanced_at           TEXT    NOT NULL
                                      CHECK (advanced_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CONSTRAINT ck_coverage_window_half_open CHECK (window_to > window_from),
        CONSTRAINT ck_coverage_ingest_half_open
            CHECK (ingest_sequence_to >= ingest_sequence_from),
        CONSTRAINT ck_coverage_no_self_predecessor
            CHECK (predecessor_window_id IS NULL OR predecessor_window_id <> id)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_coverage_window_owner_sequence
        ON coverage_window (owner_id, sequence)
    """,
    # THE CAS. Two kỳ cannot chain after the same predecessor (entities.yaml note,
    # time-and-tags.md §4.6). SQLite treats NULLs as distinct here, hence the second index.
    """
    CREATE UNIQUE INDEX ux_coverage_window_predecessor
        ON coverage_window (owner_id, predecessor_window_id)
        WHERE predecessor_window_id IS NOT NULL
    """,
    """
    CREATE UNIQUE INDEX ux_coverage_window_bootstrap
        ON coverage_window (owner_id)
        WHERE predecessor_window_id IS NULL
    """,
    "CREATE INDEX ix_coverage_window_report ON coverage_window (report_id)",
    # -- report_item (ENT-report-item) ----------------------------------------------------
    # `first_announced_report_id` NOT NULL iff item_type = 'prior_reference' is the schema
    # half of REQ-AC09: "đã báo cáo ngày D" cannot be rendered without the report it points
    # at, and a `prior_reference` without one would be a claim with no date behind it.
    f"""
    CREATE TABLE report_item (
        id                        TEXT NOT NULL PRIMARY KEY,
        owner_id                  TEXT NOT NULL REFERENCES owner (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        report_id                 TEXT NOT NULL REFERENCES report (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_kind               TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_work_id            TEXT NULL REFERENCES work (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_post_id            TEXT NULL REFERENCES post (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        {_TARGET_KEY},
        item_type                 TEXT NOT NULL
                                       CHECK (item_type IN
                                              ('new_discovery', 'prior_reference')),
        first_announced_report_id TEXT NULL REFERENCES report (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        analysis_id               TEXT NULL REFERENCES analysis (id)
                                       ON DELETE RESTRICT ON UPDATE RESTRICT,
        selection_reason          TEXT NOT NULL,
        {_EXACTLY_ONE_TARGET},
        {_TARGET_KEY_AGREES},
        CONSTRAINT ck_report_item_reference_has_date
            CHECK (item_type <> 'prior_reference' OR first_announced_report_id IS NOT NULL)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_report_item_report_target
        ON report_item (owner_id, report_id, target_key)
    """,
    "CREATE INDEX ix_report_item_target ON report_item (owner_id, target_key, item_type)",
    # -- emerging_direction (ENT-emerging-direction) --------------------------------------
    """
    CREATE TABLE emerging_direction (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        report_id               TEXT NOT NULL REFERENCES report (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        member_target_keys      TEXT NOT NULL,
        density_metric          TEXT NOT NULL,
        evidence_state          TEXT NOT NULL
                                     CHECK (evidence_state IN
                                            ('sufficient', 'insufficient_evidence')),
        embedding_generation_id TEXT NOT NULL REFERENCES embedding_generation (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT
    )
    """,
    "CREATE INDEX ix_emerging_direction_report ON emerging_direction (report_id)",
    # -- pending_item_ledger (ENT-pending-item-ledger) ------------------------------------
    # The partial UNIQUE IS the "one open pending row per target" rule of §5.1; it is what
    # makes I06 ("pending không mất khi con trỏ tiến") checkable rather than aspirational.
    """
    CREATE TABLE pending_item_ledger (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_key              TEXT NOT NULL,
        reason                  TEXT NOT NULL
                                     CHECK (reason IN ('missing_summary', 'analysis_failed',
                                                       'analysis_unknown', 'budget_exceeded')),
        first_pending_window_id TEXT NOT NULL REFERENCES coverage_window (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT
                                     DEFERRABLE INITIALLY DEFERRED,
        state                   TEXT NOT NULL
                                     CHECK (state IN ('pending', 'resolved_reported_late',
                                                      'abandoned_by_owner'))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_pending_owner_target_open
        ON pending_item_ledger (owner_id, target_key)
        WHERE state = 'pending'
    """,
    "CREATE INDEX ix_pending_window ON pending_item_ledger (first_pending_window_id)",
    # -- backfill_ledger (ENT-backfill-ledger) --------------------------------------------
    # ux_backfill_subscription_consumed IS REQ-D28 "đúng một lần": one subscription identity
    # consumes backfill once for the life of the system, add->remove->re-add included.
    f"""
    CREATE TABLE backfill_ledger (
        id                         TEXT    NOT NULL PRIMARY KEY,
        owner_id                   TEXT    NOT NULL REFERENCES owner (id)
                                           ON DELETE RESTRICT ON UPDATE RESTRICT,
        tag_id                     TEXT    NOT NULL,
        activation_sequence        INTEGER NOT NULL CHECK (activation_sequence >= 1),
        subscription_identity_hash TEXT    NOT NULL
                                           CHECK (length(subscription_identity_hash) = 64),
        entitlement                TEXT    NOT NULL
                                           CHECK (entitlement IN
                                                  ('granted', 'consumed',
                                                   'denied_already_consumed')),
        entitlement_reason         TEXT        NULL,
        backfill_days              INTEGER NOT NULL CHECK (backfill_days >= 0),
        consumed_in_report_id      TEXT        NULL REFERENCES report (id)
                                           ON DELETE RESTRICT ON UPDATE RESTRICT,
        consumed_at                TEXT        NULL
                                           CHECK (consumed_at IS NULL
                                                  OR consumed_at GLOB
                                                     '{TIMESTAMP_UTC_MS_GLOB}'),

        CONSTRAINT ck_backfill_consumed_pair
            CHECK ((consumed_in_report_id IS NULL) = (consumed_at IS NULL)),
        CONSTRAINT ck_backfill_denied_has_reason
            CHECK (entitlement <> 'denied_already_consumed'
                   OR (entitlement_reason IS NOT NULL AND length(entitlement_reason) > 0))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_backfill_tag_activation
        ON backfill_ledger (owner_id, tag_id, activation_sequence)
    """,
    """
    CREATE UNIQUE INDEX ux_backfill_subscription_consumed
        ON backfill_ledger (owner_id, subscription_identity_hash)
        WHERE consumed_in_report_id IS NOT NULL
    """,
)

#: The rebuild of ``first_announced_ledger``. Create/copy/drop/rename is the only way SQLite
#: adds a foreign key to an existing table. Column order, types, nullability and the two
#: DEFERRABLE merge references are byte-identical to 0002b; the single difference is the new
#: ``REFERENCES report (id)`` on ``first_report_id``.
_REBUILD_FIRST_ANNOUNCED: tuple[str, ...] = (
    f"""
    CREATE TABLE first_announced_ledger_rebuilt (
        id                     TEXT NOT NULL PRIMARY KEY,
        owner_id               TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        canonical_work_id      TEXT NOT NULL REFERENCES work (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        first_report_id        TEXT NOT NULL REFERENCES report (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        first_announced_at     TEXT NOT NULL
                                    CHECK (first_announced_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        merge_audit_id         TEXT NULL REFERENCES identity_merge_audit (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED,
        superseded_by_merge_id TEXT NULL REFERENCES identity_merge_audit (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED
    )
    """,
    """
    INSERT INTO first_announced_ledger_rebuilt
        (id, owner_id, canonical_work_id, first_report_id, first_announced_at,
         merge_audit_id, superseded_by_merge_id)
    SELECT id, owner_id, canonical_work_id, first_report_id, first_announced_at,
           merge_audit_id, superseded_by_merge_id
      FROM first_announced_ledger
    """,
    "DROP INDEX ux_first_announced_canonical_work",
    "DROP TABLE first_announced_ledger",
    "ALTER TABLE first_announced_ledger_rebuilt RENAME TO first_announced_ledger",
    # I07 at the schema level: one canonical work has one first-announcement.
    """
    CREATE UNIQUE INDEX ux_first_announced_canonical_work
        ON first_announced_ledger (owner_id, canonical_work_id)
    """,
    """
    CREATE INDEX ix_first_announced_effective
        ON first_announced_ledger (owner_id, canonical_work_id)
        WHERE superseded_by_merge_id IS NULL
    """,
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE backfill_ledger",
    "DROP TABLE pending_item_ledger",
    "DROP TABLE emerging_direction",
    "DROP TABLE report_item",
    "DROP TABLE coverage_window",
    "DROP TABLE report",
)

#: The downgrade half of the rebuild: put ``first_report_id`` back to a plain column so the
#: table survives ``DROP TABLE report`` above it.
_UNBUILD_FIRST_ANNOUNCED: tuple[str, ...] = (
    f"""
    CREATE TABLE first_announced_ledger_rebuilt (
        id                     TEXT NOT NULL PRIMARY KEY,
        owner_id               TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        canonical_work_id      TEXT NOT NULL REFERENCES work (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        first_report_id        TEXT NOT NULL,
        first_announced_at     TEXT NOT NULL
                                    CHECK (first_announced_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        merge_audit_id         TEXT NULL REFERENCES identity_merge_audit (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED,
        superseded_by_merge_id TEXT NULL REFERENCES identity_merge_audit (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED
    )
    """,
    """
    INSERT INTO first_announced_ledger_rebuilt
        (id, owner_id, canonical_work_id, first_report_id, first_announced_at,
         merge_audit_id, superseded_by_merge_id)
    SELECT id, owner_id, canonical_work_id, first_report_id, first_announced_at,
           merge_audit_id, superseded_by_merge_id
      FROM first_announced_ledger
    """,
    "DROP INDEX ix_first_announced_effective",
    "DROP INDEX ux_first_announced_canonical_work",
    "DROP TABLE first_announced_ledger",
    "ALTER TABLE first_announced_ledger_rebuilt RENAME TO first_announced_ledger",
    """
    CREATE UNIQUE INDEX ux_first_announced_canonical_work
        ON first_announced_ledger (owner_id, canonical_work_id)
    """,
)


def upgrade() -> None:
    """Create the six reporting tables, then give ``first_report_id`` its foreign key."""
    for statement in _STATEMENTS:
        op.execute(statement)
    for statement in _REBUILD_FIRST_ANNOUNCED:
        op.execute(statement)


def downgrade() -> None:
    """Undo the rebuild first, then drop the six tables in reverse dependency order."""
    for statement in _UNBUILD_FIRST_ANNOUNCED:
        op.execute(statement)
    for statement in _DROPS:
        op.execute(statement)
