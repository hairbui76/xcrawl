"""HTTP surface of ``MOD-saved-service``.

Routes, methods, status codes and security are read straight out of
``contracts/http/openapi.yaml``; none is invented and none is renamed:

=================================  ================  =========================================
path                               operation         auth
=================================  ================  =========================================
``POST   /v1/saved``               ``save.create``   (cookie AND CSRF) OR telegram ingress
``GET    /v1/saved``               ``save.list``     cookie
``DELETE /v1/saved/{target_ref}``  ``save.remove``   cookie AND CSRF
=================================  ================  =========================================

``save.export`` is **absent on purpose**. It exists in ``contracts/ports.yaml``, but export is
deferred for the MVP (``F-PC00-02``, REQ-OQ10) and card §10 ``SG-01`` makes shipping it a stop
condition. A route that answered it would be a feature nobody approved.

The two ways in, and why they are different
-------------------------------------------
``save.create`` is the only operation in this module with ``auth_scope:
owner_session_or_linked_chat``. openapi spells that as **two** security requirements, and they
are not interchangeable:

* ``ownerSessionCookie`` **and** ``ownerCsrfToken`` together — the browser. Missing CSRF on an
  otherwise valid session is ``CSRF_REJECTED`` (403) and does **not** end the session.
* ``telegramIngressSecret`` — the adapter. The secret is compared in constant time, and the
  chat must additionally be **linked**: an unlinked chat gets ``UNAUTHORIZED_COMMAND`` with
  zero mutations and zero replies (card §7). Linking itself belongs to
  ``TC-telegram-linking-auth``; this router asks ``app.state.telegram_link_resolver`` and
  refuses when there is none, rather than assuming the chat belongs to the owner.

Everything else — collector token, analysis worker token, no credential at all — is
``UNAUTHORIZED`` (401), which is denied cases ``NC-01``, ``NC-20`` and ``NC-36`` and ruling
R5-01 row 1. Not ``FORBIDDEN_EDGE``: that is the answer to the different question of an
in-process call across an unregistered edge, and picking the wrong one of the two is a FAIL by
card §10 ``SG-DENY``.

No business logic lives here. Transactions, the unique-index arbitration and the snapshot are
all in ``service.py``; this module maps HTTP onto that and back, and renders every failure as
the ``contracts/errors.yaml`` envelope.
"""

from __future__ import annotations

import hmac
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.saved import service
from server.app.saved.service import SavedError, TargetRef

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
TELEGRAM_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"

#: ``ENT-saved-item.save_channel`` per entry point. The channel is decided by *how the caller
#: authenticated*, never by a field in the body: a browser request that claimed
#: ``save_channel: telegram`` would put a false provenance into an immutable row.
CHANNEL_OF_CALLER: dict[str, str] = {
    "MOD-web-ui": "app",
    "MOD-telegram-adapter": "telegram",
}

router = APIRouter(tags=["saved"])


# --------------------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------------------


def _correlation_id() -> str:
    """A ULID minted in process memory.

    ``contracts/errors.yaml`` §EPR-01: ``correlation_id`` is present on every envelope,
    including while storage cannot be written — so it must not come from a database row.
    """
    return service.new_ulid()


def _error_response(error: SavedError) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        headers["Retry-After"] = str(max(1, error.retry_after_ms // 1000))
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(_correlation_id()),
        headers=headers,
    )


def _ok(payload: dict[str, Any], *, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _engine(request: Request) -> Engine:
    """``app.state.engine``. Never defaulted: a router does not invent a database.

    An unconfigured deployment gets ``INTERNAL`` (500), which is honest, rather than a
    connection to some file this module chose.
    """
    engine = getattr(request.app.state, "engine", None)
    if not isinstance(engine, Engine):
        raise SavedError(
            ErrorCode.INTERNAL,
            details_safe={"operation_id": OperationId.SAVE_CREATE.value},
        )
    return engine


def _require_wire_headers(request: Request, operation: OperationId, *, mutation: bool) -> None:
    """The required header parameters of ``contracts/http/openapi.yaml``.

    ``X-Schema-Version`` and ``X-Request-Id`` on every route, ``Idempotency-Key`` in addition
    on the two mutations (both declare it ``required: true``). A major-version mismatch is
    ``VALIDATION_ERROR`` with ``violation_kind = schema_version_unsupported``.
    """
    required = [SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER]
    if mutation:
        required.append(IDEMPOTENCY_KEY_HEADER)
    for header in required:
        if not request.headers.get(header):
            raise SavedError(
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
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            message_safe="Phiên bản schema không được hỗ trợ.",
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


async def _json_body(request: Request) -> dict[str, Any]:
    """Parse the body, mapping malformed JSON onto the contract's envelope.

    Parsed by hand rather than declared as a Pydantic parameter so that a violation produces
    ``code`` / ``retry_class`` / ``correlation_id`` instead of FastAPI's own 422 shape.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"violation_kind": "malformed_json"},
        ) from exc
    if not isinstance(body, dict):
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"violation_kind": "schema_invalid"},
        )
    return body


# --------------------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------------------


def _unauthorized(operation: OperationId, scope: str) -> SavedError:
    return SavedError(
        ErrorCode.UNAUTHORIZED,
        details_safe={"operation_id": operation.value, "required_auth_scope": scope},
    )


def _owner_session(request: Request, operation: OperationId, *, mutation: bool) -> str:
    """``ownerSessionCookie`` (+ ``ownerCsrfToken`` on a mutation) → the owner id.

    Delegates to ``TC-owner-auth-session``'s dependencies so there is exactly one session
    implementation in the process. The order matters and is the order openapi puts the two
    schemes in one requirement: a request with neither credential is ``UNAUTHORIZED``, not
    ``CSRF_REJECTED``.
    """
    from server.app.auth.middleware import require_csrf, require_owner_session
    from server.app.auth.service import AuthError

    try:
        principal = require_owner_session(request)
        if mutation:
            require_csrf(request)
    except AuthError as denied:
        details: dict[str, Any] = {"operation_id": operation.value}
        scope = (denied.details_safe or {}).get("required_auth_scope")
        if scope is not None and denied.code is ErrorCode.UNAUTHORIZED:
            details["required_auth_scope"] = scope
        raise SavedError(denied.code, details_safe=details) from denied
    session = principal.session
    owner_id = getattr(session, "owner_id", None)
    if not isinstance(owner_id, str):
        raise _unauthorized(operation, "owner_session")
    return owner_id


def _telegram_ingress(request: Request, body: dict[str, Any]) -> str | None:
    """``telegramIngressSecret`` → the linked owner id, or ``None`` when not this branch.

    Two separate refusals, and they are not the same fact:

    * a wrong or absent secret is not this branch at all — the caller falls through to the
      session branch and ends up ``UNAUTHORIZED``;
    * a **valid** secret from a chat that is not linked is ``UNAUTHORIZED_COMMAND``: the
      transport is trusted, the sender is not authorised, and card §7 requires silence with
      no state change.
    """
    expected = getattr(request.app.state, "telegram_ingress_secret", None)
    presented = request.headers.get(TELEGRAM_SECRET_HEADER)
    if not isinstance(expected, str) or not presented:
        return None
    if not hmac.compare_digest(presented, expected):
        return None

    chat_id = body.get("chat_id")
    resolver = getattr(request.app.state, "telegram_link_resolver", None)
    owner_id = None
    if resolver is not None and isinstance(chat_id, str | int):
        owner_id = resolver.owner_for_chat(str(chat_id))
    if not isinstance(owner_id, str):
        # No resolver installed is the same answer as an unlinked chat. Defaulting to "the
        # owner" because linking has not shipped yet would let any chat write Saved rows.
        raise SavedError(
            ErrorCode.UNAUTHORIZED_COMMAND,
            details_safe={
                "command_kind": "CMD-save",
                "rejection_reason_code": "chat_not_linked",
            },
        )
    return owner_id


# --------------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------------


@router.post("/v1/saved", operation_id=OperationId.SAVE_CREATE.value)
async def save_create(request: Request) -> JSONResponse:
    """``save.create`` — snapshot the target as it reads now, in one transaction.

    ``201`` with ``status: created`` for the transaction that committed; ``200`` with
    ``status: already_saved`` for a caller that lost the unique race or repeated a Telegram
    callback. The second is not an error: the row the caller asked for exists, it just was
    not this request that made it (``entities.yaml``: ``already_saved`` is a response field,
    not an error code), and every press still gets an answer (REQ-D38).
    """
    try:
        _require_wire_headers(request, OperationId.SAVE_CREATE, mutation=True)
        body = await _json_body(request)
        owner_id = _telegram_ingress(request, body)
        caller_module = "MOD-telegram-adapter"
        if owner_id is None:
            owner_id = _owner_session(request, OperationId.SAVE_CREATE, mutation=True)
            caller_module = "MOD-web-ui"
        channel = CHANNEL_OF_CALLER[caller_module]

        target_field = body.get("target")
        if isinstance(target_field, str):
            target = TargetRef.parse(target_field)
        elif isinstance(target_field, dict):
            target = TargetRef.from_object(target_field, OperationId.SAVE_CREATE)
        else:
            raise SavedError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.SAVE_CREATE.value,
                    "field_path": "target",
                    "violation_kind": "required_field_missing",
                },
            )

        result = service.create_save(
            _engine(request),
            owner_id=owner_id,
            target=target,
            save_channel=channel,
            analysis_id=_optional_str(body, "analysis_id"),
            source_report_item_id=_optional_str(body, "source_report_item_id"),
            # Stored only for the Telegram branch: `ENT-saved-item.idempotency_key` is NULL
            # for a Save made in the app, where the partial UNIQUE on the active row is the
            # arbiter instead.
            idempotency_key=(
                request.headers.get(IDEMPOTENCY_KEY_HEADER) if channel == "telegram" else None
            ),
            matched_tags=_matched_tags(body),
            caller_module=caller_module,
            guard=getattr(request.app.state, "storage_guard", None),
        )
    except SavedError as error:
        return _error_response(error)
    return _ok(
        {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "saved_item_id": result.saved_item_id,
            "status": result.status,
            "already_saved": result.already_saved,
            "saved_at": result.saved_at,
            "saved_snapshot_id": result.saved_snapshot_id,
            "content_hash": result.content_hash,
        },
        status_code=200 if result.already_saved else 201,
    )


@router.get("/v1/saved", operation_id=OperationId.SAVE_LIST.value)
def save_list(request: Request) -> JSONResponse:
    """``save.list`` — the Saved screen. Reads snapshots, never today's source rows."""
    try:
        _require_wire_headers(request, OperationId.SAVE_LIST, mutation=False)
        owner_id = _owner_session(request, OperationId.SAVE_LIST, mutation=False)
        limit = _int_param(request, "limit", default=50)
        offset = _cursor_offset(request)
        items = service.list_saved(
            _engine(request),
            owner_id=owner_id,
            limit=limit,
            offset=offset,
            query=request.query_params.get("q"),
        )
    except SavedError as error:
        return _error_response(error)
    payload: dict[str, Any] = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "items": items,
        "count": len(items),
    }
    if len(items) == limit:
        payload["next_cursor"] = f"off:{offset + limit}"
    return _ok(payload)


@router.delete("/v1/saved/{target_ref:path}", operation_id=OperationId.SAVE_REMOVE.value)
def save_remove(request: Request, target_ref: str) -> JSONResponse:
    """``save.remove`` — un-save. Deletes nothing: not the source, not the snapshot.

    Repeating it is idempotent and answers ``removed: false``; the snapshot id is still in
    the answer, because the snapshot is still readable afterwards (SRC-SPEC §7.3).
    """
    try:
        _require_wire_headers(request, OperationId.SAVE_REMOVE, mutation=True)
        owner_id = _owner_session(request, OperationId.SAVE_REMOVE, mutation=True)
        target = TargetRef.parse(target_ref)
        result = service.remove_save(
            _engine(request),
            owner_id=owner_id,
            target=target,
            guard=getattr(request.app.state, "storage_guard", None),
        )
    except SavedError as error:
        return _error_response(error)
    return _ok(
        {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "saved_item_id": result.saved_item_id,
            "state": result.state,
            "unsaved_at": result.unsaved_at,
            "removed": result.removed,
            "saved_snapshot_id": result.saved_snapshot_id,
        }
    )


# --------------------------------------------------------------------------------------
# Small parsers
# --------------------------------------------------------------------------------------


def _optional_str(body: dict[str, Any], key: str) -> str | None:
    value = body.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": key, "violation_kind": "type_not_allowed"},
        )
    return value


def _matched_tags(body: dict[str, Any]) -> list[dict[str, Any]]:
    """``matched_tags[]`` as the caller read them, validated against the snapshot schema.

    Rejected rather than trimmed: a tag object the schema would not accept must not reach an
    immutable row, and repairing it would be inventing what the screen showed.
    """
    raw = body.get("matched_tags")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": "matched_tags", "violation_kind": "type_not_allowed"},
        )
    tags: list[dict[str, Any]] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict) or not isinstance(entry.get("tag_text"), str):
            raise SavedError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "field_path": f"matched_tags[{index}]",
                    "violation_kind": "schema_invalid",
                },
            )
        tag: dict[str, Any] = {"tag_text": entry["tag_text"]}
        if isinstance(entry.get("tag_id"), str):
            tag["tag_id"] = entry["tag_id"]
        if isinstance(entry.get("similarity"), int | float) and not isinstance(
            entry.get("similarity"), bool
        ):
            tag["similarity"] = entry["similarity"]
        tags.append(tag)
    return tags


def _int_param(request: Request, name: str, *, default: int) -> int:
    raw = request.query_params.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": f"query.{name}", "violation_kind": "type_not_allowed"},
        ) from exc


def _cursor_offset(request: Request) -> int:
    """Decode the opaque page cursor. Its shape is this router's business, not the client's."""
    cursor = request.query_params.get("cursor")
    if not cursor:
        return 0
    prefix, _, value = cursor.partition(":")
    if prefix != "off" or not value.isdigit():
        raise SavedError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": "query.cursor", "violation_kind": "pattern_not_matched"},
        )
    return int(value)


__all__ = ["CHANNEL_OF_CALLER", "router"]
