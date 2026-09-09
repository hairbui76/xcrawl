"""The composition root, proved end to end on a blank database.

What this file is for
---------------------
``docs/owner-runbook.md`` gap ``G-2``: every card was tested against its own harness, and
every harness assigned ``app.state.*`` by hand. Nothing tested the path the Owner actually
takes -- migrate, bootstrap, start the real factory, log in -- and on that path
``auth.login`` returned 500.

So the rule for this module is: **no monkeypatching, no hand-assigned ``app.state``, no
fakes.** It runs ``rr_admin migrate``, ``rr_admin bootstrap-owner`` and
``server.app.wiring.wire()`` exactly as a deployment does, then drives HTTP through the
resulting application. If it passes, the documented sequence works; if it were allowed to
patch anything, it would prove only that the patch works.

The sequence asserted here is the runbook's §§2-4 in order:

1. blank directory -> ``migrate`` -> schema at ``head``;
2. ``bootstrap-owner`` -> exactly one owner row, credentialed, password never echoed;
3. the real factory, wired -> ``POST /v1/auth/login`` **200** with a session cookie and a
   CSRF cookie;
4. ``GET /v1/health/readiness`` **200** for that session (401 before it);
5. ``GET /v1/runs`` **200** with an empty list -- the route that needs ``job_context``, i.e.
   the one that proves an owner-scoped context was really built.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from server.app.settings import MEMORY_PATH, Settings, load_settings
from server.app.wiring import build_runtime, resolve_owner_id, wire

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN = REPO_ROOT / "tools" / "rr_admin.py"

OWNER_NAME = "Owner"
OWNER_PASSWORD = "correct horse battery staple"

#: Both are mandatory on every request (`contracts/http/openapi.yaml` parameters).
WIRE_HEADERS = {
    "X-Schema-Version": "0.3.0",
    "X-Request-Id": "01J0000000000000000000000Z",
}


def _settings(tmp_path: Path) -> Settings:
    """A Settings pointing at a fresh directory -- no environment mutation, no globals."""
    return Settings(
        database_path=tmp_path / "research-radar.db",
        data_dir=tmp_path,
        timezone_iana="Asia/Ho_Chi_Minh",
        schedule_slots=("08:00", "20:00"),
        provider_config_path=REPO_ROOT / "contracts" / "ai" / "providers.yaml",
        telegram_webhook_secret=None,
        collector_token_sha256=None,
        analysis_worker_token_sha256=None,
        backup_operator_token_sha256=None,
    )


def _run_admin(args: list[str], tmp_path: Path, stdin: str | None = None) -> str:
    """Invoke ``tools/rr_admin.py`` as a **subprocess**, from a directory that is not the repo.

    A subprocess rather than an import, and ``cwd=tmp_path`` rather than the repo root, so the
    test exercises the two things gap ``G-4`` was about: that the command works as a command,
    and that it works from any working directory.
    """
    completed = subprocess.run(
        [sys.executable, str(ADMIN), *args],
        cwd=str(tmp_path),
        env={
            "PATH": "/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "RR_DATA_DIR": str(tmp_path),
            "RR_DATABASE_URL": str(tmp_path / "research-radar.db"),
        },
        input=stdin,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, f"{args}: {completed.stdout}\n{completed.stderr}"
    return completed.stdout


@pytest.fixture()
def wired(tmp_path: Path) -> Iterator[tuple[TestClient, Settings, str]]:
    """migrate -> bootstrap -> real factory, wired. Yields a client, settings and owner id."""
    settings = _settings(tmp_path)
    _run_admin(["migrate"], tmp_path)
    owner_id = _run_admin(["bootstrap-owner"], tmp_path, stdin=OWNER_PASSWORD).strip()

    from server.app.main import create_app

    app = create_app()
    wire(app, settings)
    # `Secure` cookies: the session cookie is only sent back over https, so the client must
    # speak https or every authenticated assertion below would fail for the wrong reason.
    with TestClient(app, base_url="https://testserver") as client:
        yield client, settings, owner_id


def _login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/v1/auth/login",
        headers={**WIRE_HEADERS, "Content-Type": "application/json"},
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
    )
    assert response.status_code == 200, response.text
    csrf = client.cookies.get("rr_csrf")
    assert csrf, "login must set the non-HttpOnly CSRF cookie (double-submit)"
    return {**WIRE_HEADERS, "X-CSRF-Token": csrf}


# ------------------------------------------------------------------------------------
# 1-2. migrate and bootstrap
# ------------------------------------------------------------------------------------


def test_migrate_runs_from_a_foreign_working_directory(tmp_path: Path) -> None:
    """Gap ``G-4``: ``alembic upgrade head`` used to work only from inside ``server/``."""
    settings = _settings(tmp_path)
    assert not settings.database_path.exists()
    _run_admin(["migrate"], tmp_path)
    assert settings.database_path.exists()

    from sqlalchemy import text

    from server.app.db import create_sqlite_engine

    with create_sqlite_engine(settings.database_path).connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert revision, "alembic_version is empty after upgrade head"


def test_bootstrap_prints_only_the_owner_id_and_never_the_password(tmp_path: Path) -> None:
    """Gap ``G-1``. The negative half is the point: nothing about the secret may leak."""
    _run_admin(["migrate"], tmp_path)
    output = _run_admin(["bootstrap-owner"], tmp_path, stdin=OWNER_PASSWORD)

    owner_id = output.strip()
    assert len(owner_id) == 26, f"expected a ULID, got {owner_id!r}"
    assert OWNER_PASSWORD not in output
    assert "argon2" not in output.lower()
    assert "$" not in output  # an Argon2 PHC string would contain one


def test_bootstrap_refuses_a_short_password(tmp_path: Path) -> None:
    """The rule is enforced at the console too, not only by the login route's validator."""
    _run_admin(["migrate"], tmp_path)
    completed = subprocess.run(
        [sys.executable, str(ADMIN), "bootstrap-owner"],
        cwd=str(tmp_path),
        env={
            "PATH": "/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "RR_DATA_DIR": str(tmp_path),
            "RR_DATABASE_URL": str(tmp_path / "research-radar.db"),
        },
        input="short",
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "at least 8 characters" in completed.stderr
    settings = _settings(tmp_path)
    assert resolve_owner_id(build_runtime(settings).engine) is None, "nothing may be written"


# ------------------------------------------------------------------------------------
# 3-5. the wired application
# ------------------------------------------------------------------------------------


def test_login_succeeds_through_the_real_factory(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """The exact call the runbook records as returning **500** before this packet."""
    client, _settings_obj, _owner = wired
    response = client.post(
        "/v1/auth/login",
        headers={**WIRE_HEADERS, "Content-Type": "application/json"},
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
    )
    assert response.status_code == 200, response.text
    assert client.cookies.get("rr_session"), "no session cookie"
    assert client.cookies.get("rr_csrf"), "no CSRF cookie"


def test_readiness_is_401_before_login_and_200_after(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """Both halves matter: the route must deny first, then serve the authenticated owner."""
    client, _settings_obj, _owner = wired
    assert client.get("/v1/health/readiness", headers=WIRE_HEADERS).status_code == 401

    headers = _login(client)
    response = client.get("/v1/health/readiness", headers=headers)
    assert response.status_code == 200, response.text
    assert "modules" in response.json()


def test_runs_list_is_200_and_empty_on_a_fresh_database(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """``run.list`` is the proof that an **owner-scoped** context was really built.

    It reads ``app.state.job_context``, which needs the engine, the owner id and the
    schedule. A 500 here would mean the context is missing; a 200 with rows would mean the
    database was not blank. 200 with an empty list is the only correct answer.
    """
    client, _settings_obj, _owner = wired
    headers = _login(client)
    response = client.get("/v1/runs", headers=headers)
    assert response.status_code == 200, response.text

    payload: Any = response.json()
    items = payload["runs"] if isinstance(payload, dict) and "runs" in payload else payload
    if isinstance(items, dict):
        items = items.get("items", [])
    assert list(items) == [], f"a fresh database must have no runs, got {payload!r}"


def test_settings_is_200_for_the_owner_on_a_wired_app(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """``/v1/settings`` answered **500** on a real deployment (``CR-TC-SECRET-06``).

    The settings and secret contexts were simply never built by the composition root, so the
    router's ``getattr(app.state, "settings_context", None)`` returned ``None`` and every
    call raised ``SecretDependencyUnavailable``. This asserts the whole path the Owner
    actually walks: log in, then read settings.

    It deliberately does **not** configure ``RR_SECRET_MASTER_KEY``. Settings needs no master
    key -- that is the point of ``SecretContext.store`` being optional (``REQ-D51``: a key is
    not mandatory) -- so a 200 here proves the contexts exist rather than proving a key was
    supplied.
    """
    client, _settings_obj, _owner = wired
    headers = _login(client)
    response = client.get("/v1/settings", headers=headers)
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), dict)


def test_settings_needs_the_owner_session(wired: tuple[TestClient, Settings, str]) -> None:
    """Unauthenticated is 401, not 500 and not 200 -- the same default-deny as readiness."""
    client, _settings_obj, _owner = wired
    assert client.get("/v1/settings", headers=WIRE_HEADERS).status_code == 401


def test_no_master_key_leaves_the_store_unset_and_never_invents_one(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """No key configured must mean *no store*, never a generated or default key.

    ``contracts/ops/secrets.md`` §4.1 forbids inventing key material, and a deployment with
    no key still has to run (``REQ-D51``). So the honest state is: contexts built, store
    ``None``, and the reason recorded where an operator can read it.
    """
    client, _settings_obj, _owner = wired
    runtime = client.app.state.runtime  # type: ignore[attr-defined]

    assert "settings_context" in runtime.wired
    assert "secret_context" in runtime.wired
    assert client.app.state.secret_context.store is None  # type: ignore[attr-defined]

    reasons = dict(runtime.unwired)
    assert "RR_SECRET_MASTER_KEY" in reasons["secret_store"]


def test_the_wiring_report_names_the_owner_scoped_contexts(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """What was wired is observable, so a regression is a failed assertion not a 500 later."""
    client, _settings_obj, owner_id = wired
    runtime = client.app.state.runtime  # type: ignore[attr-defined]

    assert runtime.owner_id == owner_id
    for name in ("engine", "auth_service", "job_context", "ingest_context", "telegram_context"):
        assert name in runtime.wired, f"{name} was not wired"

    report = runtime.report()
    assert report["owner_bootstrapped"] is True
    # The unwired list is part of the contract of this module: each entry carries a reason.
    for name, reason in report["unwired"].items():
        assert reason, f"{name} is unwired with no reason given"


def test_unwired_reasons_are_derived_not_frozen(
    wired: tuple[TestClient, Settings, str],
) -> None:
    """``F-A3-P5-02``: the research-connector reason must come from the contract, not a literal.

    The old line told the Owner the ``REQ-A6`` rate facts were still ``PLACEHOLDER_KC``. They
    had been resolved since Phase 2 -- ``retry-policy.yaml`` carries all six values with
    ``status: DOCS_derived`` -- so the one screen built to tell the Owner what works was
    sending them to re-open a closed requirement. This asserts the new reasons name the two
    blockers that actually hold (``SG-DOC``, ``SG-LIVE``) and that the stale claim is gone.
    """
    client, _settings_obj, _owner = wired
    reasons = dict(client.app.state.runtime.unwired)  # type: ignore[attr-defined]

    connector = reasons["research_connector"]
    assert "SG-DOC" in connector and "SG-LIVE" in connector
    assert "PLACEHOLDER_KC" not in connector, "the stale REQ-A6 claim is back"

    # `report_context` is set to None *explicitly*, so a router can tell "deliberately not
    # built" from "forgotten" (F-A3-P5-03).
    assert client.app.state.report_context is None  # type: ignore[attr-defined]
    assert reasons["report_context"].startswith("CR-P0-07")

    # The secret/settings service landed, so a reason blaming its absence would be the same
    # class of staleness this test exists to catch.
    assert "no MOD-secret-service" not in reasons["analysis_context.provider_config"]


def test_status_prints_the_file_the_engine_actually_opens(tmp_path: Path) -> None:
    """One formatting site, and it must name the file the engine opens -- not a URL.

    `rr-admin status` and `rr-admin migrate` both print through `database_line()`. This
    compares that string against the path the engine is actually constructed with, so the
    two can never drift into describing different files.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    from server.app.db import create_sqlite_engine
    from tools.rr_admin import database_line

    settings = _settings(tmp_path)
    printed = database_line(settings)
    engine = create_sqlite_engine(settings.database_path)

    assert printed == str(settings.database_path.resolve())
    assert str(engine.url).endswith(printed), (printed, str(engine.url))
    assert "sqlite:" not in printed, "a URL scheme leaked into the printed path"


def test_every_sqlite_url_form_resolves_to_the_file_it_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``CR-P0-10``, now the real assertion. Was a strict xfail in ``PKT-P0-FIX9``.

    The Coordinator's process check found ``RR_DATABASE_URL=sqlite:////tmp/x/rr.db``
    producing ``/tmp/x/sqlite:/tmp/x/rr.db`` -- and the engine opened *that*, so a real
    deployment created a file literally named ``sqlite:...`` in the working directory while
    the database the operator named sat untouched. The resolver stripped only the
    ``sqlite+pysqlite:///`` spelling; plain ``sqlite:///`` is SQLAlchemy's own form and is
    what anyone reading its documentation would type.

    Every form SQLAlchemy accepts is checked, because "the one we happened to test" is how
    the gap got in.
    """
    data_dir = tmp_path / "data"
    absolute = tmp_path / "abs" / "rr.db"
    monkeypatch.setenv("RR_DATA_DIR", str(data_dir))

    for url in (
        f"sqlite:///{absolute}",  # SQLAlchemy's four-slash absolute form
        f"sqlite+pysqlite:///{absolute}",
        str(absolute),  # a bare path, which env.py has always accepted
    ):
        monkeypatch.setenv("RR_DATABASE_URL", url)
        assert load_settings().database_path == absolute, url


def test_a_relative_database_lands_in_the_data_dir_not_the_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A relative location belongs to the data volume, not to wherever the shell was.

    ``contracts/ops/deployment.md`` calls the data store "file trên volume" (rows
    ``RT-server`` / ``MOD-data-store``), and ``RR_DATA_DIR`` is this repo's name for that
    volume root. Resolving against the cwd would mean one configuration opens different
    databases depending on the directory the process started in -- the same class of defect
    as ``CR-P0-10`` itself.

    The exception is an explicit ``./``: that is an operator saying "here", and it keeps
    ``RR_DATABASE_URL=./var/research-radar.db`` -- the example ``server/migrations/env.py``
    prints -- meaning what it always has.
    """
    data_dir = tmp_path / "data"
    monkeypatch.setenv("RR_DATA_DIR", str(data_dir))

    monkeypatch.setenv("RR_DATABASE_URL", "sqlite:///nested/rr.db")
    assert load_settings().database_path == (data_dir / "nested" / "rr.db").resolve()

    monkeypatch.setenv("RR_DATABASE_URL", "nested/rr.db")
    assert load_settings().database_path == (data_dir / "nested" / "rr.db").resolve()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RR_DATABASE_URL", "./here/rr.db")
    assert load_settings().database_path == (tmp_path / "here" / "rr.db").resolve()


def test_the_in_memory_database_is_never_joined_to_a_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``:memory:`` is not a path, and treating it as one silently creates a junk file."""
    monkeypatch.setenv("RR_DATA_DIR", str(tmp_path))
    for url in ("sqlite:///:memory:", "sqlite://", ":memory:"):
        monkeypatch.setenv("RR_DATABASE_URL", url)
        settings = load_settings()
        assert settings.database_path == MEMORY_PATH, url
        assert settings.is_memory_database, url


def test_the_settings_summary_carries_no_secret(tmp_path: Path) -> None:
    """`status` and the wiring report both print this; it must never hold a credential."""
    settings = _settings(tmp_path)
    redacted = settings.redacted()
    assert redacted["telegram_webhook_secret_configured"] is False
    assert not any(
        "secret" in str(value).lower() for value in redacted.values() if value is not True
    )


def test_an_unbootstrapped_database_wires_no_owner_scoped_context(tmp_path: Path) -> None:
    """Starting the server before ``bootstrap-owner`` must be honest, not a crash.

    The owner-scoped contexts stay unset -- their routes then answer as they were designed
    to -- and the reason names the command that fixes it.
    """
    _run_admin(["migrate"], tmp_path)

    from server.app.main import create_app

    app = create_app()
    runtime = wire(app, _settings(tmp_path))

    assert runtime.owner_id is None
    assert "job_context" not in runtime.wired
    assert not hasattr(app.state, "job_context")
    reasons = dict(runtime.unwired)
    assert "bootstrap-owner" in reasons["owner-scoped contexts"]
