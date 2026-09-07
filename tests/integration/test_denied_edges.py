"""E1/E2 — NC-01, NC-02 and the SC40/SC49 refusals, driven by the fixtures.

The fixtures under ``acceptance/fixtures/`` are the only oracle (SRC-PLAN §15): ``given``
rows are loaded, ``events`` are executed through the real service and HTTP layers, and
``expected`` codes and row counts are asserted. Nothing here builds a second data set, and
nothing here edits a fixture to make a test pass.

Scenarios covered: SC40 (unauthenticated / missing CSRF), SC41 (valid token on a forbidden
edge), SC49 (the default-deny sweep, for the edges this card's boundary enforces) and the
login half of SC51.
"""

from __future__ import annotations

import collections
import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from server.app.auth.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from server.app.auth.middleware import (
    SESSION_COOKIE_NAME,
    AuthScope,
    PrincipalKind,
    TokenRegistry,
    classify_denial,
    require_edge,
    require_module_edge,
)
from server.app.auth.service import (
    LOCKOUT_DURATION_MS,
    LOGIN_FAIL_THRESHOLD,
    AuthError,
    AuthService,
    hash_bearer_token,
    to_timestamp_utc_ms,
)
from server.app.db import create_sqlite_engine
from server.app.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_NAME = "owner"
OWNER_PASSWORD = "correct horse battery staple"
WIRE_HEADERS = {"X-Schema-Version": "0.3.0", "X-Request-Id": "01J0000000000000000000000Z"}

#: Which principal class a fixture's ``actor`` presents at the HTTP boundary. Modules that
#: run *inside* the server process are not on this list on purpose: they hold no HTTP
#: credential, so their forbidden edges are enforced by import rules and capability
#: sandboxes, not by this card (ruling R5-01 rows 2 and 3).
HTTP_PRINCIPAL_OF_ACTOR: dict[str, PrincipalKind] = {
    "MOD-web-ui": PrincipalKind.OWNER_SESSION,
    "MOD-x-collector": PrincipalKind.COLLECTOR,
    "MOD-analysis-worker": PrincipalKind.ANALYSIS_WORKER,
    "MOD-backup-cli": PrincipalKind.BACKUP_OPERATOR,
    "MOD-telegram-adapter": PrincipalKind.TELEGRAM_INGRESS,
    "EXT-telegram-api": PrincipalKind.ANONYMOUS,
}


@pytest.fixture(scope="module")
def ports() -> dict[str, dict[str, Any]]:
    document = yaml.safe_load((REPO_ROOT / "contracts" / "ports.yaml").read_text("utf-8"))
    return {op["operation_id"]: op for op in document["operations"]}


def _migrate(db_path: Path) -> None:
    """Run the real Alembic upgrade to revision ``0002``.

    The tests use the migration as their schema rather than hand-written DDL: a second
    source of schema truth beside ``server/migrations/versions/`` is exactly the drift the
    entity contract exists to prevent. The target is ``0002`` and not ``head`` so that a
    revision another Phase 1 card adds later cannot silently change what this card proves.
    Three cards branched off ``0001`` in parallel (``CR-TC-AUTH-06``), so ``head`` is
    ambiguous in this tree anyway.
    """
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "0002_tc_owner_auth_session")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


def test_the_bare_app_answers_401_not_500_on_a_protected_route() -> None:
    """Coordinator note CR-03: ``create_app()`` with no ``auth_service`` must still refuse
    cleanly.

    An unwired auth backend is a default-deny condition, not an internal error: the server
    cannot establish who is calling, so nobody is authenticated. Any router from another
    card that guards itself with ``require_owner_session`` therefore gets 401 on the bare
    factory -- ``/v1/health/readiness`` (``TC-storage-write-blocked-readiness``) is the live
    example asserted here alongside this card's own read route.
    """
    bare = TestClient(create_app(), base_url="https://testserver")
    assert not hasattr(bare.app.state, "auth_service")

    session_response = bare.get("/v1/auth/session", headers=WIRE_HEADERS)
    assert session_response.status_code == 401
    assert session_response.json()["code"] == ErrorCode.UNAUTHORIZED.value

    readiness = bare.get("/v1/health/readiness", headers=WIRE_HEADERS)
    assert readiness.status_code == 401, readiness.text
    assert readiness.status_code != 500


def test_install_auth_wires_a_service_onto_the_app(auth_service: AuthService) -> None:
    """The hook a deployment (or another card's test) uses to supply the backend."""
    from server.app.auth.router import install_auth

    app = create_app()
    install_auth(app, auth_service)
    client = TestClient(app, base_url="https://testserver")
    assert (
        client.post(
            "/v1/auth/login",
            json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
            headers=WIRE_HEADERS,
        ).status_code
        == 200
    )


def test_the_auth_revision_creates_only_its_own_table(tmp_path: Path) -> None:
    """``F-A3R1-01``: this card's revision must not define ``owner``.

    ``0002_base_entities`` is the sole ``CREATE TABLE owner``; this revision creates
    ``session`` and depends on that one, so ``owner`` is complete before ``session``
    references it whichever way the graph is walked. The constraint-set proof lives in
    ``tests/contract/test_schema_matches_entities.py``; this is the ownership half, asserted
    on the revision source itself so it cannot regress unnoticed.
    """
    source = (
        REPO_ROOT / "server" / "migrations" / "versions" / "0002_tc_owner_auth_session.py"
    ).read_text("utf-8")
    body = source.split('"""', 2)[2]  # skip the module docstring, which discusses the fix
    assert "CREATE TABLE owner" not in body
    assert "ALTER TABLE owner" not in body
    assert "CREATE TABLE session" in body
    assert 'down_revision: str | None = "0002_base_entities"' in body

    # And it really does build `session` on top of a complete `owner`.
    db_path = tmp_path / "auth-only.db"
    _migrate(db_path)
    connection = sqlite3.connect(db_path)
    try:
        owner_columns = {row[1] for row in connection.execute('PRAGMA table_info("owner")')}
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    finally:
        connection.close()
    assert {"failed_login_count", "locked_until", "password_hash"} <= owner_columns
    assert {"owner", "session"} <= tables


@pytest.fixture
def engine(tmp_path: Path) -> Any:
    db_path = tmp_path / "rr.db"
    _migrate(db_path)
    return create_sqlite_engine(db_path)


@pytest.fixture
def auth_service(engine: Any) -> AuthService:
    service = AuthService(engine)
    service.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    return service


@pytest.fixture
def client(auth_service: AuthService) -> TestClient:
    app = create_app()
    app.state.auth_service = auth_service
    app.state.token_registry = TokenRegistry(
        {
            "collector-token": PrincipalKind.COLLECTOR,
            "analysis-worker-token": PrincipalKind.ANALYSIS_WORKER,
            "backup-operator-token": PrincipalKind.BACKUP_OPERATOR,
        }
    )
    return TestClient(app, base_url="https://testserver")


def _login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers=WIRE_HEADERS,
    )
    assert response.status_code == 200, response.text
    return {
        SESSION_COOKIE_NAME: client.cookies[SESSION_COOKIE_NAME],
        CSRF_COOKIE_NAME: client.cookies[CSRF_COOKIE_NAME],
    }


def _count(engine: Any, table: str) -> int:
    with engine.begin() as connection:
        return int(connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())


# --------------------------------------------------------------------------------------
# SC51 — the login half of first-time setup
# --------------------------------------------------------------------------------------


def test_sc51_login_creates_exactly_one_owner_session(client, engine, fixture_loader) -> None:
    """``ui/sc51-first-time-setup.json``: one ``session`` row, no second ``owner`` row."""
    fixture = fixture_loader("ui/sc51-first-time-setup")
    assert fixture.data["given"]["rows"]["session"] == []
    assert len(fixture.data["given"]["rows"]["owner"]) == 1
    assert _count(engine, "session") == 0

    _login(client)

    assert _count(engine, "session") == 1
    assert _count(engine, "owner") == 1
    with engine.begin() as connection:
        row = connection.execute(text("SELECT owner_id, revoked_at, token_hash FROM session")).one()
    expected_shape = fixture.data["expected"]["rows"]["session"][0]
    assert set(expected_shape) >= {"owner_id", "revoked_at"}
    assert row[1] is None
    assert str(row[2]).startswith("sha256:")


def test_the_raw_session_token_is_never_stored(client, engine) -> None:
    """``ENT-session``: ``token_hash`` only. The cookie value must not appear in the row."""
    cookies = _login(client)
    with engine.begin() as connection:
        stored = connection.execute(text("SELECT token_hash FROM session")).scalar_one()
    assert cookies[SESSION_COOKIE_NAME] not in str(stored)


def test_the_password_is_never_stored_in_clear(auth_service, engine) -> None:
    with engine.begin() as connection:
        stored = connection.execute(text("SELECT password_hash FROM owner")).scalar_one()
    assert OWNER_PASSWORD not in str(stored)
    assert str(stored).startswith("$argon2id$")


def test_a_second_owner_row_is_a_database_error(engine) -> None:
    """``ENT-owner.singleton_guard``: one account, enforced by the schema (REQ-D05)."""
    AuthService(engine).bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at) VALUES ('01SECOND00000000000000000X', 1, 'other', 'UTC', "
                "'2026-09-07T00:00:00.000Z')"
            )
        )


# --------------------------------------------------------------------------------------
# SC40 — fixture recovery/h: unauthenticated, and missing CSRF
# --------------------------------------------------------------------------------------


def test_sc40_unauthenticated_owner_calls_are_unauthorized(client, engine, fixture_loader, ports):
    """Fixture ``recovery/h`` seq1..seq3: anonymous callers get ``UNAUTHORIZED`` and change
    no rows. Executed through :func:`classify_denial` -- the same decision the HTTP
    dependencies make -- plus a real request for the one owner route that exists today."""
    fixture = fixture_loader("recovery/h-unauthenticated-owner-api")
    assert fixture.data["given"]["session"] is None

    before = _count(engine, "session")
    for event in fixture.events[:3]:
        port = ports[event["operation"]]
        code = classify_denial(
            AuthScope(port["auth_scope"]),
            mutation=bool(port["mutation"]),
            principal=PrincipalKind.ANONYMOUS,
            csrf_ok=False,
        )
        expected = fixture.data["expected"][f"seq{event['seq']}"]["error_code"]
        assert code is not None and code.value == expected, event["operation"]
    assert fixture.data["expected"]["seq3"]["rows_changed"] == 0

    response = client.get("/v1/auth/session", headers=WIRE_HEADERS)
    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value
    assert _count(engine, "session") == before


def test_sc40_missing_csrf_is_csrf_rejected_not_forbidden_edge(client, engine) -> None:
    """Card §10 ``SG-CSRF`` and ``acceptance/scenarios.yaml`` SC40 ``oracle_vi``:
    403 ``CSRF_REJECTED``, the session survives, and no row changes."""
    _login(client)
    before = _count(engine, "session")

    response = client.post("/v1/auth/logout", headers=WIRE_HEADERS)

    assert response.status_code == 403
    body = response.json()
    assert body["code"] == ErrorCode.CSRF_REJECTED.value
    assert body["code"] != ErrorCode.FORBIDDEN_EDGE.value
    assert body["scope"] == "request"
    assert body["retry_class"] == "none"
    assert _count(engine, "session") == before
    # The session is NOT revoked: the very next authenticated read still works.
    assert client.get("/v1/auth/session", headers=WIRE_HEADERS).status_code == 200


def test_sc40_mismatched_csrf_is_also_csrf_rejected(client) -> None:
    _login(client)
    response = client.post("/v1/auth/logout", headers={**WIRE_HEADERS, CSRF_HEADER_NAME: "0" * 32})
    assert response.status_code == 403
    assert response.json()["code"] == ErrorCode.CSRF_REJECTED.value
    assert client.get("/v1/auth/session", headers=WIRE_HEADERS).status_code == 200


def test_logout_with_cookie_and_csrf_succeeds_and_revokes(client, engine) -> None:
    cookies = _login(client)
    response = client.post(
        "/v1/auth/logout",
        headers={**WIRE_HEADERS, CSRF_HEADER_NAME: cookies[CSRF_COOKIE_NAME]},
    )
    assert response.status_code == 204
    with engine.begin() as connection:
        assert connection.execute(text("SELECT revoked_at FROM session")).scalar_one() is not None


def test_a_revoked_session_is_unauthorized_on_the_next_request(client, engine) -> None:
    """``ports.yaml`` ``auth.logout`` scenario note: after logout every request carrying the
    revoked session falls into the SC40 branch."""
    cookies = _login(client)
    client.post(
        "/v1/auth/logout",
        headers={**WIRE_HEADERS, CSRF_HEADER_NAME: cookies[CSRF_COOKIE_NAME]},
    )
    client.cookies.set(SESSION_COOKIE_NAME, cookies[SESSION_COOKIE_NAME])
    assert client.get("/v1/auth/session", headers=WIRE_HEADERS).status_code == 401


def test_an_expired_session_is_unauthorized_and_mutates_nothing(auth_service, engine) -> None:
    """Card §6: "phiên hết hạn giữa hai request ⇒ 401, không mutation một phần"."""
    result = auth_service.login(OWNER_NAME, OWNER_PASSWORD)
    past = datetime.now(UTC) - timedelta(minutes=1)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE session SET expires_at = :t"), {"t": to_timestamp_utc_ms(past)}
        )
    with pytest.raises(AuthError) as caught:
        auth_service.authenticate(result.session_token)
    assert caught.value.code is ErrorCode.UNAUTHORIZED


@pytest.mark.xfail(
    reason="CR-TC-AUTH-01: recovery/h seq4 still pins FORBIDDEN_EDGE for a missing CSRF "
    "token. openapi.yaml (post-FIX1), contracts/errors.yaml, acceptance/scenarios.yaml "
    "SC40 and the card's ruling R5-01 all say CSRF_REJECTED, and the fixture's own "
    "open_question CR-PC08-03 is the request to change it. The fixture is read-only to "
    "this card, so the drift is recorded as a failing expectation, not edited away.",
    strict=True,
)
def test_fixture_h_seq4_literal_expectation(fixture_loader) -> None:
    fixture = fixture_loader("recovery/h-unauthenticated-owner-api")
    assert fixture.data["expected"]["seq4"]["error_code"] == ErrorCode.CSRF_REJECTED.value


def test_fixture_h_seq4_status_and_row_count_still_hold(fixture_loader) -> None:
    """The parts of seq4 that are *not* in dispute: 403 and zero rows changed."""
    seq4 = fixture_loader("recovery/h-unauthenticated-owner-api").data["expected"]["seq4"]
    assert seq4["http_status"] == 403
    assert seq4["rows_changed"] == 0


# --------------------------------------------------------------------------------------
# SC41 / NC-01 / NC-02 — fixture recovery/i: a valid token on a forbidden edge
# --------------------------------------------------------------------------------------


def test_sc41_collector_token_on_a_forbidden_edge_is_unauthorized(fixture_loader, ports) -> None:
    """``recovery/i`` seq1 (``save.create``) and seq2 (``tag.update``): the token is valid,
    its class is simply not admitted -> ``UNAUTHORIZED`` (401), not ``FORBIDDEN_EDGE``."""
    fixture = fixture_loader("recovery/i-collector-token-calls-save")
    for event in fixture.events:
        port = ports[event["operation"]]
        code = classify_denial(
            AuthScope(port["auth_scope"]),
            mutation=bool(port["mutation"]),
            principal=PrincipalKind.COLLECTOR,
            csrf_ok=False,
        )
        expected = fixture.data["expected"][f"seq{event['seq']}"]
        if event["edge_assertion"] == "forbidden":
            assert code is not None and code.value == expected["error_code"], event["operation"]
        else:
            # seq3: the collector's one legitimate path stays open.
            assert code is None, event["operation"]
            assert expected["result"] == "committed"


def test_a_worker_token_cannot_borrow_the_collector_dependency(client) -> None:
    """The dependency other cards import, exercised directly: a genuine analysis-worker
    token presented to a collector-guarded route is ``UNAUTHORIZED``."""
    from server.app.auth.middleware import require_collector_token

    request = _fake_request(client, {"Authorization": "Bearer analysis-worker-token"})
    with pytest.raises(AuthError) as caught:
        require_collector_token(request)
    assert caught.value.code is ErrorCode.UNAUTHORIZED
    assert caught.value.http_status == 401


def test_an_unknown_bearer_token_is_unauthorized(client) -> None:
    from server.app.auth.middleware import require_backup_operator_token

    request = _fake_request(client, {"Authorization": "Bearer not-a-real-token"})
    with pytest.raises(AuthError) as caught:
        require_backup_operator_token(request)
    assert caught.value.code is ErrorCode.UNAUTHORIZED


def test_the_browser_session_cannot_reach_a_backup_route(ports) -> None:
    """``CR-PC08-02``: ``backup.*`` admits ``backupOperatorToken`` and nothing else."""
    backup_ops = [op for op in ports.values() if op["operation_id"].startswith("backup.")]
    assert backup_ops
    for port in backup_ops:
        scope = AuthScope(port["auth_scope"])
        assert scope is AuthScope.BACKUP_OPERATOR
        for intruder in (
            PrincipalKind.OWNER_SESSION,
            PrincipalKind.COLLECTOR,
            PrincipalKind.ANALYSIS_WORKER,
            PrincipalKind.TELEGRAM_INGRESS,
            PrincipalKind.ANONYMOUS,
        ):
            code = classify_denial(
                scope, mutation=bool(port["mutation"]), principal=intruder, csrf_ok=True
            )
            assert code is ErrorCode.UNAUTHORIZED, (port["operation_id"], intruder)
        assert (
            classify_denial(
                scope,
                mutation=bool(port["mutation"]),
                principal=PrincipalKind.BACKUP_OPERATOR,
                csrf_ok=False,
            )
            is None
        )


# --------------------------------------------------------------------------------------
# SC49 — the 36-edge default-deny sweep, for the edges this boundary owns
# --------------------------------------------------------------------------------------


def _sweep_events(fixture_loader: Any) -> list[dict[str, Any]]:
    fixture = fixture_loader("boundary/a-default-deny-sweep-36-edges")
    events = fixture.events
    assert len(events) == 36, "the sweep must stay exhaustive"
    return events


def _edge_level_code(event: dict[str, Any]) -> str:
    """The code the *edge* layer must produce.

    Five rows in the fixture are two-level: ``expected_error_code`` is what the audit log
    shows at the path level (``UNAUTHORIZED_COMMAND`` for the Telegram ingress,
    ``RESTORE_UNVERIFIED`` for the storage-health guard) while
    ``expected_error_code_edge_class`` is the verdict about the edge itself. The fixture's
    own ``two_level_note_vi`` says the two describe different layers and do not conflict.
    """
    return str(event.get("expected_error_code_edge_class", event["expected_error_code"]))


#: The one code per edge this card's boundary is responsible for producing, and the reason.
#: Every one of the 36 rows appears in exactly one of the three buckets below -- there is no
#: floor, no ``>=``, and no row is unaccounted for (F-A3R1-08).
_UNAUTHORIZED = ErrorCode.UNAUTHORIZED.value
_FORBIDDEN_EDGE = ErrorCode.FORBIDDEN_EDGE.value
_CAPABILITY_DENIED = ErrorCode.CAPABILITY_DENIED.value


def test_sc49_every_sweep_event_is_classified_exactly_once(fixture_loader) -> None:
    """The partition itself, asserted before anything is exercised.

    A coverage claim is only worth what its denominator is worth, so the denominator is
    pinned here: 36 rows, split into the two buckets this layer must refuse and the one it
    provably cannot reach.
    """
    events = _sweep_events(fixture_loader)
    buckets = collections.Counter(_edge_level_code(event) for event in events)
    assert buckets == {
        _UNAUTHORIZED: 12,
        _FORBIDDEN_EDGE: 10,
        _CAPABILITY_DENIED: 14,
    }, buckets
    assert sum(buckets.values()) == 36


def test_sc49_all_twelve_unauthorized_edges_are_refused_by_the_auth_boundary(
    fixture_loader, ports
) -> None:
    """Every edge-level ``UNAUTHORIZED`` row, exercised through the real scheme decision.

    No exclusions: all twelve are HTTP calls by a principal class the operation's
    ``auth_scope`` does not admit, which is exactly what this card's boundary decides.
    """
    checked: list[str] = []
    for event in _sweep_events(fixture_loader):
        if _edge_level_code(event) != _UNAUTHORIZED:
            continue
        operation = event["operation"]
        assert operation in ports, event["forbidden_edge_ref"]
        port = ports[operation]
        principal = HTTP_PRINCIPAL_OF_ACTOR[event["actor"]]
        code = classify_denial(
            AuthScope(port["auth_scope"]),
            mutation=bool(port["mutation"]),
            principal=principal,
            csrf_ok=True,
        )
        assert code is not None, event["forbidden_edge_ref"]
        assert code.value == _UNAUTHORIZED, (event["forbidden_edge_ref"], code.value)
        checked.append(event["forbidden_edge_ref"])
    assert len(checked) == 12, checked


def test_sc49_all_ten_forbidden_edges_are_refused_by_the_service_layer_guard(
    fixture_loader, ports
) -> None:
    """Every edge-level ``FORBIDDEN_EDGE`` row, exercised through ``require_edge``.

    Eight rows name an operation and go through the per-operation registry; the two that
    name none (``FE-08``, ``FE-26``, both ``in_process_call``) go through the module-pair
    registry. Both raise from real code -- the same functions another card's service calls,
    not a test-local reimplementation.
    """
    checked: list[str] = []
    for event in _sweep_events(fixture_loader):
        if _edge_level_code(event) != _FORBIDDEN_EDGE:
            continue
        ref = event["forbidden_edge_ref"]
        operation = event.get("operation")
        with pytest.raises(AuthError) as caught:
            if operation is None:
                assert event["event_type"] == "in_process_call", ref
                require_module_edge(event["actor"], event["callee"], edge_ref=ref)
            else:
                assert operation in ports, ref
                require_edge(OperationId(operation), event["actor"], edge_ref=ref)
        assert caught.value.code is ErrorCode.FORBIDDEN_EDGE, ref
        assert caught.value.http_status == 403, ref
        assert caught.value.details_safe["caller_module"] == event["actor"], ref
        assert caught.value.details_safe["forbidden_edge_ref"] == ref
        checked.append(ref)
    assert len(checked) == 10, checked


def test_sc49_the_allowed_side_of_the_same_guard_is_not_refused(ports) -> None:
    """A default-deny check that refuses everything proves nothing.

    Every declared caller of every operation must pass ``require_edge``; the two module
    pairs that are allowed for one operation and forbidden for another (``FE-28``,
    ``FE-33``) are named explicitly, because a pair-level check alone would let them
    through and this is where that would show.
    """
    for operation_id, port in ports.items():
        for caller in port["caller_modules"]:
            require_edge(OperationId(operation_id), caller)

    # FE-28: report-service may enqueue analysis tasks but not submit a result.
    require_edge(OperationId.ANALYSIS_ENQUEUE_TASKS, "MOD-report-service")
    with pytest.raises(AuthError):
        require_edge(OperationId.ANALYSIS_SUBMIT_RESULT, "MOD-report-service")
    # FE-33: the Telegram adapter reaches job-service for the three allowed commands only.
    with pytest.raises(AuthError):
        require_edge(OperationId.RUN_RESUME, "MOD-telegram-adapter")


#: The 14 rows this layer provably cannot decide, each with the mechanism `modules.yaml`
#: names as the enforcer and the card that will have to prove it. Recorded as
#: NOT_TESTABLE_AT_THIS_LAYER -- never counted as passed (F-A3R1-08).
NOT_TESTABLE_AT_THIS_LAYER: dict[str, str] = {
    "FE-01": "browser holds no SQLite driver and no route to the volume (NC-11)",
    "FE-03": "browser CSP/egress; the page holds no provider key to call with (NC-12)",
    "FE-04": "browser CSP/egress; MOD-web-ui must not reach api.telegram.org directly",
    "FE-05": "collector process has no SQLite driver for the server database (NC-05)",
    "FE-10": "collector process has no egress to api.telegram.org",
    "FE-15": "analysis worker runs on the personal machine; no route to the server volume",
    "FE-16": "AI adapter egress is the configured provider endpoint only (NC-04)",
    "FE-17": "AI adapter has no browser and no route to x.com",
    "FE-18": "AI adapter process holds no database handle",
    "FE-19": "AI adapter egress excludes arXiv; a model may not request a fetch (NC-07)",
    "FE-20": "research connector drives no browser (D08 API-only)",
    "FE-21": "no Chrome on the server image; the profile lives on the personal machine (NC-08)",
    "FE-22": "embedding service runs on the server with no provider egress (D50)",
    "FE-27": "report service has no egress to api.telegram.org; delivery owns that edge",
}

#: The three mechanisms `contracts/modules.yaml` uses for the rows above. None of them is
#: an HTTP check, which is precisely why this card cannot decide them.
_NON_HTTP_MECHANISMS = frozenset(
    {"ENF-process-capability", "ENF-network-egress-allowlist", "ENF-import-rule"}
)


def test_sc49_capability_denied_rows_are_recorded_not_testable_at_this_layer(
    fixture_loader,
) -> None:
    """The honest half of the coverage claim.

    ``CAPABILITY_DENIED`` is a process/network/filesystem verdict (ruling R5-01 row 3): it
    is produced by a sandbox and a connection count, not by an HTTP handler. These rows are
    listed by name with their enforcing mechanism so the gap is measurable, and this test
    asserts they are **not** silently absorbed into the passing counts above.
    """
    events = _sweep_events(fixture_loader)
    observed = {
        event["forbidden_edge_ref"]
        for event in events
        if _edge_level_code(event) == _CAPABILITY_DENIED
    }
    assert observed == set(NOT_TESTABLE_AT_THIS_LAYER), observed.symmetric_difference(
        NOT_TESTABLE_AT_THIS_LAYER
    )
    for event in events:
        ref = event["forbidden_edge_ref"]
        if ref not in NOT_TESTABLE_AT_THIS_LAYER:
            continue
        # The exclusion is only legitimate if the contract itself enforces the row by a
        # non-HTTP mechanism. Read from the fixture, not transcribed into the table above.
        mechanisms = set(event["enforcement"])
        assert mechanisms <= _NON_HTTP_MECHANISMS, (ref, sorted(mechanisms))
        assert "ENF-api-auth-test" not in mechanisms, (
            f"{ref} names ENF-api-auth-test, so it is reachable here and must be asserted, "
            "not excused"
        )
        assert NOT_TESTABLE_AT_THIS_LAYER[ref], ref


def test_sc49_the_three_buckets_partition_the_sweep(fixture_loader) -> None:
    """Closing the loop: 12 + 10 + 14 = 36, with no row in two buckets and none in none."""
    events = _sweep_events(fixture_loader)
    refs = [event["forbidden_edge_ref"] for event in events]
    assert len(set(refs)) == 36
    excluded = set(NOT_TESTABLE_AT_THIS_LAYER)
    asserted = {
        event["forbidden_edge_ref"]
        for event in events
        if _edge_level_code(event) in {_UNAUTHORIZED, _FORBIDDEN_EDGE}
    }
    assert asserted & excluded == set()
    assert asserted | excluded == set(refs)
    assert (len(asserted), len(excluded)) == (22, 14)


# --------------------------------------------------------------------------------------
# F-A3R1-12 — bearer tokens are stored hashed and compared in constant time
# --------------------------------------------------------------------------------------


def test_the_token_registry_keeps_no_plaintext(client) -> None:
    """``contracts/ops/secrets.md`` §3: "server lưu ``sha256``, không lưu bản rõ"."""
    registry = TokenRegistry({"collector-token": PrincipalKind.COLLECTOR})
    serialised = repr(registry.__dict__)
    assert "collector-token" not in serialised
    assert hash_bearer_token("collector-token") in serialised
    assert registry.kind_for("collector-token") is PrincipalKind.COLLECTOR
    assert registry.kind_for("collector-token ") is None
    assert registry.kind_for("") is None


def test_the_token_registry_can_be_built_from_stored_hashes_alone() -> None:
    """The real operator path: the server is configured with digests, never with a token."""
    digest = hash_bearer_token("backup-operator-token")
    registry = TokenRegistry.from_hashes({digest: PrincipalKind.BACKUP_OPERATOR})
    assert registry.kind_for("backup-operator-token") is PrincipalKind.BACKUP_OPERATOR
    assert registry.kind_for("something-else") is None


# --------------------------------------------------------------------------------------
# Lockout and wire hygiene
# --------------------------------------------------------------------------------------


def test_five_failed_logins_lock_the_account(client) -> None:
    """``contracts/ops/secrets.md`` §2.3: 5 failures -> ``RATE_LIMITED`` + retry."""
    for _ in range(LOGIN_FAIL_THRESHOLD):
        response = client.post(
            "/v1/auth/login",
            json={"username": OWNER_NAME, "password": "wrong password entirely"},
            headers=WIRE_HEADERS,
        )
        assert response.status_code == 401
        assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value

    locked = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers=WIRE_HEADERS,
    )
    assert locked.status_code == 429
    body = locked.json()
    assert body["code"] == ErrorCode.RATE_LIMITED.value
    assert body["retry_after_ms"] > 0
    assert "Retry-After" in locked.headers


def test_the_lockout_counter_survives_a_process_restart(engine, tmp_path) -> None:
    """``F-A3R1-06``: the counter is on the ``owner`` row, not in process memory.

    "Restart" is modelled the only way that proves anything: the ``AuthService`` and the
    whole app object are **thrown away** and rebuilt from the same database file. A counter
    living in a deque on the old object would be gone; one living in
    ``owner.failed_login_count`` is not.
    """
    first = AuthService(engine)
    first.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    for _ in range(LOGIN_FAIL_THRESHOLD - 1):
        with pytest.raises(AuthError) as failure:
            first.login(OWNER_NAME, "wrong password entirely")
        assert failure.value.code is ErrorCode.UNAUTHORIZED

    with engine.begin() as connection:
        stored = connection.execute(text("SELECT failed_login_count FROM owner")).scalar_one()
    assert stored == LOGIN_FAIL_THRESHOLD - 1

    # --- restart: nothing of the old service survives except the database file ---
    del first
    second = AuthService(engine)

    with pytest.raises(AuthError) as fifth:
        second.login(OWNER_NAME, "wrong password entirely")
    assert fifth.value.code is ErrorCode.UNAUTHORIZED

    third = AuthService(engine)
    with pytest.raises(AuthError) as locked:
        third.login(OWNER_NAME, OWNER_PASSWORD)
    assert locked.value.code is ErrorCode.RATE_LIMITED
    assert locked.value.retry_after_ms is not None
    assert 0 < locked.value.retry_after_ms <= LOCKOUT_DURATION_MS

    with engine.begin() as connection:
        until = connection.execute(text("SELECT locked_until FROM owner")).scalar_one()
    assert until is not None


def test_a_lock_expires_and_a_correct_password_then_works(engine) -> None:
    """A lockout is a delay, not a lockout of the owner from their own system."""
    service = AuthService(engine)
    service.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    for _ in range(LOGIN_FAIL_THRESHOLD):
        with pytest.raises(AuthError):
            service.login(OWNER_NAME, "wrong password entirely")

    with pytest.raises(AuthError) as locked:
        service.login(OWNER_NAME, OWNER_PASSWORD)
    assert locked.value.code is ErrorCode.RATE_LIMITED

    later = datetime.now(UTC) + timedelta(milliseconds=LOCKOUT_DURATION_MS + 1000)
    result = service.login(OWNER_NAME, OWNER_PASSWORD, now=later)
    assert result.session_token

    with engine.begin() as connection:
        count, until = connection.execute(
            text("SELECT failed_login_count, locked_until FROM owner")
        ).one()
    assert (count, until) == (0, None)


def test_a_successful_login_clears_the_failure_counter(engine) -> None:
    """entities.yaml ``failed_login_count``: "đăng nhập đúng đặt lại về 0"."""
    service = AuthService(engine)
    service.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    for _ in range(LOGIN_FAIL_THRESHOLD - 1):
        with pytest.raises(AuthError):
            service.login(OWNER_NAME, "wrong password entirely")
    service.login(OWNER_NAME, OWNER_PASSWORD)
    with engine.begin() as connection:
        assert connection.execute(text("SELECT failed_login_count FROM owner")).scalar_one() == 0


def test_a_locked_account_does_not_accumulate_further_failures(engine) -> None:
    """While a lock is in force nothing is counted -- the refusal is the whole response."""
    service = AuthService(engine)
    service.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    for _ in range(LOGIN_FAIL_THRESHOLD):
        with pytest.raises(AuthError):
            service.login(OWNER_NAME, "wrong password entirely")
    with engine.begin() as connection:
        before = connection.execute(
            text("SELECT failed_login_count, locked_until FROM owner")
        ).one()
    for _ in range(3):
        with pytest.raises(AuthError) as caught:
            service.login(OWNER_NAME, "wrong password entirely")
        assert caught.value.code is ErrorCode.RATE_LIMITED
    with engine.begin() as connection:
        after = connection.execute(text("SELECT failed_login_count, locked_until FROM owner")).one()
    assert before == after


def test_an_unknown_account_is_indistinguishable_from_a_wrong_password(client) -> None:
    """secrets.md §2.3: the answer must not reveal whether the account exists."""
    wrong_password = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": "wrong password entirely"},
        headers=WIRE_HEADERS,
    )
    unknown_account = client.post(
        "/v1/auth/login",
        json={"username": "somebody-else", "password": "wrong password entirely"},
        headers=WIRE_HEADERS,
    )
    assert wrong_password.status_code == unknown_account.status_code == 401
    assert wrong_password.json()["message_safe"] == unknown_account.json()["message_safe"]


def test_the_error_envelope_never_leaks_a_credential(client) -> None:
    """SRC-PLAN §5.1 / errors.yaml ``forbidden_content_vi``."""
    cookies = _login(client)
    body = client.post("/v1/auth/logout", headers=WIRE_HEADERS).text
    assert cookies[SESSION_COOKIE_NAME] not in body
    assert cookies[CSRF_COOKIE_NAME] not in body
    assert OWNER_PASSWORD not in body
    assert "Traceback" not in body


def test_the_session_cookie_is_httponly_secure_samesite_and_csrf_is_readable(client) -> None:
    """``contracts/ops/secrets.md`` §2.3 and §2.4: HttpOnly + Secure + SameSite=Lax for the
    session; ``rr_csrf`` deliberately readable so the page can echo it."""
    response = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers=WIRE_HEADERS,
    )
    session_cookie = next(
        value
        for key, value in response.headers.items()
        if key.lower() == "set-cookie" and value.startswith(f"{SESSION_COOKIE_NAME}=")
    )
    all_cookies = response.headers.get_list("set-cookie")
    csrf_cookie = next(c for c in all_cookies if c.startswith(f"{CSRF_COOKIE_NAME}="))
    assert "HttpOnly" in session_cookie
    assert "Secure" in session_cookie
    assert "SameSite=lax" in session_cookie.replace("SameSite=Lax", "SameSite=lax")
    assert "HttpOnly" not in csrf_cookie
    assert "Secure" in csrf_cookie


def test_missing_wire_headers_are_validation_error(client) -> None:
    """``X-Schema-Version`` and ``X-Request-Id`` are required parameters on every path."""
    response = client.post(
        "/v1/auth/login", json={"username": OWNER_NAME, "password": OWNER_PASSWORD}
    )
    assert response.status_code == 422
    assert response.json()["code"] == ErrorCode.VALIDATION_ERROR.value


def test_a_major_schema_version_mismatch_is_rejected(client) -> None:
    response = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers={**WIRE_HEADERS, "X-Schema-Version": "9.0.0"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["details_safe"]["violation_kind"] == "schema_version_unsupported"


@pytest.mark.xfail(
    reason="pending TC-storage-write-blocked-readiness: `storage.get_health` is consumed "
    "through the StorageHealthPort but no implementation is wired yet, so the "
    "write_blocked pre-check cannot be exercised end to end from this card.",
    strict=False,
)
def test_login_is_refused_while_storage_is_write_blocked(engine) -> None:
    class _Blocked:
        def get_health(self) -> str:
            return "write_blocked"

    service = AuthService(engine, storage_health=_Blocked())
    with pytest.raises(AuthError) as caught:
        service.login(OWNER_NAME, OWNER_PASSWORD)
    assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert caught.value.http_status == 503
    raise AssertionError("integration with the real health channel is still NOT_RUN")


def _fake_request(client: TestClient, headers: dict[str, str]) -> Any:
    """A minimal Starlette request carrying only what the dependency reads."""
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "query_string": b"",
        "app": client.app,
    }
    return Request(scope)
