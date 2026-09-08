"""Smoke tests for the server skeleton.

These prove what the *skeleton* owns and claim nothing more: the app boots; the
DB-independent liveness channel answers with only the two permitted fields and without a
session; the readiness route exists but denies an unauthenticated caller; and every
connection the engine factory hands out really has the pragmas the contracts depend on.

Business behaviour is not exercised here. It is owned and proved by the task cards
(`agent-tasks/TC-*.md`) and their own tests under `tests/contract/` and
`tests/integration/`; this module deliberately stays at the boot-and-boundary level so a
failure here means the skeleton broke, not that a feature regressed.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.db.engine import SQLITE_PRAGMAS, create_sqlite_engine, read_pragmas, session_scope
from server.app.main import StubReadinessProvider, create_app


@pytest.fixture()
def app() -> FastAPI:
    """The bare application factory: no session dependency, no readiness provider injected.

    Exposed separately from :func:`client` because ``TestClient.app`` is typed as the ASGI
    callable, which has no ``.title`` or ``.routes``. Reaching for those through the client
    would need a cast that lies about what the object is; a second fixture keeps the real
    type all the way through.
    """
    return create_app()


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_app_boots(app: FastAPI) -> None:
    assert app.title.startswith("Research Radar")


def test_liveness_returns_only_up_and_schema_version(client: TestClient) -> None:
    """HC-01: liveness returns `up` plus the schema version, and nothing else.

    The negative half matters more than the positive: the contract forbids leaking
    configuration, provider names, chat ids or business data through this channel, so the
    test asserts the exact key set, not just the presence of `status`.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "up", "schema_version": CONTRACT_SCHEMA_VERSION}
    assert response.headers["X-Schema-Version"] == CONTRACT_SCHEMA_VERSION


def test_readiness_is_routed_and_denies_an_unauthenticated_caller(
    client: TestClient, app: FastAPI
) -> None:
    """`health.get_readiness` is routed, and the bare app factory refuses it with 401.

    History of this test, kept deliberately. In Phase 0 it was a tripwire asserting **404**:
    readiness was not this packet's to build, and a 404 proved the ownership boundary had
    not been crossed by accident. Phase 1 crossed it on purpose —
    `agent-tasks/TC-storage-write-blocked-readiness.md` now owns the route and
    `server/app/health/router.py`, so the tripwire had done its job and had to be inverted
    rather than deleted: a boundary test that stops asserting anything is worse than none.

    What replaces it is the Phase 1 truth, and it is two claims, not one:

    * the route **exists** (so `contracts/http/openapi.yaml` `/v1/health/readiness` has an
      implementation, and a future refactor that drops it fails here);
    * on the **bare factory** — no owner session dependency injected — it answers **401**,
      not 200 and not 404. `contracts/http/openapi.yaml` gives this path the
      `ownerSessionCookie` scheme while `/healthz` carries `security: []`, and
      `agent-tasks/TC-owner-auth-session.md` owns the session half. Until a session
      dependency is supplied the health router's fallback **denies**; defaulting to allow
      would publish per-module internals — storage health, dispatcher recovery lock,
      embedding generation, workers online — on an unauthenticated endpoint.

    The refusal code is checked too. `contracts/errors.yaml` distinguishes `UNAUTHORIZED`
    (caller proved no identity) from `FORBIDDEN_EDGE` (identity fine, edge not allowed);
    `agent-tasks/README.md` §5.2 states plainly that returning the wrong code is a FAIL in
    its own right, not merely wrong behaviour.
    """
    response = client.get("/v1/health/readiness")
    assert response.status_code == 401, "readiness must be routed and must deny by default"
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value

    routed = {getattr(route, "operation_id", None) for route in app.routes}
    assert OperationId.HEALTH_GET_READINESS.value in routed
    assert OperationId.HEALTH_GET_LIVENESS.value in routed


def test_liveness_stays_open_while_readiness_is_locked(client: TestClient) -> None:
    """The two health channels are independent, and only one of them is authenticated.

    `contracts/state/storage.yaml` rule HC-01: liveness must answer even when the database
    cannot be read or written — which also means it must not sit behind a session, since a
    session lookup is a database read. HC-02 puts readiness behind the owner session
    because it exposes per-module internals. Asserting both in one place keeps a future
    "let's protect the health endpoints" change from silently locking liveness too.
    """
    assert client.get("/healthz").status_code == 200
    assert client.get("/v1/health/readiness").status_code == 401


def test_stub_readiness_provider_reports_not_computed() -> None:
    """It must not claim `healthy`, and `storage_health` has no `unknown` member."""
    snapshot = StubReadinessProvider().snapshot()
    assert snapshot["storage"] is None


def _pragma_int(pragmas: dict[str, object], name: str) -> int:
    """Read one pragma back as an int, asserting SQLite really returned a number.

    ``read_pragmas`` is typed ``dict[str, object]`` because ``PRAGMA`` returns whatever the
    pragma's own type is -- a string for ``journal_mode``, an integer for the other three.
    Narrowing with an ``isinstance`` assertion rather than a cast means the test also fails
    (loudly, here) if a pragma ever starts coming back as text, which would silently make
    ``int(...)`` comparisons meaningless.
    """
    value = pragmas[name]
    assert isinstance(value, int), f"PRAGMA {name} returned {value!r}, expected an integer"
    return value


def test_engine_applies_every_pragma(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "smoke.db")
    with engine.connect() as connection:
        pragmas = read_pragmas(connection)
    assert str(pragmas["journal_mode"]).lower() == "wal"
    assert _pragma_int(pragmas, "foreign_keys") == 1
    assert _pragma_int(pragmas, "busy_timeout") == 5000
    assert _pragma_int(pragmas, "synchronous") == 1  # NORMAL
    assert len(SQLITE_PRAGMAS) == 4


def test_foreign_keys_are_actually_enforced(tmp_path: Path) -> None:
    """A pragma that is set but not enforced would be worse than no pragma at all."""
    from sqlalchemy import text

    engine = create_sqlite_engine(tmp_path / "fk.db")
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
        connection.execute(
            text(
                "CREATE TABLE child (id INTEGER PRIMARY KEY, parent_id INTEGER "
                "REFERENCES parent(id))"
            )
        )
    with pytest.raises(Exception) as excinfo, session_scope(engine) as connection:
        connection.execute(text("INSERT INTO child (id, parent_id) VALUES (1, 999)"))
    assert "FOREIGN KEY" in str(excinfo.value).upper()


def test_sqlite_supports_the_backup_api() -> None:
    """AMD-B11 / ADR-0005 depend on `sqlite3.Connection.backup` existing."""
    assert hasattr(sqlite3.Connection, "backup")
