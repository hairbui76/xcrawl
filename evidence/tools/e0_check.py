#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E0 static-check tool for the Research Radar pre-code contract baseline.

contract_id: CT-evidence-e0-check
version: 0.1.0
status: draft
owner_role: verification owner (PC09)
source_refs: SRC-PLAN §11 PC09, SRC-PLAN §14.2 (E0), SRC-PLAN §17
requirement_refs: REQ-AC01..REQ-AC18 (indirectly, via acceptance/scenarios.yaml)
decision_refs: R-02 (fixture-actor-edge gate), FIX3-rulings (fixture field-level check)
invariant_refs: I01..I17 (coverage checks only; this tool proves nothing about runtime)
producers: [MOD-none]   # documentation tooling, not a product module
consumers: [MOD-none]
dependencies:
  - contracts/**            (read-only)
  - acceptance/**           (read-only)
  - precode/**              (read-only)
  - python3 stdlib + PyYAML + jsonschema
scope: >
  Static (E0) consistency checks over the frozen contract baseline. Parses every YAML/JSON
  file under contracts/, acceptance/, precode/ and evidence/; validates JSON Schema files
  against the 2020-12 metaschema; validates fixture payloads against local schemas;
  resolves every operation / error code / requirement / scenario / invariant / blocker /
  ADR / amendment identifier cited anywhere; lints the state machines; checks denied-edge
  and traceability coverage; scans for forbidden claim labels; checks coverage-window
  contiguity; enforces the fixture-actor-edge rule (ruling R-02) and the field-level
  existence rule (FIX3 rulings).
verification: this file IS the E0 verification tool. It is SELF_VALIDATION only.
claim_ceiling: DRAFT_FOR_REVIEW

WHAT THIS TOOL DOES NOT PROVE (SRC-PLAN §14.2): that any code exists, that any guard runs,
that any external service behaves as described, or that any provisional number is correct.
A PASS here is evidence of internal consistency of the checked subset and nothing more.

Usage (run from a scratch directory, never from the repo):
    PYTHONDONTWRITEBYTECODE=1 python3 <repo>/evidence/tools/e0_check.py \
        --repo <repo> --json-out <path>.json

Exit code: 0 if no check has status FAIL, 1 otherwise, 2 on tool error.
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import traceback

try:
    import yaml
except Exception as exc:  # pragma: no cover
    print("FATAL: PyYAML is required: %s" % exc, file=sys.stderr)
    sys.exit(2)

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except Exception as exc:  # pragma: no cover
    print("FATAL: jsonschema is required: %s" % exc, file=sys.stderr)
    sys.exit(2)


# --------------------------------------------------------------------------------------
# Result plumbing
# --------------------------------------------------------------------------------------

CHECKS: "list[Check]" = []


class Check:
    """One named E0 check. `status` is PASS | FAIL | BLOCKED | NOT_APPLICABLE."""

    def __init__(self, cid: str, title: str, oracle: str):
        self.id = cid
        self.title = title
        self.oracle = oracle
        self.status = "PASS"
        self.checked = 0
        self.violations: "list[dict]" = []
        self.notes: "list[str]" = []
        self.declared_deviations: "list[dict]" = []
        self.detail = None
        self.exempt_from_zero_guard = False

    def fail(self, where: str, detail: str, **extra):
        rec = {"where": where, "detail": detail}
        rec.update(extra)
        self.violations.append(rec)
        self.status = "FAIL"

    def blocked(self, reason: str):
        self.status = "BLOCKED"
        self.notes.append(reason)

    def note(self, text: str):
        self.notes.append(text)

    def deviation(self, where: str, rec: dict):
        """Record a deviation the file itself declares (x-contract.deviations).

        Ruling (FIX4 wave, item 2): a declared deviation is PASS-with-note, not FAIL.
        """
        entry = {"where": where}
        entry.update(rec)
        self.declared_deviations.append(entry)
        self.notes.append("declared deviation at %s: %s" % (where, rec.get("rule", "?")))

    def finalize(self):
        """A check that examined nothing has not passed; it has not run.

        This guard exists because E0-10a silently regressed to `items_checked: 0` while still
        reporting PASS when its loop was lost in an edit — the exact "0 checked read as clean"
        failure this tool warns about elsewhere. `exempt_from_zero_guard` is for checks whose
        subject can legitimately be empty.
        """
        if self.status == "PASS" and self.checked == 0 and not self.exempt_from_zero_guard:
            self.status = "BLOCKED"
            self.notes.append("examined 0 items: reported BLOCKED, not PASS. Either the subject "
                              "is missing or the check lost its loop.")
        return self

    def as_dict(self):
        out = {
            "check_id": self.id,
            "title": self.title,
            "oracle": self.oracle,
            "status": self.status,
            "items_checked": self.checked,
            "violation_count": len(self.violations),
            "violations": self.violations,
            "declared_deviations": self.declared_deviations,
            "notes": self.notes,
        }
        if self.detail is not None:
            out["detail"] = self.detail
        return out


def new_check(cid: str, title: str, oracle: str) -> Check:
    c = Check(cid, title, oracle)
    CHECKS.append(c)
    return c


# --------------------------------------------------------------------------------------
# Repository model
# --------------------------------------------------------------------------------------

SCAN_DIRS = ("contracts", "acceptance", "precode", "evidence")

# Files that are, by declared exception, not required to carry the baseline §3 header.
HEADER_EXEMPT = {
    "precode/requirements.csv",          # baseline.json.requirements_csv_contract_header (PC00 §6.3)
    "precode/baseline.json",             # is itself the baseline record
    "precode/source/spec-v0.2.md",       # immutable source copy
    "precode/source/pre-code-plan-v0.1.md",
    "precode/decision-register.md",
    "precode/owner-decision-request.md",
    "precode/review.md",
    "evidence/index.json",
    "evidence/manifest.schema.json",
}
HEADER_EXEMPT_PREFIX = (
    "precode/adr/",                      # Coordinator ruling R-05: ADR-specific front-matter
    "evidence/handoffs/",                # handoffs are evidence records, not contracts
    "evidence/runs/",                    # tool output
    "evidence/tools/",                   # tooling
)

BASELINE_HEADER_FIELDS = [
    "contract_id", "version", "status", "owner_role", "source_refs", "requirement_refs",
    "decision_refs", "invariant_refs", "producers", "consumers", "dependencies",
    "scope", "verification", "claim_ceiling",
]

ADR_HEADER_FIELDS = [
    "adr_id", "title", "status", "date", "decision_owner", "source_refs",
    "requirement_refs", "decision_refs", "affected_packages", "supersedes",
]

CLAIM_LABELS_ABOVE_DRAFT = [
    "CONTRACT_READY", "IMPLEMENTATION_VERIFIED", "INTEGRATION_VERIFIED",
    "LIVE_FEASIBILITY_VERIFIED", "PRODUCT_ACCEPTED",
]

OP_RE = re.compile(r"\b([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)\b")
# Backticked tokens in prose. `E0-04` only reads structured fields; these two patterns are how
# `E0-04b` reaches the free text that let F-A2R1-01 and F-A2R1-06 through.
PROSE_OP_RE = re.compile(r"`([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)`")
PROSE_CODE_RE = re.compile(r"`([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)`")
# Extensions that make a dotted token a filename rather than an operation id.
FILE_SUFFIXES = ("yaml", "yml", "md", "json", "csv", "py", "txt", "html")
# SCREAMING_SNAKE words that are project vocabulary, not error codes. Anything outside this list
# and outside errors.yaml is reported: that is how an unregistered code is caught in prose.
STATUS_VOCABULARY = {
    # requirement / decision status (baseline §3)
    "NOT_RUN", "NOT_APPLICABLE", "NOT_APPLICABLE_FREEFORM", "NOT_APPLICABLE_YET",
    "OWNER_DECISION_REQUIRED", "FIX_PROPOSED", "VERIFICATION_PENDING", "ACCEPTED_RISK",
    "PLACEHOLDER_KC", "PROVISIONAL_BOOTSTRAP", "STALE_BASELINE", "STALE_CANDIDATE",
    # claim ceilings (plan §2)
    "DRAFT_FOR_REVIEW", "CONTRACT_READY", "IMPLEMENTATION_VERIFIED", "INTEGRATION_VERIFIED",
    "LIVE_FEASIBILITY_VERIFIED", "PRODUCT_ACCEPTED", "NOT_READY_FOR_PRODUCT_CODE",
    # gate / evidence vocabulary
    "MET_PROVISIONAL", "PARTIALLY_MET", "NOT_MET", "SELF_VALIDATION", "COORDINATOR_CHECK",
    "INDEPENDENT_AUDIT", "READY_FOR_CARD", "OUT_OF_SCOPE", "DEFERRED_P1",
    # blocked/stop states (protocol §5)
    "BLOCKED_SCOPE", "BLOCKED_DEPENDENCY", "BLOCKED_AUTHORITY", "BLOCKED_LEASE",
    "BLOCKED_OWNER_DECISION", "BLOCKED_INDEPENDENCE", "STOPPED_EXPIRED", "STOPPED_REVOKED",
    "FAILED_PARTIAL", "DONE_WITH_CONCERNS", "WHOLE_NEW_FILE", "WHOLE_FILE_DELETE",
    "BYTE_RANGES", "NONEXECUTABLE_EXAMPLE", "DOCUMENTARY_DRAFT", "ENFORCED",
    "INDEPENDENT_REQUIRED", "NO_INDEPENDENT_AUDIT", "E0_CHECK_VIOLATION",
    # protocol.md message types (Coordinator ruling, FIX7 wave): these are message kinds, not
    # error codes, and they legitimately appear in contract prose.
    "OWNER_DECISION_REQUEST", "TASK_PACKET", "HANDOFF", "AUDIT_REPORT", "FROZEN_CANDIDATE",
    "WRITE_LEASE", "FINDING_DISPOSITION", "EVIDENCE_RECORD", "AUTHORITY_GRANT",
    "AUTHORITY_REVOCATION", "REVIEW_WAIVED", "NOT_APPLICABLE_FREEFORM",
    # baseline §3 requirement-status vocabulary
    "XN", "UQ", "KC",
}
# A requirement id has one of the exact registry forms (baseline §3). Range notations such as
# `REQ-D01..REQ-D59` are prose, not citations, and are excluded by the trailing `(?!\.\.)`.
REQ_RE = re.compile(
    r"\bREQ-(?:"
    r"D\d{2}|CTAG|AC\d{2}|P0-\d{2}|P1-\d{2}|OOS-\d{2}|A\d|OQ\d{2}|S\d+(?:\.\d+)*-\d{2}"
    r")\b(?!\.\.)"
)
# Any REQ-looking token, used only to spot malformed citations.
REQ_LOOSE_RE = re.compile(r"\bREQ-[A-Za-z0-9._-]*[A-Za-z0-9]\b")
SC_RE = re.compile(r"\bSC[0-9]{2,3}\b(?!\+)")
# A range marker such as `SC49+` / `SC54+` is prose meaning "from here on", not a citation.
SC_RANGE_RE = re.compile(r"\bSC[0-9]{2,3}\+")
INV_RE = re.compile(r"(?<![A-Za-z0-9_])I[0-9]{2}(?![0-9A-Za-z_])")
B_RE = re.compile(r"(?<![A-Za-z0-9_-])B[0-9]{2}(?![0-9A-Za-z_])")
ADR_RE = re.compile(r"\bADR-[0-9]{4}\b")
AMD_RE = re.compile(r"\bAMD-B[0-9]{2}\b")
ERRCODE_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![A-Za-z0-9_])")


class Repo:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.files: "list[str]" = []          # repo-relative paths
        self.text: "dict[str, str]" = {}
        self.parsed: "dict[str, object]" = {}  # rel -> parsed YAML/JSON (None if not parsed)
        self._scan()

    def rel(self, path: str) -> str:
        return os.path.relpath(path, self.root).replace(os.sep, "/")

    def abs(self, rel: str) -> str:
        return os.path.join(self.root, rel)

    def _scan(self):
        for d in SCAN_DIRS:
            base = os.path.join(self.root, d)
            if not os.path.isdir(base):
                continue
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [x for x in dirnames if x not in (".git", "__pycache__")]
                for fn in sorted(filenames):
                    if fn.endswith(".pyc"):
                        continue
                    rel = self.rel(os.path.join(dirpath, fn))
                    # F-A2R1-11: a run writes its own report into evidence/runs/, so including
                    # that directory makes `files_scanned` non-reproducible on a re-run. The
                    # directory holds tool output, never contract content.
                    if rel.startswith("evidence/runs/"):
                        continue
                    self.files.append(rel)
        self.files.sort()
        for rel in self.files:
            try:
                with open(self.abs(rel), "r", encoding="utf-8") as fh:
                    self.text[rel] = fh.read()
            except Exception as exc:
                self.text[rel] = ""
                self.parsed[rel] = ("__READ_ERROR__", str(exc))

    def all_text(self, predicate=None) -> "list[tuple[str, str]]":
        out = []
        for rel in self.files:
            if predicate and not predicate(rel):
                continue
            out.append((rel, self.text.get(rel, "")))
        return out


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_values(node, path="$"):
    """Yield (json-pointer-ish path, value) for every scalar in a parsed document."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_values(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_values(v, "%s[%d]" % (path, i))
    else:
        yield path, node


def walk_keys(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield "%s.%s" % (path, k), k
            yield from walk_keys(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_keys(v, "%s[%d]" % (path, i))


def front_matter(text: str):
    """Return the YAML front-matter block of a markdown file, or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[text.find("\n", 3) + 1:end]
    try:
        return yaml.safe_load(block)
    except Exception:
        return None


# --------------------------------------------------------------------------------------
# CHECK 1 — parse
# --------------------------------------------------------------------------------------

def check_parse(repo: Repo) -> None:
    c = new_check(
        "E0-01-parse",
        "Every YAML/JSON file under contracts/, acceptance/, precode/, evidence/ parses",
        "yaml.safe_load / json.load returns without exception for every .yaml/.yml/.json file",
    )
    for rel in repo.files:
        ext = os.path.splitext(rel)[1].lower()
        if ext not in (".yaml", ".yml", ".json"):
            continue
        c.checked += 1
        txt = repo.text.get(rel, "")
        try:
            if ext == ".json":
                repo.parsed[rel] = json.loads(txt)
            else:
                repo.parsed[rel] = yaml.safe_load(txt)
        except Exception as exc:
            repo.parsed[rel] = None
            c.fail(rel, "parse error: %s" % exc)
    # markdown front matter is parsed too, best effort
    for rel in repo.files:
        if rel.endswith(".md"):
            fm = front_matter(repo.text.get(rel, ""))
            if fm is not None:
                repo.parsed[rel + "#frontmatter"] = fm


# --------------------------------------------------------------------------------------
# CHECK 2 — JSON Schema metaschema
# --------------------------------------------------------------------------------------

DEVIATION_FIELDS = ("rule", "deviation", "reason", "evidence_refs")
# The ratified shape is {rule, deviation, reason, evidence_refs} (Coordinator, FIX4 wave).
# These synonyms are accepted so a declared deviation is never reported as undeclared merely
# because the author used a longer field name; the substitution is recorded as a note.
DEVIATION_SYNONYMS = {
    "rule": ("rule", "convention_deviated_from", "convention", "rule_vi"),
    "deviation": ("deviation", "what_this_schema_does_instead", "deviation_vi", "instead"),
    "reason": ("reason", "reason_vi", "rationale", "rationale_vi"),
    "evidence_refs": ("evidence_refs", "finding_ref", "ruling_ref", "evidence",
                      "equivalence_argument_vi", "proof_refs"),
}


def deviation_field_status(d):
    """Return (missing, synonyms_used) for one declared-deviation entry."""
    missing, synonyms = [], {}
    for canonical, names in DEVIATION_SYNONYMS.items():
        hit = next((n for n in names if n in d and d[n] not in (None, "", [], {})), None)
        if hit is None:
            missing.append(canonical)
        elif hit != canonical:
            synonyms[canonical] = hit
    return missing, synonyms


def get_declared_deviations(doc):
    """Return the x-contract.deviations list of a parsed contract/schema document."""
    if not isinstance(doc, dict):
        return []
    for holder in (doc.get("x-contract"), doc, (doc.get("info") or {}).get("x-contract")
                   if isinstance(doc.get("info"), dict) else None):
        if isinstance(holder, dict) and isinstance(holder.get("deviations"), list):
            return [d for d in holder["deviations"] if isinstance(d, dict)]
    return []


def deviation_covers(devs, keyword: str) -> bool:
    blob = json.dumps(devs, ensure_ascii=False).lower()
    return keyword.lower() in blob


def check_metaschema(repo: Repo) -> None:
    c = new_check(
        "E0-02-metaschema",
        "Every *.schema.json is a valid JSON Schema draft 2020-12 document",
        "Draft202012Validator.check_schema() raises nothing",
    )
    for rel in repo.files:
        if not rel.endswith(".schema.json"):
            continue
        c.checked += 1
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            c.fail(rel, "not a parsed JSON object")
            continue
        declared = doc.get("$schema")
        if declared != "https://json-schema.org/draft/2020-12/schema":
            c.fail(rel, "$schema is %r, expected the 2020-12 metaschema URI" % declared)
        try:
            Draft202012Validator.check_schema(doc)
        except Exception as exc:
            c.fail(rel, "metaschema violation: %s" % str(exc).splitlines()[0])
        # protocol §10 convention: discriminated unions use `oneOf` on a discriminator field.
        # `allOf` + `if/then` is functionally equivalent and is accepted when the schema
        # declares the deviation (ruling R4-04 + FIX4 wave item 2).
        blob = json.dumps(doc, ensure_ascii=False)
        uses_if_then = '"if"' in blob and '"then"' in blob
        uses_oneof = '"oneOf"' in blob
        if uses_if_then and not uses_oneof:
            devs = get_declared_deviations(doc)
            if deviation_covers(devs, "oneof") or deviation_covers(devs, "if/then") \
                    or deviation_covers(devs, "allof"):
                c.deviation(rel, next((d for d in devs if any(
                    k in json.dumps(d, ensure_ascii=False).lower()
                    for k in ("oneof", "if/then", "allof"))), {"rule": "protocol §10 oneOf"}))
            else:
                c.fail(rel, "discrimination by allOf+if/then instead of protocol §10's oneOf, "
                            "with no x-contract.deviations entry declaring it (R4-04)")


# --------------------------------------------------------------------------------------
# CHECK 3 — fixture validation against local schemas
# --------------------------------------------------------------------------------------

def build_schema_store(repo: Repo):
    store = {}
    for rel in repo.files:
        if rel.endswith(".schema.json") and isinstance(repo.parsed.get(rel), dict):
            doc = repo.parsed[rel]
            sid = doc.get("$id")
            if sid:
                store[sid] = doc
            store[rel] = doc
            store[os.path.basename(rel)] = doc
    return store


def resolve_schema(store, target: str):
    """Map a fixture's declared validation target onto a loaded schema."""
    if not target:
        return None
    if target in store:
        return store[target]
    base = os.path.basename(target)
    if base in store:
        return store[base]
    for key, doc in store.items():
        if key.endswith(base):
            return doc
    return None


# The candidate payload a fixture offers to its declared schema. `expected_validation`
# describes the outcome for the PRIMARY payload; the companion slots have fixed meanings.
PRIMARY_PAYLOAD_KEYS = (
    "rejected_payload", "batch", "saved", "payload", "instance", "document",
    "analysis_result", "analysis_result_label", "analysis_result_summary",
    "analysis_result_direction",
)
# `negative_variant` is always a schema-level counterexample; `semantic_variant` is a payload
# that passes the schema and is rejected by a downstream semantic gate (SRC-PLAN §10).
COMPANION_PAYLOAD_EXPECTATION = {"negative_variant": False, "semantic_variant": True}


def _find_payloads(doc, mode):
    """Return [(where, payload, expect_valid)] for a fixture, given its declared mode."""
    if mode in ("reject", "reject_schema"):
        primary_valid = False
    else:                       # accept, reject_semantic, or unspecified
        primary_valid = True
    out = []
    for scope_name, scope in (("$", doc), ("expected", doc.get("expected") or {})):
        if not isinstance(scope, dict):
            continue
        for k in PRIMARY_PAYLOAD_KEYS:
            if isinstance(scope.get(k), dict):
                out.append(("%s.%s" % (scope_name, k), scope[k], primary_valid))
        for k, exp in COMPANION_PAYLOAD_EXPECTATION.items():
            sub = scope.get(k)
            if not isinstance(sub, dict):
                continue
            if "expected_validation" in sub or any(pk in sub for pk in PRIMARY_PAYLOAD_KEYS):
                # A nested sub-fixture: it carries its own declared mode and its own payload.
                sub_mode = sub.get("expected_validation")
                sub_mode = sub_mode.strip().lower() if isinstance(sub_mode, str) else None
                for where, payload, ev in _find_payloads(sub, sub_mode or "accept"):
                    out.append(("%s.%s%s" % (scope_name, k, where.lstrip("$")), payload, ev))
                continue
            out.append(("%s.%s" % (scope_name, k), sub, exp))
    return out


def check_fixture_schema(repo: Repo) -> None:
    c = new_check(
        "E0-03-fixture-schema",
        "Fixtures that declare a JSON Schema validation target validate (or fail) as declared",
        "expected_validation 'accept' => every payload validates; 'reject'/'reject_schema' => "
        "the negative payload raises at least one error; 'reject_semantic' => the payload "
        "validates (rejection is a downstream semantic gate, SRC-PLAN §10); "
        "'not_applicable' => skipped with a reason. A validation_target that is not a "
        "*.schema.json path is a contract reference, not a schema, and is NOT_APPLICABLE.",
    )
    store = build_schema_store(repo)
    resolver = jsonschema.RefResolver(base_uri="", referrer={}, store=store)
    for rel in repo.files:
        if not (rel.startswith("acceptance/fixtures/") and rel.endswith(".json")):
            continue
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            continue
        target = doc.get("validation_target")
        if not target:
            continue
        expected = doc.get("expected_validation")
        mode = expected.strip().lower() if isinstance(expected, str) else None
        if mode == "not_applicable":
            c.note("%s: expected_validation not_applicable; no schema validation attempted" % rel)
            continue
        if not (isinstance(target, str) and ".schema.json" in target):
            c.note("%s: validation_target %r is a contract reference, not a JSON Schema; "
                   "NOT_APPLICABLE for this check" % (rel, target))
            continue
        schema = resolve_schema(store, target)
        if schema is None:
            c.fail(rel, "validation_target %r does not resolve to a local schema" % target)
            continue
        payloads = _find_payloads(doc, mode)
        if not payloads:
            c.fail(rel, "validation_target %r but no recognised payload key "
                        "(looked for %s under $ and $.expected)"
                   % (target, ", ".join(PRIMARY_PAYLOAD_KEYS
                                        + tuple(COMPANION_PAYLOAD_EXPECTATION))))
            continue
        try:
            validator = Draft202012Validator(schema, resolver=resolver)
        except Exception as exc:
            c.fail(rel, "validator construction failed: %s" % exc)
            continue
        for where, payload, expect_valid in payloads:
            c.checked += 1
            errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
            if expect_valid and errors:
                c.fail(rel, "%s: expected VALID but %d schema error(s); first at %s: %s"
                       % (where, len(errors), "/".join(str(p) for p in errors[0].path) or "<root>",
                          errors[0].message.splitlines()[0]))
            elif (not expect_valid) and not errors:
                c.fail(rel, "%s: expected the schema to REJECT this payload but it validates"
                       % where)


# --------------------------------------------------------------------------------------
# Reference indices
# --------------------------------------------------------------------------------------

class Index:
    def __init__(self, repo: Repo):
        self.repo = repo
        self.operations = set()
        self.op_owner = {}
        self.op_callers = {}
        self.error_codes = set()
        self.requirements = {}
        self.req_rows = []
        self.scenarios = {}
        self.invariants = set()
        self.blockers = set()
        self.adrs = set()
        self.amendments = set()
        self.entity_fields = {}
        self.state_fields = {}
        self.entity_owner = {}
        self.allowed_edges = set()
        self.forbidden_edges = {}
        self.denied_cases = []
        self.modules = set()
        self._build()

    def _build(self):
        ports = self.repo.parsed.get("contracts/ports.yaml")
        if isinstance(ports, dict):
            for op in ports.get("operations") or []:
                oid = op.get("operation_id")
                if oid:
                    self.operations.add(oid)
                    self.op_owner[oid] = op.get("owner_module")
                    self.op_callers[oid] = set(op.get("caller_modules") or [])
        errs = self.repo.parsed.get("contracts/errors.yaml")
        if isinstance(errs, dict):
            for e in errs.get("codes") or []:
                if e.get("code"):
                    self.error_codes.add(e["code"])
        csv_path = self.repo.abs("precode/requirements.csv")
        if os.path.isfile(csv_path):
            with open(csv_path, "r", encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    self.req_rows.append(row)
                    self.requirements[row["req_id"]] = row
        sc = self.repo.parsed.get("acceptance/scenarios.yaml")
        if isinstance(sc, dict):
            for s in sc.get("scenarios") or []:
                if s.get("id"):
                    self.scenarios[s["id"]] = s
        # Invariants: I01..I15 are fixed by SRC-PLAN §7; I16/I17 were added by PC02 with a
        # decision record inside contracts/data/invariants.md.
        self.invariants = {"I%02d" % n for n in range(1, 16)}
        inv_txt = self.repo.text.get("contracts/data/invariants.md", "")
        for extra in re.findall(r"^## (I[0-9]{2})", inv_txt, flags=re.M):
            self.invariants.add(extra)
        self.blockers = {"B%02d" % n for n in range(1, 18)}
        for rel in self.repo.files:
            m = re.match(r"precode/adr/(ADR-[0-9]{4})-", rel)
            if m:
                self.adrs.add(m.group(1))
        dr = self.repo.text.get("precode/decision-register.md", "")
        for a in re.findall(r"^### (AMD-B[0-9]{2})", dr, flags=re.M):
            self.amendments.add(a)
        ents = self.repo.parsed.get("contracts/data/entities.yaml")
        if isinstance(ents, dict):
            for e in ents.get("entities") or []:
                name = e.get("name")
                if not name:
                    continue
                self.entity_owner[name] = e.get("owner_module")
                cols = set()
                for f in e.get("fields") or []:
                    if isinstance(f, dict) and f.get("name"):
                        cols.add(f["name"])
                    elif isinstance(f, str):
                        cols.add(f)
                self.entity_fields[name] = cols
        # A state machine exposes a field namespace of its own: `run.status`, `storage.health`,
        # `delivery.state`. These are dotted tokens that are NOT operations and must not be
        # resolved against ports.yaml.
        for name in ("run", "analysis", "report", "delivery", "storage"):
            doc = self.repo.parsed.get("contracts/state/%s.yaml" % name)
            if not isinstance(doc, dict):
                continue
            ns = self.state_fields.setdefault(name, set())
            ns.update(k for k in (doc.get("enums") or {}) if isinstance(k, str))
            # ... and the enum VALUES themselves: `delivery.unknown`, `storage.maintenance`
            # are state values, written in the same dotted form.
            for ev in (doc.get("enums") or {}).values():
                vals = ev.get("values") if isinstance(ev, dict) else ev
                if isinstance(vals, list):
                    ns.update(v for v in vals if isinstance(v, str))
            for f in doc.get("fields") or []:
                if isinstance(f, dict) and f.get("name"):
                    ns.add(f["name"])
                elif isinstance(f, str):
                    ns.add(f)
            # the canonical trio every run-like machine exposes
            ns.update(("status", "state", "health", "phase", "outcome", "stop_reason", "quality"))
        mods = self.repo.parsed.get("contracts/modules.yaml")
        if isinstance(mods, dict):
            for m in mods.get("modules") or []:
                if m.get("id"):
                    self.modules.add(m["id"])
            for ex in mods.get("external_systems") or []:
                if isinstance(ex, dict) and ex.get("id"):
                    self.modules.add(ex["id"])
            for e in mods.get("allowed_edges") or []:
                self.allowed_edges.add((e.get("caller"), e.get("callee"), e.get("operation")))
            for f in mods.get("forbidden_edges") or []:
                if f.get("id"):
                    self.forbidden_edges[f["id"]] = f
            self.denied_cases = list(mods.get("denied_cases") or [])


# --------------------------------------------------------------------------------------
# CHECK 4..7 — reference integrity
# --------------------------------------------------------------------------------------

def structured_strings(repo: Repo, rel: str):
    """Yield (path, string) for every scalar string in a parsed structured file."""
    doc = repo.parsed.get(rel)
    if doc is None or isinstance(doc, tuple):
        return
    for p, v in walk_values(doc):
        if isinstance(v, str):
            yield p, v


def is_structured(rel: str) -> bool:
    return os.path.splitext(rel)[1].lower() in (".yaml", ".yml", ".json")


def in_scope_for_refs(rel: str) -> bool:
    if rel.startswith("precode/source/"):
        return False        # immutable copies of the sources
    if rel.startswith("evidence/runs/"):
        return False        # tool output
    if rel.startswith("evidence/tools/"):
        return False        # this tool
    return True


def check_operations(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-04-operation-refs",
        "Every operation id cited in a structured field exists in contracts/ports.yaml",
        "for each `operation`/`operation_id`/`*_operation`/`operations[]` value, the id is a "
        "key of the ports.yaml inventory",
    )
    op_keys = ("operation", "operation_id", "operations", "inbound_operations",
               "outbound_operations", "operation_refs", "operations_used",
               "consumed_operations", "produced_operations", "action_operation")
    for rel in repo.files:
        if not is_structured(rel) or not in_scope_for_refs(rel):
            continue
        if rel == "contracts/ports.yaml":
            continue
        for path, val in structured_strings(repo, rel):
            leaf = path.rsplit(".", 1)[-1].split("[")[0]
            if leaf not in op_keys:
                continue
            if not OP_RE.fullmatch(val):
                continue
            c.checked += 1
            if val not in idx.operations:
                c.fail(rel, "unknown operation id %r" % val, at=path)


def check_error_codes(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-05-error-code-refs",
        "Every error code cited in a structured field exists in contracts/errors.yaml",
        "for each `error_code`/`error_codes[]`/`expected_error_code` value, the code is "
        "registered in errors.yaml",
    )
    err_keys = ("error_code", "error_codes", "expected_error_code", "error_refs",
                "expected_error_codes", "codes_used", "error_code_expected")
    for rel in repo.files:
        if not is_structured(rel) or not in_scope_for_refs(rel):
            continue
        if rel == "contracts/errors.yaml":
            continue
        for path, val in structured_strings(repo, rel):
            leaf = path.rsplit(".", 1)[-1].split("[")[0]
            if leaf not in err_keys:
                continue
            if not ERRCODE_RE.fullmatch(val):
                continue
            c.checked += 1
            if val not in idx.error_codes:
                c.fail(rel, "unknown error code %r" % val, at=path)


def check_requirement_refs(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-06-requirement-refs",
        "Every REQ-* id cited anywhere resolves to a row in precode/requirements.csv",
        "regex-extracted REQ-* tokens over all in-scope files are a subset of the registry",
    )
    def _req_scope(r):
        # Handoffs are evidence records that legitimately quote malformed ids while
        # reporting them (CR-PC03-01); the corpus under check is the contract baseline.
        return (in_scope_for_refs(r) and r != "precode/requirements.csv"
                and not r.startswith("evidence/handoffs/"))

    for rel, txt in repo.all_text(_req_scope):
        for tok in sorted(set(REQ_RE.findall(txt))):
            c.checked += 1
            if tok not in idx.requirements:
                c.fail(rel, "unknown requirement id %r" % tok)
        # A token that looks like a requirement id but does not match a registry form is a
        # malformed citation; range notations (`REQ-D01..REQ-D59`) are excluded.
        for tok in sorted(set(REQ_LOOSE_RE.findall(txt))):
            if REQ_RE.fullmatch(tok) or tok in idx.requirements:
                continue
            if re.search(re.escape(tok) + r"\s*\.\.", txt) or ".." in tok:
                continue
            if tok in ("REQ-S", "REQ-A", "REQ-D", "REQ-P", "REQ-OQ", "REQ-AC", "REQ-OOS"):
                continue          # bare prefixes used when naming the convention itself
            c.checked += 1
            c.fail(rel, "malformed or unknown requirement citation %r" % tok)


def check_id_refs(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-07-id-refs",
        "Every SC / I / B / ADR / AMD id cited anywhere is defined",
        "SC ids resolve in acceptance/scenarios.yaml; I ids in SRC-PLAN §7 plus invariants.md; "
        "B01..B17; ADR ids to a file in precode/adr/; AMD ids to a section of decision-register.md",
    )
    id_key_hint = re.compile(r"(scenario_refs|invariant_refs|decision_refs|adr_refs|"
                             r"amendment_refs|blocker_refs)")
    # structured, key-scoped (strict)
    for rel in repo.files:
        if not is_structured(rel) or not in_scope_for_refs(rel):
            continue
        for path, val in structured_strings(repo, rel):
            if not id_key_hint.search(path):
                continue
            v = val.strip()
            if SC_RANGE_RE.fullmatch(v):
                c.note("%s: %r is a range marker, not a scenario citation; not resolved" % (rel, v))
                continue
            c.checked += 1
            if SC_RE.fullmatch(v):
                if v not in idx.scenarios:
                    c.fail(rel, "scenario id %r is not defined in acceptance/scenarios.yaml" % v,
                           at=path)
            elif INV_RE.fullmatch(v):
                if v not in idx.invariants:
                    c.fail(rel, "invariant id %r is not defined" % v, at=path)
            elif B_RE.fullmatch(v):
                if v not in idx.blockers:
                    c.fail(rel, "blocker id %r is not in B01..B17" % v, at=path)
            elif ADR_RE.fullmatch(v):
                if v not in idx.adrs:
                    c.fail(rel, "ADR id %r has no file in precode/adr/" % v, at=path)
            elif AMD_RE.fullmatch(v):
                if v not in idx.amendments:
                    c.fail(rel, "amendment id %r is not defined in decision-register.md" % v,
                           at=path)
            else:
                c.checked -= 1  # not an id we own
    # Free-text sweep for SC / ADR / AMD only (these have unambiguous forms).
    #
    # Scope decision (Coordinator ruling, FIX5 wave): `evidence/handoffs/` is EXCLUDED from the
    # free-text id sweep. Handoffs are evidence records, not contracts: they legitimately quote
    # range markers (`SC54+`, "PC05/PC06/PC07 take SC45+"), malformed ids they are reporting, and
    # ids of scenarios a later package will write. Treating that prose as citation produced false
    # positives with no corresponding defect. The same exclusion already applies to the REQ sweep
    # (see `_req_scope`). Structured `scenario_refs` fields inside handoffs are still checked by
    # the key-scoped pass above, so a real dangling citation in a table is still caught.
    for rel, txt in repo.all_text(lambda r: in_scope_for_refs(r)
                                  and not r.startswith("evidence/handoffs/")):
        if rel in ("precode/baseline.json", "acceptance/scenarios.yaml"):
            continue
        for tok in sorted(set(SC_RE.findall(txt))):
            c.checked += 1
            if tok not in idx.scenarios:
                c.fail(rel, "scenario id %r cited in text but not defined in "
                            "acceptance/scenarios.yaml" % tok)
        for tok in sorted(set(ADR_RE.findall(txt))):
            c.checked += 1
            if tok not in idx.adrs:
                c.fail(rel, "ADR id %r cited but no file in precode/adr/" % tok)
        for tok in sorted(set(AMD_RE.findall(txt))):
            c.checked += 1
            if tok not in idx.amendments:
                c.fail(rel, "amendment id %r cited but not defined" % tok)


# --------------------------------------------------------------------------------------
# CHECK 4b — operation- and error-code-shaped tokens in PROSE
# --------------------------------------------------------------------------------------

def check_prose_tokens(repo: Repo, idx: Index) -> None:
    """Resolve dotted and SCREAMING_SNAKE tokens that live in prose.

    Ruling (FIX7): a `<a>.<b>` token resolves if it is EITHER an operation in ports.yaml OR an
    `entity.column` pair in entities.yaml. Reporting is split so the two failure modes are not
    conflated: `E0-04b` is about operations, `E0-04c` about columns. A token whose namespace is
    both an operation domain and an entity name (`run`, `report`, `delivery`, `tag`) is attributed
    to whichever catalogue could plausibly own it, and is only a violation when NEITHER does.
    """
    c = new_check(
        "E0-04b-prose-op-tokens",
        "Operation-shaped tokens in prose resolve against contracts/ports.yaml",
        "Single source of the rule: contracts/ports.yaml conventions.prose_token_rule_vi. A "
        "backticked `<a>.<b>` must resolve to an operation of ports.yaml OR an entity.column of "
        "entities.yaml; tokens whose first segment is neither a known operation domain nor a "
        "known entity name (file paths, YAML structural keys, hosts, library idioms) are ignored. "
        "This check reports the operation half. E0-04 reads structured fields only; this reaches "
        "the sentences, where F-A2R1-01 lived.",
    )
    col = new_check(
        "E0-04c-prose-column-tokens",
        "Column-shaped tokens in prose resolve against contracts/data/entities.yaml",
        "Single source of the rule: contracts/ports.yaml conventions.prose_token_rule_vi. This "
        "check reports the column half. Splitting it out of E0-04b (ruling FIX7) keeps 'someone "
        "named an operation that does not exist' distinct from 'someone named a column that does "
        "not exist' — different owners, different fixes.",
    )
    code = new_check(
        "E0-04d-prose-error-tokens",
        "Error-code-shaped tokens in prose are registered codes or listed vocabulary",
        "A backticked SCREAMING_SNAKE token must be a code in contracts/errors.yaml or a word in "
        "the tool's STATUS_VOCABULARY — which covers the baseline §3 status/claim vocabularies "
        "and the protocol.md message types (Coordinator ruling, FIX7 wave). This is how "
        "F-A2R1-06 (SAVE_ALREADY_EXISTS) was found.",
    )
    domains = {o.split(".", 1)[0] for o in idx.operations}
    if not domains:
        c.blocked("contracts/ports.yaml did not parse; operation tokens cannot be resolved")
    if not idx.entity_fields:
        col.blocked("contracts/data/entities.yaml did not parse; column tokens cannot be resolved")

    def in_scope(rel):
        return (rel.startswith(("contracts/", "acceptance/"))
                and os.path.splitext(rel)[1].lower() in (".yaml", ".yml", ".json", ".md"))

    for rel, txt in repo.all_text(in_scope):
        for tok in sorted(set(PROSE_OP_RE.findall(txt))):
            ns, rest = tok.split(".", 1)
            if rest.split(".")[-1] in FILE_SUFFIXES:
                continue                                   # a filename
            if rest in idx.state_fields.get(ns, ()):       # <state machine>.<field|enum value>
                continue
            is_op_ns = ns in domains
            is_ent_ns = ns in idx.entity_fields
            resolves = (tok in idx.operations) or (rest in idx.entity_fields.get(ns, ()))
            if resolves or not (is_op_ns or is_ent_ns):
                if resolves and is_op_ns and tok in idx.operations:
                    c.checked += 1
                elif resolves and is_ent_ns:
                    col.checked += 1
                continue
            # Unresolved. Attribute it to the catalogue that owns the namespace.
            if is_ent_ns and not is_op_ns:
                col.checked += 1
                col.fail(rel, "prose names column %r, which is not a declared field of entity %r"
                         % (tok, ns))
            elif is_op_ns and not is_ent_ns:
                c.checked += 1
                near = sorted(o for o in idx.operations if o.startswith(ns + "."))
                c.fail(rel, "prose names operation %r, which is not in ports.yaml (operations in "
                            "that domain: %s)" % (tok, ", ".join(near) or "<none>"))
            else:
                # the namespace is BOTH an operation domain and an entity: neither catalogue has it
                col.checked += 1
                col.fail(rel, "prose names %r: %r is both an operation domain and an entity, and "
                              "the token is neither an operation in ports.yaml nor a column of "
                              "that entity" % (tok, ns))
        for tok in sorted(set(PROSE_CODE_RE.findall(txt))):
            if tok in STATUS_VOCABULARY:
                continue
            code.checked += 1
            if tok not in idx.error_codes:
                code.fail(rel, "prose names %r, which is neither a registered error code nor a "
                               "listed vocabulary word" % tok)


# --------------------------------------------------------------------------------------
# CHECK 8 — contract headers
# --------------------------------------------------------------------------------------

def header_required(rel: str) -> bool:
    if rel in HEADER_EXEMPT:
        return False
    for p in HEADER_EXEMPT_PREFIX:
        if rel.startswith(p):
            return False
    ext = os.path.splitext(rel)[1].lower()
    if rel.startswith("contracts/") and ext in (".yaml", ".yml", ".md", ".json"):
        return True
    if rel.startswith("acceptance/") and ext in (".yaml", ".yml", ".json", ".md"):
        return True
    if rel.startswith("precode/") and ext in (".yaml", ".yml"):
        return True
    return False


def check_headers(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-08-contract-header",
        "Every contract / schema / fixture / registry file carries the baseline §3 header",
        "YAML: the 14 fields are top-level keys. Markdown: they are in the YAML front-matter. "
        "JSON Schema: $id/title/description plus an x-contract object. Fixture JSON: an "
        "x-contract object or the directory README lists the file (ruling in baseline §3). "
        "ADRs use the R-05 field set instead.",
    )
    # ADRs: R-05 field set
    for rel in repo.files:
        if not re.match(r"precode/adr/ADR-[0-9]{4}-.*\.md$", rel):
            continue
        c.checked += 1
        fm = repo.parsed.get(rel + "#frontmatter")
        if not isinstance(fm, dict):
            body = repo.text.get(rel, "")
            missing = [f for f in ADR_HEADER_FIELDS
                       if not re.search(r"^[-*]?\s*\**%s\**\s*[::]" % re.escape(f), body, re.M)]
            if missing:
                c.fail(rel, "ADR header missing fields (R-05): %s" % ", ".join(missing))
            continue
        missing = [f for f in ADR_HEADER_FIELDS if f not in fm]
        if missing:
            c.fail(rel, "ADR front-matter missing (R-05): %s" % ", ".join(missing))

    readme_text = {}
    for rel in repo.files:
        if rel.endswith("/README.md"):
            readme_text[os.path.dirname(rel)] = repo.text.get(rel, "")

    for rel in repo.files:
        if not header_required(rel):
            continue
        c.checked += 1
        ext = os.path.splitext(rel)[1].lower()
        doc = repo.parsed.get(rel)
        if rel.endswith(".schema.json"):
            if not isinstance(doc, dict):
                c.fail(rel, "unparsed schema")
                continue
            missing = [k for k in ("$id", "title", "description") if k not in doc]
            xc = doc.get("x-contract")
            if not isinstance(xc, dict):
                missing.append("x-contract")
            else:
                missing += ["x-contract.%s" % f for f in BASELINE_HEADER_FIELDS if f not in xc]
            if missing:
                c.fail(rel, "missing: %s" % ", ".join(missing))
            continue
        if ext == ".json":
            # fixture JSON
            if not isinstance(doc, dict):
                c.fail(rel, "unparsed JSON")
                continue
            xc = doc.get("x-contract")
            if isinstance(xc, dict):
                missing = [f for f in BASELINE_HEADER_FIELDS if f not in xc]
                if missing:
                    c.fail(rel, "x-contract missing: %s" % ", ".join(missing))
                continue
            d = os.path.dirname(rel)
            base = os.path.basename(rel)
            rt = readme_text.get(d)
            if rt is None:
                c.fail(rel, "no x-contract and no directory README.md to carry the header")
            elif base not in rt:
                # A glob line such as `neg-saved-snapshot-*.json` lists the file only loosely.
                globbed = [ln for ln in rt.splitlines()
                           if "*" in ln and fnmatch_line(ln, base)]
                if globbed:
                    c.fail(rel, "directory README.md lists %r only through a glob (%s); "
                                "ruling R4-01 requires every file listed by name"
                           % (base, globbed[0].strip()[:70]))
                else:
                    c.fail(rel, "no x-contract and directory README.md does not list %r" % base)
            continue
        if ext in (".yaml", ".yml"):
            if not isinstance(doc, dict):
                c.fail(rel, "unparsed YAML")
                continue
            missing = [f for f in BASELINE_HEADER_FIELDS if f not in doc]
            if missing and isinstance(doc.get("info"), dict):
                # OpenAPI documents cannot carry arbitrary top-level keys; the header lives in
                # `info.x-contract` (OpenAPI specification extension).
                xc = doc["info"].get("x-contract")
                if isinstance(xc, dict):
                    missing = ["info.x-contract.%s" % f
                               for f in BASELINE_HEADER_FIELDS if f not in xc]
            if missing:
                c.fail(rel, "missing header fields: %s" % ", ".join(missing))
            continue
        if ext == ".md":
            fm = repo.parsed.get(rel + "#frontmatter")
            if not isinstance(fm, dict):
                c.fail(rel, "markdown contract without YAML front-matter")
                continue
            missing = [f for f in BASELINE_HEADER_FIELDS if f not in fm]
            if missing:
                c.fail(rel, "front-matter missing: %s" % ", ".join(missing))


# --------------------------------------------------------------------------------------
# CHECK 9 — state lint
# --------------------------------------------------------------------------------------

def fnmatch_line(line: str, name: str) -> bool:
    import fnmatch as _fn
    for tok in re.findall(r"[A-Za-z0-9_.*-]+\.json", line):
        if _fn.fnmatch(name, tok):
            return True
    return False


def collect_enum_values(enums, name):
    if not isinstance(enums, dict):
        return set()
    node = enums.get(name)
    if isinstance(node, dict):
        vals = node.get("values")
        if isinstance(vals, list):
            return {v for v in vals if isinstance(v, str)}
    if isinstance(node, list):
        return {v for v in node if isinstance(v, str)}
    return set()


def state_of(node):
    """Normalise a transition endpoint into a status string, if determinable."""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        for k in ("status", "state", "health"):
            v = node.get(k)
            if isinstance(v, str):
                return v
    return None


# The primary state enum of each state machine file. Other enums in the same file
# (task_type, attempt_outcome, intent_kind, abort_reason, ...) are attributes, not states.
PRIMARY_STATE_ENUM = {
    "contracts/state/run.yaml": "status",
    "contracts/state/analysis.yaml": "item_state",
    "contracts/state/report.yaml": "status",
    "contracts/state/delivery.yaml": "delivery_state",
    "contracts/state/storage.yaml": "storage_health",
}

CREATION_SENTINELS = ("(chưa tồn tại)", "(chua ton tai)", "(not exist)", "(none)", "-", "∅")
# A transition that deliberately does not move the state writes a no-op sentinel.
NOOP_SENTINELS = ("không đổi", "khong doi", "unchanged", "no change", "giữ nguyên", "giu nguyen")


def split_states(raw):
    """Normalise a transition endpoint into a list of state tokens.

    Handles `a | b`, trailing parentheticals such as `pending (resend)` or
    `pending | retry_wait (KHÔNG đổi)`, and the creation sentinel used for the row that
    creates the row rather than moving it.
    """
    if raw is None:
        return []
    s = state_of(raw)
    if s is None:
        return []
    s = s.strip()
    if s in CREATION_SENTINELS or (s.startswith("(") and s.endswith(")")):
        return ["__CREATE__"]
    if s.strip().lower() in NOOP_SENTINELS:
        return ["__NOOP__"]
    parts = []
    for piece in s.split("|"):
        piece = re.sub(r"\([^)]*\)", " ", piece).strip()
        if not piece:
            continue
        parts.append(piece)
    return parts


def check_state_lint(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-09-state-lint",
        "State machines: closed state enums, reachability, terminal states have no outgoing rows",
        "every token in a transition from/to resolves to a value of that file's primary state "
        "enum (alternatives separated by '|' are split; trailing parentheticals are commentary; "
        "a creation sentinel means the row is created); every state listed as terminal or "
        "non-terminal is reachable from the initial state; a terminal state has no outgoing "
        "transition unless the file names that transition in terminal_state_rule; the "
        "terminal / non-terminal / quasi-terminal lists partition the enum.",
    )
    for rel in sorted(repo.files):
        if not (rel.startswith("contracts/state/") and rel.endswith(".yaml")):
            continue
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            c.fail(rel, "unparsed")
            continue
        enums = doc.get("enums") or {}
        enum_name = PRIMARY_STATE_ENUM.get(rel)
        declared = collect_enum_values(enums, enum_name) if enum_name else set()
        if not declared:
            for name in ("status", "state", "health"):
                declared |= collect_enum_values(enums, name)
        if not declared:
            c.fail(rel, "cannot identify the primary state enum; add it to PRIMARY_STATE_ENUM")
            continue
        terminals = set(doc.get("terminal_states") or [])
        quasi = set(doc.get("quasi_terminal_states") or [])
        nonterm = set(doc.get("non_terminal_states") or [])
        init = state_of(doc.get("initial_state"))
        edges = []
        for t in doc.get("transitions") or []:
            if not isinstance(t, dict):
                continue
            c.checked += 1
            tid = t.get("id", "?")
            frm_list = split_states(t.get("from"))
            to_list = split_states(t.get("to"))
            for label, toks in (("from", frm_list), ("to", to_list)):
                for tok in toks:
                    if tok in ("__CREATE__", "__NOOP__", "any", "nonterminal", "*"):
                        continue
                    if tok not in declared:
                        c.fail(rel, "transition %s: %s state %r is not a value of enum %r"
                               % (tid, label, tok, enum_name))
            for f in frm_list:
                for t2 in to_list:
                    if t2 == "__NOOP__":
                        continue      # the row asserts that nothing moves
                    edges.append((f, t2, tid))
        if init:
            adj = {}
            roots = {init}
            for f, t, _ in edges:
                if f == "__CREATE__":
                    roots.add(t)
                    continue
                adj.setdefault(f, set()).add(t)
            seen, stack = set(roots), list(roots)
            while stack:
                cur = stack.pop()
                for nxt in adj.get(cur, ()):
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            universe = (terminals | nonterm | quasi) or declared
            unreachable = sorted(s for s in universe if s not in seen and s in declared)
            if unreachable:
                c.fail(rel, "states unreachable from initial %r: %s"
                       % (init, ", ".join(unreachable)))
        rule = doc.get("terminal_state_rule")
        rule_txt = json.dumps(rule, ensure_ascii=False) if rule is not None else ""
        for f, t, tid in edges:
            if f in terminals and f != "__CREATE__":
                if tid and tid in rule_txt:
                    continue
                c.fail(rel, "transition %s leaves terminal state %r (-> %r) with no exception "
                            "named in terminal_state_rule" % (tid, f, t))
        overlap = terminals & nonterm
        if overlap:
            c.fail(rel, "states declared both terminal and non-terminal: %s"
                   % ", ".join(sorted(overlap)))
        unlisted = sorted(declared - terminals - nonterm - quasi)
        if unlisted and (terminals or nonterm):
            c.fail(rel, "enum %r values in neither terminal_states nor non_terminal_states nor "
                        "quasi_terminal_states: %s" % (enum_name, ", ".join(unlisted)))


# --------------------------------------------------------------------------------------
# CHECK 10 — denied-edge coverage
# --------------------------------------------------------------------------------------

def check_denied_edges(repo: Repo, idx: Index) -> None:
    a = new_check(
        "E0-10a-denied-edge-scenario",
        "Every forbidden edge in contracts/modules.yaml is covered by a scenario",
        "for each forbidden_edges[].id there is a scenario in acceptance/scenarios.yaml whose "
        "forbidden_edge_refs contains it",
    )
    b = new_check(
        "E0-10b-denied-edge-oracle",
        "Forbidden edge ↔ denied case ↔ boundary fixture event is a content-matching bijection",
        "For each forbidden_edges[] entry: exactly ONE denied_cases[] entry references it, and "
        "that entry's attempted_edge.caller/callee equal the edge's caller/callee and its "
        "expected_error_code is a registered code; AND exactly ONE event in the boundary sweep "
        "fixture references it, with actor == caller, callee == callee, denied_case_ref == that "
        "case's id, the same expected_error_code, and (when it names an operation) the same "
        "operation. A named operation must be OWNED BY the callee when the callee is a MOD-* "
        "module (F-A2R1-05); when the callee is an EXT-* system it names the internal port whose "
        "effect is attempted, per the convention declared in modules.yaml default_deny. Nothing "
        "may reference an unknown edge, and nothing may be referenced twice. Presence of a pinned "
        "case is NOT sufficient (CR-PC01-11).",
    )
    # ---- E0-10a: every forbidden edge is named by at least one scenario
    covered_by_scenario = {}
    sc = repo.parsed.get("acceptance/scenarios.yaml")
    if isinstance(sc, dict):
        for scen in sc.get("scenarios") or []:
            for fe in scen.get("forbidden_edge_refs") or []:
                covered_by_scenario.setdefault(fe, []).append(scen.get("id"))
    for fe_id in sorted(idx.forbidden_edges):
        a.checked += 1
        if fe_id not in covered_by_scenario:
            a.fail("contracts/modules.yaml",
                   "forbidden edge %s has no scenario in acceptance/scenarios.yaml" % fe_id)
    for fe_id in sorted(covered_by_scenario):
        if fe_id not in idx.forbidden_edges:
            a.checked += 1
            a.fail("acceptance/scenarios.yaml",
                   "scenario(s) %s cite forbidden edge %r, which is not in modules.yaml"
                   % (", ".join(str(x) for x in covered_by_scenario[fe_id]), fe_id))

    # ---- E0-10b: index denied cases by the edge they claim
    nc_by_edge = {}
    for nc in idx.denied_cases:
        nc_by_edge.setdefault(nc.get("forbidden_edge_ref"), []).append(nc)
    # index boundary-sweep events by the edge they claim
    BOUNDARY = "acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json"
    ev_by_edge = {}
    bdoc = repo.parsed.get(BOUNDARY)
    if not isinstance(bdoc, dict):
        b.fail(BOUNDARY, "the default-deny sweep fixture is absent or unparsed; the bijection "
                         "cannot be evaluated")
    else:
        for ev in bdoc.get("events") or []:
            if isinstance(ev, dict):
                ev_by_edge.setdefault(ev.get("forbidden_edge_ref"), []).append(ev)

    for fe_id in sorted(idx.forbidden_edges):
        b.checked += 1
        fe = idx.forbidden_edges[fe_id]
        caller, callee = fe.get("caller"), fe.get("callee")

        cases = nc_by_edge.get(fe_id, [])
        if len(cases) != 1:
            b.fail("contracts/modules.yaml",
                   "forbidden edge %s (%s -> %s) is referenced by %d denied_cases[] entries; "
                   "expected exactly 1" % (fe_id, caller, callee, len(cases)))
            continue
        nc = cases[0]
        nc_id = nc.get("id")
        code = nc.get("expected_error_code")
        edge = nc.get("attempted_edge") or {}
        if not code:
            b.fail("contracts/modules.yaml",
                   "%s (edge %s) has no expected_error_code" % (nc_id, fe_id))
        elif code not in idx.error_codes:
            b.fail("contracts/modules.yaml",
                   "%s (edge %s) expects %r, which is not registered in errors.yaml"
                   % (nc_id, fe_id, code))
        if edge.get("caller") != caller or edge.get("callee") != callee:
            b.fail("contracts/modules.yaml",
                   "%s claims edge %s but its attempted_edge is (%s -> %s) while the edge is "
                   "(%s -> %s)" % (nc_id, fe_id, edge.get("caller"), edge.get("callee"),
                                   caller, callee))
        # F-A2R1-05: naming an operation asserts "call it and expect a refusal". That oracle is
        # unrunnable unless the CALLEE actually owns the operation. Where it does not, the honest
        # form is `operation: null` + `event_type` + `operation_absent_reason_vi`.
        nc_op = edge.get("operation")
        if nc_op and str(callee).startswith("EXT-"):
            # Declared convention (modules.yaml default_deny.attempted_edge_operation_rule_vi,
            # clause (b)): an external system owns none of our operations, so the field names the
            # INTERNAL port whose effect the violator is trying to produce. Only require that the
            # named port exists.
            if nc_op not in idx.operations:
                b.fail("contracts/modules.yaml",
                       "%s (edge %s, external callee) names port %r, which is not in ports.yaml"
                       % (nc_id, fe_id, nc_op))
        elif nc_op:
            owner = idx.op_owner.get(nc_op)
            if nc_op not in idx.operations:
                b.fail("contracts/modules.yaml",
                       "%s (edge %s) names operation %r, which is not in ports.yaml"
                       % (nc_id, fe_id, nc_op))
            elif owner != callee:
                b.fail("contracts/modules.yaml",
                       "%s (edge %s) names operation %r, but that operation is owned by %r, not "
                       "by the edge's callee %r — the callee cannot serve it, so the negative "
                       "test is unrunnable. Use operation: null + event_type + "
                       "operation_absent_reason_vi (F-A2R1-05)"
                       % (nc_id, fe_id, nc_op, owner, callee))
        else:
            # F-A2R2-04: modules.yaml default_deny.attempted_edge_operation_rule_vi branch (a)
            # makes BOTH keys mandatory on a null-operation case. This was previously emitted as
            # a note, so the run reported 0 violations while five of six cases broke the rule the
            # same file states. A rule and the check that cites it must not disagree about what
            # is mandatory: these are violations.
            for key in ("event_type", "operation_absent_reason_vi"):
                if not nc.get(key):
                    b.fail("contracts/modules.yaml",
                           "%s (edge %s) has operation: null without %r, which "
                           "default_deny.attempted_edge_operation_rule_vi branch (a) makes "
                           "mandatory" % (nc_id, fe_id, key))

        events = ev_by_edge.get(fe_id, [])
        if len(events) != 1:
            b.fail(BOUNDARY,
                   "forbidden edge %s is asserted by %d events; expected exactly 1"
                   % (fe_id, len(events)))
            continue
        ev = events[0]
        seq = ev.get("seq")
        if ev.get("denied_case_ref") != nc_id:
            b.fail(BOUNDARY, "event %r claims edge %s but denied_case_ref is %r, while the case "
                             "for that edge is %r" % (seq, fe_id, ev.get("denied_case_ref"), nc_id))
        if ev.get("actor") != caller:
            b.fail(BOUNDARY, "event %r (edge %s) actor is %r, expected the edge's caller %r"
                   % (seq, fe_id, ev.get("actor"), caller))
        if ev.get("callee") != callee:
            b.fail(BOUNDARY, "event %r (edge %s) callee is %r, expected %r"
                   % (seq, fe_id, ev.get("callee"), callee))
        if code and ev.get("expected_error_code") != code:
            b.fail(BOUNDARY, "event %r (edge %s) expects %r but denied case %s expects %r"
                   % (seq, fe_id, ev.get("expected_error_code"), nc_id, code))
        ev_op = ev.get("operation")
        if ev_op is not None and edge.get("operation") is not None \
                and ev_op != edge.get("operation"):
            b.fail(BOUNDARY, "event %r (edge %s) names operation %r but denied case %s names %r"
                   % (seq, fe_id, ev_op, nc_id, edge.get("operation")))

    # nothing may claim an edge that does not exist, in either direction
    for ref, cases in sorted(nc_by_edge.items(), key=lambda kv: str(kv[0])):
        if ref is None:
            b.checked += 1
            b.fail("contracts/modules.yaml",
                   "%d denied_cases[] entries carry no forbidden_edge_ref" % len(cases))
        elif ref not in idx.forbidden_edges:
            b.checked += 1
            b.fail("contracts/modules.yaml",
                   "denied case(s) %s reference unknown forbidden edge %r"
                   % (", ".join(str(c.get("id")) for c in cases), ref))
    for ref, events in sorted(ev_by_edge.items(), key=lambda kv: str(kv[0])):
        if ref is None:
            b.checked += 1
            b.fail(BOUNDARY, "%d sweep events carry no forbidden_edge_ref" % len(events))
        elif ref not in idx.forbidden_edges:
            b.checked += 1
            b.fail(BOUNDARY, "event(s) %s reference unknown forbidden edge %r"
                   % (", ".join(str(e.get("seq")) for e in events), ref))
    b.note("bijection checked over %d forbidden edges, %d denied cases, %d sweep events"
           % (len(idx.forbidden_edges), len(idx.denied_cases), sum(len(v) for v in ev_by_edge.values())))


# --------------------------------------------------------------------------------------
# CHECK 11 — traceability
# --------------------------------------------------------------------------------------

def check_traceability(repo: Repo, idx: Index) -> None:
    a = new_check(
        "E0-11a-no-orphan",
        "No P0 requirement with status XN or UQ is an ORPHAN in acceptance/traceability.csv",
        "traceability.csv has one row per requirements.csv row and no row with "
        "priority==P0 and status in {XN, UQ} carries coverage_status == ORPHAN",
    )
    b = new_check(
        "E0-11b-invariant-polarity",
        "Every invariant has a dedicated positive scenario AND a dedicated negative scenario",
        "for each invariant id, acceptance/scenarios.yaml contains at least one scenario citing "
        "it declared polarity 'positive' and at least one declared 'negative'. Ruling F-A2R1-10: "
        "'mixed' counts for NEITHER pole — a combined scenario is not a dedicated counterexample, "
        "and the check must not claim more than its oracle delivers.",
    )
    tpath = repo.abs("acceptance/traceability.csv")
    if not os.path.isfile(tpath):
        a.blocked("acceptance/traceability.csv is absent")
    else:
        with open(tpath, "r", encoding="utf-8", newline="") as fh:
            trows = list(csv.DictReader(fh))
        tids = {r["req_id"] for r in trows}
        rids = set(idx.requirements)
        a.checked = len(trows)
        if len(trows) != len(idx.req_rows):
            a.fail("acceptance/traceability.csv",
                   "row count %d != requirements.csv row count %d" % (len(trows), len(idx.req_rows)))
        for missing in sorted(rids - tids):
            a.fail("acceptance/traceability.csv", "requirement %s has no traceability row" % missing)
        for extra in sorted(tids - rids):
            a.fail("acceptance/traceability.csv", "row %s is not a requirement id" % extra)
        allowed = {"COVERED", "PARTIAL", "ORPHAN", "DEFERRED_P1", "OUT_OF_SCOPE"}
        for r in trows:
            cs = (r.get("coverage_status") or "").strip()
            if cs not in allowed and not cs.startswith("BLOCKED_B"):
                a.fail("acceptance/traceability.csv",
                       "%s: coverage_status %r is outside the declared vocabulary" % (r["req_id"], cs))
            src = idx.requirements.get(r["req_id"])
            if src and cs == "ORPHAN" and src["priority"] == "P0" and src["status"] in ("XN", "UQ"):
                a.fail("acceptance/traceability.csv",
                       "%s (%s/%s) is ORPHAN" % (r["req_id"], src["status"], src["priority"]))

    pos, neg = {}, {}
    for sid, s in idx.scenarios.items():
        pol = (s.get("polarity") or "").strip().lower()
        for i in s.get("invariant_refs") or []:
            if pol == "positive":
                pos.setdefault(i, []).append(sid)
            elif pol == "negative":
                neg.setdefault(i, []).append(sid)
            # 'mixed' deliberately counts for neither pole (F-A2R1-10).
    for i in sorted(idx.invariants):
        b.checked += 1
        if i not in pos:
            b.fail("acceptance/scenarios.yaml", "invariant %s has no positive scenario" % i)
        if i not in neg:
            b.fail("acceptance/scenarios.yaml", "invariant %s has no negative scenario" % i)


# --------------------------------------------------------------------------------------
# CHECK 12 — forbidden strings
# --------------------------------------------------------------------------------------

NEGATION_HINTS = (
    "không", "khong", "chưa", "chua", "no ", "not ", "never", "cấm", "cam ",
    "prohibit", "forbidden", "must not", "vocabulary", "enum", "danh sách", "danh sach",
    "trước khi", "truoc khi", "được coi là", "duoc coi la", "before ", "until ",
    "phải", "phai ", "ceiling", "trần", "tran ", "upgrade", "nâng", "nang ",
    "condition", "điều kiện", "dieu kien", "only when", "chỉ khi", "chi khi",
)


def check_forbidden_strings(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-12-forbidden-strings",
        "No asserted TBD, no status CLOSED/ACCEPTED, no claim above DRAFT_FOR_REVIEW",
        "structured fields: `status`/`claim_ceiling`/`completion_claim` values are checked "
        "exactly. Free text: occurrences are reported when the line carries no negation and "
        "no vocabulary context.",
    )
    status_keys = ("status", "claim_ceiling", "completion_claim", "coverage_status",
                   "evidence_status", "decision_status", "finding_status")
    for rel in repo.files:
        if not in_scope_for_refs(rel):
            continue
        if is_structured(rel):
            for path, val in structured_strings(repo, rel):
                leaf = path.rsplit(".", 1)[-1].split("[")[0]
                if leaf not in status_keys:
                    continue
                c.checked += 1
                v = val.strip()
                if v in ("CLOSED", "ACCEPTED"):
                    c.fail(rel, "status value %r is forbidden this session" % v, at=path)
                if v == "TBD":
                    c.fail(rel, "value TBD is forbidden (baseline §3: no vagueness)", at=path)
                if leaf in ("claim_ceiling", "completion_claim") and v in CLAIM_LABELS_ABOVE_DRAFT:
                    c.fail(rel, "claim %r exceeds the session ceiling DRAFT_FOR_REVIEW" % v, at=path)
        txt = repo.text.get(rel, "")
        for m in re.finditer(r"\bTBD\b", txt):
            line = txt[max(0, txt.rfind("\n", 0, m.start())):
                       txt.find("\n", m.end()) if txt.find("\n", m.end()) != -1 else len(txt)]
            c.checked += 1
            low = line.lower()
            if any(h in low for h in NEGATION_HINTS) or '"TBD"' in line or "`TBD`" in line:
                continue
            c.fail(rel, "bare TBD in text: %s" % line.strip()[:160])
        for label in CLAIM_LABELS_ABOVE_DRAFT:
            for m in re.finditer(r"\b%s\b" % label, txt):
                start = txt.rfind("\n", 0, m.start()) + 1
                end = txt.find("\n", m.end())
                line = txt[start:end if end != -1 else len(txt)]
                c.checked += 1
                low = line.lower()
                if any(h in low for h in NEGATION_HINTS):
                    continue
                if "`%s`" % label in line or '"%s"' % label in line:
                    continue
                c.fail(rel, "claim label %s asserted in text: %s" % (label, line.strip()[:160]))


# --------------------------------------------------------------------------------------
# CHECK 13 — coverage-window contiguity
# --------------------------------------------------------------------------------------

def _iso(v):
    if not isinstance(v, str):
        return None
    try:
        return _dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
    except Exception:
        return None


def check_coverage_windows(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-13-coverage-windows",
        "Coverage windows in reporting fixtures are half-open and contiguous",
        "for every fixture that carries coverage_window rows: window_from < window_to for each "
        "row, and for consecutive sequence numbers window_to[n] == window_from[n+1] (no gap, "
        "no overlap)",
    )
    def collect(node, out):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "coverage_window" and isinstance(v, list):
                    out.extend([x for x in v if isinstance(x, dict)])
                else:
                    collect(v, out)
        elif isinstance(node, list):
            for v in node:
                collect(v, out)

    for rel in repo.files:
        if not (rel.startswith("acceptance/fixtures/") and rel.endswith(".json")):
            continue
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            continue
        rows = []
        collect(doc, rows)
        if not rows:
            continue
        c.checked += 1
        seen = {}
        for r in rows:
            f, t = _iso(r.get("window_from")), _iso(r.get("window_to"))
            seq = r.get("sequence")
            if f is None or t is None:
                continue
            if not (f < t):
                c.fail(rel, "coverage_window sequence %r: window_from >= window_to" % seq)
            if isinstance(seq, int):
                seen.setdefault(seq, (f, t, r))
        for seq in sorted(seen):
            if seq + 1 in seen:
                _, t_this, _ = seen[seq]
                f_next, _, _ = seen[seq + 1]
                if t_this != f_next:
                    c.fail(rel, "coverage_window %d.window_to (%s) != %d.window_from (%s)"
                           % (seq, t_this.isoformat(), seq + 1, f_next.isoformat()))


# --------------------------------------------------------------------------------------
# CHECK 14 — fixture-actor-edge (ruling R-02)
# --------------------------------------------------------------------------------------

DENIED_EDGE_ERROR_CODES = {"UNAUTHORIZED", "FORBIDDEN_EDGE", "CAPABILITY_DENIED"}

# An event that declares `operation: null` makes no call. It must still say which kind of
# non-call it is, so a forgotten operation cannot hide behind an explicit null.
NULL_OPERATION_EVENT_TYPES = ("local_observation", "in_process_call")


def _event_error_codes(ev, doc):
    """Collect the error codes a forbidden-edge event asserts, wherever the fixture puts them."""
    found = set()
    for _p, v in walk_values(ev):
        if isinstance(v, str) and v in DENIED_EDGE_ERROR_CODES:
            found.add(v)
    if found:
        return found
    exp = doc.get("expected")
    if exp is not None:
        for _p, v in walk_values(exp):
            if isinstance(v, str) and v in DENIED_EDGE_ERROR_CODES:
                found.add(v)
    return found


def check_fixture_actor_edge(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-14-fixture-actor-edge",
        "Every fixture event names an allowed caller of the operation (rulings R-02, R4-02)",
        "events[].actor is in ports.yaml caller_modules for events[].operation AND the triple "
        "(actor, owner_module, operation) is in modules.yaml allowed_edges. `performed_by` is "
        "the executing service and is never read as a caller assertion. An event marked "
        "`edge_assertion: forbidden` asserts the opposite: the triple must be ABSENT from "
        "allowed_edges and the fixture must expect one of UNAUTHORIZED / FORBIDDEN_EDGE / "
        "CAPABILITY_DENIED. An event that carries an actor but no recognised operation key "
        "fails loudly rather than being skipped (F-A1R3-02).",
    )
    for rel in repo.files:
        if not (rel.startswith("acceptance/fixtures/") and rel.endswith(".json")):
            continue
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            continue
        for ev in doc.get("events") or []:
            if not isinstance(ev, dict):
                continue
            seq = ev.get("seq")
            actor = ev.get("actor")
            op = ev.get("operation")
            if op is None and "operation" in ev:
                # Explicit null: the fixture declares that this step makes no call at all.
                # Ruling (Coordinator, PC09-FIX1): such an event MUST say WHICH kind of
                # non-call it is, so "no operation" cannot silently mean "operation forgotten".
                c.checked += 1
                et = ev.get("event_type")
                if et is None:
                    c.fail(rel, "event %r has `operation: null` but no `event_type`; an event "
                                "that makes no call must declare which kind it is (%s)"
                           % (seq, " | ".join(NULL_OPERATION_EVENT_TYPES)))
                elif et not in NULL_OPERATION_EVENT_TYPES:
                    c.fail(rel, "event %r has `operation: null` and `event_type: %r`, which is "
                                "not one of %s"
                           % (seq, et, " | ".join(NULL_OPERATION_EVENT_TYPES)))
                continue
            if op is None and "operation_id" in ev:
                c.checked += 1
                c.fail(rel, "event %r uses the key `operation_id`; ruling R4-02 fixes the event "
                            "key at `operation` in every fixture directory" % seq)
                op = ev.get("operation_id")
            if op is None:
                if ev.get("event_type"):
                    continue      # clock ticks, crashes, external faults carry no edge
                if actor:
                    c.checked += 1
                    c.fail(rel, "event %r has an actor but neither `operation` nor `event_type`; "
                                "the gate refuses to skip it silently (F-A1R3-02)" % seq)
                continue
            if not isinstance(op, str) or not OP_RE.fullmatch(op):
                c.checked += 1
                c.fail(rel, "event %r: operation %r is not a <domain>.<verb_noun> id" % (seq, op))
                continue
            c.checked += 1
            forbidden_assertion = str(ev.get("edge_assertion", "")).strip().lower() == "forbidden"
            if op not in idx.operations:
                c.fail(rel, "event %r: operation %r is not in ports.yaml" % (seq, op))
                continue
            if not actor:
                c.fail(rel, "event %r: operation %r without an actor" % (seq, op))
                continue
            callers = idx.op_callers.get(op, set())
            owner = idx.op_owner.get(op)
            triple_allowed = (actor, owner, op) in idx.allowed_edges
            if forbidden_assertion:
                if actor in callers or triple_allowed:
                    c.fail(rel, "event %r is marked `edge_assertion: forbidden` but (%s, %s, %s) "
                                "IS an allowed edge" % (seq, actor, owner, op))
                    continue
                codes = _event_error_codes(ev, doc)
                if not codes:
                    c.fail(rel, "event %r is `edge_assertion: forbidden` but the fixture expects "
                                "none of %s" % (seq, "/".join(sorted(DENIED_EDGE_ERROR_CODES))))
                continue
            if actor not in callers:
                c.fail(rel, "event %r: actor %r is not a declared caller of %r (allowed: %s)"
                       % (seq, actor, op, ", ".join(sorted(callers)) or "<none>"))
                continue
            if not triple_allowed:
                c.fail(rel, "event %r: triple (%s, %s, %s) is not in modules.yaml allowed_edges"
                       % (seq, actor, owner, op))
        for ev in doc.get("events") or []:
            if isinstance(ev, dict) and ev.get("performed_by"):
                pb = ev["performed_by"]
                c.checked += 1
                if pb not in idx.modules:
                    c.fail(rel, "event %r: performed_by %r is not a module id" % (ev.get("seq"), pb))


# --------------------------------------------------------------------------------------
# CHECK 15 — fixture field-level existence (FIX3 ruling)
# --------------------------------------------------------------------------------------

ROW_CONTAINER_KEYS = ("rows",)

# Every fixture directory the gates must cover. The gates themselves match on the
# `acceptance/fixtures/` prefix, so a new directory is picked up automatically; this list exists
# so that a directory silently disappearing (or never being created) is reported rather than
# counted as zero. Ruling FIX5: `boundary/`, `e2e/` and `ui/` join the original six.
EXPECTED_FIXTURE_DIRS = (
    "ai", "boundary", "collection", "e2e", "identity", "recovery", "reporting", "telegram", "ui",
)

# Keys the audit (F-A1R3-01) identified as annotation-style rather than intended columns.
# They are still violations under R4-01 — the ruling admits no allowlist — but classifying
# them lets the readiness review separate "rename the key" from "a schema column is missing".
ANNOTATION_LIKE_KEYS = {
    "note", "note_vi", "target", "save_channel_note", "created_in_transaction",
    "payload_contains", "comment", "comment_vi", "explanation_vi",
}


def check_fixture_fields(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-15-fixture-field-existence",
        "Every column named in given.rows and expected.rows exists in entities.yaml (R4-01)",
        "for each table name under given.rows / expected.rows, every object key is either "
        "(a) a declared field of that entity in contracts/data/entities.yaml, (b) an "
        "annotation whose key starts with '_', or (c) a column carrying an in-file "
        "`pending_cr: CR-…` marker. No per-package allowlist (ruling R4-01).",
    )
    def tables_of(node):
        out = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ROW_CONTAINER_KEYS and isinstance(v, dict):
                    out.append(v)
                else:
                    out.extend(tables_of(v))
        elif isinstance(node, list):
            for v in node:
                out.extend(tables_of(v))
        return out

    # Counting method (Coordinator ruling, FIX4 wave, item 3): one unit per key occurrence
    # under rows.<entity>[], counted once per row. `_`-prefixed keys are annotations and are
    # not counted. This is the number handoffs must be able to reproduce.
    per_dir = {}
    for rel in repo.files:
        if not (rel.startswith("acceptance/fixtures/") and rel.endswith(".json")):
            continue
        doc = repo.parsed.get(rel)
        if not isinstance(doc, dict):
            continue
        d = os.path.basename(os.path.dirname(rel))
        st = per_dir.setdefault(d, {"files": 0, "files_with_rows": 0, "files_without_rows": 0,
                                    "columns_checked": 0, "unresolved": 0,
                                    "annotations_skipped": 0})
        st["files"] += 1
        if '"rows"' in repo.text.get(rel, "") or "'rows'" in repo.text.get(rel, ""):
            st["files_with_rows"] += 1
        else:
            st["files_without_rows"] += 1
        pending = repo.text.get(rel, "") if "pending_cr" in repo.text.get(rel, "") else ""
        for scope_key in ("given", "expected"):
            scope = doc.get(scope_key)
            if scope is None:
                continue
            for tbl in tables_of({"x": scope}):
                for table_name, rows in tbl.items():
                    if not isinstance(rows, list):
                        continue
                    cols = idx.entity_fields.get(table_name)
                    if cols is None:
                        c.checked += 1
                        st["columns_checked"] += 1
                        if pending and table_name in pending:
                            c.note("%s: table %r not in entities.yaml but a pending_cr marker "
                                   "is present" % (rel, table_name))
                        else:
                            st["unresolved"] += 1
                            c.fail(rel, "%s.rows table %r is not an entity in entities.yaml"
                                   % (scope_key, table_name))
                        continue
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        for k in row:
                            if k.startswith("_"):
                                st["annotations_skipped"] += 1
                                continue
                            c.checked += 1
                            st["columns_checked"] += 1
                            if k not in cols:
                                if pending and k in pending:
                                    c.note("%s: %s.%s.%s unresolved but a pending_cr marker is "
                                           "present" % (rel, scope_key, table_name, k))
                                else:
                                    st["unresolved"] += 1
                                    kind = ("annotation_key_without_underscore_prefix"
                                            if k in ANNOTATION_LIKE_KEYS
                                            else "unresolved_column")
                                    c.fail(rel, "%s.rows.%s: key %r is not a field of entity %r "
                                                "and does not start with '_' (R4-01)"
                                           % (scope_key, table_name, k, table_name),
                                           entity=table_name, key=k, klass=kind)
    # Per-directory report. A directory with zero columns checked is NOT clean: it states its
    # oracles in prose (durable_rows_expected / expected_target_state) and this check simply
    # does not reach them. Never present 0 checked as 0 unresolved.
    for d in EXPECTED_FIXTURE_DIRS:
        if d not in per_dir:
            c.checked += 1
            c.fail("acceptance/fixtures/%s" % d,
                   "expected fixture directory is absent or contains no .json file; the gate "
                   "refuses to report a missing directory as zero violations")
    for d in sorted(set(per_dir) - set(EXPECTED_FIXTURE_DIRS)):
        c.note("dir %s is not in EXPECTED_FIXTURE_DIRS; add it there so its absence would be "
               "noticed later" % d)
    breakdown = {}
    for d in sorted(per_dir):
        st = per_dir[d]
        st["verdict"] = ("NOT_APPLICABLE_FREEFORM" if st["columns_checked"] == 0
                         else ("PASS" if st["unresolved"] == 0 else "FAIL"))
        breakdown[d] = st
        c.note("dir %-10s files=%-3d with_rows=%-3d without_rows=%-3d columns_checked=%-5d "
               "unresolved=%-3d annotations_skipped=%-4d -> %s"
               % (d, st["files"], st["files_with_rows"], st["files_without_rows"],
                  st["columns_checked"], st["unresolved"], st["annotations_skipped"],
                  st["verdict"]))
    c.detail = {"per_directory": breakdown,
                "counting_method": "one unit per non-underscore key occurrence under "
                                   "rows.<entity>[], counted once per row"}


# --------------------------------------------------------------------------------------
# CHECK 16 — scenario catalogue integrity
# --------------------------------------------------------------------------------------

def check_scenarios(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-16-scenario-catalogue",
        "acceptance/scenarios.yaml is internally complete",
        "every AC-01..AC-18 has a scenario; every scenario id is unique and contiguous from "
        "SC01; every fixture_refs path exists on disk or is the literal MISSING; every "
        "error_refs code is registered; every requirement_refs id resolves; every scenario "
        "declares an evidence level and status NOT_RUN",
    )
    sc = repo.parsed.get("acceptance/scenarios.yaml")
    if not isinstance(sc, dict):
        c.blocked("acceptance/scenarios.yaml absent or unparsed")
        return
    scenarios = sc.get("scenarios") or []
    ids = [s.get("id") for s in scenarios]
    c.checked = len(scenarios)
    dupes = {i for i in ids if ids.count(i) > 1}
    for d in sorted(dupes):
        c.fail("acceptance/scenarios.yaml", "duplicate scenario id %r" % d)
    nums = sorted(int(i[2:]) for i in ids if i and SC_RE.fullmatch(i))
    if nums:
        expected = list(range(1, max(nums) + 1))
        gaps = [n for n in expected if n not in nums]
        if gaps:
            c.fail("acceptance/scenarios.yaml",
                   "scenario numbering has gaps: %s" % ", ".join("SC%02d" % n for n in gaps))
    ac_covered = set()
    valid_levels = {"E0", "E1", "E2", "E3", "E4"}
    for s in scenarios:
        sid = s.get("id", "?")
        for r in s.get("requirement_refs") or []:
            if r.startswith("REQ-AC"):
                ac_covered.add(r)
            if r not in idx.requirements:
                c.fail("acceptance/scenarios.yaml", "%s cites unknown requirement %r" % (sid, r))
        for e in s.get("error_refs") or []:
            if e not in idx.error_codes:
                c.fail("acceptance/scenarios.yaml", "%s cites unknown error code %r" % (sid, e))
        for f in s.get("fixture_refs") or []:
            if f == "MISSING":
                continue
            if not os.path.isfile(repo.abs(f)):
                c.fail("acceptance/scenarios.yaml", "%s fixture_refs path %r does not exist" % (sid, f))
        for ct in s.get("contract_refs") or []:
            p = ct.split("#", 1)[0].strip()
            if p and not os.path.isfile(repo.abs(p)):
                c.fail("acceptance/scenarios.yaml", "%s contract_refs path %r does not exist" % (sid, p))
        lvl = s.get("evidence_level_required")
        if lvl not in valid_levels:
            c.fail("acceptance/scenarios.yaml", "%s evidence_level_required %r invalid" % (sid, lvl))
        if s.get("status") != "NOT_RUN":
            c.fail("acceptance/scenarios.yaml", "%s status %r must be NOT_RUN this session"
                   % (sid, s.get("status")))
        if (s.get("polarity") or "").lower() not in ("positive", "negative", "mixed"):
            c.fail("acceptance/scenarios.yaml", "%s polarity %r invalid" % (sid, s.get("polarity")))
        for i in s.get("invariant_refs") or []:
            if i not in idx.invariants:
                c.fail("acceptance/scenarios.yaml", "%s cites unknown invariant %r" % (sid, i))
    for n in range(1, 19):
        r = "REQ-AC%02d" % n
        if r not in ac_covered:
            c.fail("acceptance/scenarios.yaml", "%s has no scenario" % r)
    # every error code needs at least one scenario
    used = set()
    for s in scenarios:
        used |= set(s.get("error_refs") or [])
    for code in sorted(idx.error_codes):
        c.checked += 1
        if code not in used:
            c.fail("acceptance/scenarios.yaml", "error code %s has no scenario" % code)


# --------------------------------------------------------------------------------------
# CHECK 17 — declared deviations are well formed and the header exceptions are written down
# --------------------------------------------------------------------------------------

def check_declared_deviations(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-17-declared-deviations",
        "Every declared deviation is well formed and every header exemption is written down",
        "an x-contract.deviations entry carries rule / deviation / reason / evidence_refs. "
        "Every path in HEADER_EXEMPT / HEADER_EXEMPT_PREFIX has its exception declared in a "
        "readable place (baseline §3 as amended by ruling R-05, precode/adr/README.md, or "
        "precode/baseline.json.requirements_csv_contract_header).",
    )
    for rel in repo.files:
        devs = get_declared_deviations(repo.parsed.get(rel))
        for d in devs:
            c.checked += 1
            missing, synonyms = deviation_field_status(d)
            if missing:
                c.fail(rel, "x-contract.deviations entry %r missing %s"
                       % (d.get("id", "?"), ", ".join(missing)))
                continue
            if synonyms:
                c.note("%s: deviation %r uses non-ratified field names %s (content present; "
                       "ruling names are rule/deviation/reason/evidence_refs)"
                       % (rel, d.get("id", "?"),
                          ", ".join("%s->%s" % (k, v) for k, v in sorted(synonyms.items()))))
            c.deviation(rel, {"rule": str(d.get("rule") or d.get("convention_deviated_from"))[:200],
                              "id": d.get("id"),
                              "declared_fields_ok": True,
                              "synonyms_used": synonyms})
    # the two standing header exceptions must be discoverable
    adr_readme = repo.text.get("precode/adr/README.md", "")
    c.checked += 1
    if "R-05" not in adr_readme:
        c.fail("precode/adr/README.md",
               "the ADR header exception (ruling R-05) is not declared in the ADR index")
    baseline = repo.parsed.get("precode/baseline.json")
    c.checked += 1
    if not (isinstance(baseline, dict)
            and isinstance(baseline.get("requirements_csv_contract_header"), dict)):
        c.fail("precode/baseline.json",
               "requirements.csv is header-exempt but baseline.json carries no "
               "requirements_csv_contract_header substitute")
    else:
        hdr = baseline["requirements_csv_contract_header"]
        missing = [f for f in BASELINE_HEADER_FIELDS if f not in hdr]
        if missing:
            c.fail("precode/baseline.json",
                   "requirements_csv_contract_header missing: %s" % ", ".join(missing))
    # acceptance/traceability.csv is a CSV for the same reason requirements.csv is: a comment or
    # front-matter line would break `csv.DictReader`. Its substitute header lives in the
    # front-matter of precode/review.md.
    c.checked += 1
    review_fm = repo.parsed.get("precode/review.md#frontmatter")
    if not os.path.isfile(repo.abs("acceptance/traceability.csv")):
        c.note("acceptance/traceability.csv absent; header substitute not checked")
    elif not (isinstance(review_fm, dict)
              and isinstance(review_fm.get("traceability_csv_contract_header"), dict)):
        c.fail("precode/review.md",
               "acceptance/traceability.csv is header-exempt (CSV) but review.md front-matter "
               "carries no traceability_csv_contract_header substitute")
    else:
        hdr = review_fm["traceability_csv_contract_header"]
        missing = [f for f in BASELINE_HEADER_FIELDS if f not in hdr]
        if missing:
            c.fail("precode/review.md",
                   "traceability_csv_contract_header missing: %s" % ", ".join(missing))


# --------------------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E0 static checks for the Research Radar baseline")
    here = os.path.dirname(os.path.abspath(__file__))
    default_repo = os.path.abspath(os.path.join(here, os.pardir, os.pardir))
    ap.add_argument("--repo", default=default_repo, help="repository root (default: %(default)s)")
    ap.add_argument("--json-out", default=None, help="write the machine-readable report here")
    ap.add_argument("--only", default=None, help="comma-separated check id prefixes to run")
    args = ap.parse_args(argv)

    started = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    repo = Repo(args.repo)

    check_parse(repo)
    idx = Index(repo)
    check_metaschema(repo)
    check_fixture_schema(repo)
    check_operations(repo, idx)
    check_error_codes(repo, idx)
    check_prose_tokens(repo, idx)
    check_requirement_refs(repo, idx)
    check_id_refs(repo, idx)
    check_headers(repo, idx)
    check_state_lint(repo, idx)
    check_denied_edges(repo, idx)
    check_traceability(repo, idx)
    check_forbidden_strings(repo, idx)
    check_coverage_windows(repo, idx)
    check_fixture_actor_edge(repo, idx)
    check_fixture_fields(repo, idx)
    check_scenarios(repo, idx)
    check_declared_deviations(repo, idx)

    for _c in CHECKS:
        _c.finalize()
    selected = CHECKS
    if args.only:
        prefixes = tuple(p.strip() for p in args.only.split(","))
        selected = [c for c in CHECKS if c.id.startswith(prefixes)]

    ended = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    baseline_hashes = {}
    for rel in repo.files:
        if rel.startswith(("contracts/", "acceptance/")) or rel in (
                "precode/requirements.csv", "precode/baseline.json"):
            try:
                baseline_hashes[rel] = sha256_file(repo.abs(rel))
            except Exception:
                baseline_hashes[rel] = None
    for src in ("research-radar-spec.md", "research-radar-pre-code-plan.md"):
        p = os.path.join(repo.root, src)
        if os.path.isfile(p):
            baseline_hashes[src] = sha256_file(p)

    n_fail = sum(1 for c in selected if c.status == "FAIL")
    n_pass = sum(1 for c in selected if c.status == "PASS")
    n_blocked = sum(1 for c in selected if c.status == "BLOCKED")
    n_na = sum(1 for c in selected if c.status == "NOT_APPLICABLE")

    report = {
        "tool": "evidence/tools/e0_check.py",
        "tool_version": "0.1.0",
        "evidence_level": "E0",
        "review_type": "SELF_VALIDATION",
        "repo": repo.root,
        "started_at": started,
        "ended_at": ended,
        "environment": {
            "python": sys.version.split()[0],
            "pyyaml": getattr(yaml, "__version__", "unknown"),
            "jsonschema": getattr(jsonschema, "__version__", "unknown"),
            "platform": sys.platform,
        },
        "files_scanned": len(repo.files),
        "summary": {
            "checks": len(selected), "pass": n_pass, "fail": n_fail,
            "blocked": n_blocked, "not_applicable": n_na,
            "total_violations": sum(len(c.violations) for c in selected),
        },
        "checks": [c.as_dict() for c in selected],
        "baseline_hashes": baseline_hashes,
        "limitations": [
            "E0 only. Nothing here proves that any code exists or that any guard runs "
            "(SRC-PLAN §14.2).",
            "Reference checks find dangling references, not missing ones: a relationship "
            "nobody wrote down cannot be detected.",
            "No OpenAPI 3.1 validator is installed in this environment, so "
            "contracts/http/openapi.yaml is checked only as YAML plus reference integrity.",
            "Fixture semantics are read, not executed. A fixture that parses and whose columns "
            "resolve is not a passing test.",
            "The free-text half of E0-12 is heuristic: it reports lines and a human must read "
            "them; it can over-report.",
        ],
    }

    if args.json_out:
        out = os.path.abspath(args.json_out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")

    # human summary
    print("E0 static check — Research Radar pre-code baseline")
    print("repo: %s" % repo.root)
    print("started %s  ended %s  files scanned %d" % (started, ended, len(repo.files)))
    print("python %s · PyYAML %s · jsonschema %s"
          % (sys.version.split()[0], getattr(yaml, "__version__", "?"),
             getattr(jsonschema, "__version__", "?")))
    print("")
    width = max(len(c.id) for c in selected) if selected else 10
    for c in selected:
        print("%-6s %-*s  checked=%-6d violations=%-5d %s"
              % (c.status, width, c.id, c.checked, len(c.violations), c.title))
        for v in c.violations[:12]:
            print("         - %s: %s" % (v.get("where"), v.get("detail")))
        if len(c.violations) > 12:
            print("         - ... %d more (see the JSON report)" % (len(c.violations) - 12))
        for n in c.notes[:4]:
            print("         # %s" % n)
        if len(c.notes) > 4:
            print("         # ... %d more notes" % (len(c.notes) - 4))
    print("")
    print("TOTAL: %d checks — PASS %d · FAIL %d · BLOCKED %d · N/A %d · violations %d"
          % (len(selected), n_pass, n_fail, n_blocked, n_na,
             sum(len(c.violations) for c in selected)))
    print("This is SELF_VALIDATION at evidence level E0. It proves internal consistency of the "
          "checked subset only.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(2)
