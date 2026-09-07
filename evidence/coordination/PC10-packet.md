# TASK_PACKET PKT-PC10 — Tạo task card cho coding và giao bộ hợp đồng

- packet_id: `PKT-PC10` · assignee_role: Worker · assignee_principal: `worker-W7`
- authority_id: `AUTH-COORD-PC10` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC10-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T12:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w7/`

## Goal
Execute plan §11 **PC10**: the task-card template, one card per independently verifiable deliverable (plan §15 examples at minimum), change-control policy, and the Pre-code README (entry point + how to navigate/validate the baseline). Stack: Option A (Python) is PROVISIONAL (ADR-0006, Owner decision); cards therefore carry **conditional** implementation/test paths under "if ADR-0006 accepted" and state that coding must not start until G5 and Owner go-ahead.

## Non-goals
No coding. No modification of other packages (raise CR-PC10-nn). No stack decision on the Owner's behalf beyond the PROVISIONAL label. Do not write `precode/review.md`/`gates.yaml` (PC09, parallel).

## Read set (frozen at dispatch; manifest path given in dispatch)
Everything under `precode/`, `contracts/`, `acceptance/`, `evidence/handoffs/`; baseline; SRC-PLAN (§4, §11 PC10, §12 G5, §15, §16, §17); SRC-SPEC (§6.3, §13); `agent_profile/*`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `agent-tasks/TEMPLATE.md` | plan §15 ten sections exactly: Task ID/goal/non-goals; read set (spec refs, ADR, contract versions+sha256, fixtures); write set (paths after stack; shared contract files read-only); consumes/produces (exact operation IDs, schemas, state effects); allowed communication (module/capability allowlist, denied paths); invariants & transaction; error obligations; verification (scenario IDs, commands, oracle, evidence artifacts, live requirement); completion ceiling; stop-and-report conditions. Plus baseline pin block (spec sha256, contract hashes), reviewer scope, dependencies, expected evidence manifest id. |
| `agent-tasks/README.md` | how cards are issued (via Coordinator/Worker protocol), ordering by milestone M1–M8 (spec §13) and gates, dependency graph, rule that cards pin contract hashes and go STALE on change. |
| `agent-tasks/TC-*.md` | at least: `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-scheduler-lease-claim`, `TC-collector-checkpoint-resume`, `TC-analysis-adapter-validation`, `TC-analysis-once-per-generation`, `TC-embedding-generation-switch`, `TC-report-coverage-publish-cas`, `TC-backfill-pending-ledger`, `TC-saved-snapshot`, `TC-telegram-linking-auth`, `TC-telegram-unknown-delivery`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`, `TC-backup-restore-drill`, `TC-ui-runs-three-states`, `TC-ui-reports-detail`, `TC-x-feasibility-probe` (SP1 card: probe only, output = evidence). Each filled per TEMPLATE with real contract paths + sha256 (compute with sha256sum), operation IDs from ports.yaml, scenario IDs from `acceptance/scenarios.yaml` (if PC09 has not finished when you start, cite SC IDs from the plan §13 numbering and mark `pending PC09`), conditional paths for stack A (e.g. `server/app/ingest/…`, `tests/contract/…` — mark PROVISIONAL), proof obligations, stop conditions, claim ceiling `IMPLEMENTATION_VERIFIED` max for code cards, `LIVE_FEASIBILITY_VERIFIED` (probe) for SP1 card, reviewer scope. No card is "build the whole backend/UI". |
| `precode/change-control.md` | Front-matter. Plan §16 rules made operational: CR format (id, source, before/after, reason, affected REQ/contracts/modules/fixtures/evidence, migration), version bump rules for schema/enum/semantics/auth changes, invalidation matrix (which change STALEs which evidence — align with `precode/gates.yaml` if present, else state and CR), one-time Owner acceptance for whole impact scope, baseline replacement for running tasks after impact review, audit retention of old versions, how CR-* raised during Pre-code are dispositioned (proposal only). |
| `precode/README.md` | entry point: what this baseline is, status `NOT_READY_FOR_PRODUCT_CODE` / claim `DRAFT_FOR_REVIEW`, directory map of every plan §4 group with actual files, how to run E0 (`evidence/tools/e0_check.py` — cite; if absent at your start, say "provided by PC09"), where the Owner decision request is, how to read gates/review, how to issue a card, what must never be done (edit sources, close blockers without Owner, start coding before G5). |
| `evidence/handoffs/PC10-handoff.md` | HANDOFF |

Directory grant: `agent-tasks/`.

## Checklist (plan PC10)
1. [ ] Stack recorded as PROVISIONAL via ADR-0006; conditional paths per card.
2. [ ] Cards split by independently verifiable deliverable.
3. [ ] Contract versions/hashes, allowed files, imports/edges, consumed/produced ops, proof obligations on every card.
4. [ ] Stop conditions, dependencies, reviewer scope, expected evidence, max claim on every card.
5. [ ] Walkthrough (write it into README or a `agent-tasks/WALKTHROUGH.md` — allowed under the directory grant) for one collector card and one delivery card: can an agent with only the card + references work without guessing communication/state? List every gap found as CR-PC10-nn.

## Verification (EV-PC10-nn, SELF_VALIDATION)
- EV-01: every hash on every card recomputed by script and matches the file; every operation id / SC id / contract path cited exists (script); misses → CR.
- EV-02: every card has all ten TEMPLATE sections (script).

## Stop gates
Baseline §6.
