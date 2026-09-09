"""HTTP surface of ``MOD-secret-service``: exactly one route.

``POST /v1/secrets/task-credentials`` -> ``secret.issue_task_credential``, security
``analysisWorkerToken``, per ``contracts/http/openapi.yaml``.

The other two operations are **not** routed, and that is the contract, not an omission:
``secret.store_provider_key`` and ``secret.revoke_task_credential`` are ``transport:
internal`` in ``contracts/ports.yaml``. ``MOD-settings-service`` calls the first as a Python
function and ``MOD-analysis-service`` the second. Publishing either would create an edge the
registry does not grant and would put a key-writing endpoint on the internet.

Refusal codes, per ruling ``R5-01`` (picking the wrong one is itself a failure):

``UNAUTHORIZED`` (401)  a principal class this route does not admit -- an owner session or a
                        collector token on the worker route. Raised by
                        :func:`server.app.auth.middleware.require_worker_token`.
``STALE_LEASE`` (409)   the class is right and the lease is not the current one. This is
                        ISO-05's negative case and it comes from ``MOD-analysis-service``.
``NOT_FOUND`` (404)     no ``secret_ref`` for the task's provider, or no such assignment.
``VALIDATION_ERROR``    a malformed request, and the ``cli_acp`` case: that path receives no
                        server secret at all (``secrets.md`` §5.1).

Nothing in this module logs a request body. The body carries no secret on the way in, and the
response carries exactly one on the way out -- to the worker that holds the lease, and nowhere
else.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth.middleware import require_worker_token
from server.app.secret.repository import new_ulid
from server.app.secret.service import (
    SecretContext,
    SecretDependencyUnavailable,
    SecretError,
    issue_task_credential,
    record_denial,
)

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

router = APIRouter(tags=["secrets"])


def _correlation_id() -> str:
    return new_ulid()


def _error_response(error: SecretError) -> JSONResponse:
    return JSONResponse(
        status_code=error.http_status,
        content=error.envelope(_correlation_id()),
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _require_wire_headers(request: Request, operation: OperationId) -> None:
    for header in (SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER, IDEMPOTENCY_KEY_HEADER):
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


def _context(request: Request) -> SecretContext:
    context: SecretContext | None = getattr(request.app.state, "secret_context", None)
    if context is None:
        raise SecretDependencyUnavailable("app.state.secret_context is not configured")
    return context


def _string(body: dict[str, Any], field: str, operation: OperationId) -> str:
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SecretError(
            ErrorCode.VALIDATION_ERROR,
            "Trường bắt buộc thiếu hoặc sai kiểu.",
            details_safe={
                "operation_id": operation.value,
                "field_path": field,
                "violation_kind": "required_field_missing",
            },
        )
    return value


@router.post(
    "/v1/secrets/task-credentials",
    dependencies=[Depends(require_worker_token)],
)
async def post_task_credential(request: Request) -> JSONResponse:
    """``secret.issue_task_credential`` -- the only public door of this module.

    ``worker_instance_id`` comes from the body, exactly as ``analysis.claim_task`` takes it in
    ``server/app/analysis/router.py``: the bearer token authenticates the *class*
    (``analysisWorkerToken``), not an instance, so the same token is what every analysis worker
    presents. The instance name is therefore advisory, and the authority that actually gates
    this call is the pair ``lease_id`` + ``lease_epoch``, which a worker cannot guess and which
    ``MOD-analysis-service`` checks against the row it wrote at claim time. Recorded as
    ``CR-TC-SECRET-04``: a per-instance credential would make the identity check load-bearing
    rather than corroborating.
    """
    operation = OperationId.SECRET_ISSUE_TASK_CREDENTIAL
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
        context = _context(request)
        try:
            lease_epoch = int(body["lease_epoch"])
        except (KeyError, TypeError, ValueError) as exc:
            raise SecretError(
                ErrorCode.VALIDATION_ERROR,
                "lease_epoch phải là số nguyên.",
                details_safe={
                    "operation_id": operation.value,
                    "field_path": "lease_epoch",
                    "violation_kind": "type_mismatch",
                },
            ) from exc

        issued = issue_task_credential(
            context,
            task_id=_string(body, "task_id", operation),
            attempt_id=_string(body, "attempt_id", operation),
            lease_id=_string(body, "lease_id", operation),
            lease_epoch=lease_epoch,
            worker_identity=_string(body, "worker_instance_id", operation),
            assignment_id=_string(body, "assignment_id", operation),
        )
    except SecretError as error:
        _record_refusal(request, error, operation)
        return _error_response(error)
    except SecretDependencyUnavailable:
        return JSONResponse(
            status_code=500,
            content=SecretError(
                ErrorCode.INTERNAL,
                "Dịch vụ chưa được cấu hình đầy đủ.",
                details_safe={
                    "correlation_id": _correlation_id(),
                    "operation_id": operation.value,
                },
            ).envelope(_correlation_id()),
            headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
        )

    return JSONResponse(
        status_code=200,
        # `credential` is the one field in this repository that carries a secret value, and it
        # is written here, once, straight into the response body. It is not logged, not echoed
        # into `details_safe`, and not stored in plaintext anywhere.
        content={
            "credential_id": issued.credential_id,
            "credential": issued.value.reveal(),
            "provider_config_id": issued.provider_config_id,
            "provider_name": issued.provider_name,
            "model_name": issued.model_name,
            "task_id": issued.task_id,
            "attempt_id": issued.attempt_id,
            "expires_at": issued.expires_at,
        },
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
    )


def _record_refusal(request: Request, error: SecretError, operation: OperationId) -> None:
    """``secrets.md`` §8: every ``UNAUTHORIZED`` / ``STALE_LEASE`` refusal is auditable.

    Best-effort by design: if the database is the reason the request failed, an audit write
    would fail too, and losing the refusal record is better than turning a 409 into a 500.
    """
    context: SecretContext | None = getattr(request.app.state, "secret_context", None)
    if context is None:
        return
    try:
        record_denial(
            context,
            actor_module="MOD-analysis-worker",
            detail=f"{operation.value} refused with {error.code.value}",
        )
    except Exception:  # pragma: no cover - audit is best effort on the refusal path
        return


__all__ = ["router"]
