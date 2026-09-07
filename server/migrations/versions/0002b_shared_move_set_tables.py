"""Tables that ``TXN-identity-merge`` rewrites but ``MOD-identity-service`` does not own.

Revision ID: 0002b_shared_move_set_tables
Revises: 0002_base_entities
Create Date: 2026-09-07

Why a revision of its own (finding ``F-A3R1-04``)
-------------------------------------------------
``entities.yaml`` gives these five tables to three other modules, and the first version of this
schema created them inside ``0003_tc_canonical_identity_merge``. The reason was sound -- the
merge move-set is a CLOSED list and cannot be proved without the tables it moves rows in -- but
the result read as if the identity card owned them. Splitting them out keeps the reason and
drops the false claim: the identity revision now creates only identity's own tables, and this
revision says in its own header who the tables belong to.

Ownership, and who takes each table over
----------------------------------------

========================== ======================== ================================
table                      ``owner_module``         card that will take it over
========================== ======================== ================================
``saved_snapshot``         ``MOD-saved-service``    ``TC-saved-snapshot``
``saved_item``             ``MOD-saved-service``    ``TC-saved-snapshot``
``analysis``               ``MOD-analysis-service`` ``TC-analysis-once-per-generation``
``work_label``             ``MOD-analysis-service`` ``TC-analysis-once-per-generation``
``first_announced_ledger`` ``MOD-report-service``   ``TC-report-coverage-publish-cas``
========================== ======================== ================================

Card files: ``agent-tasks/TC-saved-snapshot.md``,
``agent-tasks/TC-analysis-once-per-generation.md``,
``agent-tasks/TC-report-coverage-publish-cas.md``.

Custodian: ``MOD-data-store`` on behalf of those three modules until their cards run. Each of
those cards must EXTEND this revision (a later revision, or a table rebuild) rather than issue a
second ``CREATE TABLE``: two definitions of one table is exactly the defect ``F-A3R1-01`` was.
Change requests ``CR-TC-IDENTITY-11..13`` in
``evidence/handoffs/TC-canonical-identity-merge-handoff.md`` carry that instruction to them.

The columns are ``entities.yaml`` column-for-column. Two shapes are load-bearing:

* ``target_key`` is a **STORED generated column** (``target_union`` allows a stored generated
  column or a domain-written one). Generated means the merge cannot desynchronise it: rewriting
  ``target_work_id`` rewrites ``target_key``, so "the key moved" and "the pointer moved" cannot
  disagree.
* Every ``*_merge_id`` reference is ``DEFERRABLE INITIALLY DEFERRED``. ``TXN-identity-merge``
  writes the pointers and the ``identity_merge_audit`` row in ONE transaction and the audit row
  is the commit point, so checking at COMMIT is what makes "no merge without an audit row" a
  database guarantee rather than a coding convention.

``first_report_id`` carries no ``REFERENCES`` clause: ``report`` belongs to the reporting card
and does not exist yet. SQLite resolves foreign keys at DML time, so a clause naming a missing
table would turn every INSERT into an error; the column keeps its name, type and NOT NULL, and
the reporting card adds the constraint when it creates ``report``.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0002b_shared_move_set_tables"
down_revision: str | None = "0002_base_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_TARGET_KEY = (
    "target_key TEXT GENERATED ALWAYS AS "
    "(target_kind || ':' || COALESCE(target_work_id, target_post_id)) STORED"
)
_EXACTLY_ONE_TARGET = (
    "CHECK ((target_kind = 'work' AND target_work_id IS NOT NULL AND target_post_id IS NULL)"
    " OR (target_kind = 'post' AND target_post_id IS NOT NULL AND target_work_id IS NULL))"
)

_STATEMENTS: tuple[str, ...] = (
    # -- saved_snapshot (MOD-saved-service) ---------------------------------------------
    # Absolutely immutable after commit -- this table is the oracle of I17. The merge reads
    # it and writes nothing, and `data.delete_target` may not touch it either (REQ-D55).
    f"""
    CREATE TABLE saved_snapshot (
        id                  TEXT NOT NULL PRIMARY KEY,
        owner_id            TEXT NOT NULL REFERENCES owner (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_kind         TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_key_at_save  TEXT NOT NULL,
        analysis_id_at_save TEXT NULL,
        payload             TEXT NOT NULL,
        content_hash        TEXT NOT NULL CHECK (content_hash GLOB 'sha256:*'),
        created_at          TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
    )
    """,
    # -- analysis (MOD-analysis-service) -------------------------------------------------
    # `analysis_generation_id` and `accepted_from_attempt_id` keep their shape but not their
    # REFERENCES clause: `analysis_generation` and `analysis_attempt` belong to the analysis
    # card, and a clause naming a missing table breaks every INSERT under SQLite.
    f"""
    CREATE TABLE analysis (
        id                       TEXT NOT NULL PRIMARY KEY,
        owner_id                 TEXT NOT NULL REFERENCES owner (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        analysis_generation_id   TEXT NOT NULL,
        target_kind              TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_work_id           TEXT NULL REFERENCES work (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_post_id           TEXT NULL REFERENCES post (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT,
        {_TARGET_KEY},
        task_type                TEXT NOT NULL
                                      CHECK (task_type IN
                                             ('label', 'summary', 'direction_phrasing')),
        source_fingerprint       TEXT NOT NULL,
        prompt_version           TEXT NOT NULL,
        schema_version           TEXT NOT NULL,
        generation_number        INTEGER NOT NULL CHECK (generation_number >= 1),
        status                   TEXT NOT NULL
                                      CHECK (status IN ('valid', 'superseded_by_merge')),
        payload                  TEXT NOT NULL,
        payload_hash             TEXT NOT NULL CHECK (payload_hash GLOB 'sha256:*'),
        evidence_level           TEXT NOT NULL
                                      CHECK (evidence_level IN
                                             ('post_only', 'abstract', 'full_text')),
        provider_name            TEXT NOT NULL,
        model_name               TEXT NOT NULL,
        usage_tokens_in          INTEGER NULL,
        usage_tokens_out         INTEGER NULL,
        analyzed_at              TEXT NOT NULL
                                      CHECK (analyzed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        accepted_from_attempt_id TEXT NOT NULL,
        moved_by_merge_id        TEXT NULL REFERENCES identity_merge_audit (id)
                                      ON DELETE RESTRICT ON UPDATE RESTRICT
                                      DEFERRABLE INITIALLY DEFERRED,
        {_EXACTLY_ONE_TARGET}
    )
    """,
    """
    CREATE UNIQUE INDEX ux_analysis_valid_key ON analysis
        (owner_id, target_key, task_type, source_fingerprint, prompt_version,
         schema_version, generation_number)
        WHERE status = 'valid'
    """,
    # -- saved_item (MOD-saved-service) ---------------------------------------------------
    # The partial UNIQUE below IS invariant I08: at most one active Saved per target.
    f"""
    CREATE TABLE saved_item (
        id                    TEXT NOT NULL PRIMARY KEY,
        owner_id              TEXT NOT NULL REFERENCES owner (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_kind           TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_work_id        TEXT NULL REFERENCES work (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_post_id        TEXT NULL REFERENCES post (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        {_TARGET_KEY},
        state                 TEXT NOT NULL
                                   CHECK (state IN ('active', 'unsaved', 'superseded_by_merge')),
        saved_at              TEXT NOT NULL
                                   CHECK (saved_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        unsaved_at            TEXT NULL
                                   CHECK (unsaved_at IS NULL
                                          OR unsaved_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        save_channel          TEXT NOT NULL CHECK (save_channel IN ('app', 'telegram')),
        saved_snapshot_id     TEXT NOT NULL REFERENCES saved_snapshot (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        source_report_item_id TEXT NULL,
        idempotency_key       TEXT NULL,
        moved_by_merge_id     TEXT NULL REFERENCES identity_merge_audit (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT
                                   DEFERRABLE INITIALLY DEFERRED,
        {_EXACTLY_ONE_TARGET},
        CHECK ((state = 'unsaved') = (unsaved_at IS NOT NULL))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_saved_active_owner_target ON saved_item (owner_id, target_key)
        WHERE state = 'active'
    """,
    """
    CREATE UNIQUE INDEX ux_saved_idempotency ON saved_item (owner_id, idempotency_key)
        WHERE idempotency_key IS NOT NULL
    """,
    # -- work_label (MOD-analysis-service) -------------------------------------------------
    f"""
    CREATE TABLE work_label (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_kind             TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_work_id          TEXT NULL REFERENCES work (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_post_id          TEXT NULL REFERENCES post (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        {_TARGET_KEY},
        label_text              TEXT NOT NULL CHECK (length(label_text) BETWEEN 1 AND 120),
        analysis_id             TEXT NOT NULL REFERENCES analysis (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        embedding_generation_id TEXT NOT NULL,
        vector                  BLOB NULL,
        created_at              TEXT NOT NULL
                                     CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        {_EXACTLY_ONE_TARGET}
    )
    """,
    """
    CREATE UNIQUE INDEX ux_work_label_owner_target_label_gen ON work_label
        (owner_id, target_key, label_text, embedding_generation_id)
    """,
    # -- first_announced_ledger (MOD-report-service) ---------------------------------------
    # The UNIQUE below IS invariant I07: one canonical work has one first-announcement. The
    # merge's §8.3 hook depends on it -- that is why the winner cannot end up with two rows.
    f"""
    CREATE TABLE first_announced_ledger (
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
    CREATE UNIQUE INDEX ux_first_announced_canonical_work
        ON first_announced_ledger (owner_id, canonical_work_id)
    """,
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE first_announced_ledger",
    "DROP TABLE work_label",
    "DROP TABLE saved_item",
    "DROP TABLE analysis",
    "DROP TABLE saved_snapshot",
)


def upgrade() -> None:
    """Create the five move-set tables."""
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drop them in reverse dependency order."""
    for statement in _DROPS:
        op.execute(statement)
