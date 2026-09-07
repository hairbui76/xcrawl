# TASK_PACKET PKT-PC06 — Khóa AI API/CLI/ACP và grounding

- packet_id: `PKT-PC06` · assignee_role: Worker · assignee_principal: `worker-W5` (continuation of the PC04 worker; new packet, new lease)
- authority_id: `AUTH-COORD-PC06` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC06-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T08:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w5/`

## Goal
Execute plan §11 **PC06**: task-specific AI contracts (open labelling, summary D20, emerging-direction phrasing), provider/adapter capability contracts for the two families (API key, CLI/ACP), grounding rules and evidence levels, once-per-generation analysis key, retry budget across worker/adapter, fallback allowlist, CLI/ACP probe protocol, the analysis-result schema, and adversarial fixtures. Resolve B07/B13/B16/B17 provisionally per baseline §5.

## Non-goals
No provider-specific terms-of-service conclusions (A5 = KC; list what must be read). No network. No embedding provider (embedding is local, server-side — reference PC04 selection.md and entities.yaml `embedding_generation`). Do not modify earlier packages; raise CR-PC06-nn.

## Read set (frozen; record sha256)
baseline; SRC-PLAN (§3 B07/B13/B16/B17, §3.1, §5.1, §6, §7 I04/I11/I14, §8.2, §9.3, §10, §11 PC06, §13 AC-06/10/11/16/17); SRC-SPEC (§3.7, §3.8 A5, §10 all, §11.4, §12 AC-06/10/11/16/17); PC00 `precode/requirements.csv`, `decision-register.md`, `adr/*` (ADR-0008, ADR-0010); PC01 `contracts/modules.yaml`, `capabilities.yaml`, `ports.yaml`; PC02 `contracts/data/entities.yaml`, `schemas/target.schema.json`; PC03 `contracts/state/analysis.yaml`, `errors.yaml`, `retry-policy.yaml`; PC04 `contracts/reporting/selection.md`, `schemas/report.schema.json`; `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/ai/tasks.yaml` | one entry per task: `label_open_topics`, `summarize_work` (D20 shape: content / difference from existing / one-line limitation / matched tags line is **data-derived, not AI**), `phrase_emerging_direction` (input = computed density result from PC04; AI only phrases), each with: task_id, model class (cheap/strong per D40), input schema (source ids, source hashes/fingerprint, evidence_level max allowed by what was actually read: `post_only | abstract | full_text`, bounded untrusted-content blocks with delimiters, no secrets), output schema ref (analysis-result.schema.json with task-specific `oneOf`), prompt contract version, schema version, analysis key composition (B07: target canonical id + source fingerprint + task_id + prompt_version + schema_version + generation), reanalysis triggers (manual, new paper version), provider/model switch policy (keep old result until user asks), validation steps (JSON extraction for CLI, schema, semantic checks: citations must reference provided source ids, claim kinds enum, no unsupported evidence level, no field outside schema), retry budget (worker attempts × adapter attempts; total ≤ D43 "one retry" semantic, state exact numbers), timeout, cost/usage recording (`unknown` allowed, never 0), scenario refs. |
| `contracts/ai/providers.yaml` | adapter capability matrix: families `api_key` and `cli_acp`; per adapter template fields: auth family, secret scope (B13: per-task scoped credential, short-lived, delivered via `ports.yaml` op), task support, concurrency (CLI = 1), timeout, cancellation support, JSON extraction method, usage reporting (`exact | unknown`), tool/file/network isolation requirements and **verification method** (adapter disabled if not verifiable), fallback allowlist + ordering (owner-configured, never model-chosen; default off), terms check A5 = KC per provider with "read official docs before enabling"; provider-model-per-task settings shape (D39); zero-API-key path must cover label + summary + emerging phrasing (AC-16). Do not name real provider terms as facts. |
| `contracts/ai/grounding.md` | Front-matter. Evidence levels and max claims allowed; three statement kinds `author_claim | source_verified | ai_inference` (B16); citation targets (source ids only); `comparator: unknown` when no baseline (never invent); X engagement never evidence; non-peer-reviewed label; analysis date vs discovery date display rule; prompt-injection posture (content is data; delimiters; instructions inside content ignored; output constrained by schema; tool requests impossible by construction — adapter has no tools); groundedness rubric (scored fields, pass/fail thresholds PROVISIONAL, human review sampling plan for E4); AI never selects items or computes density. |
| `contracts/schemas/analysis-result.schema.json` | `$id` `https://research-radar.local/schemas/analysis-result.schema.json`; envelope: analysis_key parts, task_id, prompt_version, schema_version, generation, provider/model, evidence_level, usage {tokens_in, tokens_out, cost} each `integer|null` with `unknown: true` flag, `attempt_id`; `oneOf` by task: labels[] {label, confidence, evidence_refs[]}, summary {content, difference_from_existing {text, comparator: ref|unknown}, limitation_line, statements[] {kind enum, text, citation_refs[]}}, emerging_phrasing {text, direction_ref, member_refs[]}. `additionalProperties: false` everywhere. |
| `acceptance/fixtures/ai/README.md` | index |
| `acceptance/fixtures/ai/*.json` | golden + adversarial: (a) post-only summary → evidence_level post_only, novelty statements are ai_inference (AC-11/SC11); (b) instruction injection in post → labels only, no tool/secret, output valid (AC-17/SC17); (c) citation to non-existent source id → AI_OUTPUT_INVALID; (d) schema-valid JSON with no citations → invalid (semantic); (e) transcript containing secret canary → rejected + redaction assertion; (f) tool request in transcript → ignored/rejected; (g) CLI transcript with JSON embedded in prose → extraction success; (h) provider unavailable, no fallback configured → item retry_wait→failed, usage unknown (AI_PROVIDER_UNAVAILABLE); (i) crash after provider completion before submit → unknown_attempt (SC28/AI_ATTEMPT_UNCERTAIN); (j) same key resubmitted → one valid result (I04); (k) zero-API-key run all tasks via CLI (AC-16/SC16 fixture-level). Each with given/events/expected/forbidden_effects/scenario_refs/invariant_refs; positive examples must validate against the schema; negative examples must fail (and say which check). |
| `contracts/ops/cli-acp-probe.md` | Front-matter. Probe protocol per provider/version: what to verify before enabling (policy/terms read = KC, isolation: tool disable flags, sandbox, network egress, filesystem scope, cancellation, timeout behaviour, JSON extraction reliability over N sample prompts, concurrency = 1), pass criteria, evidence to capture, status NOT_RUN, Owner enable decision per provider. Do not infer ACP compatibility from the name. |
| `evidence/handoffs/PC06-handoff.md` | HANDOFF |

Create `contracts/ai/`, `acceptance/fixtures/ai/`.

## Checklist (plan PC06)
1. [ ] Task schemas separated; inputs carry source id/hash/evidence level.
2. [ ] Enums: claim kind, citation target, unknown comparator, unsupported field, max evidence level.
3. [ ] Adapter capabilities per family; usage unknown.
4. [ ] Retry budget across worker/adapter; fallback allowlist/order.
5. [ ] Once-per-generation, reanalysis triggers, provider switch, honest cost logging.
6. [ ] CLI/ACP probe protocol.
7. [ ] Adversarial fixtures (a)–(k).

## Invariants
I04, I11, I14 with positive + counterexample fixtures. No adapter promises just "JSON".

## Verification (EV-PC06-nn, SELF_VALIDATION)
- EV-01: YAML parse; schema metaschema check; positive fixtures validate, negatives fail with the expected validator path (script).
- EV-02: every error code / operation / entity you cite exists (script vs errors.yaml, ports.yaml, entities.yaml); misses → CR-PC06-nn.
- EV-03: analysis key composition in tasks.yaml matches ADR-0008 and entities.yaml `analysis` fields (manual diff recorded).

## Stop gates
Baseline §6.
