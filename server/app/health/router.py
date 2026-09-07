"""``health.get_liveness`` and ``health.get_readiness`` — the DB-independent channel.

The contract obligation, stated plainly
---------------------------------------
``contracts/state/storage.yaml`` ``independent_health_channel``:

``HC-01``
    ``health.get_liveness`` must answer **even when the database cannot be written and
    even when it cannot be read**. It returns ``up`` plus the schema version and reads no
    business table.
``HC-02``
    ``health.get_readiness`` reports each module's state **from process memory**: storage
    health, scheduler, dispatcher (is it locked for recovery?), embedding generation,
    source connectors, workers online/offline.
``HC-03``
    ``storage.get_health`` is an ``internal`` port that exists only inside the server
    process. The collector has no route to it -- and the refusal is ``CAPABILITY_DENIED``,
    not ``UNAUTHORIZED``, because a perfectly valid collector token still may not reach it.
``HC-04``
    These three channels are the mandatory fallback for ``EPR-01``: because they exist, no
    error code needs a new database row before it counts as reported.

So nothing in this module opens a connection, and the readiness provider is fed from the
in-memory :class:`~server.app.storage.health.StorageHealthMachine`. A readiness endpoint
that queried the database would return 500 in precisely the incident it exists to report.

Why the endpoints are built by a factory
----------------------------------------
``build_health_router`` takes its readiness provider and its authentication dependency as
arguments rather than importing them. Two reasons, both contractual:

* the owner-session dependency belongs to ``TC-owner-auth-session``
  (``server.app.auth.middleware``). Until that lands, the fallback here **denies** -- see
  :func:`_default_owner_session_dependency`. Defaulting to "allow" would publish per-module
  internals on an unauthenticated endpoint, and ``contracts/http/openapi.yaml`` gives
  ``/v1/health/readiness`` the ``ownerSessionCookie`` scheme while ``/healthz`` has
  ``security: []``;
* the readiness snapshot has to be injectable so a test can put the machine into a
  fixture's ``given.storage_health`` without a real incident.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, Protocol

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.storage.guard import StorageGuard, error_envelope

SCHEMA_VERSION_HEADER = "X-Schema-Version"

#: HTTP status for a refusal carrying ``UNAUTHORIZED`` (``contracts/http/openapi.yaml``
#: ``/v1/health/readiness`` responses).
UNAUTHORIZED_STATUS = 401


class ReadinessProvider(Protocol):
    """Structural match for ``server.app.main.ReadinessProvider`` (the Phase 0 seam).

    Declared structurally rather than imported so this module does not depend on the app
    factory that includes it.
    """

    def snapshot(self) -> dict[str, Any]:  # pragma: no cover - protocol declaration
        ...


class StorageReadinessProvider:
    """The real provider: projects the in-memory storage machine onto readiness rows.

    Only the rows this card owns are reported with a value. The other rows of
    ``contracts/ops/deployment.md`` §5 -- ``scheduler``, ``embedding``,
    ``research_sources``, ``telegram_link``, ``collector``, ``analysis_worker`` -- belong to
    other cards and are reported as ``None`` meaning *not computed*, never as ``ok``.

    That distinction is invariant ``I13`` applied to this endpoint: a row that says ``ok``
    because nobody has implemented it yet is the same defect as a screen that shows an empty
    list because the database could not be read.
    """

    #: Readiness rows this card computes. ``job_dispatch`` and ``delivery_dispatcher`` are
    #: included because ``contracts/ops/deployment.md`` §5 defines both purely in terms of
    #: storage health: ``job_dispatch`` is ``down`` when storage is not ``healthy``, and
    #: ``delivery_dispatcher`` is ``down`` when it is locked by ``recovery_required``.
    OWNED_ROWS: tuple[str, ...] = ("storage", "job_dispatch", "delivery_dispatcher")

    #: Rows owned by other cards. Present in the response so a consumer sees the full shape,
    #: with ``None`` for "no implementation has computed this yet".
    DEFERRED_ROWS: tuple[str, ...] = (
        "scheduler",
        "embedding",
        "research_sources",
        "telegram_link",
        "collector",
        "analysis_worker",
    )

    def __init__(self, guard: StorageGuard) -> None:
        self._guard = guard

    def snapshot(self) -> dict[str, Any]:
        """Build the readiness snapshot. Touches no database and cannot raise on I/O."""
        machine = self._guard.machine
        storage_row = machine.readiness_of_storage()
        dispatcher_locked = machine.dispatcher_is_locked()
        modules: dict[str, str | None] = {
            "storage": storage_row,
            # deployment.md §5: `job_dispatch` is `down` when storage is not healthy.
            "job_dispatch": "ok" if storage_row == "ok" else "down",
            # deployment.md §5: `delivery_dispatcher` is `down` when locked by recovery.
            "delivery_dispatcher": (
                "down" if dispatcher_locked else ("ok" if storage_row == "ok" else "down")
            ),
        }
        modules.update(dict.fromkeys(self.DEFERRED_ROWS, None))
        return {
            "modules": modules,
            "storage_health": machine.state.value,
            # `as_of` is UI-01: every screen showing business state must be able to say
            # when that state was last read, or it cannot distinguish "no data" from
            # "could not read" (I13).
            "as_of": _rfc3339(machine.observed_at),
            "dispatcher_locked_for_recovery": dispatcher_locked,
            "schema_version": CONTRACT_SCHEMA_VERSION,
        }


class OwnerSessionRequired(HTTPException):
    """401 for ``health.get_readiness``, carrying the contract error envelope.

    A subclass rather than a bare ``HTTPException`` so :func:`install_health_error_handler`
    can return the envelope itself; FastAPI's built-in handler would wrap it as
    ``{"detail": ...}``, which is not the shape ``contracts/errors.yaml`` defines.
    """

    def __init__(self) -> None:
        envelope = error_envelope(
            ErrorCode.UNAUTHORIZED,
            details_safe={
                "operation_id": OperationId.HEALTH_GET_READINESS.value,
                "required_auth_scope": "owner_session",
            },
        )
        super().__init__(status_code=UNAUTHORIZED_STATUS, detail=envelope)
        self.envelope = envelope


def install_health_error_handler(app: FastAPI) -> None:
    """Register the handler that renders :class:`OwnerSessionRequired` as the envelope."""

    @app.exception_handler(OwnerSessionRequired)
    async def _handle(_request: Request, exc: OwnerSessionRequired) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.envelope,
            headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
        )


def owner_session_absent() -> None:
    """Fallback owner-session dependency: refuse everything with ``UNAUTHORIZED``.

    Used until ``server.app.auth.middleware`` (``TC-owner-auth-session``) exists. Denying is
    the only defensible fallback: ``/v1/health/readiness`` carries the ``ownerSessionCookie``
    scheme in ``contracts/http/openapi.yaml`` and its body names per-module internals, so
    shipping it open until the auth card lands would publish those to anyone who can reach
    the port. Liveness is the endpoint that is public by design and stays available either
    way, so an operator is never left without a signal.
    """
    raise OwnerSessionRequired


def _default_owner_session_dependency() -> Callable[..., Any]:
    """The owner-session dependency of ``TC-owner-auth-session``, or :func:`owner_session_absent`.

    Resolved by import rather than declared as a hard dependency because
    ``server.app.auth.middleware`` is another card's write set and the two cards run in
    parallel.
    """
    try:
        from server.app.auth.middleware import require_owner_session
    except ImportError:
        return owner_session_absent
    resolved: Callable[..., Any] = require_owner_session
    return resolved


def install_storage(
    app: FastAPI,
    guard: StorageGuard | None = None,
    *,
    readiness_provider: ReadinessProvider | None = None,
    reconciliation_check: Callable[[str], bool] | None = None,
    include_liveness: bool = False,
) -> StorageGuard:
    """Wire storage health into ``app``. Called from ``create_app``'s include block.

    **The attribute other cards depend on is ``app.state.storage_guard``**, and after this
    function returns it is always present -- on the bare factory, in a test, and in a
    deployment. That guarantee is the point of the hook (finding ``F-A3R1-11``): the earlier
    version only built a guard when no readiness provider had been injected, so an app
    constructed with an explicit provider had no ``storage_guard`` at all and every
    ``assert_writable`` gate that looked for one silently did not run.

    ``TC-ingest-idempotent-ack-lost`` reads it as::

        IngestContext(engine=..., owner_id=..., storage_guard=app.state.storage_guard)

    and ``IngestContext.storage_guard`` must be that same object, not a fresh
    :class:`~server.app.storage.guard.StorageGuard`. Two guards would be two independent
    in-memory state machines, so a disk failure observed by one would leave the other
    reporting ``healthy`` -- which is the failure mode ``I02`` exists to prevent.

    :param guard: an existing guard to adopt. Omit it and one is constructed.
    :param readiness_provider: an override for the readiness snapshot source. Omit it and
        the guard's own :class:`StorageReadinessProvider` is installed, so the endpoint and
        the gate can never disagree about the state.
    :param reconciliation_check: the side-effect-free predicate of
        ``contracts/state/storage.yaml`` §7, owned by ``TC-backup-restore-drill``. Only used
        when this call constructs the guard; an adopted guard keeps the check it was built
        with. Absent, the gate stays shut: ``recovery_required`` never reopens by itself,
        which is ``I15`` and ``NC-10``.
    :param include_liveness: register ``GET /healthz`` here too. False on the shipped
        factory because ``server/app/main.py`` already registers that operation; a second
        registration of the same path would be unreachable and therefore untested.
    :returns: the guard now on ``app.state.storage_guard``.
    """
    resolved_guard = (
        guard if guard is not None else StorageGuard(reconciliation_check=reconciliation_check)
    )
    app.state.storage_guard = resolved_guard
    provider = (
        readiness_provider
        if readiness_provider is not None
        else StorageReadinessProvider(resolved_guard)
    )
    app.state.readiness_provider = provider
    install_health_error_handler(app)
    app.include_router(build_health_router(provider, include_liveness=include_liveness))
    return resolved_guard


def build_health_router(
    provider: ReadinessProvider,
    *,
    include_liveness: bool = True,
    owner_session_dependency: Callable[..., Any] | None = None,
) -> APIRouter:
    """Build the health router.

    :param provider: readiness snapshot source. Must not touch the database (HC-02).
    :param include_liveness: register ``GET /healthz``. The running application sets this
        ``False`` because ``server/app/main.py`` already registers the same operation from
        the Phase 0 skeleton; registering it twice would leave the second one unreachable
        and therefore untested. Tests set it ``True`` to exercise HC-01 through this
        module in isolation.
    :param owner_session_dependency: the ``owner_session`` check for readiness. Defaults to
        :func:`_default_owner_session_dependency`.
    """
    router = APIRouter(tags=["health"])
    auth_dependency = (
        owner_session_dependency
        if owner_session_dependency is not None
        else _default_owner_session_dependency()
    )

    if include_liveness:

        @router.get("/healthz", operation_id=OperationId.HEALTH_GET_LIVENESS.value)
        def get_liveness() -> JSONResponse:
            """``health.get_liveness`` (HC-01).

            ``security: []`` in the contract: unauthenticated by design, because a check
            that needs a session cannot report that sessions are unreachable.

            The response is only ``status`` and ``schema_version``. The negative half of
            that sentence is the contract: no configuration, provider names, chat ids or
            business data, so this endpoint reveals nothing an attacker could not learn by
            observing that the port is open.
            """
            return JSONResponse(
                content={"status": "up", "schema_version": CONTRACT_SCHEMA_VERSION},
                headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
            )

    @router.get(
        "/v1/health/readiness",
        operation_id=OperationId.HEALTH_GET_READINESS.value,
    )
    def get_readiness(_: Any = Depends(auth_dependency)) -> JSONResponse:  # noqa: B008
        """``health.get_readiness`` (HC-02).

        Reads the snapshot from process memory. There is no database call on this path and
        there must not be one: this endpoint's job is to stay answerable during the exact
        incident that makes the database unanswerable.
        """
        return JSONResponse(
            content=provider.snapshot(),
            headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
        )

    return router


def _rfc3339(moment: datetime) -> str:
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")
