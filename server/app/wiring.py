"""The composition root: engine -> repositories -> services -> ``app.state.*_context``.

What was missing
----------------
``create_app()`` mounts every card's router but constructs no service and reads no database
URL. That was correct for Phase 0 -- a bare factory with no configuration must not invent a
storage location -- but nothing ever filled the gap, so on a real process ``auth.login``
raised ``AttributeError: 'State' object has no attribute 'auth_service'`` and returned 500
(``docs/owner-runbook.md`` gap ``G-2``).

This module fills it, and it fills it by **mirroring what each card's own tests do**. Every
context below is constructed the same way the card that owns it constructs one in
``tests/integration/``; no service signature is changed and nothing is stubbed. Where a card's
test supplies a fake because the real dependency does not exist yet, the attribute is left
**unset** rather than faked -- see :data:`UNWIRED` and §"What is deliberately not wired".

The safe direction
------------------
Every router in this repo was written to fail closed: a missing context is 500 INTERNAL, a
missing credential is 401, a missing Telegram secret denies every update. So leaving something
unwired is loud and safe, while wiring it with a placeholder would be quiet and wrong. That
asymmetry is why this module never invents a dependency to make a route "work".

What is deliberately not wired
------------------------------
``app.state.report_context``
    ``PublishContext`` requires ``tag_port`` **and** ``embedding_port`` as non-optional
    fields. Neither has a production implementation: ``TagConfigVersionPort`` has none at all
    (``CR-TC-REPORT-01`` -- no card creates the tag-service side), and ``LocalEncoder`` is a
    Protocol whose only implementations live in tests, because the embedding model is still
    ``REQ-OQ09``/``REQ-A3``. Wiring a hash-based test encoder into a real deployment would
    put vectors in the database that no real model produced. Reported as ``CR-P0-07``.

``DeliveryContext.transport`` / ``AnalysisContext.provider_config`` / ``.secrets``
    All three need a credential, and there is no ``MOD-secret-service`` yet (gap ``G-6``,
    scheduled for wave 2). The contexts are built without them: both classes were designed to
    degrade -- ``require_transport()`` raises ``DeliveryDependencyUnavailable`` and analysis
    refuses rather than running unauthenticated -- so the routes exist and refuse honestly.

``app.state.research_connector``
    Left ``None`` exactly as ``install_research`` documents. The reason is **read from
    ``contracts/retry-policy.yaml`` at run time** rather than restated here: a hard-coded
    status string is precisely what went stale (``F-A3-P5-02``) -- this docstring used to say
    the ``REQ-A6`` facts were ``PLACEHOLDER_KC``, which stopped being true in Phase 2.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from server.app.auth.middleware import PrincipalKind, TokenRegistry
from server.app.auth.service import AuthService
from server.app.db import create_sqlite_engine
from server.app.settings import Settings, load_settings

#: Marker used in the wiring report for an attribute this module deliberately did not set.
UNWIRED = "unwired"

#: Why `report_context` is not built. A literal is right here and a lookup would be wrong:
#: the blocker is the *absence* of two implementations, and absence has nothing to read.
REPORT_CONTEXT_BLOCKED = (
    "CR-P0-07: TagConfigVersionPort has no implementation; no real embedding model " "(REQ-OQ09)"
)

#: The two stop conditions that actually hold the research connector below CONTRACT_READY,
#: named in `agent-tasks/TC-research-connector-metadata.md` §10.
_SG_DOC = (
    "SG-DOC: no contract names the arXiv/OpenAlex API host or endpoint (endpoint_template "
    "is None; CR-PC05-03)"
)
_SG_LIVE = "SG-LIVE: a real call is E3 and is not permitted without its own packet"


def research_connector_blockers(repo_root: Path | None = None) -> str:
    """Why the research connector is unwired -- **derived from the contract, now**.

    This function exists because the previous one-line literal was wrong for three phases.
    It told the Owner the ``REQ-A6`` rate facts were still ``PLACEHOLDER_KC``, on bytes where
    ``contracts/retry-policy.yaml`` already carried all six values with
    ``status: DOCS_derived`` and ``precode/requirements.csv`` had ``REQ-A6`` at ``XN``
    (``F-A3-P5-02``). Someone reading that line would have gone and re-resolved a requirement
    that was already closed -- on the one screen this wave built for the Owner to learn what
    works.

    So the rate-limit half is *read* rather than restated: if the facts ever do regress to
    ``PLACEHOLDER_KC`` this says so because the file says so, and if they stay resolved this
    stops claiming otherwise. The two real blockers are named as constants because they are
    the absence of a thing (a documented host; permission for a live call), and an absence
    cannot be looked up.
    """
    from server.app.settings import REPO_ROOT as _REPO_ROOT

    root = repo_root or _REPO_ROOT
    reasons = [_SG_DOC, _SG_LIVE]
    try:
        import yaml

        budgets = yaml.safe_load((root / "contracts" / "retry-policy.yaml").read_text("utf-8"))
        entry = (budgets or {}).get("budgets", {}).get("research_connector_rate_limit", {})
        status = str(entry.get("status", "")).strip()
    except Exception:  # pragma: no cover - a missing contract is its own, louder problem
        return "; ".join([*reasons, "retry-policy.yaml could not be read to confirm REQ-A6"])

    if status and status != "DOCS_derived":
        reasons.append(f"research_connector_rate_limit.status is {status!r}, not 'DOCS_derived'")
    return "; ".join(reasons)


@dataclass(frozen=True, slots=True)
class Runtime:
    """What a wired application is made of, kept together so tests can inspect it."""

    settings: Settings
    engine: Engine
    auth_service: AuthService
    owner_id: str | None
    wired: tuple[str, ...]
    unwired: tuple[tuple[str, str], ...]

    def report(self) -> dict[str, Any]:
        """A human- and machine-readable summary. Carries no secret (see `Settings.redacted`)."""
        return {
            "settings": self.settings.redacted(),
            "owner_bootstrapped": self.owner_id is not None,
            "wired": list(self.wired),
            "unwired": {name: reason for name, reason in self.unwired},
        }


def resolve_owner_id(engine: Engine) -> str | None:
    """Read the single owner row's id, or ``None`` when the database has not been bootstrapped.

    ``owner.singleton_guard`` makes "the owner row" unambiguous (``REQ-D05``: exactly one
    account, no signup page). Returning ``None`` rather than raising lets the server start
    before ``bootstrap-owner`` has run -- the owner-scoped contexts then stay unset and their
    routes answer honestly instead of the process refusing to boot.

    A missing ``owner`` table means the database has not been migrated; that is also ``None``
    here and is reported separately by ``rr_admin status``, which can tell the two apart.
    """
    try:
        with engine.connect() as connection:
            row = connection.execute(text("SELECT id FROM owner LIMIT 1")).fetchone()
    except Exception:
        return None
    return None if row is None else str(row[0])


def build_token_registry(settings: Settings) -> TokenRegistry:
    """Build the bearer-token registry from **hashes**, never from tokens.

    ``TokenRegistry.from_hashes`` exists precisely so a deployment can be configured with
    digests (``contracts/ops/secrets.md``). An empty registry is a valid, safe state: every
    bearer-authenticated route then answers 401, which is what an unconfigured server should
    say to a collector or a worker.
    """
    from server.app.auth.service import hash_bearer_token

    hashes: dict[str, PrincipalKind] = {}
    # A deployment may configure the collector token in clear (the ingest routes need it in
    # clear anyway) or as a digest. Hashing the clear one here keeps the two paths agreeing
    # instead of authenticating on one route and refusing on another.
    collector_digest = settings.collector_token_sha256
    if collector_digest is None and settings.collector_token is not None:
        collector_digest = hash_bearer_token(settings.collector_token)
    for digest, kind in (
        (collector_digest, PrincipalKind.COLLECTOR),
        (settings.analysis_worker_token_sha256, PrincipalKind.ANALYSIS_WORKER),
        (settings.backup_operator_token_sha256, PrincipalKind.BACKUP_OPERATOR),
    ):
        if digest:
            hashes[digest] = kind
    return TokenRegistry.from_hashes(hashes)


class _CheckpointAdapter:
    """``jobs.CheckpointPort`` -> the real ``ingest.get_checkpoint``.

    An adapter, not a fake: it calls the shipped service function with the shipped context.
    It exists only because the port is defined as an object with a method while the service
    is a module-level function taking its context first -- a shape difference, not a
    behaviour difference.
    """

    def __init__(self, ingest_context: Any) -> None:
        self._ctx = ingest_context

    def get_checkpoint(self, *, run_id: str) -> Any:
        from server.app.ingest.service import get_checkpoint

        try:
            return get_checkpoint(self._ctx, run_id=run_id)
        except Exception:
            # A run with no checkpoint yet is the normal case on a fresh database, and the
            # port is typed to answer `None` for it. Letting the exception out would turn
            # "nothing collected yet" into a failed assignment claim.
            return None


class _AlertIntentAdapter:
    """``jobs.AlertIntentPort`` -> the real ``delivery.create_intent`` (``run_alert``).

    **Joins the caller's transaction** (``CR-TC-COLLECTOR-11``). ``jobs.report_stop`` calls
    this port from *inside* an open ``engine.begin()``; the first version of this adapter
    ignored that and let ``create_intent`` open its own transaction, so SQLite saw a second
    writer against a database the caller already held and raised ``database is locked``. The
    run-needs-you alert could therefore not succeed in **any** wiring -- not a configuration
    problem, a deadlock built into the composition root.

    ``delivery.create_intent`` already takes ``connection=`` for exactly this reason (the
    outbox pattern: the intent must land in the same commit as the state change that caused
    it). So the fix is to pass the caller's connection straight through.

    ``connection`` is accepted as an **optional keyword** so this adapter satisfies the port
    both before and after ``W6A`` widens ``AlertIntentPort`` to pass it: today's caller omits
    it, tomorrow's supplies it, and neither needs a second version of this class. When it is
    omitted the call still runs -- on its own transaction, as before -- because refusing
    would turn a coordination window into an outage.
    """

    def __init__(self, delivery_context: Any, owner_id: str) -> None:
        self._ctx = delivery_context
        self._owner_id = owner_id

    def create_alert_intent(
        self, *, run_id: str, stop_reason: str, connection: Any | None = None
    ) -> str | None:
        # The enum comes from the generated contract bindings, which is where it is
        # defined; `delivery.service` re-exports neither it nor a synonym.
        from rr_contracts.generated.states import DeliveryIntentKind

        from server.app.delivery.service import create_intent

        result = create_intent(
            self._ctx,
            owner_id=self._owner_id,
            kind=DeliveryIntentKind.RUN_ALERT,
            caller_module="MOD-job-service",
            run_id=run_id,
            connection=connection,
        )
        # `delivery.create_intent` returns `{"intent_id": ..., "delivery_id": ...}` on all
        # three of its paths (`server/app/delivery/service.py`). The first version of this
        # line read `delivery_intent_id` or `id` -- neither key exists, so the intersection
        # was empty and this always answered `None`. `jobs.report_stop` reads `None` as "no
        # intent was created", skips its `UPDATE run SET alert_intent_id` and reports
        # `alert_created: False`. The outbox row existed; the run simply never learned about
        # it. A silent wrong answer, not a crash (`CR-TC-COLLECTOR-13`, found by WC).
        #
        # `delivery_id` is the trap: it is the *delivery* row's id, a different entity, and
        # reading it here would have produced a plausible-looking id that points at the wrong
        # thing -- worse than the `None`.
        #
        # Missing key raises rather than degrading to `None`: an absent `intent_id` means the
        # service's return shape changed, and absorbing that is exactly how this defect
        # survived its first review.
        try:
            intent_id = result["intent_id"]
        except KeyError:  # pragma: no cover - guards a contract change, not a runtime state
            raise KeyError(
                "delivery.create_intent returned no 'intent_id'; its return shape changed "
                f"(got keys: {sorted(result)})"
            ) from None
        return None if intent_id is None else str(intent_id)


class _AssignmentAdapter:
    """``ingest.AssignmentPort`` -> the ``assignment_lease`` row the job service owns.

    ``CR-TC-COLLECTOR-09``: ``IngestContext`` was built with no ``assignment`` port, so
    ``ingest.submit_batch`` could not check the lease a batch claims to hold -- the check
    that makes a stale collector's batch bounce instead of landing.

    This reads the lease table directly rather than calling into ``server/app/jobs/``: the
    port wants three fields (``run_id``, ``lease_epoch``, ``revoked``) and the job service
    exposes no read function shaped like the port. The read is scoped by ``owner_id`` and by
    both ids, and a missing row answers ``None``, which the ingest service already treats as
    "no such lease" -- the safe direction.
    """

    def __init__(self, engine: Engine, owner_id: str) -> None:
        self._engine = engine
        self._owner_id = owner_id

    def lease_snapshot(self, *, job_id: str, lease_id: str) -> Any:
        from server.app.ingest.service import LeaseSnapshot

        with self._engine.connect() as connection:
            row = (
                connection.execute(
                    text(
                        "SELECT run_id, lease_epoch, state FROM assignment_lease "
                        "WHERE owner_id = :o AND id = :lease AND job_id = :job"
                    ),
                    {"o": self._owner_id, "lease": lease_id, "job": job_id},
                )
                .mappings()
                .fetchone()
            )
        if row is None:
            return None
        return LeaseSnapshot(
            run_id=str(row["run_id"]),
            lease_epoch=int(row["lease_epoch"]),
            revoked=str(row["state"]) != "held",
        )


def build_runtime(settings: Settings | None = None) -> Runtime:
    """Create the engine and the services that do not depend on an owner row."""
    settings = settings or load_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_sqlite_engine(settings.database_path)
    auth_service = AuthService(engine)
    return Runtime(
        settings=settings,
        engine=engine,
        auth_service=auth_service,
        owner_id=resolve_owner_id(engine),
        wired=(),
        unwired=(),
    )


def wire(app: Any, settings: Settings | None = None) -> Runtime:
    """Attach a real runtime to ``app``. Returns what was wired and what was not.

    Import order note: every service import happens **inside** this function, for the same
    reason each card's include block in ``main.py`` imports inside its delimiters -- the
    factory must remain importable without dragging in every domain module, and a cycle
    through the composition root would be very hard to unpick.
    """
    runtime = build_runtime(settings)
    engine = runtime.engine
    owner_id = runtime.owner_id
    wired: list[str] = []
    unwired: list[tuple[str, str]] = []

    # -- always available: they need only an engine -------------------------------------
    app.state.engine = engine
    app.state.auth_service = runtime.auth_service
    app.state.token_registry = build_token_registry(runtime.settings)
    wired += ["engine", "auth_service", "token_registry"]

    # The owner-session authenticator the identity and saved routes read. `install_auth`
    # leaves it unset on the bare factory; here the AuthService itself is the authenticator,
    # which is what `tests/integration/test_identity_merge_audit.py` wires.
    app.state.owner_session_authenticator = runtime.auth_service
    wired.append("owner_session_authenticator")

    # `ingest.submit_batch` / `ingest.commit_checkpoint` compare the presented bearer token
    # against this attribute with `hmac.compare_digest` (`server/app/ingest/router.py`), so
    # the hash in the TokenRegistry cannot serve those two routes. Without it a fully wired
    # deployment 401s every collector call (`CR-TC-COLLECTOR-10`). Unset stays unset: the
    # router treats absent configuration as UNAUTHORIZED, never as "allow".
    if runtime.settings.collector_token is not None:
        app.state.collector_token = runtime.settings.collector_token
        wired.append("collector_token")
    else:
        unwired.append(
            ("collector_token", "RR_COLLECTOR_TOKEN is not set; collector ingest calls 401")
        )

    if runtime.settings.telegram_webhook_secret is not None:
        app.state.telegram_ingress_secret = runtime.settings.telegram_webhook_secret
        wired.append("telegram_ingress_secret")
    else:
        unwired.append(
            ("telegram_ingress_secret", "RR_TELEGRAM_WEBHOOK_SECRET is not set; updates denied")
        )

    if owner_id is None:
        unwired.append(
            (
                "owner-scoped contexts",
                "no owner row: run `uv run rr-admin bootstrap-owner` (and `rr-admin "
                "migrate` first if the database is empty), then restart",
            )
        )
        runtime = replace(runtime, wired=tuple(wired), unwired=tuple(unwired))
        app.state.runtime = runtime
        return runtime

    # -- owner-scoped contexts -----------------------------------------------------------
    from server.app.analysis.service import AnalysisContext
    from server.app.delivery.service import DeliveryContext
    from server.app.ingest.service import IngestContext
    from server.app.jobs.service import JobContext
    from server.app.scheduler.evaluator import ScheduleSettings
    from server.app.telegram.ingress import TelegramContext

    storage_guard = app.state.storage_guard  # installed by create_app's storage block
    # The identity *module* satisfies `IngestContext.IdentityPort` structurally: the port is
    # one function, `resolve_target(target, *, owner_id, ...)`, and that is exactly the
    # module-level function the identity card ships. Importing the module as the port keeps
    # the real implementation in the path instead of a wrapper that could drift from it.
    from server.app import identity as _identity_pkg  # noqa: F401  (package import first)
    from server.app.identity import service as identity_port

    ingest_context = IngestContext(
        engine=engine,
        owner_id=owner_id,
        assignment=_AssignmentAdapter(engine, owner_id),
        identity=identity_port,
        storage_guard=storage_guard,
    )
    app.state.ingest_context = ingest_context
    wired.append("ingest_context")

    delivery_context = DeliveryContext(engine=engine, storage=storage_guard)
    app.state.delivery_context = delivery_context
    wired.append("delivery_context")
    unwired.append(
        (
            "delivery_context.transport",
            "no Telegram bot token is configured; MOD-secret-service exists now, so this is "
            "a missing credential, not a missing module",
        )
    )

    app.state.analysis_context = AnalysisContext(
        engine=engine, owner_id=owner_id, storage_guard=storage_guard
    )
    wired.append("analysis_context")
    unwired.append(
        (
            "analysis_context.provider_config",
            "no AI provider is enabled: REQ-OQ03 unanswered and both adapters stay "
            "enabled=false until their isolation evidence exists (REQ-A5, ADR-0010)",
        )
    )

    app.state.telegram_context = TelegramContext(
        engine=engine,
        owner_id=owner_id,
        webhook_secret=runtime.settings.telegram_webhook_secret,
        storage_guard=storage_guard,
    )
    wired.append("telegram_context")

    app.state.job_context = JobContext(
        engine=engine,
        owner_id=owner_id,
        settings=ScheduleSettings(
            slots_local=runtime.settings.schedule_slots,
            timezone_iana=runtime.settings.timezone_iana,
        ),
        storage_guard=storage_guard,
        checkpoint_port=_CheckpointAdapter(ingest_context),
        alert_port=_AlertIntentAdapter(delivery_context, owner_id),
    )
    wired.append("job_context")

    # -- secret + settings (CR-TC-SECRET-06) ---------------------------------------------
    # `/v1/settings` and every `secret.*` route answered 500 on a real deployment because
    # neither context was ever built. They are composed here the way
    # `tests/integration/test_task_credential_lease.py` composes them, with one knot to tie:
    # `SettingsContext.secrets` points at the secret context, and the secret context's
    # `providers` is a view over the settings context. Settings is built first, the secret
    # context second, and the back-reference assigned last -- both dataclasses are mutable
    # for exactly this kind of composition.
    from server.app.secret.service import SecretContext
    from server.app.secret.store import (
        FileMaterialStore,
        MasterKeyUnavailable,
        SecretStore,
        load_master_key,
    )
    from server.app.settings_service.service import SettingsContext, SettingsProviderView

    settings_context = SettingsContext(
        engine=engine, owner_id=owner_id, storage_guard=storage_guard
    )

    # The master key is NEVER defaulted and NEVER generated (contracts/ops/secrets.md §4.1).
    # Two different conditions, deliberately handled differently:
    #
    #   * NOT SET  -> the store stays `None`. `REQ-D51` says no key is mandatory, and
    #     `SecretContext.store` is optional precisely so a deployment with no AI credential
    #     yet still runs; every operation that needs the key refuses with INTERNAL. Refusing
    #     to boot here would take `/v1/settings` -- which needs no key -- down with it.
    #   * SET BUT MALFORMED -> refuse to start, loudly, naming the variable. That is an
    #     operator error, and continuing would silently downgrade a deployment that believes
    #     it has encryption to one that has none.
    secret_store: SecretStore | None = None
    if os.environ.get("RR_SECRET_MASTER_KEY"):
        try:
            master_key = load_master_key()
        except MasterKeyUnavailable as exc:
            raise RuntimeError(
                f"RR_SECRET_MASTER_KEY is set but unusable: {exc}. Refusing to start rather "
                "than run with no envelope encryption (contracts/ops/secrets.md §4.1)."
            ) from None
        material_dir = runtime.settings.secret_material_dir
        assert material_dir is not None  # load_settings always fills it
        secret_store = SecretStore(master_key=master_key, material=FileMaterialStore(material_dir))
        wired.append("secret_store")
    else:
        unwired.append(
            (
                "secret_store",
                "RR_SECRET_MASTER_KEY is not set; secret.* operations refuse (REQ-D51: a key "
                "is not mandatory). No key is ever generated or defaulted.",
            )
        )

    secret_context = SecretContext(
        engine=engine,
        owner_id=owner_id,
        store=secret_store,
        providers=SettingsProviderView(settings_context),
        storage_guard=storage_guard,
    )
    settings_context.secrets = secret_context

    app.state.secret_context = secret_context
    app.state.settings_context = settings_context
    wired += ["secret_context", "settings_context"]

    # Set explicitly rather than left absent (`F-A3-P5-03`). `None` and "attribute missing"
    # are the same to `getattr(..., None)`, but only one of them is a *statement*: W4A is
    # making the report routes answer a declared error instead of 500, and that needs the
    # composition root to have said "deliberately not built" rather than to have forgotten.
    app.state.report_context = None
    unwired.append(("report_context", REPORT_CONTEXT_BLOCKED))
    unwired.append(("research_connector", research_connector_blockers()))

    runtime = replace(runtime, wired=tuple(wired), unwired=tuple(unwired))
    app.state.runtime = runtime
    return runtime


def create_wired_app(settings: Settings | None = None) -> Any:
    """``create_app()`` plus :func:`wire` -- the entry point a real process should use."""
    from server.app.main import create_app

    app = create_app()
    wire(app, settings)
    return app


def alembic_config(database_path: Path) -> Any:
    """An Alembic ``Config`` that works from **any** working directory (gap ``G-4``).

    ``server/alembic.ini`` uses ``script_location = migrations``, resolved relative to the
    process's cwd, so ``alembic upgrade head`` only worked from inside ``server/``. Building
    the config here with absolute paths removes the cwd dependency without touching the ini
    file or ``server/migrations/env.py`` -- both of which the cards' test fixtures already
    load, and neither of which is this packet's to change.
    """
    from alembic.config import Config

    from server.app.settings import REPO_ROOT

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    return config


@contextmanager
def alembic_database_env(database_path: Path) -> Iterator[None]:
    """Point ``server/migrations/env.py`` at ``database_path`` for the duration of a block.

    ``env.py`` deliberately refuses to guess a location and reads ``RR_DATABASE_URL`` from
    the environment -- it ignores ``sqlalchemy.url``. Rather than change that file (it is not
    in this packet's write set, and its refusal to guess is correct), this sets the variable
    around the upgrade and restores it afterwards. That is precisely what the cards' own
    migration fixtures do, e.g. ``tests/integration/test_denied_edges.py::_migrate``.
    """
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(database_path)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


def upgrade_database(database_path: Path, revision: str = "head") -> None:
    """Run ``alembic upgrade`` against ``database_path`` from any working directory."""
    from alembic import command

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with alembic_database_env(database_path):
        command.upgrade(alembic_config(database_path), revision)


__all__ = [
    "REPORT_CONTEXT_BLOCKED",
    "UNWIRED",
    "Runtime",
    "alembic_config",
    "alembic_database_env",
    "build_runtime",
    "build_token_registry",
    "create_wired_app",
    "research_connector_blockers",
    "resolve_owner_id",
    "upgrade_database",
    "wire",
]
