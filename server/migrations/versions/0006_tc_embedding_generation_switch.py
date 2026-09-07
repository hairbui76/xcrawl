"""``embedding_generation`` and ``tag_vector``: the two tables ``MOD-embedding-service`` owns.

Revision ID: 0006_tc_embedding_generation_switch
Revises: 0005_tc_research_connector_metadata
Create Date: 2026-09-08

Card: ``agent-tasks/TC-embedding-generation-switch.md`` §4 (state effects), §6 (I12).
Source of truth: ``contracts/data/entities.yaml`` entities ``embedding_generation``
(``ENT-embedding-generation``) and ``tag_vector`` (``ENT-tag-vector``), both
``owner_module: MOD-embedding-service`` (``contracts/modules.yaml`` ``data_owner_of``).

Why the two partial/total unique indexes carry the whole invariant
-----------------------------------------------------------------
``ux_embedding_generation_active`` is ``UNIQUE(owner_id) WHERE state = 'active'``. That one
index is what makes "switching the active generation is atomic" a property of the database
rather than a property of the code that happens to be careful: with it in place there is no
observable instant at which two rows are ``active``, and the retire-then-activate pair
inside one ``BEGIN…COMMIT`` cannot half-apply. Fixture
``acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`` asserts
``embedding_generation[state='active'] == 1`` after every event, including the refused one.

``ux_embedding_generation_model`` is total, over
``(owner_id, model_name, model_version, dimension, normalization)``. It is the durable half
of ``embedding.start_generation_rebuild``'s idempotency rule ("cùng model mục tiêu không
dựng hai generation song song", ``contracts/ports.yaml``): two concurrent rebuild commands
for the same target model cannot both insert, so exactly one wins and the loser reads the
winner's row instead of building a second copy of the same generation.

What is enforced here and what deliberately is not
--------------------------------------------------
Enforced as CHECKs: the closed enums (``normalization``, ``state``), ``dimension > 0``
(``entities.yaml`` writes it into the field's constraints and I12 rests on it), the
non-negative counters, the ULID length, the millisecond-precision RFC 3339 GLOB every
``timestamp_utc_ms`` column in this schema carries, and ``activated_at IS NOT NULL`` once a
generation has left ``building`` -- the contract's "NOT NULL khi state ∈ {active, retired}"
written as SQL rather than left to the application.

**Not** enforced here, on purpose:

``length(tag_vector.vector) == embedding_generation.dimension``
    ``entities.yaml`` states it, and SQLite CHECK constraints cannot read another table. It
    is enforced in :mod:`server.app.embedding.repository` at every insert, and asserted by
    ``tests/contract/test_embedding_generation_guard.py``. A CHECK that pretended to cover
    it would be worse than none.

``work_label.embedding_generation_id`` remains without a REFERENCES clause
    That column shipped in ``0002b_shared_move_set_tables`` before this table existed, and
    SQLite cannot add a foreign key to an existing table without rebuilding it. Rebuilding
    a table this card does not own, to add a constraint no test in this card needs, is a
    larger risk than the one it removes; it is recorded as ``CR-TC-embedding-01`` in the
    handoff instead of done quietly here.

``built_vector_count >= expected_vector_count``
    Not a table invariant: it is false for every generation while it is still ``building``,
    which is the normal state. It is the *activation* guard, and it lives in
    :func:`server.app.embedding.service.activate_generation` where it can refuse with
    ``EMBEDDING_GENERATION_MISMATCH`` instead of raising an opaque integrity error.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_tc_embedding_generation_switch"
down_revision: str | None = "0005_tc_research_connector_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_STATEMENTS: tuple[str, ...] = (
    f"""
    CREATE TABLE embedding_generation (
        id                    TEXT NOT NULL PRIMARY KEY,
        owner_id              TEXT NOT NULL REFERENCES owner (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        model_name            TEXT NOT NULL,
        model_version         TEXT NOT NULL,
        dimension             INTEGER NOT NULL,
        normalization         TEXT NOT NULL,
        state                 TEXT NOT NULL,
        expected_vector_count INTEGER NULL,
        built_vector_count    INTEGER NOT NULL DEFAULT 0,
        created_at            TEXT NOT NULL,
        activated_at          TEXT NULL,

        CHECK (length(id) = 26),
        CHECK (length(model_name) BETWEEN 1 AND 200),
        -- entities.yaml: "Phiên bản/revision của model; không dùng `latest`."
        CHECK (length(model_version) BETWEEN 1 AND 100 AND model_version <> 'latest'),
        CHECK (dimension > 0),
        CHECK (normalization IN ('l2', 'none')),
        CHECK (state IN ('building', 'active', 'retired')),
        CHECK (expected_vector_count IS NULL OR expected_vector_count >= 0),
        CHECK (built_vector_count >= 0),
        CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        CHECK (activated_at IS NULL OR activated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        -- "NOT NULL khi state ∈ {{active, retired}}" (entities.yaml, activated_at).
        CHECK (state = 'building' OR activated_at IS NOT NULL)
    )
    """,
    # I12, as an index. See the module docstring.
    """
    CREATE UNIQUE INDEX ux_embedding_generation_active
        ON embedding_generation (owner_id)
        WHERE state = 'active'
    """,
    """
    CREATE UNIQUE INDEX ux_embedding_generation_model
        ON embedding_generation (owner_id, model_name, model_version, dimension, normalization)
    """,
    """
    CREATE TABLE tag_vector (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        subject_type            TEXT NOT NULL,
        subject_id              TEXT NOT NULL,
        embedding_generation_id TEXT NOT NULL REFERENCES embedding_generation (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        vector                  BLOB NOT NULL,

        CHECK (length(id) = 26),
        CHECK (subject_type IN ('tag', 'tag_alias', 'tag_exclusion')),
        CHECK (length(subject_id) = 26),
        CHECK (length(vector) > 0)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_tag_vector_subject_generation
        ON tag_vector (owner_id, subject_type, subject_id, embedding_generation_id)
    """,
    # Selection reads "every vector of generation G" and the coverage counter reads "how
    # many rows does G have". Both are the same access path, so one index answers both.
    "CREATE INDEX ix_tag_vector_generation ON tag_vector (embedding_generation_id)",
)

_DOWN: tuple[str, ...] = (
    "DROP INDEX IF EXISTS ix_tag_vector_generation",
    "DROP INDEX IF EXISTS ux_tag_vector_subject_generation",
    "DROP TABLE IF EXISTS tag_vector",
    "DROP INDEX IF EXISTS ux_embedding_generation_model",
    "DROP INDEX IF EXISTS ux_embedding_generation_active",
    "DROP TABLE IF EXISTS embedding_generation",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DOWN:
        op.execute(statement)
