#!/usr/bin/env python3
"""Card pin verifier — the executable form of PC10's EV-PC10-01.

PC10 verified the 18 task cards with a throw-away script in a scratch directory
(`evidence/handoffs/PC10-handoff.md`, EV-PC10-01/EV-PC10-02). That script is gone, so the
one gate that keeps a card from silently going stale existed only as a claim in a handoff.
This file is that gate, checked in and runnable in CI.

What it checks
--------------
The oracle is EV-PC10-01's (a)-(m) in full. Until PKT-PC10-FIX16 this port ran only (a)-(g)
plus (m) and a card-consensus-only form of (k); `CR-PC10-10` recorded that gap, because the
generator that held the other five checks lives in a scratch directory and disappears with
it. Nothing here is weaker than the original:

``pins``       (a) every pinned sha256 recomputed from the file on disk matches, and the
                   byte count matches too.
``epoch``      (k) every card declares the same pin epoch, AND every file that asserts a
                   *current* pin — `precode/README.md`, `agent-tasks/README.md`,
                   `TEMPLATE.md`, `WALKTHROUGH.md` — names exactly that epoch, with older
                   epochs allowed only in a paragraph that also carries a supersession
                   marker. §0: "Card là nguồn chuẩn của tên epoch"; two cards on different
                   epochs means one of them was re-pinned alone, and an entry-point file
                   left on a superseded epoch sends a reader to check the wrong bytes
                   (finding `F-A2R1-03`, and again in PKT-PC10-FIX14 §N.3).
``paths``      (b) every repository path a card cites inside `contracts/`, `acceptance/`,
                   `precode/`, `agent-tasks/` or `evidence/` exists on disk. Paths under
                   the seven implementation trees are the card's *write set* — they are
                   allowed not to exist yet, and are checked by ``layout`` instead.
``operations`` (c) every operation id in a card's §4 Produces/Consumes list exists in
                   `contracts/ports.yaml`.
``scenarios``  (d) every `SC..` id resolves in `acceptance/scenarios.yaml`.
``errors``     (e) every SCREAMING_SNAKE token in §7 is a code registered in
                   `contracts/errors.yaml` (or a listed status word).
``modules``    (f) every `MOD-*` exists in `contracts/modules.yaml`.
``invariants`` (g) every `I<nn>` is in the range the invariant register defines.
``obligations``(h) FIX5's floor on every card: `SC49` (the 36-edge default-deny sweep), the
                   R5-01 boundary table in §5 naming `UNAUTHORIZED`, `FORBIDDEN_EDGE`,
                   `CAPABILITY_DENIED` and `CSRF_REJECTED`, and the boundary fixture.
                   Returning the wrong code is a FAIL too, so the codes must be written down.
``claim_labels``(i) a card may only use the claim labels of SRC-PLAN §2. A new label
                   invented in a card is a claim nobody defined the evidence bar for.
``pc09_unpinned``(j) the six PC09 files plus `e0_check.py` must NOT be pinned by hash in §0
                   (Coordinator ruling on `CR-PC10-01`): they are cited by path + SC id.
                   Pinning them would make every card STALE on a PC09 edit that the cards
                   were told to read live.
``stack``      (l) no card presents Stack A as the chosen stack. Owner chose Option B
                   (`OD-20260907-01`); historical narrative is allowed only in a paragraph
                   that marks it superseded, and every card must name the accepted stack
                   and cite the ratification.
``layout``     (m) the two-language rule of `agent-tasks/README.md` §5.3: no `.py` under
                   `web/`, no `.ts`/`.tsx` under `server/`, `collector/`, `worker/`,
                   `probe/` — checked BOTH against the paths cards write down AND against
                   the files actually on disk, because a rule checked only on paper is not
                   checked.

A check that examined zero items reports ``BLOCKED``, never ``PASS`` (the rule of
`evidence/tools/README.md` §7.3): a loop that lost its input is not a clean result.

What it does NOT check
----------------------
It does not read the cards for meaning. A card can pass every check here and still order
the wrong work. It is `SELF_VALIDATION` in the sense of SRC-PLAN §11: a machine re-reading
declarations, not an independent review.

Proving the checks bite
-----------------------
``--self-test`` builds a shadow tree in a scratch directory (never in the repo), injects one
known defect per check, and asserts that (1) the pristine shadow passes and (2) each mutated
shadow fails the check that owns the defect. Every injection is verified to have landed:
`evidence/tools/README.md` §5b records what happens when a self-test's mutation silently does
not apply — the check reports PASS and the self-test proves nothing, in a way that looks like
success. Exit 0 only when every mutation was caught.

Exit code: 0 when every check PASSes, 1 when any FAILs or is BLOCKED, 2 when the tool itself
cannot run. This tool only reads the repository; it writes nothing except the optional
--json-out report and, under --self-test, files inside its own scratch directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment problem, not a card problem
    print("PyYAML is required: uv run python evidence/tools/verify_cards.py", file=sys.stderr)
    raise SystemExit(2) from None

CARDS_DIR = "agent-tasks"
CARD_RE = re.compile(r"^TC-[a-z0-9-]+\.md$")

#: A pin row: `| <something with a `path`> | <64 hex> | <bytes> |`.
PIN_ROW_RE = re.compile(
    r"^\|(?P<label>[^|]*)\|\s*`?(?P<sha>[0-9a-f]{64})`?\s*\|\s*(?P<bytes>[0-9][0-9\s]*)\|"
)
BACKTICKED_RE = re.compile(r"`([^`]+)`")
EPOCH_RE = re.compile(r"Pin epoch:\s*\*{0,2}`(?P<epoch>[A-Za-z0-9._-]+)`")
SECTION_RE = re.compile(r"^##\s+§(?P<num>[0-9]+)\.", re.M)

#: Path-shaped token: at least one "/" and a known suffix, or a top-level tree prefix.
PATH_RE = re.compile(
    r"^(?:contracts|acceptance|precode|agent-tasks|evidence|server|collector|worker|probe"
    r"|shared|tests|web|tools|docs)/[A-Za-z0-9._/*-]+$"
)
DOC_ROOTS = ("contracts/", "acceptance/", "precode/", "agent-tasks/", "evidence/", "docs/")

#: Paths a card NAMES AS ITS OWN FUTURE OUTPUT. EV-PC10-01's limitations record this as one
#: of the three false-positive classes its oracle was corrected for: `evidence/runs/<card>/`
#: is where the card's evidence manifest WILL be written when the card runs, so requiring it
#: to exist now would make every unstarted card fail. This is an exclusion *by rule*, not a
#: waiver of a real miss: anything outside these prefixes is still required to exist.
FUTURE_ARTEFACT_PREFIXES = ("evidence/runs/",)
PYTHON_TREES = ("server/", "collector/", "worker/", "probe/", "shared/", "tests/", "tools/")
WEB_TREE = "web/"

#: (k) An epoch token anywhere in prose, not only in the `Pin epoch:` declaration.
EPOCH_TOKEN_RE = re.compile(r"PC10-PIN-[A-Za-z0-9-]*[0-9]")
#: Files that assert a *current* pin epoch and must therefore name the cards' epoch.
ASSERTING_FILES = (
    "precode/README.md",
    "agent-tasks/README.md",
    "agent-tasks/TEMPLATE.md",
    "agent-tasks/WALKTHROUGH.md",
)
#: A superseded epoch may be named only in a paragraph that says it is superseded.
SUPERSEDE_MARKERS = (
    "thay",
    "superseded",
    "bản trước",
    "trước đó",
    "epoch cũ",
    "cũ hơn",
    "ví dụ",
    "gốc",
    "lịch sử",
    "hiện hành",
)

#: (h) FIX5 obligations carried by every card.
R5_BOUNDARY_CODES = ("UNAUTHORIZED", "FORBIDDEN_EDGE", "CAPABILITY_DENIED", "CSRF_REJECTED")
DEFAULT_DENY_SCENARIO = "SC49"
BOUNDARY_FIXTURE = "boundary/a-default-deny-sweep-36-edges.json"

#: (i) The only claim labels SRC-PLAN §2 defines.
PLAN_LABELS = frozenset(
    {
        "DRAFT_FOR_REVIEW",
        "CONTRACT_READY",
        "IMPLEMENTATION_VERIFIED",
        "INTEGRATION_VERIFIED",
        "LIVE_FEASIBILITY_VERIFIED",
        "PRODUCT_ACCEPTED",
    }
)
#: Tokens that read as a claim label and are therefore held to the allowlist. `CONTRACT_ONLY`
#: is listed here and absent from PLAN_LABELS on purpose: it is a plausible invention, and an
#: invented label is exactly what this check exists to reject.
CLAIM_LABEL_RE = re.compile(r"\b([A-Z][A-Z_]{6,})\b")
CLAIM_LABEL_TRIGGERS = frozenset(
    {"CONTRACT_ONLY", "CONTRACT_READY", "DRAFT_FOR_REVIEW", "PRODUCT_ACCEPTED"}
)

#: (j) PC09 owns these; the cards cite them by path + SC id and must NOT pin their hashes.
PC09_UNPINNED_FILES = (
    "acceptance/scenarios.yaml",
    "acceptance/traceability.csv",
    "precode/gates.yaml",
    "precode/review.md",
    "evidence/manifest.schema.json",
    "evidence/index.json",
    "evidence/tools/e0_check.py",
)

#: (l) Stack A must not be presented as the chosen stack.
STACK_A_RE = re.compile(r"Option A|Python toàn bộ")
ACCEPTED_STACK = "Option B"
STACK_RATIFICATION = "OD-20260907-01"

OPERATION_RE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
SCENARIO_RE = re.compile(r"\bSC(?P<n>[0-9]{2,3})\b")
MODULE_RE = re.compile(r"\bMOD-[a-z0-9-]+\b")
INVARIANT_RE = re.compile(r"(?<![A-Za-z0-9])I(?P<n>[0-9]{2})(?![0-9A-Za-z])")
SCREAMING_RE = re.compile(r"`([A-Z][A-Z0-9_]{3,})`")

#: Words that look like error codes in §7 but are protocol/status vocabulary. Same idea as
#: STATUS_VOCABULARY in evidence/tools/e0_check.py; kept short and explicit on purpose.
STATUS_VOCABULARY = {
    "PASS",
    "FAIL",
    "BLOCKED",
    "NOT_RUN",
    "STALE",
    "NOT_APPLICABLE",
    "DRAFT_FOR_REVIEW",
    "CONTRACT_READY",
    "IMPLEMENTATION_VERIFIED",
    "INTEGRATION_VERIFIED",
    "LIVE_FEASIBILITY_VERIFIED",
    "PRODUCT_ACCEPTED",
    "SELF_VALIDATION",
    "TASK_PACKET",
    "HANDOFF",
    "AUDIT_REPORT",
    "OPEN",
    "PROVISIONAL",
    "RATIFIED",
    "ACCEPTED",
    "OWNER_DECISION_REQUIRED",
    "TRUE",
    "FALSE",
    "NULL",
    "AND",
    "OR",
    "NOT",
    "UPDATE",
    "INSERT",
    "SELECT",
    "DELETE",
}


@dataclass
class Check:
    id: str
    title: str
    checked: int = 0
    violations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def fail(self, where: str, message: str) -> None:
        self.violations.append(f"{where}: {message}")

    def note(self, message: str) -> None:
        self.notes.append(message)

    @property
    def status(self) -> str:
        if self.violations:
            return "FAIL"
        # evidence/tools/README.md §7.3: a check that read nothing is not a clean check.
        return "BLOCKED" if self.checked == 0 else "PASS"

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "checked": self.checked,
            "status": self.status,
            "violations": self.violations,
            "notes": self.notes,
        }


class Repo:
    def __init__(self, root: str) -> None:
        self.root = os.path.abspath(root)
        self.cards: dict[str, str] = {}
        cards_dir = os.path.join(self.root, CARDS_DIR)
        if not os.path.isdir(cards_dir):
            raise SystemExit(f"no {CARDS_DIR}/ directory under {self.root}")
        for name in sorted(os.listdir(cards_dir)):
            if CARD_RE.match(name):
                with open(os.path.join(cards_dir, name), encoding="utf-8") as handle:
                    self.cards[f"{CARDS_DIR}/{name}"] = handle.read()
        if not self.cards:
            raise SystemExit(f"no TC-*.md cards found in {cards_dir}")

    def path(self, rel: str) -> str:
        return os.path.join(self.root, rel)

    def exists(self, rel: str) -> bool:
        return os.path.exists(self.path(rel))

    def read_yaml(self, rel: str) -> Any:
        with open(self.path(rel), encoding="utf-8") as handle:
            return yaml.safe_load(handle)


def sections(text: str) -> dict[int, str]:
    """Split a card into its `## §N.` sections."""
    marks = [(m.start(), int(m.group("num"))) for m in SECTION_RE.finditer(text)]
    out: dict[int, str] = {}
    for index, (start, num) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(text)
        out[num] = text[start:end]
    return out


def backticked(text: str) -> list[str]:
    return [m.group(1).strip() for m in BACKTICKED_RE.finditer(text)]


# ----------------------------------------------------------------------------------------
# checks
# ----------------------------------------------------------------------------------------

def check_pins(repo: Repo) -> Check:
    check = Check("pins", "Every pinned sha256 and byte count matches the file on disk")
    for card, text in repo.cards.items():
        for line in text.splitlines():
            match = PIN_ROW_RE.match(line.strip())
            if not match:
                continue
            labels = backticked(match.group("label"))
            if not labels:
                continue
            rel = labels[0]
            if not PATH_RE.match(rel) and "/" not in rel and not rel.endswith(".md"):
                continue
            check.checked += 1
            expected_sha = match.group("sha")
            expected_bytes = int(match.group("bytes").replace(" ", "").replace(" ", ""))
            if not repo.exists(rel):
                check.fail(card, f"pinned file is missing: {rel}")
                continue
            with open(repo.path(rel), "rb") as handle:
                blob = handle.read()
            actual_sha = hashlib.sha256(blob).hexdigest()
            if actual_sha != expected_sha:
                check.fail(
                    card,
                    f"{rel}: pinned sha256 {expected_sha[:16]}… but file is "
                    f"{actual_sha[:16]}… — the card is STALE",
                )
            elif len(blob) != expected_bytes:
                check.fail(
                    card,
                    f"{rel}: pinned {expected_bytes} bytes but file is {len(blob)}",
                )
    return check


def check_epoch(repo: Repo) -> Check:
    check = Check(
        "epoch",
        "All cards declare the same pin epoch (§0), and every file asserting a current pin "
        "names that same epoch",
    )
    epochs: dict[str, str] = {}
    for card, text in repo.cards.items():
        check.checked += 1
        match = EPOCH_RE.search(text)
        if not match:
            check.fail(card, "§0 declares no pin epoch")
            continue
        epochs[card] = match.group("epoch")
    distinct = sorted(set(epochs.values()))
    current: str | None = None
    if len(distinct) > 1:
        for card, epoch in sorted(epochs.items()):
            if epoch != max(distinct, key=lambda e: sum(1 for v in epochs.values() if v == e)):
                check.fail(card, f"pin epoch {epoch!r} differs from the majority {distinct!r}")
    elif distinct:
        current = distinct[0]
        check.note(f"pin epoch: {current}")

    # (k) full form. The epoch is READ FROM THE CARDS, never transcribed: the cards are the
    # source of truth (§0), so a file that names a superseded epoch under a "current pin"
    # heading sends its reader to verify the wrong bytes.
    if current is None:
        check.note(
            "cards do not agree on one epoch, so the asserting files could not be checked "
            "against it — fix the cards first"
        )
        return check
    for rel in ASSERTING_FILES:
        if not repo.exists(rel):
            check.note(f"{rel} does not exist; nothing to assert")
            continue
        body = _read_text(repo, rel)
        tokens = EPOCH_TOKEN_RE.findall(body)
        if not tokens:
            continue
        check.checked += 1
        if current not in tokens:
            check.fail(
                rel,
                f"names pin epoch(s) {sorted(set(tokens))} but never the current one {current}",
            )
        # A wrapped sentence stays in one unit: split on blank lines, not newlines.
        for paragraph in re.split(r"\n\s*\n", body):
            for token in EPOCH_TOKEN_RE.findall(paragraph):
                if token == current:
                    continue
                if not any(marker in paragraph for marker in SUPERSEDE_MARKERS):
                    condensed = " ".join(paragraph.split())[:110]
                    check.fail(
                        rel,
                        f"superseded epoch {token} asserted without a supersession marker: "
                        f"{condensed}",
                    )
    return check


def check_obligations(repo: Repo) -> Check:
    """(h) FIX5's floor: default-deny sweep, R5-01 boundary table, boundary fixture."""
    check = Check(
        "obligations",
        f"Every card carries {DEFAULT_DENY_SCENARIO}, the R5-01 boundary code table in §5, "
        "and the default-deny fixture",
    )
    for card, text in repo.cards.items():
        check.checked += 1
        if DEFAULT_DENY_SCENARIO not in text:
            check.fail(card, f"missing the {DEFAULT_DENY_SCENARIO} default-deny obligation")
        if BOUNDARY_FIXTURE not in text:
            check.fail(card, f"does not reference the boundary fixture {BOUNDARY_FIXTURE}")
        section5 = sections(text).get(5, "")
        if not section5:
            check.fail(card, "has no §5, so the R5-01 boundary table cannot be there")
            continue
        for code in R5_BOUNDARY_CODES:
            check.checked += 1
            if code not in section5:
                check.fail(card, f"§5 has no R5-01 boundary row for {code}")
    return check


def check_claim_labels(repo: Repo) -> Check:
    """(i) Claim labels come from SRC-PLAN §2 or they do not exist."""
    check = Check("claim_labels", "Every claim label a card uses is one SRC-PLAN §2 defines")
    for card, text in repo.cards.items():
        for label in sorted(set(CLAIM_LABEL_RE.findall(text))):
            if not (label.endswith("_VERIFIED") or label in CLAIM_LABEL_TRIGGERS):
                continue
            check.checked += 1
            if label not in PLAN_LABELS:
                check.fail(card, f"uses claim label {label!r}, which SRC-PLAN §2 does not define")
    return check


def check_pc09_unpinned(repo: Repo) -> Check:
    """(j) PC09's files are cited by path + SC id and must not be pinned by hash."""
    check = Check(
        "pc09_unpinned",
        "No card pins a PC09-owned file by hash in §0 (Coordinator ruling on CR-PC10-01)",
    )
    for card, text in repo.cards.items():
        section0 = sections(text).get(0, "")
        for rel in PC09_UNPINNED_FILES:
            check.checked += 1
            pinned = re.search(
                r"\|\s*`" + re.escape(rel) + r"`\s*\|\s*`?[0-9a-f]{64}", section0
            )
            if pinned:
                check.fail(
                    card,
                    f"§0 pins {rel} by hash; it must be cited by path + SC id and read live",
                )
    return check


def check_stack(repo: Repo) -> Check:
    """(l) Stack A may appear as history, never as the chosen stack."""
    check = Check(
        "stack",
        f"No card presents Stack A as chosen; every card names {ACCEPTED_STACK} and cites "
        f"{STACK_RATIFICATION}",
    )
    for card, text in repo.cards.items():
        check.checked += 1
        if ACCEPTED_STACK not in text:
            check.fail(card, f"does not name the accepted stack ({ACCEPTED_STACK})")
        if STACK_RATIFICATION not in text:
            check.fail(card, f"does not cite the Owner ratification {STACK_RATIFICATION}")
        for paragraph in re.split(r"\n\s*\n", text):
            if not STACK_A_RE.search(paragraph):
                continue
            check.checked += 1
            if not re.search(r"thay|không phải|superseded|cũ|trước đó|bị bác", paragraph):
                condensed = " ".join(paragraph.split())[:110]
                check.fail(card, f"presents Stack A without a superseded marker: {condensed}")
    return check


def check_paths(repo: Repo) -> Check:
    check = Check("paths", "Every cited path under a documentation tree exists on disk")
    skipped_future = 0
    for card, text in repo.cards.items():
        for token in sorted(set(backticked(text))):
            candidate = token.rstrip(",.;:")
            if not candidate.startswith(DOC_ROOTS):
                continue
            if candidate.startswith(FUTURE_ARTEFACT_PREFIXES):
                skipped_future += 1
                continue
            if "*" in candidate or candidate.endswith("/"):
                continue
            if not PATH_RE.match(candidate):
                continue
            # `file.yaml.key` — a YAML key path, not a file (EV-PC10-01 limitation 1).
            if not os.path.splitext(candidate)[1] in (
                ".md",
                ".yaml",
                ".yml",
                ".json",
                ".csv",
                ".py",
            ):
                continue
            check.checked += 1
            if not repo.exists(candidate):
                check.fail(card, f"cited path does not exist: {candidate}")
    if skipped_future:
        check.note(
            f"{skipped_future} citation(s) of a card's own future evidence output under "
            f"{FUTURE_ARTEFACT_PREFIXES[0]} were not required to exist (EV-PC10-01 "
            f"false-positive class 2). They are NOT proof that any evidence was produced."
        )
    return check


def check_operations(repo: Repo) -> Check:
    check = Check("operations", "Every operation id in §4 exists in contracts/ports.yaml")
    ports = repo.read_yaml("contracts/ports.yaml")
    known = {entry["operation_id"] for entry in ports["operations"]}
    for card, text in repo.cards.items():
        section = sections(text).get(4, "")
        for line in section.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- `"):
                continue
            for token in backticked(stripped):
                if not OPERATION_RE.match(token):
                    continue
                check.checked += 1
                if token not in known:
                    check.fail(card, f"§4 names operation {token!r}, absent from ports.yaml")
    return check


def check_scenarios(repo: Repo) -> Check:
    check = Check("scenarios", "Every SC id resolves in acceptance/scenarios.yaml")
    doc = repo.read_yaml("acceptance/scenarios.yaml")
    known: set[str] = set()
    for value in _walk_values(doc):
        if isinstance(value, str) and re.fullmatch(r"SC[0-9]{2,3}", value):
            known.add(value)
    if not known:
        check.fail("acceptance/scenarios.yaml", "no scenario ids found; cannot verify")
        return check
    for card, text in repo.cards.items():
        for match in SCENARIO_RE.finditer(text):
            sc = f"SC{match.group('n')}"
            check.checked += 1
            if sc not in known:
                check.fail(card, f"cites {sc}, which is not defined in scenarios.yaml")
    return check


def check_errors(repo: Repo) -> Check:
    check = Check("errors", "Every error code named in §7 is registered in contracts/errors.yaml")
    errors = repo.read_yaml("contracts/errors.yaml")
    known = {entry["code"] for entry in errors["codes"]}
    for card, text in repo.cards.items():
        section = sections(text).get(7, "")
        for match in SCREAMING_RE.finditer(section):
            token = match.group(1)
            if token in STATUS_VOCABULARY:
                continue
            check.checked += 1
            if token not in known:
                check.fail(card, f"§7 names {token!r}, which is not a registered error code")
    return check


def check_modules(repo: Repo) -> Check:
    check = Check("modules", "Every MOD-* exists in contracts/modules.yaml")
    text_modules = set(MODULE_RE.findall(_read_text(repo, "contracts/modules.yaml")))
    if not text_modules:
        check.fail("contracts/modules.yaml", "no MOD-* ids found; cannot verify")
        return check
    for card, text in repo.cards.items():
        for module in sorted(set(MODULE_RE.findall(text))):
            check.checked += 1
            if module not in text_modules:
                check.fail(card, f"names {module}, absent from contracts/modules.yaml")
    return check


def check_invariants(repo: Repo) -> Check:
    check = Check("invariants", "Every I<nn> is a defined invariant")
    defined = set(MODULE_INVARIANTS := set())
    for source in ("contracts/data/invariants.md", "research-radar-pre-code-plan.md"):
        if repo.exists(source):
            for match in INVARIANT_RE.finditer(_read_text(repo, source)):
                defined.add(f"I{match.group('n')}")
    del MODULE_INVARIANTS
    if not defined:
        check.fail("contracts/data/invariants.md", "no invariant ids found; cannot verify")
        return check
    for card, text in repo.cards.items():
        for match in INVARIANT_RE.finditer(text):
            inv = f"I{match.group('n')}"
            check.checked += 1
            if inv not in defined:
                check.fail(card, f"cites {inv}, which no invariant register defines")
    return check


def check_layout(repo: Repo) -> Check:
    check = Check(
        "layout",
        "Two-language rule (agent-tasks/README.md §5.3): no .py under web/, no .ts under "
        "the Python trees — checked on the cards AND on disk",
    )
    for card, text in repo.cards.items():
        for token in sorted(set(backticked(text))):
            candidate = token.rstrip(",.;:")
            if not PATH_RE.match(candidate):
                continue
            check.checked += 1
            if candidate.startswith(WEB_TREE) and candidate.endswith(".py"):
                check.fail(card, f"names a Python file under web/: {candidate}")
            if candidate.startswith(PYTHON_TREES) and candidate.endswith((".ts", ".tsx")):
                check.fail(card, f"names a TypeScript file under a Python tree: {candidate}")

    skip = {".git", "node_modules", ".venv", "__pycache__", "dist", ".mypy_cache",
            ".pytest_cache", ".ruff_cache"}
    for tree in (WEB_TREE, *PYTHON_TREES):
        base = repo.path(tree.rstrip("/"))
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for name in filenames:
                rel = os.path.relpath(os.path.join(dirpath, name), repo.root)
                check.checked += 1
                if tree == WEB_TREE and name.endswith(".py"):
                    check.fail("on disk", f"Python file under web/: {rel}")
                if tree != WEB_TREE and name.endswith((".ts", ".tsx")):
                    check.fail("on disk", f"TypeScript file under a Python tree: {rel}")
    return check


def _read_text(repo: Repo, rel: str) -> str:
    with open(repo.path(rel), encoding="utf-8") as handle:
        return handle.read()


def _walk_values(node: Any):  # type: ignore[no-untyped-def]
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_values(value)
    else:
        yield node


# ----------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------

CHECKS = (
    check_pins,
    check_epoch,
    check_paths,
    check_operations,
    check_scenarios,
    check_errors,
    check_modules,
    check_invariants,
    check_obligations,
    check_claim_labels,
    check_pc09_unpinned,
    check_stack,
    check_layout,
)


#: Ids a `--only` selection may name. Derived from the function names so the two cannot drift.
KNOWN_CHECK_IDS = frozenset(
    fn.__name__[len("check_"):] if fn.__name__.startswith("check_") else fn.__name__
    for fn in CHECKS
)


def run_checks(repo: Repo, wanted: set[str] | None = None) -> list[Check]:
    results: list[Check] = []
    for function in CHECKS:
        check = function(repo)
        if wanted and check.id not in wanted:
            continue
        results.append(check)
    return results


def build_report(repo: Repo, results: list[Check]) -> dict[str, Any]:
    return {
        "tool": "evidence/tools/verify_cards.py",
        "repo": repo.root,
        "cards": sorted(repo.cards),
        "checks": [c.to_json() for c in results],
        "totals": {
            "assertions": sum(c.checked for c in results),
            "violations": sum(len(c.violations) for c in results),
            "pass": sum(1 for c in results if c.status == "PASS"),
            "fail": sum(1 for c in results if c.status == "FAIL"),
            "blocked": sum(1 for c in results if c.status == "BLOCKED"),
        },
        "evidence_kind": "SELF_VALIDATION",
    }


# ----------------------------------------------------------------------------------------
# negative self-test
# ----------------------------------------------------------------------------------------
#: Trees the shadow copies for real, because mutations land in them. Everything else at the
#: repository root is symlinked, so the shadow costs a few hundred kilobytes, not a checkout.
SHADOW_COPIED = ("agent-tasks", "precode")


def _build_shadow(root: str, dest: str) -> None:
    import shutil

    os.makedirs(dest, exist_ok=False)
    for name in sorted(os.listdir(root)):
        source = os.path.join(root, name)
        target = os.path.join(dest, name)
        if name in SHADOW_COPIED:
            shutil.copytree(source, target, symlinks=True)
        else:
            os.symlink(source, target)


def _mutate(path: str, old: str, new: str) -> None:
    """Replace `old` once, and fail loudly when the target string is not there.

    evidence/tools/README.md §5b: a mutation that silently does not apply makes the check
    report PASS and the self-test prove nothing, in the shape of a success.
    """
    with open(path, encoding="utf-8") as handle:
        body = handle.read()
    if old not in body:
        raise SystemExit(f"self-test: mutation target absent in {path}: {old[:60]!r}")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body.replace(old, new, 1))


def _first_card(shadow: str) -> str:
    names = sorted(n for n in os.listdir(os.path.join(shadow, CARDS_DIR)) if CARD_RE.match(n))
    return os.path.join(shadow, CARDS_DIR, names[0])


def _m_pins(shadow: str) -> None:
    card = _first_card(shadow)
    with open(card, encoding="utf-8") as handle:
        match = re.search(r"`([0-9a-f]{64})`", handle.read())
    assert match is not None
    _mutate(card, match.group(1), "0" * 64)


def _m_epoch_cards(shadow: str) -> None:
    _mutate(_first_card(shadow), "Pin epoch: `PC10-PIN-", "Pin epoch: `PC10-PIN-BOGUS9-")


def _m_epoch_asserting(shadow: str) -> None:
    path = os.path.join(shadow, "agent-tasks", "README.md")
    with open(path, encoding="utf-8") as handle:
        tokens = EPOCH_TOKEN_RE.findall(handle.read())
    if not tokens:
        raise SystemExit("self-test: agent-tasks/README.md names no epoch to mutate")
    _mutate(path, tokens[0], "PC10-PIN-STALE0-20260101")


def _m_paths(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §1.", "`contracts/no-such-contract.yaml`\n\n## §1.")


def _m_operations(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §4.", "## §4.\n\n- `bogus.operation_id`\n")


def _m_scenarios(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §8.", "## §8.\n\nSC97 là kịch bản không tồn tại.\n")


def _m_errors(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §7.", "## §7.\n\n`NOT_A_REGISTERED_CODE`\n")


def _m_modules(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §4.", "## §4.\n\nMOD-not-a-real-module\n")


def _m_invariants(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §6.", "## §6.\n\n`I97` là bất biến không tồn tại.\n")


def _m_obligations(shadow: str) -> None:
    card = _first_card(shadow)
    # Both halves of the obligation, and every occurrence: a partial rename would leave the
    # code as a substring and the check would still find it.
    _mutate(card, "CSRF_REJECTED", "CSRF_DENIED")
    with open(card, encoding="utf-8") as handle:
        body = handle.read()
    with open(card, "w", encoding="utf-8") as handle:
        handle.write(body.replace("CSRF_REJECTED", "CSRF_DENIED").replace(
            DEFAULT_DENY_SCENARIO, "SC48"))


def _m_claim_labels(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §1.", "## §1.\n\nTrần claim: `PRODUCTION_VERIFIED`.\n")


def _m_pc09_unpinned(shadow: str) -> None:
    _mutate(
        _first_card(shadow),
        "| Hợp đồng / fixture đã pin | SHA-256 | Bytes |\n| --- | --- | --- |\n",
        "| Hợp đồng / fixture đã pin | SHA-256 | Bytes |\n| --- | --- | --- |\n"
        "| `acceptance/scenarios.yaml` | `" + "a" * 64 + "` | 1 |\n",
    )


def _m_stack(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §3.", "Stack: Option A.\n\n## §3.")


def _m_layout(shadow: str) -> None:
    _mutate(_first_card(shadow), "## §3.", "## §3.\n\n| `web/src/lib/handler.py` | vai trò |\n")


#: (check id, what the defect is, how to inject it). Order matches CHECKS.
SELF_TESTS: tuple[tuple[str, str, Any], ...] = (
    ("pins", "a pinned sha256 no longer matches the file on disk", _m_pins),
    ("epoch", "one card re-pinned alone, to a different epoch", _m_epoch_cards),
    ("epoch", "an entry-point file left asserting a superseded epoch", _m_epoch_asserting),
    ("paths", "a card cites a contract that does not exist", _m_paths),
    ("operations", "§4 names an operation absent from ports.yaml", _m_operations),
    ("scenarios", "a card cites an SC id no scenario defines", _m_scenarios),
    ("errors", "§7 names an unregistered error code", _m_errors),
    ("modules", "a card names a module absent from modules.yaml", _m_modules),
    ("invariants", "a card cites an undefined invariant", _m_invariants),
    ("obligations", "SC49 and one R5-01 boundary code removed from a card", _m_obligations),
    ("claim_labels", "a card invents a claim label outside SRC-PLAN §2", _m_claim_labels),
    ("pc09_unpinned", "a card pins a PC09-owned file by hash", _m_pc09_unpinned),
    ("stack", "a card presents Stack A as chosen, with no supersession marker", _m_stack),
    ("layout", "a card puts a Python file under web/", _m_layout),
)


def self_test(root: str, scratch: str) -> int:
    """Inject one known defect per check and require the owning check to catch it."""
    import shutil

    os.makedirs(scratch, exist_ok=True)
    shadow = os.path.join(scratch, "shadow")
    if os.path.exists(shadow):
        shutil.rmtree(shadow)
    _build_shadow(root, shadow)
    pristine = {
        rel: _read_bytes(os.path.join(shadow, rel))
        for rel in _mutable_files(shadow)
    }

    print("=== negative self-test: does each check bite? ===")
    print(f"shadow tree: {shadow}  (copied: {', '.join(SHADOW_COPIED)}; rest symlinked)")

    # The baseline is per check, not global. A check that already fails on the real tree (a
    # genuinely stale pin, say) can still be proven to bite: its violation count must GROW
    # when the defect is injected. A global "everything must pass first" precondition would
    # instead disable the whole self-test exactly when the tree needs it most.
    baseline = {c.id: (c.status, len(c.violations)) for c in run_checks(Repo(shadow))}
    unclean = {cid: v for cid, v in baseline.items() if v[0] != "PASS"}
    if unclean:
        print(f"note: shadow is not clean to begin with: {unclean} — comparing violation counts")
    print()

    caught = 0
    for check_id, defect, mutator in SELF_TESTS:
        for rel, blob in pristine.items():
            _write_bytes(os.path.join(shadow, rel), blob)
        mutator(shadow)
        result = next(c for c in run_checks(Repo(shadow), {check_id}))
        before = baseline[check_id][1]
        ok = len(result.violations) > before
        caught += 1 if ok else 0
        suffix = f" (baseline already had {before})" if before else ""
        print(f"{'CAUGHT ' if ok else 'MISSED '} {check_id:<14} {defect}{suffix}")
        if not ok:
            print(
                f"         ! the mutation landed but {check_id} still reported "
                f"{result.status} with {len(result.violations)} violations"
            )
        else:
            print(f"         → {result.violations[-1]}")

    for rel, blob in pristine.items():
        _write_bytes(os.path.join(shadow, rel), blob)
    shutil.rmtree(shadow)
    print(f"\nSELF-TEST: {caught}/{len(SELF_TESTS)} mutations caught")
    if unclean:
        print(
            "The self-test proves the checks bite. It does NOT say the repository passes — "
            f"these checks were already failing before any mutation: {sorted(unclean)}"
        )
    return 0 if caught == len(SELF_TESTS) else 1


def _mutable_files(shadow: str) -> list[str]:
    out = [os.path.join(CARDS_DIR, n) for n in sorted(os.listdir(os.path.join(shadow, CARDS_DIR)))
           if n.endswith(".md")]
    out.append("precode/README.md")
    return [rel for rel in out if os.path.isfile(os.path.join(shadow, rel))]


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _write_bytes(path: str, blob: bytes) -> None:
    with open(path, "wb") as handle:
        handle.write(blob)


def main(argv: list[str] | None = None) -> int:
    default_repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser = argparse.ArgumentParser(description="Verify the agent-tasks/ card pins")
    parser.add_argument("--repo", default=default_repo, help="repository root")
    parser.add_argument("--json-out", default=None, help="write a machine-readable report here")
    parser.add_argument(
        "--json", action="store_true", help="print the machine-readable report to stdout"
    )
    parser.add_argument("--only", default=None, help="comma-separated check ids")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="inject one known defect per check and require the check to catch it",
    )
    parser.add_argument(
        "--self-test-dir",
        default=None,
        help="scratch directory for --self-test (default: a temporary directory); never "
        "inside the repository",
    )
    args = parser.parse_args(argv)

    repo = Repo(args.repo)
    wanted = {c.strip() for c in args.only.split(",")} if args.only else None
    if wanted:
        # An unknown id must not select nothing and exit 0 — that is a silent pass.
        unknown = wanted - KNOWN_CHECK_IDS
        if unknown:
            print(f"unknown check id(s): {sorted(unknown)}; known: {sorted(KNOWN_CHECK_IDS)}",
                  file=sys.stderr)
            return 2

    if args.self_test:
        import tempfile

        scratch = args.self_test_dir or tempfile.mkdtemp(prefix="verify_cards_selftest_")
        if os.path.abspath(scratch).startswith(repo.root + os.sep):
            print("--self-test-dir must be outside the repository", file=sys.stderr)
            return 2
        return self_test(repo.root, scratch)

    results = run_checks(repo, wanted)

    if args.json:
        json.dump(build_report(repo, results), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 1 if any(c.status != "PASS" for c in results) else 0

    failed = 0
    for check in results:
        print(
            f"{check.status:<6} {check.id:<12} checked={check.checked:<6} "
            f"violations={len(check.violations):<5} {check.title}"
        )
        for note in check.notes:
            print(f"         # {note}")
        for violation in check.violations[:50]:
            print(f"         ! {violation}")
        if len(check.violations) > 50:
            print(f"         ! … {len(check.violations) - 50} more")
        failed += len(check.violations)

    total_checked = sum(c.checked for c in results)
    blocked = sum(1 for c in results if c.status == "BLOCKED")
    print(
        f"\nTOTAL: {len(results)} checks over {len(repo.cards)} cards — "
        f"{sum(1 for c in results if c.status == 'PASS')} PASS, "
        f"{sum(1 for c in results if c.status == 'FAIL')} FAIL, "
        f"{blocked} BLOCKED, "
        f"{total_checked} assertions, {failed} violations"
    )
    print(
        "This is SELF_VALIDATION: it re-reads declarations. It does not review what a card "
        "orders."
    )

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(build_report(repo, results), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    return 1 if any(c.status != "PASS" for c in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
