"""HTTP surface of ``MOD-delivery-service``: ``delivery.get_status``, ``delivery.decide_unknown``.

Routes, methods, status codes and security come from ``contracts/http/openapi.yaml``:

===============================================  =============================  ==============
path                                             operation                       auth
===============================================  =============================  ==============
``GET  /v1/deliveries/{delivery_id}``            ``delivery.get_status``         cookie
``POST /v1/deliveries/parts/{id}/decide``        ``delivery.decide_unknown``     cookie AND CSRF
===============================================  =============================  ==============

Session and CSRF belong to ``TC-owner-auth-session``. This file declares the seam and
installs a provider that denies everything, so a route wired before that card lands answers
``401 UNAUTHORIZED`` instead of serving owner data to an unauthenticated caller.

Every failure leaves as the seven-field envelope of ``contracts/errors.yaml``, with the code
taken from the generated registry -- never a string literal. A missing CSRF token is
``CSRF_REJECTED`` (403) and does **not** end the session; a caller that is not ``MOD-web-ui``
is ``FORBIDDEN_EDGE``, which is a different fact from being unauthenticated (ruling R5-01).

There is no route here for ``delivery.dispatch_next``, ``create_intent``, ``record_receipt``
or ``mark_unknown``: ``contracts/ports.yaml`` marks all four ``transport: internal``, and
exposing any of them over HTTP would hand an outside caller the send path.
"""

from __future__ import annotations

from typing import Any, Protocol

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import DeliveryUnknownDecision

from server.app.delivery.outbox import new_ulid
from server.app.delivery.service import (
    DeliveryContext,
    DeliveryDependencyUnavailable,
    DeliveryError,
    decide_unknown,
    get_status,
)

SESSION_COOKIE = "rr_session"
CSRF_COOKIE = "rr_csrf"
CSRF_HEADER = "X-CSRF-Token"
REQUEST_ID_HEADER = "X-Request-Id"
SCHEMA_VERSION_HEADER = "X-Schema-Version"

router = APIRouter(tags=["delivery"])


class OwnerSessionAuthenticator(Protocol):
    """Seam owned by ``TC-owner-auth-session``; identical shape to the identity router's."""

    def authenticate(
        self,
        *,
        session_cookie: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        mutation: bool,
    ) -> str: ...  # pragma: no cover - protocol declaration


class DenyAllOwnerSession:
    """In force until a real authenticator is installed. Denies every request.

    Returning a fabricated owner id would turn "authentication is not wired" into "everyone
    is the owner", the conversion ``I13`` and CAP-P5 forbid elsewhere in this system.
    """

    def authenticate(
        self,
        *,
        session_cookie: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        mutation: bool,
    ) -> str:
        raise DeliveryError(
            ErrorCode.UNAUTHORIZED,
            details_safe={"operation_id": None, "required_auth_scope": "owner_session"},
            message_safe="Phiên đăng nhập của owner chưa được cấu hình trên máy chủ này.",
        )


def _authenticator(request: Request) -> OwnerSessionAuthenticator:
    provider = getattr(request.app.state, "owner_session_authenticator", None)
    if provider is None:
        return DenyAllOwnerSession()
    return provider  # type: ignore[no-any-return]


def _context(request: Request) -> DeliveryContext:
    context = getattr(request.app.state, "delivery_context", None)
    if context is None:
        raise DeliveryDependencyUnavailable("app.state.delivery_context is not configured")
    return context  # type: ignore[no-any-return]


def _correlation_id(request: Request) -> str:
    """The caller's ``X-Request-Id`` when it sent one, else a fresh id from process memory.

    Never read from a row: the envelope must carry one even when nothing can be written
    (``contracts/errors.yaml`` ``correlation_rule_vi``).
    """
    supplied = request.headers.get(REQUEST_ID_HEADER)
    return supplied if supplied else new_ulid()


def _error_response(error: DeliveryError, correlation_id: str) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        headers["Retry-After"] = str(max(1, error.retry_after_ms // 1000))
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(correlation_id),
        headers=headers,
    )


def _ok(payload: dict[str, Any]) -> JSONResponse:
    return JSONResponse(content=payload, headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION})


@router.get("/v1/deliveries/{delivery_id}", operation_id=OperationId.DELIVERY_GET_STATUS.value)
def get_delivery_status(delivery_id: str, request: Request) -> JSONResponse:
    """``delivery.get_status`` -- read-only, so cookie without CSRF (``x-mutation: false``)."""
    correlation_id = _correlation_id(request)
    try:
        owner_id = _authenticator(request).authenticate(
            session_cookie=request.cookies.get(SESSION_COOKIE),
            csrf_cookie=request.cookies.get(CSRF_COOKIE),
            csrf_header=request.headers.get(CSRF_HEADER),
            mutation=False,
        )
        return _ok(get_status(_context(request), owner_id=owner_id, delivery_id=delivery_id))
    except DeliveryError as error:
        return _error_response(error, correlation_id)


@router.post(
    "/v1/deliveries/parts/{delivery_part_id}/decide",
    operation_id=OperationId.DELIVERY_DECIDE_UNKNOWN.value,
)
async def decide_unknown_part(delivery_part_id: str, request: Request) -> JSONResponse:
    """``delivery.decide_unknown`` -- owner session **and** CSRF, per the openapi security row.

    The body carries ``decision``, ``decision_request_id`` and
    ``duplicate_risk_accepted``. The last one is not a formality: ``§5.2`` requires the UI to
    state the duplicate risk before confirming a resend, and the server refuses a resend that
    does not carry the confirmation, so a client that skips the warning cannot skip the
    acceptance either.
    """
    correlation_id = _correlation_id(request)
    try:
        owner_id = _authenticator(request).authenticate(
            session_cookie=request.cookies.get(SESSION_COOKIE),
            csrf_cookie=request.cookies.get(CSRF_COOKIE),
            csrf_header=request.headers.get(CSRF_HEADER),
            mutation=True,
        )
        body = await _json_body(request)
        decision = _decision_of(body.get("decision"))
        decision_request_id = body.get("decision_request_id")
        if not isinstance(decision_request_id, str) or not decision_request_id:
            raise DeliveryError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                    "field_path": "decision_request_id",
                    "violation_kind": "required",
                },
            )
        return _ok(
            decide_unknown(
                _context(request),
                owner_id=owner_id,
                delivery_part_id=delivery_part_id,
                decision=decision,
                decision_request_id=decision_request_id,
                duplicate_risk_accepted=bool(body.get("duplicate_risk_accepted", False)),
            )
        )
    except DeliveryError as error:
        return _error_response(error, correlation_id)


async def _json_body(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except ValueError as invalid:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                "field_path": "body",
                "violation_kind": "malformed_json",
            },
        ) from invalid
    if not isinstance(payload, dict):
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                "field_path": "body",
                "violation_kind": "not_an_object",
            },
        )
    return payload


def _decision_of(value: Any) -> DeliveryUnknownDecision:
    """The three members of ``unknown_decision``; anything else is a validation error.

    A closed set, deliberately: the system never invents a fourth way out of ``unknown``, and
    an unrecognised value must not fall back to one of the three.
    """
    try:
        return DeliveryUnknownDecision(value)
    except ValueError as invalid:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                "field_path": "decision",
                "violation_kind": "not_in_enum",
            },
        ) from invalid


def install_delivery(app: Any, context: DeliveryContext | None = None) -> None:
    """Mount the two routes; attach ``context`` when one is supplied.

    No context is fabricated: a deployment that wires none gets ``500 INTERNAL`` from
    :func:`_context`, not a router that invents a database connection or a Telegram transport.
    """
    if context is not None:
        app.state.delivery_context = context
    app.include_router(router)
