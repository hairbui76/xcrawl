"""HTTP surface of ``MOD-telegram-adapter``. Three routes, exactly as openapi declares them.

============================================  ==============================  ==============
path                                          operation                        auth
============================================  ==============================  ==============
``POST   /v1/telegram/webhook``               ``telegram.receive_update``      telegramIngressSecret
``POST   /v1/telegram/link-codes``            ``telegram.issue_link_code``     cookie AND CSRF
``DELETE /v1/telegram/link``                  ``telegram.unlink``              cookie AND CSRF
============================================  ==============================  ==============

``telegram.execute_command`` and ``telegram.consume_link_code`` are **internal** in
``contracts/ports.yaml`` and are deliberately absent here: exposing either over HTTP would
create an edge the module registry does not grant and would put the B09 exception on the
open internet.

The webhook always answers 204
------------------------------
``contracts/http/openapi.yaml``: *"LUÔN 204 với mọi update hợp lệ về mặt transport — kể cả
update bị bỏ im lặng."* A distinguishable status code would be a reply: it would tell an
unlinked sender that this address is a bot and that its message was interesting. So a
dropped update, a link-code miss and an executed ``/status`` are all 204, and only a failure
of the *transport* contract -- bad secret, malformed body -- gets a code of its own.

The unlink/link-code routes are ordinary owner mutations: cookie **and** CSRF in one
security requirement, ``CSRF_REJECTED`` (403) without the double-submit and the session
left intact.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.db import session_scope
from server.app.telegram.commands import CommandPortUnavailable
from server.app.telegram.ingress import (
    TELEGRAM_SECRET_HEADER,
    TelegramContext,
    TelegramError,
    receive_update,
    verify_webhook_secret,
)
from server.app.telegram.linking import (
    issue_link_code,
    link_snapshot,
    new_ulid,
    unlink,
)

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
SESSION_COOKIE = "rr_session"
CSRF_COOKIE = "rr_csrf"
CSRF_HEADER = "X-CSRF-Token"

router = APIRouter(tags=["telegram"])


def install_telegram(app: FastAPI, context: TelegramContext | None = None) -> None:
    """Mount the routes and, optionally, the context they run against.

    Without a context the routes still exist and answer ``INTERNAL``: a deployment that
    wired no database must not be silently indistinguishable from one that did.
    """
    if context is not None:
        app.state.telegram_context = context
    app.include_router(router)


def _context(request: Request) -> TelegramContext:
    context = getattr(request.app.state, "telegram_context", None)
    if context is None:
        raise TelegramError(
            ErrorCode.INTERNAL,
            "Lỗi nội bộ. Yêu cầu chưa được xử lý.",
            details_safe=None,
        )
    assert isinstance(context, TelegramContext)
    return context


def _correlation_id(request: Request) -> str:
    """The caller's ``X-Request-Id`` if it sent one, else a ULID from process memory.

    Never read from a row: ``errors.yaml`` ``EPR-01`` requires the envelope to be complete
    while storage is unavailable, and a correlation id fetched from the database would be
    the one field that disappears exactly when it is needed.
    """
    return request.headers.get(REQUEST_ID_HEADER) or new_ulid()


def _error_response(error: TelegramError, correlation_id: str) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        headers["Retry-After"] = str(max(1, error.retry_after_ms // 1000))
    return JSONResponse(
        status_code=error.http_status, content=error.envelope(correlation_id), headers=headers
    )


def _ok(payload: dict[str, Any], *, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _authenticate_owner(request: Request, *, mutation: bool) -> str:
    """Owner session, and CSRF for a mutation. Delegates to ``TC-owner-auth-session``.

    Imported inside the function: the auth package is another card's module and a top-level
    import would make this module unimportable in a deployment that has not installed it,
    turning a missing dependency into a startup crash instead of a 401.
    """
    from server.app.auth.middleware import require_csrf, require_owner_session
    from server.app.auth.service import AuthError

    try:
        principal = require_owner_session(request)
        if mutation:
            require_csrf(request)
    except AuthError as error:  # translate the sibling card's exception into this card's
        raise TelegramError(
            error.code,
            "Không có quyền thực hiện thao tác này."
            if error.code is ErrorCode.UNAUTHORIZED
            else "Yêu cầu thiếu hoặc sai CSRF token.",
            details_safe=error.details_safe or None,
        ) from error
    session = principal.session
    if session is None:  # pragma: no cover - require_owner_session always sets it
        raise TelegramError(ErrorCode.UNAUTHORIZED, "Không có quyền thực hiện thao tác này.")
    return str(session.owner_id)


@router.post(
    "/v1/telegram/webhook",
    operation_id=OperationId.TELEGRAM_RECEIVE_UPDATE.value,
    status_code=204,
    response_model=None,
)
async def telegram_webhook(request: Request) -> Response:
    """``telegram.receive_update`` — 204 for every transport-valid update.

    The secret header is checked **before** the body is looked at: ING-02 says the payload's
    ``chat_id`` means nothing until the secret matched, and reading the body first would
    invite a decision to be made on unauthenticated data.
    """
    correlation_id = _correlation_id(request)
    try:
        context = _context(request)
        verify_webhook_secret(request.headers.get(TELEGRAM_SECRET_HEADER), context.webhook_secret)
        payload = await request.json()
        if not isinstance(payload, dict):
            raise TelegramError(
                ErrorCode.VALIDATION_ERROR,
                "Dữ liệu gửi lên không hợp lệ.",
                details_safe={
                    "operation_id": OperationId.TELEGRAM_RECEIVE_UPDATE.value,
                    "field_path": "body",
                    "violation_kind": "type_mismatch",
                },
            )
        receive_update(context, payload)
    except TelegramError as error:
        return _error_response(error, correlation_id)
    except CommandPortUnavailable:
        # A wiring gap, not a client error, and never a fabricated answer to the chat.
        return _error_response(
            TelegramError(ErrorCode.INTERNAL, "Lỗi nội bộ. Yêu cầu chưa được xử lý."),
            correlation_id,
        )
    return Response(status_code=204, headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION})


@router.post(
    "/v1/telegram/link-codes",
    operation_id=OperationId.TELEGRAM_ISSUE_LINK_CODE.value,
    status_code=201,
    response_model=None,
)
async def create_link_code(request: Request) -> Response:
    """``telegram.issue_link_code`` — the code is returned **once**, in this response.

    It is not written to a log, not stored in plaintext and never sent over Telegram
    (``commands.yaml`` § linking → issue_flow): the app displays it and the owner types it
    into the chat. That one-way trip is what makes the B09 exception safe -- a code that
    travelled over the channel it authorises would authorise whoever intercepted it.
    """
    correlation_id = _correlation_id(request)
    try:
        context = _context(request)
        owner_id = _authenticate_owner(request, mutation=True)
        with session_scope(context.engine) as connection:
            issued = issue_link_code(
                connection, owner_id=owner_id, now=_now(), policy=context.policy
            )
    except TelegramError as error:
        return _error_response(error, correlation_id)
    return _ok(
        {
            "code": issued.code,
            "expires_at": issued.expires_at,
            "schema_version": CONTRACT_SCHEMA_VERSION,
        },
        status_code=201,
    )


@router.delete(
    "/v1/telegram/link",
    operation_id=OperationId.TELEGRAM_UNLINK.value,
    response_model=None,
)
async def delete_link(request: Request) -> Response:
    """``telegram.unlink`` — the app action of ``AMD-B10``, idempotent by contract.

    Unlinking an already-unlinked account is a 200 with ``linked: false``, not a 404: the
    caller asked for a state and that state holds.

    Cancelling the deliveries pinned to the revoked generation is ``T-DL-08`` in
    ``MOD-delivery-service`` (fixture ``d``). This route does not reach into ``delivery``
    rows; that edge belongs to ``TC-telegram-unknown-delivery``.
    """
    correlation_id = _correlation_id(request)
    try:
        context = _context(request)
        owner_id = _authenticate_owner(request, mutation=True)
        with session_scope(context.engine) as connection:
            result = unlink(connection, owner_id=owner_id, now=_now())
            snapshot = link_snapshot(connection, owner_id=owner_id)
    except TelegramError as error:
        return _error_response(error, correlation_id)
    return _ok(
        {
            "linked": snapshot["linked"],
            "revoked_generation": result.revoked_generation,
            "schema_version": CONTRACT_SCHEMA_VERSION,
        }
    )


def _now() -> datetime:
    """The server clock, in one place so a test can monkeypatch a single symbol."""
    return datetime.now(tz=UTC)


__all__ = ["install_telegram", "router"]
