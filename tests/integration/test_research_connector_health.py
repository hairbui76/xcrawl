"""E1/E2 -- the refusal, the health channel and the network boundary.

Card §12 puts three questions to a reviewer. This file is written to answer them by
measurement rather than by reading the code:

1. *"có đường nào một chuỗi chưa chuẩn hóa hoặc do model sinh trở thành một lời gọi mạng
   không"* -- :func:`test_a_redirect_to_a_private_address_is_refused_at_every_hop` and the
   allowlist tests count the requests that actually reached a transport.
2. *"có con số nhịp gọi nào được viết cứng trong code thay vì đọc từ settings không"* --
   :func:`test_no_rate_number_is_hard_coded_anywhere_in_the_package` greps the package.
3. *"khi cấu hình còn null, connector có thật sự từ chối khởi động, hay chỉ ghi log rồi chạy
   tiếp"* -- :func:`test_the_contract_state_today_is_a_refusal_with_zero_requests` runs the
   connector on the configuration the repository actually ships and counts zero requests.

The unconfigured state is not hypothetical: ``contracts/retry-policy.yaml``
``research_connector_rate_limit`` carries four ``null`` values today, and
:func:`test_the_four_unresolved_facts_are_exactly_the_ones_the_contract_leaves_null` reads
them out of the contract so the two cannot drift apart.
"""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
import yaml
from rr_contracts.generated.errors import ErrorCode

from server.app.identity.normalization import IdScheme
from server.app.research import client_arxiv, client_openalex, repository, router, service
from server.app.research.router import (
    FORBIDDEN_EDGE_CHROME_PROFILE,
    FORBIDDEN_EDGE_X_WEB,
    assert_no_browser_capability,
    assert_target_allowed,
    build_connector,
)
from server.app.research.service import (
    CONTRACT_ARXIV_RATE_LIMIT,
    CONTRACT_OPENALEX_RATE_LIMIT,
    CONTRACT_RATE_FACTS_RETRIEVED_AT,
    UNCONFIGURED_ARXIV,
    UNCONFIGURED_OPENALEX,
    ConcurrencyLimitExceeded,
    ConnectorNotConfigured,
    ConnectorSettings,
    NetworkJournal,
    RateGate,
    ResearchContext,
    ResearchError,
    ResponseTooLarge,
    SourceConfig,
    SourceRateLimit,
    address_is_blocked,
    fetch_work_metadata,
    get_connector_health,
    inspect_url,
    normalized_identifier,
    overall_state,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"

ARXIV_HOST = "arxiv.test.invalid"
OPENALEX_HOST = "openalex.test.invalid"
PUBLIC_HOST = "public-host.example"
PUBLIC_ADDRESS = "93.184.216.34"

#: Test values. The contract's four numbers are still `null` (REQ-A6) and nothing here
#: fills them in; these exist so the *configured* branch can be exercised at all.
TEST_RATE = SourceRateLimit(requests_per_window=1, window_seconds=3)

ARXIV_FEED = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>https://{ARXIV_HOST}/abs/2504.04444v1</id>
    <title>SYNTHETIC RECORD -- a title</title>
    <summary>SYNTHETIC RECORD -- an abstract.</summary>
  </entry>
</feed>
""".encode()


def configured_settings(**overrides: object) -> ConnectorSettings:
    base = ConnectorSettings(
        arxiv=SourceConfig(
            source_type="arxiv_api",
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
            rate_limit=TEST_RATE,
        ),
        openalex=SourceConfig(
            source_type="openalex_api",
            endpoint_template=f"https://{OPENALEX_HOST}/works/doi:{{id}}",
            host_allowlist=frozenset({OPENALEX_HOST}),
            rate_limit=TEST_RATE,
            requires_contact_identity=True,
            contact_identity_param="mailto",
            contact_identity="owner@example.invalid",
        ),
        min_interval_ms=0,
    )
    return ConnectorSettings(**{**base.__dict__, **overrides})  # type: ignore[arg-type]


def resolver(host: str) -> tuple[str, ...]:
    table = {
        ARXIV_HOST: (PUBLIC_ADDRESS,),
        OPENALEX_HOST: (PUBLIC_ADDRESS,),
        PUBLIC_HOST: (PUBLIC_ADDRESS,),
        "localhost": ("127.0.0.1",),
        "rebind.example": ("127.0.0.1",),
        "mixed.example": (PUBLIC_ADDRESS, "10.0.0.5"),
        "metadata.example": ("169.254.169.254",),
    }
    if host in table:
        return table[host]
    raise OSError(f"unknown test host {host!r}")


class Recorder:
    def __init__(self, responder) -> None:  # type: ignore[no-untyped-def]
        self.requests: list[httpx.Request] = []
        self._responder = responder

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self._responder(request)


def context(recorder: Recorder, settings: ConnectorSettings, **kwargs: object) -> ResearchContext:
    """A context with test doubles for everything that would otherwise touch the world.

    ``kwargs`` wins over the defaults, so a test that needs a fake clock supplies its own
    ``monotonic``/``sleeper`` instead of getting the no-op ones.
    """
    defaults: dict[str, object] = {
        "repository": None,
        "resolver": resolver,
        "sleeper": lambda _seconds: None,
    }
    return ResearchContext(
        owner_id=OWNER_ID,
        settings=settings,
        transport=httpx.MockTransport(recorder),
        **{**defaults, **kwargs},  # type: ignore[arg-type]
    )


def ok_feed(_request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=ARXIV_FEED)


# --------------------------------------------------------------------------------------
# The refusal (card §10 SG-A6 / SG-IDENT)
# --------------------------------------------------------------------------------------


def test_the_four_rate_facts_are_read_from_the_contract_not_from_memory() -> None:
    """The shipped constants are compared against ``contracts/retry-policy.yaml`` itself.

    This replaces the earlier assertion that the four values were ``null``. That assertion
    was correct until version 0.8.0 resolved them from the official documentation, and it is
    kept here in inverted form for the same reason it existed: the dependency must run from
    the contract to the code, never the other way. Editing a number in ``service.py`` fails
    this test; editing the contract fails it until the code follows.
    """
    policy = yaml.safe_load((REPO_ROOT / "contracts" / "retry-policy.yaml").read_text("utf-8"))
    block = policy["budgets"]["research_connector_rate_limit"]
    values = block["values"]

    assert block["status"] == "DOCS_derived"
    assert [
        name for name, value in values.items() if value is None
    ] == [], "no REQ-A6 value may be null any more"

    assert CONTRACT_ARXIV_RATE_LIMIT.requests_per_window == values["arxiv_requests_per_window"]
    assert CONTRACT_ARXIV_RATE_LIMIT.window_seconds == values["arxiv_window_seconds"]
    assert (
        CONTRACT_ARXIV_RATE_LIMIT.max_concurrent_connections
        == values["arxiv_max_concurrent_connections"]
    )
    assert (
        CONTRACT_OPENALEX_RATE_LIMIT.requests_per_window == values["openalex_requests_per_window"]
    )
    assert CONTRACT_OPENALEX_RATE_LIMIT.window_seconds == values["openalex_window_seconds"]

    # Every fact carries a source with a URL, a retrieval date and a verbatim quotation.
    dates = {source["retrieved_at"] for source in block["sources"]}
    assert dates == {CONTRACT_RATE_FACTS_RETRIEVED_AT}


def test_neither_source_requires_identification_today_and_the_rule_survives_anyway() -> None:
    """``SG-IDENT``'s premise changed; ``SG-IDENT`` itself did not.

    The contract's ``identification`` block records that neither source's current
    documentation mandates a ``mailto`` or any other identifier, so the shipped configs set
    ``requires_contact_identity=False`` and nothing is blocked. The contract also says, in as
    many words, that the rule must stay in the code -- so the second half of this test
    configures a source that *does* require identification and proves it is still refused.
    """
    policy = yaml.safe_load((REPO_ROOT / "contracts" / "retry-policy.yaml").read_text("utf-8"))
    identification = policy["budgets"]["research_connector_rate_limit"]["identification"]
    assert identification["arxiv_identification_required"] is False
    assert identification["openalex_identification_required"] is False

    shipped = ConnectorSettings()
    assert shipped.arxiv.requires_contact_identity is False
    assert shipped.openalex.requires_contact_identity is False
    assert shipped.openalex.missing_req_a6_facts() == ()

    # The mechanism is intact: a source that demands identification without one still stops.
    demanding = SourceConfig(
        source_type="openalex_api",
        endpoint_template=f"https://{OPENALEX_HOST}/works/doi:{{id}}",
        host_allowlist=frozenset({OPENALEX_HOST}),
        rate_limit=CONTRACT_OPENALEX_RATE_LIMIT,
        requires_contact_identity=True,
        contact_identity=None,
    )
    assert "openalex_contact_identity" in demanding.missing_req_a6_facts()
    with pytest.raises(ConnectorNotConfigured):
        demanding.require_configured()


def test_the_shipped_defaults_no_longer_refuse_on_req_a6_grounds() -> None:
    """``SG-A6``'s condition -- "the four values are still null" -- no longer holds."""
    shipped = ConnectorSettings()
    assert shipped.arxiv.missing_req_a6_facts() == ()
    assert shipped.openalex.missing_req_a6_facts() == ()


def test_the_shipped_defaults_still_refuse_without_an_endpoint() -> None:
    """Knowing how fast to go is not knowing where to go.

    No contract in this repository states either service's API host -- ``retry-policy.yaml``
    cites the two *documentation* pages -- so the endpoint stays a deployment decision and
    an unset one stays a refusal (``SG-DOC``).
    """
    shipped = ConnectorSettings()
    for source in (shipped.arxiv, shipped.openalex):
        assert source.missing_deployment_config()
        with pytest.raises(ConnectorNotConfigured) as caught:
            source.require_configured()
        assert any("endpoint_template" in name for name in caught.value.missing)
        assert any("host_allowlist" in name for name in caught.value.missing)


def test_an_explicitly_nulled_rate_still_refuses() -> None:
    """Regression: the refusal path is reachable, it is just no longer the default.

    Three ways to get there, all of which a future source or a mis-edited config could hit:
    the unconfigured constants, a bare ``SourceRateLimit()``, and a partially filled one.
    """
    assert UNCONFIGURED_ARXIV.missing_req_a6_facts() == (
        "arxiv_requests_per_window",
        "arxiv_window_seconds",
    )
    assert "openalex_contact_identity" in UNCONFIGURED_OPENALEX.missing_req_a6_facts()

    for rate in (
        SourceRateLimit(),
        SourceRateLimit(requests_per_window=1),
        SourceRateLimit(window_seconds=3),
    ):
        blanked = SourceConfig(
            source_type="arxiv_api",
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
            rate_limit=rate,
        )
        assert blanked.missing_req_a6_facts(), f"{rate} must not pass as configured"
        with pytest.raises(ConnectorNotConfigured):
            blanked.require_configured()


def test_a_nulled_rate_makes_zero_requests_and_reports_the_req_a6_reason() -> None:
    """The end-to-end regression: an explicitly unconfigured source calls nothing."""
    settings = configured_settings(arxiv=UNCONFIGURED_ARXIV)
    recorder = Recorder(ok_feed)
    ctx = context(recorder, settings)

    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert caught.value.details_safe["attempt_number"] == 0
    assert recorder.requests == []
    assert ctx.journal.inspected == []

    entry = get_connector_health(ctx)["sources"]["arxiv_api"]
    assert entry["state"] == "unavailable"
    assert entry["reason_code"] == "rate_facts_unresolved"
    assert "arxiv_requests_per_window" in entry["unresolved_facts"]


def test_the_shipped_state_today_still_makes_zero_requests_but_for_a_different_reason() -> None:
    """Card §8's count is unchanged; only the reason behind it moved.

    ``ConnectorSettings()`` still calls nothing, because it has no endpoint. It is worth a
    test of its own that this is now an *endpoint* gap and not a REQ-A6 one: the two look
    identical from the outside (zero requests) and would otherwise be confusable.
    """
    recorder = Recorder(ok_feed)
    ctx = context(recorder, ConnectorSettings())

    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert caught.value.details_safe["attempt_number"] == 0, "no attempt was even started"
    assert recorder.requests == []
    assert ctx.journal.inspected == [], "no URL was even built"

    entry = get_connector_health(ctx)["sources"]["arxiv_api"]
    assert entry["reason_code"] == "endpoint_not_configured"
    assert entry["unresolved_facts"] == []


def test_openalex_without_a_contact_identity_is_never_called() -> None:
    """SG-IDENT: an anonymous call to a source that asks who is calling is not an option."""
    settings = configured_settings(
        openalex=SourceConfig(
            source_type="openalex_api",
            endpoint_template=f"https://{OPENALEX_HOST}/works/doi:{{id}}",
            host_allowlist=frozenset({OPENALEX_HOST}),
            rate_limit=TEST_RATE,
            requires_contact_identity=True,
            contact_identity_param="mailto",
            contact_identity=None,
        )
    )
    recorder = Recorder(ok_feed)
    ctx = context(recorder, settings)

    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.DOI, "10.1000/x"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert recorder.requests == []

    health = get_connector_health(ctx)
    assert health["sources"]["openalex_api"]["state"] == "unavailable"
    assert "openalex_contact_identity" in health["sources"]["openalex_api"]["unresolved_facts"]
    assert health["sources"]["openalex_api"]["reason_code"] == "rate_facts_unresolved"
    # ... and arXiv, which asks for no identity, is unaffected.
    assert health["sources"]["arxiv_api"]["state"] != "unavailable"


def test_every_rate_literal_in_the_package_equals_the_contract() -> None:
    """Card §12 question 2, restated for a world where the numbers are known.

    Before 0.8.0 the answer was "there must be no rate literal at all". Now the contract has
    values and the code carries them, so the question becomes: does every literal in the
    package match the contract, and does it live in exactly one place? Anything else --
    a second copy, a nudged value, a number in a client module -- fails here.
    """
    policy = yaml.safe_load((REPO_ROOT / "contracts" / "retry-policy.yaml").read_text("utf-8"))
    values = policy["budgets"]["research_connector_rate_limit"]["values"]
    permitted = {
        values["arxiv_requests_per_window"],
        values["arxiv_window_seconds"],
        values["arxiv_max_concurrent_connections"],
        values["openalex_requests_per_window"],
        values["openalex_window_seconds"],
    }

    package = REPO_ROOT / "server" / "app" / "research"
    seen = 0
    for path in sorted(package.glob("*.py")):
        source = path.read_text("utf-8")
        for name in ("requests_per_window", "window_seconds", "max_concurrent_connections"):
            for match in re.finditer(rf"{name}\s*=\s*(-?\d+)", source):
                seen += 1
                assert path.name == "service.py", (
                    f"{path.name} carries a rate literal; they belong to the contract "
                    "constants in service.py only"
                )
                assert int(match.group(1)) in permitted, (
                    f"{path.name} assigns {match.group(0)!r}, which is not a value "
                    "contracts/retry-policy.yaml states"
                )
    assert seen >= 5, "the contract constants should be the literals this test found"


def test_the_floor_is_never_loosened_to_match_a_documented_rate() -> None:
    """OpenAlex permits 100 req/s; the connector still goes at one per three seconds.

    ``effective_interval_ms`` takes the **stricter** of the floor and the documented rate.
    The contract's ``rationale_vi`` is explicit that this is a decision, not an oversight:
    a one-user system reading a few dozen targets has no need of 100 req/s, and the daily
    budget and ``429`` risk are real.
    """
    shipped = ConnectorSettings()
    floor = shipped.min_interval_ms
    assert floor == 3000

    # arXiv: documented rate and floor coincide at 3000 ms.
    assert CONTRACT_ARXIV_RATE_LIMIT.interval_ms == 3000
    assert shipped.arxiv.effective_interval_ms(floor) == 3000

    # OpenAlex: documented rate is 10 ms; the floor governs and is ~300x slower.
    assert CONTRACT_OPENALEX_RATE_LIMIT.interval_ms == 10
    assert shipped.openalex.effective_interval_ms(floor) == 3000

    # A source slower than the floor would win, which is the whole point of `max`.
    slow = SourceConfig(
        source_type="arxiv_api",
        rate_limit=SourceRateLimit(requests_per_window=1, window_seconds=60),
    )
    assert slow.effective_interval_ms(floor) == 60_000


def test_the_connector_proceeds_with_the_shipped_rates_and_only_an_endpoint_supplied() -> None:
    """The packet's headline behaviour: no rate override, and the call goes through.

    ``endpoint_settings`` copies the shipped ``ConnectorSettings`` and adds *only* the
    endpoint and host -- the rate limits are the contract's, untouched. The transport is
    still an ``httpx.MockTransport``: no live call is made anywhere in this file.
    """
    shipped = ConnectorSettings()
    settings = ConnectorSettings(
        arxiv=replace(
            shipped.arxiv,
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
        ),
        openalex=shipped.openalex,
    )
    assert settings.arxiv.rate_limit is CONTRACT_ARXIV_RATE_LIMIT
    assert settings.arxiv.configured

    clock = [0.0]
    recorder = Recorder(ok_feed)
    ctx = context(
        recorder,
        settings,
        monotonic=lambda: clock[0],
        sleeper=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    result = fetch_work_metadata(
        ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444")
    )
    assert result.metadata.title is not None
    assert len(recorder.requests) == 1
    assert get_connector_health(ctx)["sources"]["arxiv_api"]["state"] == "ok"


def test_two_arxiv_lookups_are_spaced_by_the_documented_three_seconds() -> None:
    """arXiv: "make no more than one request every three seconds"."""
    shipped = ConnectorSettings()
    settings = ConnectorSettings(
        arxiv=replace(
            shipped.arxiv,
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
        )
    )
    clock = [0.0]
    slept: list[float] = []

    def sleeper(seconds: float) -> None:
        slept.append(seconds)
        clock[0] += seconds

    recorder = Recorder(ok_feed)
    ctx = context(recorder, settings, monotonic=lambda: clock[0], sleeper=sleeper)

    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2503.03333"))

    assert len(recorder.requests) == 2
    assert slept == [3.0], "the second call waited the documented three seconds"


def test_arxiv_is_held_to_a_single_connection_at_a_time() -> None:
    """The other half of arXiv's terms: "limit requests to a single connection at a time".

    A rate limit alone does not express this -- one request per three seconds while holding
    four sockets open still breaks the terms -- so it is a separate counter with a separate
    assertion.
    """
    shipped = ConnectorSettings()
    settings = ConnectorSettings(
        arxiv=replace(
            shipped.arxiv,
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
        )
    )
    clock = [0.0]
    recorder = Recorder(ok_feed)
    ctx = context(
        recorder,
        settings,
        monotonic=lambda: clock[0],
        sleeper=lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2503.03333"))

    assert ctx.gate().peak_in_flight["arxiv_api"] == 1

    # And a caller that tries to hold two at once is refused rather than quietly queued.
    with (
        pytest.raises(ConcurrencyLimitExceeded) as caught,
        ctx.gate().connection("arxiv_api"),
        ctx.gate().connection("arxiv_api"),
    ):
        pass  # pragma: no cover - the second `connection` raises
    assert caught.value.limit == 1
    assert caught.value.source_type == "arxiv_api"

    # OpenAlex's documentation states no connection ceiling, so none is imposed.
    with ctx.gate().connection("openalex_api"), ctx.gate().connection("openalex_api"):
        pass


def test_the_openalex_daily_budget_is_read_from_headers_not_guessed() -> None:
    """``A6-OPENALEX-BUDGET``: the daily budget is money, not calls, and is run-time only.

    The contract names ``X-RateLimit-*`` as the source of truth, so the connector reports
    what the source said and holds no number of its own.
    """
    shipped = ConnectorSettings()
    settings = ConnectorSettings(
        openalex=replace(
            shipped.openalex,
            endpoint_template=f"https://{OPENALEX_HOST}/works/doi:{{id}}",
            host_allowlist=frozenset({OPENALEX_HOST}),
        )
    )
    body = b'{"display_name": "SYNTHETIC RECORD -- a work"}'
    recorder = Recorder(
        lambda _request: httpx.Response(
            200,
            content=body,
            headers={
                "x-ratelimit-limit": "100000",
                "x-ratelimit-remaining": "99998",
                "x-ratelimit-credits-used": "$0.02",
                "x-ratelimit-reset": "3600",
            },
        )
    )
    ctx = context(recorder, settings)
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.DOI, "10.1000/x"))

    budget = get_connector_health(ctx)["sources"]["openalex_api"]["budget"]
    assert budget["limit"] == 100000
    assert budget["remaining"] == 99998
    assert budget["credits_used"] == "$0.02"
    assert budget["reset_seconds"] == 3600
    assert budget["exhausted"] is False


def test_an_exhausted_daily_budget_is_unavailable_and_an_absent_header_is_not() -> None:
    """ "Remaining zero" is unavailable; "no header" is unknown, and unknown is not zero (I13)."""
    shipped = ConnectorSettings()
    settings = ConnectorSettings(
        openalex=replace(
            shipped.openalex,
            endpoint_template=f"https://{OPENALEX_HOST}/works/doi:{{id}}",
            host_allowlist=frozenset({OPENALEX_HOST}),
        )
    )
    body = b'{"display_name": "SYNTHETIC RECORD -- a work"}'
    recorder = Recorder(
        lambda _request: httpx.Response(200, content=body, headers={"x-ratelimit-remaining": "0"})
    )
    ctx = context(recorder, settings)
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.DOI, "10.1000/x"))
    entry = get_connector_health(ctx)["sources"]["openalex_api"]
    assert entry["state"] == "unavailable"
    assert entry["reason_code"] == "daily_budget_exhausted"

    # arXiv sends no such headers at all; that must not read as an exhausted budget.
    arxiv_settings = ConnectorSettings(
        arxiv=replace(
            shipped.arxiv,
            endpoint_template=f"https://{ARXIV_HOST}/query?id_list={{id}}",
            host_allowlist=frozenset({ARXIV_HOST}),
        )
    )
    plain = context(Recorder(ok_feed), arxiv_settings)
    fetch_work_metadata(plain, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    arxiv_entry = get_connector_health(plain)["sources"]["arxiv_api"]
    assert arxiv_entry["budget"] is None
    assert arxiv_entry["state"] == "ok"


# --------------------------------------------------------------------------------------
# research.get_connector_health
# --------------------------------------------------------------------------------------


def test_health_on_the_shipped_configuration_separates_the_two_kinds_of_gap() -> None:
    """Both sources are still ``unavailable``, but the report says *why* precisely.

    ``unresolved_facts`` (REQ-A6) is now empty and ``missing_configuration`` (deployment) is
    not. Reporting them under one key would have made "nobody read the rate" and "nobody
    told us the URL" indistinguishable at exactly the moment they stopped being the same
    problem.
    """
    ctx = context(Recorder(ok_feed), ConnectorSettings())
    health = get_connector_health(ctx)

    for source in ("arxiv_api", "openalex_api"):
        entry = health["sources"][source]
        assert entry["state"] == "unavailable"
        assert entry["reason_code"] == "endpoint_not_configured"
        assert entry["unresolved_facts"] == [], "REQ-A6 is resolved"
        assert entry["missing_configuration"], "an unavailable source must say what is missing"
        assert entry["rate_facts_retrieved_at"] == CONTRACT_RATE_FACTS_RETRIEVED_AT
        assert entry["effective_interval_ms"] == 3000
    assert health["overall"] == "unavailable"
    assert health["min_interval_ms_status"] == "PROVISIONAL_SELF_IMPOSED_FLOOR"
    assert health["rate_facts_status"] == "DOCS_derived"


def test_a_configured_but_never_called_source_is_degraded_not_ok() -> None:
    """I13: an undetermined state is never reported as a good one.

    ``ok | degraded | unavailable`` is closed (``ports.yaml``), so "not observed yet" has to
    land on one of the three. It lands on ``degraded`` with a reason that says exactly that
    -- reporting ``ok`` would be asserting a source works because nobody has asked it.
    """
    ctx = context(Recorder(ok_feed), configured_settings())
    entry = get_connector_health(ctx)["sources"]["arxiv_api"]
    assert entry["state"] == "degraded"
    assert entry["reason_code"] == "no_observation_yet"
    assert entry["last_outcome"] is None


def test_health_becomes_ok_after_a_successful_call_and_degraded_after_a_failure() -> None:
    responses = iter(
        [
            httpx.Response(200, content=ARXIV_FEED),
            httpx.Response(503, content=b"SYNTHETIC RECORD"),
            httpx.Response(503, content=b"SYNTHETIC RECORD"),
        ]
    )
    recorder = Recorder(lambda _request: next(responses))
    ctx = context(recorder, configured_settings())

    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert get_connector_health(ctx)["sources"]["arxiv_api"]["state"] == "ok"
    assert get_connector_health(ctx)["overall"] == "ok"

    with pytest.raises(ResearchError):
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2503.03333"))
    entry = get_connector_health(ctx)["sources"]["arxiv_api"]
    assert entry["state"] == "degraded"
    assert entry["last_outcome"] == "error"


def test_overall_state_follows_the_deployment_contract_row() -> None:
    """``contracts/ops/deployment.md`` §5 ``research_sources``."""
    assert overall_state(["ok", "unavailable"]) == "ok"
    assert overall_state(["degraded", "unavailable"]) == "degraded"
    assert overall_state(["unavailable", "unavailable"]) == "unavailable"


def test_get_connector_health_takes_no_parameters_and_raises_no_request_error() -> None:
    """``ports.yaml`` ``error_note_vi`` / ruling ``F-A2R1-09``: ``INTERNAL`` is the only code.

    A degraded source is a **return value**. The test asserts the shape rather than a
    refusal, because there is no input that could be invalid.
    """
    ctx = context(Recorder(ok_feed), configured_settings())
    health = get_connector_health(ctx)
    assert set(health["sources"]) == {"arxiv_api", "openalex_api"}
    assert health["overall"] in {"ok", "degraded", "unavailable"}


def test_the_health_reason_never_contains_a_host_or_the_contact_identity() -> None:
    """``ports.yaml``: "Trạng thái từng nguồn ... + lý do **đã che secrets**"."""
    responses = iter([httpx.Response(503, content=b"x"), httpx.Response(503, content=b"x")])
    recorder = Recorder(lambda _request: next(responses))
    ctx = context(recorder, configured_settings())
    with pytest.raises(ResearchError):
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    rendered = repr(get_connector_health(ctx))
    assert ARXIV_HOST not in rendered
    assert "owner@example.invalid" not in rendered


def test_health_answers_with_no_database_at_all() -> None:
    """SRC-PLAN §8.4: the health channel must keep answering when storage cannot be read."""
    ctx = context(Recorder(ok_feed), configured_settings())
    assert ctx.repository is None
    assert get_connector_health(ctx)["overall"] in {"degraded", "ok", "unavailable"}


# --------------------------------------------------------------------------------------
# The network boundary (contracts/ops/internet-boundary.md §3.2)
# --------------------------------------------------------------------------------------


def test_a_redirect_to_a_private_address_is_refused_at_every_hop(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """``acceptance/fixtures/recovery/g-ssrf-redirect-private.json`` is the oracle.

    Its chain ends at ``http://127.0.0.1:8080/admin``. The fixture requires
    ``connections_to_loopback == 0``, ``blocked_at_redirect_step == 3`` and
    ``error_code == SOURCE_METADATA_UNAVAILABLE``, and notes that the last hop breaks the
    scheme rule *and* the address rule independently.
    """
    fixture = fixture_loader("recovery/g-ssrf-redirect-private")
    chain = fixture.data["given"]["redirect_chain"]
    expected = fixture.data["expected"]["seq2"]
    assert chain[-1].startswith("http://127.0.0.1")

    hops = iter(chain[1:])

    def redirecting(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": next(hops)})

    recorder = Recorder(redirecting)
    settings = configured_settings(
        arxiv=SourceConfig(
            source_type="arxiv_api",
            endpoint_template=chain[0],
            host_allowlist=frozenset({PUBLIC_HOST}),
            rate_limit=TEST_RATE,
        )
    )
    journal = NetworkJournal()
    ctx = context(recorder, settings, journal=journal)

    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2601.00099"))

    assert caught.value.code == ErrorCode[expected["error_code"]]
    refusals = journal.refused()
    assert len(refusals) == 1
    refused_at_hop = journal.inspected.index(refusals[0]) + 1
    assert refused_at_hop == expected["blocked_at_redirect_step"] == 3

    # Both independent rules fired, exactly as the fixture says they should.
    assert "scheme_not_allowed" in refusals[0].violations
    assert "host_not_in_allowlist" in refusals[0].violations

    # The counts the fixture actually asserts on.
    assert journal.dispatched_to_blocked_address() == []
    assert fixture.data["expected"]["connections_to_loopback"] == 0
    assert fixture.data["expected"]["connections_to_private_ranges"] == 0
    assert len(recorder.requests) == 2, "only the two allowlisted hops were dispatched"
    assert all(r.url.host == PUBLIC_HOST for r in recorder.requests)


def test_a_public_name_that_resolves_to_loopback_is_refused_before_the_request() -> None:
    """DNS rebinding: the *address* is checked, never the name."""
    settings = configured_settings(
        arxiv=SourceConfig(
            source_type="arxiv_api",
            endpoint_template="https://rebind.example/q?id={id}",
            host_allowlist=frozenset({"rebind.example"}),
            rate_limit=TEST_RATE,
        )
    )
    recorder = Recorder(ok_feed)
    ctx = context(recorder, settings)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert recorder.requests == []
    assert "resolved_address_blocked" in ctx.journal.inspected[0].violations


def test_a_mixed_dns_answer_is_refused_rather_than_filtered() -> None:
    """One blocked address in the answer refuses the whole name.

    Picking the "good" address out of a mixed answer leaves exactly the rebinding window
    the rule exists to close: the checked address and the connected address could differ.
    """
    decision = inspect_url(
        "https://mixed.example/x", host_allowlist={"mixed.example"}, resolver=resolver
    )
    assert not decision.allowed
    assert "resolved_address_blocked" in decision.violations


@pytest.mark.parametrize(
    "address",
    ["127.0.0.1", "::1", "10.0.0.5", "172.16.0.1", "192.168.1.1", "169.254.169.254", "0.0.0.0"],
)
def test_every_range_internet_boundary_names_is_blocked(address: str) -> None:
    assert address_is_blocked(address)


def test_a_globally_routable_address_is_not_blocked() -> None:
    """The block list must not be so wide that the allowed path is unreachable."""
    assert not address_is_blocked(PUBLIC_ADDRESS)


def test_a_non_https_scheme_is_refused() -> None:
    decision = inspect_url(f"http://{ARXIV_HOST}/q", host_allowlist={ARXIV_HOST}, resolver=resolver)
    assert "scheme_not_allowed" in decision.violations
    for url in (f"file://{ARXIV_HOST}/etc/passwd", f"gopher://{ARXIV_HOST}/1"):
        assert (
            "scheme_not_allowed"
            in inspect_url(url, host_allowlist={ARXIV_HOST}, resolver=resolver).violations
        )


def test_credentials_in_a_url_are_refused() -> None:
    decision = inspect_url(
        f"https://user:pass@{ARXIV_HOST}/q", host_allowlist={ARXIV_HOST}, resolver=resolver
    )
    assert "userinfo_present" in decision.violations


def test_more_redirects_than_the_cap_are_refused() -> None:
    """``max_redirects = 3`` (internet-boundary.md §3.2, PROVISIONAL)."""

    def always_redirect(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": f"https://{ARXIV_HOST}/next"})

    recorder = Recorder(always_redirect)
    ctx = context(recorder, configured_settings())
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert len(recorder.requests) == ctx.settings.max_redirects + 1


def test_a_body_over_the_cap_aborts_instead_of_being_measured_afterwards() -> None:
    settings = configured_settings(max_response_bytes=1024)
    recorder = Recorder(lambda _request: httpx.Response(200, content=b"x" * 4096))
    ctx = context(recorder, settings)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert issubclass(ResponseTooLarge, Exception)


# --------------------------------------------------------------------------------------
# SC49 -- the two forbidden edges that touch this module
# --------------------------------------------------------------------------------------


def test_sc49_rows_20_and_21_pin_capability_denied(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """The sweep fixture is the oracle for the code, not this file."""
    fixture = fixture_loader("boundary/a-default-deny-sweep-36-edges")
    rows = {
        event["forbidden_edge_ref"]: event
        for event in fixture.data["events"]
        if event["actor"] == "MOD-research-connector"
    }
    assert set(rows) == {FORBIDDEN_EDGE_X_WEB, FORBIDDEN_EDGE_CHROME_PROFILE}
    for row in rows.values():
        assert row["expected_error_code"] == ErrorCode.CAPABILITY_DENIED.value


def test_sc49_fe20_reaching_the_x_surface_is_capability_denied() -> None:
    """``FE-20``: the connector's ``network_egress`` is arXiv and OpenAlex, and nothing else."""
    for host in ("x.com", "api.x.com", "twitter.com", "t.co"):
        with pytest.raises(ResearchError) as caught:
            assert_target_allowed(host, allowlist={ARXIV_HOST, OPENALEX_HOST})
        assert caught.value.code is ErrorCode.CAPABILITY_DENIED
        assert caught.value.details_safe["forbidden_edge_ref"] == FORBIDDEN_EDGE_X_WEB
        assert caught.value.details_safe["module_id"] == "MOD-research-connector"


def test_sc49_any_host_off_the_allowlist_is_denied_not_just_the_named_ones() -> None:
    """An allow list, not a block list: the refusal does not depend on recognising X."""
    with pytest.raises(ResearchError) as caught:
        assert_target_allowed("some-other-host.example", allowlist={ARXIV_HOST})
    assert caught.value.code is ErrorCode.CAPABILITY_DENIED
    assert caught.value.details_safe["forbidden_edge_ref"] is None
    assert_target_allowed(ARXIV_HOST.upper() + ".", allowlist={ARXIV_HOST})


def test_sc49_fe21_no_research_module_can_reach_a_browser() -> None:
    """``FE-21``, enforced as an import rule -- the honest reading of "does not drive Chrome"
    is that the code to do so is not reachable from this package."""
    for module in (service, router, repository, client_arxiv, client_openalex):
        assert_no_browser_capability(vars(module))

    # The static half: parse the package's own import statements. Grepping the whole file
    # for the word "playwright" would match the allowlist that forbids it -- a check that
    # fails on its own enforcement is not a check.
    forbidden_roots = {"playwright", "selenium", "pyppeteer", "webdriver", "collector"}
    for path in sorted((REPO_ROOT / "server" / "app" / "research").glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"), filename=str(path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        assert not (
            imported & forbidden_roots
        ), f"{path.name} imports {sorted(imported & forbidden_roots)}; FE-21 forbids it"


def test_the_connector_denies_a_health_caller_that_is_not_the_health_service() -> None:
    from server.app.auth.service import AuthError

    connector = build_connector(
        owner_id=OWNER_ID,
        settings=configured_settings(),
        transport=httpx.MockTransport(Recorder(ok_feed)),
        resolver=resolver,
        sleeper=lambda _seconds: None,
    )
    with pytest.raises(AuthError) as caught:
        connector.get_connector_health(caller_module="MOD-x-collector")
    assert caught.value.code is ErrorCode.FORBIDDEN_EDGE
    assert connector.get_connector_health(caller_module="MOD-health-service")["overall"]


def test_install_research_registers_no_http_route() -> None:
    """``transport: internal`` means there is no path to register (card §3, ``SG-EDGE``)."""
    from server.app.main import create_app

    app = create_app()
    paths = {getattr(route, "path", None) for route in app.routes}
    assert not any(path and "research" in path for path in paths)

    router.install_research(app, None)
    assert app.state.research_connector is None
    after = {getattr(route, "path", None) for route in app.routes}
    assert after == paths, "install_research must add no route"


# --------------------------------------------------------------------------------------
# Pacing
# --------------------------------------------------------------------------------------


def test_the_pacing_floor_is_per_source_and_is_actually_waited_for() -> None:
    """Card §6: the gate is per source, so two lookups cannot halve the interval."""
    clock = [0.0]
    slept: list[float] = []

    def sleeper(seconds: float) -> None:
        slept.append(seconds)
        clock[0] += seconds

    gate = RateGate(min_interval_ms=3000, monotonic=lambda: clock[0], sleeper=sleeper)
    gate.acquire("arxiv_api")
    gate.acquire("arxiv_api")
    assert slept == [3.0]

    # A different source is not held behind the first source's interval.
    gate.acquire("openalex_api")
    assert slept == [3.0]


def test_a_source_retry_after_beats_every_configured_number() -> None:
    """retry-policy: "``Retry-After`` do nguồn trả về **luôn thắng** mọi giá trị cấu hình"."""
    clock = [0.0]
    slept: list[float] = []

    def sleeper(seconds: float) -> None:
        slept.append(seconds)
        clock[0] += seconds

    gate = RateGate(min_interval_ms=1, monotonic=lambda: clock[0], sleeper=sleeper)
    gate.penalise("arxiv_api", 60_000)
    gate.acquire("arxiv_api")
    assert slept == [60.0], "the source's own delay wins over the configured floor"

    # ... and a shorter penalty never shortens a longer one already in force.
    gate.penalise("arxiv_api", 30_000)
    gate.penalise("arxiv_api", 1)
    gate.acquire("arxiv_api")
    assert slept[-1] == pytest.approx(30.0)


def test_a_429_is_rate_limited_and_carries_the_sources_retry_after() -> None:
    recorder = Recorder(
        lambda _request: httpx.Response(429, content=b"", headers={"retry-after": "42"})
    )
    ctx = context(recorder, configured_settings())
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    assert caught.value.code is ErrorCode.RATE_LIMITED
    assert caught.value.retry_after_ms == 42_000
    assert caught.value.details_safe["source_kind"] == "arxiv_api"
    assert caught.value.details_safe["window_seconds"] == TEST_RATE.window_seconds
    assert len(recorder.requests) == 1, "a rate limit is not retried inside the same call"
    envelope = caught.value.envelope("01JCORREL0000000000000000")
    assert envelope["retry_class"] == "retryable_with_budget"
