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
import ast
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

# Records ABOUT the work rather than part of the contract corpus. Free-text id sweeps skip
# these: they quote ids they are reporting as wrong, and ids not yet created. Structured
# fields inside them are still checked, so a dangling citation in a table is still caught.
COORDINATION_RECORD_PREFIXES = ("evidence/handoffs/", "evidence/coordination/")

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
    # Ratification vocabulary (OD-20260907-01). `ACCEPTED_WORKING_VALUE` is the Owner's
    # "accepted, but the number may change once measured" state — item 20/22/23 of the record.
    # It is deliberately NOT plain `ACCEPTED`, and that precision is worth preserving.
    "ACCEPTED_WORKING_VALUE", "RATIFIED", "PROVISIONAL",
    # protocol.md message types (Coordinator ruling, FIX7 wave): these are message kinds, not
    # error codes, and they legitimately appear in contract prose.
    "OWNER_DECISION_REQUEST", "TASK_PACKET", "HANDOFF", "AUDIT_REPORT", "FROZEN_CANDIDATE",
    "WRITE_LEASE", "FINDING_DISPOSITION", "EVIDENCE_RECORD", "AUTHORITY_GRANT",
    "AUTHORITY_REVOCATION", "REVIEW_WAIVED", "NOT_APPLICABLE_FREEFORM",
    # baseline §3 requirement-status vocabulary
    "XN", "UQ", "KC",
    # Test-disposition vocabulary introduced by the Coordinator ruling on `F-A3R1-08`
    # (post-A3-R1 fix wave, 2026-09-07T11:00Z) and shipped in
    # `tests/integration/test_denied_edges.py`: the 14 `CAPABILITY_DENIED` sweep edges are
    # process/network-capability edges that no HTTP or service-layer test can reach, so they are
    # asserted as NOT_TESTABLE_AT_THIS_LAYER with the enforcing mechanism named per
    # `contracts/modules.yaml` — and are never counted as passed. It is a status word about a
    # test, not an error code, which is why `E0-05`/`E0-04d` must not demand it be in
    # `errors.yaml`. Added at PKT-PC09-P1.
    "NOT_TESTABLE_AT_THIS_LAYER",
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
# The only executed statuses a scenario may carry this session (E0-16). E3/E4 are deliberately
# NOT in the pattern: nothing live and nothing multi-period has been run.
SCENARIO_PASS_RE = re.compile(r"PASS \((E1|E2)\)")
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


def claim_fields(repo: Repo, rel: str):
    """Yield (path, string) for the structured fields the CLAIM rule reads.

    F-A3R4-01: `E0-12`'s own note said "their STRUCTURED fields are still checked", and that was
    true of `.yaml`/`.json` and false of Markdown FRONT MATTER — which no claim scan reached at
    all. A Markdown file's front matter IS a structured field set (`check_headers` has read it
    since the beginning, as `rel + "#frontmatter"`), so the honest fix is to read it here too
    rather than to narrow the sentence. This closes the gap the finding names in
    `evidence/coordination/*.md` AND the wider pre-existing one in `evidence/handoffs/*.md`,
    which does make claims and had only the prose sweep guarding it.
    """
    seen = False
    for p, v in structured_strings(repo, rel):
        seen = True
        yield p, v
    if seen:
        return
    fm = repo.parsed.get(rel + "#frontmatter")
    if isinstance(fm, dict):
        for p, v in walk_values(fm):
            if isinstance(v, str):
                yield "frontmatter" + p[1:] if p.startswith("$") else p, v


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
        # Coordination records — handoffs, rulings, packets, the Coordinator ledger — are
        # evidence ABOUT the corpus, not part of it. They legitimately quote ids they are
        # reporting as wrong (FIX3-rulings names `REQ-S8.4-01` in order to have it replaced)
        # and ids a later package will create. The corpus under check is the contract baseline.
        return (in_scope_for_refs(r) and r != "precode/requirements.csv"
                and not r.startswith(COORDINATION_RECORD_PREFIXES))

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
                                  and not r.startswith(COORDINATION_RECORD_PREFIXES)):
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
            partial = None
            if isinstance(xc, dict):
                missing = [f for f in BASELINE_HEADER_FIELDS if f not in xc]
                if not missing:
                    continue
                # The oracle is "an x-contract object OR the directory README lists the file".
                # A fixture that carries a PARTIAL x-contract (e.g. only the ratification fields
                # ruling F-A2R5-04 asks for) has not lost the README route it already satisfied.
                # Treating a partial header as an exclusive branch would make adding provenance
                # break a file that was compliant — a check punishing the fix it asked for.
                partial = missing
            d = os.path.dirname(rel)
            base = os.path.basename(rel)
            rt = readme_text.get(d)
            if partial is not None and rt is not None and base in rt:
                c.note("%s carries a partial x-contract (missing %s) and is listed by name in "
                       "%s/README.md, which is the route the ruling allows" %
                       (rel, ", ".join(partial), d))
                continue
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


# Ratification of OD-20260907-01 (Owner, 2026-09-07) changed what these words mean. Before it,
# `ACCEPTED`/`CONTRACT_READY` anywhere was a false claim. After it, they are true in exactly the
# scopes the Owner ratified — and still false everywhere else. The check therefore became a
# SCOPE check rather than a blanket ban (CR-PC01-13).
RATIFICATION_ID = "OD-20260907-01"
RATIFICATION_RECORD = "precode/owner-decisions.md"

# F-A2R5-03: eligibility is an explicit ALLOWLIST held as DATA in precode/gates.yaml
# (`ratified_contract_scopes`), which cites OD-20260907-01. It used to be a denylist of prefixes
# written in this source file, with "eligible" as the default for anything under contracts/ or
# acceptance/. That polarity meant a newly added file was ratified-eligible and nobody was told —
# the direct cause of F-A2R5-04. The list now lives outside the tool so that widening the Owner's
# ratified scope is an edit to a contract, not an edit to a checker.
RATIFIED_SCOPES_FILE = "precode/gates.yaml"

CLAIM_LABELS_ABOVE_CONTRACT_READY = [
    "IMPLEMENTATION_VERIFIED", "INTEGRATION_VERIFIED",
    "LIVE_FEASIBILITY_VERIFIED", "PRODUCT_ACCEPTED",
]

# CR-P0-02. Until Phase 0/1, this check's oracle said "no code exists, so nothing above
# CONTRACT_READY is establishable", and that sentence was true. It stopped being true when the
# skeleton and the four Phase 1 cards shipped code that an independent auditor (A3) reproduced.
# The rule is therefore narrowed rather than dropped:
#
#   * `IMPLEMENTATION_VERIFIED` — and NOTHING above it — may appear in a file under
#     `evidence/handoffs/**` or `evidence/runs/**` THAT CITES AN A3 REPORT. The citation is what
#     makes the label an evidence reference instead of a self-award: a Worker's own run cannot
#     raise its own ceiling (`evidence/manifest.schema.json` caps a `SELF_VALIDATION` record at
#     `CONTRACT_READY`, and that cap is unchanged).
#   * `contracts/**`, `acceptance/**` and `precode/**` are UNCHANGED: every label above
#     CONTRACT_READY stays forbidden there, cited or not. A contract does not become verified
#     because code that reads it passed a test.
#   * `INTEGRATION_VERIFIED`, `LIVE_FEASIBILITY_VERIFIED` and `PRODUCT_ACCEPTED` stay forbidden
#     everywhere in the scanned scope: no integration run, no live probe and no owner acceptance
#     has happened.
#
# Granularity, stated so the oracle is not read as wider than the measurement: the citation is
# checked PER FILE, not per record. A handoff that cites an A3 report anywhere may therefore
# carry the label on a record the report did not verdict. The per-record obligation is enforced
# by `evidence/manifest.schema.json` and by the review, not here.
PHASE1_CLAIM_LABEL = "IMPLEMENTATION_VERIFIED"
PHASE1_CLAIM_PREFIXES = ("evidence/handoffs/", "evidence/runs/")
# The three places an evidence RECORD can live. `evidence/index.json` is the registry: it embeds
# each record verbatim, so a label smuggled into it is a label in a record. It is added here at
# PKT-PC09-P1-FIX1 for the same reason `evidence/runs/` is (F-A3R3-01): the rule text is about
# records, and a rule that names a tree it never reads is worse than no rule. This is a
# TIGHTENING relative to the previous wave, in which `claim.supports_label` was checked in no
# file at all — but it also EXTENDS the CR-P0-02 permission to a third path, which is a Worker
# reading a Coordinator rule slightly wider than its literal text. `CR-PC09-17` asks the
# Coordinator to ratify this reading or narrow it; until then the extension is declared here,
# in the check's oracle, and in the handoff, rather than applied quietly.
EVIDENCE_RECORD_LOCATIONS = ("evidence/handoffs/", "evidence/runs/", "evidence/index.json")
# Records ABOUT the work rather than claims made BY a file: packets, rulings, the ledger. A
# dispatch that asks "may IMPLEMENTATION_VERIFIED stand for these four cards?" is quoting the
# label it is asking about, exactly as an `agent-tasks/` card's `claim_ceiling` names the ceiling
# of the work it orders. The free-text claim sweep therefore skips this ONE prefix and counts
# what it skipped (below), the same treatment `agent-tasks/` already gets. `evidence/handoffs/`
# is deliberately NOT here: a handoff is where a package states its own completion claim, which
# is precisely what CR-P0-02 governs.
DISPATCH_RECORD_PREFIXES = ("evidence/coordination/",)
# Claim fields as they are spelled in a manifest record, in addition to `status_keys`.
RECORD_CLAIM_KEYS = ("supports_label",)
A3_REPORT_RE = re.compile(r"\bA3-R\d+-report\.md\b|\bAUDIT_REPORT\s+`?A3-R\d+`?")


def in_evidence_record_tree(rel: str) -> bool:
    return rel == "evidence/index.json" or rel.startswith(PHASE1_CLAIM_PREFIXES)


def cites_a3_report(repo, rel: str) -> bool:
    """True when this file cites an A3 independent-audit report by name."""
    return bool(A3_REPORT_RE.search(repo.text.get(rel, "")))


def phase1_label_allowed(repo, rel: str, label: str) -> bool:
    """CR-P0-02: is `label` permitted in `rel`?"""
    if label != PHASE1_CLAIM_LABEL:
        return False
    if not in_evidence_record_tree(rel):
        return False
    return cites_a3_report(repo, rel)


def run_record_files(repo) -> "list[str]":
    """`evidence/runs/**` paths, read on demand.

    `Repo._scan` deliberately excludes this tree so that `files_scanned` is reproducible across
    runs (F-A2R1-11) — a run writes its own report into it. That exclusion is right for
    `files_scanned` and wrong for the claim rule, which the oracle says covers run records
    (F-A3R3-01). So the tree is walked HERE, for this check only, and the files are counted in
    this check's `items_checked` and in a note — never in `files_scanned`.

    Only STRUCTURED claim fields are examined in this tree. The free-text sweep is deliberately
    not applied: an E0 report is itself a run file, and it embeds this very oracle, which names
    every forbidden label. Sweeping prose here would make the tool fail on its own output. A run
    file is a JSON record; its claim lives in a field, and that is what is checked.
    """
    base = os.path.join(repo.root, "evidence", "runs")
    if not os.path.isdir(base):
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [x for x in dirnames if x not in (".git", "__pycache__")]
        for fn in sorted(filenames):
            if fn.endswith(".pyc"):
                continue
            out.append(repo.rel(os.path.join(dirpath, fn)))
    return sorted(out)


_ALLOWLIST_CACHE = {}


def ratified_allowlist(repo: Repo):
    """(files, directories, error) from the ratified-scope allowlist in precode/gates.yaml.

    `error` is a string when the allowlist cannot be read or does not cite the ratification. A
    caller that gets an error must BLOCK, never silently treat everything as ineligible (which
    would look like a clean PASS) and never fall back to a built-in list (which would put the
    scope back inside the tool).
    """
    key = id(repo)
    if key in _ALLOWLIST_CACHE:
        return _ALLOWLIST_CACHE[key]
    doc = repo.parsed.get(RATIFIED_SCOPES_FILE)
    block = doc.get("ratified_contract_scopes") if isinstance(doc, dict) else None
    if not isinstance(block, dict):
        out = (frozenset(), tuple(), "%s carries no `ratified_contract_scopes` block" %
               RATIFIED_SCOPES_FILE)
    elif RATIFICATION_ID not in str(block.get("ratification_ref", "")):
        out = (frozenset(), tuple(), "%s allowlist does not cite %s" %
               (RATIFIED_SCOPES_FILE, RATIFICATION_ID))
    else:
        files, dirs = set(), []
        for scope in block.get("scopes") or []:
            if not isinstance(scope, dict):
                continue
            for f in scope.get("files") or []:
                files.add(str(f).strip())
            for d in scope.get("directories") or []:
                d = str(d).strip()
                dirs.append(d if d.endswith("/") else d + "/")
        out = (frozenset(files), tuple(dirs), None if files else
               "%s allowlist is empty" % RATIFIED_SCOPES_FILE)
    _ALLOWLIST_CACHE[key] = out
    return out


def contract_ready_eligible(repo: Repo, rel: str) -> bool:
    """Is this exact path on the Owner-ratified allowlist? Default is NO."""
    files, dirs, err = ratified_allowlist(repo)
    if err:
        return False
    if rel in files:
        return True
    return any(rel.startswith(d) for d in dirs)


def ratification_ref_of(repo: Repo, rel: str):
    """The file's ratification reference, read ONLY from its declared contract header.

    F-A2R5-03 mutation M6b: moving the reference out of the header and leaving a prose line that
    mentions the string used to satisfy this function, so a file could claim CONTRACT_READY on a
    sentence. A header field is a declaration; a sentence is a mention. Only the first is a claim
    the file makes about itself, so only the first counts here. There is deliberately NO regex
    fallback over the file text.
    """
    doc = repo.parsed.get(rel)
    if not isinstance(doc, dict):
        doc = repo.parsed.get(rel + "#frontmatter")
    if not isinstance(doc, dict):
        return None
    holders = [doc, doc.get("x-contract")]
    info = doc.get("info")
    if isinstance(info, dict):
        holders.append(info.get("x-contract"))
    for holder in holders:
        if isinstance(holder, dict) and holder.get("ratification_ref"):
            return holder["ratification_ref"]
    return None


def claim_label_violation(c, repo, rel: str, path: str, v: str) -> bool:
    """One rule, one place: is claim label `v` at `rel`:`path` permitted? Fails `c` if not.

    Applied identically to files inside `repo.files` and to `evidence/runs/**` files walked
    separately, so the two trees cannot drift apart the way they did before F-A3R3-01.
    """
    if v not in CLAIM_LABELS_ABOVE_CONTRACT_READY:
        return False
    if phase1_label_allowed(repo, rel, v):
        return False
    if in_evidence_record_tree(rel):
        if v == PHASE1_CLAIM_LABEL:
            c.fail(rel, "claims %s but this record cites no A3 report; a Worker may not raise "
                        "its own ceiling (CR-P0-02)" % v, at=path)
        else:
            c.fail(rel, "claims %s inside an evidence-record tree; CR-P0-02 opened those trees "
                        "for %s ONLY, and no gate for %s is open (G6-X1 / SP1-X2 / G7)"
                   % (v, PHASE1_CLAIM_LABEL, v), at=path)
    else:
        c.fail(rel, "claim %r exceeds CONTRACT_READY and this file is outside the evidence-record "
                    "trees CR-P0-02 opened (%s)" % (v, ", ".join(EVIDENCE_RECORD_LOCATIONS)),
               at=path)
    return True


def check_forbidden_strings(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-12-forbidden-strings",
        "Ratified vocabulary is used only where the Owner ratified it; nothing claims more",
        "After OD-20260907-01: `ACCEPTED` / `RATIFIED` / `CONTRACT_READY` are permitted only in a "
        "file that carries `ratification_ref: %s`, or anywhere under precode/ (the register and "
        "the ADRs are where the ratification is recorded). `CONTRACT_READY` is additionally "
        "confined to the four ratified scopes — a file outside them may not claim it however it "
        "is annotated — eligibility is the explicit allowlist in %s, so a file not named there is "
        "ineligible by default. Claims ABOVE CONTRACT_READY are forbidden THROUGHOUT THE SCANNED SCOPE "
        "(%s) with ONE narrowed exception (CR-P0-02): `IMPLEMENTATION_VERIFIED` — and nothing above "
        "it — is permitted inside the three places an evidence RECORD lives (%s) when the file CITES "
        "an A3 independent-audit report by name; contracts/, acceptance/ and precode/ are unchanged, "
        "and `INTEGRATION_VERIFIED` / `LIVE_FEASIBILITY_VERIFIED` / `PRODUCT_ACCEPTED` stay forbidden "
        "everywhere because no integration run, live probe or owner acceptance exists. "
        "`evidence/runs/**` is walked separately for this rule (it is excluded from `files_scanned` "
        "by F-A2R1-11, which is why F-A3R3-01 found the oracle describing a tree the loop never "
        "read) and is examined in STRUCTURED claim/status fields only, `supports_label` included. "
        "A record's `supports_label` inside an evidence tree is exempt from the ratified-vocabulary "
        "and four-scope legs (it says what a RUN supports, not what a FILE is) but NOT from the "
        "above-CONTRACT_READY cap. "
        "The citation is checked per FILE, not per record — see the notes below. Structured claim "
        "fields are read in `.yaml`/`.json` AND in Markdown front matter (F-A3R4-01). "
        "`agent-tasks/` is NOT scanned by this tool; the cards there use "
        "`claim_ceiling` with a different meaning (the ceiling the ordered work may reach) and "
        "are counted in a note below rather than silently omitted. "
        "`TBD` remains forbidden as a value, and `CLOSED` as a status."
        % (RATIFICATION_ID, RATIFIED_SCOPES_FILE, ", ".join(SCAN_DIRS),
           ", ".join(EVIDENCE_RECORD_LOCATIONS)),
    )
    status_keys = ("status", "claim_ceiling", "completion_claim", "coverage_status",
                   "evidence_status", "decision_status", "finding_status")
    ratified_words = {"ACCEPTED", "RATIFIED", "CONTRACT_READY"}

    _, _, allow_err = ratified_allowlist(repo)
    if allow_err:
        c.blocked("cannot read the ratified-scope allowlist: %s. This check refuses to run "
                  "rather than report a clean PASS on an unenforceable rule." % allow_err)
        return

    for rel in repo.files:
        if not in_scope_for_refs(rel):
            continue
        under_precode = rel.startswith("precode/")
        rat = ratification_ref_of(repo, rel)
        has_rat = (rat is not None and RATIFICATION_ID in str(rat))

        # A per-ITEM `status: ACCEPTED` is legitimate when the ratification reference sits on the
        # SAME node — that is better provenance than a file-level one, because it says which item
        # the Owner ratified. `CONTRACT_READY` is a claim the FILE makes about itself and keeps
        # the strict header-only rule below.
        ratified_nodes = set()
        if is_structured(rel):
            for path, val in structured_strings(repo, rel):
                if path.rsplit(".", 1)[-1].split("[")[0] == "ratification_ref" \
                        and RATIFICATION_ID in str(val):
                    ratified_nodes.add(path.rsplit(".", 1)[0])

        # F-A3R4-01: `.md` front matter is read here too, so the note's word "structured" is
        # true of every file type this loop touches instead of only two of them.
        if True:
            for path, val in claim_fields(repo, rel):
                leaf = path.rsplit(".", 1)[-1].split("[")[0]
                # `supports_label` is a manifest record's claim field. It is examined only where
                # records live, because that is the only place it means anything — and because
                # before PKT-PC09-P1-FIX1 it was examined NOWHERE, which is how six records could
                # carry IMPLEMENTATION_VERIFIED with no machine check on the label at all.
                keys = status_keys + (RECORD_CLAIM_KEYS if in_evidence_record_tree(rel) else ())
                if leaf not in keys:
                    continue
                node = path.rsplit(".", 1)[0]
                c.checked += 1
                v = val.strip()
                if v == "CLOSED":
                    c.fail(rel, "status value 'CLOSED' is forbidden; a finding is closed only by "
                                "the designated disposition authority (protocol §8)", at=path)
                if v == "TBD":
                    c.fail(rel, "value TBD is forbidden (baseline §3: no vagueness)", at=path)
                claim_label_violation(c, repo, rel, path, v)
                # A RECORD's `supports_label` says "this run supports a claim up to X". A
                # FILE's `claim_ceiling` says "this file IS X". The ratified-vocabulary and
                # four-scope rules police the second; applying them to the first conflates two
                # different assertions — and the manifest schema already caps a SELF_VALIDATION
                # record at exactly CONTRACT_READY, so the value is legitimate there by
                # construction. Found by this check itself when the Phase-3 workers became the
                # first to use that cap (PKT-PC09-P3). The cap that matters is untouched:
                # anything ABOVE CONTRACT_READY in these trees still goes through
                # `claim_label_violation` above, citation rule and all.
                record_label = (leaf in RECORD_CLAIM_KEYS
                                and in_evidence_record_tree(rel))
                if v in ratified_words and not record_label and not (
                        has_rat or under_precode or node in ratified_nodes):
                    c.fail(rel, "uses ratified vocabulary %r without `ratification_ref: %s`"
                           % (v, RATIFICATION_ID), at=path)
                if v == "CONTRACT_READY" and not under_precode and not record_label:
                    if not contract_ready_eligible(repo, rel):
                        c.fail(rel, "claims CONTRACT_READY but this file is outside the four "
                                    "scopes the Owner ratified (OD-20260907-01)", at=path)
                    elif not has_rat:
                        c.fail(rel, "claims CONTRACT_READY without a resolvable "
                                    "`ratification_ref`", at=path)

        txt = repo.text.get(rel, "")
        for label in CLAIM_LABELS_ABOVE_CONTRACT_READY:
            if phase1_label_allowed(repo, rel, label):
                continue
            if rel.startswith(DISPATCH_RECORD_PREFIXES):
                continue        # quotation in a dispatch record, not a claim; counted below
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
        for m in re.finditer(r"\bTBD\b", txt):
            start = txt.rfind("\n", 0, m.start()) + 1
            end = txt.find("\n", m.end())
            line = txt[start:end if end != -1 else len(txt)]
            c.checked += 1
            low = line.lower()
            if any(h in low for h in NEGATION_HINTS) or '"TBD"' in line or "`TBD`" in line:
                continue
            c.fail(rel, "bare TBD in text: %s" % line.strip()[:160])

    # Scope honesty (CR-PC09-14). This check's reach is SCAN_DIRS; `agent-tasks/` is outside it.
    # Rather than let the oracle sound wider than the measurement — the defect class every audit
    # finding in this package shared — measure the gap and report it as a note.
    cards_dir = os.path.join(repo.root, "agent-tasks")
    above = []
    if os.path.isdir(cards_dir):
        for fn in sorted(os.listdir(cards_dir)):
            if not fn.endswith(".md"):
                continue
            try:
                with open(os.path.join(cards_dir, fn), "r", encoding="utf-8") as fh:
                    head = fh.read(4000)
            except Exception:
                continue
            for ln in head.splitlines():
                if not ln.startswith("claim_ceiling:"):
                    continue
                val = ln.split(":", 1)[1].strip()
                for label in CLAIM_LABELS_ABOVE_CONTRACT_READY:
                    if val.startswith(label):
                        above.append("agent-tasks/%s -> %s" % (fn, label))
                        break
    # ---- F-A3R3-01: the tree the rule names but the scan never reached.
    # `Repo._scan` skips `evidence/runs/` so that `files_scanned` stays reproducible. The claim
    # rule still has to reach it, so it is walked here, structured fields only (see
    # `run_record_files`). These files are counted in this check's `items_checked` and named in a
    # note; they are NOT added to `files_scanned`.
    run_files = run_record_files(repo)
    run_fields_checked = 0
    for rel in run_files:
        try:
            with open(repo.abs(rel), "r", encoding="utf-8") as fh:
                txt_run = fh.read()
        except Exception as exc:
            c.fail(rel, "evidence/runs record is unreadable: %s" % exc)
            continue
        if not is_structured(rel):
            continue
        try:
            doc = json.loads(txt_run) if rel.endswith(".json") else yaml.safe_load(txt_run)
        except Exception as exc:
            c.fail(rel, "evidence/runs record does not parse: %s" % exc)
            continue
        # a local citation test: the run file itself, not repo.text (which has no entry for it)
        cited = bool(A3_REPORT_RE.search(txt_run))

        def walk(node, where="$"):
            global_hits = []
            if isinstance(node, dict):
                for k, val in node.items():
                    p = "%s.%s" % (where, k)
                    if isinstance(val, str) and k in (status_keys + RECORD_CLAIM_KEYS):
                        global_hits.append((p, val))
                    global_hits.extend(walk(val, p))
            elif isinstance(node, list):
                for i, val in enumerate(node):
                    global_hits.extend(walk(val, "%s[%d]" % (where, i)))
            return global_hits

        for path, val in walk(doc):
            run_fields_checked += 1
            c.checked += 1
            v = val.strip()
            if v == "CLOSED":
                c.fail(rel, "status value 'CLOSED' is forbidden (protocol §8)", at=path)
            if v == "TBD":
                c.fail(rel, "value TBD is forbidden (baseline §3)", at=path)
            if v in CLAIM_LABELS_ABOVE_CONTRACT_READY:
                if v == PHASE1_CLAIM_LABEL and cited:
                    continue
                if v == PHASE1_CLAIM_LABEL:
                    c.fail(rel, "claims %s but this run record cites no A3 report (CR-P0-02)" % v,
                           at=path)
                else:
                    c.fail(rel, "claims %s in a run record; CR-P0-02 opened the evidence trees "
                                "for %s ONLY, and no gate for %s is open"
                           % (v, PHASE1_CLAIM_LABEL, v), at=path)
    c.note("F-A3R3-01: `evidence/runs/` is excluded from `files_scanned` (F-A2R1-11) but is NOT "
           "excluded from this claim rule any more. %d run file(s) walked separately, %d "
           "structured claim/status field(s) examined in them. Structured fields ONLY: an E0 "
           "report is itself a run file and embeds this oracle, which names every forbidden "
           "label, so a prose sweep here would make the tool fail on its own output. The count "
           "of run files grows by one each closing run — that is why it is reported here and "
           "not folded into `files_scanned`."
           % (len(run_files), run_fields_checked))

    # CR-P0-02 exception accounting. A widened rule that nobody can see the reach of is a rule
    # nobody can review, so the files that USED the exception are named, not just permitted.
    used_exception = sorted(
        rel for rel in repo.files
        if in_evidence_record_tree(rel)
        and PHASE1_CLAIM_LABEL in repo.text.get(rel, "")
        and cites_a3_report(repo, rel))
    no_citation = sorted(
        rel for rel in repo.files
        if in_evidence_record_tree(rel)
        and PHASE1_CLAIM_LABEL in repo.text.get(rel, "")
        and not cites_a3_report(repo, rel))
    c.note("CR-P0-02 exception: %d file(s) under %s contain the token %s AND cite an A3 report, "
           "so the label is permitted there outright: %s. %d file(s) contain the token WITHOUT "
           "an A3 citation and stay under the ordinary rule — they pass today only because "
           "every occurrence in them is backticked, quoted or negated, and a bare assertion "
           "would FAIL: %s. The citation is checked per FILE, not per record; the per-record "
           "obligation is enforced by evidence/manifest.schema.json and by precode/review.md, "
           "not by this check."
           % (len(used_exception), ", ".join(EVIDENCE_RECORD_LOCATIONS), PHASE1_CLAIM_LABEL,
              ", ".join(used_exception) if used_exception else "none",
              len(no_citation), ", ".join(no_citation) if no_citation else "none"))
    quoted = {}
    for rel in repo.files:
        if not rel.startswith(DISPATCH_RECORD_PREFIXES):
            continue
        for label in CLAIM_LABELS_ABOVE_CONTRACT_READY:
            n = len(re.findall(r"\b%s\b" % label, repo.text.get(rel, "")))
            if n:
                quoted[label] = quoted.get(label, 0) + n
    c.note("dispatch records (%s) are exempt from the free-text claim sweep because a packet or "
           "ruling QUOTES the label it is dispatching about; their structured fields are still "
           "checked, and since F-A3R4-01 that includes MARKDOWN FRONT MATTER, not only "
           "`.yaml`/`.json` — the sentence used to promise a reach the loop did not have, which "
           "is the defect class of F-A3R3-01 repeated one level down. Occurrences skipped, "
           "counted rather than hidden: %s. What the exemption still cannot catch: a claim "
           "stated about ITSELF in the PROSE of one of these files. That residue is why the "
           "count is printed."
           % (", ".join(DISPATCH_RECORD_PREFIXES),
              ", ".join("%s×%d" % (k, v) for k, v in sorted(quoted.items())) or "none"))
    c.note("scan scope is %s; agent-tasks/ is NOT scanned. %d task card(s) there declare a "
           "claim_ceiling above CONTRACT_READY, which in a card denotes the ceiling of the "
           "work it orders, not a claim about the card: %s"
           % (", ".join(SCAN_DIRS), len(above), "; ".join(above) if above else "none"))


# --------------------------------------------------------------------------------------
# CHECK 12b — every CONTRACT_READY file's ratification_ref resolves to the Owner record
# --------------------------------------------------------------------------------------

def check_ratification_refs(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-12b-ratification-refs",
        "Every CONTRACT_READY file cites a ratification that resolves to the Owner's record",
        "A file whose claim_ceiling is CONTRACT_READY must carry `ratification_ref` naming %s IN ITS "
        "PARSED CONTRACT HEADER (front-matter, top-level key, or `x-contract`) — a prose mention "
        "does not count (F-A2R5-03 mutation M6b) — and %s must exist and contain that id. The "
        "eligible set is the explicit allowlist in %s. A ceiling raised on a citation that does "
        "not resolve, or on a sentence, is a claim with no authority behind it."
        % (RATIFICATION_ID, RATIFICATION_RECORD, RATIFIED_SCOPES_FILE),
    )
    _, _, allow_err = ratified_allowlist(repo)
    if allow_err:
        c.blocked("cannot read the ratified-scope allowlist: %s" % allow_err)
        return
    record = repo.text.get(RATIFICATION_RECORD)
    c.checked += 1
    if record is None:
        c.fail(RATIFICATION_RECORD, "the Owner decision record is absent, so no CONTRACT_READY "
                                    "citation in the corpus can resolve")
        return
    if RATIFICATION_ID not in record:
        c.fail(RATIFICATION_RECORD, "the record does not contain %s" % RATIFICATION_ID)

    for rel in repo.files:
        if not (rel.startswith(("contracts/", "acceptance/")) and in_scope_for_refs(rel)):
            continue
        claims = any(v.strip() == "CONTRACT_READY"
                     for p, v in structured_strings(repo, rel)
                     if p.rsplit(".", 1)[-1].split("[")[0] in ("claim_ceiling", "completion_claim"))
        if not claims and isinstance(repo.parsed.get(rel + "#frontmatter"), dict):
            claims = repo.parsed[rel + "#frontmatter"].get("claim_ceiling") == "CONTRACT_READY"
        if not claims:
            continue
        c.checked += 1
        rat = ratification_ref_of(repo, rel)
        if rat is None:
            c.fail(rel, "claims CONTRACT_READY but carries no `ratification_ref` in its parsed "
                        "contract header (a prose mention does not count)")
        elif RATIFICATION_ID not in str(rat):
            c.fail(rel, "claims CONTRACT_READY citing %r, which is not %s"
                   % (rat, RATIFICATION_ID))
        elif not contract_ready_eligible(repo, rel):
            c.fail(rel, "claims CONTRACT_READY inside a scope the Owner did not ratify")


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
        "declares an evidence level; and every scenario status is either NOT_RUN or one of "
        "`PASS (E1)` / `PASS (E2)` — the only two levels anything has actually been run at. A "
        "PASS status is only accepted when (i) the scenario's evidence_level_required is at or "
        "below the level claimed, (ii) `status_evidence_refs` is non-empty and every path in it "
        "exists on disk, and (iii) `status_scope_vi` says what the run did and did not "
        "establish. `PASS (E3)` / `PASS (E4)` are rejected outright: no live probe and no "
        "multi-period review has run. Before Phase 0/1 this leg read 'status must be NOT_RUN'; "
        "it is now a backing requirement rather than a ban, because four scenarios really were "
        "executed and reproduced by an independent auditor.",
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
        st = (s.get("status") or "").strip()
        if st != "NOT_RUN":
            m = SCENARIO_PASS_RE.fullmatch(st)
            if not m:
                c.fail("acceptance/scenarios.yaml",
                       "%s status %r is outside the vocabulary {NOT_RUN, 'PASS (E1)', "
                       "'PASS (E2)'}" % (sid, st))
            else:
                claimed = m.group(1)
                if not isinstance(lvl, str) or lvl > claimed:
                    c.fail("acceptance/scenarios.yaml",
                           "%s claims %s but evidence_level_required is %r — a scenario cannot "
                           "pass below the level it requires" % (sid, st, lvl))
                refs = s.get("status_evidence_refs") or []
                if not isinstance(refs, list) or not refs:
                    c.fail("acceptance/scenarios.yaml",
                           "%s claims %s with no status_evidence_refs" % (sid, st))
                else:
                    for ref in refs:
                        if not os.path.isfile(repo.abs(str(ref))):
                            c.fail("acceptance/scenarios.yaml",
                                   "%s status_evidence_refs path %r does not exist" % (sid, ref))
                if not str(s.get("status_scope_vi") or "").strip():
                    c.fail("acceptance/scenarios.yaml",
                           "%s claims %s without status_scope_vi" % (sid, st))
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

# --------------------------------------------------------------------------------------
# CHECK 18 — the ratified data.purge_all table sets say the same thing in every artefact
#
# F-A2R5-01 (MAJOR): the Owner's most consequential answer was applied in two contracts and left
# unapplied in six artefacts, one of them SC44 — the acceptance oracle that tests it. The corpus
# reported one decision as both ratified and pending. No check caught it because no check
# compared what the artefacts SAY about purge.
#
# This check does two things a reader cannot do reliably by eye:
#   (a) partition integrity — the three sets in entities.yaml must be pairwise disjoint and must
#       cover every entity exactly once. A table added later without being classified FAILS here
#       instead of quietly landing in "not asserted".
#   (b) cross-artefact agreement — any artefact that ENUMERATES a purge set (five or more entity
#       names inside one purge-context span) must produce a set equal to one of the three
#       authoritative sets, and no artefact in the purge conversation may still mark the scope
#       undecided except on a line that also names the ratification or the finding.
# --------------------------------------------------------------------------------------

PURGE_ARTEFACTS = (
    "contracts/data/entities.yaml",
    "contracts/ports.yaml",
    "contracts/http/openapi.yaml",
    "contracts/ops/secrets.md",
    "contracts/ops/backup-restore.md",
    "contracts/ui/screens.yaml",
    "acceptance/scenarios.yaml",
    "acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json",
    "acceptance/fixtures/recovery/README.md",
)
PURGE_UNDECIDED_MARKERS = ("OWNER_DECISION_REQUIRED", "PROV-PC00-01", "PROV-PC01-03")
PURGE_RESOLVED_CONTEXT = (RATIFICATION_ID, "F-A2R5-01", "PURGE-LIST", "Lịch sử", "lịch sử",
                          "trước ratification", "từng", "history", "no longer")


def purge_sets(repo: Repo):
    """(purged, retained, never_purged, error) from entities.yaml TXN-purge-all."""
    doc = repo.parsed.get("contracts/data/entities.yaml")
    if not isinstance(doc, dict):
        return None, None, None, "contracts/data/entities.yaml did not parse"
    tx = doc.get("transactions")
    node = None
    if isinstance(tx, list):
        for t in tx:
            if isinstance(t, dict) and "purge" in str(t.get("id", "")).lower():
                node = t
                break
    elif isinstance(tx, dict):
        node = tx.get("TXN-purge-all")
    tables = (node or {}).get("tables") if isinstance(node, dict) else None
    if not isinstance(tables, dict):
        return None, None, None, "TXN-purge-all carries no `tables` block"

    def grab(key):
        # The three lists are authored in three different shapes (a dict with `list`, a dict with
        # `tables`, a bare list of {table, why_vi}). Read the artefact as written rather than
        # forcing one shape: a checker that only understands one spelling of the same fact is how
        # the fact goes unchecked.
        v = tables.get(key)
        if isinstance(v, dict):
            v = v.get("list") or v.get("tables") or v.get("entities")
        if not isinstance(v, list):
            return None
        out = set()
        for x in v:
            if isinstance(x, dict):
                x = x.get("table") or x.get("name") or x.get("entity")
            if x is None:
                return None
            out.add(str(x).strip())
        return frozenset(out)

    p, r, n = grab("purged"), grab("retained_by_owner_decision"), grab("never_purged")
    if p is None or r is None or n is None:
        return None, None, None, "TXN-purge-all `tables` lacks one of the three lists"
    return p, r, n, None


# CR-PC02-25 leg (d)/(e): LITERAL count agreement.
#
# AMD-ENT-maintenance-01 moved the purge sets to 37/22/2 (61 entities) and nine artefacts were
# left asserting the old 21. E0-18 passed throughout, because legs (b)/(c) read markers and
# STRUCTURED lists only — by design (see the long comment in leg (b)). The gap was not prose
# enumerations; it was NUMBERS. A number is cheap to read and cannot be misread the way a
# paragraph can, so this leg reads numbers and nothing else, over a named artefact list.
PURGE_COUNT_ARTEFACTS = (
    "contracts/ports.yaml",
    "contracts/modules.yaml",
    "contracts/http/openapi.yaml",
    "contracts/ops/secrets.md",
    "contracts/ops/backup-restore.md",
    "contracts/ops/deployment.md",
    "contracts/ui/screens.yaml",
    "acceptance/scenarios.yaml",
    "acceptance/fixtures/recovery/README.md",
    "acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json",
)
# A bare "37 bảng" is only a purge claim if the purge conversation is nearby; without this the
# leg would read every table count in the corpus and go back to being noise.
PURGE_COUNT_CUES = ("purge", "xóa", "retain", "giữ lại", "giữ nguyên",
                    "never_purged", "tập bảng")
TABLE_COUNT_RE = re.compile(r"(?<![\d.])(\d{1,3})\s*(?:bảng|tables\b|table\b)")
ENTITY_COUNT_RE = re.compile(r"(?<![\d.])(\d{1,3})\s*(?:entity|entities|thực thể)\b", re.I)
# Role-tagged forms, `never` first so that "không bao giờ xóa 2" is read as one `never` claim
# and not additionally as a `purged` claim of 2 (it was, in the first draft).
PURGE_ROLE_PATTERNS = (
    ("never", re.compile(r"(?:không bao giờ xóa|never[ _-]?purged)\s*\**\s*(\d{1,3})", re.I)),
    ("never", re.compile(r"(\d{1,3})\s*(?:bảng|tables?)\s*\**\s*(?:không bao giờ|never)", re.I)),
    ("purged", re.compile(r"(?:bị\s+xóa|xóa|purge[ds]?)\s*\**\s*(\d{1,3})\s*\**\s*(?:bảng|tables?\b|,)", re.I)),
    ("purged", re.compile(r"(\d{1,3})\s*(?:bảng|tables?)\s*\**\s*(?:bị\s+xóa|được\s+xóa|purged)", re.I)),
    ("retained", re.compile(r"(?:giữ lại|giữ nguyên|giữ|retain(?:ed)?)\s*\**\s*(\d{1,3})\s*\**\s*(?:bảng|tables?\b|,)", re.I)),
    ("retained", re.compile(r"(\d{1,3})\s*(?:bảng|tables?)\s*\**\s*(?:retained|giữ lại|giữ nguyên)", re.I)),
)
PURGE_TRIPLE_RE = re.compile(
    r"xóa\s*\**\s*(\d{1,3})\s*\**\s*(?:bảng)?\s*\**\s*,\s*\**\s*giữ\s*\**\s*(\d{1,3})"
    r"\s*\**\s*(?:bảng)?\s*\**\s*,\s*\**\s*không bao giờ xóa\s*\**\s*(\d{1,3})", re.I)
# Structured keys whose VALUE is a purge-set size (int) or whose LENGTH is one (list/dict).
PURGE_COUNT_KEYS = {
    "purged_table_count": "purged", "retained_table_count": "retained",
    "never_purged_table_count": "never", "_purged_tables": "purged",
    "_retained_tables": "retained", "_never_purged_tables": "never",
    "purged_table_counts_after": "purged", "purged_tables": "purged",
    "retained_tables": "retained",
}


def purge_count_claims(text):
    """Yield (kind, role, value, snippet) for every LITERAL count assertion in `text`.

    Literal only: a number written next to `bảng`/`table(s)`/`entity`, next to one of the
    three role words, or inside the ratified `xóa A, giữ B, không bao giờ xóa C` triple.
    Prose ENUMERATIONS (runs of table names) are still NOT read here — that version produced
    ~20 false positives and was withdrawn; see evidence/tools/README.md §5g.
    """
    claimed = []

    def overlaps(a, b):
        return any(not (b <= s or a >= e) for s, e in claimed)

    for role, rx in PURGE_ROLE_PATTERNS:
        for m in rx.finditer(text):
            if overlaps(m.start(), m.end()):
                continue
            claimed.append((m.start(), m.end()))
            yield "role", role, int(m.group(1)), " ".join(m.group(0).split())
    for m in PURGE_TRIPLE_RE.finditer(text):
        for role, g in (("purged", 1), ("retained", 2), ("never", 3)):
            yield "triple", role, int(m.group(g)), " ".join(m.group(0).split())[:90]
    for rx, unit in ((TABLE_COUNT_RE, "bảng"), (ENTITY_COUNT_RE, "entity")):
        for m in rx.finditer(text):
            win = text[max(0, m.start() - 120):m.end() + 120].lower()
            if not any(k in win for k in PURGE_COUNT_CUES):
                continue
            yield ("magnitude" if unit != "entity" else "entity_total"), None, int(m.group(1)),                 " ".join(text[max(0, m.start() - 45):m.end() + 40].split())


def purge_count_keys(doc):
    """Yield (path, role, kind, value) for structured keys that carry a purge-set size."""
    def walk(node, path="$"):
        if isinstance(node, dict):
            for k, v in node.items():
                p = "%s.%s" % (path, k)
                role = PURGE_COUNT_KEYS.get(str(k))
                if role is not None:
                    if isinstance(v, (list, dict)):
                        yield p, role, "length", len(v)
                    elif isinstance(v, int) and not isinstance(v, bool):
                        yield p, role, "value", v
                yield from walk(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from walk(v, "%s[%d]" % (path, i))

    yield from walk(doc)


def structured_lists(repo: Repo, rel: str):
    """Yield (path, list) for every list value in a parsed structured document."""
    doc = repo.parsed.get(rel)

    def walk(node, path="$"):
        if isinstance(node, dict):
            for k, v in node.items():
                yield from walk(v, "%s.%s" % (path, k))
        elif isinstance(node, list):
            yield path, node
            for i, v in enumerate(node):
                yield from walk(v, "%s[%d]" % (path, i))

    if doc is not None:
        yield from walk(doc)


def check_purge_sets(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-18-purge-set-agreement",
        "The ratified data.purge_all sets partition the entities and every artefact agrees",
        "contracts/data/entities.yaml `TXN-purge-all.tables` is the authoritative enumeration "
        "(OD-20260907-01 item 24). The three sets must be pairwise disjoint and cover `entities` "
        "exactly. Any artefact that enumerates five or more entity names inside a purge-context "
        "span must yield a set EQUAL to one of the three. No artefact may still mark the purge "
        "scope undecided (OWNER_DECISION_REQUIRED / PROV-PC00-01 / PROV-PC01-03) except on a "
        "line that also names the ratification or the finding that closed it. Every "
        "LITERAL count assertion (“N bảng”, the xóa/giữ/không-bao-giờ triple, a "
        "*_table_count field) in the named artefact list must equal the size of the set it "
        "names; prose ENUMERATIONS are not compared (CR-PC02-25).",
    )
    purged, retained, never, err = purge_sets(repo)
    if err:
        c.blocked(err)
        return

    entities = set(idx.entities) if getattr(idx, "entities", None) else set()
    if not entities:
        doc = repo.parsed.get("contracts/data/entities.yaml") or {}
        ents = doc.get("entities")
        if isinstance(ents, list):
            entities = {str(e.get("name") or e.get("id")) for e in ents if isinstance(e, dict)}
        elif isinstance(ents, dict):
            entities = set(ents)

    # (a) partition integrity
    c.checked += 1
    for a, b, an, bn in ((purged, retained, "purged", "retained_by_owner_decision"),
                         (purged, never, "purged", "never_purged"),
                         (retained, never, "retained_by_owner_decision", "never_purged")):
        both = sorted(a & b)
        if both:
            c.fail("contracts/data/entities.yaml",
                   "tables appear in both %s and %s: %s" % (an, bn, ", ".join(both)))
    union = purged | retained | never
    if entities:
        c.checked += 1
        missing = sorted(entities - union)
        extra = sorted(union - entities)
        if missing:
            c.fail("contracts/data/entities.yaml",
                   "entities never classified by TXN-purge-all (they would be silently "
                   "unasserted by every purge oracle): %s" % ", ".join(missing))
        if extra:
            c.fail("contracts/data/entities.yaml",
                   "TXN-purge-all names tables that are not entities: %s" % ", ".join(extra))
    c.note("authoritative sets: purged %d · retained %d · never_purged %d · union %d of %d "
           "entities" % (len(purged), len(retained), len(never), len(union), len(entities)))

    # (b) no artefact may still call the purge scope undecided
    #
    # Deliberately NOT done here: comparing prose enumerations set-for-set. I wrote that version
    # first and it produced 24 violations of which ~20 were false — any paragraph mentioning
    # "purge" near five entity names tripped it, and entities.yaml trips it by existing. A noisy
    # check is worse than no check: it teaches its readers to skip the output. What is left is
    # crisp and is what would actually have caught F-A2R5-01 — every one of the six stale
    # artefacts carried an undecided marker. Prose enumerations remain unverified, and that
    # limitation is written down in evidence/tools/README.md §5g rather than implied by a PASS.
    for rel in PURGE_ARTEFACTS:
        txt = repo.text.get(rel)
        if txt is None:
            c.fail(rel, "artefact named in the purge conversation is absent from the corpus")
            continue
        blocks = re.split(r"\n\s*\n", txt)
        for block in blocks:
            if "purge" not in block.lower():
                continue          # markers elsewhere in the file are other decisions, not this one
            blines = block.splitlines()
            for i, line in enumerate(blines):
                for marker in PURGE_UNDECIDED_MARKERS:
                    if marker not in line:
                        continue
                    c.checked += 1
                    # A folded YAML sentence is split by the author's line width, not by meaning,
                    # so the history qualifier can land on the neighbouring line. Widen to ±1
                    # line — enough for folding, far too narrow to let a stale marker inherit a
                    # ratification mentioned elsewhere in the same block.
                    window = " ".join(blines[max(0, i - 1):i + 2])
                    if any(h in window for h in PURGE_RESOLVED_CONTEXT):
                        continue
                    c.fail(rel, "calls the purge scope undecided (%s) on a line that does not "
                                "mark it as history or name the ratification that closed it: %s"
                           % (marker, line.strip()[:130]))

    # (c) a STRUCTURED purge list anywhere else must equal the authority
    for rel in PURGE_ARTEFACTS:
        if rel == "contracts/data/entities.yaml" or not is_structured(rel):
            continue
        for path, val in structured_lists(repo, rel):
            leaf = path.rsplit(".", 1)[-1].split("[")[0].lower()
            if leaf not in ("purged", "retained_by_owner_decision", "never_purged",
                            "purged_tables", "retained_tables"):
                continue
            names = set()
            for x in val:
                if isinstance(x, dict):
                    x = x.get("table") or x.get("name") or x.get("entity")
                if isinstance(x, str):
                    names.add(x.strip())
            if not names:
                continue
            c.checked += 1
            target = purged if leaf.startswith("purged") else (
                never if leaf == "never_purged" else retained)
            if names != set(target):
                c.fail(rel, "a structured purge list at %s differs from the authoritative set: %s"
                       % (path, ", ".join(sorted(names ^ set(target)))[:200]))

    # (d)/(e) CR-PC02-25: literal COUNT agreement over the named artefact list.
    #
    # W3n's AMD-ENT-maintenance-01 moved the sets to 37/22/2 and nine artefacts kept asserting
    # 21; grep found them, this check did not. Numbers are read three ways, all literal:
    #   role      "22 bảng giữ lại" / "không bao giờ xóa 2"  -> must equal that set's size
    #   triple    "xóa 37, giữ 22, không bao giờ xóa 2"      -> must equal all three
    #   magnitude any "N bảng" near a purge cue              -> must be one of {37,22,2,61}
    #   entity    any "N entity" near a purge cue            -> must be the union size
    # The magnitude rule is the loose one on purpose: it cannot tell a swapped pair apart, but
    # it catches every arithmetic that is simply out of date, with no window guessing.
    auth = {"purged": len(purged), "retained": len(retained), "never": len(never)}
    total = len(union)
    legal = set(auth.values()) | {total}
    seen_counts = 0
    silent = []
    for rel in PURGE_COUNT_ARTEFACTS:
        txt = repo.text.get(rel)
        if txt is None:
            c.fail(rel, "artefact named in the purge count list is absent from the corpus")
            continue
        before = seen_counts
        for kind, role, n, snip in purge_count_claims(txt):
            c.checked += 1
            seen_counts += 1
            if kind in ("role", "triple"):
                if n != auth[role]:
                    c.fail(rel, "states the %s set as %d; contracts/data/entities.yaml "
                                "TXN-purge-all says %d: %s" % (role, n, auth[role], snip[:120]))
            elif kind == "entity_total":
                if n != total:
                    c.fail(rel, "states the purge scope as %d entities; the three sets cover "
                                "%d: %s" % (n, total, snip[:120]))
            elif n not in legal:
                c.fail(rel, "a table count of %d appears in a purge context; the only "
                            "authoritative sizes are %s: %s"
                       % (n, "/".join(str(x) for x in sorted(legal)), snip[:120]))
        if seen_counts == before:
            silent.append(rel)
        doc = repo.parsed.get(rel)
        if doc is not None:
            for path, role, kind, val in purge_count_keys(doc):
                c.checked += 1
                seen_counts += 1
                if val != auth[role]:
                    c.fail(rel, "%s at %s is %d; the %s set has %d members"
                           % ("the length of the list" if kind == "length" else "the count",
                              path, val, role, auth[role]))
    c.note("CR-PC02-25 count leg: %d literal count assertion(s) read across %d named artefact(s) "
           "and compared to purged %d / retained %d / never %d / union %d.%s"
           % (seen_counts, len(PURGE_COUNT_ARTEFACTS), auth["purged"], auth["retained"],
              auth["never"], total,
              (" %d artefact(s) state no count at all and are therefore unconstrained by this "
               "leg: %s." % (len(silent), ", ".join(silent))) if silent else ""))
    c.note("NOT compared by E0-18, and this is deliberate (README §5g): PROSE ENUMERATIONS — a "
           "paragraph or table that lists entity names one by one is never read as a purge set. "
           "The set-comparison version of that rule produced 24 violations of which ~20 were "
           "false. So a stale artefact that spells out the wrong 21 NAMES without writing a "
           "number is still invisible to this check; only structured lists (leg c) and literal "
           "numbers (leg d/e) are verified.")


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
# CHECK 19 — generated code still matches the contracts it was generated from
#
# ADR-0011 has a "generate, don't hand-edit" rule, and until now it was carried entirely by
# `pytest` / `vitest` (`shared/rr_contracts/tests/test_generated_matches_contracts.py` and
# `web/scripts/generate.mjs --check`). Those gates run the generators; this one does not run
# anything. It reads the two `GENERATED_FROM.json` manifests as DECLARATIONS and asks the only
# question a static check can answer honestly: are the source hashes the generated tree claims
# to have been built from still the hashes on disk?
#
# What this proves: a contract cannot be edited without either regenerating or leaving a visible
# mismatch here. What it does NOT prove: that the generator output is correct, or that a
# generated file was not hand-edited — a hand-edited output leaves these source hashes intact,
# and only re-running the generator catches it. That is why this check ADDS to the pytest/vitest
# gates and does not replace them.
#
# CR-P0-06 / F-A3R2-04: `contracts/data/entities.yaml` is deliberately NOT a generator source.
# The database shape reaches code by hand — the Alembic revisions and
# `tests/contract/test_schema_matches_entities.py` — and that pair is checked by pytest, not
# here. This check states that absence out loud so nobody reads a clean E0-19 as "the schema
# tracks entities.yaml automatically". It does not.
# --------------------------------------------------------------------------------------

GENERATED_FROM_MANIFESTS = (
    "shared/rr_contracts/rr_contracts/generated/GENERATED_FROM.json",
    "web/src/generated/GENERATED_FROM.json",
)
# The contract whose absence from every manifest is intentional, not an oversight.
NOT_A_GENERATOR_SOURCE = "contracts/data/entities.yaml"


def check_generated_matches(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-19-generated-matches",
        "Every GENERATED_FROM.json source hash equals the contract on disk today",
        "For each manifest in %s: the file parses, declares `generator` and a non-empty "
        "`sources` list, and every `sources[].path` exists with `sha256` equal to the file's "
        "current SHA-256 (and `bytes`, when declared, equal to its size). A mismatch means the "
        "contract moved without the generated tree being rebuilt — the 'generate, don't "
        "hand-edit' rule of ADR-0011 as a static check. It does NOT prove the generated output "
        "is correct or unedited: only re-running the generator (pytest "
        "`shared/rr_contracts/tests/test_generated_matches_contracts.py`, vitest / "
        "`node web/scripts/generate.mjs --check`) proves that, and those gates stay. "
        "`%s` is intentionally absent from both manifests (CR-P0-06, F-A3R2-04): the database "
        "shape is hand-written in the Alembic revisions and is checked by the pytest gate "
        "`tests/contract/test_schema_matches_entities.py`, which is a test, not an E0 check."
        % (", ".join(GENERATED_FROM_MANIFESTS), NOT_A_GENERATOR_SOURCE),
    )
    seen_sources = set()
    for rel in GENERATED_FROM_MANIFESTS:
        c.checked += 1
        path = repo.abs(rel)
        if not os.path.isfile(path):
            c.fail(rel, "GENERATED_FROM manifest is absent; the generated tree declares no "
                        "provenance and this check cannot verify it")
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception as exc:
            c.fail(rel, "GENERATED_FROM manifest does not parse: %s" % exc)
            continue
        if not str(doc.get("generator") or "").strip():
            c.fail(rel, "manifest declares no `generator`")
        sources = doc.get("sources")
        if not isinstance(sources, list) or not sources:
            c.fail(rel, "manifest declares no `sources`; a provenance record with no sources "
                        "asserts nothing and would pass this check vacuously")
            continue
        for entry in sources:
            c.checked += 1
            if not isinstance(entry, dict):
                c.fail(rel, "sources entry is not an object: %r" % (entry,))
                continue
            src = str(entry.get("path") or "")
            declared = str(entry.get("sha256") or "")
            if not src or not declared:
                c.fail(rel, "sources entry missing path or sha256: %r" % (entry,))
                continue
            seen_sources.add(src)
            spath = repo.abs(src)
            if not os.path.isfile(spath):
                c.fail(rel, "declared source %s does not exist" % src)
                continue
            actual = sha256_file(spath)
            if actual != declared:
                c.fail(rel, "%s changed since the tree was generated: manifest says %s, disk is "
                            "%s. Regenerate (or the generated tree is stale)."
                       % (src, declared[:16] + "…", actual[:16] + "…"))
                continue
            size = entry.get("bytes")
            if isinstance(size, int) and size != os.path.getsize(spath):
                c.fail(rel, "%s size %d != declared %d (hash matched: declaration is "
                            "internally inconsistent)" % (src, os.path.getsize(spath), size))
    c.note("%s appears in %d of the %d manifests. Absence is INTENTIONAL (CR-P0-06, "
           "F-A3R2-04): the generated trees do not track it, so a change to it is caught by "
           "the Alembic revisions plus tests/contract/test_schema_matches_entities.py under "
           "pytest — the schema gate lives in pytest, not in E0."
           % (NOT_A_GENERATOR_SOURCE,
              1 if NOT_A_GENERATOR_SOURCE in seen_sources else 0,
              len(GENERATED_FROM_MANIFESTS)))
    if NOT_A_GENERATOR_SOURCE in seen_sources:
        c.note("%s is NOW a declared generator source; the note above and CR-P0-06 are stale "
               "and must be rewritten." % NOT_A_GENERATOR_SOURCE)


# --------------------------------------------------------------------------------------
# CHECK 20 — every §2 fixture of an IMPLEMENTED card is accounted for
#
# Third recurrence of one defect class: `F-A3R1-09` (Phase 1), `F-A3-P2-01` (Phase 2) and
# `F-A3-P3-03` (Phase 3) are all "a card's read-set fixture is neither exercised by a test nor
# recorded NOT_RUN". Three rounds of an auditor finding the same shape by hand is the signal
# that it should stop being a per-round finding and become a standing check (Coordinator ruling,
# post-A3-P3-R1 fix wave).
#
# The rule, stated so it can be argued with:
#   * A card is IMPLEMENTED when `evidence/runs/<card>-E1-*.json` exists. Cards nobody has built
#     yet are out of scope — their fixtures cannot be exercised and saying so every run would be
#     noise, not signal.
#   * For an implemented card, every `acceptance/fixtures/**.json` path named in its `§2. Read
#     set` must be EITHER referenced by some file under `tests/`, OR named in that card's handoff
#     in a paragraph that also says `NOT_RUN`.
#   * READMEs are excluded: a directory README is documentation, not an oracle.
#
# What this proves: no fixture a card was told to read disappears silently. What it does NOT
# prove: that the test which references a fixture actually asserts anything with it. A reference
# is presence, not coverage — that judgement stays with the reviewer, and this check says so
# rather than letting a clean run be read as "every fixture is covered".
# --------------------------------------------------------------------------------------

CARD_DIR = "agent-tasks"
FIXTURE_IN_PROSE = re.compile(r"acceptance/fixtures/[A-Za-z0-9_./-]+\.json")


def card_read_set_fixtures(repo: Repo, card_path: str) -> "list[str]":
    """Fixture paths named in a card's `§2. Read set`, READMEs excluded."""
    try:
        with open(card_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except Exception:
        return []
    m = re.search(r"^##\s*§2\..*?$(.*?)^##\s*§3\.", text, re.S | re.M)
    if not m:
        return []
    return sorted({p for p in FIXTURE_IN_PROSE.findall(m.group(1))
                   if not p.endswith("README.md")})


def paragraphs_naming(text: str, needle: str) -> "list[str]":
    """Blank-line-separated blocks of `text` that mention `needle`."""
    return [b for b in re.split(r"\n\s*\n", text) if needle in b]


def check_card_fixture_accounting(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-20-card-fixture-accounting",
        "Every §2 fixture of an implemented card is exercised by a test or recorded NOT_RUN",
        "A card counts as IMPLEMENTED when `evidence/runs/<card>-E1-*.json` exists. For each such "
        "card, every `acceptance/fixtures/**.json` named in its `§2. Read set` (READMEs excluded) "
        "must be EITHER referenced by a file under any TEST tree — `tests/`, `web/tests/`, or a "
        "co-located `*.test.*` / `*.spec.*` under `web/src/` (CR-TC-uiruns-08: walking only the "
        "Python tree made every UI card unpassable) — OR named in "
        "`evidence/handoffs/<card>-handoff.md` in a paragraph that also contains `NOT_RUN`. "
        "Silence is the defect this catches, not absence of coverage: `F-A3R1-09`, `F-A3-P2-01` "
        "and `F-A3-P3-03` are the same finding three rounds running, which is why it is now a "
        "check instead of a reviewer's memory. A reference is PRESENCE, not coverage — this "
        "check cannot tell whether the test that names a fixture asserts anything with it, and a "
        "clean result must not be read as 'every fixture is covered'.",
    )
    cards_dir = os.path.join(repo.root, CARD_DIR)
    runs_dir = os.path.join(repo.root, "evidence", "runs")
    if not os.path.isdir(cards_dir) or not os.path.isdir(runs_dir):
        c.blocked("agent-tasks/ or evidence/runs/ is absent; the check refuses to report a clean "
                  "PASS on a subject it cannot see")
        return

    runs = os.listdir(runs_dir)
    # Every text file under any TEST tree, read once.
    #
    # CR-TC-uiruns-08: this walked only the Python `tests/` tree, so a UI card's fixture — loaded
    # by name in Vitest under `web/tests/` — was invisible and the card could never pass. The
    # check was measuring "referenced by a PYTHON test" while its oracle said "referenced by a
    # test", which is the same class of defect (`F-A3R3-01`, `F-A3R4-01`) this file has now been
    # caught by three times: a stated reach wider than the actual one. The walk follows the
    # oracle instead of the other way round.
    test_blob = []
    test_roots = [os.path.join(repo.root, "tests"),
                  os.path.join(repo.root, "web", "tests"),
                  os.path.join(repo.root, "web", "src")]
    for root in test_roots:
        if not os.path.isdir(root):
            continue
        in_src = root.endswith(os.path.join("web", "src"))
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in ("__pycache__", ".pytest_cache", "node_modules",
                                        "generated", "dist", "build")]
            for fn in filenames:
                if fn.endswith((".pyc", ".json")):
                    continue
                # Under `web/src/` only co-located test files count: shipping code that merely
                # mentions a fixture path is not a test exercising it.
                if in_src and ".test." not in fn and ".spec." not in fn:
                    continue
                try:
                    with open(os.path.join(dirpath, fn), "r", encoding="utf-8") as fh:
                        test_blob.append(fh.read())
                except Exception:
                    continue
    tests_text = "\n".join(test_blob)

    implemented, skipped = [], []
    for fn in sorted(os.listdir(cards_dir)):
        if not (fn.startswith("TC-") and fn.endswith(".md")):
            continue
        card = fn[:-3]
        if not any(r.startswith(card + "-E1-") and r.endswith(".json") for r in runs):
            skipped.append(card)
            continue
        implemented.append(card)
        handoff = os.path.join(repo.root, "evidence", "handoffs", card + "-handoff.md")
        try:
            with open(handoff, "r", encoding="utf-8") as fh:
                handoff_text = fh.read()
        except Exception:
            handoff_text = ""
            c.fail("agent-tasks/%s" % fn,
                   "card is implemented but %s is unreadable, so no fixture of it can be "
                   "accounted for" % os.path.relpath(handoff, repo.root))
        for fixture in card_read_set_fixtures(repo, os.path.join(cards_dir, fn)):
            c.checked += 1
            base = os.path.basename(fixture)[:-5]
            if fixture in tests_text or base in tests_text:
                continue
            blocks = paragraphs_naming(handoff_text, fixture) or \
                paragraphs_naming(handoff_text, base)
            if any("NOT_RUN" in b for b in blocks):
                continue
            if blocks:
                c.fail("agent-tasks/%s" % fn,
                       "§2 fixture %s is named in the handoff but not as NOT_RUN, and no test "
                       "references it: a mention is not a disposition" % fixture)
            else:
                c.fail("agent-tasks/%s" % fn,
                       "§2 fixture %s is referenced by no test and named nowhere in the card's "
                       "handoff — the silence F-A3R1-09 / F-A3-P2-01 / F-A3-P3-03 each caught "
                       "by hand" % fixture)
    c.note("test trees walked: %s (existing ones only). %d card(s) implemented and checked: %s. "
           "%d card(s) not implemented and therefore out of scope: %s."
           % (", ".join(os.path.relpath(r, repo.root) for r in test_roots
                         if os.path.isdir(r)),
              len(implemented), ", ".join(implemented) or "none",
              len(skipped), ", ".join(skipped) or "none"))

# --------------------------------------------------------------------------------------
# CHECK 21 — no xfail/skip reason rests on a premise that is no longer true
#
# Fourth recurrence of one class: `F-A3R3-03`, `F-A3-P2-01`, `F-A3-P3-02` and now `F-A3-P4-03`
# are all "a marker's REASON says something is absent, and it is not absent any more". The
# marker itself is honest — `strict=True` means the test really does still fail — but the
# sentence explaining why has rotted, and a reader trusts the sentence.
#
# What is flagged: a reason that asserts an ABSENCE (`pending`, `not yet`, `chưa`, `absent`,
# `no implementation`, `needs the`, `does not exist`, …) about a subject that now EXISTS —
# either a `TC-…` card whose handoff is on disk, or a table the migrations create.
#
# Why absence markers rather than "names a card/table at all": a marker whose reason describes a
# real DEFECT (`CR-TC-BACKFILL-09`, a fixture that disagrees with a contract) legitimately names
# tables and cards that exist. Flagging those would train people to delete accurate reasons.
# The cost of that choice is stated rather than hidden: a rotted reason phrased WITHOUT any of
# these markers slips through, and the note prints the marker list so the gap is inspectable.
# --------------------------------------------------------------------------------------

ABSENCE_MARKERS = (
    "pending", "not yet", "no implementation", "not wired", "needs the", "needs a",
    "does not exist", "doesn't exist", "absent", "not in phase", "not in m1", "is missing",
    "chưa", "không tồn tại", "vắng mặt",
)
XFAIL_RE = re.compile(r"xfail\(")
STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"' r"|'([^'\\]*(?:\\.[^'\\]*)*)'")
CARD_RE = re.compile(r"\bTC-[a-z0-9-]+\b", re.I)
VITEST_SKIP_RE = re.compile(r"\b(?:it|test|describe)\.(?:skip|todo)\s*\(")


def migration_tables(repo: Repo) -> "set[str]":
    """Table names the Alembic revisions create, read statically from the revision files."""
    out = set()
    base = os.path.join(repo.root, "server", "migrations", "versions")
    if not os.path.isdir(base):
        return out
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".py"):
            continue
        try:
            with open(os.path.join(base, fn), "r", encoding="utf-8") as fh:
                body = fh.read()
        except Exception:
            continue
        out |= {m.lower() for m in re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?([a-z_]+)", body, re.I)}
        out |= {m.lower() for m in re.findall(r'op\.create_table\(\s*"([a-z_]+)"', body)}
    return out


def marker_reasons(text: str, python: bool) -> "list[str]":
    r"""Reason strings of every `xfail(...)` in `text`.

    F-A3-P4R2-01: the first version matched the argument list with a regex terminated by
    `\)\s*$` or `\n\s*\)`. Under `re.S`, `$` is end-of-STRING, so neither alternative can fire
    for the one-line form `xfail(reason="…")` — the closing paren sits mid-file on the same
    line. A textbook stale reason written that way was skipped **entirely**, and the check
    reported a smaller `items_checked` rather than a violation, which is the quiet failure mode
    this file keeps warning about. A test module is valid Python, so it is now parsed with `ast`
    and the keyword read directly; implicit string concatenation arrives already folded into one
    `Constant`. The regex survives only as a fallback for files that do not parse, and it now
    terminates on a bare `)` as well.
    """
    out, unreadable = [], []
    if python:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func
                dotted = []
                while isinstance(name, ast.Attribute):
                    dotted.append(name.attr)
                    name = name.value
                if isinstance(name, ast.Name):
                    dotted.append(name.id)
                if "xfail" not in dotted and "skip" not in dotted:
                    continue
                kws = [kw for kw in node.keywords if kw.arg == "reason"]
                if not kws:
                    unreadable.append("no reason= keyword")
                for kw in kws:
                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        out.append(kw.value.value)
                    else:
                        # An f-string or a variable: this check cannot read it, and saying so is
                        # the difference between "clean" and "not looked at".
                        unreadable.append("reason is not a string literal")
            return out, unreadable
    for m in XFAIL_RE.finditer(text):
        seg = text[m.start():m.start() + 900]
        r = re.search(r"reason\s*=\s*(.*?)(?:,\s*\w+\s*=|\s*\))", seg, re.S)
        if not r:
            continue
        parts = [a or b for a, b in STRING_RE.findall(r.group(1))]
        if parts:
            out.append(" ".join(parts))
    return out, unreadable


def check_marker_reasons(repo: Repo, idx: Index) -> None:
    c = new_check(
        "E0-21-marker-reason-freshness",
        "No xfail/skip reason rests on a premise the tree has since falsified",
        "For every `pytest.mark.xfail(reason=…)` under any test tree, and every Vitest "
        "`it/test/describe.skip|todo`: if the reason asserts an ABSENCE (%s) about a `TC-…` card "
        "whose handoff exists on disk, or about a table the Alembic revisions create, the reason "
        "is STALE and is reported. A table matches only when the reason writes it as a backticked name on its own (`report`), never as a bare word inside a path such as `contracts/telegram/delivery.md`.  The marker may still be correct — `strict=True` means the "
        "test does still fail — but the sentence explaining why is not, and a reader trusts the "
        "sentence. Fourth recurrence of this class (`F-A3R3-03`, `F-A3-P2-01`, `F-A3-P3-02`, "
        "`F-A3-P4-03`), which is why it is a check now. What it deliberately does NOT flag: a "
        "reason describing a real DEFECT, which legitimately names cards and tables that exist "
        "— flagging those would train people to delete accurate reasons. The cost: a rotted "
        "reason phrased without any absence marker slips through."
        % ", ".join("`%s`" % m for m in ABSENCE_MARKERS[:6]),
    )
    tables = migration_tables(repo)
    handoffs = set()
    hdir = os.path.join(repo.root, "evidence", "handoffs")
    if os.path.isdir(hdir):
        handoffs = {fn[:-len("-handoff.md")].lower()
                    for fn in os.listdir(hdir) if fn.endswith("-handoff.md")}

    roots = [os.path.join(repo.root, "tests"), os.path.join(repo.root, "web", "tests"),
             os.path.join(repo.root, "web", "src"), os.path.join(repo.root, "server", "tests")]
    examined = vitest_seen = 0
    unreadable_total = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in ("__pycache__", ".pytest_cache", "node_modules")]
            for fn in sorted(filenames):
                if not fn.endswith((".py", ".ts", ".tsx", ".js")):
                    continue
                rel = repo.rel(os.path.join(dirpath, fn))
                try:
                    with open(os.path.join(dirpath, fn), "r", encoding="utf-8") as fh:
                        body = fh.read()
                except Exception:
                    continue
                vitest_seen += len(VITEST_SKIP_RE.findall(body))
                reasons, unreadable = marker_reasons(body, python=fn.endswith(".py"))
                for why in unreadable:
                    unreadable_total.append("%s (%s)" % (rel, why))
                # A Vitest skip/todo carries no reason= kwarg; its nearest string is the title.
                for m in VITEST_SKIP_RE.finditer(body):
                    seg = body[m.end():m.end() + 400]
                    parts = [a or b for a, b in STRING_RE.findall(seg)][:1]
                    if parts:
                        reasons.append(parts[0])
                for reason in reasons:
                    examined += 1
                    c.checked += 1
                    low = reason.lower()
                    if not any(mk in low for mk in ABSENCE_MARKERS):
                        continue
                    for card in {m.lower() for m in CARD_RE.findall(reason)}:
                        if card in handoffs:
                            c.fail(rel, "marker reason asserts %s is absent, but "
                                        "evidence/handoffs/%s-handoff.md exists — the card "
                                        "landed and the reason has rotted: %s"
                                   % (card, card, reason[:180]))
                    # A table name counts only when the reason writes it AS a table: the whole
                    # backticked span equals the name. Matching bare words made
                    # `contracts/telegram/delivery.md` look like the `delivery` table and
                    # produced a false positive on a reason whose premise is still true. A check
                    # that cries wolf teaches people to ignore it, so the match is exact.
                    for span in {s.strip().lower() for s in re.findall(r"`([^`]+)`", reason)}:
                        if span in tables:
                            c.fail(rel, "marker reason asserts table `%s` is absent, but the "
                                        "migrations create it: %s" % (span, reason[:180]))
    if unreadable_total:
        c.note("%d marker(s) carry no readable literal reason and were NOT examined: %s. This is "
               "a gap in the check, not a clean result for those markers."
               % (len(unreadable_total), "; ".join(sorted(set(unreadable_total)))))
    c.note("examined %d marker reason(s) across tests/, web/tests/, web/src/ and server/tests/; "
           "%d Vitest skip/todo marker(s) found (a Vitest marker has no `reason=`, so its TITLE "
           "is read instead — weaker, and said so). %d table name(s) known from the migrations, "
           "%d card handoff(s) on disk. Absence markers used: %s."
           % (examined, vitest_seen, len(tables), len(handoffs),
              ", ".join(ABSENCE_MARKERS)))


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
    check_ratification_refs(repo, idx)
    check_coverage_windows(repo, idx)
    check_fixture_actor_edge(repo, idx)
    check_fixture_fields(repo, idx)
    check_scenarios(repo, idx)
    check_purge_sets(repo, idx)
    check_declared_deviations(repo, idx)
    check_generated_matches(repo, idx)
    check_card_fixture_accounting(repo, idx)
    check_marker_reasons(repo, idx)

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
