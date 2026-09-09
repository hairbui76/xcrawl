"""The four tables ``MOD-settings-service`` owns.

``settings`` -- key/value configuration. ``ENT-settings.value_json`` says "Không bao giờ chứa
secret — secret ở PC08", so this module writes schedule, timezone, per-run limits and the
embedding model name here, and routes anything key-shaped to ``MOD-secret-service`` instead.

``provider_config`` -- one row per ``(owner, task_type)``. The two CHECKs the migration writes
(``ck_provider_config_terms_before_enable``, ``ck_provider_config_terms_by``) mean this layer
does not have to police ``REQ-A5``: an ``UPDATE ... SET enabled = 1`` without a
``terms_check_at`` is rejected by SQLite, so the gate holds for code paths that do not exist
yet.

``provider_test_result`` -- append-only. ``I14``: ``unknown`` is a legitimate outcome and is
never rewritten as ``unusable``.

``source_connection`` -- the per-source session state the collector and the research connector
report; ``secret_ref`` here is a pointer, never a value.
"""

from __future__ import annotations

import json
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
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions/id_type)."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def format_timestamp(moment: datetime) -> str:
    """RFC 3339 UTC with mandatory millisecond precision."""
    return moment.astimezone(UTC).strftime(_TIMESTAMP_FORMAT)[:-3] + "Z"


@dataclass
class ProviderConfigRow:
    id: str
    owner_id: str
    task_type: str
    auth_family: str
    provider_name: str
    model_name: str
    max_concurrency: int
    secret_ref: str | None
    enabled: bool
    terms_check_at: str | None
    terms_check_by: str | None
    terms_doc_ref: str | None


@dataclass
class ProviderTestResultRow:
    id: str
    owner_id: str
    provider_config_id: str
    tested_at: str
    outcome: str
    error_code: str | None
    detail_safe: str | None


_PROVIDER_COLUMNS = (
    "id, owner_id, task_type, auth_family, provider_name, model_name, max_concurrency, "
    "secret_ref, enabled, terms_check_at, terms_check_by, terms_doc_ref"
)
_TEST_RESULT_COLUMNS = (
    "id, owner_id, provider_config_id, tested_at, outcome, error_code, detail_safe"
)


class SettingsRepository:
    """Row access. No policy: the CHECKs are in the schema and the decisions in the service."""

    # ---------------------------------------------------------------------- settings

    def get_setting(self, connection: Connection, *, owner_id: str, key: str) -> Any | None:
        row = connection.execute(
            text('SELECT value_json FROM settings WHERE owner_id = :owner_id AND "key" = :key'),
            {"owner_id": owner_id, "key": key},
        ).first()
        return None if row is None else json.loads(row[0])

    def all_settings(self, connection: Connection, *, owner_id: str) -> dict[str, Any]:
        rows = connection.execute(
            text(
                'SELECT "key", value_json FROM settings '
                'WHERE owner_id = :owner_id ORDER BY "key"'
            ),
            {"owner_id": owner_id},
        ).all()
        return {key: json.loads(value) for key, value in rows}

    def put_setting(
        self, connection: Connection, *, owner_id: str, key: str, value: Any, updated_at: str
    ) -> None:
        """Upsert on ``ux_settings_owner_key``. One row per (owner, key), by construction."""
        connection.execute(
            text(
                'INSERT INTO settings (id, owner_id, "key", value_json, updated_at) '
                "VALUES (:id, :owner_id, :key, :value_json, :updated_at) "
                'ON CONFLICT (owner_id, "key") DO UPDATE SET '
                "value_json = excluded.value_json, updated_at = excluded.updated_at"
            ),
            {
                "id": new_ulid(),
                "owner_id": owner_id,
                "key": key,
                "value_json": json.dumps(value, ensure_ascii=False, sort_keys=True),
                "updated_at": updated_at,
            },
        )

    # --------------------------------------------------------------- provider_config

    def provider_by_task(
        self, connection: Connection, *, owner_id: str, task_type: str
    ) -> ProviderConfigRow | None:
        row = (
            connection.execute(
                text(
                    f"SELECT {_PROVIDER_COLUMNS} FROM provider_config "
                    "WHERE owner_id = :owner_id AND task_type = :task_type"
                ),
                {"owner_id": owner_id, "task_type": task_type},
            )
            .mappings()
            .first()
        )
        return None if row is None else self._provider(row)

    def provider_by_name(
        self, connection: Connection, *, owner_id: str, provider_name: str
    ) -> ProviderConfigRow | None:
        row = (
            connection.execute(
                text(
                    f"SELECT {_PROVIDER_COLUMNS} FROM provider_config "
                    "WHERE owner_id = :owner_id AND provider_name = :provider_name "
                    "ORDER BY task_type LIMIT 1"
                ),
                {"owner_id": owner_id, "provider_name": provider_name},
            )
            .mappings()
            .first()
        )
        return None if row is None else self._provider(row)

    def all_providers(
        self, connection: Connection, *, owner_id: str
    ) -> Sequence[ProviderConfigRow]:
        rows = (
            connection.execute(
                text(
                    f"SELECT {_PROVIDER_COLUMNS} FROM provider_config "
                    "WHERE owner_id = :owner_id ORDER BY task_type"
                ),
                {"owner_id": owner_id},
            )
            .mappings()
            .all()
        )
        return [self._provider(row) for row in rows]

    def upsert_provider(self, connection: Connection, row: ProviderConfigRow) -> None:
        """Insert or update the one row for ``(owner_id, task_type)``.

        The two ``terms_*`` CHECKs run **inside** the caller's transaction, so a batch that
        tries to enable an adapter without a terms record rolls the whole batch back
        (card §6 ``TXN-settings-update``).
        """
        values = vars(row) | {"enabled": 1 if row.enabled else 0}
        connection.execute(
            text(
                f"INSERT INTO provider_config ({_PROVIDER_COLUMNS}) VALUES "
                "(:id, :owner_id, :task_type, :auth_family, :provider_name, :model_name, "
                ":max_concurrency, :secret_ref, :enabled, :terms_check_at, :terms_check_by, "
                ":terms_doc_ref) "
                "ON CONFLICT (owner_id, task_type) DO UPDATE SET "
                "auth_family = excluded.auth_family, provider_name = excluded.provider_name, "
                "model_name = excluded.model_name, max_concurrency = excluded.max_concurrency, "
                "secret_ref = excluded.secret_ref, enabled = excluded.enabled, "
                "terms_check_at = excluded.terms_check_at, "
                "terms_check_by = excluded.terms_check_by, "
                "terms_doc_ref = excluded.terms_doc_ref"
            ),
            values,
        )

    def set_provider_secret_ref(
        self, connection: Connection, *, owner_id: str, task_type: str, secret_ref_id: str
    ) -> None:
        connection.execute(
            text(
                "UPDATE provider_config SET secret_ref = :secret_ref "
                "WHERE owner_id = :owner_id AND task_type = :task_type"
            ),
            {"owner_id": owner_id, "task_type": task_type, "secret_ref": secret_ref_id},
        )

    # ---------------------------------------------------------- provider_test_result

    def insert_test_result(self, connection: Connection, row: ProviderTestResultRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO provider_test_result ({_TEST_RESULT_COLUMNS}) VALUES "
                "(:id, :owner_id, :provider_config_id, :tested_at, :outcome, :error_code, "
                ":detail_safe)"
            ),
            vars(row),
        )

    def latest_test_result(
        self, connection: Connection, *, owner_id: str, provider_config_id: str
    ) -> ProviderTestResultRow | None:
        row = (
            connection.execute(
                text(
                    f"SELECT {_TEST_RESULT_COLUMNS} FROM provider_test_result "
                    "WHERE owner_id = :owner_id AND provider_config_id = :provider_config_id "
                    "ORDER BY tested_at DESC, id DESC LIMIT 1"
                ),
                {"owner_id": owner_id, "provider_config_id": provider_config_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else ProviderTestResultRow(**dict(row))

    # ------------------------------------------------------------- source_connection

    def source_connections(self, connection: Connection, *, owner_id: str) -> list[dict[str, Any]]:
        rows = (
            connection.execute(
                text(
                    "SELECT id, source_type, session_state, secret_ref, last_checked_at "
                    "FROM source_connection WHERE owner_id = :owner_id ORDER BY source_type"
                ),
                {"owner_id": owner_id},
            )
            .mappings()
            .all()
        )
        # `secret_ref` is reduced to a boolean here rather than carried outwards: the read
        # model has no legitimate use for the pointer, and a field that is never rendered
        # cannot be rendered by mistake.
        return [
            {
                "source_type": row["source_type"],
                "session_state": row["session_state"],
                "credential_configured": row["secret_ref"] is not None,
                "last_checked_at": row["last_checked_at"],
            }
            for row in rows
        ]

    @staticmethod
    def _provider(row: Any) -> ProviderConfigRow:
        values = dict(row)
        values["enabled"] = bool(values["enabled"])
        return ProviderConfigRow(**values)


__all__ = [
    "ProviderConfigRow",
    "ProviderTestResultRow",
    "SettingsRepository",
    "format_timestamp",
    "new_ulid",
]
