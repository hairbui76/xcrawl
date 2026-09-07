"""``MOD-saved-service`` takes ownership of ``saved_snapshot`` and ``saved_item``.

Revision ID: 0008_tc_saved_snapshot
Revises: 0007_merge_phase3_5_heads
Create Date: 2026-09-08

What this revision does, and what it deliberately does not
----------------------------------------------------------
Both tables already exist. ``0002b_shared_move_set_tables`` created them **on behalf of this
module** while ``TXN-identity-merge`` needed something to move rows in, and its header says
in as many words that the card taking them over must EXTEND that revision rather than issue a
second ``CREATE TABLE`` (change requests ``CR-TC-IDENTITY-11..13``). So there is no second
``CREATE TABLE saved_item`` here, no re-declaration of columns that are already right, and no
"while I am here" tidying. ``saved_item`` is not touched at all: every column, check, index and
foreign key ``entities.yaml`` ``ENT-saved-item`` asks for is already present.

The single gap: the foreign key on ``analysis_id_at_save``
----------------------------------------------------------
``entities.yaml`` ``ENT-saved-snapshot`` declares ``analysis_id_at_save`` as *"FK →
analysis.id"*, and 0002b left it as a bare ``TEXT NULL`` column with no ``REFERENCES``
clause. It had no choice: it creates ``saved_snapshot`` before ``analysis``, and it was
already carrying two other columns (``first_report_id``, ``source_report_item_id``) whose
target tables do not exist yet.

That missing clause is not cosmetic. ``TXN-delete-target`` narrows the set of deletable
``analysis`` rows to those **not** pointed at by a ``saved_snapshot``, and states its oracle as
*"no deleted ``analysis`` row is still referenced by a ``saved_snapshot`` — checked by FK,
which must be 0 violations"*. Without the constraint, that check has nothing to check: a
delete would silently orphan the analysis a snapshot cites, and the snapshot's
``analysis_ref`` would point into a hole. ``ON DELETE RESTRICT`` is what turns the contract's
sentence into a database guarantee.

Why a rebuild, and why it is safe
---------------------------------
SQLite cannot add a foreign key to an existing column, so the table is rebuilt with the
standard rename/copy/drop dance. Three details make it safe:

1. **Order.** ``saved_item`` is renamed out of the way *first*, so when ``saved_snapshot`` is
   renamed, SQLite rewrites the child's ``REFERENCES saved_snapshot`` to point at the renamed
   parent and the schema stays parseable at every step. Renaming the parent while a child
   still names a table that is about to disappear is what makes this dance fail.
2. **Indexes.** ``ALTER TABLE … RENAME`` carries a table's indexes along under their original
   names, so the two ``saved_item`` indexes are dropped before the rename and recreated
   afterwards, byte-identical to 0002b's definitions.
3. **Rows.** Existing rows are copied, not discarded. ``saved_item.target_key`` is a STORED
   generated column and so is omitted from both the column list and the SELECT — SQLite
   recomputes it, which is the property that makes "the key moved" and "the pointer moved"
   impossible to disagree about.

The copy is where the new constraint is first enforced: if some ``saved_snapshot`` row already
cited an ``analysis`` row that is not there, this migration fails loudly instead of blessing
it. That is the intended behaviour — the alternative is to keep pretending the reference is
sound.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0008_tc_saved_snapshot"
down_revision: str | None = "0007_merge_phase3_5_heads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps), spelled
#: exactly as ``0002b_shared_move_set_tables`` spells it.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

#: ``saved_snapshot`` as 0002b defined it, plus the one clause this revision adds.
#: Everything else -- column order, types, NOT NULL, the ``content_hash`` GLOB check, the
#: ``created_at`` timestamp check -- is unchanged, so a diff of the two definitions shows one
#: line.
_SAVED_SNAPSHOT_NEW = f"""
CREATE TABLE saved_snapshot (
    id                  TEXT NOT NULL PRIMARY KEY,
    owner_id            TEXT NOT NULL REFERENCES owner (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    target_kind         TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
    target_key_at_save  TEXT NOT NULL,
    analysis_id_at_save TEXT NULL REFERENCES analysis (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    payload             TEXT NOT NULL,
    content_hash        TEXT NOT NULL CHECK (content_hash GLOB 'sha256:*'),
    created_at          TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

#: 0002b's definition, restored verbatim on downgrade.
_SAVED_SNAPSHOT_OLD = f"""
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
"""

_SNAPSHOT_COLUMNS = (
    "id, owner_id, target_kind, target_key_at_save, analysis_id_at_save,"
    " payload, content_hash, created_at"
)

#: The two ``saved_item`` indexes of 0002b. Dropped before the rename and recreated after,
#: because a renamed table keeps its indexes and the names would then be taken.
_SAVED_ITEM_INDEXES: tuple[str, ...] = (
    """
    CREATE UNIQUE INDEX ux_saved_active_owner_target ON saved_item (owner_id, target_key)
        WHERE state = 'active'
    """,
    """
    CREATE UNIQUE INDEX ux_saved_idempotency ON saved_item (owner_id, idempotency_key)
        WHERE idempotency_key IS NOT NULL
    """,
)

#: Explicit column list: ``target_key`` is generated and must not be written.
_SAVED_ITEM_COLUMNS = (
    "id, owner_id, target_kind, target_work_id, target_post_id, state, saved_at,"
    " unsaved_at, save_channel, saved_snapshot_id, source_report_item_id,"
    " idempotency_key, moved_by_merge_id"
)

_SAVED_ITEM = f"""
CREATE TABLE saved_item (
    id                    TEXT NOT NULL PRIMARY KEY,
    owner_id              TEXT NOT NULL REFERENCES owner (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
    target_kind           TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
    target_work_id        TEXT NULL REFERENCES work (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
    target_post_id        TEXT NULL REFERENCES post (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
    target_key TEXT GENERATED ALWAYS AS
        (target_kind || ':' || COALESCE(target_work_id, target_post_id)) STORED,
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
    CHECK ((target_kind = 'work' AND target_work_id IS NOT NULL AND target_post_id IS NULL)
           OR (target_kind = 'post' AND target_post_id IS NOT NULL AND target_work_id IS NULL)),
    CHECK ((state = 'unsaved') = (unsaved_at IS NOT NULL))
)
"""


def _rebuild(snapshot_ddl: str) -> tuple[str, ...]:
    """The rename/copy/drop sequence, parameterised by which ``saved_snapshot`` to build.

    Shared by :func:`upgrade` and :func:`downgrade` so the two directions cannot drift: the
    only difference between them is one ``REFERENCES`` clause.
    """
    return (
        "DROP INDEX ux_saved_active_owner_target",
        "DROP INDEX ux_saved_idempotency",
        # The child is renamed first; renaming the parent afterwards rewrites this table's
        # `REFERENCES saved_snapshot` to `saved_snapshot_old` for us.
        "ALTER TABLE saved_item RENAME TO saved_item_old",
        "ALTER TABLE saved_snapshot RENAME TO saved_snapshot_old",
        snapshot_ddl,
        _SAVED_ITEM,
        f"INSERT INTO saved_snapshot ({_SNAPSHOT_COLUMNS})"
        f" SELECT {_SNAPSHOT_COLUMNS} FROM saved_snapshot_old",
        f"INSERT INTO saved_item ({_SAVED_ITEM_COLUMNS})"
        f" SELECT {_SAVED_ITEM_COLUMNS} FROM saved_item_old",
        "DROP TABLE saved_item_old",
        "DROP TABLE saved_snapshot_old",
        *_SAVED_ITEM_INDEXES,
    )


def upgrade() -> None:
    """Add ``saved_snapshot.analysis_id_at_save -> analysis(id) ON DELETE RESTRICT``."""
    for statement in _rebuild(_SAVED_SNAPSHOT_NEW):
        op.execute(statement)


def downgrade() -> None:
    """Restore 0002b's ``saved_snapshot``, without the foreign key."""
    for statement in _rebuild(_SAVED_SNAPSHOT_OLD):
        op.execute(statement)
