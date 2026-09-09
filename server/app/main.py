"""FastAPI application factory.

Scope of this file in Phase 0 (repo skeleton). It wires:

* the app object and its OpenAPI identity, taken from ``contracts/http/openapi.yaml``;
* a placeholder ``GET /healthz`` implementing operation ``health.get_liveness``;
* a readiness *provider seam* (:class:`ReadinessProvider`) that returns a stub.

What this file deliberately does NOT do
---------------------------------------
``server/app/health/router.py`` and the real readiness computation are the write set of
``agent-tasks/TC-storage-write-blocked-readiness.md``. Operation ``health.get_readiness``
(``GET /v1/health/readiness``) is therefore NOT routed here; the seam below exists so that
card can plug the real provider in without restructuring the app factory.

Contract references
-------------------
* ``contracts/http/openapi.yaml`` paths ``/healthz`` and ``/v1/health/readiness``.
* ``contracts/state/storage.yaml`` ``independent_health_channel`` rules HC-01..HC-04:
  liveness must answer even when the database cannot be written or read, and it returns
  only ``up`` plus a schema version -- no configuration, provider names, chat ids or
  business data.
* ``contracts/ports.yaml`` operation ids ``health.get_liveness``, ``health.get_readiness``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, Protocol

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# CONTRACT_SCHEMA_VERSION is generated from ``info.version`` of contracts/http/openapi.yaml;
# it is the wire version the server speaks (SRC-PLAN §5.1 schema_version discipline).
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.operations import OperationId

SCHEMA_VERSION_HEADER = "X-Schema-Version"


class ReadinessProvider(Protocol):
    """Seam for the per-module readiness snapshot read from PROCESS MEMORY (rule HC-02).

    The real implementation belongs to ``TC-storage-write-blocked-readiness``. It must not
    reach the database: the whole point of the channel is that it still answers when the
    database does not.
    """

    def snapshot(self) -> dict[str, Any]:  # pragma: no cover - protocol declaration
        ...


class StubReadinessProvider:
    """Phase 0 stub. Reports ``unknown`` rather than inventing a healthy answer.

    ``contracts/state/storage.yaml`` closes ``storage_health`` over four values and there is
    deliberately no ``unknown`` member, so this stub does NOT pick one: it reports ``None``,
    meaning "not computed". ``contracts/capabilities.yaml`` principle CAP-P5 and invariant
    I13 forbid converting an undetermined state into a good one, and returning
    ``healthy`` here would do exactly that.
    """

    def snapshot(self) -> dict[str, Any]:
        return {
            "storage": None,
            "detail": "phase-0 skeleton: no readiness computation exists yet",
        }


def create_app(
    readiness_provider: ReadinessProvider | None = None,
    *,
    lifespan: Callable[[FastAPI], Any] | None = None,
) -> FastAPI:
    """Build the ASGI application.

    :param readiness_provider: injected by ``TC-storage-write-blocked-readiness`` later;
        Phase 0 falls back to :class:`StubReadinessProvider`.
    :param lifespan: optional ASGI lifespan. **Defaulted to ``None`` on purpose**: with no
        argument this factory still returns the same bare, unconfigured application it
        always has -- no database, no services, every card's test unaffected. The parameter
        exists so the module-level ``app`` below can wire itself when a real server starts
        it, without the mere *import* of this module touching a filesystem.
    """
    app = FastAPI(
        title="Research Radar — Owner API",
        version=CONTRACT_SCHEMA_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.readiness_provider = readiness_provider or StubReadinessProvider()

    # >>> TC-owner-auth-session (MOD-auth-service) >>>
    # One delimited include, import inside the delimiters (F-A3R1-13).
    #
    # No AuthService is constructed here: the bare factory has no database URL (Phase 0
    # deliberately gave Alembic none), so building one would invent a storage location.
    # A deployment or a test calls `install_auth(app, service)` -- or assigns
    # `app.state.auth_service` -- to supply it. Until then every owner-session dependency
    # answers 401 UNAUTHORIZED rather than raising, so routers from other cards that guard
    # themselves with `require_owner_session` behave correctly on the bare app.
    from server.app.auth.router import install_auth

    install_auth(app)
    # <<< TC-owner-auth-session <<<

    # >>> TC-storage-write-blocked-readiness (MOD-data-store, MOD-health-service) >>>
    # Appended by TC-storage-write-blocked-readiness, which owns `server/app/storage/` and
    # `server/app/health/`. Import and call both sit inside these delimiters (F-A3R1-13);
    # importing inside the factory also keeps this module free of an import-time dependency
    # on the health package, so the two cannot form a cycle through `ReadinessProvider`.
    #
    # `install_storage` always sets `app.state.storage_guard` -- that is the attribute the
    # ingest write gate reads, and F-A3R1-11 was that it did not exist on every path. When
    # no provider was injected it also replaces the Phase 0 `StubReadinessProvider`, whose
    # `storage: None` ("not computed") is right for a skeleton with no state machine and
    # wrong now that one exists. Passing `readiness_provider` through keeps an explicitly
    # injected provider authoritative while still building the guard.
    #
    # No `reconciliation_check` is supplied: it belongs to TC-backup-restore-drill, and
    # until it exists `recovery_required` must not reopen on its own (I15, NC-10).
    from server.app.health.router import install_storage

    install_storage(app, readiness_provider=readiness_provider)
    # <<< TC-storage-write-blocked-readiness <<<

    # >>> TC-ingest-idempotent-ack-lost (MOD-ingest-service) >>>
    # One delimited include, imports inside the delimiters (F-A3R1-13). The router reads
    # `app.state.ingest_context` for its engine and `app.state.storage_guard` -- installed
    # just above by `install_storage`, so the ingest write gate is live on the bare factory
    # (F-A3R1-11). Neither is defaulted here: a deployment that wired no context gets 500
    # INTERNAL and one that configured no collector token gets 401, rather than a router
    # inventing a database connection or accepting every caller.
    from server.app.ingest.router import install_ingest_error_handlers
    from server.app.ingest.router import router as ingest_router

    install_ingest_error_handlers(app)
    app.include_router(ingest_router)
    # <<< TC-ingest-idempotent-ack-lost <<<

    # --- BEGIN include: TC-canonical-identity-merge (MOD-identity-service) -------------
    # Appended by TC-canonical-identity-merge per Phase 1 dispatch rule 2 (shared file, one
    # clearly delimited include). The router reads `app.state.engine` and
    # `app.state.owner_session_authenticator`; neither is defaulted here. Until
    # TC-owner-auth-session installs a real authenticator the identity routes answer 401,
    # which is the safe direction: an unconfigured deployment shows the owner's data to
    # nobody rather than to everybody.
    from server.app.identity.router import router as identity_router

    app.include_router(identity_router)
    # --- END include: TC-canonical-identity-merge --------------------------------------

    # >>> TC-telegram-linking-auth (MOD-telegram-adapter) >>>
    # One delimited include, import inside the delimiters (F-A3R1-13). The routes read
    # `app.state.telegram_context`; nothing is defaulted here. With no context installed the
    # webhook answers INTERNAL rather than inventing a database or a webhook secret, and
    # `ingress.verify_webhook_secret` denies every update while the secret is unconfigured --
    # default deny in the one place an unauthenticated caller can reach.
    from server.app.telegram.router import install_telegram

    install_telegram(app)
    # <<< TC-telegram-linking-auth <<<

    # >>> TC-saved-snapshot (MOD-saved-service) >>>
    # One delimited include, import inside the delimiters (F-A3R1-13). The routes read
    # `app.state.engine` (shared with the identity routes) and `app.state.storage_guard`
    # (installed above by `install_storage`, so the write gate is live on the bare factory).
    # Two more attributes are read and NOT defaulted here: `app.state.telegram_ingress_secret`
    # and `app.state.telegram_link_resolver`. Without them the Telegram branch of
    # `save.create` refuses -- an unlinked chat must not be able to write Saved rows, and
    # "linking has not been configured" is not a reason to trust the caller.
    #
    # `save.export` is deliberately not routed: export is deferred for the MVP (F-PC00-02)
    # and card §10 SG-01 makes shipping it a stop condition.
    from server.app.saved.router import router as saved_router

    app.include_router(saved_router)
    # <<< TC-saved-snapshot <<<

    # >>> TC-telegram-unknown-delivery (MOD-delivery-service) >>>
    # One delimited include, imports inside the delimiters (F-A3R1-13). The router reads
    # `app.state.delivery_context` for its engine, storage guard and the three ports
    # (`telegram.send_payload`, the link generation, the published report payload). None is
    # defaulted here: a deployment that wired no context gets 500 INTERNAL rather than a
    # router that invents a Telegram transport or a chat id, and an unconfigured owner
    # session answers 401 rather than serving delivery status to everybody.
    from server.app.delivery.router import install_delivery

    install_delivery(app)
    # <<< TC-telegram-unknown-delivery <<<

    # >>> TC-analysis-once-per-generation (MOD-analysis-service) >>>
    # One delimited include, imports inside the delimiters (F-A3R1-13). The router reads
    # `app.state.analysis_context` for its engine and ports, and `app.state.storage_guard`
    # (installed above by `install_storage`) so the analysis write gate is live on the bare
    # factory. Neither is defaulted here: a deployment that wired no context gets 500
    # INTERNAL and one with no analysis worker token gets 401, rather than a router
    # inventing a database connection or admitting every caller.
    #
    # `analysis.enqueue_tasks` is NOT routed: its transport is `internal`, so ingest and the
    # report builder call the service function directly (contracts/ports.yaml). Publishing it
    # would create the edge FE-07 exists to forbid.
    from server.app.analysis.router import install_analysis_error_handlers
    from server.app.analysis.router import router as analysis_router

    install_analysis_error_handlers(app)
    app.include_router(analysis_router)
    # <<< TC-analysis-once-per-generation <<<

    # >>> TC-report-coverage-publish-cas (MOD-report-service) >>>
    # One delimited include, import inside the delimiters (F-A3R1-13). The two routes read
    # `app.state.report_context` (a `PublishContext`: engine, tag port, embedding port) and
    # nothing is defaulted here -- a deployment that wired no context gets 500 INTERNAL rather
    # than a router that invents a database or writes its own tag service, and an
    # unconfigured owner session answers 401 rather than serving reports to everybody.
    #
    # `report.build` and `report.publish` are NOT routed: both are `transport: internal` in
    # contracts/ports.yaml, so the job service calls the builder in process. Exposing them
    # over HTTP would open the edge FE-13 exists to forbid.
    from server.app.report.router import install_reports

    install_reports(app)
    # <<< TC-report-coverage-publish-cas <<<

    # >>> TC-scheduler-lease-claim (MOD-scheduler, MOD-job-service) >>>
    # One delimited include, imports inside the delimiters (F-A3R1-13). The eleven `worker.*`
    # and `run.*` routes read `app.state.job_context` (a `JobContext`: engine, owner id,
    # schedule settings, clock, and the two allowed ports -- `ingest.get_checkpoint` and
    # `delivery.create_intent`). Nothing is defaulted here: a deployment that wired no context
    # gets 500 INTERNAL rather than a router that invents a database handle, an owner id or a
    # schedule, and an unconfigured owner session answers 401 rather than serving run history
    # to everybody.
    #
    # `scheduler.evaluate_due`, `job.enqueue_scheduled_run` and `job.coalesce_overdue` are NOT
    # routed: all three are `transport: internal` in contracts/ports.yaml, so the scheduler
    # loop calls them in process. Exposing them would let something outside the server start a
    # run, which is exactly the edge default-deny exists to forbid.
    from server.app.jobs.router import install_job_error_handlers
    from server.app.jobs.router import router as jobs_router

    install_job_error_handlers(app)
    app.include_router(jobs_router)
    # <<< TC-scheduler-lease-claim <<<

    # >>> TC-secret-settings-service (MOD-secret-service, MOD-settings-service) >>>
    # Four routes: three `settings.*` on the owner session (the two mutations additionally
    # behind CSRF) and one `secret.issue_task_credential` on the analysis worker token.
    #
    # `secret.store_provider_key` and `secret.revoke_task_credential` are NOT routed. Both are
    # `transport: internal` in contracts/ports.yaml -- MOD-settings-service calls the first in
    # process, MOD-analysis-service the second -- and publishing a key-writing endpoint would
    # create an edge the registry does not grant.
    #
    # The routers read `app.state.secret_context` / `app.state.settings_context`, which
    # `server/app/wiring.py` does not build yet (that file is outside this card's write set;
    # its own comments still record the gap as G-6). Until it does, both routers answer 500
    # INTERNAL rather than inventing an engine or an owner id -- the same shape the analysis
    # router already uses for an unwired context.
    from server.app.secret.router import router as secret_router
    from server.app.settings_service.router import router as settings_router

    app.include_router(secret_router)
    app.include_router(settings_router)
    # <<< TC-secret-settings-service <<<

    @app.get("/healthz", operation_id=OperationId.HEALTH_GET_LIVENESS.value)
    def get_liveness() -> JSONResponse:
        """``health.get_liveness`` — DB-independent liveness (HC-01).

        Returns only ``up`` and the schema version. It touches no table and no
        configuration, so it keeps answering while storage is blocked (SC26).
        """
        return JSONResponse(
            content={"status": "up", "schema_version": CONTRACT_SCHEMA_VERSION},
            headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
        )

    return app


@asynccontextmanager
async def _wire_on_startup(application: FastAPI) -> AsyncIterator[None]:
    """Build the real runtime when the process starts serving (``docs/owner-runbook.md`` G-2).

    Wiring belongs in a lifespan rather than at import time for one concrete reason: importing
    ``server.app.main`` must not create a database file. Test collection imports this module
    dozens of times, ``rr_admin status`` imports it to ask what a server *would* wire, and a
    factory that opened storage on import would make all of those write to disk.

    The failure mode is deliberately loud. If configuration is broken the process fails to
    start with the real error, instead of booting and answering 500 to the first login --
    which is exactly the symptom this whole packet exists to remove.
    """
    from server.app.wiring import wire

    wire(application)
    yield


#: The ASGI entry point the runbook and README name: ``server.app.main:app``. It is wired by
#: :func:`_wire_on_startup`; ``create_app()`` called directly stays bare.
app = create_app(lifespan=_wire_on_startup)
