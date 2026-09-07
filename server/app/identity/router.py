"""HTTP surface of ``MOD-identity-service``: ``identity.resolve_conflict`` and ``work.get_detail``.

Routes, methods, status codes and security come from ``contracts/http/openapi.yaml``:

============================================  ================================  ==============
path                                          operation                          auth
============================================  ================================  ==============
``POST /v1/identity/conflicts/{id}/resolve``  ``identity.resolve_conflict``      cookie AND CSRF
``GET  /v1/works/{work_id}``                  ``work.get_detail``                cookie
============================================  ================================  ==============

Two boundaries this module keeps deliberately thin:

*Session and CSRF* belong to ``TC-owner-auth-session``. This file declares the seam
(:class:`OwnerSessionAuthenticator`) and installs a provider that denies everything, so a route
that is wired before that card lands answers ``401 UNAUTHORIZED`` rather than serving owner data
to an unauthenticated caller. Silence is not a default here.

*Error rendering*: every failure leaves as the envelope of ``contracts/errors.yaml`` --
``code``, ``scope``, ``retry_class``, ``message_safe``, ``correlation_id``, ``details_safe`` --
with the code coming from the generated registry. A missing CSRF token is ``CSRF_REJECTED``
(403) and does NOT end the session; a caller that is not ``MOD-web-ui`` is ``FORBIDDEN_EDGE``,
which is a different fact from being unauthenticated (ruling R5-01).
"""

from __future__ import annotations

from typing import Any, Protocol

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.identity import service
from server.app.identity.repository import new_ulid
from server.app.identity.service import IdentityError

SESSION_COOKIE = "rr_session"
CSRF_COOKIE = "rr_csrf"
CSRF_HEADER = "X-CSRF-Token"
REQUEST_ID_HEADER = "X-Request-Id"
SCHEMA_VERSION_HEADER = "X-Schema-Version"

router = APIRouter(tags=["identity"])


class OwnerSessionAuthenticator(Protocol):
    """Seam owned by ``TC-owner-auth-session``.

    :param session_cookie: value of the ``rr_session`` cookie, if any.
    :param csrf_cookie: value of the ``rr_csrf`` cookie, if any.
    :param csrf_header: value of the ``X-CSRF-Token`` header, if any.
    :param mutation: ``True`` for a state-changing route; the CSRF check applies only then,
        because CSRF protects writes, not reads (openapi ``ownerSessionCookie``).
    :returns: the authenticated ``owner_id``.
    :raises IdentityError: ``UNAUTHORIZED`` or ``CSRF_REJECTED``.
    """

    def authenticate(
        self,
        *,
        session_cookie: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        mutation: bool,
    ) -> str: ...  # pragma: no cover - protocol declaration


class DenyAllOwnerSession:
    """The provider in force until ``TC-owner-auth-session`` installs the real one.

    It denies every request. Returning a fabricated owner id would turn "authentication is not
    implemented yet" into "everyone is the owner", which is exactly the conversion I13 and
    CAP-P5 forbid elsewhere in this system.
    """

    def authenticate(
        self,
        *,
        session_cookie: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        mutation: bool,
    ) -> str:
        raise IdentityError(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": None,
                "required_auth_scope": "owner_session",
            },
            message_safe="Phiên đăng nhập của owner chưa được cấu hình trên máy chủ này.",
        )


def _authenticator(request: Request) -> OwnerSessionAuthenticator:
    provider = getattr(request.app.state, "owner_session_authenticator", None)
    if provider is None:
        return DenyAllOwnerSession()
    return provider  # type: ignore[no-any-return]


def _engine(request: Request) -> Engine:
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        raise IdentityError(
            ErrorCode.STORAGE_WRITE_FAILED,
            details_safe={"storage_health": None, "failed_operation_id": None},
            message_safe="Kho dữ liệu chưa sẵn sàng.",
        )
    return engine  # type: ignore[no-any-return]


def _correlation_id(request: Request) -> str:
    """The request's correlation id: the caller's ``X-Request-Id`` when it sent one.

    It is always present in the envelope, even when nothing can be written to the database --
    it comes from process memory, not from a row (errors.yaml ``correlation_rule_vi``).
    """
    return request.headers.get(REQUEST_ID_HEADER) or new_ulid()


def _error_response(error: IdentityError, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(correlation_id),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _ok(payload: dict[str, Any]) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


@router.get("/v1/works/{work_id}", operation_id=OperationId.WORK_GET_DETAIL.value)
async def get_work_detail(work_id: str, request: Request) -> JSONResponse:
    """``work.get_detail`` -- read-only, owner session, no CSRF (openapi security).

    The body is a target object of ``contracts/schemas/target.schema.json``, which is what the
    200 response of this operation is pinned to. ports.yaml describes a richer read model
    (source posts, analysis history, related reported items); the two contracts disagree, and
    the handoff raises that as a change request instead of this file inventing a shape.
    """
    correlation_id = _correlation_id(request)
    try:
        owner_id = _authenticator(request).authenticate(
            session_cookie=request.cookies.get(SESSION_COOKIE),
            csrf_cookie=request.cookies.get(CSRF_COOKIE),
            csrf_header=request.headers.get(CSRF_HEADER),
            mutation=False,
        )
        detail = service.get_detail(
            _engine(request), owner_id=owner_id, work_id=work_id, caller_module="MOD-web-ui"
        )
    except IdentityError as error:
        return _error_response(error, correlation_id)
    return _ok(detail.target)


@router.post(
    "/v1/identity/conflicts/{conflict_id}/resolve",
    operation_id=OperationId.IDENTITY_RESOLVE_CONFLICT.value,
)
async def post_resolve_conflict(conflict_id: str, request: Request) -> JSONResponse:
    """``identity.resolve_conflict`` -- owner session **and** CSRF, in one requirement.

    The body is ``{"decision": "merge" | "keep_separate", "reason"?, "linking_evidence"?,
    "winner_work_id"?}``. ``merge`` without evidence is refused: an owner may decide *which*
    work survives, but not that two works are the same without a source saying so (B15).
    """
    correlation_id = _correlation_id(request)
    try:
        owner_id = _authenticator(request).authenticate(
            session_cookie=request.cookies.get(SESSION_COOKIE),
            csrf_cookie=request.cookies.get(CSRF_COOKIE),
            csrf_header=request.headers.get(CSRF_HEADER),
            mutation=True,
        )
        try:
            body = await request.json()
        except ValueError:
            body = None
        if not isinstance(body, dict):
            raise IdentityError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.IDENTITY_RESOLVE_CONFLICT.value,
                    "field_path": "$",
                    "violation_kind": "body_not_an_object",
                },
            )
        resolution = service.resolve_conflict(
            _engine(request),
            owner_id=owner_id,
            conflict_id=conflict_id,
            decision=str(body.get("decision", "")),
            resolution_note=body.get("reason"),
            linking_evidence=body.get("linking_evidence"),
            winner_work_id=body.get("winner_work_id"),
            caller_module="MOD-web-ui",
        )
    except IdentityError as error:
        return _error_response(error, correlation_id)

    merge = resolution.merge
    return _ok(
        {
            "conflict_id": resolution.conflict_id,
            "state": resolution.state,
            "merge_id": merge.merge_id if merge is not None else None,
            "winner_work_id": merge.winner_work_id if merge is not None else None,
            "loser_work_id": merge.loser_work_id if merge is not None else None,
            "moved_counts": merge.moved_counts if merge is not None else None,
            "preserved_counts": merge.preserved_counts if merge is not None else None,
        }
    )
