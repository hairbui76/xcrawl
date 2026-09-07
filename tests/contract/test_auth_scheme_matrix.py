"""E1 — the security scheme matrix of ``contracts/http/openapi.yaml``, asserted.

The reviewer question card §12 makes mandatory is: *is there any owner mutation route that
accepts the cookie on its own?* :func:`test_every_owner_mutation_requires_cookie_and_csrf`
answers it by reading all 54 HTTP operations out of the contract, not by reading code.

Everything in this file compares **code against contract**. The contract is never adjusted
to make a test pass; a mismatch is a change request (SRC-PLAN §15).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.routing import APIRoute
from pydantic import ValidationError
from rr_contracts.generated.constants import SECURITY_SCHEMES
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth import middleware
from server.app.auth.csrf import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    CSRF_TOKEN_BITS,
    csrf_matches,
    new_csrf_token,
)
from server.app.auth.middleware import (
    ALLOWED_CALLERS,
    ALLOWED_MODULE_EDGES,
    OWNER_CSRF_TOKEN_SCHEME,
    OWNER_SESSION_COOKIE_SCHEME,
    SCHEME_REQUIREMENTS,
    AuthScope,
)
from server.app.auth.router import LoginRequest, SessionInfo
from server.app.auth.service import (
    ABSOLUTE_TIMEOUT_MS,
    ARGON2_MEMORY_COST_KIB,
    ARGON2_PARALLELISM,
    ARGON2_TIME_COST,
    DETAILS_SAFE_KEYS,
    HTTP_STATUS,
    IDLE_TIMEOUT_MS,
    LOCKOUT_DURATION_MS,
    LOGIN_FAIL_THRESHOLD,
    LOGIN_FAIL_WINDOW_MS,
    MESSAGE_SAFE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
HTTP_METHODS = ("get", "post", "put", "patch", "delete")


@pytest.fixture(scope="module")
def openapi_document() -> dict[str, Any]:
    return dict(
        yaml.safe_load((REPO_ROOT / "contracts" / "http" / "openapi.yaml").read_text("utf-8"))
    )


@pytest.fixture(scope="module")
def ports() -> dict[str, dict[str, Any]]:
    document = yaml.safe_load((REPO_ROOT / "contracts" / "ports.yaml").read_text("utf-8"))
    return {op["operation_id"]: op for op in document["operations"]}


@pytest.fixture(scope="module")
def errors() -> dict[str, dict[str, Any]]:
    document = yaml.safe_load((REPO_ROOT / "contracts" / "errors.yaml").read_text("utf-8"))
    return {code["code"]: code for code in document["codes"]}


def _http_operations(document: dict[str, Any]) -> list[tuple[str, str, str, dict[str, Any]]]:
    """``(operation_id, path, method, operation object)`` for every path in the contract."""
    out = []
    for path, item in document["paths"].items():
        for method, operation in item.items():
            if method in HTTP_METHODS:
                out.append((operation["operationId"], path, method, operation))
    return out


# --------------------------------------------------------------------------------------
# The card's headline oracle
# --------------------------------------------------------------------------------------


def test_every_owner_mutation_requires_cookie_and_csrf(openapi_document, ports) -> None:
    """Card §8 oracle: every ``mutation: true`` owner operation names **both** schemes in
    **one** security requirement -- an AND, not a choice."""
    checked = 0
    for operation_id, path, method, operation in _http_operations(openapi_document):
        port = ports[operation_id]
        if port["auth_scope"] != "owner_session" or not port["mutation"]:
            continue
        checked += 1
        requirements = [set(requirement) for requirement in operation["security"]]
        assert requirements, f"{operation_id} declares no security requirement"
        for requirement in requirements:
            assert requirement == {OWNER_SESSION_COOKIE_SCHEME, OWNER_CSRF_TOKEN_SCHEME}, (
                f"{method.upper()} {path} ({operation_id}) accepts {sorted(requirement)}; "
                "an owner mutation must require cookie AND CSRF in one requirement"
            )
    # 17 operations carry `auth_scope: owner_session` with `mutation: true` in the pinned
    # contract. Pinned as a number so that an operation quietly losing its CSRF requirement
    # by being re-scoped shows up here.
    assert checked == 17, f"expected 17 owner-session mutations, found {checked}"


def test_every_operation_errors_yaml_lists_for_csrf_requires_the_header(
    openapi_document, errors
) -> None:
    """``contracts/errors.yaml`` names the operations that can answer ``CSRF_REJECTED``.
    Each must actually declare ``ownerCsrfToken`` somewhere in its security."""
    listed = set(errors["CSRF_REJECTED"]["operations"])
    seen = set()
    for operation_id, _path, _method, operation in _http_operations(openapi_document):
        if operation_id not in listed:
            continue
        seen.add(operation_id)
        assert any(
            OWNER_CSRF_TOKEN_SCHEME in requirement for requirement in operation["security"]
        ), operation_id
    assert seen == listed, f"not routed over HTTP: {sorted(listed - seen)}"


def test_no_owner_mutation_accepts_the_cookie_alone(openapi_document, ports) -> None:
    """The negative form of the same question, stated separately so it cannot be lost in a
    refactor of the loop above."""
    offenders = [
        operation_id
        for operation_id, _path, _method, operation in _http_operations(openapi_document)
        if ports[operation_id]["auth_scope"] == "owner_session"
        and ports[operation_id]["mutation"]
        and any(set(req) == {OWNER_SESSION_COOKIE_SCHEME} for req in operation["security"])
    ]
    assert offenders == []


def test_owner_reads_take_the_cookie_alone(openapi_document, ports) -> None:
    """CSRF guards state changes, not reads (openapi ``ownerSessionCookie`` description)."""
    for operation_id, _path, _method, operation in _http_operations(openapi_document):
        port = ports[operation_id]
        if port["auth_scope"] != "owner_session" or port["mutation"]:
            continue
        assert [set(r) for r in operation["security"]] == [{OWNER_SESSION_COOKIE_SCHEME}]


def test_every_backup_route_accepts_only_the_backup_operator_token(openapi_document) -> None:
    """``CR-PC08-02``: a browser session must not be able to trigger a restore."""
    backup_ops = [
        (operation_id, operation)
        for operation_id, _path, _method, operation in _http_operations(openapi_document)
        if operation_id.startswith("backup.")
    ]
    assert backup_ops, "no backup.* route found in the contract"
    for operation_id, operation in backup_ops:
        assert [set(r) for r in operation["security"]] == [
            {middleware.BACKUP_OPERATOR_TOKEN_SCHEME}
        ], operation_id


def test_no_signup_or_password_reset_endpoint_exists(openapi_document) -> None:
    """REQ-D05 and the ``forbidden_effects`` of ``ui/sc51-first-time-setup.json``."""
    forbidden = ("signup", "sign-up", "/register", "password-reset", "password_reset", "forgot")
    auth_operations = set()
    for operation_id, path, _method, _operation in _http_operations(openapi_document):
        joined = f"{path} {operation_id}".lower()
        assert not any(word in joined for word in forbidden), joined
        if operation_id.startswith("auth."):
            auth_operations.add(operation_id)
    assert auth_operations == {"auth.login", "auth.logout", "auth.get_session"}


def test_mounted_app_exposes_exactly_the_three_auth_routes() -> None:
    """The router adds no fourth route -- checked on the real app, not on the contract."""
    from server.app.main import create_app

    routes = {
        (route.path, tuple(sorted(route.methods)))
        for route in create_app().routes
        if isinstance(route, APIRoute) and route.path.startswith("/v1/auth")
    }
    assert routes == {
        ("/v1/auth/login", ("POST",)),
        ("/v1/auth/logout", ("POST",)),
        ("/v1/auth/session", ("GET",)),
    }


# --------------------------------------------------------------------------------------
# Code vs contract: the tables this card had to hand-write
# --------------------------------------------------------------------------------------


def test_scheme_names_match_the_contract(openapi_document) -> None:
    contract_names = tuple(openapi_document["components"]["securitySchemes"])
    assert contract_names == tuple(SECURITY_SCHEMES)
    assert contract_names == (
        middleware.OWNER_SESSION_COOKIE_SCHEME,
        middleware.OWNER_CSRF_TOKEN_SCHEME,
        middleware.COLLECTOR_TOKEN_SCHEME,
        middleware.ANALYSIS_WORKER_TOKEN_SCHEME,
        middleware.TELEGRAM_INGRESS_SECRET_SCHEME,
        middleware.BACKUP_OPERATOR_TOKEN_SCHEME,
    )


def test_cookie_and_header_names_match_the_contract(openapi_document) -> None:
    schemes = openapi_document["components"]["securitySchemes"]
    assert schemes[OWNER_SESSION_COOKIE_SCHEME]["name"] == middleware.SESSION_COOKIE_NAME
    assert schemes[OWNER_CSRF_TOKEN_SCHEME]["name"] == CSRF_HEADER_NAME
    assert CSRF_COOKIE_NAME == "rr_csrf"
    csrf_header = openapi_document["components"]["parameters"]["CsrfTokenHeader"]["schema"]
    token = new_csrf_token()
    assert csrf_header["minLength"] <= len(token) <= csrf_header["maxLength"]
    assert len(token) * 4 == CSRF_TOKEN_BITS


def test_scheme_requirements_table_equals_the_contract(openapi_document, ports) -> None:
    """``middleware.SCHEME_REQUIREMENTS`` is hand-written contract data (``CR-TC-AUTH-01``).
    This test regenerates it from the document and demands equality, so a contract change
    breaks the build instead of drifting past it."""
    derived: dict[tuple[AuthScope, bool], set[frozenset[str]]] = {}
    for operation_id, _path, _method, operation in _http_operations(openapi_document):
        port = ports[operation_id]
        key = (AuthScope(port["auth_scope"]), bool(port["mutation"]))
        derived[key] = derived.get(key, set()) | {
            frozenset(requirement) for requirement in operation["security"]
        }
    assert {k: set(v) for k, v in SCHEME_REQUIREMENTS.items()} == derived


@pytest.fixture(scope="module")
def modules() -> dict[str, Any]:
    return dict(yaml.safe_load((REPO_ROOT / "contracts" / "modules.yaml").read_text("utf-8")))


def test_allowed_callers_table_equals_ports_yaml(ports) -> None:
    """``middleware.ALLOWED_CALLERS`` is the default-deny registry ``require_edge`` reads.

    Hand-written contract data (``CR-TC-AUTH-05``: the generator emits ``OWNER_MODULE``,
    ``TRANSPORT`` and ``MUTATION`` but not ``caller_modules``). Rebuilt here from the
    contract and compared, so the table cannot drift: all 85 operations, exactly.
    """
    derived = {
        OperationId(operation_id): frozenset(port["caller_modules"])
        for operation_id, port in ports.items()
    }
    assert derived == ALLOWED_CALLERS
    assert len(ALLOWED_CALLERS) == 85


def test_allowed_module_edges_table_equals_modules_yaml(modules) -> None:
    """The pair-level half, for the two sweep rows that name no operation."""
    derived = {(edge["caller"], edge["callee"]) for edge in modules["allowed_edges"]}
    assert set(ALLOWED_MODULE_EDGES) == derived


def test_every_forbidden_edge_is_refused_by_one_of_the_two_registries(modules, ports) -> None:
    """``default_deny``: none of the 36 forbidden edges may be reachable through either
    registry. Asserted against ``modules.yaml`` itself, not against the fixture, so the two
    oracles have to agree."""
    forbidden = modules["forbidden_edges"]
    assert len(forbidden) == 36
    for edge in forbidden:
        operation = edge.get("operation")
        if operation is not None and operation in ports:
            assert edge["caller"] not in ALLOWED_CALLERS[OperationId(operation)], edge["id"]
        else:
            # No operation named at edge level: the pair itself must be absent, unless the
            # pair is legitimate for some *other* operation (FE-28, FE-33 -- both carry an
            # `operation_scope` that narrows them).
            pair = (edge["caller"], edge["callee"])
            assert pair not in ALLOWED_MODULE_EDGES or "operation_scope" in edge, edge["id"]


def test_openapi_auth_scope_matches_ports(openapi_document, ports) -> None:
    """``x-auth-scope`` and ``x-mutation`` restate ports.yaml; a drift between the two would
    make every other assertion here meaningless."""
    for operation_id, _path, _method, operation in _http_operations(openapi_document):
        assert operation["x-auth-scope"] == ports[operation_id]["auth_scope"], operation_id
        assert operation["x-mutation"] == ports[operation_id]["mutation"], operation_id


def test_error_envelope_tables_match_errors_yaml(errors) -> None:
    for code, message in MESSAGE_SAFE.items():
        contract = errors[code.value]
        assert message == contract["message_safe_template_vi"], code.value
        assert DETAILS_SAFE_KEYS[code] == frozenset(contract["details_safe_keys"]), code.value
        assert SCOPE[code] == contract["scope"]
        assert RETRY_CLASS[code] == contract["retry_class"]


def test_http_status_table_matches_the_contract_responses(openapi_document) -> None:
    """Every status this card returns is one the contract declares for that path.

    The mapping is asserted per path, so "403 means CSRF_REJECTED on logout" is checked
    against the document's own response description rather than against a memory of it.
    """
    assert (HTTP_STATUS[ErrorCode.UNAUTHORIZED], HTTP_STATUS[ErrorCode.CSRF_REJECTED]) == (
        401,
        403,
    )
    assert HTTP_STATUS[ErrorCode.RATE_LIMITED] == 429
    assert HTTP_STATUS[ErrorCode.STORAGE_WRITE_FAILED] == 503

    responses = openapi_document["paths"]["/v1/auth/logout"]["post"]["responses"]
    assert "CSRF_REJECTED" in responses["403"]["description"]
    assert "UNAUTHORIZED" in responses["401"]["description"]

    login_responses = openapi_document["paths"]["/v1/auth/login"]["post"]["responses"]
    assert "RATE_LIMITED" in login_responses["429"]["description"]
    assert "STORAGE_WRITE_FAILED" in login_responses["503"]["description"]


def test_wire_models_match_the_openapi_components(openapi_document) -> None:
    """``LoginRequest`` / ``SessionInfo`` are hand-written (``CR-TC-AUTH-04``)."""
    schemas = openapi_document["components"]["schemas"]

    login = schemas["LoginRequest"]
    assert set(LoginRequest.model_fields) == set(login["properties"])
    assert set(login["required"]) == {"username", "password"}
    assert login["additionalProperties"] is False
    assert LoginRequest.model_config["extra"] == "forbid"

    session = schemas["SessionInfo"]
    assert set(SessionInfo.model_fields) == set(session["properties"])
    assert session["required"] == ["authenticated"]
    assert session["additionalProperties"] is False
    with pytest.raises(ValidationError):
        LoginRequest(username="owner", password="short")  # < minLength 8


# --------------------------------------------------------------------------------------
# The PROVISIONAL numbers of contracts/ops/secrets.md §2, restated in code
# --------------------------------------------------------------------------------------


def test_session_and_hashing_parameters_match_secrets_md() -> None:
    """Each of these has a number, a unit and a rationale line in the contract."""
    assert (ARGON2_MEMORY_COST_KIB, ARGON2_TIME_COST, ARGON2_PARALLELISM) == (64 * 1024, 3, 1)
    assert IDLE_TIMEOUT_MS == 12 * 60 * 60 * 1000
    assert ABSOLUTE_TIMEOUT_MS == 30 * 24 * 60 * 60 * 1000
    assert (LOGIN_FAIL_THRESHOLD, LOGIN_FAIL_WINDOW_MS) == (5, 15 * 60 * 1000)
    assert LOCKOUT_DURATION_MS == 15 * 60 * 1000


def test_csrf_comparison_rejects_missing_and_mismatched() -> None:
    token = new_csrf_token()
    assert csrf_matches(token, token)
    assert not csrf_matches(token, None)
    assert not csrf_matches(None, token)
    assert not csrf_matches(None, None)
    assert not csrf_matches(token, new_csrf_token())


#: Every fixture named in card §2 item 5, and what this card does with it. A fixture the
#: card is told to read and then never mentions again is the defect ``F-A3R1-09`` records,
#: so the accounting is in code rather than only in prose.
CARD_FIXTURES: dict[str, str] = {
    "recovery/h-unauthenticated-owner-api": "EXERCISED — SC40, test_denied_edges.py",
    "recovery/i-collector-token-calls-save": "EXERCISED — SC41, test_denied_edges.py",
    "boundary/a-default-deny-sweep-36-edges": "EXERCISED — SC49, all 36 rows partitioned",
    "ui/sc51-first-time-setup": "EXERCISED — SC51 login step, session row count",
    "recovery/g-ssrf-redirect-private": (
        "NOT_RUN — SC39 is an SSRF case on `research.fetch_work_metadata`, owned by "
        "MOD-research-connector. It reaches no auth code path: the boundary it tests is "
        "per-redirect-hop egress (CAPABILITY_DENIED / SOURCE_METADATA_UNAVAILABLE), not a "
        "security scheme. No connector card exists in M1, so it is recorded NOT_RUN with "
        "this reason rather than left silent (F-A3R1-09)."
    ),
}


def test_every_card_fixture_is_readable_and_accounted_for(fixture_loader) -> None:
    """Guards the oracle itself: an unreadable fixture is a BLOCKED result, not a pass.

    The accounting is asserted too -- each of the five fixtures card §2 names is either
    EXERCISED (and says where) or NOT_RUN (and says why).
    """
    for ref, disposition in CARD_FIXTURES.items():
        assert json.dumps(fixture_loader(ref).data)
        assert disposition.startswith(("EXERCISED", "NOT_RUN")), ref
        if disposition.startswith("NOT_RUN"):
            assert len(disposition) > 60, f"{ref}: NOT_RUN needs a reason, not a label"


def test_the_not_run_fixture_is_out_of_this_cards_reach(fixture_loader) -> None:
    """``recovery/g-ssrf-redirect-private``: named in §2, and demonstrably not ours.

    Rather than asserting nothing, this reads the fixture and shows *why* it is NOT_RUN --
    its operation belongs to another module and its error codes are not this card's.
    """
    fixture = fixture_loader("recovery/g-ssrf-redirect-private")
    text = json.dumps(fixture.data, ensure_ascii=False)
    assert "research.fetch_work_metadata" in text
    for owned_code in ("UNAUTHORIZED", "CSRF_REJECTED"):
        assert owned_code not in text, owned_code
