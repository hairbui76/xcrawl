"""The three tables ``MOD-backup-service`` owns: snapshot, manifest, restore record.

Revision ID: 0012_tc_backup_restore_drill
Revises: 0011_merge_phase4_6_heads
Create Date: 2026-09-08

None of these three exists yet, so this revision creates them outright -- there is no
custodian to take over from, unlike ``saved_snapshot`` in ``0002b``. The columns are
``entities.yaml`` column-for-column (``ENT-backup-snapshot``, ``ENT-backup-manifest``,
``ENT-restore-record``).

Four shapes are load-bearing
----------------------------
``backup_snapshot.method`` has exactly two members. ``file_copy`` is **not** one of them and
must never be added: ``AMD-B11`` / ``ADR-0005`` point 1 amended ``REQ-D58`` precisely because
copying a live WAL database can lose committed transactions. Making that a CHECK means the
forbidden method cannot be recorded even by a caller that tried it.

``restore_record.new_restore_generation`` is UNIQUE per owner. That index *is* the mechanism
of ``I15``: ``outbox_intent.restore_generation`` is compared against it, and an intent
restored from a snapshot necessarily carries an older value, so "the dispatcher does not
replay the old outbox" becomes a numeric comparison rather than a promise in a runbook.

``restore_record.dispatcher_unlocked_at`` is NULL until reconciliation finishes, and the
CHECK below refuses to let it be set while ``integrity_check_outcome`` is not ``passed``.
``entities.yaml`` lists "unlock the dispatcher when ``integrity_check_outcome != 'passed'``"
as forbidden; a constraint is the only version of that sentence a future code path cannot
forget.

``operator_ack_principal`` is NOT NULL exactly when ``operator_ack_at`` is -- clause 7 of
``reconciliation_complete`` needs a *named* acknowledgement, and a timestamp with nobody
attached to it would satisfy the letter of the clause while destroying its point (the machine
cannot certify that a human looked).

Two contract divergences this revision resolves in favour of ``entities.yaml``
------------------------------------------------------------------------------
Fixture ``recovery/d`` expects ``backup_snapshot.state == 'invalid'`` and
``integrity_check_outcome == 'mismatch'``; ``backup-restore.md`` §5.6 clause 1 says
``integrity_check_outcome == 'ok'``. Neither value exists in ``entities.yaml``, whose enums are
``running | completed | failed | verified`` and ``passed | failed | not_run``. Per the
Coordinator's ruling the entity contract wins, so the CHECKs below carry the entity values and
the mapping is asserted in ``tests/integration/test_wal_unsafe_detected.py``.
``CR-TC-BACKUP-02``.

No idempotency-key columns
--------------------------
``ports.yaml`` makes ``backup.create_snapshot`` idempotent on ``snapshot_request_id`` and
``backup.restore_snapshot`` on ``restore_request_id``, but ``entities.yaml`` declares **no
column** on either table to hold them. Adding one would ship a column the entity contract does
not declare, which ``tests/contract/test_schema_matches_entities.py`` rejects in both
directions -- and rightly: a schema that quietly grows fields is how the DDL and the contract
stop describing the same database.

So neither column exists here. The two operations get their idempotency from what the contract
*does* give (see ``server/app/backup/snapshot.py`` and ``restore.py``), and the gap is raised as
``CR-TC-BACKUP-07``.

``schema_migration_version`` stays nullable and is written NULL: ``ENT-schema-migration`` is
owned by ``MOD-data-store`` and no card has created that table, so ``MAX(version)`` is not
computable. The Alembic head revision is recorded in the manifest instead.
``CR-TC-BACKUP-04``.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0012_tc_backup_restore_drill"
down_revision: str | None = "0011_merge_phase4_6_heads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"


def _ts(column: str, *, nullable: bool = False) -> str:
    check = f"{column} GLOB '{TIMESTAMP_UTC_MS_GLOB}'"
    return f"CHECK ({column} IS NULL OR {check})" if nullable else f"CHECK ({check})"


_STATEMENTS: tuple[str, ...] = (
    # -- backup_snapshot (ENT-backup-snapshot) ------------------------------------------
    f"""
    CREATE TABLE backup_snapshot (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        method                  TEXT NOT NULL
                                     CHECK (method IN ('sqlite_online_backup_api',
                                                       'vacuum_into')),
        started_at              TEXT NOT NULL {_ts('started_at')},
        completed_at            TEXT NULL {_ts('completed_at', nullable=True)},
        artifact_path           TEXT NULL,
        artifact_sha256         TEXT NULL
                                     CHECK (artifact_sha256 IS NULL
                                            OR artifact_sha256 GLOB 'sha256:*'),
        schema_migration_version INTEGER NULL,
        state                   TEXT NOT NULL
                                     CHECK (state IN ('running', 'completed', 'failed',
                                                      'verified')),

        CHECK (length(id) = 26),
        -- entities.yaml: `artifact_sha256` NOT NULL when completed. A completed snapshot
        -- with no hash could never be verified, which is the one thing a backup must be.
        CHECK (state NOT IN ('completed', 'verified')
               OR (artifact_sha256 IS NOT NULL AND artifact_path IS NOT NULL
                   AND completed_at IS NOT NULL))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_backup_snapshot_artifact ON backup_snapshot
        (owner_id, artifact_sha256)
        WHERE artifact_sha256 IS NOT NULL
    """,
    # -- backup_manifest (ENT-backup-manifest) ------------------------------------------
    """
    CREATE TABLE backup_manifest (
        id                             TEXT NOT NULL PRIMARY KEY,
        owner_id                       TEXT NOT NULL REFERENCES owner (id)
                                            ON DELETE RESTRICT ON UPDATE RESTRICT,
        backup_snapshot_id             TEXT NOT NULL REFERENCES backup_snapshot (id)
                                            ON DELETE RESTRICT ON UPDATE RESTRICT,
        entries                        TEXT NOT NULL,
        manifest_sha256                TEXT NOT NULL
                                            CHECK (manifest_sha256 GLOB 'sha256:*'),
        counts                         TEXT NOT NULL,
        embedding_model_artifact_sha256 TEXT NULL
                                            CHECK (embedding_model_artifact_sha256 IS NULL
                                                   OR embedding_model_artifact_sha256
                                                      GLOB 'sha256:*'),

        CHECK (length(id) = 26)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_backup_manifest_snapshot ON backup_manifest
        (owner_id, backup_snapshot_id)
    """,
    # -- restore_record (ENT-restore-record) --------------------------------------------
    f"""
    CREATE TABLE restore_record (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        backup_snapshot_id      TEXT NOT NULL REFERENCES backup_snapshot (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        restored_at             TEXT NOT NULL {_ts('restored_at')},
        new_restore_generation  INTEGER NOT NULL CHECK (new_restore_generation >= 1),
        integrity_check_outcome TEXT NOT NULL
                                     CHECK (integrity_check_outcome IN
                                            ('passed', 'failed', 'not_run')),
        counts_observed         TEXT NOT NULL,
        leases_revoked          INTEGER NOT NULL CHECK (leases_revoked >= 0),
        dispatcher_unlocked_at  TEXT NULL {_ts('dispatcher_unlocked_at', nullable=True)},
        operator_ack_at         TEXT NULL {_ts('operator_ack_at', nullable=True)},
        operator_ack_principal  TEXT NULL,
        operator_ack_note       TEXT NULL,

        CHECK (length(id) = 26),
        -- entities.yaml `forbidden`: never unlock the dispatcher unless integrity passed.
        CHECK (dispatcher_unlocked_at IS NULL OR integrity_check_outcome = 'passed'),
        -- An acknowledgement with no principal is not an acknowledgement (clause 7).
        CHECK ((operator_ack_at IS NULL) = (operator_ack_principal IS NULL))
    )
    """,
    """
    CREATE UNIQUE INDEX ux_restore_record_generation ON restore_record
        (owner_id, new_restore_generation)
    """,
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE restore_record",
    "DROP TABLE backup_manifest",
    "DROP TABLE backup_snapshot",
)


def upgrade() -> None:
    """Create the three backup tables."""
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drop them in reverse dependency order."""
    for statement in _DROPS:
        op.execute(statement)
