"""E1 contract tests for identifier normalisation (``contracts/data/identity.md`` §2).

The oracle is the contract's own algorithm plus the ``normalization_cases`` block of
``acceptance/fixtures/identity/h-five-posts-thread-one-target.json`` and the ``id_value_raw`` /
``id_value_normalized`` pairs the identity fixtures already assert. Nothing here invents a
second test data set: a case that is not in a contract or a fixture is not tested here.

Why this file matters more than it looks: ``identity_alias`` is only a lookup FUNCTION -- and
therefore I03 only holds -- if normalisation is deterministic. Every case below is really the
same claim: two spellings of one identifier must collapse to one key, and two different
identifiers must not.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from server.app.identity.normalization import (
    CANONICAL_SCHEMES,
    REJECT,
    ArxivId,
    IdScheme,
    normalize,
    normalize_arxiv,
    normalize_doi,
    normalize_landing_url,
    normalize_openalex,
    normalize_pmid,
    target_key,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "identity"


def _fixture(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    return data


# --- DOI, identity.md §2.1 --------------------------------------------------------------------

# (raw, expected). `None` means REJECT. Every row cites the step it exercises.
DOI_CASES: list[tuple[str, str | None]] = [
    ("10.1000/xyz123", "10.1000/xyz123"),  # bare
    ("doi:10.1000/xyz123", "10.1000/xyz123"),  # step 2 prefix
    ("DOI: 10.1000/XYZ123", "10.1000/xyz123"),  # step 2 case + space, step 5 lowercase
    ("https://doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("http://doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("https://dx.doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("http://dx.doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("dx.doi.org/10.1000/xyz123", "10.1000/xyz123"),
    ("  10.1000/xyz123  ", "10.1000/xyz123"),  # step 1 trim
    ("https://doi.org/10.1000/xyz.", "10.1000/xyz"),  # step 4 sentence full stop
    ("10.1000/xyz),", "10.1000/xyz"),  # step 4 repeats
    ("10.1000/a%2Fb", "10.1000/a/b"),  # step 3 percent-decode once
    ("10.1000/a%252Fb", "10.1000/a%2fb"),  # step 3: decoded ONCE, not twice
    ("10.1000/XYZ", "10.1000/xyz"),  # step 5
    ("not-a-doi", None),  # step 6
    ("10.1/short", None),  # registrant code too short
    ("10.1000/", None),  # empty suffix
    ("", None),
]


@pytest.mark.parametrize(("raw", "expected"), DOI_CASES)
def test_normalize_doi(raw: str, expected: str | None) -> None:
    result = normalize_doi(raw)
    if expected is None:
        assert result is REJECT, f"{raw!r} must be REJECTed, not repaired"
    else:
        assert result == expected


def test_doi_case_variants_collapse_to_one_key() -> None:
    """``10.1000/XYZ`` and ``https://doi.org/10.1000/xyz`` are ONE DOI, so ONE alias row."""
    assert normalize_doi("10.1000/XYZ") == normalize_doi("https://doi.org/10.1000/xyz")


def test_reject_never_produces_a_repaired_value() -> None:
    """A rejected DOI yields nothing at all -- ``REJECT`` is falsy and is not a string."""
    result = normalize_doi("10.abc/xyz")
    assert result is REJECT
    assert not result
    assert not isinstance(result, str)


# --- arXiv, identity.md §2.2 ------------------------------------------------------------------

ARXIV_CASES: list[tuple[str, str | None, str | None]] = [
    ("2501.01234", "2501.01234", None),
    ("arXiv:2501.01234v1", "2501.01234", "v1"),
    ("ARXIV:2504.04444 .", "2504.04444", None),  # case-insensitive prefix + trailing punctuation
    ("https://arxiv.org/abs/2504.04444", "2504.04444", None),
    ("http://arxiv.org/abs/2504.04444", "2504.04444", None),
    ("https://arxiv.org/pdf/2504.04444.pdf", "2504.04444", None),  # step 3
    ("https://arxiv.org/pdf/2504.04444v2.pdf", "2504.04444", "v2"),
    ("https://arxiv.org/abs/2504.04444?utm_source=newsletter", "2504.04444", None),  # step 4
    ("https://arxiv.org/abs/2504.04444#section", "2504.04444", None),  # step 4
    ("0704.0001", "0704.0001", None),  # first new-style id
    ("math.GT/0309136", "math.GT/0309136", None),  # old style
    ("Math.gt/0309136", "math.GT/0309136", None),  # old style, case normalised both ways
    ("hep-th/9901001v2", "hep-th/9901001", "v2"),
    ("2501.0123", "2501.0123", None),  # four digits after the dot is also valid
    ("2501.012345", None, None),  # six digits is not an arXiv id
    ("2501.012", None, None),  # too few digits
    ("arXiv:", None, None),
    ("some paper", None, None),
]


@pytest.mark.parametrize(("raw", "base", "version"), ARXIV_CASES)
def test_normalize_arxiv(raw: str, base: str | None, version: str | None) -> None:
    result = normalize_arxiv(raw)
    if base is None:
        assert result is REJECT, f"{raw!r} must be REJECTed"
        return
    assert isinstance(result, ArxivId)
    assert result.base == base
    assert result.version == version


def test_arxiv_version_is_never_part_of_the_canonical_id() -> None:
    """v1 and v2 share one base -> ONE work, two ``work_version`` rows (identity.md §2.2)."""
    first = normalize_arxiv("arXiv:2501.01234v1")
    second = normalize_arxiv("https://arxiv.org/abs/2501.01234v2")
    assert isinstance(first, ArxivId) and isinstance(second, ArxivId)
    assert first.base == second.base == "2501.01234"
    assert (first.version, second.version) == ("v1", "v2")
    assert normalize(IdScheme.ARXIV, "arXiv:2501.01234v2") == "2501.01234"


# --- the fixtures' own normalisation table ----------------------------------------------------


def test_fixture_h_normalization_cases() -> None:
    """Fixture (h) states five raw spellings and their one normalised base. It is the oracle."""
    cases = _fixture("h-five-posts-thread-one-target")["normalization_cases"]
    assert len(cases) == 5
    for case in cases:
        result = normalize_arxiv(case["raw"])
        assert isinstance(result, ArxivId), case["raw"]
        assert result.base == case["normalized_base"], case
        assert result.version == case["version"], case
    assert len({case["normalized_base"] for case in cases}) == 1, "five spellings, one key"


@pytest.mark.parametrize("fixture_name", ["a-merge-doi-arxiv", "g-arxiv-version-v1-v2"])
def test_fixture_alias_rows_normalize_as_declared(fixture_name: str) -> None:
    """Every ``identity_alias`` row that carries both raw and normalised values must agree."""
    fixture = _fixture(fixture_name)
    rows = fixture["given"]["rows"]["identity_alias"]
    checked = 0
    for row in rows:
        if "id_value_raw" not in row:
            continue
        scheme = IdScheme(row["id_scheme"])
        assert normalize(scheme, row["id_value_raw"]) == row["id_value_normalized"], row
        checked += 1
    assert checked > 0, "fixture carries no raw/normalised pair to check"


# --- the alias-only schemes, identity.md §2.3 -------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("W2741809807", "W2741809807"),
        ("w2741809807", "W2741809807"),
        ("https://openalex.org/W2741809807", "W2741809807"),
        ("W123.", "W123"),
        ("2741809807", None),
        ("X123", None),
    ],
)
def test_normalize_openalex(raw: str, expected: str | None) -> None:
    result = normalize_openalex(raw)
    assert result == expected if expected is not None else result is REJECT


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("12345678", "12345678"), ("1", "1"), ("1234567890", None), ("12a", None)],
)
def test_normalize_pmid(raw: str, expected: str | None) -> None:
    result = normalize_pmid(raw)
    assert result == expected if expected is not None else result is REJECT


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("HTTPS://WWW.Example.com/Path", "https://example.com/Path"),
        ("https://example.com/Path#frag", "https://example.com/Path"),
        ("https://example.com/p?utm_source=x&utm_medium=y", "https://example.com/p"),
        ("https://example.com/p?ref=abc&keep=1", "https://example.com/p?keep=1"),
        ("https://example.com/p?s=1", "https://example.com/p"),
        ("ftp://example.com/p", None),
        ("not a url", None),
    ],
)
def test_normalize_landing_url(raw: str, expected: str | None) -> None:
    result = normalize_landing_url(raw)
    assert result == expected if expected is not None else result is REJECT


def test_landing_url_keeps_path_case() -> None:
    """Paths are case-sensitive on most servers; folding them would merge two pages into one."""
    assert normalize_landing_url("https://example.com/A") != normalize_landing_url(
        "https://example.com/a"
    )


# --- properties that hold for every scheme ----------------------------------------------------

_ALL_RAW: list[tuple[IdScheme, str]] = [
    (IdScheme.DOI, "https://doi.org/10.1000/XYZ."),
    (IdScheme.ARXIV, "https://arxiv.org/pdf/2504.04444v2.pdf"),
    (IdScheme.OPENALEX, "https://openalex.org/w2741809807"),
    (IdScheme.PMID, "12345678"),
    (IdScheme.LANDING_URL, "HTTPS://WWW.Example.com/p?utm_source=x"),
]


@pytest.mark.parametrize(("scheme", "raw"), _ALL_RAW)
def test_normalization_is_idempotent(scheme: IdScheme, raw: str) -> None:
    """``normalize(normalize(x)) == normalize(x)``.

    Without this, re-running the §8 migration that recomputes ``id_value_normalized`` from
    ``id_value_raw`` could change keys on every pass.
    """
    once = normalize(scheme, raw)
    assert isinstance(once, str)
    assert normalize(scheme, once) == once


@pytest.mark.parametrize(("scheme", "raw"), _ALL_RAW)
def test_normalization_is_deterministic(scheme: IdScheme, raw: str) -> None:
    assert normalize(scheme, raw) == normalize(scheme, raw)


def test_only_doi_and_arxiv_are_canonical() -> None:
    """entities.yaml: only these two may be written to a ``work.canonical_*`` column."""
    assert {IdScheme.DOI, IdScheme.ARXIV} == CANONICAL_SCHEMES
    assert IdScheme.OPENALEX not in CANONICAL_SCHEMES


@pytest.mark.parametrize(
    ("kind", "identifier", "expected"),
    [
        ("work", "01JW0RKA100000000000000000", "work:01JW0RKA100000000000000000"),
        ("post", "01JP0STA100000000000000000", "post:01JP0STA100000000000000000"),
    ],
)
def test_target_key(kind: str, identifier: str, expected: str) -> None:
    assert target_key(kind, identifier) == expected


def test_target_key_rejects_a_third_kind() -> None:
    """The union has exactly two branches (target.schema.json ``oneOf``)."""
    with pytest.raises(ValueError, match="work"):
        target_key("report_item", "01JW0RKA100000000000000000")
