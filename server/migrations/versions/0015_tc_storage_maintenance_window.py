"""``maintenance_window``: the one table storage health is allowed to persist.

Revision ID: 0015_tc_storage_maintenance_window
Revises: 0014_tc_secret_settings_service
Create Date: 2026-09-09

Why this table exists
---------------------
``contracts/state/storage.yaml`` ``T-ST-03`` has always said its transaction is *"Ghi một
hàng maintenance window"* — write a maintenance window row — but until
``AMD-ENT-maintenance-01`` no entity declared one, so ``storage.health`` lived only in
``StorageGuard`` process memory. Gap ``G-3``: ``backup_cli maintenance --open`` reported
``T-ST-03`` and exit 0, and the very next CLI invocation constructed a fresh guard at
``healthy``, so ``restore`` refused with ``precondition_not_met`` and the two-step restore in
``docs/owner-runbook.md`` §9.4 was unreachable. This revision is the row.

What is deliberately **not** here
---------------------------------
There is no ``storage_health`` column and no table for the other two states, because
``ENT-maintenance-window`` ``what_it_is_not_vi`` forbids both:

``write_blocked``
    must never be persisted (``T-ST-01``, ``forbidden_transitions`` row 4). It has to be
    inferred from a write that just failed. A row read at startup saying "blocked" would
    refuse writes on a healthy disk, and one saying "healthy" would let a full disk take
    assignments — which is what ``I02`` forbids.

``recovery_required``
    already exists on disk: a ``restore_record`` whose ``dispatcher_unlocked_at`` is NULL
    *is* that state. ``server/app/storage/guard.py`` reads it there rather than duplicating
    it, so the two can never disagree.

Chained, not merged
-------------------
``0014_tc_secret_settings_service`` was head when this was written, so this revision chains
off it and ``alembic heads`` stays length 1. A merge revision is a shared artifact that two
authors have to agree not to write simultaneously — the race that produced ``0004``,
``0007`` and ``0011``. Chaining needs no agreement.
``tests/integration/test_readiness_independent_channel.py`` asserts ``len(heads) == 1``
structurally rather than against a literal.

Every column, CHECK and index below is transcribed from ``ENT-maintenance-window``;
``tests/contract/test_schema_matches_entities.py`` asserts set equality in both directions,
so a field invented here or omitted here fails that gate.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0015_tc_storage_maintenance_window"
down_revision: str | None = "0014_tc_secret_settings_service"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps), spelled the
#: way every earlier revision spells it.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

#: ``reason`` — four purposes named by T-ST-03/T-ST-04/T-ST-05 plus ``disk_cleanup``, which
#: T-ST-09's guard names in as many words ("dọn ổ, migrate, restore"). Closed enum.
_REASONS = ("snapshot", "migration", "restore", "purge_all", "disk_cleanup")

#: ``storage_health_at_open`` — T-ST-03 opens from ``healthy``, T-ST-09 from
#: ``write_blocked``. Two values, not four: a window cannot be opened from ``maintenance``
#: (it is already open) nor from ``recovery_required`` (no such transition exists).
_HEALTH_AT_OPEN = ("healthy", "write_blocked")


def _in_list(column: str, values: tuple[str, ...]) -> str:
    rendered = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({rendered})"


_MAINTENANCE_WINDOW = f"""
CREATE TABLE maintenance_window (
    id                      TEXT NOT NULL PRIMARY KEY,
    owner_id                TEXT NOT NULL REFERENCES owner (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,
    opened_at               TEXT NOT NULL CHECK (opened_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    opened_by               TEXT NOT NULL CHECK (length(opened_by) BETWEEN 1 AND 200),
    reason                  TEXT NOT NULL CHECK ({_in_list("reason", _REASONS)}),
    storage_health_at_open  TEXT NOT NULL CHECK (
                                 {_in_list("storage_health_at_open", _HEALTH_AT_OPEN)}),
    closed_at               TEXT     NULL CHECK (
                                 closed_at IS NULL
                                 OR closed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    closed_by               TEXT     NULL CHECK (
                                 closed_by IS NULL
                                 OR length(closed_by) BETWEEN 1 AND 200),
    snapshot_verified_at    TEXT     NULL CHECK (
                                 snapshot_verified_at IS NULL
                                 OR snapshot_verified_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    restore_record_id       TEXT     NULL REFERENCES restore_record (id)
                                 ON DELETE RESTRICT ON UPDATE RESTRICT,

    -- Closing a window is a human act; a close with no principal cannot be audited.
    CONSTRAINT ck_maintenance_window_closed_by
        CHECK (closed_at IS NULL OR closed_by IS NOT NULL),

    -- T-ST-04 `forbidden_vi`: "Đóng cửa sổ khi verify chưa pass". The guard can only
    -- enforce that inside one process; this enforces it at the store, which is the whole
    -- point of the table. Bound to `snapshot` windows only because T-ST-04's guard says the
    -- other branch is "hoặc migration hoàn tất" — there is no snapshot to verify there.
    CONSTRAINT ck_maintenance_window_verify_before_close
        CHECK (closed_at IS NULL OR reason <> 'snapshot' OR snapshot_verified_at IS NOT NULL),

    CONSTRAINT ck_maintenance_window_closed_after_open
        CHECK (closed_at IS NULL OR closed_at >= opened_at)
)
"""

_STATEMENTS: tuple[str, ...] = (
    _MAINTENANCE_WINDOW,
    # At most ONE open window per owner — the assumption T-ST-03 and T-ST-09 make every time
    # they say *the* window. Partial, so closed windows accumulate as history.
    "CREATE UNIQUE INDEX ux_maintenance_window_open ON maintenance_window (owner_id) "
    "WHERE closed_at IS NULL",
)

_DROPS: tuple[str, ...] = ("DROP TABLE IF EXISTS maintenance_window",)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DROPS:
        op.execute(statement)
