"""Fixture loader for the E1 contract tests.

The rule this file serves is ADR-0011's "Test" row and SRC-PLAN §15: **the fixtures under
``acceptance/fixtures/**`` are the only oracle**. Tests read those files directly. There is
no second test data set, and a test that needs different data changes the fixture through
change control, never in Python.

What a fixture looks like
-------------------------
Every fixture is one JSON object. The keys the loader exposes are the ones the fixtures
actually use::

    {
      "x-contract": { ... },          # provenance header (baseline §3)
      "scenario_ref": "SC26",         # or "scenario_refs": [...]
      "given":    { "rows": { "<entity>": [ {...}, ... ] }, ... },
      "events":   [ { "actor": ..., "operation": ..., ... }, ... ],
      "expected": { "rows": { "<entity>": [ {...}, ... ] }, ... }
    }

Not every fixture has all three. Two directories -- ``collection/`` and ``recovery/`` --
state their oracle in prose fields (``durable_rows_expected``, ``expected_target_state``)
instead of ``rows``; ``evidence/tools/README.md`` §5.1 records that E0 cannot measure those
and reports them as ``NOT_APPLICABLE_FREEFORM`` rather than as clean. The loader mirrors
that honesty: :func:`rows` raises when a fixture has no ``rows`` block, instead of
returning an empty list that a test would read as "nothing expected".

Usage
-----
::

    def test_disk_full_keeps_row_counts(fixture_loader):
        fx = fixture_loader("recovery/c-disk-full-mid-ingest")
        for event in fx.events:
            ...

Available fixtures: ``acceptance/fixtures/<dir>/<name>.json`` across the nine directories
``ai``, ``boundary``, ``collection``, ``e2e``, ``identity``, ``recovery``, ``reporting``,
``telegram``, ``ui``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "acceptance" / "fixtures"

#: The nine fixture directories in scope for every fixture gate (evidence/tools/README.md §4).
FIXTURE_DIRS: tuple[str, ...] = (
    "ai",
    "boundary",
    "collection",
    "e2e",
    "identity",
    "recovery",
    "reporting",
    "telegram",
    "ui",
)


class FixtureNotFound(LookupError):
    """Raised with the list of candidates, so a typo names its own fix."""


class FixtureShapeError(AssertionError):
    """Raised when a fixture is asked for a block it does not carry.

    Deliberately an error rather than an empty default: a test that silently asserts
    against nothing passes for the wrong reason.
    """


@dataclass(frozen=True)
class Fixture:
    """One loaded fixture file."""

    #: Path relative to ``acceptance/fixtures/`` without the ``.json`` suffix.
    ref: str
    path: Path
    data: dict[str, Any]

    @property
    def given(self) -> dict[str, Any]:
        return self._block("given")

    @property
    def expected(self) -> dict[str, Any]:
        return self._block("expected")

    @property
    def events(self) -> list[dict[str, Any]]:
        events = self.data.get("events")
        if events is None:
            raise FixtureShapeError(f"{self.ref} has no `events` block")
        return list(events)

    @property
    def scenario_refs(self) -> list[str]:
        if "scenario_refs" in self.data:
            return list(self.data["scenario_refs"])
        if "scenario_ref" in self.data:
            return [self.data["scenario_ref"]]
        return []

    def rows(self, entity: str, *, block: str = "given") -> list[dict[str, Any]]:
        """Return ``<block>.rows.<entity>[]``.

        :raises FixtureShapeError: if the block or its ``rows`` map is absent -- see the
            module docstring on ``NOT_APPLICABLE_FREEFORM`` directories.
        """
        section = self._block(block)
        rows = section.get("rows")
        if not isinstance(rows, dict):
            raise FixtureShapeError(
                f"{self.ref}.{block} states its oracle in prose, not in `rows`; this "
                f"fixture cannot answer a row query (evidence/tools/README.md §5.1)"
            )
        if entity not in rows:
            raise FixtureShapeError(
                f"{self.ref}.{block}.rows has no entity {entity!r}; it has " f"{sorted(rows)}"
            )
        return list(rows[entity])

    def entities(self, *, block: str = "given") -> list[str]:
        rows = self._block(block).get("rows")
        return sorted(rows) if isinstance(rows, dict) else []

    def _block(self, name: str) -> dict[str, Any]:
        block = self.data.get(name)
        if not isinstance(block, dict):
            raise FixtureShapeError(f"{self.ref} has no `{name}` block")
        return block


def _resolve(ref: str) -> Path:
    """``"identity/pos-ingest-batch-valid"`` or a bare name -> a path under the fixture root."""
    candidate = FIXTURE_ROOT / f"{ref}.json"
    if candidate.is_file():
        return candidate
    if "/" not in ref:
        matches = sorted(FIXTURE_ROOT.glob(f"*/{ref}.json"))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FixtureNotFound(
                f"{ref!r} is ambiguous; qualify it with a directory: "
                f"{[str(m.relative_to(FIXTURE_ROOT)) for m in matches]}"
            )
    raise FixtureNotFound(
        f"no fixture {ref!r} under {FIXTURE_ROOT}; directories are {list(FIXTURE_DIRS)}"
    )


def load_fixture(ref: str) -> Fixture:
    """Load one fixture by ``<dir>/<name>`` (or by bare name when unambiguous)."""
    path = _resolve(ref)
    data = json.loads(path.read_text(encoding="utf-8"))
    return Fixture(ref=str(path.relative_to(FIXTURE_ROOT))[: -len(".json")], path=path, data=data)


def load_directory(directory: str) -> list[Fixture]:
    """Load every fixture in one directory, in sorted order, excluding ``README.md``."""
    root = FIXTURE_ROOT / directory
    if not root.is_dir():
        raise FixtureNotFound(f"no fixture directory {directory!r} under {FIXTURE_ROOT}")
    return [load_fixture(f"{directory}/{p.stem}") for p in sorted(root.glob("*.json"))]


@pytest.fixture(scope="session")
def fixture_root() -> Path:
    return FIXTURE_ROOT


@pytest.fixture(scope="session")
def fixture_loader():  # type: ignore[no-untyped-def]
    """Session-scoped loader: ``fixture_loader("telegram/g-link-code-used-twice")``."""
    return load_fixture


@pytest.fixture(scope="session")
def fixture_directory_loader():  # type: ignore[no-untyped-def]
    """Session-scoped directory loader: ``fixture_directory_loader("identity")``."""
    return load_directory
