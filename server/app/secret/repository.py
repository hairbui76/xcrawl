"""The three tables ``MOD-secret-service`` owns, and nothing else.

``secret_ref`` -- a pointer and a state. ``entities.yaml`` says it in as many words:
"``secret_ref`` chỉ giữ **tham chiếu + trạng thái**, không giữ giá trị". There is no column
here that could hold a key, so no query in this file can return one.

``task_credential`` -- one row per (assignment, secret_ref), the durable record of an issue.
``ux_task_credential_assignment`` is what makes the replay rule in ``ports.yaml``
("cùng attempt trả cùng credential còn hạn") a database property rather than an intention.

``secret_audit`` -- ``secrets.md`` §8. Every issue, revoke and refusal, with
``outcome_detail_safe`` already masked by :func:`server.app.secret.store.redact` before it
reaches this layer. Masking happens before the write (``SEC-P6``), so this module never has
to trust a caller to have done it -- but it also never *un*-masks.

SQLAlchemy 2 Core, explicit SQL, per ADR-0011: the transactions in
``contracts/data/entities.yaml`` need statement-level control, and partial indexes are not an
ORM concept.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Connection, text

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def new_ulid() -> str:
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions/id_type).

    Defined here rather than imported from another domain package: the module registry grants
    no import edge between domain services, and a shared utility module is not one of this
    card's write targets. Same construction as every other package's copy.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def format_timestamp(moment: datetime) -> str:
    """RFC 3339 UTC with mandatory millisecond precision (``entities.yaml`` §conventions)."""
    return moment.astimezone(UTC).strftime(_TIMESTAMP_FORMAT)[:-3] + "Z"


def parse_timestamp(value: str) -> datetime:
    """Inverse of :func:`format_timestamp`."""
    return datetime.strptime(value, _TIMESTAMP_FORMAT + "Z").replace(tzinfo=UTC)


@dataclass
class SecretRefRow:
    id: str
    owner_id: str
    purpose: str
    store_locator: str
    created_at: str
    rotated_at: str | None
    state: str


@dataclass
class TaskCredentialRow:
    id: str
    owner_id: str
    assignment_id: str
    secret_ref_id: str
    issued_to_worker_identity: str
    issued_at: str
    expires_at: str
    revoked_at: str | None


@dataclass
class SecretAuditRow:
    id: str
    owner_id: str
    action: str
    secret_ref_id: str | None
    actor_module: str
    at: str
    outcome_detail_safe: str | None


_SECRET_REF_COLUMNS = "id, owner_id, purpose, store_locator, created_at, rotated_at, state"
_TASK_CREDENTIAL_COLUMNS = (
    "id, owner_id, assignment_id, secret_ref_id, issued_to_worker_identity, "
    "issued_at, expires_at, revoked_at"
)
_SECRET_AUDIT_COLUMNS = "id, owner_id, action, secret_ref_id, actor_module, at, outcome_detail_safe"


class SecretRepository:
    """Row access for the three tables. No decisions, no encryption, no masking."""

    # ------------------------------------------------------------------- secret_ref

    def insert_secret_ref(self, connection: Connection, row: SecretRefRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO secret_ref ({_SECRET_REF_COLUMNS}) VALUES "
                "(:id, :owner_id, :purpose, :store_locator, :created_at, :rotated_at, :state)"
            ),
            vars(row),
        )

    def active_secret_ref(
        self, connection: Connection, *, owner_id: str, purpose: str
    ) -> SecretRefRow | None:
        row = (
            connection.execute(
                text(
                    f"SELECT {_SECRET_REF_COLUMNS} FROM secret_ref "
                    "WHERE owner_id = :owner_id AND purpose = :purpose AND state = 'active'"
                ),
                {"owner_id": owner_id, "purpose": purpose},
            )
            .mappings()
            .first()
        )
        return None if row is None else SecretRefRow(**dict(row))

    def secret_ref_by_id(self, connection: Connection, secret_ref_id: str) -> SecretRefRow | None:
        row = (
            connection.execute(
                text(f"SELECT {_SECRET_REF_COLUMNS} FROM secret_ref WHERE id = :id"),
                {"id": secret_ref_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else SecretRefRow(**dict(row))

    def mark_secret_ref_rotated(
        self, connection: Connection, *, secret_ref_id: str, rotated_at: str
    ) -> None:
        """``active`` -> ``rotated``. The old row stays: ``secrets.md`` §3 keeps both live for
        ``rotation_overlap``, and an audit trail with the previous ref deleted is not one."""
        connection.execute(
            text(
                "UPDATE secret_ref SET state = 'rotated', rotated_at = :rotated_at "
                "WHERE id = :id AND state = 'active'"
            ),
            {"id": secret_ref_id, "rotated_at": rotated_at},
        )

    # -------------------------------------------------------------- task_credential

    def insert_task_credential(self, connection: Connection, row: TaskCredentialRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO task_credential ({_TASK_CREDENTIAL_COLUMNS}) VALUES "
                "(:id, :owner_id, :assignment_id, :secret_ref_id, :issued_to_worker_identity, "
                ":issued_at, :expires_at, :revoked_at)"
            ),
            vars(row),
        )

    def live_credential(
        self,
        connection: Connection,
        *,
        owner_id: str,
        assignment_id: str,
        secret_ref_id: str,
        now: str,
    ) -> TaskCredentialRow | None:
        """The unexpired, unrevoked credential for this (assignment, secret_ref), if any.

        This is the read behind the replay rule: a second call for the same attempt finds this
        row and returns it rather than minting a second credential.
        """
        row = (
            connection.execute(
                text(
                    f"SELECT {_TASK_CREDENTIAL_COLUMNS} FROM task_credential "
                    "WHERE owner_id = :owner_id AND assignment_id = :assignment_id "
                    "AND secret_ref_id = :secret_ref_id AND revoked_at IS NULL "
                    "AND expires_at > :now"
                ),
                {
                    "owner_id": owner_id,
                    "assignment_id": assignment_id,
                    "secret_ref_id": secret_ref_id,
                    "now": now,
                },
            )
            .mappings()
            .first()
        )
        return None if row is None else TaskCredentialRow(**dict(row))

    def credentials_for_assignment(
        self, connection: Connection, *, owner_id: str, assignment_id: str
    ) -> Sequence[TaskCredentialRow]:
        rows = (
            connection.execute(
                text(
                    f"SELECT {_TASK_CREDENTIAL_COLUMNS} FROM task_credential "
                    "WHERE owner_id = :owner_id AND assignment_id = :assignment_id "
                    "ORDER BY issued_at"
                ),
                {"owner_id": owner_id, "assignment_id": assignment_id},
            )
            .mappings()
            .all()
        )
        return [TaskCredentialRow(**dict(row)) for row in rows]

    def revoke_credentials(
        self, connection: Connection, *, owner_id: str, assignment_id: str, revoked_at: str
    ) -> int:
        """Revoke every live credential of one assignment. Idempotent by construction:
        ``revoked_at IS NULL`` means a second call matches nothing and changes no state
        (``ports.yaml``: "Thu hồi lại không đổi trạng thái")."""
        result = connection.execute(
            text(
                "UPDATE task_credential SET revoked_at = :revoked_at "
                "WHERE owner_id = :owner_id AND assignment_id = :assignment_id "
                "AND revoked_at IS NULL"
            ),
            {"owner_id": owner_id, "assignment_id": assignment_id, "revoked_at": revoked_at},
        )
        return int(result.rowcount or 0)

    def count_credentials(self, connection: Connection, *, owner_id: str) -> int:
        """The ISO-05 oracle: a refusal must leave this number unchanged."""
        return int(
            connection.execute(
                text("SELECT COUNT(*) FROM task_credential WHERE owner_id = :owner_id"),
                {"owner_id": owner_id},
            ).scalar_one()
        )

    # ----------------------------------------------------------------- secret_audit

    def insert_audit(self, connection: Connection, row: SecretAuditRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO secret_audit ({_SECRET_AUDIT_COLUMNS}) VALUES "
                "(:id, :owner_id, :action, :secret_ref_id, :actor_module, :at, "
                ":outcome_detail_safe)"
            ),
            vars(row),
        )

    def audit_rows(self, connection: Connection, *, owner_id: str) -> Sequence[SecretAuditRow]:
        rows = (
            connection.execute(
                text(
                    f"SELECT {_SECRET_AUDIT_COLUMNS} FROM secret_audit "
                    "WHERE owner_id = :owner_id ORDER BY at, id"
                ),
                {"owner_id": owner_id},
            )
            .mappings()
            .all()
        )
        return [SecretAuditRow(**dict(row)) for row in rows]

    # ------------------------------------------------------------------- assignment

    def assignment_exists(self, connection: Connection, *, assignment_id: str) -> bool:
        """``task_credential.assignment_id`` is a real FK; a credential for an assignment that
        does not exist is ``NOT_FOUND``, not an integrity error surfaced as ``INTERNAL``."""
        row: Any = connection.execute(
            text("SELECT 1 FROM assignment WHERE id = :id"), {"id": assignment_id}
        ).first()
        return row is not None


__all__ = [
    "SecretAuditRow",
    "SecretRefRow",
    "SecretRepository",
    "TaskCredentialRow",
    "format_timestamp",
    "new_ulid",
    "parse_timestamp",
]
