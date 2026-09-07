# Coordinator rulings — FIX3 wave (after AUDIT_REPORT PKT-A1-R2 on FC-W2 epoch 2, and CRs from PC03/PC04/PC08) — 2026-09-06T19:05Z

Report: `…/scratchpad/audits/A1-R2-report.md`. Findings stay OPEN → FIX_PROPOSED; A1 verifies at the next freeze. Naming authorities unchanged: entities.yaml (entities/fields), ports.yaml (operations), errors.yaml (codes).

## Field-level names fixed now (so parallel packages converge) — PC02 FIX3 implements; PC03/PC04/PC05 cite exactly
| Entity | Field / constraint | Ruling |
| --- | --- | --- |
| `report` | `report_build_id` | string (UUIDv4), NOT NULL, `UNIQUE(owner_id, report_build_id)`; the `report.publish` idempotency anchor (F-A1R2-01) |
| `report` | `abort_reason` | enum `empty_period \| tag_version_stale \| embedding_generation_mismatch \| cas_conflict \| builder_failure \| cancelled`, nullable, CHECK: NOT NULL iff `status='aborted'` (CR-PC04-09, CR-PC04-08) |
| `coverage_window` | `ingest_sequence_from`, `ingest_sequence_to` | integers, half-open on ingest sequence, contiguous with predecessor (CR-PC04-01) |
| `backfill_ledger` | `subscription_identity_hash` | sha256 hex of `owner_id + "\n" + normalised tag text` (normalisation per PC04 §6.2); NOT NULL |
| `backfill_ledger` | `entitlement`, `entitlement_reason` | enum `granted \| consumed \| denied_already_consumed`; free text; partial `UNIQUE(owner_id, subscription_identity_hash) WHERE consumed_in_report_id IS NOT NULL` (CR-PC04-02, F-A1R2-03) |
| `run` | 16 additive columns per `contracts/state/run.yaml §3` | add verbatim (CR-PC03-03) |
| `delivery_part` | `state` | add `sending` (CR-PC03-07) |
| `restore_record` | `operator_ack_at`, `operator_ack_principal`, `operator_ack_note` | nullable; clause 7 of reconciliation (CR-PC08-05) |
| `backup_manifest` | `embedding_model_artifact_sha256` | nullable string (CR-PC08-05) |
| TXN-ingest-batch | clock clamp | `discovered_at` = server clock; if server clock < last committed `discovered_at` for the owner, clamp to that value + 1 ms and increment sequence (CR-PC04-03) |

## Error codes (PC03 FIX1 registers; PC05 FIX1 maps)
- `CSRF_REJECTED`: HTTP 403, scope request, retry_class none, no state change; missing/invalid CSRF token on an owner-session mutation (CR-PC08-03). `FORBIDDEN_EDGE` stays "edge not in registry"; `UNAUTHORIZED` stays "principal class not allowed / identity not established" (CR-PC08-04 accepted: collector token → Save = UNAUTHORIZED 401).

## Operations (PC01 FIX3)
- CR-PC03-01: replace the non-existent `REQ-S8.4-01` citation with the correct requirement id(s) from requirements.csv (storage/disk-full → REQ-S9.3-*; check).
- CR-PC03-02: `run.resume` guard extended: allowed from `needs_user` (after challenge cleared) and from `blocked` (owner declares the blocking condition cleared, `unblock_reason` required); never from other states. Document in ports.yaml; PC03 FIX1 adds the transition row.
- CR-PC03-05: task_type enum in ports.yaml/capabilities.yaml renamed to entities.yaml spelling.
- CR-PC04-04: `report.publish.error_codes` += `CONFLICT`.
- F-A1R2-06: `data.purge_all.scenario_refs: [SC44]`.
- CR-PC08-02: `backup.*` carry `backupOperatorToken`; every owner mutation carries cookie+CSRF (PC05 confirms in its fix; PC01 states in ports.yaml auth_scope if missing).

## Scenario IDs registered (PC00 FIX2 anchors; PC09 writes them)
SC33–SC36 (PC03), SC37–SC38 (PC04), SC39–SC43 (PC08), **SC44** = `data.purge_all` two-phase confirmation + maintenance precondition + lease revocation + negatives. Remove the stray `SC29+` anchor (F-A1R2-05). PC05/PC06/PC07 take SC45+ if needed (state in handoff).

## Fixtures (rule binding on every package from now)
Before handoff, any package that writes fixtures runs the fixture-actor-edge check (actor ∈ ports.yaml caller_modules and (caller, owner, op) ∈ allowed_edges; `performed_by` = executing service, defined in the directory README, never a caller assertion) and a field-level existence check for every column named in `expected.rows`; unresolved columns carry an in-file `pending_cr: CR-…` marker. PC04 FIX1 applies this to its 13 fixtures (F-A1R2-02/-03).

## PC03 FIX1
F-A1R2-04 (CP-07 wording → append one new checkpoint row, cite CR-PC02-12), CR-PC04-08 (abort_reason on T-RP-03…07), CR-PC03-02 transition row (blocked → queued via `run.resume` guard), register `CSRF_REJECTED`, cite `report.report_build_id` in `publish_cas`.

## PC00 FIX2
F-A1R2-05; anchors SC33–SC44; append new PROVISIONAL decisions and Owner questions raised by PC03 (schedule_timezone real value, per-run limits, schedule slots), PC04 (8 items in its handoff §7.3, incl. backfill keyed by normalised tag text, threshold PROVISIONAL_BOOTSTRAP, empty-period option (b)), PC08 (purge exclusions consequences, RPO/RTO, retention, auth mechanism) to `precode/decision-register.md` and `precode/owner-decision-request.md`; add `CSRF_REJECTED` / `data.purge_all` / `run.resume`-from-blocked as PROVISIONAL decisions.
