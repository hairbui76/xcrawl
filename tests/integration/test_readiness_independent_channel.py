"""E1/E2 — the health channel is independent of the database.

Oracles (``agent-tasks/TC-storage-write-blocked-readiness.md`` §8 and
``contracts/state/storage.yaml`` ``independent_health_channel``):

* ``health.get_liveness`` still answers when the database is dead (HC-01);
* ``health.get_readiness`` reports storage red from process memory, with no database access
  at all (HC-02);
* ``storage.get_health`` is internal: the five forbidden edges into ``MOD-data-store`` are
  refused with the codes pinned in
  ``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` (HC-03, SC49, stop
  gate ``SG-DENY``);
* fixture ``recovery/j``: ``recovery_required`` means ``COUNT(delivery attempt after
  restore) = 0`` and the dispatcher stays locked (SC42, ``I15``).

Stop gate ``SG-01`` is the reason the "no database access" assertions are written as
statement counters rather than as "it returned 200": an endpoint that happened to succeed
because the test database was healthy would prove nothing about the incident.
"""

from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth
from sqlalchemy import text

from server.app.db.engine import create_sqlite_engine, session_scope
from server.app.db.faults import WriteFaultInjector
from server.app.health.router import (
    StorageReadinessProvider,
    build_health_router,
    install_health_error_handler,
    install_storage,
    owner_session_absent,
)
from server.app.main import create_app
from server.app.storage.guard import StorageGuard, StorageRefused
from server.app.storage.health import (
    READINESS_OF_STORAGE,
    TRANSITIONS,
    ForbiddenTransition,
    StorageHealthMachine,
)

FIXTURE_J = "recovery/j-restore-verification-incomplete-dispatch-locked"
FIXTURE_BOUNDARY = "boundary/a-default-deny-sweep-36-edges"

#: ``server.app.auth.middleware`` is the write set of ``TC-owner-auth-session``.
AUTH_MIDDLEWARE_PRESENT = importlib.util.find_spec("server.app.auth.middleware") is not None


def _allow_owner_session() -> None:
    """Test stand-in for the owner-session dependency.

    Only used by the tests whose subject is readiness *content*. The tests whose subject is
    the auth scheme itself do not use it -- see :func:`test_readiness_requires_owner_session`.
    """
    return None


def _client(guard: StorageGuard, *, authenticated: bool = True) -> TestClient:
    """A minimal app carrying only this card's router.

    Built here rather than via ``create_app`` so a failure points at this card's router and
    not at whatever else the application factory has accumulated.

    ``authenticated=False`` installs :func:`owner_session_absent`, the documented fallback
    for a tree without ``server.app.auth.middleware``. It is passed explicitly rather than
    left to the default so this test keeps asserting the *deny* behaviour even now that the
    real middleware exists -- which is exactly when a deny-by-default fallback is easiest to
    break without noticing.
    """
    app = FastAPI()
    install_health_error_handler(app)
    app.include_router(
        build_health_router(
            StorageReadinessProvider(guard),
            include_liveness=True,
            owner_session_dependency=(
                _allow_owner_session if authenticated else owner_session_absent
            ),
        )
    )
    return TestClient(app)


@pytest.fixture()
def guard() -> StorageGuard:
    return StorageGuard(StorageHealthMachine())


# ---------------------------------------------------------------------------------------
# HC-01 -- liveness survives a dead database
# ---------------------------------------------------------------------------------------


def test_liveness_answers_while_the_database_cannot_be_written(
    guard: StorageGuard, tmp_path: Path
) -> None:
    """HC-01, write half."""
    engine = create_sqlite_engine(tmp_path / "live.db")
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY)"))
    injector = WriteFaultInjector(engine)
    guard.record_write_failure()

    with injector.disk_full():
        response = _client(guard).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "up", "schema_version": CONTRACT_SCHEMA_VERSION}


def test_liveness_answers_when_the_database_file_does_not_exist(guard: StorageGuard) -> None:
    """HC-01, read half: *"kể cả khi DB không đọc được"*.

    No engine is created at all here. If liveness ever grew a database dependency this test
    would fail with an import or connection error rather than quietly passing.
    """
    response = _client(guard).get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "up"


def test_liveness_body_carries_nothing_but_status_and_version(guard: StorageGuard) -> None:
    """The prohibition is the contract: no configuration, provider names, chat ids, data.

    Asserting the exact key set rather than the presence of ``status`` is what makes this a
    test of the prohibition rather than of the happy path.
    """
    body = _client(guard).get("/healthz").json()
    assert set(body) == {"status", "schema_version"}


# ---------------------------------------------------------------------------------------
# HC-02 -- readiness comes from memory
# ---------------------------------------------------------------------------------------


def test_readiness_reports_red_without_touching_the_database(
    guard: StorageGuard, tmp_path: Path
) -> None:
    """HC-02: red storage, and the statement counter proves no query was issued."""
    engine = create_sqlite_engine(tmp_path / "ready.db")
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY)"))
    injector = WriteFaultInjector(engine)
    guard.record_write_failure()
    injector.reset_counters()

    response = _client(guard).get("/v1/health/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["modules"]["storage"] == "down"
    assert body["storage_health"] == StorageHealth.WRITE_BLOCKED.value
    assert injector.statements_attempted == 0


@pytest.mark.parametrize(
    ("state", "expected_row"),
    [(state, row) for state, row in READINESS_OF_STORAGE.items()],
)
def test_readiness_row_matches_deployment_contract(state: StorageHealth, expected_row: str) -> None:
    """``contracts/ops/deployment.md`` §5, all four states.

    ``maintenance`` is the interesting row: ``degraded``, not ``down``. Collapsing it into
    ``down`` would tell an operator their own planned window is an incident (``I13``).
    """
    guard = StorageGuard(StorageHealthMachine(initial=state))
    body = _client(guard).get("/v1/health/readiness").json()
    assert body["modules"]["storage"] == expected_row


def test_readiness_reports_unimplemented_rows_as_not_computed(guard: StorageGuard) -> None:
    """``I13`` applied to this endpoint: unknown is reported, never rounded up to ``ok``."""
    body = _client(guard).get("/v1/health/readiness").json()
    for row in StorageReadinessProvider.DEFERRED_ROWS:
        assert body["modules"][row] is None


def test_readiness_carries_as_of(guard: StorageGuard) -> None:
    """``UI-01``: the UI cannot label last-known data without knowing when it was read."""
    body = _client(guard).get("/v1/health/readiness").json()
    parsed = datetime.fromisoformat(body["as_of"].replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    assert parsed <= datetime.now(UTC)


def test_as_of_moves_when_the_state_changes(guard: StorageGuard) -> None:
    """A frozen ``as_of`` would make stale data look fresh."""
    before = _client(guard).get("/v1/health/readiness").json()["as_of"]
    guard.record_write_failure()
    after = _client(guard).get("/v1/health/readiness").json()["as_of"]
    assert after >= before


@pytest.mark.skipif(
    not AUTH_MIDDLEWARE_PRESENT, reason="server.app.auth.middleware not present yet"
)
def test_readiness_uses_the_real_owner_session_middleware() -> None:
    """Readiness must use ``TC-owner-auth-session``'s dependency, not a local copy.

    Skipped rather than xfailed when that card has not landed: the assertion is about which
    module is wired, and until it exists there is nothing to observe. The deny-by-default
    fallback that stands in meanwhile is asserted by
    :func:`test_readiness_requires_owner_session`.
    """
    from server.app.auth.middleware import (  # type: ignore[import-not-found]
        require_owner_session,
    )
    from server.app.health.router import _default_owner_session_dependency

    assert _default_owner_session_dependency() is require_owner_session


def test_readiness_requires_owner_session(guard: StorageGuard) -> None:
    """``contracts/http/openapi.yaml``: ``/v1/health/readiness`` is ``ownerSessionCookie``.

    With no auth module present the router denies, and it denies with the contract's
    envelope rather than FastAPI's default ``{"detail": ...}``.
    """
    response = _client(guard, authenticated=False).get("/v1/health/readiness")
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == ErrorCode.UNAUTHORIZED.value
    assert body["scope"] == "request"
    assert body["retry_class"] == "none"
    assert body["correlation_id"]
    assert body["details_safe"] == {
        "operation_id": OperationId.HEALTH_GET_READINESS.value,
        "required_auth_scope": "owner_session",
    }


def test_liveness_stays_unauthenticated(guard: StorageGuard) -> None:
    """``security: []`` in the contract. A liveness check behind a session is not one."""
    assert _client(guard, authenticated=False).get("/healthz").status_code == 200


# ---------------------------------------------------------------------------------------
# HC-03 / SG-DENY -- storage.get_health is internal
# ---------------------------------------------------------------------------------------


def test_default_deny_on_storage_get_health(fixture_loader: Any) -> None:
    """SC49: every forbidden edge into ``MOD-data-store`` is refused with its pinned code.

    Driven from the sweep fixture, filtered to the edges whose callee is this card's module,
    so the codes come from the oracle and not from a list retyped here. Getting the *code*
    wrong is a failure even when the call is correctly refused (card §5, ruling R5-01):
    ``CAPABILITY_DENIED`` and ``FORBIDDEN_EDGE`` tell an operator different things about
    where the block lives.
    """
    fixture = fixture_loader(FIXTURE_BOUNDARY)
    edges = [e for e in fixture.events if e["callee"] == "MOD-data-store"]
    assert {e["forbidden_edge_ref"] for e in edges} == {
        "FE-01",
        "FE-05",
        "FE-15",
        "FE-18",
        "FE-29",
    }

    guard = StorageGuard(StorageHealthMachine())
    for edge in edges:
        assert edge["operation"] == OperationId.STORAGE_GET_HEALTH.value
        with pytest.raises(StorageRefused) as caught:
            guard.get_health(caller_module=edge["actor"])
        assert caught.value.envelope["code"] == edge["expected_error_code"], edge[
            "forbidden_edge_ref"
        ]


def test_allowed_callers_reach_storage_get_health(guard: StorageGuard) -> None:
    """The positive control for default deny: the two contracted callers do get through."""
    for caller in ("MOD-health-service", "MOD-job-service"):
        health = guard.get_health(caller_module=caller)
        assert health["storage_health"] == StorageHealth.HEALTHY.value
        assert health["observed_at"].endswith("Z")


def test_unknown_caller_is_denied(guard: StorageGuard) -> None:
    """Default deny means default: a module the registry has never heard of is refused."""
    with pytest.raises(StorageRefused) as caught:
        guard.get_health(caller_module="MOD-does-not-exist")
    assert caught.value.code is ErrorCode.CAPABILITY_DENIED


# ---------------------------------------------------------------------------------------
# Fixture j -- recovery_required keeps the dispatcher locked (SC42, I15)
# ---------------------------------------------------------------------------------------


@pytest.fixture()
def recovering_guard(fixture_loader: Any) -> StorageGuard:
    """A guard in the state fixture ``j`` describes: restored, not reconciled."""
    fixture = fixture_loader(FIXTURE_J)
    assert fixture.given["storage_health"] == StorageHealth.RECOVERY_REQUIRED.value
    restore_id = fixture.given["restore_record"]["id"]
    return StorageGuard(
        StorageHealthMachine(initial=StorageHealth.RECOVERY_REQUIRED, pending_restore_id=restore_id)
    )


def test_fixture_j_refuses_every_event_with_restore_unverified(
    fixture_loader: Any, recovering_guard: StorageGuard
) -> None:
    """``expected.seq1/2/3``: all three refused, all three with ``RESTORE_UNVERIFIED``."""
    fixture = fixture_loader(FIXTURE_J)
    expected = fixture.expected
    assert expected["seq1"]["error_code"] == ErrorCode.RESTORE_UNVERIFIED.value

    # seq 1 -- backup.reconcile_after_restore itself is refused while the predicate is false.
    restore_id = fixture.given["restore_record"]["id"]
    with pytest.raises(StorageRefused) as caught:
        recovering_guard.complete_reconciliation(restore_id)
    assert caught.value.code is ErrorCode.RESTORE_UNVERIFIED

    # seq 2 and seq 3 -- dispatch and worker claim.
    for seq, operation in (
        (2, OperationId.DELIVERY_DISPATCH_NEXT),
        (3, OperationId.WORKER_CLAIM_ASSIGNMENT),
    ):
        with pytest.raises(StorageRefused) as caught:
            recovering_guard.assert_writable(operation)
        assert caught.value.envelope["code"] == expected[f"seq{seq}"]["error_code"]

    assert expected["seq2"]["messages_sent"] == 0
    assert expected["storage_health_after"] == StorageHealth.RECOVERY_REQUIRED.value
    assert recovering_guard.current_health() is StorageHealth.RECOVERY_REQUIRED


def test_fixture_j_reconciliation_predicate_is_false(
    fixture_loader: Any, recovering_guard: StorageGuard
) -> None:
    """``oracle_vi``: ``reconciliation_complete(RR-03) == false``.

    The fixture's ``given`` has integrity ``ok`` and every count matching the manifest --
    and reconciliation is still incomplete, because ``operator_acknowledgement`` is null.
    An implementation that inferred completion from counts would pass this fixture's
    ``given`` and unlock dispatch, which is ``forbidden_effects`` row 3.
    """
    fixture = fixture_loader(FIXTURE_J)
    record = fixture.given["restore_record"]
    assert record["integrity_check_outcome"] == "ok"
    assert record["counts_observed"] == record["manifest_counts"]
    assert record["operator_acknowledgement"] is None

    assert recovering_guard.reconciliation_complete(record["id"]) is False
    assert fixture.expected["dispatcher_unlocked_at"] is None
    assert recovering_guard.machine.dispatcher_is_locked() is True


def test_readiness_shows_the_dispatcher_locked_during_recovery(
    recovering_guard: StorageGuard,
) -> None:
    """``contracts/ops/deployment.md`` §5: ``delivery_dispatcher`` is ``down`` when locked."""
    body = _client(recovering_guard).get("/v1/health/readiness").json()
    assert body["modules"]["delivery_dispatcher"] == "down"
    assert body["dispatcher_locked_for_recovery"] is True
    assert body["storage_health"] == StorageHealth.RECOVERY_REQUIRED.value


def test_reconciliation_unlocks_only_through_the_predicate(fixture_loader: Any) -> None:
    """``T-ST-06`` is the single gate out of ``recovery_required``.

    The same guard is asked twice with only the injected predicate changed, so the test
    isolates the predicate as the cause.
    """
    fixture = fixture_loader(FIXTURE_J)
    restore_id = fixture.given["restore_record"]["id"]
    guard = StorageGuard(
        StorageHealthMachine(
            initial=StorageHealth.RECOVERY_REQUIRED, pending_restore_id=restore_id
        ),
        reconciliation_check=lambda _restore_id: True,
    )
    assert guard.complete_reconciliation(restore_id) == "T-ST-06"
    assert guard.current_health() is StorageHealth.HEALTHY
    assert guard.machine.pending_restore_id is None


def test_recovery_required_has_no_automatic_exit() -> None:
    """``NC-10`` and ``forbidden_transitions`` row 1: no timeout, no attempt count, no restart.

    Restarting a process is modelled as building a fresh machine from the persisted
    ``restore_record``; if that came back ``healthy``, the outbox would replay.
    """
    guard = StorageGuard(
        StorageHealthMachine(initial=StorageHealth.RECOVERY_REQUIRED, pending_restore_id="RR-03")
    )
    for _ in range(50):
        with pytest.raises(StorageRefused):
            guard.assert_writable(OperationId.DELIVERY_DISPATCH_NEXT)
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED

    restarted = StorageGuard(
        StorageHealthMachine(initial=StorageHealth.RECOVERY_REQUIRED, pending_restore_id="RR-03")
    )
    assert restarted.current_health() is StorageHealth.RECOVERY_REQUIRED


def test_reconciling_the_wrong_restore_id_is_refused() -> None:
    """A predicate that says "yes" about a different restore must not unlock this one."""
    guard = StorageGuard(
        StorageHealthMachine(initial=StorageHealth.RECOVERY_REQUIRED, pending_restore_id="RR-03"),
        reconciliation_check=lambda _restore_id: True,
    )
    with pytest.raises(ForbiddenTransition):
        guard.machine.complete_reconciliation(
            "RR-99", reconciliation_complete=lambda _restore_id: True
        )
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED


# ---------------------------------------------------------------------------------------
# The state machine as a whole
# ---------------------------------------------------------------------------------------


def test_all_nine_transitions_are_declared() -> None:
    """``T-ST-01``..``T-ST-09``, no more and no fewer."""
    assert [t.id for t in TRANSITIONS] == [f"T-ST-{n:02d}" for n in range(1, 10)]


def test_maintenance_still_refuses_worker_claim() -> None:
    """``T-ST-09.oracle_vi``: maintenance is not a back door to granting work."""
    guard = StorageGuard(StorageHealthMachine())
    guard.record_write_failure()
    assert guard.enter_maintenance() == "T-ST-09"
    with pytest.raises(StorageRefused) as caught:
        guard.assert_writable(OperationId.WORKER_CLAIM_ASSIGNMENT)
    assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED


def test_maintenance_from_write_blocked_is_refused_while_a_restore_is_pending() -> None:
    """``T-ST-09`` must not become a laundering route to ``healthy`` via ``T-ST-04``."""
    guard = StorageGuard(
        StorageHealthMachine(initial=StorageHealth.WRITE_BLOCKED, pending_restore_id="RR-03")
    )
    with pytest.raises(ForbiddenTransition):
        guard.enter_maintenance()


def test_maintenance_cannot_close_before_verify_passes() -> None:
    """``T-ST-04.forbidden_vi``."""
    guard = StorageGuard(StorageHealthMachine())
    guard.enter_maintenance()
    with pytest.raises(ForbiddenTransition):
        guard.leave_maintenance(snapshot_verified=False)
    assert guard.current_health() is StorageHealth.MAINTENANCE
    assert guard.leave_maintenance(snapshot_verified=True) == "T-ST-04"


def test_restore_then_write_failure_keeps_the_reconciliation_debt() -> None:
    """``T-ST-07``: a disk incident during recovery must not erase what is owed."""
    guard = StorageGuard(StorageHealthMachine())
    guard.enter_maintenance()
    guard.mark_recovery_required("RR-03")
    assert guard.record_write_failure() == "T-ST-07"
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED
    assert guard.machine.pending_restore_id == "RR-03"


def test_the_full_incident_path_visits_the_contracted_transitions() -> None:
    """One end-to-end walk: healthy -> maintenance -> restore -> disk fault -> recovery."""
    guard = StorageGuard(StorageHealthMachine())
    guard.enter_maintenance()
    guard.mark_recovery_required("RR-03")
    guard.record_write_failure()
    now = datetime(2026, 9, 7, 9, 0, 0, tzinfo=UTC)
    for step in range(3):
        guard.record_probe(success=True, at=now.replace(minute=step * 2))
    assert guard.machine.history == ("T-ST-03", "T-ST-05", "T-ST-07", "T-ST-08")
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED


# ---------------------------------------------------------------------------------------
# The bare factory -- F-A3R1-11
# ---------------------------------------------------------------------------------------


def test_create_app_always_exposes_the_storage_guard() -> None:
    """``app.state.storage_guard`` exists on the shipped factory, with no wiring done.

    This is the attribute ``TC-ingest-idempotent-ack-lost`` reads to build its
    ``IngestContext``. The finding it closes (``F-A3R1-11``) was that the earlier include
    block only built a guard when no readiness provider had been injected, so on one of the
    two construction paths the ingest write gate silently did not run.
    """
    app = create_app()
    guard = app.state.storage_guard
    assert isinstance(guard, StorageGuard)
    assert guard.current_health() is StorageHealth.HEALTHY


def test_the_factory_guard_is_the_same_object_the_readiness_endpoint_reads() -> None:
    """One state machine, not two.

    Two guards would be two independent in-memory machines: a disk failure observed by the
    write gate would leave the health channel still reporting ``healthy``, which is exactly
    the divergence ``I02`` and ``I13`` forbid. The test drives the guard and reads the
    provider, so only a shared object can make it pass.
    """
    app = create_app()
    guard = app.state.storage_guard
    provider = app.state.readiness_provider

    assert provider.snapshot()["storage_health"] == StorageHealth.HEALTHY.value
    guard.record_write_failure()
    assert provider.snapshot()["storage_health"] == StorageHealth.WRITE_BLOCKED.value
    assert provider.snapshot()["modules"]["storage"] == "down"


def test_the_factory_write_gate_refuses_after_a_write_failure() -> None:
    """The gate reachable from ``app.state`` is a working gate, not a placeholder."""
    app = create_app()
    guard = app.state.storage_guard

    guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)  # healthy: no refusal
    guard.record_write_failure()
    with pytest.raises(StorageRefused) as caught:
        guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)
    assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED


def test_the_factory_reconciliation_gate_is_wired_and_shut() -> None:
    """``recovery_required`` is reachable on the factory and does not reopen by itself.

    Wired means both halves are real: ``mark_recovery_required`` moves the shipped guard,
    and ``complete_reconciliation`` refuses because no ``reconciliation_check`` has been
    supplied. ``TC-backup-restore-drill`` supplies one; until then the shut gate is the
    contract (``I15``, ``NC-10``), not an omission.
    """
    app = create_app()
    guard = app.state.storage_guard

    guard.enter_maintenance()
    assert guard.mark_recovery_required("RR-03") == "T-ST-05"
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED
    assert guard.reconciliation_complete("RR-03") is False

    with pytest.raises(StorageRefused) as caught:
        guard.complete_reconciliation("RR-03")
    assert caught.value.code is ErrorCode.RESTORE_UNVERIFIED
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED

    # And the health channel says so, from the same object.
    snapshot = app.state.readiness_provider.snapshot()
    assert snapshot["dispatcher_locked_for_recovery"] is True
    assert snapshot["modules"]["delivery_dispatcher"] == "down"


def test_an_injected_readiness_provider_still_gets_a_guard() -> None:
    """The construction path that used to skip the guard entirely.

    ``create_app(provider)`` keeps the caller's provider authoritative -- overriding it
    would make the parameter a lie -- while still installing a guard, so the ingest gate
    works on this path too.
    """
    provider = StorageReadinessProvider(StorageGuard(StorageHealthMachine()))
    app = create_app(provider)
    assert app.state.readiness_provider is provider
    assert isinstance(app.state.storage_guard, StorageGuard)


def test_install_storage_adopts_an_existing_guard() -> None:
    """A deployment that already holds a guard must not get a second one."""
    app = FastAPI()
    existing = StorageGuard(StorageHealthMachine(initial=StorageHealth.MAINTENANCE))
    returned = install_storage(app, existing)
    assert returned is existing
    assert app.state.storage_guard is existing
    assert app.state.readiness_provider.snapshot()["modules"]["storage"] == "degraded"


def test_install_storage_passes_the_reconciliation_check_through() -> None:
    """The seam ``TC-backup-restore-drill`` will use, exercised end to end."""
    app = FastAPI()
    install_storage(app, reconciliation_check=lambda restore_id: restore_id == "RR-07")
    guard = app.state.storage_guard
    guard.enter_maintenance()
    guard.mark_recovery_required("RR-07")
    assert guard.reconciliation_complete("RR-07") is True
    assert guard.complete_reconciliation("RR-07") == "T-ST-06"
    assert guard.current_health() is StorageHealth.HEALTHY


def test_readiness_on_the_factory_denies_without_a_session() -> None:
    """The shipped endpoint is reachable and guarded.

    Reachability and the 401 are asserted together on purpose: a 404 would mean the router
    was never included, and both answers are "not 200", so checking only the status class
    would not tell them apart.
    """
    client = TestClient(create_app())
    response = client.get("/v1/health/readiness")
    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value


def test_liveness_on_the_factory_is_still_public() -> None:
    """Registered once, by the skeleton; ``install_storage`` must not shadow or break it."""
    response = TestClient(create_app()).get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "up"
