"""The generate-don't-hand-edit rule, made checkable.

ADR-0011 and ``agent-tasks/README.md`` §5.3 forbid hand-editing anything under
``rr_contracts/generated/``. A prohibition nobody can verify is a comment, not a rule, so
this module turns it into two failing tests:

``test_source_hashes_still_match``
    catches *contract moved, code did not*. Every source listed in ``GENERATED_FROM.json``
    is re-hashed against the file on disk.

``test_regeneration_produces_no_diff``
    catches *code moved, contract did not* -- i.e. a hand edit. The generator is re-run
    into a temporary directory and the trees are compared byte for byte.

Between them the only way to change a generated file is to change a contract and
regenerate, which is exactly the workflow INV-06 assumes when it marks task cards STALE.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATED_DIR = REPO_ROOT / "shared" / "rr_contracts" / "rr_contracts" / "generated"
MANIFEST = GENERATED_DIR / "GENERATED_FROM.json"
GENERATOR = REPO_ROOT / "shared" / "rr_contracts" / "generate.py"


def _load_generator():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("rr_contracts_generate", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_exists_and_lists_every_source(manifest: dict) -> None:
    generate = _load_generator()
    listed = [entry["path"] for entry in manifest["sources"]]
    assert listed == list(generate.ALL_SOURCES), (
        "GENERATED_FROM.json does not list the generator's own source set; one of the two "
        "was changed without the other"
    )


def test_source_hashes_still_match(manifest: dict) -> None:
    """Every contract this package was generated from is byte-identical to the record."""
    drifted = []
    for entry in manifest["sources"]:
        path = REPO_ROOT / entry["path"]
        assert path.exists(), f"source contract disappeared: {entry['path']}"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            drifted.append(
                f"{entry['path']}: recorded {entry['sha256'][:16]}…, on disk {actual[:16]}…"
            )
    assert not drifted, (
        "contracts changed without regenerating rr_contracts. Run "
        "`uv run python shared/rr_contracts/generate.py` and review the diff:\n  "
        + "\n  ".join(drifted)
    )


def test_every_generated_file_carries_the_banner() -> None:
    missing = [
        str(path.relative_to(GENERATED_DIR))
        for path in sorted(GENERATED_DIR.rglob("*.py"))
        if not path.read_text(encoding="utf-8").startswith("# GENERATED — do not edit;")
    ]
    assert not missing, f"generated files without the do-not-edit banner: {missing}"


def test_regeneration_produces_no_diff() -> None:
    """Re-run the generator and require a byte-identical tree.

    This is the test that actually catches a hand edit. It is also the slowest test in the
    Python suite because it shells out to ``datamodel-codegen`` seven times; that cost buys
    the only guarantee that generated code and contracts have not silently diverged.
    """
    generate = _load_generator()
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "generated"
        generate.generate(fresh)
        differences = generate.diff_trees(GENERATED_DIR, fresh)
    assert not differences, (
        "regenerating produced a different tree — a generated file was hand-edited, or the "
        "generator is not deterministic:\n  " + "\n  ".join(differences)
    )
