"""OpenAlex client: build the request from configuration, parse the JSON answer.

Same split as the arXiv client -- a pure URL builder and a pure parser -- with one extra
rule that is not a style choice:

**No contact identity, no call.** ``REQ-D34`` and ``REQ-A6`` record that OpenAlex asks
callers to identify themselves, and card §10 ``SG-IDENT`` says calling anonymously when a
source asks to be told who is calling is a terms violation, not a configuration shortcut.
The identity is a *scoped secret* (``contracts/capabilities.yaml`` ``ACT-research-connector``:
"Chỉ email/định danh liên hệ mà OpenAlex yêu cầu (A6); không có key AI"), so it is supplied
by configuration, attached by :meth:`SourceConfig.build_url`, and stripped from
``source_fetch_log.endpoint`` by ``redact_endpoint``. It is enforced in
:meth:`SourceConfig.missing_facts` -- an OpenAlex config without it is *unconfigured*, and
an unconfigured source is never called.

The exact parameter name is configuration too (``contact_identity_param``): the pinned
sources carry no OpenAlex documentation URL (``CR-PC05-03``), so hard-coding a parameter
name here would be a guess.
"""

from __future__ import annotations

import json
from typing import Any

from server.app.research.service import NormalizedIdentifier, SourceConfig, WorkMetadata


def build_request_url(config: SourceConfig, identifier: NormalizedIdentifier) -> str:
    """The URL for one lookup, contact identity included when configured."""
    return config.build_url(identifier.value)


def _string(value: Any) -> str | None:
    if isinstance(value, str):
        collapsed = " ".join(value.split())
        return collapsed or None
    return None


def _normalised_doi(value: Any) -> str | None:
    """OpenAlex reports a DOI as a URL. Strip the resolver prefix and lowercase.

    Anything that does not look like a DOI after that is dropped rather than repaired: a
    "nearly a DOI" string turned into a canonical identifier is exactly the guess I03 and
    ``B15`` forbid.
    """
    raw = _string(value)
    if raw is None:
        return None
    lowered = raw.lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix) :]
            break
    return lowered if lowered.startswith("10.") and "/" in lowered else None


def _abstract_from_inverted_index(index: Any) -> str | None:
    """Rebuild the abstract from OpenAlex's ``{token: [positions]}`` form.

    This is a lossless re-ordering of tokens the source itself supplied -- it invents no
    word. Whitespace between tokens is the one thing the inverted index does not record, so
    the result is single-spaced; that is a known fidelity limit, recorded in the handoff
    rather than papered over.
    """
    if not isinstance(index, dict) or not index:
        return None
    positions: dict[int, str] = {}
    for token, spots in index.items():
        if not isinstance(token, str) or not isinstance(spots, list):
            return None
        for spot in spots:
            if not isinstance(spot, int):
                return None
            positions[spot] = token
    if not positions:
        return None
    return " ".join(positions[key] for key in sorted(positions))


def parse_response(body: bytes, *, identifier: NormalizedIdentifier) -> WorkMetadata | None:
    """Parse an OpenAlex work document, or ``None`` when it describes no work.

    :raises ValueError: the body is not readable JSON, or not an object. The caller turns
        that into ``SOURCE_METADATA_UNAVAILABLE``; it is a different fact from "no such
        work", which is ``None`` and becomes ``NOT_FOUND``.
    """
    try:
        document = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("OpenAlex response is not readable JSON") from exc
    if not isinstance(document, dict):
        raise ValueError("OpenAlex response is not a JSON object")

    # A "results" envelope with an empty list is the source saying it has nothing.
    if "results" in document:
        results = document.get("results")
        if not isinstance(results, list):
            raise ValueError("OpenAlex `results` is not a list")
        if not results:
            return None
        first = results[0]
        if not isinstance(first, dict):
            raise ValueError("OpenAlex `results[0]` is not an object")
        document = first

    title = _string(document.get("title")) or _string(document.get("display_name"))
    if title is None:
        return None

    location = document.get("primary_location")
    paper_url = _string(location.get("landing_page_url")) if isinstance(location, dict) else None

    doi = _normalised_doi(document.get("doi"))
    # The looked-up DOI is the one that has been through contracts/data/identity.md
    # normalisation, so it is authoritative for the canonical column when the source's own
    # rendering does not survive normalisation.
    canonical_doi = doi if doi is not None else identifier.value

    return WorkMetadata(
        source_type="openalex_api",
        canonical_doi=canonical_doi,
        # An arXiv id is NOT derived here even when the record hints at a preprint: the
        # connector was asked about a DOI, and minting a second canonical identifier from
        # one source's cross-reference is the guessed merge B15 forbids. The alias belongs
        # to MOD-identity-service, on evidence it evaluates itself.
        canonical_arxiv_base=None,
        version_label=None,
        title=title,
        abstract_text=_abstract_from_inverted_index(document.get("abstract_inverted_index")),
        paper_url=paper_url,
        code_url=None,
        announced_at=_string(document.get("publication_date")),
    )
