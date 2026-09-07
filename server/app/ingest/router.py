"""HTTP surface of ``MOD-ingest-service``.

Three routes, exactly as ``contracts/http/openapi.yaml`` declares them -- no route is
invented here and none is renamed:

===================================================  ============================
``POST /v1/ingest/batches``                          ``ingest.submit_batch``
``POST /v1/ingest/checkpoints``                      ``ingest.commit_checkpoint``
``GET  /v1/ingest/receipts/{idempotency_key}``       ``ingest.get_receipt``
===================================================  ============================

``ingest.get_checkpoint`` is deliberately absent: its transport in ``contracts/ports.yaml``
is ``internal``, so it is a function call from ``MOD-job-service`` into
:func:`server.app.ingest.service.get_checkpoint`, not an endpoint. Exposing it over HTTP
would create an edge the module registry does not grant.

Authentication is the ``collectorToken`` bearer scheme and nothing else. A request with an
owner session cookie, an analysis worker token or no credential at all gets
``UNAUTHORIZED`` (401) -- the R5-01 boundary table: a principal class that is not permitted
for an operation is ``UNAUTHORIZED``, distinct from ``FORBIDDEN_EDGE`` (an in-process call
across an edge the registry does not contain) and from ``CAPABILITY_DENIED`` (a platform
capability the actor lacks). Picking the wrong one of the three is a failure in its own
right, so the mapping lives in one place and is asserted by the tests.

The handlers do no business logic. Every decision -- replay, conflict, guard, transaction --
is in ``service.py``; this module translates HTTP to that and back, and turns an
:class:`~server.app.ingest.service.IngestError` into the contract's ``ErrorEnvelope``.
"""

from __future__ import annotations

import hmac
from dataclasses import replace
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.ingest.repository import new_ulid
from server.app.ingest.service import (
    IngestContext,
    IngestDependencyUnavailable,
    IngestError,
    commit_checkpoint,
    get_receipt,
    submit_batch,
)

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

router = APIRouter(tags=["ingest"])


def _correlation_id() -> str:
    """A ULID minted in process memory.

    ``contracts/errors.yaml`` §EPR-01: ``correlation_id`` is always present, including
    while storage cannot be written. Deriving it from a database row would make the one
    field that must survive a storage outage depend on storage.
    """
    return new_ulid()


def _error_response(error: IngestError) -> JSONResponse:
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


def _ok(payload: dict[str, Any]) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=payload,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _require_collector_token(request: Request, operation: OperationId) -> None:
    """Authenticate the ``collectorToken`` bearer scheme.

    The expected token is read from ``app.state.collector_token`` and is never a literal in
    this repository (SRC-SPEC §11.2: the collector's token lives in a restricted-permission
    file on the personal machine). Comparison is constant-time.

    Absent configuration is ``UNAUTHORIZED``, not "allow": a deployment that forgot to
    configure the token must reject collectors, not accept everyone.
    """
    expected = getattr(request.app.state, "collector_token", None)
    presented = request.headers.get("Authorization", "")
    scheme, _, value = presented.partition(" ")
    if (
        not isinstance(expected, str)
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(value, expected)
    ):
        raise IngestError(
            ErrorCode.UNAUTHORIZED,
            "Yêu cầu thiếu hoặc sai xác thực cho operation này.",
            details_safe={
                "operation_id": operation.value,
                "required_auth_scope": "collector_token",
            },
        )


def _require_wire_headers(request: Request, operation: OperationId, *, mutation: bool) -> None:
    """Enforce the required header parameters of ``contracts/http/openapi.yaml``.

    ``X-Schema-Version`` and ``X-Request-Id`` are required on all three routes;
    ``Idempotency-Key`` additionally on the two mutations. A major-version mismatch is a
    ``VALIDATION_ERROR`` with ``violation_kind = schema_version_unsupported``, and
    ``latest`` is not a version.
    """
    required = [SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER]
    if mutation:
        required.append(IDEMPOTENCY_KEY_HEADER)
    for header in required:
        if not request.headers.get(header):
            raise IngestError(
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
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "Phiên bản schema không được hỗ trợ.",
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


def _context(request: Request) -> IngestContext:
    """The service context for this request, with the app's storage guard attached.

    ``app.state.storage_guard`` is installed by ``install_storage`` (owned by
    ``TC-storage-write-blocked-readiness``) and is read here rather than constructed: a
    second :class:`StorageGuard` would be a second in-memory state machine, so a disk
    failure observed by one would leave the other still reporting ``healthy``. Finding
    ``F-A3R1-11`` was that the gate was inert on the shipped factory because nothing carried
    that object into the ingest context; this is the wire.

    A context that already carries a guard keeps it -- an explicit injection, typically from
    a test, is never overridden by the app's.
    """
    context = getattr(request.app.state, "ingest_context", None)
    if not isinstance(context, IngestContext):
        raise IngestDependencyUnavailable(
            "app.state.ingest_context is not configured; the deployment entrypoint or the "
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

    The body is parsed here rather than declared as a Pydantic parameter so that a schema
    violation produces the contract's envelope instead of FastAPI's own 422 shape, which
    carries no ``code``, no ``correlation_id`` and no ``retry_class``.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "Body không phải JSON hợp lệ.",
            details_safe={"violation_kind": "malformed_json"},
        ) from exc
    if not isinstance(body, dict):
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "Body phải là một object JSON.",
            details_safe={"violation_kind": "schema_invalid"},
        )
    return body


@router.post("/v1/ingest/batches", operation_id=OperationId.INGEST_SUBMIT_BATCH.value)
async def post_ingest_batch(request: Request) -> Any:
    """``ingest.submit_batch``. The 200 is sent only after ``TXN-ingest-batch`` committed."""
    _require_collector_token(request, OperationId.INGEST_SUBMIT_BATCH)
    _require_wire_headers(request, OperationId.INGEST_SUBMIT_BATCH, mutation=True)
    body = await _json_body(request)
    header_key = request.headers[IDEMPOTENCY_KEY_HEADER]
    if body.get("idempotency_key") != header_key:
        # openapi carries the key in a header, the schema carries it in the body. They are
        # the same key; a request where they disagree has no single answer to "which key
        # did this batch commit under?", so it is rejected rather than resolved.
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "Idempotency-Key ở header và body không khớp.",
            details_safe={"violation_kind": "idempotency_key_mismatch"},
        )
    return _ok(submit_batch(_context(request), body))


@router.post("/v1/ingest/checkpoints", operation_id=OperationId.INGEST_COMMIT_CHECKPOINT.value)
async def post_ingest_checkpoint(request: Request) -> Any:
    """``ingest.commit_checkpoint``. Cursor-only advance; never carries items."""
    _require_collector_token(request, OperationId.INGEST_COMMIT_CHECKPOINT)
    _require_wire_headers(request, OperationId.INGEST_COMMIT_CHECKPOINT, mutation=True)
    body = await _json_body(request)
    # The route's requestBody is `ingest-receipt.schema.json#/$defs/checkpoint_only_request`
    # itself; fixtures wrap it under the union key, so both spellings are accepted.
    payload = body.get("checkpoint_only_request", body)
    if not isinstance(payload, dict):
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "checkpoint_only_request phải là một object JSON.",
            details_safe={"violation_kind": "schema_invalid"},
        )
    return _ok(commit_checkpoint(_context(request), payload))


@router.get(
    "/v1/ingest/receipts/{idempotency_key}",
    operation_id=OperationId.INGEST_GET_RECEIPT.value,
)
async def get_ingest_receipt(request: Request, idempotency_key: str) -> Any:
    """``ingest.get_receipt`` -- the mandatory lookup before retrying a lost ACK.

    ``assignment_id`` is a required query parameter in the contract; a missing one is a
    ``VALIDATION_ERROR`` rather than a silently broader lookup.
    """
    _require_collector_token(request, OperationId.INGEST_GET_RECEIPT)
    _require_wire_headers(request, OperationId.INGEST_GET_RECEIPT, mutation=False)
    if not request.query_params.get("assignment_id"):
        raise IngestError(
            ErrorCode.VALIDATION_ERROR,
            "Thiếu tham số bắt buộc assignment_id.",
            details_safe={
                "operation_id": OperationId.INGEST_GET_RECEIPT.value,
                "field_path": "query.assignment_id",
                "violation_kind": "required_parameter_missing",
            },
        )
    return _ok(get_receipt(_context(request), idempotency_key=idempotency_key))


def ingest_error_handler(_request: Request, exc: Exception) -> Response:
    """App-level handler: an ``IngestError`` raised anywhere becomes the contract envelope."""
    assert isinstance(exc, IngestError)
    return _error_response(exc)


def ingest_dependency_handler(_request: Request, exc: Exception) -> Response:
    """A missing internal port is a server fault: ``INTERNAL`` (500), never a 4xx.

    The exception's message names the unwired port for the operator's logs, but the
    envelope carries only the contract's safe message -- an envelope may not leak internal
    wiring.
    """
    assert isinstance(exc, IngestDependencyUnavailable)
    return _error_response(IngestError(ErrorCode.INTERNAL, "Lỗi nội bộ; yêu cầu chưa được xử lý."))


def install_ingest_error_handlers(app: Any) -> None:
    """Register both handlers on a FastAPI app."""
    app.add_exception_handler(IngestError, ingest_error_handler)
    app.add_exception_handler(IngestDependencyUnavailable, ingest_dependency_handler)


__all__ = [
    "ingest_dependency_handler",
    "ingest_error_handler",
    "install_ingest_error_handlers",
    "router",
]
