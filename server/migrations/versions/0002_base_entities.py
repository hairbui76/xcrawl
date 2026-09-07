"""Base entities shared by the Phase 1 cards: ``owner``, ``work``, ``post``, ``post_work``.

Revision ID: 0002_base_entities
Revises: 0001
Create Date: 2026-09-07

Why this revision exists
------------------------
``TC-canonical-identity-merge`` and ``TC-ingest-idempotent-ack-lost`` both need the same four
tables: an ingest batch writes ``post``/``post_work`` and the identity service owns ``work``.
Putting them in one revision keeps a single definition of each table, as the Phase 1 dispatch
requires. The identity-specific tables live in the next revision.

One definition per table (finding ``F-A3R1-01``)
------------------------------------------------
This revision is the **sole** ``CREATE TABLE owner``. Two revisions used to create it with
different constraint sets, both guarded by ``IF NOT EXISTS``, so the shipped schema depended on
which branch Alembic happened to traverse first -- the database stopped being a function of
``contracts/data/entities.yaml``. The definition below carries the full ``ENT-owner`` set,
including the four credential columns added by amendment ``AMD-ENT-owner-01``
(``CR-TC-AUTH-02`` / ``CR-TC-AUTH-03``), the ``display_name`` length CHECK and the
``created_at`` timestamp CHECK (``F-A3R1-14``); ``0002_tc_owner_auth_session`` creates
``session`` only and depends on this revision.

``post.ingest_receipt_id`` (finding ``F-A3R1-05``)
--------------------------------------------------
``entities.yaml`` requires ``post.ingest_receipt_id -> ingest_receipt(id)``. ``ingest_receipt``
belongs to ``TC-ingest-idempotent-ack-lost`` and is created two revisions later, and SQLite
cannot add a foreign key to an existing table without a full table rebuild. The two options were
to pull ``ingest_receipt`` into this revision or to have the ingest revision rebuild ``post``.
**Agreed choice: the ingest revision rebuilds ``post``** -- pulling ``ingest_receipt`` here would
repeat exactly the ownership mistake ``F-A3R1-04`` was raised about, whereas the rebuild happens
inside the revision that owns the referenced table, on an empty table, in one place. The column
keeps its name, type and NOT NULL here; ``CR-TC-IDENTITY-14`` carries the request to the ingest
card, which must document the mirror image of this paragraph.

Other cross-revision references
-------------------------------
* ``work.current_work_version_id`` and ``post_work.moved_by_merge_id`` DO keep their
  ``REFERENCES`` clauses: ``work_version`` and ``identity_merge_audit`` are created in the very
  next revision, and no row carrying a non-NULL value can exist before then. The reference to
  ``identity_merge_audit`` is ``DEFERRABLE INITIALLY DEFERRED`` because ``TXN-identity-merge``
  moves the rows and writes the audit row in ONE transaction; checking at COMMIT is what makes
  "no merge without an audit row" enforceable by the database rather than by convention.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0002_base_entities"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_STATEMENTS: tuple[str, ...] = (
    # -- owner -------------------------------------------------------------------------
    # entities.yaml `owner` in full: exactly one row (CHECK + UNIQUE), the display-name length
    # rule, the millisecond timestamp shape, and the four credential columns of
    # AMD-ENT-owner-01. The credential columns live on the owner row, not in process memory,
    # because a lockout counter that a restart clears is not a lockout (F-A3R1-06).
    # `password_hash` NULL means "no credential yet" -- never an empty password.
    f"""
    CREATE TABLE owner (
        id                  TEXT    NOT NULL PRIMARY KEY,
        singleton_guard     INTEGER NOT NULL CHECK (singleton_guard = 1),
        display_name        TEXT    NOT NULL
                                    CHECK (length(display_name) BETWEEN 1 AND 120),
        timezone_iana       TEXT    NOT NULL CHECK (length(timezone_iana) >= 1),
        created_at          TEXT    NOT NULL
                                    CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        password_hash       TEXT        NULL,
        password_updated_at TEXT        NULL
                                    CHECK (password_updated_at IS NULL
                                           OR password_updated_at GLOB
                                              '{TIMESTAMP_UTC_MS_GLOB}'),
        failed_login_count  INTEGER NOT NULL DEFAULT 0 CHECK (failed_login_count >= 0),
        locked_until        TEXT        NULL
                                    CHECK (locked_until IS NULL
                                           OR locked_until GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        CHECK ((password_hash IS NULL) = (password_updated_at IS NULL))
    )
    """,
    "CREATE UNIQUE INDEX ux_owner_singleton ON owner (singleton_guard)",
    # -- work --------------------------------------------------------------------------
    # `identity_state` closes over three values; `merged_into_work_id` is NOT NULL if and
    # only if the row is `merged` (entities.yaml `work`), and never points at itself.
    f"""
    CREATE TABLE work (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        canonical_doi           TEXT NULL,
        canonical_arxiv_id      TEXT NULL,
        title                   TEXT NULL,
        paper_url               TEXT NULL,
        code_url                TEXT NULL,
        current_work_version_id TEXT NULL REFERENCES work_version (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        metadata_state          TEXT NOT NULL
                                     CHECK (metadata_state IN
                                            ('none', 'partial', 'complete', 'unavailable')),
        identity_state          TEXT NOT NULL
                                     CHECK (identity_state IN
                                            ('active', 'merged', 'quarantined')),
        merged_into_work_id     TEXT NULL REFERENCES work (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        first_discovered_at     TEXT    NOT NULL
                                     CHECK (first_discovered_at GLOB
                                            '{TIMESTAMP_UTC_MS_GLOB}'),
        ingest_sequence         INTEGER NOT NULL CHECK (ingest_sequence >= 1),
        content_state           TEXT    NOT NULL
                                     CHECK (content_state IN
                                            ('present', 'redacted_by_owner_deletion')),
        created_at              TEXT    NOT NULL
                                     CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        CHECK (merged_into_work_id IS NULL OR merged_into_work_id <> id),
        CHECK ((identity_state = 'merged') = (merged_into_work_id IS NOT NULL))
    )
    """,
    # Partial UNIQUE excluding `merged`: the losing row keeps its old canonical value as
    # evidence without colliding with the winner (entities.yaml `work.keys.note`, B15).
    """
    CREATE UNIQUE INDEX ux_work_owner_canonical_doi ON work (owner_id, canonical_doi)
        WHERE canonical_doi IS NOT NULL AND identity_state <> 'merged'
    """,
    """
    CREATE UNIQUE INDEX ux_work_owner_canonical_arxiv_id ON work (owner_id, canonical_arxiv_id)
        WHERE canonical_arxiv_id IS NOT NULL AND identity_state <> 'merged'
    """,
    "CREATE UNIQUE INDEX ux_work_owner_ingest_sequence ON work (owner_id, ingest_sequence)",
    "CREATE INDEX ix_work_merged_into ON work (merged_into_work_id)",
    # -- post --------------------------------------------------------------------------
    # The value CHECKs come from the ingest card's own first version of this table and are
    # kept here so moving the table did not weaken it: `x_post_id` is digits (IDs travel as
    # strings, SRC-PLAN §5.1), `url` is https, timestamps carry milliseconds, the snapshot
    # hash is a sha256, and `ingest_sequence` starts at 1. `discovered_by_run_id` and
    # `ingest_receipt_id` keep their shape but not their REFERENCES clause -- see the header.
    f"""
    CREATE TABLE post (
        id                         TEXT NOT NULL PRIMARY KEY,
        owner_id                   TEXT NOT NULL REFERENCES owner (id)
                                        ON DELETE RESTRICT ON UPDATE RESTRICT,
        x_post_id                  TEXT    NOT NULL CHECK (x_post_id GLOB '[0-9]*'),
        author_handle              TEXT    NOT NULL,
        author_display_name        TEXT    NULL,
        author_x_user_id           TEXT    NULL,
        url                        TEXT    NOT NULL CHECK (url GLOB 'https://*'),
        text                       TEXT    NOT NULL,
        lang                       TEXT    NULL,
        published_at               TEXT    NULL
                                        CHECK (published_at IS NULL
                                               OR published_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        discovered_at              TEXT    NOT NULL
                                        CHECK (discovered_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        ingest_sequence            INTEGER NOT NULL CHECK (ingest_sequence >= 1),
        collected_at_client        TEXT    NULL,
        discovered_by_run_id       TEXT    NOT NULL,
        ingest_receipt_id          TEXT    NOT NULL,
        thread_root_x_post_id      TEXT    NULL,
        is_author_thread_member    INTEGER NOT NULL CHECK (is_author_thread_member IN (0, 1)),
        media_refs                 TEXT    NOT NULL,
        referenced_links           TEXT    NOT NULL,
        identity_resolution        TEXT    NOT NULL
                                        CHECK (identity_resolution IN
                                               ('pending', 'resolved_linked',
                                                'resolved_post_only', 'conflict')),
        source_snapshot_hash       TEXT    NOT NULL
                                        CHECK (source_snapshot_hash GLOB 'sha256:*'),
        content_state              TEXT    NOT NULL DEFAULT 'present'
                                        CHECK (content_state IN
                                               ('present', 'redacted_by_owner_deletion')),
        source_deleted_observed_at TEXT    NULL
                                        CHECK (source_deleted_observed_at IS NULL
                                               OR source_deleted_observed_at GLOB
                                                  '{TIMESTAMP_UTC_MS_GLOB}')
    )
    """,
    "CREATE UNIQUE INDEX ux_post_owner_x_post_id ON post (owner_id, x_post_id)",
    "CREATE UNIQUE INDEX ux_post_owner_ingest_sequence ON post (owner_id, ingest_sequence)",
    # -- post_work ---------------------------------------------------------------------
    f"""
    CREATE TABLE post_work (
        id                TEXT NOT NULL PRIMARY KEY,
        owner_id          TEXT NOT NULL REFERENCES owner (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        post_id           TEXT NOT NULL REFERENCES post (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        work_id           TEXT NOT NULL REFERENCES work (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        link_evidence     TEXT NOT NULL
                               CHECK (link_evidence IN
                                      ('explicit_url_in_post', 'arxiv_api_lookup',
                                       'openalex_api_lookup', 'owner_manual')),
        linked_at         TEXT NOT NULL
                               CHECK (linked_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        moved_by_merge_id TEXT NULL REFERENCES identity_merge_audit (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT
                               DEFERRABLE INITIALLY DEFERRED
    )
    """,
    "CREATE UNIQUE INDEX ux_post_work_owner_post_work ON post_work (owner_id, post_id, work_id)",
    "CREATE INDEX ix_post_work_work ON post_work (work_id)",
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE post_work",
    "DROP TABLE post",
    "DROP TABLE work",
    "DROP TABLE owner",
)


def upgrade() -> None:
    """Create the four shared base tables."""
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drop the four tables, in reverse dependency order."""
    for statement in _DROPS:
        op.execute(statement)
