"""Identifier normalisation -- pure, deterministic, no network (contracts/data/identity.md §2).

Every function here is a total function from a raw observed string to either a normalised
value or :data:`REJECT`. Same input, same output, for ever: ``identity_alias`` is only a
lookup *function* (I03a) if the key it is indexed by is computed deterministically. The raw
value is never discarded -- it is stored in ``identity_alias.id_value_raw`` so §8 can recompute
every key if these rules ever change.

``REJECT`` is not an error. It means "this string is not an identifier of this scheme", and the
caller drops it (identity.md §3 step 1) and lets the post continue down the post-only branch.
Nothing here ever repairs a malformed identifier into a valid-looking one.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Final
from urllib.parse import parse_qsl, urlsplit, urlunsplit


class IdScheme(str, Enum):
    """The five schemes ``identity_alias.id_scheme`` closes over (entities.yaml)."""

    DOI = "doi"
    ARXIV = "arxiv"
    OPENALEX = "openalex"
    PMID = "pmid"
    LANDING_URL = "landing_url"


#: Only these two may be written to ``work.canonical_doi`` / ``work.canonical_arxiv_id`` and
#: are therefore enforced by a UNIQUE index; the rest exist only to bridge (identity.md §2.3).
CANONICAL_SCHEMES: Final[frozenset[IdScheme]] = frozenset({IdScheme.DOI, IdScheme.ARXIV})


class _Reject:
    """Sentinel type for "not an identifier of this scheme"."""

    _instance: _Reject | None = None

    def __new__(cls) -> _Reject:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "REJECT"

    def __bool__(self) -> bool:
        return False


#: Returned instead of a value. Falsy, so ``if normalize_doi(x):`` reads correctly.
REJECT: Final[_Reject] = _Reject()


@dataclass(frozen=True)
class ArxivId:
    """An arXiv identifier split into the part that identifies the *work* and the version.

    ``work.canonical_arxiv_id`` stores :attr:`base` only. ``2501.01234v1`` and ``2501.01234v2``
    are ONE work with two ``work_version`` rows (identity.md §2.2, REQ-D26), which is exactly
    what keeping the version out of the canonical column enforces.
    """

    base: str
    version: str | None


# Trailing punctuation a post's prose leaves glued to an identifier (identity.md §2.1 step 4).
# Whitespace is included because a raw value such as ``"ARXIV:2504.04444 ."`` (fixture (h))
# carries a space between the identifier and the sentence's full stop; an identifier has no
# interior trailing whitespace, so stripping it cannot change which identifier is meant.
_TRAILING: Final[str] = ".,;:)]}>\"' \t\r\n"

# Order matters: the longest, most specific prefixes first, each removed at most once.
_DOI_PREFIXES: Final[tuple[str, ...]] = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi.org/",
    "dx.doi.org/",
    "doi:",
)
_ARXIV_PREFIXES: Final[tuple[str, ...]] = (
    "https://arxiv.org/abs/",
    "http://arxiv.org/abs/",
    "https://arxiv.org/pdf/",
    "http://arxiv.org/pdf/",
    "arxiv.org/abs/",
    "arxiv.org/pdf/",
    "arxiv:",
)

_DOI_RE: Final[re.Pattern[str]] = re.compile(r"^10\.[0-9]{4,9}/[\x21-\x7e]+$")
_ARXIV_NEW_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9]{4}\.[0-9]{4,5}$")
_ARXIV_OLD_RE: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z-]+(\.[A-Za-z]{2})?/[0-9]{7}$")
_ARXIV_VERSION_RE: Final[re.Pattern[str]] = re.compile(r"^(.*?)v([1-9][0-9]{0,2})$", re.IGNORECASE)
_OPENALEX_RE: Final[re.Pattern[str]] = re.compile(r"^W[0-9]+$")
_PMID_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9]{1,9}$")
_PERCENT_RE: Final[re.Pattern[str]] = re.compile(r"%([0-9A-Fa-f]{2})")

#: Query parameters dropped from a landing URL (identity.md §2.3): campaign noise, not identity.
_TRACKING_PARAMS: Final[frozenset[str]] = frozenset({"ref", "s"})


def _prepare(raw: str) -> str:
    """Step 1 of every algorithm: trim, then NFC."""
    return unicodedata.normalize("NFC", raw.strip())


def _strip_prefixes(value: str, prefixes: tuple[str, ...]) -> str:
    """Remove each prefix at most once, case-insensitively, in the given order.

    A prefix ending in ``:`` may be followed by whitespace (``"DOI: 10.1000/x"``), which is
    removed with it.
    """
    for prefix in prefixes:
        if value.lower().startswith(prefix):
            value = value[len(prefix) :]
            if prefix.endswith(":"):
                value = value.lstrip()
    return value


def _strip_trailing(value: str) -> str:
    """Step 4/5: drop sentence punctuation from the end, repeatedly."""
    return value.rstrip(_TRAILING)


def _percent_decode_once(value: str) -> str:
    """Decode ``%XX`` exactly once.

    A single pass is the rule, not a shortcut: a valid DOI may legitimately contain a ``%``,
    so decoding until nothing changes would corrupt it (identity.md §2.1 step 3).
    """
    return _PERCENT_RE.sub(lambda match: chr(int(match.group(1), 16)), value)


def normalize_doi(raw: str) -> str | _Reject:
    """``normalize_doi(raw) -> string | REJECT`` -- identity.md §2.1.

    Lowercasing is deliberate and load-bearing: DOI syntax is case-insensitive in practice, so
    ``10.1000/XYZ`` and ``10.1000/xyz`` are ONE DOI and must produce one alias row.
    """
    value = _prepare(raw)
    value = _strip_prefixes(value, _DOI_PREFIXES)
    value = _percent_decode_once(value)
    value = _strip_trailing(value)
    value = value.lower()
    return value if _DOI_RE.match(value) else REJECT


def normalize_arxiv(raw: str) -> ArxivId | _Reject:
    """``normalize_arxiv(raw) -> {base, version} | REJECT`` -- identity.md §2.2.

    The old style is case-folded in two directions on purpose (``Math.gt/0309136`` ->
    ``math.GT/0309136``): that is the form arXiv publishes, and a deterministic single form is
    what makes ``identity_alias`` a function.
    """
    value = _prepare(raw)
    value = _strip_prefixes(value, _ARXIV_PREFIXES)
    if value.lower().endswith(".pdf"):
        value = value[: -len(".pdf")]
    value = re.split(r"[?#]", value, maxsplit=1)[0]
    value = _strip_trailing(value)

    version: str | None = None
    match = _ARXIV_VERSION_RE.match(value)
    if match:
        version = f"v{match.group(2)}"
        value = match.group(1)

    if _ARXIV_NEW_RE.match(value):
        return ArxivId(base=value, version=version)
    if _ARXIV_OLD_RE.match(value):
        archive, _, number = value.partition("/")
        head, dot, subject_class = archive.partition(".")
        base = f"{head.lower()}{dot}{subject_class.upper()}/{number}"
        return ArxivId(base=base, version=version)
    return REJECT


def normalize_openalex(raw: str) -> str | _Reject:
    """OpenAlex work id, ``^W[0-9]+$`` with a capital W (identity.md §2.3).

    Alias-only: an OpenAlex id may change, so it never defines a work on its own -- it bridges
    a DOI to an arXiv id, which is the evidence fixture (a) merges on.
    """
    value = _strip_trailing(_prepare(raw))
    value = _strip_prefixes(value, ("https://openalex.org/", "http://openalex.org/"))
    value = value.upper()
    return value if _OPENALEX_RE.match(value) else REJECT


def normalize_pmid(raw: str) -> str | _Reject:
    """PubMed id, ``^[0-9]{1,9}$`` (identity.md §2.3). Alias-only."""
    value = _strip_trailing(_prepare(raw))
    return value if _PMID_RE.match(value) else REJECT


def normalize_landing_url(raw: str) -> str | _Reject:
    """Landing page URL: the weakest evidence there is, so it is alias-only (identity.md §2.3).

    Scheme and host are lowercased, ``www.`` is dropped, the fragment goes, and the tracking
    parameters ``utm_*``, ``ref`` and ``s`` are removed. The path is kept byte-for-byte: a path
    is case-sensitive on most servers and "tidying" it would merge two different pages.
    """
    value = _strip_trailing(_prepare(raw))
    if not value:
        return REJECT
    parts = urlsplit(value)
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return REJECT
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[len("www.") :]
    kept = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_PARAMS
    ]
    query = "&".join(f"{key}={val}" if val != "" else key for key, val in kept)
    return urlunsplit((parts.scheme.lower(), host, parts.path, query, ""))


def normalize(scheme: IdScheme, raw: str) -> str | _Reject:
    """Normalise ``raw`` for ``scheme`` and return the value stored in ``id_value_normalized``.

    For ``arxiv`` this returns the BASE only; the version label is obtained from
    :func:`normalize_arxiv` and belongs to ``work_version``, never to an alias row.
    """
    if scheme is IdScheme.DOI:
        return normalize_doi(raw)
    if scheme is IdScheme.ARXIV:
        arxiv = normalize_arxiv(raw)
        return arxiv.base if isinstance(arxiv, ArxivId) else REJECT
    if scheme is IdScheme.OPENALEX:
        return normalize_openalex(raw)
    if scheme is IdScheme.PMID:
        return normalize_pmid(raw)
    return normalize_landing_url(raw)


def target_key(kind: str, identifier: str) -> str:
    """``work:<ulid>`` / ``post:<ulid>`` -- the union key of entities.yaml ``target_union``."""
    if kind not in {"work", "post"}:
        raise ValueError(f"target kind must be 'work' or 'post', not {kind!r}")
    return f"{kind}:{identifier}"
