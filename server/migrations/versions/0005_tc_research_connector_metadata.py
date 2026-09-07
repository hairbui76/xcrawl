"""``source_fetch_log``: provenance of every arXiv/OpenAlex call.

Revision ID: 0005_tc_research_connector_metadata
Revises: 0004_merge_phase1_heads
Create Date: 2026-09-07

Card: ``agent-tasks/TC-research-connector-metadata.md`` §4 (state effects).
Source of truth: ``contracts/data/entities.yaml`` entity ``source_fetch_log``
(``ENT-source-fetch-log``, ``owner_module: MOD-research-connector``, ``owned_by_package: PC05``).

One table, eight columns, no more
---------------------------------
The contract declares exactly eight fields and this revision creates exactly those eight. It
does **not** add a ``run_id``, a duration or a retry counter, however useful they might look:
a migration that invents columns makes the schema and the contract disagree, and
``tests/contract/test_schema_matches_entities.py`` is the gate that would then have to be
argued with.

Two closed enums are enforced as CHECK constraints rather than left to the application:

``source_type``  ``arxiv_api | openalex_api`` -- the two hosts of
                 ``contracts/modules.yaml`` ``network_egress``. A third value in this column
                 would be a record of a call to a source the module may not reach.
``outcome``      ``ok | not_found | rate_limited | error | timeout_unknown``.
                 ``timeout_unknown`` is separate from ``error`` because retry-policy
                 ``RP-01`` makes it a different fact: a transport timeout is an *unknown*
                 result, not an observed failure, and collapsing the two would let a replay
                 decision be made on evidence that does not exist.

``work_id`` is nullable with ``ON DELETE RESTRICT``: a lookup often happens before any work
row exists, and a work that has been fetched for may not be deleted out from under its own
provenance. ``requested_at`` carries the millisecond-precision RFC 3339 GLOB every
``timestamp_utc_ms`` column in this schema carries (``entities.yaml`` §conventions, AMD-B08,
finding ``F-A3R1-14``), so a wrongly-shaped timestamp is refused at the row rather than
discovered later by something that sorts strings.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0005_tc_research_connector_metadata"
down_revision: str | None = "0004_merge_phase1_heads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_STATEMENTS: tuple[str, ...] = (
    f"""
    CREATE TABLE source_fetch_log (
        id            TEXT NOT NULL PRIMARY KEY,
        owner_id      TEXT NOT NULL REFERENCES owner (id) ON DELETE RESTRICT,
        source_type   TEXT NOT NULL,
        endpoint      TEXT NOT NULL,
        requested_at  TEXT NOT NULL,
        outcome       TEXT NOT NULL,
        response_hash TEXT NULL,
        work_id       TEXT NULL REFERENCES work (id) ON DELETE RESTRICT,

        CHECK (length(id) = 26),
        CHECK (source_type IN ('arxiv_api', 'openalex_api')),
        CHECK (outcome IN ('ok', 'not_found', 'rate_limited', 'error', 'timeout_unknown')),
        CHECK (requested_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        -- entities.yaml types response_hash as hash_sha256: 64 lowercase hex characters.
        CHECK (response_hash IS NULL OR
               (length(response_hash) = 64 AND response_hash NOT GLOB '*[^0-9a-f]*'))
    )
    """,
    # Health and rate auditing both read "the recent calls for one source", and a work
    # detail page reads "the calls made for this work". Two indexes, one per question.
    """
    CREATE INDEX ix_source_fetch_log_owner_source_time
        ON source_fetch_log (owner_id, source_type, requested_at)
    """,
    "CREATE INDEX ix_source_fetch_log_work ON source_fetch_log (work_id)",
)

_DOWN: tuple[str, ...] = (
    "DROP INDEX IF EXISTS ix_source_fetch_log_work",
    "DROP INDEX IF EXISTS ix_source_fetch_log_owner_source_time",
    "DROP TABLE IF EXISTS source_fetch_log",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DOWN:
        op.execute(statement)
