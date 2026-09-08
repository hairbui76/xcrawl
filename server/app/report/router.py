"""HTTP surface of ``MOD-report-service``: the two read operations, and nothing else.

Routes, methods, status codes and security are read straight out of
``contracts/http/openapi.yaml``; none is invented and none is renamed:

=================================  =================  ======================
path                               operation          auth
=================================  =================  ======================
``GET /v1/reports``                ``report.list``    ``ownerSessionCookie``
``GET /v1/reports/{report_id}``    ``report.get``     ``ownerSessionCookie``
=================================  =================  ======================

``report.build`` and ``report.publish`` are **deliberately not routed**. Both are
``transport: internal`` in ``contracts/ports.yaml``: the job service calls ``report.build``
in process and the report service calls its own ``report.publish``. Publishing them over HTTP
would open the edge ``FE-13`` exists to forbid -- an analysis worker deciding that a work has
been reported.

Reads, so no CSRF
-----------------
``contracts/http/openapi.yaml`` puts ``ownerSessionCookie`` alone in the security requirement
for both operations; ``ownerCsrfToken`` appears only on mutations. CSRF protects state changes,
and adding it to a read would be a different contract from the one the web client was
generated against. Any other principal -- collector token, analysis-worker token, nothing at
all -- is ``UNAUTHORIZED`` (401) and not ``FORBIDDEN_EDGE``: ruling R5-01 row 1 is about *who
you are at the HTTP boundary*, row 2 is about *whether an in-process edge exists*, and picking
the wrong one is a FAIL by card §10 ``SG-DENY``.

The read model is rebuilt from rows, never re-derived from live state
----------------------------------------------------------------------
``report.get`` answers with :func:`server.app.report.publisher.read_model`, which reads only
rows written inside the publish transaction. That is what makes ``content_hash`` still verify
after a tag edit, after an identity merge and after a restore -- the three cases fixtures ``c``,
``i`` and the recovery set pin. A handler that re-ran selection would answer with today's tags
and quietly break I05.

``CR-TC-REPORT-07``: ``report.list``'s declared 200 schema
-----------------------------------------------------------
openapi gives ``report.list`` the response schema ``../schemas/report.schema.json`` -- the
read model of **one** published report -- while its own description asks for one row per
period ("Ngày, coverage ``[from, to)``, số mục, số hướng nổi, quality"). A list cannot be a
single report object. This module follows the description, answers
``{"reports": [...], "next_cursor": ...}``, and reports the mismatch rather than inventing a
shape that satisfies neither.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import ReportStatus
from sqlalchemy import text

from server.app.db.engine import session_scope
from server.app.report.coverage import CoverageRepository, ReportError, new_ulid
from server.app.report.publisher import PublishContext, read_model

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"

router = APIRouter(tags=["reports"])


# --------------------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------------------


def _correlation_id() -> str:
    """A ULID minted in process memory.

    ``contracts/errors.yaml`` §EPR-01: ``correlation_id`` is on every envelope, including
    while storage cannot be written -- so it must not come from a database row.
    """
    return new_ulid()


def _error_response(error: ReportError) -> JSONResponse:
    headers = {SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION}
    if error.retry_after_ms is not None:
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


def _require_wire_headers(request: Request, operation: OperationId) -> None:
    """``X-Schema-Version`` and ``X-Request-Id``, both ``required: true`` in the contract.

    A major-version mismatch is ``VALIDATION_ERROR`` with ``violation_kind =
    schema_version_unsupported``, which is the exact wording the parameter's own description
    pins.
    """
    for header in (SCHEMA_VERSION_HEADER, REQUEST_ID_HEADER):
        if not request.headers.get(header):
            raise ReportError(
                ErrorCode.VALIDATION_ERROR,
                message_safe="Thiếu header bắt buộc theo hợp đồng wire.",
                details_safe={
                    "operation_id": operation.value,
                    "field_path": f"header.{header}",
                    "violation_kind": "required_header_missing",
                },
            )
    sent = str(request.headers[SCHEMA_VERSION_HEADER])
    if sent.split(".")[0] != CONTRACT_SCHEMA_VERSION.split(".")[0]:
        raise ReportError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": operation.value,
                "field_path": f"header.{SCHEMA_VERSION_HEADER}",
                "violation_kind": "schema_version_unsupported",
            },
        )


def _owner_session(request: Request, operation: OperationId) -> str:
    """``ownerSessionCookie``. Anything else is 401, with no hint about what was wrong."""
    from server.app.auth.middleware import require_owner_session

    try:
        principal = require_owner_session(request)
    except Exception as exc:  # noqa: BLE001 - AuthError and its subclasses live in auth
        code = getattr(exc, "code", None)
        if code is None:
            raise
        raise ReportError(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": operation.value,
                "required_auth_scope": "owner_session",
            },
        ) from exc
    session = getattr(principal, "session", None)
    owner_id = getattr(session, "owner_id", None)
    if not owner_id:
        raise ReportError(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": operation.value,
                "required_auth_scope": "owner_session",
            },
        )
    return str(owner_id)


def _context(request: Request) -> PublishContext:
    """``app.state.report_context``. Never defaulted: a router does not invent a database.

    An unconfigured deployment gets ``INTERNAL`` (500), which is honest, rather than a
    connection to some file this module chose or a tag port this module wrote itself.
    """
    context = getattr(request.app.state, "report_context", None)
    if not isinstance(context, PublishContext):
        raise ReportError(
            ErrorCode.INTERNAL,
            details_safe={"operation_id": OperationId.REPORT_GET.value},
        )
    return context


def install_reports(app: Any, context: PublishContext | None = None) -> None:
    """Mount the two read routes; optionally install the context in one call."""
    if context is not None:
        app.state.report_context = context
    app.include_router(router)


# --------------------------------------------------------------------------------------
# report.list
# --------------------------------------------------------------------------------------


@router.get("/v1/reports", operation_id=OperationId.REPORT_LIST.value)
def list_reports(
    request: Request,
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> Any:
    """``report.list`` -- one row per **published** period, newest first.

    ``building`` and ``aborted`` rows are not listed: ``report.schema.json`` makes ``status``
    a ``const "published"``, so there is no read model for the other two. An empty period is
    therefore invisible here **by design** and is visible in the coverage ledger instead -- the
    UI reads "không có nội dung phù hợp" from the ledger, never from a missing report (I13).

    The cursor is the ``published_at`` of the last row of the previous page; ``published_at``
    is unique per owner in practice and the tie-break on ``id`` makes the page boundary total.
    """
    try:
        _require_wire_headers(request, OperationId.REPORT_LIST)
        owner_id = _owner_session(request, OperationId.REPORT_LIST)
        context = _context(request)
    except ReportError as error:
        return _error_response(error)

    with session_scope(context.engine) as connection:
        rows = (
            connection.execute(
                text(
                    "SELECT r.id, r.published_at, r.quality, r.coverage_from, r.coverage_to,"
                    "       r.content_hash,"
                    "       (SELECT COUNT(*) FROM report_item i WHERE i.report_id = r.id)"
                    "         AS item_count,"
                    "       (SELECT COUNT(*) FROM emerging_direction d"
                    "         WHERE d.report_id = r.id AND d.evidence_state = 'sufficient')"
                    "         AS direction_count"
                    "  FROM report r"
                    " WHERE r.owner_id = :owner AND r.status = :published"
                    "   AND (:cursor IS NULL OR r.published_at < :cursor)"
                    " ORDER BY r.published_at DESC, r.id DESC LIMIT :limit"
                ),
                {
                    "owner": owner_id,
                    "published": ReportStatus.PUBLISHED.value,
                    "cursor": cursor,
                    "limit": limit,
                },
            )
            .mappings()
            .all()
        )
        coverage = CoverageRepository()
        reports = []
        for row in rows:
            window = coverage.window_for_report(connection, owner_id, str(row["id"]))
            reports.append(
                {
                    "report_id": str(row["id"]),
                    "published_at": str(row["published_at"]),
                    "quality": str(row["quality"]),
                    "coverage": {
                        "coverage_window_id": "" if window is None else window.id,
                        "sequence": 0 if window is None else window.sequence,
                        "coverage_from": str(row["coverage_from"]),
                        "coverage_to": str(row["coverage_to"]),
                    },
                    "item_count": int(row["item_count"]),
                    "emerging_direction_count": int(row["direction_count"]),
                    "content_hash": str(row["content_hash"]),
                }
            )
    return _ok(
        {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "reports": reports,
            "next_cursor": reports[-1]["published_at"] if len(reports) == limit else None,
        }
    )


# --------------------------------------------------------------------------------------
# report.get
# --------------------------------------------------------------------------------------


@router.get("/v1/reports/{report_id}", operation_id=OperationId.REPORT_GET.value)
def get_report(request: Request, report_id: str) -> Any:
    """``report.get`` -- the full read model of one published period.

    ``NOT_FOUND`` covers three cases and says the same thing about all of them: no such id,
    an id belonging to another owner, and a ``building``/``aborted`` build. The third is not a
    special case to explain -- those states have no read model at all (SRC-PLAN §8.2) -- and
    distinguishing them in the response would confirm the existence of rows the caller is not
    entitled to know about.
    """
    try:
        _require_wire_headers(request, OperationId.REPORT_GET)
        owner_id = _owner_session(request, OperationId.REPORT_GET)
        context = _context(request)
    except ReportError as error:
        return _error_response(error)

    with session_scope(context.engine) as connection:
        body = read_model(connection, context, owner_id=owner_id, report_id=report_id)
    if body is None:
        return _error_response(
            ReportError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.REPORT_GET.value,
                    "resource_kind": "report",
                },
            )
        )
    return _ok(body)


__all__ = ["install_reports", "router"]
