"""HTTP surface of ``MOD-analysis-service``.

Six routes, exactly as ``contracts/http/openapi.yaml`` declares them -- none invented, none
renamed:

============================================================ ================================
``POST /v1/analysis/tasks/claim``                            ``analysis.claim_task``
``GET  /v1/analysis/tasks/{task_id}/input``                  ``analysis.get_task_input``
``POST /v1/analysis/tasks/{task_id}/heartbeat``              ``analysis.heartbeat``
``POST /v1/analysis/tasks/{task_id}/result``                 ``analysis.submit_result``
``POST /v1/analysis/tasks/{task_id}/attempt-unknown``        ``analysis.report_attempt_unknown``
``POST /v1/analysis/reanalysis``                             ``analysis.request_reanalysis``
============================================================ ================================

``analysis.enqueue_tasks`` is deliberately absent. Its transport in ``contracts/ports.yaml``
is ``internal``, so it is a function call from ``MOD-ingest-service`` or
``MOD-report-service`` into :func:`server.app.analysis.service.enqueue_tasks`, not an
endpoint. Publishing it would create an edge the registry does not grant -- and it is exactly
the edge FE-07 forbids the collector from using (B12: a worker never receives uncommitted
data).

Two credentials, and the boundary between them
----------------------------------------------
The five worker routes accept ``analysisWorkerToken`` and nothing else. The reanalysis route
accepts an owner session **and** a CSRF token in one security requirement, because
``contracts/http/openapi.yaml`` writes them as one requirement rather than two alternatives:
a session without the double-submit token is ``CSRF_REJECTED`` (403, session left intact),
not ``UNAUTHORIZED``.

Ruling R5-01 makes picking the wrong refusal a failure in its own right, so the three live in
three places and never blur:

``UNAUTHORIZED`` (401)  a principal class that this operation does not admit -- a collector
                        token on a worker route, an owner session on ``claim_task``.
``FORBIDDEN_EDGE``      an **in-process** call across an edge absent from ``allowed_edges``.
                        Raised by :func:`server.app.auth.middleware.require_edge` inside the
                        service, never by an HTTP handler.
``CSRF_REJECTED`` (403) the class is admitted; the intent is unproven.

The handlers do no business logic. Every decision -- lease, idempotency, validation gate,
transaction -- is in ``service.py``; this module translates HTTP to that and back.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.analysis.repository import new_ulid
from server.app.analysis.service import (
    AnalysisContext,
    AnalysisDependencyUnavailable,
    AnalysisError,
    TargetRequest,
    claim_task,
    enqueue_tasks,
    get_task_input,
    heartbeat,
    report_attempt_unknown,
    request_reanalysis,
    submit_result,
)
from server.app.auth.middleware import require_csrf, require_owner_session, require_worker_token

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

router = APIRouter(tags=["analysis"])


def _correlation_id() -> str:
    """A ULID minted in process memory.

    ``contracts/errors.yaml`` §EPR-01: ``correlation_id`` is always present, including while
    storage cannot be written. Deriving it from a database row would make the one field that
    must survive a storage outage depend on storage.
    """
    return new_ulid()


def _error_response(error: AnalysisError) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
        # openapi declares `Retry-After` in seconds on the 429/503 responses; the envelope
        # carries the millisecond value under `retry_after_ms`.
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


def _require_wire_headers(request: Request, operation: OperationId, *, mutation: bool) -> None:
    """Enforce the required header parameters of ``contracts/http/openapi.yaml``.

    ``X-Schema-Version`` and ``X-Request-Id`` on every route; ``Idempotency-Key``
    additionally on the mutations. A major-version mismatch is a ``VALIDATION_ERROR`` with
    ``violation_kind = schema_version_unsupported``, and ``latest`` is not a version.
    """
    required = [SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER]
    if mutation:
        required.append(IDEMPOTENCY_KEY_HEADER)
    for header in required:
        if not request.headers.get(header):
            raise AnalysisError(
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
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Phiên bản schema không được hỗ trợ.",
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


def _context(request: Request) -> AnalysisContext:
    """The service context for this request, with the app's storage guard attached.

    ``app.state.storage_guard`` is installed by ``install_storage`` (owned by
    ``TC-storage-write-blocked-readiness``) and read here rather than constructed: a second
    ``StorageGuard`` would be a second in-memory state machine, so a disk failure observed by
    one would leave the other still reporting ``healthy``. A context that already carries a
    guard keeps it -- an explicit injection, typically from a test, is never overridden.
    """
    context = getattr(request.app.state, "analysis_context", None)
    if not isinstance(context, AnalysisContext):
        raise AnalysisDependencyUnavailable(
            "app.state.analysis_context is not configured; the deployment entrypoint or the "
            "test wires it. The router refuses to invent a database connection."
        )
    if context.storage_guard is not None:
        return context
    guard = getattr(request.app.state, "storage_guard", None)
    if guard is None:
        return context
    return replace(context, storage_guard=guard)


async def _json_body(request: Request) -> dict[str, Any]:
    """Parse the request body, mapping malformed JSON onto ``VALIDATION_ERROR``.

    Parsed here rather than declared as a Pydantic parameter so that a violation produces the
    contract's envelope instead of FastAPI's own 422 shape, which carries no ``code``, no
    ``correlation_id`` and no ``retry_class``.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Body không phải JSON hợp lệ.",
            details_safe={"violation_kind": "malformed_json"},
        ) from exc
    if not isinstance(body, dict):
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Body phải là một object JSON.",
            details_safe={"violation_kind": "schema_invalid"},
        )
    return body


def _lease(body: dict[str, Any], operation: OperationId) -> tuple[str, int]:
    """Read ``lease_id`` / ``lease_epoch`` off a worker request body.

    Both are required on every worker mutation (``contracts/ports.yaml``): a request that
    carries no epoch cannot be checked for staleness, and admitting it would defeat I10.
    """
    lease_id = body.get("lease_id")
    lease_epoch = body.get("lease_epoch")
    if not isinstance(lease_id, str) or not isinstance(lease_epoch, int):
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu lease_id hoặc lease_epoch.",
            details_safe={
                "operation_id": operation.value,
                "field_path": "body.lease_id",
                "violation_kind": "required_field_missing",
            },
        )
    return lease_id, lease_epoch


@router.post(
    "/v1/analysis/tasks/claim",
    operation_id=OperationId.ANALYSIS_CLAIM_TASK.value,
    dependencies=[Depends(require_worker_token)],
)
async def post_claim_task(request: Request) -> Any:
    """``analysis.claim_task``. Answers ``{"task": null}`` when nothing is claimable.

    "No task" is a 200, not an error: an empty queue and a provider the Owner has not enabled
    are both ordinary conditions, and turning them into failures would make a worker retry a
    situation that no retry can change.
    """
    _require_wire_headers(request, OperationId.ANALYSIS_CLAIM_TASK, mutation=True)
    body = await _json_body(request)
    worker_identity = body.get("worker_instance_id")
    if not isinstance(worker_identity, str) or not worker_identity:
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu worker_instance_id.",
            details_safe={
                "operation_id": OperationId.ANALYSIS_CLAIM_TASK.value,
                "field_path": "body.worker_instance_id",
                "violation_kind": "required_field_missing",
            },
        )
    capabilities = body.get("task_types") or body.get("capabilities") or []
    return _ok(
        claim_task(
            _context(request),
            worker_identity=worker_identity,
            claim_request_id=request.headers[IDEMPOTENCY_KEY_HEADER],
            task_types=[str(value) for value in capabilities],
            run_id=body.get("run_id"),
        )
    )


@router.get(
    "/v1/analysis/tasks/{task_id}/input",
    operation_id=OperationId.ANALYSIS_GET_TASK_INPUT.value,
    dependencies=[Depends(require_worker_token)],
)
async def get_analysis_task_input(request: Request, task_id: str) -> Any:
    """``analysis.get_task_input``. The single data path to a worker (B12).

    The content it returns is **data with a boundary**, never instructions (I11). Nothing
    about that guarantee lives in this handler: it is the shape of the payload the service
    builds, plus the fact that an adapter has no tool to be instructed into using.
    """
    _require_wire_headers(request, OperationId.ANALYSIS_GET_TASK_INPUT, mutation=False)
    lease_id = request.query_params.get("lease_id")
    lease_epoch = request.query_params.get("lease_epoch")
    if not lease_id or lease_epoch is None or not lease_epoch.isdigit():
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu tham số bắt buộc lease_id/lease_epoch.",
            details_safe={
                "operation_id": OperationId.ANALYSIS_GET_TASK_INPUT.value,
                "field_path": "query.lease_id",
                "violation_kind": "required_parameter_missing",
            },
        )
    return _ok(
        get_task_input(
            _context(request),
            task_id=task_id,
            lease_id=lease_id,
            lease_epoch=int(lease_epoch),
        )
    )


@router.post(
    "/v1/analysis/tasks/{task_id}/heartbeat",
    operation_id=OperationId.ANALYSIS_HEARTBEAT.value,
    dependencies=[Depends(require_worker_token)],
)
async def post_heartbeat(request: Request, task_id: str) -> Any:
    """``analysis.heartbeat``. Extends a live lease; never writes a result."""
    _require_wire_headers(request, OperationId.ANALYSIS_HEARTBEAT, mutation=False)
    body = await _json_body(request)
    lease_id, lease_epoch = _lease(body, OperationId.ANALYSIS_HEARTBEAT)
    return _ok(
        heartbeat(_context(request), task_id=task_id, lease_id=lease_id, lease_epoch=lease_epoch)
    )


@router.post(
    "/v1/analysis/tasks/{task_id}/result",
    operation_id=OperationId.ANALYSIS_SUBMIT_RESULT.value,
    dependencies=[Depends(require_worker_token)],
)
async def post_submit_result(request: Request, task_id: str) -> Any:
    """``analysis.submit_result``. The 200 is sent only after ``TXN-analysis-accept`` committed."""
    _require_wire_headers(request, OperationId.ANALYSIS_SUBMIT_RESULT, mutation=True)
    body = await _json_body(request)
    lease_id, lease_epoch = _lease(body, OperationId.ANALYSIS_SUBMIT_RESULT)
    # The route's requestBody is `analysis-result.schema.json` itself; fixtures wrap it under
    # `analysis_result`, so both spellings are accepted and neither is guessed at.
    result = body.get("analysis_result", body.get("result_document"))
    if not isinstance(result, dict):
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu tài liệu kết quả theo analysis-result schema.",
            details_safe={
                "operation_id": OperationId.ANALYSIS_SUBMIT_RESULT.value,
                "field_path": "body.analysis_result",
                "violation_kind": "required_field_missing",
            },
        )
    return _ok(
        submit_result(
            _context(request),
            task_id=task_id,
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            result=result,
        )
    )


@router.post(
    "/v1/analysis/tasks/{task_id}/attempt-unknown",
    operation_id=OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN.value,
    dependencies=[Depends(require_worker_token)],
)
async def post_attempt_unknown(request: Request, task_id: str) -> Any:
    """``analysis.report_attempt_unknown``. Records what nobody knows; writes no result."""
    _require_wire_headers(request, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN, mutation=True)
    body = await _json_body(request)
    lease_id, lease_epoch = _lease(body, OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN)
    attempt_id = body.get("attempt_id")
    if not isinstance(attempt_id, str):
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu attempt_id.",
            details_safe={
                "operation_id": OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN.value,
                "field_path": "body.attempt_id",
                "violation_kind": "required_field_missing",
            },
        )
    return _ok(
        report_attempt_unknown(
            _context(request),
            task_id=task_id,
            attempt_id=attempt_id,
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            reason=str(body.get("reason") or "worker_lost_after_provider_call"),
        )
    )


@router.post(
    "/v1/analysis/reanalysis",
    operation_id=OperationId.ANALYSIS_REQUEST_REANALYSIS.value,
    dependencies=[Depends(require_owner_session), Depends(require_csrf)],
)
async def post_request_reanalysis(request: Request) -> Any:
    """``analysis.request_reanalysis`` -- 202, a new generation, the old result untouched.

    The dependency order is load-bearing: ``require_owner_session`` first, so a request with
    neither credential is ``UNAUTHORIZED`` rather than ``CSRF_REJECTED``.
    """
    _require_wire_headers(request, OperationId.ANALYSIS_REQUEST_REANALYSIS, mutation=True)
    body = await _json_body(request)
    target = body.get("target_ref") or body.get("target") or {}
    required = ("kind", "id")
    if not isinstance(target, dict) or any(key not in target for key in required):
        raise AnalysisError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu target_ref {kind, id}.",
            details_safe={
                "operation_id": OperationId.ANALYSIS_REQUEST_REANALYSIS.value,
                "field_path": "body.target_ref",
                "violation_kind": "required_field_missing",
            },
        )
    return _ok(
        request_reanalysis(
            _context(request),
            target_kind=str(target["kind"]),
            target_id=str(target["id"]),
            task_type=str(body.get("task_type", "summary")),
            source_fingerprint=str(body.get("source_fingerprint", "")),
            prompt_version=str(body.get("prompt_version", "1.0.0")),
            schema_version=str(body.get("schema_version", "0.1.0")),
            reason=str(body.get("reason", "")),
            request_id=request.headers[IDEMPOTENCY_KEY_HEADER],
        ),
        status_code=202,
    )


def analysis_error_handler(_request: Request, exc: Exception) -> Response:
    """App-level handler: an ``AnalysisError`` raised anywhere becomes the contract envelope."""
    assert isinstance(exc, AnalysisError)
    return _error_response(exc)


def analysis_dependency_handler(_request: Request, exc: Exception) -> Response:
    """A missing internal port is a server fault: ``INTERNAL`` (500), never a 4xx.

    The exception's message names the unwired port for the operator's logs; the envelope
    carries only the contract's safe message, because an envelope may not leak internal
    wiring.
    """
    assert isinstance(exc, AnalysisDependencyUnavailable)
    return _error_response(
        AnalysisError(ErrorCode.INTERNAL, "Lỗi nội bộ; yêu cầu chưa được xử lý.")
    )


def install_analysis_error_handlers(app: Any) -> None:
    """Register both handlers on a FastAPI app."""
    app.add_exception_handler(AnalysisError, analysis_error_handler)
    app.add_exception_handler(AnalysisDependencyUnavailable, analysis_dependency_handler)


__all__ = [
    "TargetRequest",
    "analysis_dependency_handler",
    "analysis_error_handler",
    "enqueue_tasks",
    "install_analysis_error_handlers",
    "router",
]
