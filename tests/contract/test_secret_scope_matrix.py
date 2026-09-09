"""E1 — who may call the ``secret.*`` / ``settings.*`` operations, and with which refusal.

The card's §5 turns ruling ``R5-01`` into a pass/fail property: *choosing the wrong error code
is a failure in its own right*, not a cosmetic difference. So this file asserts the code, not
merely that something was refused.

The matrix, from ``contracts/ops/secrets.md`` §4.2 and ``contracts/http/openapi.yaml``:

=========================  ==================================  =======================
caller                     operation                           expected
=========================  ==================================  =======================
owner session + CSRF       ``settings.*``                      allowed
owner session, no CSRF     ``settings.update_config``          ``CSRF_REJECTED`` (403)
anonymous                  ``settings.get_config``             ``UNAUTHORIZED`` (401)
collector token            ``settings.*``                      ``UNAUTHORIZED`` (401)
collector token            ``secret.issue_task_credential``    ``UNAUTHORIZED`` (401)
owner session              ``secret.issue_task_credential``    ``UNAUTHORIZED`` (401)
analysis worker token      ``secret.issue_task_credential``    admitted (then ISO-05)
=========================  ==================================  =======================

Fixture ``recovery/i-collector-token-calls-save.json`` is the frozen precedent for the code in
rows 4 and 5: a valid token of the wrong class is ``UNAUTHORIZED``, not ``FORBIDDEN_EDGE``
(``NC-01``/``NC-02``, and the fixture's own ``packet_deviation`` note records the packet text
that once said otherwise). Fixture ``recovery/h-unauthenticated-owner-api.json`` is the
precedent for row 3.

Two structural assertions round it out: no route of this module returns a secret value, and
the two ``internal`` operations have no route at all.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import text

from server.app.auth.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from server.app.auth.middleware import PrincipalKind, TokenRegistry
from server.app.auth.service import AuthService
from server.app.db import create_sqlite_engine
from server.app.main import create_app
from server.app.secret.repository import SecretRepository
from server.app.secret.service import SecretContext
from server.app.secret.store import InMemoryMaterialStore, SecretStore
from server.app.settings_service.repository import SettingsRepository
from server.app.settings_service.service import SettingsContext, SettingsProviderView

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_NAME = "owner"
OWNER_PASSWORD = "correct horse battery staple"
WIRE_HEADERS = {"X-Schema-Version": "0.3.0", "X-Request-Id": "01J0000000000000000000000Z"}
MUTATION_HEADERS = {**WIRE_HEADERS, "Idempotency-Key": "01J0000000000000000000001Z"}

#: A 32-byte test key. It is a test value, not a deployment default: nothing in
#: ``server/app/`` supplies one, and ``load_master_key`` raises when the variable is unset.
TEST_MASTER_KEY = b"\x11" * 32


#: The tests run against the **real** AES-256-GCM backend (``PKT-P0-FIX7`` put
#: ``cryptography>=43,<47`` in the lockfile, closing ``CR-TC-SECRET-02``). ``SecretStore``
#: defaults to it, so nothing here passes a ``cipher=`` argument any more and every assertion
#: below -- the canary count, the masked audit rows, the reference-only read model -- is now
#: made about ciphertext produced by the cipher the contract asks for.


def _migrate(db_path: Path) -> None:
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


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
def owner_id(engine: Any, auth_service: AuthService) -> str:
    """Depends on ``auth_service`` because that is what creates the single ``owner`` row.

    ``I01`` gives every table an ``owner_id`` and every one of them is a real foreign key, so
    a test that writes a secret without bootstrapping the owner is testing nothing.
    """
    with engine.connect() as connection:
        return str(connection.execute(text("SELECT id FROM owner")).scalar_one())


@pytest.fixture
def secret_context(engine: Any, owner_id: str) -> SecretContext:
    store = SecretStore(master_key=TEST_MASTER_KEY, material=InMemoryMaterialStore())
    return SecretContext(engine=engine, owner_id=owner_id, store=store)


@pytest.fixture
def settings_context(engine: Any, owner_id: str, secret_context: SecretContext) -> SettingsContext:
    return SettingsContext(engine=engine, owner_id=owner_id, secrets=secret_context)


@pytest.fixture
def client(
    auth_service: AuthService,
    secret_context: SecretContext,
    settings_context: SettingsContext,
) -> TestClient:
    app = create_app()
    app.state.auth_service = auth_service
    app.state.token_registry = TokenRegistry(
        {
            "collector-token": PrincipalKind.COLLECTOR,
            "analysis-worker-token": PrincipalKind.ANALYSIS_WORKER,
        }
    )
    app.state.secret_context = secret_context
    app.state.settings_context = settings_context
    return TestClient(app, base_url="https://testserver")


def _login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers=WIRE_HEADERS,
    )
    assert response.status_code == 200, response.text
    return {CSRF_HEADER_NAME: client.cookies[CSRF_COOKIE_NAME]}


def _code(response: Any) -> str:
    return str(response.json()["code"])


# ----------------------------------------------------------------------------- the matrix


def test_anonymous_cannot_read_the_config(client: TestClient) -> None:
    """Row 3, fixture ``recovery/h``: no session, no config -- and 401, not 403."""
    response = client.get("/v1/settings", headers=WIRE_HEADERS)
    assert response.status_code == 401, response.text
    assert _code(response) == ErrorCode.UNAUTHORIZED.value


def test_collector_token_cannot_read_the_config(client: TestClient) -> None:
    """Row 4. ``secrets.md`` §4.2 gives ``ACT-collector`` nothing here (``FE-09``)."""
    response = client.get(
        "/v1/settings", headers={**WIRE_HEADERS, "Authorization": "Bearer collector-token"}
    )
    assert response.status_code == 401, response.text
    assert _code(response) == ErrorCode.UNAUTHORIZED.value


def test_collector_token_cannot_ask_for_a_task_credential(client: TestClient) -> None:
    """Row 5 -- the same shape as fixture ``recovery/i``: right token, wrong class."""
    response = client.post(
        "/v1/secrets/task-credentials",
        headers={**MUTATION_HEADERS, "Authorization": "Bearer collector-token"},
        json={
            "task_id": "T",
            "attempt_id": "A",
            "lease_id": "L",
            "lease_epoch": 1,
            "worker_instance_id": "w1",
            "assignment_id": "S",
        },
    )
    assert response.status_code == 401, response.text
    assert _code(response) == ErrorCode.UNAUTHORIZED.value


def test_owner_session_cannot_ask_for_a_task_credential(client: TestClient) -> None:
    """Row 6. ``DC-OWN-01`` / ``NC-03``: the owner configures keys, never draws one."""
    csrf = _login(client)
    response = client.post(
        "/v1/secrets/task-credentials",
        headers={**MUTATION_HEADERS, **csrf},
        json={
            "task_id": "T",
            "attempt_id": "A",
            "lease_id": "L",
            "lease_epoch": 1,
            "worker_instance_id": "w1",
            "assignment_id": "S",
        },
    )
    assert response.status_code == 401, response.text
    assert _code(response) == ErrorCode.UNAUTHORIZED.value


def test_owner_session_without_csrf_is_csrf_rejected_not_unauthorized(client: TestClient) -> None:
    """Row 2, and the distinction ``R5-01`` makes load-bearing.

    The class is admitted; the intent is unproven. 403 ``CSRF_REJECTED``, and the session
    survives -- a mutation that logged the owner out on a missing header would turn a
    misconfigured proxy into a denial of service.
    """
    _login(client)
    response = client.patch(
        "/v1/settings", headers=WIRE_HEADERS, json={"settings": {"backfill_days": 7}}
    )
    assert response.status_code == 403, response.text
    assert _code(response) == ErrorCode.CSRF_REJECTED.value
    assert client.get("/v1/settings", headers=WIRE_HEADERS).status_code == 200


def test_owner_session_with_csrf_may_write_config(client: TestClient) -> None:
    """Row 1: the allowed path exists, so the refusals above mean something."""
    csrf = _login(client)
    response = client.patch(
        "/v1/settings",
        headers={**WIRE_HEADERS, **csrf},
        json={"settings": {"backfill_days": 7, "timezone_iana": "Asia/Ho_Chi_Minh"}},
    )
    assert response.status_code == 200, response.text
    assert response.json()["settings"]["backfill_days"] == 7


def test_worker_token_is_admitted_and_then_judged_on_the_lease(client: TestClient) -> None:
    """Row 7: the boundary lets the worker in; ISO-05 decides after that.

    The point of this assertion is the *absence* of 401: a worker refused at the door would
    make ``tests/integration/test_task_credential_lease.py`` pass for the wrong reason.
    """
    response = client.post(
        "/v1/secrets/task-credentials",
        headers={**MUTATION_HEADERS, "Authorization": "Bearer analysis-worker-token"},
        json={
            "task_id": "no-such-task",
            "attempt_id": "A",
            "lease_id": "L",
            "lease_epoch": 1,
            "worker_instance_id": "w1",
            "assignment_id": "S",
        },
    )
    assert response.status_code != 401, response.text
    assert _code(response) != ErrorCode.UNAUTHORIZED.value


# ------------------------------------------------------------------- structural assertions


def test_the_internal_operations_have_no_route(client: TestClient) -> None:
    """``secret.store_provider_key`` and ``secret.revoke_task_credential`` are ``internal``.

    Asserted against the live route table rather than by reading the source: a path added by a
    future edit shows up here, and "we did not write that endpoint" is not a property a
    reviewer can check by grep alone.
    """
    paths = {route.path for route in client.app.routes}  # type: ignore[attr-defined]
    assert "/v1/secrets/task-credentials" in paths
    assert not [path for path in paths if "provider-key" in path or "revoke" in path]


def test_get_config_never_returns_a_key_value(
    client: TestClient, secret_context: SecretContext, engine: Any, owner_id: str
) -> None:
    """``NC-03`` as a string search over the whole response body.

    The key is stored through the real operation, then the whole ``GET /v1/settings`` body is
    searched for it. Counting occurrences (0) rather than eyeballing the shape is what makes
    this an oracle: a future field that happens to carry the value fails here.
    """
    from server.app.secret.service import store_provider_key

    secret_value = "sk-live-canary-DO-NOT-EMIT-8f3a"
    reference = store_provider_key(
        secret_context, provider_id="anthropic", value=secret_value, key_version=1
    )
    with engine.begin() as connection:
        SettingsRepository().upsert_provider(
            connection,
            _provider_row(owner_id, reference.secret_ref_id),
        )

    _login(client)
    response = client.get("/v1/settings", headers=WIRE_HEADERS)
    assert response.status_code == 200, response.text
    assert secret_value not in response.text
    assert response.text.count(secret_value) == 0
    provider = response.json()["providers"][0]
    assert provider["key_configured"] is True
    assert provider["secret_ref"] == reference.secret_ref_id
    assert "provider_key" not in provider
    assert "value" not in provider


def test_the_stored_row_holds_a_pointer_not_a_value(
    secret_context: SecretContext, engine: Any, owner_id: str
) -> None:
    """``ENT-secret-ref``: "chỉ giữ tham chiếu + trạng thái, không giữ giá trị"."""
    from server.app.secret.service import store_provider_key

    secret_value = "sk-live-canary-row-check-9271"
    store_provider_key(secret_context, provider_id="anthropic", value=secret_value, key_version=1)
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT * FROM secret_ref")).mappings().all()
    assert len(rows) == 1
    assert secret_value not in str(dict(rows[0]))


def test_audit_details_are_masked_before_the_write(
    secret_context: SecretContext, engine: Any, owner_id: str
) -> None:
    """``SEC-P6``: the mask happens on the way in, so the stored row never held the value."""
    from server.app.secret.service import store_provider_key

    secret_value = "sk-live-audit-canary-55f1a2b3c4"
    store_provider_key(secret_context, provider_id="anthropic", value=secret_value, key_version=1)
    with engine.connect() as connection:
        details = [
            row.outcome_detail_safe or ""
            for row in SecretRepository().audit_rows(connection, owner_id=owner_id)
        ]
    assert details, "storing a key must leave an audit row"
    assert all(secret_value not in detail for detail in details)


def test_storing_the_same_version_twice_is_one_row(
    secret_context: SecretContext, engine: Any
) -> None:
    """``ports.yaml``: "Ghi cùng version không tạo bản ghi thứ hai"."""
    from server.app.secret.service import store_provider_key

    first = store_provider_key(secret_context, provider_id="anthropic", value="k1", key_version=1)
    second = store_provider_key(secret_context, provider_id="anthropic", value="k1", key_version=1)
    assert first.secret_ref_id == second.secret_ref_id
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM secret_ref")).scalar_one() == 1


def test_same_version_with_a_different_value_is_an_idempotency_conflict(
    secret_context: SecretContext,
) -> None:
    """The other half of the same rule: a silent overwrite would lose the live key."""
    from server.app.secret.service import SecretError, store_provider_key

    store_provider_key(secret_context, provider_id="anthropic", value="k1", key_version=1)
    with pytest.raises(SecretError) as raised:
        store_provider_key(secret_context, provider_id="anthropic", value="k2", key_version=1)
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT


def test_a_new_version_rotates_and_keeps_the_old_row(
    secret_context: SecretContext, engine: Any
) -> None:
    """``secrets.md`` §3: old and new are both live during ``rotation_overlap``."""
    from server.app.secret.service import store_provider_key

    store_provider_key(secret_context, provider_id="anthropic", value="k1", key_version=1)
    second = store_provider_key(secret_context, provider_id="anthropic", value="k2", key_version=2)
    assert second.rotated_previous is True
    with engine.connect() as connection:
        states = dict(
            connection.execute(text("SELECT state, COUNT(*) FROM secret_ref GROUP BY state")).all()
        )
    assert states == {"active": 1, "rotated": 1}


def _provider_row(owner_id: str, secret_ref_id: str | None) -> Any:
    from server.app.settings_service.repository import ProviderConfigRow

    return ProviderConfigRow(
        id="01J00000000000000000PROV1",
        owner_id=owner_id,
        task_type="label",
        auth_family="api_key",
        provider_name="anthropic",
        model_name="claude-sonnet-5",
        max_concurrency=1,
        secret_ref=secret_ref_id,
        enabled=False,
        terms_check_at=None,
        terms_check_by=None,
        terms_doc_ref=None,
    )


def test_settings_provider_view_exposes_no_value(
    settings_context: SettingsContext, engine: Any, owner_id: str
) -> None:
    """The port ``MOD-secret-service`` reads: a binding, an id, a flag -- and no key."""
    with engine.begin() as connection:
        SettingsRepository().upsert_provider(connection, _provider_row(owner_id, None))
    binding = SettingsProviderView(settings_context).secret_ref_for_task("label")
    assert binding is not None
    assert binding.enabled is False
    assert binding.secret_ref_id is None
    assert not hasattr(binding, "value")
    assert not hasattr(binding, "key")


# ------------------------------------------------------- the cipher itself (CR-TC-SECRET-02)


def test_the_stored_material_is_not_the_plaintext(secret_context: SecretContext) -> None:
    """``secrets.md`` §4.1: the store holds ciphertext, and this is the assertion that says so.

    Every other test in this file would pass against a store that wrote the key out verbatim --
    they check who may read it, not what is on the medium. This one reads the serialised
    envelope straight out of the material store and searches it, so "encrypted at rest" is a
    measurement rather than a design intention.
    """
    from server.app.secret.service import store_provider_key

    value = "sk-live-plaintext-must-not-appear-4417"
    reference = store_provider_key(secret_context, provider_id="anthropic", value=value)
    store = secret_context.store
    assert store is not None
    blob = store._material.get(reference.store_locator)  # noqa: SLF001 - the point of the test
    assert blob is not None
    assert value not in blob
    assert value.encode().hex() not in blob
    # And it is genuinely recoverable, so the absence above is encryption and not data loss.
    assert (
        store.reveal(locator=reference.store_locator, purpose=reference.purpose).reveal() == value
    )


def test_material_written_under_one_master_key_will_not_open_under_another(
    secret_context: SecretContext,
) -> None:
    """The property that makes the master key worth protecting.

    ``secrets.md`` §4.1 states the consequence in as many words -- "mất master key là mất mọi
    secret dù backup còn nguyên" -- and a store that quietly decrypted under the wrong key would
    make that sentence false and the whole envelope scheme decorative. The refusal is an AEAD
    authentication failure, surfaced as ``MasterKeyMismatch``: an operator-side condition,
    distinct from "no material here".
    """
    from server.app.secret.service import store_provider_key
    from server.app.secret.store import MasterKeyMismatch, SecretStore

    reference = store_provider_key(secret_context, provider_id="anthropic", value="sk-live-abc")
    original = secret_context.store
    assert original is not None
    stranger = SecretStore(master_key=b"\xff" * 32, material=original._material)  # noqa: SLF001

    with pytest.raises(MasterKeyMismatch):
        stranger.reveal(locator=reference.store_locator, purpose=reference.purpose)


def test_the_same_purpose_does_not_open_another_locators_material(
    secret_context: SecretContext,
) -> None:
    """Locator and purpose are bound in as associated data, so material cannot be swapped.

    A restore that shuffled two blobs, or a bug that read the Telegram token for an AI task,
    fails authentication instead of returning the wrong secret confidently.
    """
    from server.app.secret.service import store_provider_key
    from server.app.secret.store import MasterKeyMismatch

    reference = store_provider_key(secret_context, provider_id="anthropic", value="sk-live-abc")
    store = secret_context.store
    assert store is not None
    with pytest.raises(MasterKeyMismatch):
        store.reveal(locator=reference.store_locator, purpose="telegram_bot_token")


def test_no_nonce_is_ever_reused(secret_context: SecretContext) -> None:
    """GCM's one fatal misuse, asserted as a count rather than promised in a docstring.

    Two messages sharing a (key, nonce) pair under AES-GCM leak their XOR and the
    authentication subkey. Each secret gets its own data key *and* a fresh nonce, so this
    encrypts many values through the real store and asserts every nonce -- the data-key wrap
    nonce and the payload nonce alike -- is distinct.
    """
    from server.app.secret.store import SecretMaterial

    store = secret_context.store
    assert store is not None
    nonces: list[bytes] = []
    for index in range(64):
        locator = f"nonce-probe-{index}"
        store.store(locator=locator, purpose="ai_provider_key", value=f"sk-live-{index}")
        blob = store._material.get(locator)  # noqa: SLF001
        assert blob is not None
        envelope = SecretMaterial.parse(blob)
        nonces.append(envelope.nonce)
        nonces.append(envelope.wrapped_data_key[:12])

    assert len(nonces) == 128
    assert len(set(nonces)) == 128, "a nonce repeated; AES-GCM must never reuse one under a key"


def test_the_algorithm_is_the_one_the_contract_names(secret_context: SecretContext) -> None:
    """``secrets.md`` §4.1 offers AES-256-GCM or XChaCha20-Poly1305; this build uses the first.

    Recorded as an assertion so that a future swap to another primitive has to come past a test
    that names the clause, rather than sliding in as an import change.
    """
    from server.app.secret.cipher import ALGORITHM, KEY_BYTES, NONCE_BYTES, AesGcm256

    assert ALGORITHM == "AES-256-GCM"
    assert (KEY_BYTES, NONCE_BYTES) == (32, 12)
    assert AesGcm256().algorithm == ALGORITHM
    store = secret_context.store
    assert store is not None
    assert isinstance(store._cipher, AesGcm256)  # noqa: SLF001 - production default, asserted
