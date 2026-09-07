# TASK_PACKET PKT-PC04 — Khóa thời gian, tag, coverage và chọn hướng nghiên cứu

- packet_id: `PKT-PC04` · assignee_role: Worker · assignee_principal: `worker-W5`
- authority_id: `AUTH-COORD-PC04` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC04-e1` (exclusive, fencing 1)
- created_at: (see dispatch message) · expires_at: 2026-09-07T04:00Z
- enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w5/`

## Goal
Execute plan §11 **PC04**: time/tag/coverage semantics (tag freeze at publish, half-open contiguous coverage windows, discovered_at + sequence, pending/late ledger, one-time backfill ledger, manual rescan, first-announcement/reference logic), selection semantics (embedding match, alias/exclusion precedence, thresholds, generation pinning), vector-density "hướng đang nổi" definition, report schema, and reporting fixtures. Resolve B01/B04/B08(time part)/B14/B17 provisionally per baseline §5.

## Non-goals
Do not write state machines (PC03 owns `contracts/state/*` — PC03 runs in parallel with you; both of you derive from plan §8, use its state names verbatim: report `building|published|aborted`, `quality complete|partial`; run `phase/status/outcome/stop_reason`). Do not write AI task schemas (PC06) or UI (PC07). Do not modify PC00–PC02 files; raise `CR-PC04-nn`.

## Read set (frozen; record sha256 of each file you rely on)
- baseline file; SRC-PLAN (esp. §3 B01/B04/B08/B14/B17, §5.1, §7 I05/I06/I07/I12, §8.2, §9.2, §9.3, §10, §13 AC-05/06/08/09), SRC-SPEC (esp. §3.4, §3.5, §5.5, §8, §10.1, §12 AC-05..09).
- PC00: `precode/requirements.csv`, `precode/decision-register.md`, `precode/adr/*`.
- PC01: `contracts/modules.yaml`, `contracts/ports.yaml` (cite operation IDs verbatim).
- PC02: `contracts/data/entities.yaml` (use entity/field names verbatim: coverage_window, pending_item_ledger, backfill_ledger, embedding_generation, work_label, tag_config_version…), `contracts/data/identity.md` (merge interface for first_announced), `contracts/schemas/target.schema.json`.
- `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/reporting/time-and-tags.md` | Front-matter. Sections: (1) timestamps & ordering: UTC RFC 3339 ms, `discovered_at` = server accept time, `ingest_sequence` tie-break, `published_at` distinct; (2) owner timezone (B08) usage for period labels only; (3) tag freeze: `tag_config_version` snapshot at publish transaction (B01), what a tag change before/after publish does, `TAG_VERSION_STALE` rebuild/abort; (4) coverage: `[from, to)` half-open contiguous windows from the authoritative coverage ledger, how `to` is chosen (ingest boundary = max discovered_at/sequence at build snapshot), empty period record, partial period wording ("observed data" only), first period bootstrap, CAS single publisher; (5) pending/late ledger: items discovered in window but lacking analysis → pending, surfaced later with "phát hiện muộn" label, never lost when cursor advances (I06); (6) backfill ledger: N days (PROVISIONAL 7) consumed exactly once per subscription activation; define activation identity and add→remove→re-add rule; crash/model failure does not consume; (7) manual rescan: separate command, separate ledger, never resets first_announced or main coverage; (8) first-announcement: one per canonical work (I07), reference items dated, behaviour after identity merge (take earliest, audit), new paper version, Saved independent of subscription. Each section ends with oracle(s). |
| `contracts/reporting/selection.md` | Front-matter. Selection = data query (no AI): inputs (frozen tag_config_version, active embedding generation, label vectors), alias/exclusion precedence (exclusion wins; alias inherits tag threshold; per-tag threshold override), similarity metric (cosine), threshold policy (global default PROVISIONAL + per-tag; calibration gate A2 → `KC`), generation pinning (I12: never mix generations; block selection with reason `EMBEDDING_GENERATION_MISMATCH`), tie-break/ordering, max items per period (spec §10.4) and overflow → pending, "vector density" definition for emerging directions (B14): algorithm (e.g., density-based grouping over selected + recent label vectors within a comparison window of K prior periods), parameters (window, radius/threshold, min sample size, cold-start rule, tie-break) all PROVISIONAL with A4 gate, output object fields (member targets, density now vs prior, label "ứng viên để đọc sâu"), `insufficient_evidence` result when below min sample — never called "emerging". AI only phrases the computed result (PC06). Include a worked numeric example. |
| `contracts/schemas/report.schema.json` | JSON Schema 2020-12 for the published report read model: report id, coverage_from/to, tag_config_version, selection_version, embedding_generation, quality, items[] (target ref via target.schema.json `$ref` by `$id`, item_type `new|reference`, first_announced_at/report ref for references, matched_tags with scores, analysis_ref/revision, evidence_level, summary fields by reference to PC06 schema id `https://research-radar.local/schemas/analysis-result.schema.json` — reference only, do not define), emerging_directions[] (or `insufficient_evidence`), pending_items[], coverage_note, built_at/published_at, evidence_refs. `$id` `https://research-radar.local/schemas/report.schema.json`. |
| `acceptance/fixtures/reporting/README.md` | index |
| `acceptance/fixtures/reporting/*.json` | fixtures with `given/events/expected/forbidden_effects/scenario_refs/invariant_refs`: (a) tag removed before publish → excluded (AC-05/SC05); (b) tag removed then re-added → same analysis reused, provider calls delta 0 (AC-06/SC06); (c) tag change after publish before Telegram send → published content unchanged (SC19); (d) empty period → coverage record, no digest, no visible report (SC08 part); (e) late analysis → pending then "phát hiện muộn" next period (SC22 part); (f) three offline periods → one catch-up run, one coverage window covering all (AC-02/SC02 reporting side); (g) concurrent publishers → one wins CAS, other rebuilds (SC08); (h) already-announced work → reference with date (AC-09/SC09); (i) identity merge after announcement → single first_announced (SC23 part); (j) backfill add→remove→re-add; (k) builder crash mid-build → backfill not consumed, no partial report; (l) embedding generation switch mid-selection → blocked (SC24); (m) density: below min sample → insufficient_evidence; above → one direction with expected member IDs (worked example numbers). Use timeline tables with explicit UTC timestamps and sequence numbers. |
| `evidence/handoffs/PC04-handoff.md` | HANDOFF |

Create `contracts/reporting/`, `acceptance/fixtures/reporting/` as needed.

## Checklist (plan PC04)
1. [ ] Tag freeze point, coverage boundary, discovered_at/sequence, backlog, single CAS publisher.
2. [ ] Alias/exclusion precedence, similarity metric, threshold policy, embedding generation.
3. [ ] Backfill ledger + manual rescan incl. add/remove/re-add and builder crash.
4. [ ] First-announcement/reference after merge, new paper version, Saved independence.
5. [ ] Vector density: window, min sample, cold-start, tie-break, label; AI phrases only.
6. [ ] Fixtures (a)–(m).

## Invariants
I05, I06, I07, I12 each with owner section, positive fixture and counterexample fixture. Selection stale → rebuild/abort, never mutate published report.

## Verification (EV-PC04-nn, SELF_VALIDATION)
- EV-01: report.schema.json passes Draft 2020-12 metaschema check; every fixture JSON parses; fixture `expected.report` objects (where present) validate against report.schema.json (resolve the target `$ref` by loading PC02's schema into a registry/RefResolver).
- EV-02: worked density example recomputed by a tiny script in your scratch dir (cosine values → expected grouping) and the numbers in selection.md match.
- EV-03: every operation ID and entity name you cite exists in ports.yaml / entities.yaml (script diff; misses → CR-PC04-nn).
- EV-04: coverage fixtures: windows contiguous and half-open by script check.

## Stop gates
Baseline §6. Threshold/density parameters are PROVISIONAL with A2/A4 gates; never mark them validated.
