"""``tag``, ``settings`` and ``rescan_ledger``: the three tables this card's semantics need.

Revision ID: 0013_tc_backfill_pending_ledger
Revises: 0012_tc_backup_restore_drill
Create Date: 2026-09-08

One head, by chaining rather than by merging
---------------------------------------------
``0012_tc_backup_restore_drill`` (``TC-backup-restore-drill``, same wave) had already branched
off ``0011_merge_phase4_6_heads`` when this revision was written, so landing here off ``0011``
too would have left two heads. The wave's rule is one head; the two ways to get there are a
merge revision or a chain. This revision chains, because a merge is a *shared* artifact and
both remaining migration authors in the wave would have had to agree not to write one — the
same race that produced ``0004``, ``0007`` and ``0011`` in the first place. Chaining needs no
agreement and no second file: ``alembic heads`` returns exactly one revision, and
``tests/integration/test_backfill_once.py`` asserts that structurally (``len(heads) == 1``,
computed, never a literal).

Nothing here depends on what ``0012_tc_backup_restore_drill`` creates — ``backup_snapshot``,
``backup_manifest`` and ``restore_record`` are untouched by this card — so the order is a
graph edge, not a data dependency.

What this revision does **not** do
----------------------------------
``backfill_ledger`` and ``pending_item_ledger`` already exist.
``0010_tc_report_coverage_publish_cas`` created them as **custodian** for this card and said
in as many words that the card taking them over must EXTEND that definition, never issue a
second ``CREATE TABLE`` — the ``F-A3R1-01`` rule. So there is no second ``CREATE TABLE`` for
either here, no re-declaration of a column that is already right, and ``pending_item_ledger``
is not touched at all: every column, CHECK and index ``ENT-pending-item-ledger`` asks for is
already on disk and correct.

Three tables created
--------------------
===================  ==========================  =========================================
table                entity                      why this revision
===================  ==========================  =========================================
``tag``              ``ENT-tag``                 ``MOD-tag-service``; this card's other
                                                 owner module, and the parent both ledgers'
                                                 ``tag_id`` columns are declared to point at
``settings``         ``ENT-settings``            created **on behalf of**
                                                 ``MOD-settings-service``; card §10
                                                 ``SG-03`` requires N to be read from
                                                 settings rather than hard-coded, so there
                                                 has to be somewhere to read it from
``rescan_ledger``    ``ENT-rescan-ledger``       ``MOD-tag-service``; the separate ledger
                                                 ``tag.rescan_corpus`` writes (§7)
===================  ==========================  =========================================

``settings`` carries the same custodian note 0002b and 0010 carry: a card that later takes it
over EXTENDS this definition and does not recreate it.

Why ``CR-TC-REPORT-01`` is **not** closed here — ``CR-TC-BACKFILL-10``
-----------------------------------------------------------------------
``0010_tc_report_coverage_publish_cas`` shipped ``backfill_ledger.tag_id`` and
``report.tag_config_version_id`` without their ``REFERENCES`` clauses, because ``tag`` and
``tag_config_version`` did not exist — SQLite resolves foreign keys at DML time, so a clause
naming a missing table turns every INSERT into an error — and asked the revision that creates
the parent table to add the constraint.

``tag`` exists as of this revision, so adding ``REFERENCES tag (id)`` is now possible, and it
was written and then deliberately withdrawn. It breaks a sibling card's passing test:
``tests/integration/test_coverage_contiguous.py::test_a_refused_write_advances_nothing_and_consumes_no_backfill``
inserts a ``backfill_ledger`` row with a synthetic ``tag_id`` and — correctly, for a repository
in which ``tag`` did not exist — seeds no ``tag`` row, so the new constraint fails it with
``FOREIGN KEY constraint failed``. That file is ``TC-report-coverage-publish-cas``'s write set
and this card does not edit it, and the contract fix is one seeded row rather than a schema
change, so the honest move is to leave the column as 0010 shipped it and hand the evidence
back. ``CR-TC-BACKFILL-10`` carries it, with the exact test and the one-line fix.

``report.tag_config_version_id`` stays open for the same family of reasons plus one more:
``tag_config_version`` has no writer among the 19 cards at all.

``rescan_ledger.tag_id`` **does** get its foreign key: that table is created here, so there is
no existing row and no sibling test to invalidate.

``ux_rescan_open`` and NULL
---------------------------
``entities.yaml`` declares ``UNIQUE(owner_id, tag_id) WHERE state IN ('requested','running')``
and its own ``does_not_guarantee`` note is worth restating: SQLite treats two NULLs as
distinct, so the index limits open rescans **per tag** and does not limit concurrent
whole-corpus rescans (``tag_id IS NULL``). That is a property of the key the contract declares,
not a deviation from it, and ``server/app/tags/rescan.py`` says so where a caller can see it.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0013_tc_backfill_pending_ledger"
down_revision: str | None = "0012_tc_backup_restore_drill"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps;
#: ``contracts/reporting/time-and-tags.md`` §1.1), spelled as the earlier revisions spell it.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_SETTINGS = f"""
CREATE TABLE settings (
    id          TEXT NOT NULL PRIMARY KEY,
    owner_id    TEXT NOT NULL REFERENCES owner (id)
                     ON DELETE RESTRICT ON UPDATE RESTRICT,
    "key"       TEXT NOT NULL CHECK (length("key") BETWEEN 1 AND 120),
    value_json  TEXT NOT NULL,
    updated_at  TEXT NOT NULL CHECK (updated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

_TAG = f"""
CREATE TABLE tag (
    id                    TEXT NOT NULL PRIMARY KEY,
    owner_id              TEXT NOT NULL REFERENCES owner (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
    "text"                TEXT NOT NULL CHECK (length("text") BETWEEN 1 AND 200),
    similarity_threshold  REAL     NULL CHECK (
                               similarity_threshold IS NULL
                               OR (similarity_threshold >= 0 AND similarity_threshold <= 1)),
    state                 TEXT NOT NULL CHECK (state IN ('active', 'removed')),
    created_at            TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    updated_at            TEXT NOT NULL CHECK (updated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    removed_at            TEXT     NULL CHECK (
                               removed_at IS NULL
                               OR removed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

    CONSTRAINT ck_tag_removed_at_pairs_with_state
        CHECK ((state = 'removed') = (removed_at IS NOT NULL))
)
"""

_RESCAN_LEDGER = f"""
CREATE TABLE rescan_ledger (
    id                  TEXT NOT NULL PRIMARY KEY,
    owner_id            TEXT NOT NULL REFERENCES owner (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    tag_id              TEXT     NULL REFERENCES tag (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    requested_at        TEXT NOT NULL CHECK (requested_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    scope_from          TEXT     NULL CHECK (
                             scope_from IS NULL
                             OR scope_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    state               TEXT NOT NULL CHECK (
                             state IN ('requested', 'running', 'done', 'failed')),
    consumed_report_id  TEXT     NULL REFERENCES report (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT
)
"""

_STATEMENTS: tuple[str, ...] = (
    _SETTINGS,
    'CREATE UNIQUE INDEX ux_settings_owner_key ON settings (owner_id, "key")',
    _TAG,
    'CREATE UNIQUE INDEX ux_tag_owner_text_active ON tag (owner_id, "text") '
    "WHERE state = 'active'",
    _RESCAN_LEDGER,
    "CREATE UNIQUE INDEX ux_rescan_open ON rescan_ledger (owner_id, tag_id) "
    "WHERE state IN ('requested', 'running')",
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE IF EXISTS rescan_ledger",
    "DROP TABLE IF EXISTS tag",
    "DROP TABLE IF EXISTS settings",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DROPS:
        op.execute(statement)
