"""arXiv client: build the request from configuration, parse the Atom answer.

Two halves, deliberately separate:

* :func:`build_request_url` -- pure. It asks :class:`~server.app.research.service.SourceConfig`
  for the endpoint template, so **no arXiv host, path or query parameter appears in this
  file**. ``contracts/ops/collector-probe.md`` §9.2 records that neither pinned source
  document contains a documentation URL for the arXiv API (``CR-PC05-03``); writing one in
  here would be a guess dressed up as an implementation.
* :func:`parse_response` -- pure. It turns bytes into a
  :class:`~server.app.research.service.WorkMetadata` and never performs I/O, so the parser
  can be tested against a recorded body with no network at all.

What the parser is allowed to conclude
--------------------------------------
Only what the document says. ``canonical_arxiv_base`` is taken from the identifier that was
*looked up*, not re-derived from the answer's prose; a DOI is reported only if the document
carries one in the DOI element; the abstract is reported only if a summary element exists.
Everything absent stays ``None`` (REQ-D33, I03: no guessed identifier, ever).

XML safety
----------
``xml.etree.ElementTree`` expands internal entities, which is the classic "billion laughs"
amplifier. :func:`parse_response` therefore refuses any body that carries a document type or
entity declaration at all, before the parser sees it: an Atom feed has no legitimate use for
one, and a check on the bytes is verifiable where reaching into expat's handlers is not (the
C accelerator does not expose them, so that guard would quietly do nothing). The 10 MiB
response cap in :class:`~server.app.research.service.GuardedSession` is the second, independent
limit; ``contracts/ops/internet-boundary.md`` §3.2 asks for byte counting on the
**decompressed** stream, which is what that cap measures.
"""

from __future__ import annotations

from typing import Final
from xml.etree import ElementTree

from server.app.research.service import NormalizedIdentifier, SourceConfig, WorkMetadata

#: Atom 1.0 plus the arXiv extension namespace. Element *names* are contract-independent
#: facts of the XML documents involved, unlike hosts and rates, which are configuration.
_ATOM: Final[str] = "{http://www.w3.org/2005/Atom}"
_ARXIV: Final[str] = "{http://arxiv.org/schemas/atom}"


def build_request_url(config: SourceConfig, identifier: NormalizedIdentifier) -> str:
    """The URL for one lookup. Delegates entirely to the configured template."""
    return config.build_url(identifier.value)


#: A document type declaration is the only way an XML document can define an entity, and an
#: Atom feed has no legitimate use for one. Refusing the declaration outright is checkable
#: from the bytes; reaching into expat's handlers to disarm expansion is not (the C
#: accelerator does not expose them, so a guard written that way would silently do nothing).
_ENTITY_MARKERS: Final[tuple[bytes, ...]] = (b"<!doctype", b"<!entity")


def _reject_entity_declarations(body: bytes) -> None:
    """Refuse a body that declares XML entities -- the "billion laughs" amplifier."""
    lowered = body.lower()
    if any(marker in lowered for marker in _ENTITY_MARKERS):
        raise ValueError("entity declarations are not accepted in a source response")


def _text(node: ElementTree.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    collapsed = " ".join(node.text.split())
    return collapsed or None


def _version_label(entry_id: str | None) -> str | None:
    """``http://arxiv.org/abs/2503.03333v2`` -> ``v2``.

    The version belongs to ``work_version.version_label`` and never to
    ``work.canonical_arxiv_id`` (``identity.md`` §2.2, fixture
    ``acceptance/fixtures/identity/g-arxiv-version-v1-v2.json``: "canonical_arxiv_id KHÔNG
    đổi và KHÔNG mang hậu tố v2").
    """
    if not entry_id:
        return None
    tail = entry_id.rstrip("/").rsplit("/", 1)[-1]
    marker = tail.rfind("v")
    if marker <= 0:
        return None
    suffix = tail[marker + 1 :]
    if not suffix.isdigit() or suffix.startswith("0") or not 1 <= len(suffix) <= 3:
        return None
    return f"v{suffix}"


def parse_response(body: bytes, *, identifier: NormalizedIdentifier) -> WorkMetadata | None:
    """Parse an arXiv Atom feed into metadata, or ``None`` when it holds no entry.

    ``None`` is "the source answered and has nothing for this id" -- the caller turns it
    into ``NOT_FOUND``. A malformed document raises :class:`ValueError`, which the caller
    turns into ``SOURCE_METADATA_UNAVAILABLE``; the two are different facts and are kept
    apart on purpose.
    """
    _reject_entity_declarations(body)
    try:
        root = ElementTree.fromstring(body.decode("utf-8"))
    except (ElementTree.ParseError, UnicodeDecodeError) as exc:
        raise ValueError("arXiv response is not a readable Atom document") from exc

    entry = root.find(f"{_ATOM}entry")
    if entry is None:
        return None

    entry_id = _text(entry.find(f"{_ATOM}id"))
    # An arXiv "no results" feed carries an entry whose id is the error document; a feed
    # with no title element is not a work either. Both are "nothing for this id".
    title = _text(entry.find(f"{_ATOM}title"))
    if title is None:
        return None

    paper_url: str | None = None
    for link in entry.findall(f"{_ATOM}link"):
        if link.get("rel") in (None, "alternate") and link.get("href"):
            paper_url = link.get("href")
            break

    return WorkMetadata(
        source_type="arxiv_api",
        # The looked-up identifier is authoritative for the canonical value: it is the one
        # string that has been through contracts/data/identity.md normalisation.
        canonical_arxiv_base=identifier.value,
        canonical_doi=_text(entry.find(f"{_ARXIV}doi")),
        version_label=_version_label(entry_id),
        title=title,
        abstract_text=_text(entry.find(f"{_ATOM}summary")),
        paper_url=paper_url,
        # arXiv's Atom feed declares no code repository field. Reporting one would mean
        # inferring it from prose, which REQ-D33 forbids for identifiers and the `work`
        # entity forbids for `code_url` ("Nếu nguồn khai báo; không suy diễn").
        code_url=None,
        announced_at=_text(entry.find(f"{_ATOM}published")),
    )
