# TASK_PACKET PKT-PC07 — Khóa app, Save và Telegram delivery

- packet_id: `PKT-PC07` · assignee_role: Worker · assignee_principal: `worker-W3` (continuation of the PC02 worker; new packet, new lease)
- authority_id: `AUTH-COORD-PC07` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC07-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T08:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w3/`

## Goal
Execute plan §11 **PC07**: screen read-model/action map for every spec §4 screen, Telegram command contract (3 commands + linking lifecycle + B09 exception + B10 rules), delivery contract (outbox, parts, receipts, unknown, AC-14 amendment), Saved snapshot schema, and Telegram fixtures. Resolve B01 (delivery side), B03, B09, B10 provisionally per baseline §5.

## Non-goals
No HTTP wire (PC05 owns openapi; cite operationIds), no state machine files (PC03 owns delivery.yaml; you specify behaviour that must be consistent with it and cite it), no secrets lifecycle (PC08). No visual design (spec §4 says deliberately not fixed). Do not modify earlier packages; raise CR-PC07-nn.

## Read set (frozen; record sha256)
baseline; SRC-PLAN (§3 B01/B03/B09/B10, §3.1 Telegram, §5.1, §6, §7 I08/I09/I13, §8.3, §10, §11 PC07, §13 AC-10/12/13/14/15/18, SC19/SC25); SRC-SPEC (§3.6, §4, §5.3, §5.4, §8.2 rows 7/10, §8.3, §9.1, §9.3, §11.3, §12 AC-10..15, AC-18); PC00 `precode/requirements.csv`, `decision-register.md`, `adr/*`; PC01 `contracts/modules.yaml`, `capabilities.yaml`, `ports.yaml`; PC02 `contracts/data/entities.yaml` (saved_item, saved_snapshot, target union, delivery_part, outbox_intent, telegram_link), `schemas/target.schema.json`; PC03 `contracts/state/run.yaml`, `report.yaml`, `delivery.yaml`, `errors.yaml`, `retry-policy.yaml`; PC04 `contracts/reporting/time-and-tags.md`, `schemas/report.schema.json`; `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/ui/screens.yaml` | per screen (Reports, Report detail, Work detail, Topics, Tag matching preview, Saved, Runs, Run detail, Settings): read_model (fields, source entities, derived fields such as the three distinguishable run states of spec §8.3 with exact labels and the forbidden label "không có nghiên cứu mới"), actions (each → exactly one `ports.yaml` operation_id, auth scope, mobile availability per spec §4 last column), states (loading / empty / partial / error / stale-last-known per PC03 storage.yaml) with exact copy for empty states as the spec dictates (Topics empty ≠ "no new research"), resume action location (B10: Runs/Run detail only), reanalysis action, unsaved-changes and stale-data rules; no direct DB/secret access (I01/I11). |
| `contracts/telegram/commands.yaml` | ingress: update authentication (webhook secret, source validation), replay/dedup by update_id, chat authorisation (linked owner chat only), silent drop rules; B09 linking exception (exact code format regex, expiry PROVISIONAL minutes, one-use, rate limit, invalid → silent); commands: `save` (callback with item ref + report ref + link generation; stale callback → silent or safe reply per rule; validates target exists in that report revision), `run_now` (never overrides needs_user → reply states blocked + points to app resume), `status` (read-only; three states distinguishable in text); unlink (D37; Coordinator ruling on CR-PC01-02: unlink is an **app action** `telegram.unlink`-style op as PC01 named it, not a fourth chat command — D36 XN "3 lệnh" wins over D37 ĐX; record PROVISIONAL, Owner may reverse) and relink lifecycle (new link invalidates old; `link_generation` increments; pending deliveries to old generation → cancelled); no config/tag mutation via chat; response templates (safe text, no secrets, escaping rules referenced to delivery.md); error/edge: unknown callback data, oversized text, duplicate Save presses (5× → one Saved, 5 replies). |
| `contracts/telegram/delivery.md` | Front-matter. Outbox intent created in publish transaction (B01; content frozen = published report revision), payload rendering (digest structure: emerging block + items with short summary + app deep links D04; formatting/length limits per Telegram API as `KC` with URL `https://core.telegram.org/bots/api#sendmessage`, escaping of source text, part splitting with `delivery_part` index + payload hash), send procedure consistent with PC03 delivery.yaml (attempt row before network call; receipt with message id; retry_wait rules; `unknown` after timeout/crash-after-possible-send — no auto resend; operator decision op), AC-14 amendment text (AMD-B03) and the guarantee that replaces "no message sent twice"; alert delivery for needs_user (one intent per run, I09/AC-04); no digest for empty periods (D57); catch-up run covers window in text (D15); quiet hours PROVISIONAL none; Save button payload. |
| `contracts/schemas/saved-snapshot.schema.json` | `$id` `https://research-radar.local/schemas/saved-snapshot.schema.json`: saved_item + immutable snapshot: target (ref target schema `$id`), report ref + analysis revision read at save time (not newer), snapshot content (summary fields, matched tags, evidence level, source posts list with urls/text, work metadata), snapshot_hash (sha256 of canonical JSON — define canonicalisation), saved_at, saved_via `app|telegram`, active flag (unsave keeps snapshot; re-save creates new active row? — decide per I08: at most one active per target; define unsave→re-save behaviour), owner_id. |
| `acceptance/fixtures/telegram/README.md` | index |
| `acceptance/fixtures/telegram/*.json` | (a) multi-part digest, part 2 times out → part 2 unknown, part 1 sent, no resend (SC14/AC-14); (b) response lost after Telegram received → unknown, operator decides (TELEGRAM_SEND_UNCERTAIN); (c) permanent failure → failed, report intact, run outcome unchanged (TELEGRAM_PERMANENT_FAILURE/I09); (d) unlink before send → cancelled; (e) relink → old generation deliveries cancelled, new not auto-sent (SC26); (f) stale callback (report revision/link generation changed) → no Save; (g) link code used twice → second silent + code consumed; (h) unknown chat sends `/status` → no reply, no mutation, outbound calls 0 (AC-18/SC18); (i) unknown chat sends a valid-format code → validated (B09); (j) Save app + Telegram concurrently → one Saved, snapshot from report revision (AC-13/SC13); (k) Save then source deleted → snapshot readable (AC-12/SC12); (l) run_now while needs_user → not resumed, reply points to app (B10); (m) three runs empty/limit/failed → three distinct status texts (AC-15/SC15). Each: given/events/expected/forbidden_effects/scenario_refs/invariant_refs, with expected outbound call counts. |
| `evidence/handoffs/PC07-handoff.md` | HANDOFF |

Create `contracts/ui/`, `contracts/telegram/`, `acceptance/fixtures/telegram/`.

## Checklist (plan PC07)
1. [ ] Every spec §4 screen mapped (read model, actions→operation, auth, mobile, loading/empty/partial/error).
2. [ ] 3 commands; resume location; link/unlink lifecycle; linking exception.
3. [ ] Snapshot from the report analysis revision being read; Save duplicate; unsave/re-save.
4. [ ] Ingress auth/replay, callback validation, recipient generation, OTP expiry/one-use, silent rejection.
5. [ ] Outbox + parts + receipts + unknown; AC-14 policy; payload formatting/escaping as KC with doc URL.
6. [ ] Fixtures (a)–(m).

## Invariants
I08, I09, I13 with positive + counterexample fixtures; report in app independent of delivery; unknown never displayed as sent/failed.

## Verification (EV-PC07-nn, SELF_VALIDATION)
- EV-01: YAML parse; schema metaschema; fixture saved objects validate against saved-snapshot schema (registry with target schema); negative fixture(s) fail.
- EV-02: every action's operation_id exists in ports.yaml; every error code exists in errors.yaml; every delivery state you reference exists in delivery.yaml (script); misses → CR-PC07-nn.
- EV-03: fixture (h)/(i) assert outbound call count 0 / validation path; fixture (a) asserts no resend of unknown part.

## Stop gates
Baseline §6.
