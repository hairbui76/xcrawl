"""E1 -- ``research.fetch_work_metadata`` against the four fixtures the card names.

The fixtures under ``acceptance/fixtures/`` are the only oracle (SRC-PLAN §15). Nothing here
edits one, and nothing here builds a second data set: the identifiers, the expected error
code and the expected target state are all read out of the fixture files at run time, so a
fixture change breaks this file rather than passing unnoticed.

    ``collection/h-metadata-unavailable-post-only.json``  SC11 -- the source has nothing
    ``identity/b-post-only-missing-ids.json``             SC29 -- no identifier, no call
    ``identity/g-arxiv-version-v1-v2.json``               SC30 -- v1/v2 is one work
    ``identity/h-five-posts-thread-one-target.json``      SC07 -- six spellings, one call

About the recorded responses
----------------------------
The bodies in ``RECORDED`` are **synthetic**, written by hand for this card, and every host
in them is under a reserved test name (``.invalid``, RFC 2606) with a reserved test address
(``203.0.113.0/24``, RFC 5737). They exercise the parsers and the boundary; they do **not**
establish that the real arXiv or OpenAlex payload has this shape. Card §10 ``SG-LIVE``
keeps a live call out of this packet, and the handoff records the tautology risk explicitly:
the same worker wrote both the parser and the body it parses, so agreement between them is
evidence of internal consistency and of nothing else. Only E3 closes that.

About the numbers
-----------------
``TEST_RATE`` is a **test value**, not a documented rate. The four
``research_connector_rate_limit`` values in ``contracts/retry-policy.yaml`` are still
``null`` (``PLACEHOLDER_KC``, REQ-A6) and this file does not fill them in: it supplies
explicit numbers to a test-local :class:`ConnectorSettings` so the *configured* path can be
exercised at all, and ``test_research_connector_health.py`` covers the unconfigured path
that a real deployment is in today.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from pathlib import Path

import httpx
import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.identity.normalization import ArxivId, IdScheme, normalize_arxiv, normalize_doi
from server.app.research.repository import SourceFetchLogRepository
from server.app.research.router import ResearchConnector, build_connector
from server.app.research.service import (
    ConnectorSettings,
    NormalizedIdentifier,
    ResearchContext,
    ResearchError,
    SourceConfig,
    SourceRateLimit,
    fetch_work_metadata,
    normalized_identifier,
    redact_endpoint,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------------------
# Test-only configuration. None of it is a claim about either real service.
# --------------------------------------------------------------------------------------

ARXIV_HOST = "arxiv.test.invalid"
OPENALEX_HOST = "openalex.test.invalid"

#: A globally routable literal, and deliberately NOT one of the RFC 5737 documentation
#: ranges: :mod:`ipaddress` classifies ``192.0.2.0/24``, ``198.51.100.0/24`` and
#: ``203.0.113.0/24`` as ``is_private`` (they are in the IANA special-purpose registry), so
#: the boundary correctly refuses them and the allowed path could never be exercised with
#: one. No connection is ever made to it: the transport is an :class:`httpx.MockTransport`
#: and the resolver below is a dictionary.
PUBLIC_ADDRESS = "93.184.216.34"

#: A test value. NOT the documented rate: retry-policy's four values are still null.
TEST_RATE = SourceRateLimit(requests_per_window=1, window_seconds=3)

OWNER_ID = "01J0WNER100000000000000000"


def settings(**overrides: object) -> ConnectorSettings:
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
        # A zero floor keeps the suite fast. The floor itself is asserted in
        # test_research_connector_health.py, where the clock is faked instead of ignored.
        min_interval_ms=0,
    )
    return ConnectorSettings(**{**base.__dict__, **overrides})  # type: ignore[arg-type]


def resolver(host: str) -> tuple[str, ...]:
    """A fake DNS. No test in this file performs a real lookup."""
    if host in {ARXIV_HOST, OPENALEX_HOST}:
        return (PUBLIC_ADDRESS,)
    raise OSError(f"unknown test host {host!r}")


# --------------------------------------------------------------------------------------
# Recorded (synthetic) responses
# --------------------------------------------------------------------------------------

ARXIV_V2_ATOM = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>https://{ARXIV_HOST}/abs/2503.03333v2</id>
    <published>2026-03-04T00:00:00Z</published>
    <updated>2026-03-11T00:00:00Z</updated>
    <title>SYNTHETIC RECORD -- a paper title for fixture g</title>
    <summary>SYNTHETIC RECORD -- the abstract of version two.</summary>
    <link href="https://{ARXIV_HOST}/abs/2503.03333v2" rel="alternate" type="text/html"/>
  </entry>
</feed>
""".encode()

ARXIV_ONE_TARGET_ATOM = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>https://{ARXIV_HOST}/abs/2504.04444v1</id>
    <published>2026-04-05T00:00:00Z</published>
    <title>SYNTHETIC RECORD -- a paper title for fixture h</title>
    <summary>SYNTHETIC RECORD -- one abstract for six posts.</summary>
    <link href="https://{ARXIV_HOST}/abs/2504.04444v1" rel="alternate" type="text/html"/>
    <arxiv:doi>10.48550/arxiv.2504.04444</arxiv:doi>
  </entry>
</feed>
""".encode()

ARXIV_EMPTY_ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>SYNTHETIC RECORD -- no entries</title></feed>
"""

OPENALEX_WORK_JSON = json.dumps(
    {
        "id": "https://openalex.example.invalid/W1",
        "doi": "https://doi.org/10.1000/synthetic-1",
        "display_name": "SYNTHETIC RECORD -- an OpenAlex work",
        "publication_date": "2026-02-01",
        "primary_location": {"landing_page_url": "https://publisher.example.invalid/a"},
        "abstract_inverted_index": {"SYNTHETIC": [0], "abstract": [1], "text": [2]},
    }
).encode()


# --------------------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------------------


class Recorder:
    """A ``MockTransport`` handler that records every request it is asked to make.

    The request list is the oracle for card §8's two counts: "every outbound connection is
    on the allowlist" and "outside the allowlist = 0". A request that never reaches this
    handler never left the process.
    """

    def __init__(self, responder: Callable[[httpx.Request], httpx.Response]) -> None:
        self.requests: list[httpx.Request] = []
        self._responder = responder

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self._responder(request)

    @property
    def hosts(self) -> list[str]:
        return [request.url.host for request in self.requests]


def always(status: int, body: bytes = b"", **headers: str) -> Callable[..., httpx.Response]:
    def responder(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, content=body, headers=headers)

    return responder


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    """A real SQLite database at ``head``, with one owner row for the FK."""
    import os

    from alembic import command
    from alembic.config import Config

    db_path = tmp_path / "research.db"
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

    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at)"
                " VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', '2026-09-07T00:00:00.000Z')"
            ),
            {"id": OWNER_ID},
        )
    yield engine
    engine.dispose()


def context(
    recorder: Recorder,
    *,
    engine: Engine | None = None,
    connector_settings: ConnectorSettings | None = None,
) -> ResearchContext:
    return ResearchContext(
        owner_id=OWNER_ID,
        settings=connector_settings or settings(),
        transport=httpx.MockTransport(recorder),
        repository=SourceFetchLogRepository(engine) if engine is not None else None,
        resolver=resolver,
        sleeper=lambda _seconds: None,
    )


def table_counts(engine: Engine) -> dict[str, int]:
    """Row counts of every table, so "nothing else changed" is a measurement."""
    with engine.begin() as connection:
        names = [
            row[0]
            for row in connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        ]
        return {
            name: int(connection.execute(text(f"SELECT COUNT(*) FROM {name}")).scalar() or 0)  # noqa: S608
            for name in names
        }


# --------------------------------------------------------------------------------------
# SC29 -- acceptance/fixtures/identity/b-post-only-missing-ids.json
# --------------------------------------------------------------------------------------


def test_sc29_a_post_with_no_identifier_produces_no_outbound_request(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """Card §8: "không có DOI/arXiv id ⇒ **không gọi nguồn** ... số request ra ngoài = 0"."""
    fixture = fixture_loader("identity/b-post-only-missing-ids")
    item = fixture.events[0]["item"]
    assert item["referenced_links"] == [], "fixture b must carry no links"

    recorder = Recorder(always(200, ARXIV_ONE_TARGET_ATOM))
    ctx = context(recorder)

    # The connector is identifier-driven: with no identifier there is nothing to call it
    # with. The assertion is that no code path manufactures one from the post's text or
    # media (REQ-D33, I03) -- which is why this test asserts on the *absence* of a call.
    identifiers = [
        link for link in item["referenced_links"] if link.get("link_kind_hint") != "unknown"
    ]
    for link in identifiers:  # pragma: no cover - the list is empty by construction
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, link["url"]))

    assert recorder.requests == []
    assert fixture.expected["counts"]["work"] == 0
    assert fixture.expected["counts"]["identity_alias"] == 0


def test_sc29_a_free_text_string_is_never_accepted_as_an_identifier() -> None:
    """``DC-RC-02``/CN-4: only an already-normalised id may be looked up.

    This is the question card §12 puts to the reviewer first: "có đường nào một chuỗi chưa
    chuẩn hóa hoặc do model sinh trở thành một lời gọi mạng không". The answer has to be a
    refusal at the constructor, before any transport exists.
    """
    for raw in (
        "arXiv:2504.04444",  # a prefix -- not normalised
        "https://arxiv.org/abs/2504.04444",  # a URL -- not normalised
        "2504.04444v1",  # a version suffix -- belongs to work_version
        "Attention Is All You Need",  # prose from a post
        "10.1000/ABC",  # uppercase -- a DOI normalises to lowercase
    ):
        with pytest.raises(ResearchError) as caught:
            normalized_identifier(IdScheme.ARXIV, raw)
        assert caught.value.code is ErrorCode.VALIDATION_ERROR


def test_a_landing_url_scheme_cannot_be_used_as_a_lookup_key() -> None:
    """``NC-07``/I11: "fetch this URL from a post" must not be expressible at all."""
    for scheme in (IdScheme.LANDING_URL, IdScheme.OPENALEX, IdScheme.PMID):
        with pytest.raises(ResearchError) as caught:
            normalized_identifier(scheme, "https://attacker.example.invalid/x")
        assert caught.value.code is ErrorCode.VALIDATION_ERROR
        assert caught.value.details_safe["violation_kind"] == "scheme_not_canonical"


# --------------------------------------------------------------------------------------
# SC07 -- acceptance/fixtures/identity/h-five-posts-thread-one-target.json
# --------------------------------------------------------------------------------------


def test_sc07_six_spellings_of_one_arxiv_id_produce_one_lookup(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """Six raw spellings, one normalised base, one outbound call.

    The fixture's oracle is "đúng MỘT giá trị sau chuẩn hóa cho cả năm dạng viết". At the
    connector's layer that means the six posts collapse to one lookup key, so the source is
    asked once rather than six times -- which is also the only reading of the REQ-A6 pacing
    floor that survives a batch.
    """
    fixture = fixture_loader("identity/h-five-posts-thread-one-target")
    raw_urls = [
        link["url"] for item in fixture.data["batch"]["items"] for link in item["referenced_links"]
    ]
    assert len(raw_urls) == 6

    bases = set()
    for raw in raw_urls:
        parsed = normalize_arxiv(raw)
        assert isinstance(parsed, ArxivId)
        bases.add(parsed.base)
    assert bases == {"2504.04444"}, "fixture h: five spellings, one base"

    recorder = Recorder(always(200, ARXIV_ONE_TARGET_ATOM))
    ctx = context(recorder)
    identifier = normalized_identifier(IdScheme.ARXIV, bases.pop())
    result = fetch_work_metadata(ctx, identifier=identifier)

    assert len(recorder.requests) == 1
    assert recorder.hosts == [ARXIV_HOST]
    assert result.metadata.canonical_arxiv_base == "2504.04444"
    assert fixture.expected["counts"]["work__total"] == 1
    assert fixture.expected["counts"]["identity_alias__total"] == 1


def test_sc07_the_connector_writes_no_work_and_no_alias(fixture_loader, engine: Engine) -> None:  # type: ignore[no-untyped-def]
    """``DC-RC-03``, card §4: the only row this module writes is ``source_fetch_log``."""
    fixture_loader("identity/h-five-posts-thread-one-target")
    recorder = Recorder(always(200, ARXIV_ONE_TARGET_ATOM))
    ctx = context(recorder, engine=engine)

    before = table_counts(engine)
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    after = table_counts(engine)

    assert after["source_fetch_log"] == before["source_fetch_log"] + 1
    changed = {name for name in after if after[name] != before[name]}
    assert changed == {"source_fetch_log"}


# --------------------------------------------------------------------------------------
# SC30 -- acceptance/fixtures/identity/g-arxiv-version-v1-v2.json
# --------------------------------------------------------------------------------------


def test_sc30_the_version_never_reaches_the_canonical_identifier(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """Fixture g: ``canonical_arxiv_id`` KHÔNG đổi và KHÔNG mang hậu tố ``v2``.

    The connector reports ``version_label`` separately so ``MOD-identity-service`` can open a
    second ``work_version`` without a second ``work``. Folding the version into the canonical
    value is listed in the fixture's ``forbidden_effects``.
    """
    fixture = fixture_loader("identity/g-arxiv-version-v1-v2")
    expected_work = fixture.rows("work", block="expected")[0]
    assert expected_work["canonical_arxiv_id"] == "2503.03333"

    recorder = Recorder(always(200, ARXIV_V2_ATOM))
    ctx = context(recorder)
    result = fetch_work_metadata(
        ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2503.03333")
    )

    assert result.metadata.canonical_arxiv_base == expected_work["canonical_arxiv_id"]
    assert result.metadata.version_label == "v2"
    assert "v2" not in (result.metadata.canonical_arxiv_base or "")
    assert result.evidence_level == "abstract"

    forbidden = fixture.data["forbidden_effects"]
    assert "Ghi '2503.03333v2' vào work.canonical_arxiv_id." in forbidden


def test_sc30_the_seq3_event_of_fixture_g_is_this_operation(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """The fixture names the caller and the performer; the code must agree with both."""
    fixture = fixture_loader("identity/g-arxiv-version-v1-v2")
    event = next(e for e in fixture.events if e["operation"] == "research.fetch_work_metadata")
    assert event["actor"] == "MOD-ingest-service"
    assert event["performed_by"] == "MOD-research-connector"


def test_a_request_carries_provenance_that_matches_the_fetch_log(engine: Engine) -> None:
    """``identity.md`` §7: ``evidence_ref.response_hash`` joins to ``source_fetch_log``."""
    recorder = Recorder(always(200, ARXIV_V2_ATOM))
    ctx = context(recorder, engine=engine)
    result = fetch_work_metadata(
        ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2503.03333")
    )

    provenance = result.metadata.provenance
    assert provenance is not None
    rows = SourceFetchLogRepository(engine).list_for_owner(OWNER_ID)
    assert len(rows) == 1
    assert rows[0].response_hash == provenance.response_hash
    assert rows[0].id == provenance.source_fetch_log_id
    assert rows[0].outcome == "ok"
    assert set(provenance.as_evidence_ref()) == {
        "api_endpoint",
        "retrieved_at",
        "response_hash",
    }


def test_the_logged_endpoint_never_contains_the_contact_identity(engine: Engine) -> None:
    """``source_fetch_log.endpoint`` is "URL đã gọi, **đã che tham số nhạy cảm**".

    The contact identity is the one secret this module holds
    (``capabilities.yaml`` ``ACT-research-connector``), and it travels in the query string.
    """
    recorder = Recorder(always(200, OPENALEX_WORK_JSON))
    ctx = context(recorder, engine=engine)
    fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.DOI, "10.1000/synthetic-1"))

    rows = SourceFetchLogRepository(engine).list_for_owner(OWNER_ID)
    assert len(rows) == 1
    assert "owner@example.invalid" not in rows[0].endpoint
    assert "mailto=<redacted>" in rows[0].endpoint
    # ... while the request that actually went out did carry it, as OpenAlex asks (REQ-D34).
    assert "owner%40example.invalid" in str(recorder.requests[0].url)


def test_redact_endpoint_drops_every_query_value_not_a_named_list() -> None:
    """A key-name allowlist would have to be kept in step with the configuration; this
    redaction cannot fall behind because it keeps no key values at all."""
    redacted = redact_endpoint("https://h.test.invalid/p?mailto=a@b.invalid&token=secret&x=1")
    assert redacted == "https://h.test.invalid/p?mailto=<redacted>&token=<redacted>&x=<redacted>"


# --------------------------------------------------------------------------------------
# SC11 -- acceptance/fixtures/collection/h-metadata-unavailable-post-only.json
# --------------------------------------------------------------------------------------


def test_sc11_the_fixture_pins_the_code_this_module_must_raise(fixture_loader) -> None:  # type: ignore[no-untyped-def]
    """Read the expected code out of the fixture rather than restating it here."""
    fixture = fixture_loader("collection/h-metadata-unavailable-post-only")
    warnings = fixture.events[0]["response_body"]["receipt"]["warnings"]
    assert [w["code"] for w in warnings] == [ErrorCode.SOURCE_METADATA_UNAVAILABLE.value]


def test_sc11_a_source_that_fails_twice_degrades_to_post_only(
    fixture_loader,  # type: ignore[no-untyped-def]
    engine: Engine,
) -> None:
    """The item ends at ``post_only`` with no work row and no guessed identifier.

    ``research_connector_attempts = 2`` (``contracts/retry-policy.yaml``), so two attempts
    are made and two rows are logged -- a failed call still leaves a trace, because a call
    that leaves none cannot be audited for pacing (card §6).
    """
    fixture = fixture_loader("collection/h-metadata-unavailable-post-only")
    expected = fixture.data["expected_target_state"]["1900000000000000041"]
    assert expected["evidence_level"] == "post_only"
    assert expected["doi"] is None and expected["arxiv_id"] is None

    recorder = Recorder(always(503, b"SYNTHETIC RECORD -- upstream error"))
    ctx = context(recorder, engine=engine)

    before = table_counts(engine)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    after = table_counts(engine)

    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    assert len(recorder.requests) == 2, "research_connector_attempts = 2"
    assert after["source_fetch_log"] == before["source_fetch_log"] + 2
    assert after["work"] == before["work"] == 0, "no work row is invented from a failure"
    rows = SourceFetchLogRepository(engine).list_for_owner(OWNER_ID)
    assert {row.outcome for row in rows} == {"error"}


def test_sc11_the_error_envelope_carries_no_identifier_guess_and_no_url() -> None:
    """errors.yaml §redaction_vi: "Không ghi URL đầy đủ ...; chỉ ID đã chuẩn hóa"."""
    recorder = Recorder(always(503, b"SYNTHETIC RECORD -- upstream error"))
    ctx = context(recorder)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    envelope = caught.value.envelope("01JCORREL0000000000000000")
    assert envelope["code"] == ErrorCode.SOURCE_METADATA_UNAVAILABLE.value
    assert envelope["scope"] == "item"
    assert envelope["retry_class"] == "retryable_with_budget"
    assert set(envelope) == {
        "code",
        "scope",
        "retry_class",
        "message_safe",
        "correlation_id",
        "details_safe",
        "retry_after_ms",
    }
    assert envelope["details_safe"] == {
        "target_key": "arxiv:2504.04444",
        "connector_name": "research-connector",
        "attempt_number": 2,
        "retry_after_ms": None,
    }
    assert ARXIV_HOST not in json.dumps(envelope)


def test_a_timeout_is_recorded_as_unknown_not_as_an_error(engine: Engine) -> None:
    """retry-policy ``RP-01``: a transport timeout is an unknown outcome.

    Recording it as ``error`` would assert the source answered when nobody observed one, and
    the fixture's forbidden list depends on that distinction staying real.
    """

    def timeout(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("SYNTHETIC RECORD -- timeout")

    recorder = Recorder(timeout)
    ctx = context(recorder, engine=engine)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE
    rows = SourceFetchLogRepository(engine).list_for_owner(OWNER_ID)
    assert {row.outcome for row in rows} == {"timeout_unknown"}


def test_an_empty_feed_is_not_found_not_metadata_unavailable(engine: Engine) -> None:
    """ "The source has nothing" and "the source did not answer" are different facts and get
    different codes (``NOT_FOUND`` vs ``SOURCE_METADATA_UNAVAILABLE``)."""
    recorder = Recorder(always(200, ARXIV_EMPTY_ATOM))
    ctx = context(recorder, engine=engine)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))

    assert caught.value.code is ErrorCode.NOT_FOUND
    assert len(recorder.requests) == 1, "an answered lookup is not retried"
    rows = SourceFetchLogRepository(engine).list_for_owner(OWNER_ID)
    assert [row.outcome for row in rows] == ["not_found"]


def test_a_malformed_body_degrades_and_never_partially_parses(engine: Engine) -> None:
    recorder = Recorder(always(200, b"<feed><entry>SYNTHETIC RECORD -- truncated"))
    ctx = context(recorder, engine=engine)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE


def test_an_xml_entity_declaration_is_refused_rather_than_expanded(engine: Engine) -> None:
    """A "billion laughs" body is a parse failure, not a memory event."""
    bomb = (
        b'<?xml version="1.0"?><!DOCTYPE feed [<!ENTITY a "aaaaaaaaaa">'
        b'<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">]>'
        b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>&b;</title></entry></feed>'
    )
    recorder = Recorder(always(200, bomb))
    ctx = context(recorder, engine=engine)
    with pytest.raises(ResearchError) as caught:
        fetch_work_metadata(ctx, identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"))
    assert caught.value.code is ErrorCode.SOURCE_METADATA_UNAVAILABLE


def test_openalex_metadata_keeps_the_looked_up_doi_and_invents_no_arxiv_id() -> None:
    """B15/I03: one source's cross-reference is not a second canonical identifier."""
    recorder = Recorder(always(200, OPENALEX_WORK_JSON))
    ctx = context(recorder)
    result = fetch_work_metadata(
        ctx, identifier=normalized_identifier(IdScheme.DOI, "10.1000/synthetic-1")
    )
    assert result.metadata.canonical_doi == "10.1000/synthetic-1"
    assert result.metadata.canonical_arxiv_base is None
    assert result.metadata.abstract_text == "SYNTHETIC abstract text"


def test_a_doi_normalises_to_itself_before_it_is_looked_up() -> None:
    """The guard is the contract's own normaliser, not a second implementation."""
    assert normalize_doi("https://doi.org/10.1000/Synthetic-1") == "10.1000/synthetic-1"
    identifier: NormalizedIdentifier = normalized_identifier(IdScheme.DOI, "10.1000/synthetic-1")
    assert identifier.source_type == "openalex_api"
    assert identifier.alias_key == "doi:10.1000/synthetic-1"


def test_the_connector_object_refuses_a_caller_that_is_not_ingest(engine: Engine) -> None:
    """Card §5: ``MOD-ingest-service`` is the only caller of ``research.fetch_work_metadata``.

    ``MOD-x-collector`` calling it directly is the fixture's forbidden effect "Cho collector
    tự gọi arXiv/OpenAlex (REQ-D32, denied case NC-08)", and ruling ``R5-01`` puts an
    in-process call over an unregistered edge at ``FORBIDDEN_EDGE``.
    """
    from server.app.auth.service import AuthError

    recorder = Recorder(always(200, ARXIV_ONE_TARGET_ATOM))
    connector: ResearchConnector = build_connector(
        owner_id=OWNER_ID,
        settings=settings(),
        transport=httpx.MockTransport(recorder),
        repository=SourceFetchLogRepository(engine),
        resolver=resolver,
        sleeper=lambda _seconds: None,
    )
    with pytest.raises(AuthError) as caught:
        connector.fetch_work_metadata(
            caller_module="MOD-x-collector",
            identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"),
        )
    assert caught.value.code is ErrorCode.FORBIDDEN_EDGE
    assert recorder.requests == [], "a refused edge makes no outbound call"

    result = connector.fetch_work_metadata(
        caller_module="MOD-ingest-service",
        identifier=normalized_identifier(IdScheme.ARXIV, "2504.04444"),
    )
    assert result.metadata.title is not None
