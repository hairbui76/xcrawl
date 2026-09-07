#!/usr/bin/env python3
"""Generate ``rr_contracts.generated`` from ``contracts/``.

Why this file exists
--------------------
ADR-0011 ("Hệ quả") and ``agent-tasks/README.md`` §5.3 make one rule non-negotiable:
Pydantic models, enum constants and the TypeScript client are **generated from**
``contracts/`` and are **never hand-edited**. A hand edit makes code and contract drift
apart silently, which is exactly the failure mode ADR-0006 flagged as the largest cost of
a two-language stack.

A rule is only a rule if it is checkable. This generator is therefore paired with
``shared/rr_contracts/tests/test_generated_matches_contracts.py``, which fails when

* a source contract's sha256 no longer matches the one recorded in ``GENERATED_FROM.json``
  (the contract changed, the code did not), or
* re-running this generator produces any diff against the checked-in tree
  (the code changed, the contract did not).

Determinism
-----------
Every output is a pure function of the source bytes:

* ``datamodel-codegen`` runs with ``--disable-timestamp`` so no clock enters the output.
* The emitters below sort nothing that the contract orders, and preserve contract order
  where the contract has one (operation ids, error codes, enum values) so a reviewer can
  diff generated code against the contract line by line.
* No network access, and no tool version string is written into the output; the tool
  version is pinned in ``uv.lock`` and recorded in ``GENERATED_FROM.json``.

What is deliberately NOT a source
---------------------------------
``contracts/data/entities.yaml`` is **intentionally not** in ``ALL_SOURCES``. The generator
emits the *wire* contract — request/response payloads, error codes, operation ids, state
enums — while ``entities.yaml`` describes the *database*, and the two are not the same
shape: a column exists that never crosses the wire, and a payload field exists that is
never a column. The entity contract reaches the code by two other paths, both of which read
``entities.yaml`` directly:

* the Alembic base revision under ``server/migrations/versions/``, which writes the DDL;
* ``tests/contract/test_schema_matches_entities.py``, the permanent check that every column
  present after ``alembic upgrade head`` resolves to an ``entities.yaml`` field, with the
  NOT NULL / UNIQUE / CHECK constraints the entity declares (the check `F-A3R1-02` made
  permanent).

So an amendment to an entity — for example ``AMD-ENT-owner-01`` adding the four credential
fields to ``ENT-owner`` — correctly produces **no diff** here. Generating a Python entity
registry from ``entities.yaml`` as well is a possible future improvement, recorded as
``CR-P0-06``; it is not in this generator's scope.

Usage
-----
    uv run python shared/rr_contracts/generate.py            # write into the package
    uv run python shared/rr_contracts/generate.py --out DIR  # write elsewhere (the test)
    uv run python shared/rr_contracts/generate.py --check    # regenerate + diff, exit 1
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent / "rr_contracts"
DEFAULT_OUT = PACKAGE_DIR / "generated"

#: Contract files this generator reads. Order is stable; it is the order recorded in
#: GENERATED_FROM.json and the order the header hashes are listed in.
SCHEMA_FILES: tuple[str, ...] = (
    "contracts/schemas/analysis-result.schema.json",
    "contracts/schemas/ingest-batch.schema.json",
    "contracts/schemas/ingest-receipt.schema.json",
    "contracts/schemas/report.schema.json",
    "contracts/schemas/saved-snapshot.schema.json",
    "contracts/schemas/target.schema.json",
    "contracts/schemas/worker-assignment.schema.json",
)
STATE_FILES: tuple[str, ...] = (
    "contracts/state/analysis.yaml",
    "contracts/state/delivery.yaml",
    "contracts/state/report.yaml",
    "contracts/state/run.yaml",
    "contracts/state/storage.yaml",
)
ERRORS_FILE = "contracts/errors.yaml"
PORTS_FILE = "contracts/ports.yaml"
OPENAPI_FILE = "contracts/http/openapi.yaml"

ALL_SOURCES: tuple[str, ...] = (
    *SCHEMA_FILES,
    *STATE_FILES,
    ERRORS_FILE,
    PORTS_FILE,
    OPENAPI_FILE,
)

BANNER = "# GENERATED — do not edit; source sha256 {hashes}\n"
BANNER_BODY = (
    "# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.\n"
    "# Editing this file by hand makes code and contract drift apart silently; the rule is\n"
    "# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the\n"
    "# contract, regenerate, and mark the affected task cards STALE per INV-06.\n"
)


# ----------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def header(rel_sources: list[str], hashes: dict[str, str]) -> str:
    listed = ", ".join(f"{rel}={hashes[rel][:16]}…" for rel in rel_sources)
    lines = [BANNER.format(hashes=listed), BANNER_BODY]
    for rel in rel_sources:
        lines.append(f"#   {rel}  sha256:{hashes[rel]}\n")
    return "".join(lines) + "\n"


def enum_member(value: str) -> str:
    """Contract value -> Python enum member name.

    ``worker.claim_assignment`` -> ``WORKER_CLAIM_ASSIGNMENT``;
    ``challenge_required`` -> ``CHALLENGE_REQUIRED``. Collisions are impossible within one
    enum because the contract values are unique and this mapping is injective over the
    character set the contracts use ([a-z0-9_.]).
    """
    name = re.sub(r"[^0-9a-zA-Z]+", "_", value).strip("_").upper()
    if not name or name[0].isdigit():
        name = "V_" + name
    return name


def class_name(stem: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[-_.]+", stem) if part)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_yaml(rel: str) -> Any:
    return yaml.safe_load((REPO_ROOT / rel).read_text(encoding="utf-8"))


def py_literal(value: object) -> str:
    """A deterministic Python literal (json.dumps keeps key order and escaping stable)."""
    return json.dumps(value, ensure_ascii=False, sort_keys=False)


# ----------------------------------------------------------------------------------------
# emitters
# ----------------------------------------------------------------------------------------


def _rewrite_local_refs(node: Any, prefix: str) -> Any:
    """Rewrite ``#/$defs/X`` to ``#/$defs/<prefix>__X`` throughout ``node``."""
    if isinstance(node, dict):
        result: dict[str, Any] = {}
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str) and value.startswith("#/$defs/"):
                result[key] = f"#/$defs/{prefix}__{value[len('#/$defs/'):]}"
            else:
                result[key] = _rewrite_local_refs(value, prefix)
        return result
    if isinstance(node, list):
        return [_rewrite_local_refs(item, prefix) for item in node]
    return node


def bundle_schema(rel: str, by_id: dict[str, str]) -> dict[str, Any]:
    """Return ``rel`` with cross-schema ``$ref``s inlined into its own ``$defs``.

    ``contracts/schemas/report.schema.json`` refers to ``target.schema.json`` by its
    ``$id`` URL. That is correct JSON Schema, but ``datamodel-codegen`` turns a URL ``$ref``
    into a relative import that climbs out of the output package (``from ..target import
    schema``) and does not import. Rather than hand-fix the generated code -- which is the
    one thing this package forbids -- the reference is resolved *before* generation:

    * the referenced schema is copied into ``$defs`` under ``ext_<stem>``;
    * its own ``$defs`` are copied alongside as ``ext_<stem>__<name>``, so the two schemas'
      identically named helpers (``ulid``, ``sha256``, ``timestamp_utc_ms``, ...) cannot
      collide;
    * the URL ``$ref`` becomes ``#/$defs/ext_<stem>``.

    The transform is textual and order-independent, so the bundle is a pure function of the
    source bytes. It changes no constraint and no field name: validating a document against
    the bundle and against the original is the same validation.
    """
    doc = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
    own_id = doc.get("$id")
    pending: list[str] = []

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            result: dict[str, Any] = {}
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str) and value in by_id and value != own_id:
                    stem = Path(by_id[value]).name.replace(".schema.json", "")
                    prefix = "ext_" + stem.replace("-", "_")
                    if prefix not in pending:
                        pending.append(prefix)
                    result[key] = f"#/$defs/{prefix}"
                else:
                    result[key] = walk(value)
            return result
        if isinstance(node, list):
            return [walk(item) for item in node]
        return node

    bundled = walk(doc)
    defs = dict(bundled.get("$defs") or {})
    resolved: set[str] = set()
    while pending:
        prefix = pending.pop(0)
        if prefix in resolved:
            continue
        resolved.add(prefix)
        stem = prefix[len("ext_") :].replace("_", "-")
        ext_rel = next(r for r in by_id.values() if Path(r).name == f"{stem}.schema.json")
        ext = json.loads((REPO_ROOT / ext_rel).read_text(encoding="utf-8"))
        ext_defs = ext.pop("$defs", {})
        for name, sub in ext_defs.items():
            defs[f"{prefix}__{name}"] = _rewrite_local_refs(sub, prefix)
        for meta in ("$schema", "$id", "x-contract"):
            ext.pop(meta, None)
        defs[prefix] = _rewrite_local_refs(ext, prefix)
    bundled["$defs"] = defs
    return bundled


def emit_models(out: Path, hashes: dict[str, str]) -> list[str]:
    """Pydantic v2 models, one module per ``contracts/schemas/*.json``."""
    models_dir = out / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    module_names: list[str] = []

    by_id: dict[str, str] = {}
    for rel in SCHEMA_FILES:
        doc = json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
        if doc.get("$id"):
            by_id[doc["$id"]] = rel

    bundle_dir = Path(tempfile.mkdtemp(prefix="rr-contracts-bundle-"))
    for rel in SCHEMA_FILES:
        src = REPO_ROOT / rel
        stem = src.name.replace(".schema.json", "")
        module = stem.replace("-", "_")
        module_names.append(module)
        target = models_dir / f"{module}.py"
        bundled_path = bundle_dir / src.name
        bundled_path.write_text(
            json.dumps(bundle_schema(rel, by_id), ensure_ascii=False, indent=2, sort_keys=False)
            + "\n",
            encoding="utf-8",
        )
        cmd = [
            sys.executable,
            "-m",
            "datamodel_code_generator",
            "--input",
            str(bundled_path),
            "--input-file-type",
            "jsonschema",
            "--output",
            str(target),
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--target-python-version",
            "3.12",
            "--disable-timestamp",
            "--use-standard-collections",
            "--use-union-operator",
            "--use-schema-description",
            "--field-constraints",
            "--class-name",
            class_name(stem),
        ]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        subprocess.run(cmd, check=True, cwd=str(REPO_ROOT), env=env)
        body = target.read_text(encoding="utf-8")
        # datamodel-codegen writes its own two-line provenance comment; keep it and put the
        # contract provenance above it, so the file states both where it came from and what
        # produced it.
        write(target, header([rel], hashes) + body)
    shutil.rmtree(bundle_dir)

    init_lines = [
        header(list(SCHEMA_FILES), hashes),
        '"""Pydantic v2 models generated from contracts/schemas/*.json."""\n\n',
    ]
    for module in module_names:
        init_lines.append(f"from rr_contracts.generated.models import {module} as {module}\n")
    init_lines.append("\n__all__ = [\n")
    for module in module_names:
        init_lines.append(f'    "{module}",\n')
    init_lines.append("]\n")
    write(models_dir / "__init__.py", "".join(init_lines))
    return module_names


def emit_errors(out: Path, hashes: dict[str, str]) -> int:
    doc = load_yaml(ERRORS_FILE)
    codes = doc["codes"]
    lines = [
        header([ERRORS_FILE], hashes),
        '"""Error codes registered in contracts/errors.yaml.\n\n',
        "The registry is the single source of truth for the wire vocabulary: an error code\n",
        "that is not in this enum does not exist (contracts/errors.yaml). ``SCOPE`` and\n",
        "``RETRY_CLASS`` carry the two fields a caller must branch on and are kept beside the\n",
        "enum so a handler cannot invent a retry policy the contract did not grant.\n",
        '"""\n\n',
        "from __future__ import annotations\n\n",
        "from enum import Enum\n\n\n",
        "class ErrorCode(str, Enum):\n",
        '    """Every code in contracts/errors.yaml, in contract order."""\n\n',
    ]
    for entry in codes:
        code = entry["code"]
        title = str(entry.get("title_vi", "")).replace("\n", " ").strip()
        lines.append(f"    #: {title}\n")
        lines.append(f'    {enum_member(code)} = "{code}"\n')
    lines.append("\n\n")
    lines.append("#: Error code -> `scope` field of contracts/errors.yaml.\n")
    lines.append("SCOPE: dict[ErrorCode, str] = {\n")
    for entry in codes:
        lines.append(f"    ErrorCode.{enum_member(entry['code'])}: {py_literal(entry['scope'])},\n")
    lines.append("}\n\n")
    lines.append("#: Error code -> `retry_class` field of contracts/errors.yaml.\n")
    lines.append("RETRY_CLASS: dict[ErrorCode, str] = {\n")
    for entry in codes:
        lines.append(
            f"    ErrorCode.{enum_member(entry['code'])}: {py_literal(entry['retry_class'])},\n"
        )
    lines.append("}\n")
    write(out / "errors.py", "".join(lines))
    return len(codes)


def emit_operations(out: Path, hashes: dict[str, str]) -> int:
    doc = load_yaml(PORTS_FILE)
    operations = doc["operations"]
    lines = [
        header([PORTS_FILE], hashes),
        '"""Operation ids from contracts/ports.yaml.\n\n',
        "contracts/ports.yaml is the naming authority for operations (coordination baseline\n",
        "§3). Referring to an operation by a string literal instead of a member of this enum\n",
        "is how a near-miss name (`worker.grab_assignment`) gets into code without failing a\n",
        "build.\n\n",
        "``OWNER_MODULE``, ``TRANSPORT`` and ``MUTATION`` restate the three fields the\n",
        "default-deny boundary check needs (contracts/modules.yaml): who owns the operation,\n",
        "how it is reached, and whether it changes state.\n",
        '"""\n\n',
        "from __future__ import annotations\n\n",
        "from enum import Enum\n\n\n",
        "class OperationId(str, Enum):\n",
        '    """Every operation in contracts/ports.yaml, in contract order."""\n\n',
    ]
    for entry in operations:
        oid = entry["operation_id"]
        title = str(entry.get("title_vi", "")).replace("\n", " ").strip()
        lines.append(f"    #: {title}\n")
        lines.append(f'    {enum_member(oid)} = "{oid}"\n')
    lines.append("\n\n")
    for const, field in (
        ("OWNER_MODULE", "owner_module"),
        ("TRANSPORT", "transport"),
    ):
        lines.append(f"#: Operation id -> `{field}` of contracts/ports.yaml.\n")
        lines.append(f"{const}: dict[OperationId, str] = {{\n")
        for entry in operations:
            lines.append(
                f"    OperationId.{enum_member(entry['operation_id'])}: "
                f"{py_literal(entry.get(field))},\n"
            )
        lines.append("}\n\n")
    lines.append("#: Operation id -> `mutation` of contracts/ports.yaml.\n")
    lines.append("MUTATION: dict[OperationId, bool] = {\n")
    for entry in operations:
        lines.append(
            f"    OperationId.{enum_member(entry['operation_id'])}: "
            f"{bool(entry.get('mutation'))},\n"
        )
    lines.append("}\n")
    write(out / "operations.py", "".join(lines))
    return len(operations)


def emit_states(out: Path, hashes: dict[str, str]) -> int:
    lines = [
        header(list(STATE_FILES), hashes),
        '"""State enums from contracts/state/*.yaml.\n\n',
        "Each enum is CLOSED: E0-09 proves the contract lists every reachable state, so a\n",
        "value absent here is a value the state machine does not have. Notably\n",
        "``StorageHealth`` has no ``unknown`` member -- code that cannot determine storage\n",
        "health must say so some other way rather than widening the enum.\n",
        '"""\n\n',
        "from __future__ import annotations\n\n",
        "from enum import Enum\n",
    ]
    count = 0
    for rel in STATE_FILES:
        doc = load_yaml(rel)
        machine = Path(rel).stem
        for enum_name, spec in doc["enums"].items():
            values = spec["values"] if isinstance(spec, dict) else spec
            cls = (
                class_name(f"{enum_name}")
                if enum_name.startswith(machine)
                else class_name(f"{machine}_{enum_name}")
            )
            note = ""
            if isinstance(spec, dict) and spec.get("note_vi"):
                note = " ".join(str(spec["note_vi"]).split())
            lines.append("\n\n")
            lines.append(f"class {cls}(str, Enum):\n")
            lines.append(f'    """`{enum_name}` of {rel}.\n\n')
            if note:
                lines.append(f"    {note}\n")
            lines.append('    """\n\n')
            for value in values:
                lines.append(f'    {enum_member(value)} = "{value}"\n')
            count += 1
    lines.append("\n")
    write(out / "states.py", "".join(lines))
    return count


def emit_constants(out: Path, hashes: dict[str, str]) -> None:
    openapi = load_yaml(OPENAPI_FILE)
    errors = load_yaml(ERRORS_FILE)
    envelope_fields = errors["error_envelope"]["fields"]
    if isinstance(envelope_fields, dict):
        field_names = list(envelope_fields.keys())
    else:
        field_names = [f["name"] if isinstance(f, dict) else str(f) for f in envelope_fields]
    lines = [
        header([OPENAPI_FILE, ERRORS_FILE], hashes),
        '"""Wire constants generated from the contracts.\n\n',
        "``CONTRACT_SCHEMA_VERSION`` is ``info.version`` of contracts/http/openapi.yaml. It\n",
        "is the version a process declares it speaks (SRC-PLAN §5.1); it is not the version\n",
        "of this package.\n",
        '"""\n\n',
        "from __future__ import annotations\n\n",
        f"CONTRACT_SCHEMA_VERSION: str = {py_literal(openapi['info']['version'])}\n",
        f"OPENAPI_VERSION: str = {py_literal(openapi['openapi'])}\n\n",
        "#: Field names of the error envelope (contracts/errors.yaml `error_envelope.fields`).\n",
        f"ERROR_ENVELOPE_FIELDS: tuple[str, ...] = {tuple(field_names)!r}\n\n",
        "#: Security scheme names of contracts/http/openapi.yaml, in contract order.\n",
        "SECURITY_SCHEMES: tuple[str, ...] = "
        f"{tuple(openapi['components']['securitySchemes'].keys())!r}\n",
    ]
    write(out / "constants.py", "".join(lines))


def emit_package_init(out: Path, hashes: dict[str, str], modules: list[str]) -> None:
    lines = [
        header(list(ALL_SOURCES), hashes),
        '"""Generated contract bindings.\n\n',
        "Nothing in this package is written by hand. See shared/rr_contracts/generate.py.\n",
        '"""\n\n',
        "from rr_contracts.generated import constants as constants\n",
        "from rr_contracts.generated import errors as errors\n",
        "from rr_contracts.generated import models as models\n",
        "from rr_contracts.generated import operations as operations\n",
        "from rr_contracts.generated import states as states\n",
        "from rr_contracts.generated.errors import ErrorCode as ErrorCode\n",
        "from rr_contracts.generated.operations import OperationId as OperationId\n\n",
        '__all__ = [\n    "ErrorCode",\n    "OperationId",\n    "constants",\n    "errors",\n'
        '    "models",\n    "operations",\n    "states",\n]\n',
    ]
    write(out / "__init__.py", "".join(lines))


# ----------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------


def generate(out: Path) -> dict[str, Any]:
    hashes = {rel: sha256_of(REPO_ROOT / rel) for rel in ALL_SOURCES}
    sizes = {rel: (REPO_ROOT / rel).stat().st_size for rel in ALL_SOURCES}

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    modules = emit_models(out, hashes)
    n_errors = emit_errors(out, hashes)
    n_operations = emit_operations(out, hashes)
    n_states = emit_states(out, hashes)
    emit_constants(out, hashes)
    emit_package_init(out, hashes, modules)

    manifest = {
        "generator": "shared/rr_contracts/generate.py",
        "rule": (
            "Generated code must match the contracts it was generated from. A mismatch "
            "here means either the contract changed without regeneration, or a generated "
            "file was hand-edited. Both are defects (ADR-0011; agent-tasks/README.md §5.3)."
        ),
        "sources": [
            {"path": rel, "sha256": hashes[rel], "bytes": sizes[rel]} for rel in ALL_SOURCES
        ],
        "outputs": {
            "models": [f"models/{m}.py" for m in modules],
            "error_codes": n_errors,
            "operation_ids": n_operations,
            "state_enums": n_states,
        },
    }
    write(out / "GENERATED_FROM.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def diff_trees(a: Path, b: Path) -> list[str]:
    """Return a list of human-readable differences between two generated trees."""
    differences: list[str] = []

    def rel_files(root: Path) -> set[str]:
        return {
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }

    left, right = rel_files(a), rel_files(b)
    for missing in sorted(left - right):
        differences.append(f"only in {a}: {missing}")
    for extra in sorted(right - left):
        differences.append(f"only in {b}: {extra}")
    for name in sorted(left & right):
        if not filecmp.cmp(a / name, b / name, shallow=False):
            differences.append(f"content differs: {name}")
    return differences


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output directory")
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate into a temporary directory and diff against --out; exit 1 on any diff",
    )
    args = parser.parse_args(argv)
    out = Path(args.out)

    if not args.check:
        manifest = generate(out)
        print(
            "generated {} models, {} error codes, {} operation ids, {} state enums -> {}".format(
                len(manifest["outputs"]["models"]),
                manifest["outputs"]["error_codes"],
                manifest["outputs"]["operation_ids"],
                manifest["outputs"]["state_enums"],
                out,
            )
        )
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "generated"
        generate(fresh)
        differences = diff_trees(out, fresh)
    if differences:
        print("REGENERATION DIFF:", file=sys.stderr)
        for line in differences:
            print("  " + line, file=sys.stderr)
        return 1
    print("generated tree matches a fresh run of the generator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
