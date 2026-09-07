"""HTTP handlers for ``auth.login``, ``auth.logout`` and ``auth.get_session``.

Paths, status codes, headers and bodies come from ``contracts/http/openapi.yaml``. Three
things about this router are contract obligations rather than style:

* **There is no fourth route.** No signup, no password reset, no "forgot password"
  (REQ-D05). ``acceptance/fixtures/ui/sc51-first-time-setup.json`` lists the existence of a
  signup endpoint as a forbidden effect, and ``tests/contract/test_auth_scheme_matrix.py``
  asserts the absence by scanning the mounted routes.
* **``/v1/auth/logout`` depends on the cookie *and* the CSRF token, in that order.** The
  order is what makes an entirely unauthenticated call ``UNAUTHORIZED`` rather than
  ``CSRF_REJECTED``.
* **The error body is the envelope of ``contracts/errors.yaml``** -- and never contains a
  cookie, a token, a password or a stack trace.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth.csrf import CSRF_COOKIE_NAME
from server.app.auth.middleware import (
    SESSION_COOKIE_NAME,
    Principal,
    require_csrf,
    require_owner_session,
)
from server.app.auth.service import (
    IDLE_TIMEOUT_MS,
    AuthError,
    AuthService,
    from_epoch_ms,
    new_ulid,
    to_timestamp_utc_ms,
)

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    """``components.schemas.LoginRequest``.

    Hand-written because the generator emits only the seven standalone JSON Schemas of
    ``contracts/schemas/`` and not the inline OpenAPI components (``CR-TC-AUTH-04``); the
    contract test asserts these field names and bounds still equal the document.
    """

    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=8, max_length=1024)


class SessionInfo(BaseModel):
    """``components.schemas.SessionInfo``. Carries no secret beyond the CSRF token."""

    model_config = ConfigDict(extra="forbid")

    authenticated: bool
    csrf_token: str | None = Field(default=None, min_length=32, max_length=128)
    expires_at: str | None = None
    schema_version: str | None = None


def _correlation_id() -> str:
    """A ULID minted in process memory, so an envelope is complete even with storage down."""
    return new_ulid()


def _error_response(error: AuthError) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        # openapi declares a `Retry-After` header (seconds) on the 429/503 responses; the
        # envelope carries the millisecond value under `retry_after_ms`.
        headers["Retry-After"] = str(max(1, error.retry_after_ms // 1000))
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(_correlation_id()),
        headers=headers,
    )


def _require_wire_headers(request: Request, operation: OperationId) -> None:
    """``X-Schema-Version`` and ``X-Request-Id`` are required parameters on every path.

    A major-version mismatch is ``VALIDATION_ERROR`` with
    ``details_safe.violation_kind = schema_version_unsupported`` (openapi
    ``components.parameters.SchemaVersionHeader``); ``latest`` is not accepted.
    """
    for header in (SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER):
        if not request.headers.get(header):
            raise AuthError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": operation.value,
                    "field_path": f"header.{header}",
                    "violation_kind": "required_header_missing",
                },
            )
    sent = request.headers[SCHEMA_VERSION_HEADER]
    if sent.split(".")[0] != CONTRACT_SCHEMA_VERSION.split(".")[0]:
        raise AuthError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


def _wellformed_csrf(value: str | None) -> str | None:
    """Echo the CSRF cookie back only if it is within the schema bounds (32..128)."""
    return value if value is not None and 32 <= len(value) <= 128 else None


def _service(request: Request) -> AuthService:
    service = request.app.state.auth_service
    assert isinstance(service, AuthService)
    return service


def _set_session_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    """``rr_session`` HttpOnly+Secure+SameSite=Lax; ``rr_csrf`` readable by the page.

    ``rr_csrf`` is intentionally **not** HttpOnly: the browser half of the double-submit
    (``web/src/lib/api.ts``, owned by the UI cards) has to read it to set the header.
    """
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=IDLE_TIMEOUT_MS // 1000,
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=IDLE_TIMEOUT_MS // 1000,
        path="/",
    )


@router.post(
    "/v1/auth/login",
    operation_id=OperationId.AUTH_LOGIN.value,
    response_model=None,
)
def login(request: Request, body: LoginRequest) -> Any:
    """``auth.login`` -- ``security: []``, the only unauthenticated mutation.

    Not a signup: the row it authenticates against is created by the operator through
    ``AuthService.bootstrap_owner``. Wrong password and unknown account are indistinguishable
    to the caller, by contract.
    """
    try:
        _require_wire_headers(request, OperationId.AUTH_LOGIN)
        result = _service(request).login(
            body.username, body.password, user_agent=request.headers.get("User-Agent")
        )
    except AuthError as error:
        return _error_response(error)
    payload = SessionInfo(
        authenticated=True,
        csrf_token=result.csrf_token,
        expires_at=to_timestamp_utc_ms(from_epoch_ms(result.session.expires_at_ms)),
        schema_version=CONTRACT_SCHEMA_VERSION,
    )
    response = JSONResponse(
        status_code=200,
        content=payload.model_dump(),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )
    _set_session_cookies(response, result.session_token, result.csrf_token)
    return response


@router.post(
    "/v1/auth/logout",
    operation_id=OperationId.AUTH_LOGOUT.value,
    status_code=204,
    response_model=None,
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
def logout(request: Request) -> Any:
    """``auth.logout`` -- ``ownerSessionCookie`` **and** ``ownerCsrfToken``.

    204, and both cookies are cleared. Idempotent on an already-revoked session.
    """
    try:
        _require_wire_headers(request, OperationId.AUTH_LOGOUT)
        _service(request).logout(request.cookies.get(SESSION_COOKIE_NAME))
    except AuthError as error:
        return _error_response(error)
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")
    return response


@router.get(
    "/v1/auth/session",
    operation_id=OperationId.AUTH_GET_SESSION.value,
    response_model=None,
)
def get_session(
    request: Request,
    principal: Annotated[Principal, Depends(require_owner_session)],
) -> Any:
    """``auth.get_session`` -- cookie alone; a read needs no CSRF proof."""
    try:
        _require_wire_headers(request, OperationId.AUTH_GET_SESSION)
    except AuthError as error:
        return _error_response(error)
    session = principal.session
    assert session is not None
    payload = SessionInfo(
        authenticated=True,
        csrf_token=_wellformed_csrf(request.cookies.get(CSRF_COOKIE_NAME)),
        expires_at=to_timestamp_utc_ms(from_epoch_ms(session.expires_at_ms)),
        schema_version=CONTRACT_SCHEMA_VERSION,
    )
    return JSONResponse(
        status_code=200,
        content=payload.model_dump(),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def install_auth(app: Any, service: AuthService | None = None, token_registry: Any = None) -> None:
    """Wire this card's error handler, router and (optionally) its service into ``app``.

    Called from the delimited include block in ``server/app/main.py``. The service is
    **optional on purpose**: the bare factory has no database URL -- ``server/migrations``
    refuses to guess one -- so constructing an ``AuthService`` here would invent a storage
    location. When it is absent every owner-session dependency answers ``UNAUTHORIZED``
    (401), which is the default-deny outcome and, importantly, not a 500: other cards'
    routers that depend on ``require_owner_session`` keep working on the bare app
    (Coordinator note CR-03).
    """
    app.add_exception_handler(AuthError, auth_error_handler)
    app.include_router(router)
    if service is not None:
        app.state.auth_service = service
    if token_registry is not None:
        app.state.token_registry = token_registry


def auth_error_handler(_request: Request, exc: Exception) -> Response:
    """App-level handler so a dependency's ``AuthError`` becomes the contract envelope."""
    assert isinstance(exc, AuthError)
    return _error_response(exc)


__all__ = ["LoginRequest", "SessionInfo", "auth_error_handler", "install_auth", "router"]
