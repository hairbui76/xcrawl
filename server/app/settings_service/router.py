"""HTTP surface of ``MOD-settings-service``: three routes, exactly as ``openapi.yaml`` has them.

============================================================  ==========================
``GET   /v1/settings``                                        ``settings.get_config``
``PATCH /v1/settings``                                        ``settings.update_config``
``POST  /v1/settings/providers/{provider_name}/test``         ``settings.test_provider``
============================================================  ==========================

``GET`` takes ``ownerSessionCookie``. The two mutations take ``ownerSessionCookie`` **and**
``ownerCsrfToken`` in one security requirement -- one requirement, not two alternatives -- so a
session without the double-submit token is ``CSRF_REJECTED`` (403, session intact), never
``UNAUTHORIZED``. Ruling ``R5-01`` makes that distinction a pass/fail property of the card.

The key travels in exactly one direction here. ``PATCH`` accepts ``provider_key`` in the body
and the service hands it to ``MOD-secret-service``; no response of any route in this module has
a field that could carry it back.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth.middleware import require_csrf, require_owner_session
from server.app.secret.service import SecretDependencyUnavailable, SecretError
from server.app.settings_service.repository import new_ulid
from server.app.settings_service.service import (
    SettingsContext,
    get_config,
    test_provider,
    update_config,
)

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"

router = APIRouter(tags=["settings"])


def _correlation_id() -> str:
    return new_ulid()


def _error_response(error: SecretError) -> JSONResponse:
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(_correlation_id()),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _internal_response(operation: OperationId) -> JSONResponse:
    correlation = _correlation_id()
    return JSONResponse(
        status_code=500,
        content=SecretError(
            ErrorCode.INTERNAL,
            "Dịch vụ chưa được cấu hình đầy đủ.",
            details_safe={"correlation_id": correlation, "operation_id": operation.value},
        ).envelope(correlation),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _require_wire_headers(request: Request, operation: OperationId) -> None:
    for header in (SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER):
        if not request.headers.get(header):
            raise SecretError(
                ErrorCode.VALIDATION_ERROR,
                "Thiếu header bắt buộc theo hợp đồng wire.",
                details_safe={
                    "operation_id": operation.value,
                    "field_path": f"header.{header}",
                    "violation_kind": "required_header_missing",
                },
            )
    sent = request.headers[SCHEMA_VERSION_HEADER]
    if sent.split(".")[0] != CONTRACT_SCHEMA_VERSION.split(".")[0]:
        raise SecretError(
            ErrorCode.VALIDATION_ERROR,
            "Phiên bản schema không được hỗ trợ.",
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


def _context(request: Request) -> SettingsContext:
    context: SettingsContext | None = getattr(request.app.state, "settings_context", None)
    if context is None:
        raise SecretDependencyUnavailable("app.state.settings_context is not configured")
    return context


def _ok(payload: dict[str, Any]) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


@router.get("/v1/settings", dependencies=[Depends(require_owner_session)])
async def get_settings(request: Request) -> JSONResponse:
    """``settings.get_config`` -- reference and status only, never a key value."""
    operation = OperationId.SETTINGS_GET_CONFIG
    try:
        _require_wire_headers(request, operation)
        return _ok(get_config(_context(request)))
    except SecretError as error:
        return _error_response(error)
    except SecretDependencyUnavailable:
        return _internal_response(operation)


@router.patch(
    "/v1/settings",
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
async def patch_settings(request: Request) -> JSONResponse:
    """``settings.update_config`` -- owner session **and** CSRF, in one requirement."""
    operation = OperationId.SETTINGS_UPDATE_CONFIG
    try:
        _require_wire_headers(request, operation)
        body = await request.json()
        if not isinstance(body, dict):
            raise SecretError(
                ErrorCode.VALIDATION_ERROR,
                "Body phải là một object JSON.",
                details_safe={
                    "operation_id": operation.value,
                    "field_path": "body",
                    "violation_kind": "type_mismatch",
                },
            )
        result = update_config(
            _context(request),
            request_id=request.headers.get(REQUEST_ID_HEADER, ""),
            settings=body.get("settings"),
            provider=body.get("provider"),
            provider_key=body.get("provider_key"),
        )
        return _ok(result)
    except SecretError as error:
        return _error_response(error)
    except SecretDependencyUnavailable:
        return _internal_response(operation)


@router.post(
    "/v1/settings/providers/{provider_name}/test",
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
async def post_provider_test(provider_name: str, request: Request) -> JSONResponse:
    """``settings.test_provider`` -- one new result row per call, ``unknown`` allowed."""
    operation = OperationId.SETTINGS_TEST_PROVIDER
    try:
        _require_wire_headers(request, operation)
        return _ok(test_provider(_context(request), provider_name=provider_name))
    except SecretError as error:
        return _error_response(error)
    except SecretDependencyUnavailable:
        return _internal_response(operation)


__all__ = ["router"]
