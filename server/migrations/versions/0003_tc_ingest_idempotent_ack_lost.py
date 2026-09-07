"""Tables owned by MOD-ingest-service: ``ingest_receipt`` and ``checkpoint``.

Revision ID: 0003_tc_ingest_idempotent_ack_lost
Revises: 0002_base_entities
Create Date: 2026-09-07

Card: ``agent-tasks/TC-ingest-idempotent-ack-lost.md``.
Source of truth: ``contracts/data/entities.yaml`` entities ``ENT-ingest-receipt`` and
``ENT-checkpoint``, and transactions ``TXN-ingest-batch`` / ``TXN-checkpoint-only``. The DDL
below is written from that contract, column by column; it is not reverse-engineered from
code and there is no ORM metadata behind it.

Why ``post`` is not here
------------------------
``post`` is created by ``0002_base_entities``, the shared revision written by
``TC-canonical-identity-merge`` because ``post``, ``post_work``, ``work`` and ``owner`` are
needed by both cards. Creating it again here would put two definitions of one table on one
migration chain. This revision therefore chains *after* that one and adds only the two
tables no other card needs.

Three deliberate decisions, all reported in the card handoff:

1. **Deferred foreign keys between the two tables.** ``ingest_receipt.checkpoint_id`` points
   at ``checkpoint`` and ``checkpoint.created_by_receipt_id`` points back at
   ``ingest_receipt``. Both rows are written in ONE transaction (``TXN-ingest-batch``), so
   the cycle can only be satisfied if the constraints are checked at COMMIT.
   ``DEFERRABLE INITIALLY DEFERRED`` makes the contract's "rows written together" literally
   enforceable: a partial write fails at the commit point instead of being accepted.

2. **``post.ingest_receipt_id`` keeps no REFERENCES clause.** ``0002_base_entities`` left it
   as a bare NOT NULL column and noted that this card would add the constraint once
   ``ingest_receipt`` exists. SQLite cannot add a foreign key to an existing table without a
   full twelve-step table rebuild, and rebuilding another card's table from this revision
   would put this card's hands on rows it does not own. The column keeps its shape; the
   constraint is left for a coordinated revision. See ``CR-TC-ingest-01``.

3. **Cross-card columns stay columns.** ``ingest_receipt.run_id -> run(id)`` and
   ``ingest_receipt.lease_id -> assignment_lease(id)`` reference tables owned by
   ``TC-scheduler-lease-claim``, which has not created them. SQLite resolves REFERENCES at
   DML time, so declaring them now would turn every INSERT into "no such table".

SQLite notes: ``sequence`` is quoted throughout; booleans are INTEGER 0/1 and JSON columns
are TEXT, per ``entities.yaml`` §conventions ``sql_affinity``.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0003_tc_ingest_idempotent_ack_lost"

#: Single parent: ``post`` must exist before this revision can point a foreign key at it and
#: before it can rebuild the table (see ``upgrade``). The three Phase 1 branches are joined by
#: ``0004_merge_phase1_heads``, which is the one merge point; carrying a second merge here as
#: well made the same two revisions ancestors twice over and left the history harder to read
#: than the problem it solved.
down_revision: str | None = "0002_base_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

CHECKPOINT_DDL = f"""
CREATE TABLE checkpoint (
    id                            TEXT    NOT NULL PRIMARY KEY,
    owner_id                      TEXT    NOT NULL
        REFERENCES owner (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    run_id                        TEXT    NOT NULL,
    phase                         TEXT    NOT NULL
        CHECK (phase IN ('collecting', 'enriching', 'analyzing', 'reporting')),
    "sequence"                    INTEGER NOT NULL CHECK ("sequence" >= 0),
    cursor_token                  TEXT        NULL,
    cursor_state                  TEXT    NOT NULL
        CHECK (cursor_state IN ('valid', 'invalidated')),
    acked_through_ingest_sequence INTEGER NOT NULL CHECK (acked_through_ingest_sequence >= 0),
    items_ingested_total          INTEGER NOT NULL CHECK (items_ingested_total >= 0),
    created_at                    TEXT    NOT NULL
        CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    created_by_receipt_id         TEXT        NULL
        REFERENCES ingest_receipt (id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT ux_checkpoint_run_sequence UNIQUE (owner_id, run_id, "sequence")
)
"""

INGEST_RECEIPT_DDL = f"""
CREATE TABLE ingest_receipt (
    id                  TEXT    NOT NULL PRIMARY KEY,
    owner_id            TEXT    NOT NULL
        REFERENCES owner (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    receipt_kind        TEXT    NOT NULL
        CHECK (receipt_kind IN ('batch_ingest', 'checkpoint_only')),
    idempotency_key     TEXT    NOT NULL
        CHECK (length(idempotency_key) BETWEEN 16 AND 128),
    request_id          TEXT    NOT NULL,
    payload_hash        TEXT    NOT NULL CHECK (payload_hash GLOB 'sha256:*'),
    schema_version      TEXT    NOT NULL,
    run_id              TEXT    NOT NULL,
    job_id              TEXT    NOT NULL,
    lease_id            TEXT    NOT NULL,
    lease_epoch         INTEGER NOT NULL CHECK (lease_epoch >= 1),
    items_received      INTEGER NOT NULL CHECK (items_received >= 0),
    posts_inserted      INTEGER NOT NULL CHECK (posts_inserted >= 0),
    posts_duplicate     INTEGER NOT NULL CHECK (posts_duplicate >= 0),
    items_rejected      INTEGER NOT NULL CHECK (items_rejected >= 0),
    works_linked        INTEGER NOT NULL CHECK (works_linked >= 0),
    checkpoint_id       TEXT    NOT NULL
        REFERENCES checkpoint (id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    max_ingest_sequence INTEGER NOT NULL CHECK (max_ingest_sequence >= 0),
    committed_at        TEXT    NOT NULL
        CHECK (committed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    receipt_hash        TEXT    NOT NULL CHECK (receipt_hash GLOB 'sha256:*'),
    CONSTRAINT ck_ingest_receipt_counts
        CHECK (posts_inserted + posts_duplicate + items_rejected = items_received),
    CONSTRAINT ck_ingest_receipt_checkpoint_only_is_empty
        CHECK (
            receipt_kind <> 'checkpoint_only'
            OR (items_received = 0 AND posts_inserted = 0
                AND posts_duplicate = 0 AND items_rejected = 0 AND works_linked = 0)
        ),
    CONSTRAINT ux_ingest_receipt_owner_idempotency_key UNIQUE (owner_id, idempotency_key)
)
"""


#: Column list of ``post`` as ``0002_base_entities`` creates it, in order. Named explicitly
#: rather than using ``SELECT *`` so that a column added to the base revision without a
#: matching change here fails loudly at migration time instead of shifting values silently
#: into the wrong columns.
POST_COLUMNS = (
    "id, owner_id, x_post_id, author_handle, author_display_name, author_x_user_id, "
    "url, text, lang, published_at, discovered_at, ingest_sequence, collected_at_client, "
    "discovered_by_run_id, ingest_receipt_id, thread_root_x_post_id, "
    "is_author_thread_member, media_refs, referenced_links, identity_resolution, "
    "source_snapshot_hash, content_state, source_deleted_observed_at"
)

POST_REBUILT_DDL = """
CREATE TABLE post_rebuilt (
    id                         TEXT NOT NULL PRIMARY KEY,
    owner_id                   TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
    x_post_id                  TEXT    NOT NULL,
    author_handle              TEXT    NOT NULL,
    author_display_name        TEXT    NULL,
    author_x_user_id           TEXT    NULL,
    url                        TEXT    NOT NULL,
    text                       TEXT    NOT NULL,
    lang                       TEXT    NULL,
    published_at               TEXT    NULL,
    discovered_at              TEXT    NOT NULL,
    ingest_sequence            INTEGER NOT NULL,
    collected_at_client        TEXT    NULL,
    discovered_by_run_id       TEXT    NOT NULL,
    ingest_receipt_id          TEXT    NOT NULL REFERENCES ingest_receipt (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT
                                    DEFERRABLE INITIALLY DEFERRED,
    thread_root_x_post_id      TEXT    NULL,
    is_author_thread_member    INTEGER NOT NULL CHECK (is_author_thread_member IN (0, 1)),
    media_refs                 TEXT    NOT NULL,
    referenced_links           TEXT    NOT NULL,
    identity_resolution        TEXT    NOT NULL
                                    CHECK (identity_resolution IN
                                           ('pending', 'resolved_linked',
                                            'resolved_post_only', 'conflict')),
    source_snapshot_hash       TEXT    NOT NULL,
    content_state              TEXT    NOT NULL
                                    CHECK (content_state IN
                                           ('present', 'redacted_by_owner_deletion')),
    source_deleted_observed_at TEXT    NULL
)
"""

#: The SQLite table rebuild that gives ``post.ingest_receipt_id`` its foreign key
#: (finding ``F-A3R1-05``). Everything except the CREATE and the two index rebuilds is the
#: standard procedure from the SQLite manual's "Making Other Kinds Of Table Schema Changes".
POST_REBUILD_STEPS: tuple[str, ...] = (
    # Alembic runs a revision inside a transaction, and `PRAGMA foreign_keys` is a no-op
    # there. `defer_foreign_keys` is the pragma that DOES work inside one: it postpones every
    # foreign key check to COMMIT, which is exactly what a drop-and-rename needs, and it
    # resets itself at the end of the transaction so it cannot leak into application code.
    "PRAGMA defer_foreign_keys = ON",
    POST_REBUILT_DDL,
    f"INSERT INTO post_rebuilt ({POST_COLUMNS}) SELECT {POST_COLUMNS} FROM post",
    "DROP TABLE post",
    "ALTER TABLE post_rebuilt RENAME TO post",
    # Indexes belong to the dropped table and do not survive it.
    "CREATE UNIQUE INDEX ux_post_owner_x_post_id ON post (owner_id, x_post_id)",
    "CREATE UNIQUE INDEX ux_post_owner_ingest_sequence ON post (owner_id, ingest_sequence)",
)


def upgrade() -> None:
    """Create the two tables of ``MOD-ingest-service``.

    ``checkpoint`` first: SQLite resolves REFERENCES lazily, so the forward reference from
    ``checkpoint.created_by_receipt_id`` to a table that does not exist yet is legal at
    CREATE time and is resolved before any DML runs.
    """
    op.execute(CHECKPOINT_DDL)
    op.execute(INGEST_RECEIPT_DDL)
    op.execute('CREATE INDEX ix_checkpoint_owner_run ON checkpoint (owner_id, run_id, "sequence")')
    op.execute(
        "CREATE INDEX ix_ingest_receipt_owner_run ON ingest_receipt (owner_id, run_id, "
        "max_ingest_sequence)"
    )
    for statement in POST_REBUILD_STEPS:
        op.execute(statement)


def downgrade() -> None:
    """Drop in reverse dependency order, and give ``post`` its pre-rebuild shape back.

    A downgrade that left ``post.ingest_receipt_id`` pointing at a table this revision is
    about to drop would produce a database that cannot accept a single insert.
    """
    op.execute("PRAGMA defer_foreign_keys = ON")
    op.execute(POST_REBUILT_DDL.replace("REFERENCES ingest_receipt (id)", "-- no reference"))
    op.execute(f"INSERT INTO post_rebuilt ({POST_COLUMNS}) SELECT {POST_COLUMNS} FROM post")
    op.execute("DROP TABLE post")
    op.execute("ALTER TABLE post_rebuilt RENAME TO post")
    op.execute("CREATE UNIQUE INDEX ux_post_owner_x_post_id ON post (owner_id, x_post_id)")
    op.execute(
        "CREATE UNIQUE INDEX ux_post_owner_ingest_sequence ON post (owner_id, ingest_sequence)"
    )
    op.execute("DROP TABLE IF EXISTS ingest_receipt")
    op.execute("DROP TABLE IF EXISTS checkpoint")
