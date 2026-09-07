# TASK_PACKET PKT-PC03 — Khóa scheduler, lease, checkpoint và state machines

- packet_id: `PKT-PC03` · assignee_role: Worker · assignee_principal: `worker-W4`
- authority_id: `AUTH-COORD-PC03` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC03-e1` (exclusive, fencing 1)
- created_at: (see dispatch message) · expires_at: 2026-09-07T04:00Z
- enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w4/`

## Goal
Execute plan §11 **PC03**: the five state-machine contracts (run, analysis, report, delivery, storage) as transition tables with guards/commit/effects/oracles; the typed error catalogue; the retry/budget policy with concrete numbers; lease/claim/heartbeat/epoch semantics; schedule/timezone/catch-up rules; checkpoint-on-ACKed-data rules; failure timelines. Resolve B02/B05/B08/B10 provisionally per baseline §5.

## Non-goals
Do not define report selection/coverage semantics (PC04 owns `contracts/reporting/*` and `report.schema.json`; you own `contracts/state/report.yaml` = status/quality lifecycle only, referencing PC04 for content rules). Do not define HTTP wire (PC05). Do not modify PC00/PC01/PC02 files; raise `CR-PC03-nn` for needed changes.

## Read set (frozen; record the sha256 of each file you rely on in the handoff)
- baseline file; SRC-PLAN (esp. §3 B02/B05/B08/B10, §5.1, §7, §8 all, §9, §10), SRC-SPEC (esp. §3.3, §5.2, §5.4, §8.2 rows 8–9, §9, §12 AC-01..04, AC-14, AC-15).
- PC00 outputs: `precode/requirements.csv`, `precode/decision-register.md`, `precode/adr/*` (cite REQ/ADR IDs).
- PC01 outputs: `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml`, `contracts/ops/deployment.md` — **use operation IDs exactly as spelled in ports.yaml**.
- PC02 outputs: `contracts/data/entities.yaml`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/schemas/*.json` — use entity/field names exactly.
- `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/state/run.yaml` | `phase`, `status`, `outcome`, `stop_reason` enums exactly as plan §8.1; **mapping table** spec §9.1 old enum → new (queued, collecting, analyzing, reporting, done, needs_user, stopped_limit, failed, failed_partial, delivered, delivered_partial); transition table rows `from / event / guard / to / transaction (rows written together) / effects (allowed side effects, e.g. at most one alert intent per run) / forbidden / oracle / scenario_refs / error_codes`. Must cover every row of plan §8.1 table plus: manual run-now while a run is active (coalesce vs reject), cancel from every non-terminal state, lease expiry in each phase, worker lost, storage write_blocked mid-run. Terminal states listed; assert no terminal state performs side effects. Coverage metadata fields (observed window, limit hit) as separate fields. |
| `contracts/state/analysis.yaml` | item states `pending → running → valid` + `retry_wait`, `failed`, `unknown_attempt`; attempt vs result separation (B07, cite ADR-0008 and entities.yaml); retry budget reference; crash-after-provider-completion timeline; "valid" only after schema+semantic validation (defer semantic rules to PC06 by reference). |
| `contracts/state/report.yaml` | `building → published` + `aborted`; `quality: complete|partial` separate field; publish = CAS transaction (predecessor coverage, tag_config_version, model/embedding generation checks) — reference PC04 for what is checked; `TAG_VERSION_STALE` handling; empty-period behaviour (coverage record, no digest, no visible report). |
| `contracts/state/delivery.yaml` | plan §8.3 table verbatim + `delivery_part` semantics, sender lease, attempt-before-send rule, unknown handling (no auto retry; operator decision op from ports.yaml), unlink/link-generation change → cancelled, budget/backoff numbers by reference to retry-policy. |
| `contracts/state/storage.yaml` | `healthy | write_blocked | maintenance | recovery_required`; entry/exit conditions; what is refused in each state (claims, ACKs, publish, dispatch); readiness channel independent from DB; last-known vs unsaved state for UI; post-restore reconciliation gate (reference PC08). |
| `contracts/errors.yaml` | every error code from plan §10 + generic wire errors (`UNAUTHORIZED`, `FORBIDDEN_EDGE`, `IDEMPOTENCY_CONFLICT`, `STALE_LEASE`, `VALIDATION_ERROR`, `NOT_FOUND`, `RATE_LIMITED`, `CONFLICT`, `INTERNAL`, `CAPABILITY_DENIED` — the last one is CR-PC01-01, accepted by the Coordinator: process/network/tool capability refusal distinct from API-level UNAUTHORIZED, used by modules.yaml denied cases NC-*) and every code named anywhere in `contracts/ports.yaml` / `modules.yaml` (script the diff); fields per code: `scope` (run/item/delivery/storage/request), `retry_class` (`none | retryable_with_budget | needs_user | operator_decision | unknown_outcome`), target state(s) per machine, data kept, forbidden behaviour, oracle/evidence, `message_safe` template, `details_safe` allowed keys, redaction notes, scenario_refs. Error envelope schema per plan §5.1 (inline definition here; PC05 will reference). |
| `contracts/retry-policy.yaml` | named budgets with number+unit+rationale (PROVISIONAL where guessed): lease TTL, heartbeat interval, heartbeat grace, claim timeout, ingest batch max size/attempts/backoff, analysis attempts per item (worker vs adapter split so retries do not multiply; D43 "one retry" preserved), provider unavailable backoff, Telegram send attempts/backoff/max window, research connector rate limits (placeholders referencing A6 as KC), schedule coalescing window, catch-up rules, run-now debounce, storage recovery probe interval. Who retries (server vs worker) for each; when never to retry (unknown outcome, needs_user, blocked). |
| `evidence/handoffs/PC03-handoff.md` | HANDOFF |

Create `contracts/state/` as needed.

## Checklist (plan PC03)
1. [ ] Transition tables with from/event/guard/to/transaction/effect/oracle; old-enum mapping.
2. [ ] Claim/lease TTL/heartbeat/epoch, stale writer rejection (`STALE_LEASE`), cancel, resume (only from needs_user via dedicated op, new lease on claim — B10); every number has unit + reason.
3. [ ] Schedule/timezone (B08: one IANA tz, UTC storage, DST rule: a scheduled local time that does not exist or occurs twice → define deterministic choice), earliest-run semantics (D13), catch-up coalescing (D15/D16: one run, covering window recorded, no old digests re-sent), manual request during active run.
4. [ ] Checkpoint only on ACKed data (I02), replay of lost ACK (`INGEST_ACK_LOST`), stale cursor → re-read + ingest dedup (B05), worker death after external call (uncertainty preserved).
5. [ ] Failure timeline per commit boundary (ingest, checkpoint, analysis accept, publish, send) as a table: t0..tn events, durable rows at each step, what a crash at each step yields, recovery action. Forbidden-transition list (e.g. needs_user → running without resume op; failed → completed; delivery.unknown → sending automatically).

## Invariants
I02, I09, I10, I13 (state part), I15 (dispatch lock after restore) must each appear with owner transition + counterexample. No terminal state emits side effects. No state requires persisting an error into a DB that cannot write without an independent health fallback.

## Verification (EV-PC03-nn, SELF_VALIDATION) — write a small lint script in your scratch dir
- EV-01: YAML parse of all 7 files.
- EV-02: transition lint: every `to`/`from` ∈ declared enums; every event has ≥1 row; every non-terminal state has ≥1 outgoing row; terminal states have no outgoing rows (except explicit "retry via new generation" comment); reachability from initial state to every state.
- EV-03: every error code in errors.yaml maps to ≥1 target state in some machine; every code referenced by state files exists in errors.yaml; every plan §10 code present.
- EV-04: every operation ID you cite exists in `contracts/ports.yaml` (script diff); list misses as CR-PC03-nn.
- EV-05: every budget in retry-policy has number, unit, rationale.

## Stop gates
Baseline §6. If ports.yaml lacks an operation you need (e.g. resume, operator decision on unknown delivery), do NOT invent a differently-named one silently: cite the closest existing ID if semantically identical, else raise `CR-PC03-nn` with the proposed ID and use it with a `pending_cr:` marker.
