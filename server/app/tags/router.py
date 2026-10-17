"""HTTP surface of ``MOD-tag-service`` — card ``TC-tag-service``.

Routes, methods, status codes and security are read from ``contracts/http/openapi.yaml``:

======================================  =======================  ============================
path                                    operation                auth
======================================  =======================  ============================
``GET    /v1/tags``                     ``tag.list``             cookie
``POST   /v1/tags``                     ``tag.create`` (201)     cookie AND CSRF
``PATCH  /v1/tags/{tag_id}``            ``tag.update``           cookie AND CSRF
``DELETE /v1/tags/{tag_id}``            ``tag.delete``           cookie AND CSRF
``POST   /v1/tags/preview-matches``     ``tag.preview_matches``  cookie (read-only)
``POST   /v1/tags/rescan-corpus``       ``tag.rescan_corpus``    cookie AND CSRF (202)
======================================  =======================  ============================

``tag.get_active_config_version`` and ``tag.freeze_config_version`` are **not** routed: both are
``transport: internal`` for ``MOD-report-service`` only, and an HTTP path for them would be an
edge ``contracts/modules.yaml`` does not grant.

``tag.rescan_corpus`` closes ``CR-TC-BACKFILL-12``: the service has existed since
``TC-backfill-pending-ledger`` but nothing routed it.

Every caller that is not the owner's browser session — collector token, analysis worker token,
Telegram, nothing at all — is ``UNAUTHORIZED`` (401), ruling R5-01 row 1 (``FE-11``, ``FE-12``,
``FE-30``). Request bodies are ``GenericObject`` in openapi; the shapes this router accepts are
pinned in card §4 and raised as ``CR-TC-TAG-07``.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.tags import service
from server.app.tags.service import OWNER_MODULE, TagContext, TagError

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

router = APIRouter(tags=["tags"])


# --------------------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------------------


def _error_response(error: TagError) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        headers["Retry-After"] = str(max(1, error.retry_after_ms // 1000))
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(service.new_ulid()),
        headers=headers,
    )


def _ok(payload: dict[str, Any], *, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _context(request: Request, operation: OperationId) -> TagContext:
    """``app.state.tag_context``. Never defaulted: an unwired deployment answers ``INTERNAL``."""
    context = getattr(request.app.state, "tag_context", None)
    if not isinstance(context, TagContext):
        raise TagError(ErrorCode.INTERNAL, details_safe={"operation_id": operation.value})
    return context


def _require_wire_headers(request: Request, operation: OperationId, *, mutation: bool) -> str:
    """The openapi header parameters; returns the ``Idempotency-Key`` of a mutation."""
    required = [SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER]
    if mutation:
        required.append(IDEMPOTENCY_KEY_HEADER)
    for header in required:
        if not request.headers.get(header):
            raise TagError(
                ErrorCode.VALIDATION_ERROR,
                message_safe="Thiếu header bắt buộc theo hợp đồng wire.",
                details_safe={
                    "operation_id": operation.value,
                    "field_path": f"header.{header}",
                    "violation_kind": "required_header_missing",
                },
            )
    sent = request.headers[SCHEMA_VERSION_HEADER]
    if sent.split(".")[0] != CONTRACT_SCHEMA_VERSION.split(".")[0]:
        raise TagError(
            ErrorCode.VALIDATION_ERROR,
            message_safe="Phiên bản schema không được hỗ trợ.",
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )
    return request.headers.get(IDEMPOTENCY_KEY_HEADER, "")


async def _json_body(request: Request, operation: OperationId) -> dict[str, Any]:
    raw = await request.body()
    if not raw:
        return {}
    try:
        body = await request.json()
    except ValueError as exc:
        raise TagError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"operation_id": operation.value, "violation_kind": "malformed_json"},
        ) from exc
    if not isinstance(body, dict):
        raise TagError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"operation_id": operation.value, "violation_kind": "schema_invalid"},
        )
    return body


def _owner_session(request: Request, operation: OperationId, *, mutation: bool) -> None:
    """``ownerSessionCookie`` (+ ``ownerCsrfToken`` on a mutation), via the one auth module.

    No credential at all is ``UNAUTHORIZED`` before CSRF is looked at — the order openapi puts
    the two schemes in one requirement.
    """
    from server.app.auth.middleware import require_csrf, require_owner_session
    from server.app.auth.service import AuthError

    try:
        require_owner_session(request)
        if mutation:
            require_csrf(request)
    except AuthError as denied:
        details: dict[str, Any] = {"operation_id": operation.value}
        if denied.code is ErrorCode.UNAUTHORIZED:
            details["required_auth_scope"] = "owner_session"
        raise TagError(denied.code, details_safe=details) from denied


def _from_rescan(error: Exception) -> TagError:
    """``RescanError`` / ``StorageRefused`` → this module's envelope, code carried through."""
    from server.app.tags.rescan import RescanError

    def _registered(code: ErrorCode, details: dict[str, Any]) -> dict[str, Any]:
        # `rescan.py` predates this envelope and names `idempotency_key_kind`, which is not a
        # registered key of IDEMPOTENCY_CONFLICT; unregistered keys are dropped, never sent.
        allowed = service.DETAILS_SAFE_KEYS.get(code, frozenset())
        return {key: value for key, value in details.items() if key in allowed}

    if isinstance(error, RescanError):
        return TagError(error.code, details_safe=_registered(error.code, error.details_safe))
    envelope = getattr(error, "envelope", None)
    if isinstance(envelope, dict):
        code = ErrorCode(envelope["code"])
        return TagError(
            code,
            message_safe=envelope.get("message_safe"),
            details_safe=_registered(code, envelope.get("details_safe") or {}),
            retry_after_ms=envelope.get("retry_after_ms"),
        )
    raise error


# --------------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------------


@router.get("/v1/tags", operation_id=OperationId.TAG_LIST.value)
async def get_tags(request: Request) -> JSONResponse:
    """``tag.list``. ``limit`` / ``cursor`` are accepted and not needed: the set is one owner's
    subscriptions, returned whole, and a page boundary inside it would split a tag from its
    aliases."""
    operation = OperationId.TAG_LIST
    try:
        _require_wire_headers(request, operation, mutation=False)
        _owner_session(request, operation, mutation=False)
        return _ok(service.list_tags(_context(request, operation)))
    except TagError as error:
        return _error_response(error)


@router.post("/v1/tags", operation_id=OperationId.TAG_CREATE.value)
async def post_tag(request: Request) -> JSONResponse:
    """``tag.create`` — 201 with the tag, the new config version and the backfill activation."""
    operation = OperationId.TAG_CREATE
    try:
        key = _require_wire_headers(request, operation, mutation=True)
        _owner_session(request, operation, mutation=True)
        body = await _json_body(request, operation)
        result = service.create_tag(_context(request, operation), idempotency_key=key, body=body)
        return _ok(result, status_code=201)
    except TagError as error:
        return _error_response(error)


@router.patch("/v1/tags/{tag_id}", operation_id=OperationId.TAG_UPDATE.value)
async def patch_tag(request: Request, tag_id: str) -> JSONResponse:
    """``tag.update`` — threshold, aliases, exclusions. ``text`` is not editable (card §4)."""
    operation = OperationId.TAG_UPDATE
    try:
        key = _require_wire_headers(request, operation, mutation=True)
        _owner_session(request, operation, mutation=True)
        body = await _json_body(request, operation)
        context = _context(request, operation)
        return _ok(service.update_tag(context, tag_id=tag_id, idempotency_key=key, body=body))
    except TagError as error:
        return _error_response(error)


@router.delete("/v1/tags/{tag_id}", operation_id=OperationId.TAG_DELETE.value)
async def delete_tag(request: Request, tag_id: str) -> JSONResponse:
    """``tag.delete`` — idempotent; deletes no post, work, analysis or Saved row."""
    operation = OperationId.TAG_DELETE
    try:
        key = _require_wire_headers(request, operation, mutation=True)
        _owner_session(request, operation, mutation=True)
        body = await _json_body(request, operation)
        context = _context(request, operation)
        return _ok(service.delete_tag(context, tag_id=tag_id, idempotency_key=key, body=body))
    except TagError as error:
        return _error_response(error)


@router.post("/v1/tags/preview-matches", operation_id=OperationId.TAG_PREVIEW_MATCHES.value)
async def post_preview(request: Request) -> JSONResponse:
    """``tag.preview_matches`` — a POST that writes nothing, so no CSRF and no idempotency key."""
    operation = OperationId.TAG_PREVIEW_MATCHES
    try:
        _require_wire_headers(request, operation, mutation=False)
        _owner_session(request, operation, mutation=False)
        body = await _json_body(request, operation)
        return _ok(service.preview_matches(_context(request, operation), body))
    except TagError as error:
        return _error_response(error)


@router.post("/v1/tags/rescan-corpus", operation_id=OperationId.TAG_RESCAN_CORPUS.value)
async def post_rescan(request: Request) -> JSONResponse:
    """``tag.rescan_corpus`` — 202; the ``Idempotency-Key`` header is its ``request_id``."""
    from server.app.tags import rescan

    operation = OperationId.TAG_RESCAN_CORPUS
    try:
        key = _require_wire_headers(request, operation, mutation=True)
        _owner_session(request, operation, mutation=True)
        body = await _json_body(request, operation)
        for name in body:
            if name not in {"tag_id", "scope_from"}:
                raise TagError(
                    ErrorCode.VALIDATION_ERROR,
                    details_safe={
                        "operation_id": operation.value,
                        "field_path": name,
                        "violation_kind": "unknown_field",
                    },
                )
        context = getattr(request.app.state, "rescan_context", None)
        if not isinstance(context, rescan.RescanContext):
            raise TagError(ErrorCode.INTERNAL, details_safe={"operation_id": operation.value})
        tag_id = body.get("tag_id")
        scope_from = body.get("scope_from")
        if tag_id is not None and not isinstance(tag_id, str):
            raise TagError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": operation.value,
                    "field_path": "tag_id",
                    "violation_kind": "type_invalid",
                },
            )
        try:
            record = rescan.request_rescan(
                context,
                tag_id=tag_id,
                request_id=key,
                scope_from=scope_from if isinstance(scope_from, str) else None,
                caller_module="MOD-web-ui",
            )
        except Exception as refused:  # RescanError / StorageRefused / AuthError(FORBIDDEN_EDGE)
            raise _from_rescan(refused) from refused
        return _ok(
            {
                "rescan_id": record.id,
                "tag_id": record.tag_id,
                "state": record.state,
                "requested_at": record.requested_at,
                "scope_from": record.scope_from,
            },
            status_code=202,
        )
    except TagError as error:
        return _error_response(error)


__all__ = ["OWNER_MODULE", "router"]
