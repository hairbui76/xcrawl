# TASK_PACKET PKT-PC02 — Khóa identity, entity và transaction

- packet_id: `PKT-PC02` · assignee_role: Worker · assignee_principal: `worker-W3`
- authority_id: `AUTH-COORD-PC02` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC02-e1` (exclusive, fencing 1)
- created_at: 2026-09-06T16:55Z · expires_at: 2026-09-07T00:00Z
- enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w3/`

## Goal
Execute plan §11 **PC02**: entity model, canonical identity/alias/merge rules, transaction map, target tagged union, ingest batch schema, and identity fixtures. Resolve B06/B07/B15 provisionally per baseline §5.

## Non-goals
No state machines (PC03), no report/selection semantics (PC04), no HTTP wire (PC05). Do not write `precode/*` or `contracts/modules.yaml`/`ports.yaml` (PC00/PC01 run in parallel). Reference operation IDs using baseline §3 form; if you must name one that PC01 may spell differently, put it in `unresolved refs` as `CR-PC02-nn` so PC09 reconciles.

## Read set
baseline file, SRC-PLAN (esp. §3 B06/B07/B15, §5.1, §7 I02/I03/I04/I08, §9.1, §9.3, §10), SRC-SPEC (esp. §7, §8, §9.2, §12 AC-07/09/12/13), `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/data/entities.yaml` | every entity from spec §7.1 plus the ones the plan requires: `identity_alias`, `identity_merge_audit`, `work_version`, `analysis_generation`/`analysis_attempt`, `saved_snapshot`, `coverage_window` (declare only; PC04 details), `ingest_receipt`, `checkpoint`, `assignment_lease` (declare; PC03 details), `delivery_part`, `outbox_intent`, `pending_item_ledger`, `backfill_ledger`, `embedding_generation`. For each: fields (name, type, nullable, constraints), keys, UNIQUE constraints and **what each UNIQUE does and does not guarantee**, owner module (MOD- ids), `owner_id` present on every data table (D01; single owner, no tenant features), versioning, referential integrity, migration/versioning policy (`schema_version`, additive-only rules). Include `target` tagged union (`kind: work|post`, exactly one id set) and state that UNIQUE(owner, target) for Saved is on the union key. |
| `contracts/data/identity.md` | canonical identity: DOI normalisation (case, prefix, URL forms), arXiv ID normalisation (old/new style, version suffix), which identifiers are canonical vs alias, post-only targets, evidence/provenance retention, `identity_conflict` quarantine semantics, merge algorithm (winner selection rules, what moves: post_work refs, first_announced (PC04 decides policy—state the interface), Saved, analysis), audit trail, non-goals (no fuzzy title merge in MVP → `KC`). Front-matter. |
| `contracts/data/invariants.md` | I02, I03, I04, I08 (and I15 data part) each with: statement, owner contract, positive scenario, ≥1 counterexample that must fail, oracle (row counts/hashes/references), evidence type. Plus any new data invariant (I16+) with justification. |
| `contracts/schemas/target.schema.json` | JSON Schema 2020-12 for the target union + canonical identifier objects. `$id` `https://research-radar.local/schemas/target.schema.json`. |
| `contracts/schemas/ingest-batch.schema.json` | wire schema for an ingest batch mutation (plan §5.1: request_id, schema_version, idempotency_key, payload_hash, job_id, lease_id, lease_epoch, items[], client_checkpoint_proposal, source provenance incl. `x_post_id`, author, url, published_at, text, media refs, thread context, collected_at (worker clock, untrusted)). Include limits (max items, max text bytes) with PROVISIONAL numbers. |
| `acceptance/fixtures/identity/README.md` | fixture index + how each is used |
| `acceptance/fixtures/identity/*.json` | fixtures: (a) merge after ingest: two works discovered separately then linked by DOI↔arXiv; (b) missing IDs → post-only; (c) conflicting IDs → identity_conflict; (d) concurrent Save app/Telegram same target → one Saved; (e) source deleted after Save → snapshot intact; (f) ingest replay same idempotency key → same receipt, counts unchanged; (g) arXiv v1→v2 new version; (h) five posts + author thread same arXiv → one target (AC-07). Each fixture: `given` rows, `events`, `expected` rows/counts/hashes, `forbidden_effects`, `scenario_refs`, `invariant_refs`. |
| `evidence/handoffs/PC02-handoff.md` | HANDOFF |

Directory-scoped grant: `acceptance/fixtures/identity/`. Create `contracts/data/`, `contracts/schemas/`, `acceptance/fixtures/identity/`, `evidence/handoffs/` as needed.

## Checklist (plan PC02)
1. [ ] post / work / post-only / alias / paper version / analysis generation / Saved target / snapshot defined.
2. [ ] Single owner at schema level: keep `owner_id` (D01), no multi-user features.
3. [ ] Transaction map (in entities.yaml `transactions:` or invariants.md): ingest+receipt+checkpoint (one transaction; ACK only after commit; replay returns stored receipt), identity merge, Save (snapshot from the report analysis revision being read), analysis accept (one valid per key; attempt rows separate). For each: rows written together, commit point, what an external observer may see before/after, failure timeline.
4. [ ] Fixtures (a)–(h) above.
5. [ ] Migration/versioning, referential integrity, historical snapshots unchanged after merge (state the rule and the oracle).

## Invariants
I02, I03, I04, I08 must each have oracle + counterexample. Two UNIQUE columns are explicitly stated as insufficient for duplicate resolution (B06). No guessed merges (B15).

## Verification (EV-PC02-nn, SELF_VALIDATION)
- EV-01: YAML parse entities.yaml; JSON parse all fixtures; both schemas validate as Draft 2020-12 metaschemas (`jsonschema.Draft202012Validator.check_schema`).
- EV-02: every fixture's `given`/`expected` target objects validate against target.schema.json; an ingest-batch example (positive) validates and ≥3 negative examples (missing idempotency_key, bad hash format, empty items) are rejected — include the negatives as fixtures too.
- EV-03: every entity referenced in transactions/invariants exists in entities.yaml.
Record commands and results.

## Stop gates
Baseline §6.
