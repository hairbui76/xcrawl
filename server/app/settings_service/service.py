"""``MOD-settings-service``: the three ``settings.*`` operations.

======================================  ==========================================
``settings.get_config``                 :func:`get_config`      (owner session)
``settings.update_config``              :func:`update_config`   (owner session + CSRF)
``settings.test_provider``              :func:`test_provider`   (owner session + CSRF)
======================================  ==========================================

Three properties this module exists to hold
-------------------------------------------
**A key goes in and never comes out.** ``settings.update_config`` accepts
``provider_key`` and hands it straight to ``secret.store_provider_key``. Nothing here keeps a
copy, and :func:`get_config` answers with ``key_configured: true|false`` plus the
``secret_ref`` id -- denied case ``NC-03``, ``secrets.md`` §4.2. The read model has no field a
key could occupy, which is a stronger statement than "we remember not to include it".

**Enabling an adapter is gated at the database.** ``ck_provider_config_terms_before_enable``
rejects ``enabled = 1`` without ``terms_check_at``. This module also checks it before writing,
so the caller gets ``VALIDATION_ERROR`` rather than an opaque integrity error -- but the
check that *counts* is the one in the schema, and the card's §12 reviewer question 3 asks for
exactly that distinction. This module never fills ``terms_check_at`` by itself: ``SG-TERMS``
says reading a vendor's terms is the owner's manual act, and a service that stamps the field
to make its own write succeed has forged the evidence.

**``unknown`` is an answer.** ``settings.test_provider`` records ``usable | unusable |
unknown`` and ``I14`` forbids collapsing the third into the second. A provider that is
configured but not reachable from here -- every ``cli_acp`` adapter, by construction -- is
``unknown`` with a reason code, not a failure.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.secret.service import (
    PURPOSE_AI_PROVIDER_KEY,
    SecretContext,
    SecretError,
    store_provider_key,
)
from server.app.secret.store import redact
from server.app.settings_service.repository import (
    ProviderConfigRow,
    ProviderTestResultRow,
    SettingsRepository,
    format_timestamp,
    new_ulid,
)

MODULE_ID = "MOD-settings-service"

#: ``contracts/data/entities.yaml`` ``ENT-analysis.task_type`` (ruling ``R-03``).
TASK_TYPES = ("label", "summary", "direction_phrasing")

#: Settings keys this module accepts. An unknown key is ``VALIDATION_ERROR``: a config store
#: that accepts any key silently becomes a second, undocumented schema.
SETTINGS_KEYS = frozenset(
    {
        "timezone_iana",
        "schedule_times",
        "run_item_limit",
        "run_minutes_limit",
        "backfill_days",
        "embedding_model_name",
        "telegram_quiet_hours",
    }
)


class SecretWriterPort(Protocol):
    """``secret.store_provider_key``, the only secret operation this module may call."""

    def store_provider_key(
        self, *, provider_id: str, value: str, key_version: int, purpose: str
    ) -> str: ...


class EmbeddingRebuildPort(Protocol):
    """``embedding.start_generation_rebuild`` -- the one operation §4 lets this card consume."""

    def start_generation_rebuild(self, *, model_name: str, reason: str) -> str | None: ...


class ProviderProbePort(Protocol):
    """What ``settings.test_provider`` calls instead of a provider.

    There is no live call in this card (``§8``: E3 ``NOT_RUN``, no adapter is enabled). A
    deployment injects a real probe; the tests inject one that returns a recorded answer. The
    port exists so that "no live call happened" is a property of the wiring rather than a
    promise in a docstring.
    """

    def probe(self, *, provider_name: str, model_name: str) -> tuple[str, str | None, str | None]:
        """Return ``(outcome, error_code, detail_safe)``."""


class StorageGuardPort(Protocol):
    def assert_writable(self, operation_id: OperationId) -> None: ...

    def record_write_failure(self) -> str | None: ...


@dataclass
class SettingsContext:
    engine: Engine
    owner_id: str
    repository: SettingsRepository = field(default_factory=SettingsRepository)
    secrets: SecretContext | None = None
    probe: ProviderProbePort | None = None
    embedding: EmbeddingRebuildPort | None = None
    storage_guard: StorageGuardPort | None = None
    clock: Any = None
    id_factory: Any = None
    #: ``ports.yaml``: ``settings.update_config`` is idempotent on ``request_id``. ``ENT-settings``
    #: has no column for it, so the registry is process-local -- the same shape, and the same
    #: limitation, that ``server/app/analysis/service.py`` records as ``CR-TC-ANALYSIS-04``.
    #: Recorded here as ``CR-TC-SECRET-05``.
    update_receipts: dict[str, str] = field(default_factory=dict)

    def now(self) -> datetime:
        return datetime.now(UTC) if self.clock is None else self.clock()

    def new_id(self) -> str:
        return new_ulid() if self.id_factory is None else self.id_factory()


def _validation(message: str, **details: Any) -> SecretError:
    return SecretError(ErrorCode.VALIDATION_ERROR, message, details_safe=details)


def _assert_writable(ctx: SettingsContext, operation: OperationId) -> None:
    if ctx.storage_guard is not None:
        ctx.storage_guard.assert_writable(operation)


def _payload_hash(payload: Mapping[str, Any]) -> str:
    """A hash of the *redacted* payload: the key never reaches the digest input either."""
    safe = {
        key: ("[REDACTED:value]" if key == "provider_key" else value)
        for key, value in sorted(payload.items())
    }
    return hashlib.sha256(json.dumps(safe, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# ------------------------------------------------------------------- settings.get_config


def get_config(ctx: SettingsContext) -> dict[str, Any]:
    """The full configuration, with secrets reduced to *configured / not configured*.

    ``ports.yaml``: "CHỈ trả THAM CHIẾU tới secret, không bao giờ giá trị key". The provider
    view below carries ``secret_ref`` (an id) and ``key_configured`` (a boolean) and has no
    field for a value -- the read model cannot leak what it cannot represent.
    """
    with ctx.engine.connect() as connection:
        settings = ctx.repository.all_settings(connection, owner_id=ctx.owner_id)
        providers = ctx.repository.all_providers(connection, owner_id=ctx.owner_id)
        sources = ctx.repository.source_connections(connection, owner_id=ctx.owner_id)
        latest = {
            provider.id: ctx.repository.latest_test_result(
                connection, owner_id=ctx.owner_id, provider_config_id=provider.id
            )
            for provider in providers
        }

    return {
        "settings": settings,
        "timezone_iana": settings.get("timezone_iana"),
        "providers": [
            {
                "task_type": provider.task_type,
                "auth_family": provider.auth_family,
                "provider_name": provider.provider_name,
                "model_name": provider.model_name,
                "max_concurrency": provider.max_concurrency,
                "enabled": provider.enabled,
                "secret_ref": provider.secret_ref,
                "key_configured": provider.secret_ref is not None,
                "terms_check_at": provider.terms_check_at,
                "terms_check_by": provider.terms_check_by,
                "terms_doc_ref": provider.terms_doc_ref,
                "last_test": _test_view(latest.get(provider.id)),
            }
            for provider in providers
        ],
        "source_connections": sources,
    }


def _test_view(row: ProviderTestResultRow | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "outcome": row.outcome,
        "error_code": row.error_code,
        "detail_safe": row.detail_safe,
        "tested_at": row.tested_at,
    }


# ---------------------------------------------------------------- settings.update_config


def update_config(
    ctx: SettingsContext,
    *,
    request_id: str,
    settings: Mapping[str, Any] | None = None,
    provider: Mapping[str, Any] | None = None,
    provider_key: str | None = None,
) -> dict[str, Any]:
    """Write configuration, and route a new key to the secret service.

    One transaction (``TXN-settings-update``): the settings rows, the ``provider_config`` row
    and the CHECKs that guard it either all land or none do. The key is written *first*,
    through ``secret.store_provider_key``, because a ``provider_config.secret_ref`` pointing at
    a secret that was never stored is worse than a stored secret nothing points at yet.
    """
    if not request_id:
        raise _validation(
            "request_id là bắt buộc.",
            operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
            field_path="request_id",
            violation_kind="required_field_missing",
        )
    settings_patch: dict[str, Any] = dict(settings or {})
    provider_patch: dict[str, Any] = dict(provider or {})
    digest = _payload_hash(
        {
            "settings": settings_patch,
            "provider": provider_patch,
            "provider_key": provider_key,
        }
    )
    seen = ctx.update_receipts.get(request_id)
    if seen is not None and seen != digest:
        raise SecretError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Cùng request_id với payload khác.",
            details_safe={
                "idempotency_key": request_id,
                "payload_hash_seen": digest[:16],
                "payload_hash_stored": seen[:16],
            },
        )

    for key in settings_patch:
        if key not in SETTINGS_KEYS:
            raise _validation(
                "Khóa cấu hình không được hỗ trợ.",
                operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
                field_path=f"settings.{key}",
                violation_kind="enum_value_unknown",
            )

    if provider_patch:
        _validate_provider_patch(provider_patch)

    _assert_writable(ctx, OperationId.SETTINGS_UPDATE_CONFIG)
    now = format_timestamp(ctx.now())

    secret_ref_id: str | None = None
    if provider_key is not None:
        if not provider_patch:
            raise _validation(
                "Gửi key mà không nêu provider nào.",
                operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
                field_path="provider",
                violation_kind="required_field_missing",
            )
        if ctx.secrets is None:
            raise SecretError(
                ErrorCode.STORAGE_WRITE_FAILED,
                "Secret service chưa sẵn sàng.",
                details_safe={
                    "storage_health": "unavailable",
                    "failed_operation_id": OperationId.SETTINGS_UPDATE_CONFIG.value,
                },
            )
        reference = store_provider_key(
            ctx.secrets,
            provider_id=str(provider_patch["provider_name"]),
            value=provider_key,
            key_version=int(provider_patch.get("key_version", 1)),
            purpose=PURPOSE_AI_PROVIDER_KEY,
            actor_module=MODULE_ID,
        )
        secret_ref_id = reference.secret_ref_id

    with ctx.engine.begin() as connection:
        for key, value in settings_patch.items():
            ctx.repository.put_setting(
                connection, owner_id=ctx.owner_id, key=key, value=value, updated_at=now
            )
        if provider_patch:
            existing = ctx.repository.provider_by_task(
                connection, owner_id=ctx.owner_id, task_type=provider_patch["task_type"]
            )
            row = _merged_provider_row(ctx, existing, provider_patch, secret_ref_id)
            if row.enabled and row.terms_check_at is None:
                # Refused here so the owner gets a contract error rather than an integrity
                # error -- but the row would be refused by the DB CHECK anyway, and the test
                # proves that by attempting the raw write.
                raise _validation(
                    "Không thể bật adapter khi chưa ghi nhận việc đọc điều khoản (REQ-A5).",
                    operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
                    field_path="provider.enabled",
                    violation_kind="terms_check_missing",
                )
            ctx.repository.upsert_provider(connection, row)

    if "embedding_model_name" in settings_patch and ctx.embedding is not None:
        # `settings.update_config` consumes exactly one operation (card §4), and it does not
        # switch the active generation: `embedding.start_generation_rebuild` queues a rebuild
        # and the switch is its own decision (REQ-D48/B14).
        ctx.embedding.start_generation_rebuild(
            model_name=str(settings_patch["embedding_model_name"]),
            reason="settings_update",
        )

    ctx.update_receipts[request_id] = digest
    return get_config(ctx)


def _validate_provider_patch(patch: Mapping[str, Any]) -> None:
    required = ("task_type", "auth_family", "provider_name", "model_name")
    for field_name in required:
        if not patch.get(field_name):
            raise _validation(
                "Thiếu trường bắt buộc của provider.",
                operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
                field_path=f"provider.{field_name}",
                violation_kind="required_field_missing",
            )
    if patch["task_type"] not in TASK_TYPES:
        raise _validation(
            "task_type không hợp lệ.",
            operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
            field_path="provider.task_type",
            violation_kind="enum_value_unknown",
        )
    if patch["auth_family"] not in ("api_key", "cli_acp"):
        raise _validation(
            "auth_family không hợp lệ.",
            operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
            field_path="provider.auth_family",
            violation_kind="enum_value_unknown",
        )
    if patch["model_name"] == "latest":
        # `entities.yaml`: "Không dùng `latest`". A moving model name makes `analysis_key`'s
        # provenance meaningless.
        raise _validation(
            "model_name không được là 'latest'.",
            operation_id=OperationId.SETTINGS_UPDATE_CONFIG.value,
            field_path="provider.model_name",
            violation_kind="value_not_allowed",
        )


def _merged_provider_row(
    ctx: SettingsContext,
    existing: ProviderConfigRow | None,
    patch: Mapping[str, Any],
    secret_ref_id: str | None,
) -> ProviderConfigRow:
    """Patch semantics: absent fields keep their stored value.

    ``terms_check_at`` / ``terms_check_by`` are carried over but **never invented**: only an
    explicit ``terms_check`` block in the patch sets them, and that block is the owner
    recording that they read the vendor's terms (``SG-TERMS``, ``REQ-A5``).
    """
    auth_family = str(patch["auth_family"])
    terms = patch.get("terms_check") or {}
    terms_at = terms.get("at") or (existing.terms_check_at if existing else None)
    terms_by = terms.get("by") or (existing.terms_check_by if existing else None)
    terms_doc = terms.get("doc_ref") or (existing.terms_doc_ref if existing else None)
    return ProviderConfigRow(
        id=existing.id if existing else ctx.new_id(),
        owner_id=ctx.owner_id,
        task_type=str(patch["task_type"]),
        auth_family=auth_family,
        provider_name=str(patch["provider_name"]),
        model_name=str(patch["model_name"]),
        # `providers.yaml` §1: the CLI/ACP path is concurrency 1 by contract, not by default.
        max_concurrency=1
        if auth_family == "cli_acp"
        else int(patch.get("max_concurrency", existing.max_concurrency if existing else 1)),
        # REQ-D51: the CLI path holds no server secret at all.
        secret_ref=None
        if auth_family == "cli_acp"
        else (secret_ref_id or (existing.secret_ref if existing else None)),
        enabled=bool(patch.get("enabled", existing.enabled if existing else False)),
        terms_check_at=terms_at,
        terms_check_by=terms_by,
        terms_doc_ref=terms_doc,
    )


# ---------------------------------------------------------------- settings.test_provider


def test_provider(ctx: SettingsContext, *, provider_name: str) -> dict[str, Any]:
    """Record one ``provider_test_result``. Never reuses an older one (``ports.yaml``).

    ``cli_acp`` is answered ``unknown`` without calling anything: ``ports.yaml`` says that path
    "**không** thử được từ server; trạng thái của nó chỉ đến từ ``worker.register_capabilities``
    trên máy cá nhân". Reporting it as ``unusable`` would be the ``I14`` violation this
    operation is most likely to commit.
    """
    _assert_writable(ctx, OperationId.SETTINGS_TEST_PROVIDER)
    with ctx.engine.connect() as connection:
        provider = ctx.repository.provider_by_name(
            connection, owner_id=ctx.owner_id, provider_name=provider_name
        )
    if provider is None:
        raise SecretError(
            ErrorCode.NOT_FOUND,
            "Không tìm thấy provider đã cấu hình.",
            details_safe={
                "operation_id": OperationId.SETTINGS_TEST_PROVIDER.value,
                "resource_kind": "provider_config",
            },
        )

    outcome: str
    error_code: str | None
    detail: str | None
    if provider.auth_family == "cli_acp":
        outcome, error_code, detail = ("unknown", None, "cli_acp: chỉ worker trên máy cá nhân biết")
    elif not provider.enabled:
        # B13/ADR-0010 §3: an adapter whose isolation is unverified is disabled, and a
        # disabled adapter is not probed. `unknown`, not `unusable`: nothing was measured.
        outcome, error_code, detail = ("unknown", None, "adapter disabled: isolation_unverified")
    elif provider.secret_ref is None:
        outcome, error_code, detail = ("unusable", ErrorCode.NOT_FOUND.value, "no key configured")
    elif ctx.probe is None:
        outcome, error_code, detail = ("unknown", None, "no probe configured")
    else:
        outcome, error_code, detail = ctx.probe.probe(
            provider_name=provider.provider_name, model_name=provider.model_name
        )

    row = ProviderTestResultRow(
        id=ctx.new_id(),
        owner_id=ctx.owner_id,
        provider_config_id=provider.id,
        tested_at=format_timestamp(ctx.now()),
        outcome=outcome,
        error_code=error_code,
        detail_safe=redact(detail or "")[:300] or None,
    )
    with ctx.engine.begin() as connection:
        ctx.repository.insert_test_result(connection, row)
    return _test_view(row) or {}


class SettingsProviderView:
    """Adapts this module's ``provider_config`` rows to ``MOD-secret-service``'s port.

    ``server.app.secret.service.ProviderSecretPort`` asks one question -- "which secret_ref
    does this task type resolve to, and is that adapter enabled?" -- and gets back no key and
    no way to ask for one.
    """

    def __init__(self, ctx: SettingsContext) -> None:
        self._ctx = ctx

    def secret_ref_for_task(self, task_type: str) -> Any:
        from server.app.secret.service import ProviderSecretBinding

        with self._ctx.engine.connect() as connection:
            row = self._ctx.repository.provider_by_task(
                connection, owner_id=self._ctx.owner_id, task_type=task_type
            )
        if row is None:
            return None
        return ProviderSecretBinding(
            provider_config_id=row.id,
            provider_name=row.provider_name,
            model_name=row.model_name,
            auth_family=row.auth_family,
            enabled=row.enabled,
            secret_ref_id=row.secret_ref,
        )


__all__ = [
    "MODULE_ID",
    "SETTINGS_KEYS",
    "TASK_TYPES",
    "EmbeddingRebuildPort",
    "ProviderProbePort",
    "SecretWriterPort",
    "SettingsContext",
    "SettingsProviderView",
    "StorageGuardPort",
    "get_config",
    "test_provider",
    "update_config",
]
