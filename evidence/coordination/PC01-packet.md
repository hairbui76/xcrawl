# TASK_PACKET PKT-PC01 — Khóa topology, ownership và capability

- packet_id: `PKT-PC01` · assignee_role: Worker · assignee_principal: `worker-W2`
- authority_id: `AUTH-COORD-PC01` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC01-e1` (exclusive, fencing 1)
- created_at: 2026-09-06T16:55Z · expires_at: 2026-09-07T00:00Z
- enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w2/`

## Goal
Execute plan §11 **PC01**: module registry with owners/locations/edges, capability & secret/network scopes, the **complete operation inventory** (ports), and the deployment/readiness contract. Close D08/D42/D50/D09 provisionally per baseline §5 B12/B13.

## Non-goals
No HTTP wire schemas (PC05 owns `contracts/http/openapi.yaml`), no state machines (PC03), no secrets lifecycle detail (PC08 owns `contracts/ops/secrets.md`). Do not write `precode/*` (PC00 runs in parallel; reference its IDs by the convention in baseline §3 — you do not need its files to exist).

## Read set
- baseline file `…/scratchpad/packets/00-coordination-baseline.md` (binding), SRC-PLAN, SRC-SPEC (full), `agent_profile/worker.md`, `protocol.md`, `registry.json`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/modules.yaml` | module registry: `MOD-*` id, runs_on (server/personal_machine), process placement (modular monolith allowed), data_owner_of (tables/entities), inbound_operations, outbound_operations, allowed_edges (caller→callee→operation), **forbidden_edges** with reason, auth_scope per actor, network egress allowlist, secret access (none / scoped / owner). Must cover every row of plan §6 and spec §6.1 and the negative cases in PC01 checklist. |
| `contracts/capabilities.yaml` | per actor/principal (web session owner, collector token, analysis worker token, Telegram adapter, backup operator, scheduler, embedding service, research connector, AI adapter): capabilities granted/denied, secret scope, network scope, filesystem scope (Chrome profile, config file), tool scope (CLI adapter: inference only), readiness/capability registration payload (what a local worker reports: collector online, chrome profile ready, X session state, CLI provider usable yes/no/unknown, embedding not on worker). |
| `contracts/ports.yaml` | the single **operation inventory**: `operation_id` (baseline §3 form), transport (`http` or `internal`), owner module, caller modules, auth_scope, mutation yes/no, idempotency requirement, brief request/response summary (schemas are defined later; reference planned schema file names from plan §4), state effects summary, error codes it may return (plan §10 names + `UNAUTHORIZED`, `IDEMPOTENCY_CONFLICT`, `STALE_LEASE`, `VALIDATION_ERROR`, `NOT_FOUND`), scenario refs. Must include at least: auth login/logout/session; settings read/update; tag CRUD + preview matches + rescan; run list/detail/run_now/resume/cancel; worker claim/heartbeat/ingest_batch/checkpoint/report_stop (challenge, limit, blocked)/release; research metadata fetch (internal); analysis claim/heartbeat/submit_result/report_attempt_unknown; embedding generate/generation switch (internal); report build/publish/list/detail; save create/unsave/list/export(P1 flagged); telegram ingress webhook/update, link code issue/consume, unlink, send intent/outbox dispatch, receipt record; delivery status/operator decide unknown; backup create/restore/verify/reconcile; health/readiness. Each is stable — later packages cite them verbatim. |
| `contracts/ops/deployment.md` | where each module runs, Docker vs host process, ports/bindings (Chrome debug loopback only), outbound-only connectivity from personal machine, readiness definitions per module, startup ordering, what "collector online" means, capability registration flow, upgrade/compat note (schema_version). Front-matter per baseline §3. |
| `evidence/handoffs/PC01-handoff.md` | HANDOFF |

Create `contracts/`, `contracts/ops/`, `evidence/handoffs/` as needed.

## Checklist (plan PC01)
1. [ ] Module IDs, run location, data owner, inbound/outbound operation IDs, forbidden edges — every row of plan §6 table represented, plus embedding, scheduler, job service, secret service, repository ports.
2. [ ] D08/D42/D50 provisionally closed per baseline §5 B12; analysis input path = server task after ingest commit; record `decision_refs: [B12, ADR-0001]` (ADR written by PC00 in parallel; cite by ID).
3. [ ] Actor owners: browser owner session, collector, analysis worker, Telegram dispatcher, backup operator, scheduler — distinct auth scopes; no actor has more than one owner role for a mutation.
4. [ ] Readiness/capability registration for local workers, including CLI provider usability (`usable | unusable | unknown`) and reasons.
5. [ ] Negative cases matrix (in modules.yaml `denied_cases` or a section in deployment.md): collector calls Save; worker changes tag; frontend reads secret; adapter sends Telegram; collector writes SQLite; Telegram adapter changes config; AI adapter fetches URLs; research connector drives Chrome; scheduler sends digest; backup operator resumes dispatcher automatically. Each with expected error code and enforcement mechanism (import rule / API auth test / process capability).

## Invariants
- Default deny: an edge absent from `allowed_edges` is forbidden. State this in the file.
- I01, I11 must be traceable to specific edges/capabilities.
- Every operation_id unique; every operation's owner module owns the data it mutates (one owner per mutation).

## Verification (EV-PC01-nn, SELF_VALIDATION)
- EV-01: YAML parses (python3 yaml.safe_load) for all three YAML files.
- EV-02: script: every operation referenced in modules.yaml exists in ports.yaml and vice versa; every module referenced in ports.yaml exists in modules.yaml; no duplicate operation_id; every forbidden edge has a reason.
- EV-03: negative-case matrix covers all ten cases above.
Record commands and results.

## Stop gates
Baseline §6. If you need an operation whose ownership is a genuine product decision not covered by baseline §5, choose the plan's default, mark PROVISIONAL, list in unresolved refs.
