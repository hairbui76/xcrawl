# Coordination baseline — Research Radar Pre-code execution

Issued by: Coordinator (this Claude Code session, principal `coordinator@session-01BAnmhQcMCXY2V66NH6c1PY`)
Issued at: 2026-09-06T16:50Z · Mode: `DOCUMENTARY_DRAFT` · Enforcement: `NOT_IMPLEMENTED` (leases are message-tracked; you MUST self-enforce scope)

Read this file first, then your own packet file, then `agent_profile/worker.md` and `agent_profile/protocol.md` (Workers) or `agent_profile/auditor.md` (Auditors). Then read the two source documents in full.

## 1. Authority chain

- `AUTH-OWNER-20260906-01`: Owner (user of this session) instructed: "Act as a Project Manager … use agent_profile/ to run research-radar-pre-code-plan.md with research-radar-spec.md" and then "Do everything until finish this project." Issued 2026-09-06. This is the explicit Owner grant for a documentary drafting session covering all Pre-code deliverables (PC00–PC10) listed in plan §4.
- `AUTH-COORD-<PACKET>`: delegation from Coordinator to one Worker/Auditor, scoped to exactly the paths in the packet, valid until the packet `expires_at`. Delegation depth 1; you may not delegate further or spawn agents.
- Product blockers B01–B17 stay formally OPEN in `agent_profile/registry.json`. The Coordinator has ruled that each is **provisionally resolved** using the plan's PC-ĐX recommendation (see §5 below). Use the label `PROVISIONAL` for these decisions everywhere; never write `CLOSED`, `ACCEPTED` or `XN` for them. Ratification is the Owner's, via the OWNER_DECISION_REQUEST that PC00 drafts and PC09 finalises.

## 2. Workspace and source baselines

Workspace root (canonical): `/mnt/virtual/repo/xcrawl`. All write targets are relative to this root. Git: do **not** commit, stage, stash, or run any git command that mutates the repo. Do not create files outside your allowlist (no `__pycache__`: set `PYTHONDONTWRITEBYTECODE=1`; run any helper script from your scratch directory given in your packet, never from the repo).

Pinned sources (verify with `sha256sum` before you start and again before HANDOFF; if either differs → STALE_BASELINE, stop):

| Ref | Path | SHA-256 | Bytes |
| --- | --- | --- | --- |
| SRC-PLAN | `/mnt/virtual/repo/xcrawl/research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |
| SRC-SPEC | `/mnt/virtual/repo/xcrawl/research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |

The registry pins the same hashes under older paths (`/workspace/scratch/9cff39a6f330/…`); the repo paths above are canonical for this session. `project-overview.md` and `master-interview-prompt.md` are historical context only; the plan §1 forbids using the old overview to reopen newer decisions.

## 3. Global conventions (binding for every package)

**Language.** Prose in Vietnamese (matching the sources). Identifiers, YAML/JSON keys, enums, operation IDs, error codes, file names in English.

**Stable IDs** (use exactly these forms; they are how parallel packages cross-reference each other):

| Kind | Form | Notes |
| --- | --- | --- |
| Requirement from decision log | `REQ-D01` … `REQ-D59` | keep the spec's numbering incl. gaps; `REQ-CTAG` for the row "C03/D-tag" |
| Acceptance criterion | `REQ-AC01` … `REQ-AC18` | |
| P0 scope item | `REQ-P0-01` … `REQ-P0-12` | spec §2.1 rows in order |
| Deferred / out of scope | `REQ-P1-01`…, `REQ-OOS-01`… | spec §2.2 rows, §2.3 bullets in order |
| Assumption | `REQ-A1` … `REQ-A7` | |
| Open question | `REQ-OQ01` … `REQ-OQ10` | spec §13.1 |
| Other atomic prose requirement | `REQ-S<section>-<nn>` | e.g. `REQ-S11.3-02`; section number from the spec, two-digit sequence within section |
| Blocker | `B01` … `B17` | plan §3 |
| Amendment | `AMD-B01` … | one per blocker that changes committed behaviour |
| ADR | `ADR-0001` … | zero-padded 4 digits |
| Invariant | `I01` … `I15` | plan §7; new ones `I16+` only with a decision record |
| Error code | as plan §10 (`X_CHALLENGE_REQUIRED` …) | new codes SCREAMING_SNAKE, registered in `contracts/errors.yaml` |
| Scenario | `SC01` … `SC18` (= AC-01…18), `SC19` … `SC28` (plan §13 list, in order), `SC29+` extra | |
| Gate | `G0` … `G7`, `SP1` | |
| Module | `MOD-<kebab>` | e.g. `MOD-web-ui`, `MOD-backend-api`, `MOD-x-collector` — PC01 owns the list |
| Operation | `<domain>.<verb_noun>` snake_case | e.g. `worker.claim_assignment`, `ingest.submit_batch` — PC01 owns the inventory in `contracts/ports.yaml` |
| Contract | `CT-<area>-<name>` | e.g. `CT-state-run`, `CT-schema-target` |
| Change request | `CR-<PC>-<nn>` | raised by a package that needs a change in a file it may not write |
| Evidence record | `EV-<PC>-<nn>` | |

**Status vocabulary.** Requirement status: `XN | UQ | ĐX | KC` as in the spec. Decision/blocker status: `OPEN | PROVISIONAL | OWNER_DECISION_REQUIRED` (never CLOSED/ACCEPTED in this session). Contract status: `draft` (all files this session). Claim labels only from the plan §2 table; the maximum any file may assert this session is `DRAFT_FOR_REVIEW`. Test/evidence results: `PASS | FAIL | BLOCKED | NOT_RUN | STALE | NOT_APPLICABLE`.

**Contract file header.** Every contract/schema/fixture/registry file carries the plan §5 mandatory fields. YAML files: top-level keys. Markdown files: a YAML front-matter block. JSON schema files: `$id`, `title`, `description` plus an `x-contract` object. Minimum fields:

```yaml
contract_id: CT-...
version: 0.1.0
status: draft
owner_role: <role from the plan package "Owner">
source_refs: [SRC-SPEC §…, SRC-PLAN §…]
requirement_refs: [REQ-…]
decision_refs: [B…, AMD-…, ADR-…]
invariant_refs: [I…]
producers: [MOD-…]
consumers: [MOD-…]
dependencies: [CT-… or file paths]
scope: <one paragraph>
verification: <how this file is checked: E0 lint / fixtures / scenarios>
claim_ceiling: DRAFT_FOR_REVIEW
```

Exception (Coordinator ruling R-05, 2026-09-06T18:00Z): ADR files under `precode/adr/` carry an ADR-specific front-matter (`adr_id, title, status, date, decision_owner, source_refs, requirement_refs, decision_refs, affected_packages, supersedes`) instead of the contract header; `precode/requirements.csv` carries its header in `precode/baseline.json.requirements_csv_contract_header`. Fixture JSON files carry the header as an `x-contract` object or in their directory README (README must list every fixture). General rule (ruling on CR-PC00-10, 2026-09-07): tabular files (`*.csv`) carry their header in `precode/baseline.json` under a `<name>_contract_header` object; record-type files (ADRs, task cards under `agent-tasks/`) carry a record-specific front-matter declared in their directory README; any other deviation is declared in the file's `x-contract.deviations`.

**Entity naming authority** (ruling R-03): `contracts/data/entities.yaml` entity names are authoritative; `contracts/modules.yaml.data_owner_of` uses those names. **Operation naming authority**: `contracts/ports.yaml`.

**Wire rules** (plan §5.1) are binding on every schema and operation. **Default deny** (plan §6): any edge not in `contracts/modules.yaml` is forbidden.

**No vagueness.** Every timeout/budget/limit needs a number, a unit and a rationale line; if the number is a guess, label it `PROVISIONAL` with the decision ref, never leave it as "TBD".

**No fabricated verification.** Anything you did not run is `NOT_RUN`. Self-checks are `SELF_VALIDATION`. Never write "independent audit passed".

**No product code, no network, no secrets.** Validation helpers (python3 with PyYAML 6.0.1 and jsonschema 4.10.3, node 22, jq) are allowed for parsing/validating your own files, run from your scratch directory.

## 4. Handoff contract (Workers)

Before HANDOFF: run `sha256sum` on the sources (must still match §2) and on every file you created. Write your HANDOFF to the exact path given in your packet (`evidence/handoffs/<PC>-handoff.md`), containing:

1. packet_id, worker principal, authority_id, lease_id, status (`DONE | DONE_WITH_CONCERNS | BLOCKED | FAILED_PARTIAL | STALE_BASELINE`), completion_claim (max `DRAFT_FOR_REVIEW`)
2. `changes`: table of every created file — path, operation `CREATE`, before `ABSENT`, after sha256, bytes
3. source baselines you relied on (path + sha256)
4. evidence records `EV-<PC>-<nn>`: id, type `SELF_VALIDATION`, exact command, started/ended UTC, input hashes, oracle, expected/observed, exit code, status, limitations
5. checklist from your packet with each item `DONE | PARTIAL | NOT_DONE` and a pointer to where it lives
6. unresolved refs: open questions, `CR-…` change requests to other packages, assumptions labelled PROVISIONAL that you introduced
7. next actor: `Coordinator`; `lease_released_at`: UTC timestamp

Return to the Coordinator (your final message) ONLY: status, list of created paths with byte counts, one-line evidence summary, concerns/CRs. Keep it under 40 lines; the detail lives in the handoff file. After writing the handoff you must not touch any file again.

## 5. Provisional decisions (Coordinator rulings under AUTH-OWNER-20260906-01)

Each row adopts the plan's PC-ĐX. Record them as `PROVISIONAL` with `decision_owner: Owner`.

| ID | Provisional resolution |
| --- | --- |
| B01 | Tag freeze at the report **publish transaction**; report stores an immutable `tag_config_version`; delivery never changes published content. "Thời điểm gửi" in C03 is re-read as "thời điểm publish report". Requires AMD-B01. |
| B02 | Run split into `phase / status / outcome / stop_reason` exactly as plan §8.1; delivery is a separate lifecycle; mapping table old spec enum → new. Requires AMD-B02 (AC-03 wording). |
| B03 | Add `delivery.unknown`; no automatic retry from unknown; AC-14 amended to "no automatic duplicate send; unknown surfaced to operator". Requires AMD-B03. |
| B04 | Coverage ledger independent of displayed reports; pending-item ledger and backfill ledger independent of the period cursor; coverage advances only at publish commit (empty periods included). |
| B05 | Commitment is no duplicate **ingest** (by `x_post_id`), not "never re-read"; re-reading allowed under recovery policy; checkpoint contains only server-ACKed data; X coverage limits stated in run metadata. Requires AMD-B05 (AC-04 wording "không lấy lại bài đã có" → "không ingest trùng"). |
| B06 | Identity model with alias table + merge audit trail; work versions (arXiv vN); target is a tagged union `work | post`. |
| B07 | One valid analysis result per key (target canonical id, source fingerprint, task type, prompt/schema version, generation); reanalysis = new generation; failed/unknown attempts are not results. |
| B08 | One owner-confirmed IANA timezone stored in settings (`PROVISIONAL` default `Asia/Ho_Chi_Minh`); all timestamps UTC RFC 3339 with millisecond precision + ingest sequence tie-break; DST/catch-up rules per PC03. Owner must confirm the timezone. |
| B09 | Narrow linking exception: a message from an unlinked chat that exactly matches the link-code format is validated against unexpired unused codes; everything else from unlinked chats is silently dropped. |
| B10 | `status` is read-only; `run-now` never overrides `needs_user`; resume is a dedicated app action; no fourth Telegram command. Requires AMD-B10 (spec §5.4 step 4). |
| B11 | Backup = SQLite Online Backup API or `VACUUM INTO` consistent snapshot (WAL-safe) + manifest; restore drill with side-effect lock. Requires AMD-B11 (D58 "copy file"). |
| B12 | D09 project-specific Chrome profile adopted; D08 API-only; D42 LLM worker on the personal machine; D50 embedding on server; analysis worker receives tasks from the server **after ingest commit**, never data directly from the collector (spec §6.2 edge COL→AW removed). |
| B13 | Per-task scoped secret access (worker receives only the credential for the assigned task's provider, short-lived); CLI/ACP adapter must run with tools/file/network disabled beyond inference; if isolation cannot be verified for a provider, that adapter stays disabled. |
| B14 | Vector density defined by PC04 (algorithm, window, threshold, min sample); insufficient data → `insufficient_evidence`, never "emerging". Parameters are PROVISIONAL until A4 evaluation. |
| B15 | "0 duplicates" invariant scoped to known canonical identity (DOI/arXiv/normalised); conflicts → `identity_conflict` quarantine, sources kept, no guessed merge. |
| B16 | Analysis output separates `author_claim`, `source_verified`, `ai_inference`; missing comparator recorded as `comparator: unknown`, never invented. |
| B17 | Summary tasks enqueued for targets **selected** by the report builder at build time; report `quality: partial` with explicit pending list when items lack summary; `completed` requires every selected item summarised or explicitly marked pending. |
| Stack | Option A (Python everywhere) PROVISIONAL, used only by PC10 for paths; needs ADR + Owner choice. |
| OQ defaults | N backfill = 7 days (PROVISIONAL); schedule 08:00 and 20:00 owner-local (PROVISIONAL, from spec examples); per-run limit PROVISIONAL 200 posts or 30 min whichever first (owner sets real values after M0); Telegram quiet hours none (PROVISIONAL); Saved export deferred to P1 (PROVISIONAL). |

## 6. Stop gates (all packets)

| Trigger | Status to report | What to do |
| --- | --- | --- |
| Source hash mismatch | STALE_BASELINE | stop, report both hashes |
| You need a file outside your allowlist | BLOCKED_SCOPE | stop; report the exact path and why; do not write |
| A required upstream file (dependency) is missing/unreadable | BLOCKED_DEPENDENCY | stop; name it |
| A product decision outside §5 is needed | do not decide | choose the plan's recommendation if one exists, label PROVISIONAL, record in unresolved refs; if none exists, record `OWNER_DECISION_REQUIRED` and keep the affected scope explicitly blocked in your file |
| Your lease expiry passed | STOPPED_EXPIRED | write handoff with what exists, no further writes |
| Partial failure while writing | FAILED_PARTIAL | list what exists with hashes; do not roll back |
