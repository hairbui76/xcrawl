# TASK_PACKET PKT-PC05 — Khóa collector và paper connector; thiết kế probe khả thi

- packet_id: `PKT-PC05` · assignee_role: Worker · assignee_principal: `worker-W4` (continuation of the PC03 worker; new packet, new lease)
- authority_id: `AUTH-COORD-PC05` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC05-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T08:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w4/`

## Goal
Execute plan §11 **PC05**: the HTTP wire contract (OpenAPI 3.1) for every `transport: http` operation in `contracts/ports.yaml` (collector, analysis worker, owner UI, Telegram ingress, health), the worker-assignment and ingest-receipt schemas, collector source limits and connector rules, the X feasibility probe protocol (SP1), and offline collection fixtures. Resolve B05/B12 collector aspects.

## Non-goals
No state changes to PC03 files (cite them). No AI task schemas (PC06). No Telegram command semantics (PC07 — but the ingress webhook *wire* is yours; put command semantics by reference). No live X/arXiv/OpenAlex calls; **no network**. Do not pin external doc versions you have not read: mark A5/A6 items `KC` with the exact doc URL from the sources and "to be read at implementation".

## Read set (frozen; record sha256)
baseline; SRC-PLAN (§3 B05/B12, §5.1, §6, §8.1, §9.1, §10, §11 PC05, §12 SP1, §13 SC01–04); SRC-SPEC (§2.3, §3.2, §5.4, §6, §9, §11.2, §13 M0, §13.2); PC00 `precode/requirements.csv`, `decision-register.md`, `adr/*`; PC01 `contracts/modules.yaml`, `capabilities.yaml`, `ports.yaml`, `ops/deployment.md`; PC02 `contracts/data/entities.yaml`, `schemas/target.schema.json`, `schemas/ingest-batch.schema.json`; PC03 `contracts/state/run.yaml`, `analysis.yaml`, `storage.yaml`, `errors.yaml`, `retry-policy.yaml`; `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/http/openapi.yaml` | OpenAPI **3.1.0** (pin the version in `openapi:` and in the header). One path+method per http operation in ports.yaml; `operationId` = ports.yaml operation_id. Security schemes: owner session (cookie or bearer — follow PC01/PC08 choice; if PC08 not yet written, choose bearer session token PROVISIONAL and note), collector token, worker token, telegram webhook secret header. Components: reference JSON schemas by `$ref` to files under `../schemas/*.json` (relative refs), error envelope (from errors.yaml — define `ErrorEnvelope` component matching it exactly), pagination, `Idempotency-Key`/`request_id` headers per plan §5.1, `schema_version` header/field. Every mutation documents: idempotency key scope, payload_hash, lease fields, conflict responses (`IDEMPOTENCY_CONFLICT` 409, `STALE_LEASE` 409/412, `VALIDATION_ERROR` 422, `UNAUTHORIZED` 401, `FORBIDDEN_EDGE` 403, storage `write_blocked` 503 + retry_after), size limits (bytes), timeouts. Include `x-contract` header fields (baseline §3) at top level under `info.x-contract`. Add `x-scenario-refs` per operation. |
| `contracts/schemas/worker-assignment.schema.json` | assignment/claim response: assignment id, run id, phase, lease {id, epoch, ttl_s, heartbeat_interval_s, expires_at}, capability requirements, search config snapshot (tags used only for searching — D24; `tag_config_version` of the search snapshot), stop conditions (limits from settings with units), checkpoint (server-ACKed only: cursor tokens, last ingest_sequence, counts), resume flag, X coverage note. |
| `contracts/schemas/ingest-receipt.schema.json` | receipt: request_id, idempotency_key, payload_hash, status `committed | duplicate_replay`, committed_at (server), counts {received, inserted, deduplicated, quarantined}, accepted item map (x_post_id → post id, discovered_at, ingest_sequence), checkpoint_ack {cursor, last_sequence}, storage_state, warnings; replay semantics stated in `description`. |
| `contracts/ops/collector-probe.md` | Front-matter. SP1/M0 probe protocol per plan PC05 and spec A1/M0: prerequisites (project Chrome profile D09, logged-in session, no CAPTCHA-evasion), 5–10 runs schedule, per-run budget (posts/time PROVISIONAL numbers), stop conditions (challenge, blocked, rate-limit, session expired, budget), what is recorded per run (timestamp, posts seen, new posts, challenge count, blocked count, unobservable scope), file output format (no DB, no AI — M0), go/no-go criteria (numeric PROVISIONAL, e.g. ≥ N successful runs, challenge rate ≤ x), acceptance by the Owner before running, explicit statement that the probe has **not** run and evidence status NOT_RUN; source limits section: author-thread only (D31), no external replies (P1), image-only posts → post-only, no ID guessing (D33), Chrome only X (D32), metadata via server API (arXiv/OpenAlex) with rate/identity requirements listed as `KC` with the official doc URLs from the spec; connector rules: allowlisted hosts only, no model-directed URL fetch, no Chrome control. |
| `acceptance/fixtures/collection/README.md` | index |
| `acceptance/fixtures/collection/*.json` | static/recorded-style fixtures: (a) feed layout change → parser degraded, run stops with `SOURCE_LAYOUT_CHANGED` or blocked reason (register code via CR if absent in errors.yaml); (b) cursor invalid → re-read with dedup, no duplicate ingest (SC03/B05); (c) challenge mid-batch → needs_user, one alert intent, checkpoint = last ACKed (AC-04/SC04); (d) duplicate ingest replay (SC21/INGEST_ACK_LOST); (e) limit reached → stop, checkpoint, phase transition (AC-03/SC03); (f) two workers claim same assignment → second gets STALE_LEASE/epoch reject (SC20); (g) schedule due while online → claim (AC-01/SC01 wire side); (h) metadata unavailable → post-only, no DOI guess (SOURCE_METADATA_UNAVAILABLE). Each fixture: http request/response examples (validate against openapi components), durable rows expected, forbidden effects, scenario_refs, invariant_refs. |
| `evidence/handoffs/PC05-handoff.md` | HANDOFF |

Create `contracts/http/`, `acceptance/fixtures/collection/`.

## Checklist (plan PC05)
1. [ ] claim/heartbeat/ingest/stop/resume operations: payload sizes, provenance, auth — all http ops in ports.yaml covered (script check).
2. [ ] Source limits recorded (author thread, no external replies, no image ID guessing, Chrome only X, metadata via server API).
3. [ ] arXiv/OpenAlex requirements pinned as KC with doc URLs; no unlimited calls (rate budget refs to retry-policy).
4. [ ] Probe protocol 5–10 runs, go/no-go, stop conditions, Owner acceptance gate, NOT_RUN status.
5. [ ] Fixtures (a)–(h); platform tests must not require live X.

## Invariants
I02, I10 (collector part), I11 (connector: no model-directed fetch). Timeout = unknown outcome (plan §5.1). No network call inside a DB transaction.

## Verification (EV-PC05-nn, SELF_VALIDATION)
- EV-01: openapi.yaml parses; structural self-check script: every ports.yaml http operation has exactly one operationId in openapi; every operationId exists in ports.yaml; every `$ref` target file exists; every mutation has idempotency + error responses listed above.
- EV-02: both schemas pass Draft 2020-12 metaschema; fixture request/response bodies validate against the corresponding schema (use jsonschema with a registry of the local schema files).
- EV-03: every error code used exists in errors.yaml; misses → CR-PC05-nn.
(If an OpenAPI validator library is not installed, do not install anything; do the structural checks by script and record the limitation.)

## Stop gates
Baseline §6. Operation names missing in ports.yaml → CR-PC05-nn (do not invent silently).
