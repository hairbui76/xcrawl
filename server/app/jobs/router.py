"""HTTP for ``worker.*`` and ``run.*`` — the eleven routes ``contracts/http/openapi.yaml`` declares.

======================================================= ============================================
path                                                    operation
======================================================= ============================================
``POST /v1/workers/registrations``                      ``worker.register_capabilities``
``POST /v1/workers/assignments/claim``                  ``worker.claim_assignment``
``POST /v1/workers/assignments/{id}/heartbeat``         ``worker.heartbeat``
``POST /v1/workers/assignments/{id}/stop``              ``worker.report_stop``
``POST /v1/workers/assignments/{id}/release``           ``worker.release_assignment``
``GET  /v1/workers/status``                             ``worker.get_status``
``GET  /v1/runs``                                       ``run.list``
``GET  /v1/runs/{run_id}``                              ``run.get``
``POST /v1/runs/run-now``                               ``run.run_now``
``POST /v1/runs/{run_id}/resume``                       ``run.resume``
``POST /v1/runs/{run_id}/cancel``                       ``run.cancel``
======================================================= ============================================

Paths are the contract's, not this file's invention, and they are already the paths
``collector/app/client.py`` posts to. That collector was written against a server that did not
exist yet; landing this router is what turns its ``worker.*`` calls from a stub into a real
round trip. **No collector file is edited by this card** — the integration is that the two
halves already agree, and ``tests/integration/test_lease_two_claimants.py`` exercises the
server half through the same paths.

``scheduler.evaluate_due``, ``job.enqueue_scheduled_run`` and ``job.coalesce_overdue`` are
**not** routed. All three are ``transport: internal`` in ``contracts/ports.yaml``, so the
scheduler loop calls the service functions in process; publishing them would create an edge
the registry does not have.

The auth matrix, from the contract
-----------------------------------
Each route's dependency list is the ``security`` block of its path item, and the three shapes
are genuinely different:

* ``collector_token`` alone for claim/heartbeat/stop/release — an analysis worker's token is
  a *valid* token on the *wrong* edge and gets ``UNAUTHORIZED`` (ruling R5-01 row 1).
* ``collector_token_or_analysis_worker_token`` for registration — the one route both worker
  kinds use, handled by :func:`require_any_worker_token` because the shared middleware has a
  dependency per single scheme and this is the only place the disjunction is needed.
* ``owner_session`` **and** ``ownerCsrfToken`` in one requirement for every ``run.*``
  mutation; ``run.list`` and ``run.run_now`` additionally accept the Telegram ingress secret
  (``owner_session_or_linked_chat``).

``run.resume`` and ``run.cancel`` are owner-session-only: ``B10``/``AMD-B10`` says there is no
Telegram command for either, and that is enforced here by not accepting the ingress secret
rather than by hoping the adapter never sends one.
"""

from __future__ import annotations

import hmac
import os
import time as _time
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth.middleware import (
    AuthScope,
    PrincipalKind,
    require_collector_token,
    require_csrf,
    require_owner_session,
)
from server.app.jobs import service
from server.app.jobs.lease import JobError
from server.app.jobs.service import JobContext, StopEcho

router = APIRouter(tags=["jobs"])

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _correlation_id() -> str:
    """A ULID generated in process memory.

    ``contracts/errors.yaml`` §EPR-01 requires a ``correlation_id`` on **every** envelope,
    including the ones produced while storage is blocked, so this must not read a sequence
    from the database — it would be unavailable exactly when it is needed.
    """
    value = (int(_time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def _error_response(error: JobError) -> JSONResponse:
    """The envelope — or, for a :class:`StopEcho`, the envelope **plus** its siblings.

    ``collection/a-feed-layout-changed.json`` answers a *successful* ``worker.report_stop``
    with 409 and ``{error, run, alert_intent_created, alert_intent_id}``. The extra keys are
    siblings of ``error`` rather than entries in ``details_safe``, because
    ``contracts/errors.yaml`` closes that key set and ``JobError`` drops anything outside it.
    Every other refusal is the bare envelope, unchanged.
    """
    correlation_id = _correlation_id()
    content = (
        error.envelope_body(correlation_id)
        if isinstance(error, StopEcho)
        else error.envelope(correlation_id)
    )
    return JSONResponse(
        status_code=error.http_status,
        content=content,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _ok(payload: dict[str, Any], *, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _context(request: Request) -> JobContext:
    """``app.state.job_context``, or ``INTERNAL``.

    Not defaulted. A deployment that wired no context gets a 500 with a correlation id rather
    than a router that opens its own database connection and invents an owner id — the same
    rule the analysis and delivery routers follow.
    """
    context = getattr(request.app.state, "job_context", None)
    if not isinstance(context, JobContext):
        raise JobError(
            ErrorCode.INTERNAL,
            details_safe={"operation_id": "job_context", "correlation_id": "unset"},
        )
    return context


def require_any_worker_token(request: Request) -> PrincipalKind:
    """``collector_token_or_analysis_worker_token`` — the only route both kinds may call.

    Written here rather than in the shared middleware because it is the single disjunctive
    scheme in the contract, and a general "any bearer" dependency in the middleware would be
    reachable from routes whose contract allows exactly one kind.

    A bearer that is neither is ``UNAUTHORIZED`` (R5-01 row 1): the caller presented a
    credential of the wrong *class* for this operation, which is the HTTP question, not the
    in-process edge question that ``FORBIDDEN_EDGE`` answers.
    """
    from server.app.auth.middleware import _bearer, _token_registry  # noqa: PLC0415

    token = _bearer(request)
    registry = _token_registry(request)
    kind = registry.kind_for(token) if token else None
    if kind not in (PrincipalKind.COLLECTOR, PrincipalKind.ANALYSIS_WORKER):
        raise JobError(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": OperationId.WORKER_REGISTER_CAPABILITIES.value,
                "required_auth_scope": AuthScope.COLLECTOR_TOKEN_OR_ANALYSIS_WORKER_TOKEN.value,
            },
        )
    return kind


def _require_wire_headers(request: Request, operation: OperationId) -> None:
    """``X-Schema-Version`` and ``X-Request-Id`` on every call (SRC-PLAN §5.1).

    A missing or mismatched schema version is a ``VALIDATION_ERROR`` rather than a silent
    accept: two sides disagreeing about the wire shape is the failure that produces
    plausible-looking wrong data.
    """
    version = request.headers.get(SCHEMA_VERSION_HEADER)
    if version is None or version != CONTRACT_SCHEMA_VERSION:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": operation.value,
                "field_path": SCHEMA_VERSION_HEADER,
                "violation_kind": "missing_or_mismatched",
                "limit_name": "contract_schema_version",
                "limit_value": CONTRACT_SCHEMA_VERSION,
            },
        )
    if not request.headers.get(REQUEST_ID_HEADER):
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": operation.value,
                "field_path": REQUEST_ID_HEADER,
                "violation_kind": "missing_or_empty",
            },
        )


async def _body(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except ValueError as exc:
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": "body", "violation_kind": "not_json"},
        ) from exc
    if not isinstance(payload, dict):
        raise JobError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": "body", "violation_kind": "not_an_object"},
        )
    return payload


# --------------------------------------------------------------------------------------
# worker.*
# --------------------------------------------------------------------------------------


@router.post(
    "/v1/workers/registrations",
    operation_id=OperationId.WORKER_REGISTER_CAPABILITIES.value,
    dependencies=[Depends(require_any_worker_token)],
)
async def post_registration(request: Request) -> Response:
    """``worker.register_capabilities`` — grants no lease (LM-01)."""
    try:
        _require_wire_headers(request, OperationId.WORKER_REGISTER_CAPABILITIES)
        return _ok(service.register_capabilities(_context(request), await _body(request)))
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/workers/assignments/claim",
    operation_id=OperationId.WORKER_CLAIM_ASSIGNMENT.value,
    dependencies=[Depends(require_collector_token)],
)
async def post_claim(request: Request) -> Response:
    """``worker.claim_assignment`` — an ``assignment`` or a ``no_work``, both 200.

    ``no_work`` is not an error status, and that is the contract's choice rather than a
    convenience: fixture ``collection/g-schedule-due-claim.json`` event 3 pins
    ``response_status: 200`` for a worker that already holds the assignment.
    """
    try:
        _require_wire_headers(request, OperationId.WORKER_CLAIM_ASSIGNMENT)
        return _ok(service.claim_assignment(_context(request), await _body(request)))
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/workers/assignments/{assignment_id}/heartbeat",
    operation_id=OperationId.WORKER_HEARTBEAT.value,
    dependencies=[Depends(require_collector_token)],
)
async def post_heartbeat(request: Request, assignment_id: str) -> Response:
    """``worker.heartbeat`` — a stale epoch changes nothing and answers ``STALE_LEASE``."""
    try:
        _require_wire_headers(request, OperationId.WORKER_HEARTBEAT)
        body = await _body(request)
        body.setdefault("assignment_id", assignment_id)
        return _ok(service.heartbeat(_context(request), body))
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/workers/assignments/{assignment_id}/stop",
    operation_id=OperationId.WORKER_REPORT_STOP.value,
    dependencies=[Depends(require_collector_token)],
)
async def post_stop(request: Request, assignment_id: str) -> Response:
    """``worker.report_stop`` — report and halt; never a retry, never an account rotation.

    Two success shapes, both pinned by fixtures: 200 with
    ``{run, alert_intent_created[, alert_intent_id]}``, or — for ``source_layout_changed`` —
    409 with that object beside a ``SOURCE_LAYOUT_CHANGED`` envelope. The 409 is an
    *acknowledgement*: the run moved and the alert was created, and the transaction committed
    before :class:`~server.app.jobs.service.StopEcho` was raised. The collector knows not to
    retry it (``client._STOP_ECHO_CODES``).
    """
    try:
        _require_wire_headers(request, OperationId.WORKER_REPORT_STOP)
        body = await _body(request)
        body.setdefault("assignment_id", assignment_id)
        return _ok(service.report_stop(_context(request), body))
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/workers/assignments/{assignment_id}/release",
    operation_id=OperationId.WORKER_RELEASE_ASSIGNMENT.value,
    dependencies=[Depends(require_collector_token)],
)
async def post_release(request: Request, assignment_id: str) -> Response:
    """``worker.release_assignment`` — revoke the lease and bump the epoch (LM-06)."""
    try:
        _require_wire_headers(request, OperationId.WORKER_RELEASE_ASSIGNMENT)
        body = await _body(request)
        body.setdefault("assignment_id", assignment_id)
        return _ok(service.release_assignment(_context(request), body))
    except JobError as error:
        return _error_response(error)


@router.get(
    "/v1/workers/status",
    operation_id=OperationId.WORKER_GET_STATUS.value,
    dependencies=[Depends(require_owner_session)],
)
async def get_worker_status(request: Request) -> Response:
    """``worker.get_status`` — ``online`` / ``offline`` / ``unknown``, three distinct answers."""
    try:
        return _ok(service.get_worker_status(_context(request)))
    except JobError as error:
        return _error_response(error)


# --------------------------------------------------------------------------------------
# run.*
# --------------------------------------------------------------------------------------


def require_owner_or_linked_chat(request: Request) -> None:
    """``owner_session_or_linked_chat`` for ``run.list`` and ``run.run_now``.

    Two alternative requirements, and the Telegram branch is satisfied by the ingress secret
    the adapter presents. Compared in constant time via the auth service's own helper where
    one is configured; where none is, the branch simply does not admit anybody, because
    "linking has not been configured" is not a reason to trust a caller.
    """
    try:
        require_owner_session(request)
        return
    except Exception:  # noqa: BLE001 - the owner branch failing is not the answer yet
        pass
    secret = getattr(request.app.state, "telegram_ingress_secret", None)
    presented = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    # Constant time, and only on two real strings: `compare_digest` on a `None` would be a
    # TypeError, and an unconfigured secret must refuse rather than crash.
    if not (
        isinstance(secret, str)
        and isinstance(presented, str)
        and hmac.compare_digest(secret, presented)
    ):
        raise JobError(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": OperationId.RUN_LIST.value,
                "required_auth_scope": AuthScope.OWNER_SESSION_OR_LINKED_CHAT.value,
            },
        ) from None


@router.get("/v1/runs", operation_id=OperationId.RUN_LIST.value)
async def get_runs(request: Request) -> Response:
    """``run.list`` — read-only, for the app **and** the Telegram ``status`` command (B10)."""
    try:
        require_owner_or_linked_chat(request)
        limit = int(request.query_params.get("limit", "50"))
        return _ok(service.list_runs(_context(request), limit=limit))
    except JobError as error:
        return _error_response(error)
    except ValueError:
        return _error_response(
            JobError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.RUN_LIST.value,
                    "field_path": "limit",
                    "violation_kind": "not_an_integer",
                },
            )
        )


@router.get(
    "/v1/runs/{run_id}",
    operation_id=OperationId.RUN_GET.value,
    dependencies=[Depends(require_owner_session)],
)
async def get_run_detail(request: Request, run_id: str) -> Response:
    """``run.get`` — owner session only; no Telegram equivalent."""
    try:
        return _ok(service.get_run(_context(request), run_id=run_id))
    except JobError as error:
        return _error_response(error)


@router.post("/v1/runs/run-now", operation_id=OperationId.RUN_RUN_NOW.value)
async def post_run_now(request: Request) -> Response:
    """``run.run_now`` — coalesces onto an active run; never resumes ``needs_user`` (B10).

    The owner branch requires CSRF; the Telegram branch does not, because a webhook carries no
    cookie and the double-submit defence is meaningless there. Both are in the contract's own
    ``security`` list as two alternative requirements.
    """
    try:
        _require_wire_headers(request, OperationId.RUN_RUN_NOW)
        try:
            require_owner_session(request)
            require_csrf(request)
        except JobError:
            raise
        except Exception:  # noqa: BLE001 - fall through to the Telegram alternative
            require_owner_or_linked_chat(request)
        body = await _body(request)
        request_id = str(body.get("request_id", ""))
        return _ok(service.run_now(_context(request), request_id=request_id))
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/runs/{run_id}/resume",
    operation_id=OperationId.RUN_RESUME.value,
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
async def post_resume(request: Request, run_id: str) -> Response:
    """``run.resume`` — T-RUN-10 and T-RUN-23. Owner session only: there is no Telegram resume.

    The dependency order is load-bearing: ``require_owner_session`` first, so an
    unauthenticated request answers ``UNAUTHORIZED`` rather than ``CSRF_REJECTED`` and the
    two refusals stay distinguishable (R5-01 rows 1 and 4).
    """
    try:
        _require_wire_headers(request, OperationId.RUN_RESUME)
        body = await _body(request)
        return _ok(
            service.resume_run(
                _context(request),
                run_id=run_id,
                unblock_reason=body.get("unblock_reason"),
            )
        )
    except JobError as error:
        return _error_response(error)


@router.post(
    "/v1/runs/{run_id}/cancel",
    operation_id=OperationId.RUN_CANCEL.value,
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
async def post_cancel(request: Request, run_id: str) -> Response:
    """``run.cancel`` — the exit from every non-terminal status (T-RUN-17a/b/c)."""
    try:
        _require_wire_headers(request, OperationId.RUN_CANCEL)
        return _ok(service.cancel_run(_context(request), run_id=run_id))
    except JobError as error:
        return _error_response(error)


def job_error_handler(_request: Request, exc: Exception) -> Response:
    """Catch a :class:`JobError` raised inside a dependency, where the route cannot."""
    if isinstance(exc, JobError):
        return _error_response(exc)
    raise exc


def install_job_error_handlers(app: Any) -> None:
    """Register the handler so a dependency-raised ``JobError`` still gets an envelope."""
    app.add_exception_handler(JobError, job_error_handler)


__all__ = [
    "install_job_error_handlers",
    "require_any_worker_token",
    "require_owner_or_linked_chat",
    "router",
]
