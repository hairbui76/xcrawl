"""TC-tag-service: ``tag_alias``, ``tag_exclusion``, ``tag_config_version``.

``tag`` and ``rescan_ledger`` already exist -- ``0013_tc_backfill_pending_ledger`` created them
on behalf of ``MOD-tag-service`` because the backfill ledger needed a tag row to point at. The
three tables below are the rest of the module's ``data_owner_of`` in ``contracts/modules.yaml``
and had no card until ``OD-20261017-12`` item 6 (``CR-TC-BACKFILL-07``, ``CR-TC-REPORT-01``).

Every column, CHECK and index is transcribed from ``ENT-tag-alias``, ``ENT-tag-exclusion`` and
``ENT-tag-config-version``; ``tests/contract/test_schema_matches_entities.py`` asserts set
equality in both directions, so a field invented here or omitted here fails that gate.

Two things are deliberately *not* added, both recorded on the card rather than decided here:
a foreign key from ``report.tag_config_version_id`` to this new table, and one from
``backfill_ledger.tag_id`` to ``tag`` (``CR-TC-REPORT-01`` second half, ``CR-TC-BACKFILL-10``).
Both columns live in other modules' tables, and existing tests seed synthetic ids into them.

``0015_tc_storage_maintenance_window`` was head when this was written, so this revision chains
off it and ``alembic heads`` stays length 1.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0016_tc_tag_service"
down_revision: str | None = "0015_tc_storage_maintenance_window"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps), spelled the
#: way every earlier revision spells it.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_TAG_ALIAS = f"""
CREATE TABLE tag_alias (
    id          TEXT NOT NULL PRIMARY KEY,
    owner_id    TEXT NOT NULL REFERENCES owner (id)
                     ON DELETE RESTRICT ON UPDATE RESTRICT,
    tag_id      TEXT NOT NULL REFERENCES tag (id)
                     ON DELETE RESTRICT ON UPDATE RESTRICT,
    "text"      TEXT NOT NULL CHECK (length("text") BETWEEN 1 AND 200),
    state       TEXT NOT NULL CHECK (state IN ('active', 'removed')),
    created_at  TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

# `tag_id` NULL = a global exclusion (ENT-tag-exclusion). The FK is not in the entity text,
# but a non-NULL value is a tag id by definition and RESTRICT matches tag_alias.
_TAG_EXCLUSION = f"""
CREATE TABLE tag_exclusion (
    id          TEXT NOT NULL PRIMARY KEY,
    owner_id    TEXT NOT NULL REFERENCES owner (id)
                     ON DELETE RESTRICT ON UPDATE RESTRICT,
    tag_id      TEXT     NULL REFERENCES tag (id)
                     ON DELETE RESTRICT ON UPDATE RESTRICT,
    "text"      TEXT NOT NULL CHECK (length("text") BETWEEN 1 AND 200),
    state       TEXT NOT NULL CHECK (state IN ('active', 'removed')),
    created_at  TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

_TAG_CONFIG_VERSION = f"""
CREATE TABLE tag_config_version (
    id            TEXT NOT NULL PRIMARY KEY,
    owner_id      TEXT NOT NULL REFERENCES owner (id)
                       ON DELETE RESTRICT ON UPDATE RESTRICT,
    sequence      INTEGER NOT NULL CHECK (sequence >= 1),
    payload       TEXT NOT NULL,
    content_hash  TEXT NOT NULL CHECK (content_hash GLOB 'sha256:*'),
    created_at    TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

_STATEMENTS: tuple[str, ...] = (
    _TAG_ALIAS,
    'CREATE UNIQUE INDEX ux_tag_alias_owner_tag_text ON tag_alias (owner_id, tag_id, "text")',
    _TAG_EXCLUSION,
    "CREATE UNIQUE INDEX ux_tag_exclusion_owner_scope_text "
    'ON tag_exclusion (owner_id, tag_id, "text")',
    _TAG_CONFIG_VERSION,
    "CREATE UNIQUE INDEX ux_tag_config_version_owner_sequence "
    "ON tag_config_version (owner_id, sequence)",
    "CREATE UNIQUE INDEX ux_tag_config_version_owner_hash "
    "ON tag_config_version (owner_id, content_hash)",
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE IF EXISTS tag_config_version",
    "DROP TABLE IF EXISTS tag_exclusion",
    "DROP TABLE IF EXISTS tag_alias",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DROPS:
        op.execute(statement)
