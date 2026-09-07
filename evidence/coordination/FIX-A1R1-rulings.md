# Coordinator rulings on AUDIT_REPORT PKT-A1-R1 (FC-W1 epoch 1) — 2026-09-06T18:00Z

Report: `…/scratchpad/audits/A1-R1-report.md`. All findings stay OPEN → FIX_PROPOSED after these packets; A1 verifies on the next freeze (FC-W1 epoch 2). Nothing here closes a finding.

## R-01 (F-A1R1-01, checkpoint) — option (b)
- Exactly one entity: **`checkpoint`** (PC02 name), owned by **`MOD-ingest-service`**. PC01 tokens `ingest_checkpoint` → `checkpoint`; `run_checkpoint_pointer` removed from `MOD-job-service` (job-service reads checkpoint state through `worker.claim_assignment` / an internal read port, never owns it).
- `ingest.submit_batch` remains the primary path: the batch's `client_checkpoint_proposal` is committed in the same transaction as posts + receipt (PC02 `TXN-ingest-batch`).
- `ingest.commit_checkpoint` **survives but is restricted to a cursor-only advance with no new items** (empty page / end-of-feed / segment close). Guard: the proposed cursor may only reference `ingest_sequence ≤ acked_through_ingest_sequence` already committed for that run; a proposal beyond it → `VALIDATION_ERROR` (no partial write). Transaction: single row update of `checkpoint` + receipt; commit point; failure timeline; oracle: after any sequence of `commit_checkpoint` calls, `checkpoint.acked_through ≤ max(committed ingest_receipt.sequence)` — a checkpoint can never point past durable posts.
- PC02 rewords I02 counterexample 2 to condemn "checkpoint that references or advances past posts not yet committed / written in a separate transaction **before** the batch commit", and adds `TXN-checkpoint-only` to the transaction map with the oracle above.

## R-02 (F-A1R1-02, fixture actors)
Every `events[].actor` must be an allowed caller of the operation per `ports.yaml.caller_modules` and `modules.yaml.allowed_edges`. Fix the 10 events (research metadata fetch is called by `MOD-ingest-service`; `identity.merge_works` by ingest/identity; `identity.resolve_target` by ingest/report; `analysis.request_reanalysis` by `MOD-web-ui`; `ingest.submit_batch` by `MOD-x-collector`). Where the fixture really means "the service executing the transaction", use a separate key `performed_by` defined in the fixture README as *not* a caller assertion. Automated gate: PC09 e0_check item (already required; make it explicit as check "fixture-actor-edge").

## R-03 (F-A1R1-03, naming authority) — PC02 entity names are authoritative
PC01 `data_owner_of` token → ruling:

| PC01 token | Ruling |
| --- | --- |
| `work_alias` | rename → `identity_alias` (MOD-identity-service) |
| `ingest_checkpoint` | rename → `checkpoint` (MOD-ingest-service) |
| `run_checkpoint_pointer` | remove (see R-01) |
| `lease` | rename → `assignment_lease` (MOD-job-service) |
| `coverage_ledger` | rename → `coverage_window` (MOD-report-service) |
| `vector` | rename → `tag_vector` (MOD-embedding-service) |
| `sqlite_database_file`, `wal`, `readiness_snapshot_in_memory` | keep but mark `kind: artifact` (not an entity; excluded from entity↔owner check) |
| `session`, `provider_config`, `provider_test_result`, `rescan_ledger`, `schedule_occurrence`, `assignment`, `worker_registration`, `source_fetch_log`, `analysis_task`, `first_announced_ledger`, `delivery_attempt`, `delivery_receipt`, `telegram_link_code`, `telegram_update_log`, `secret_ref`, `task_credential`, `secret_audit`, `backup_snapshot`, `backup_manifest`, `restore_record` | keep token; **PC02 adds an entity contract for each** (declare-level: purpose, fields with types/nullability, keys/UNIQUE + what it guarantees, owner_module = PC01 owner, refs). `first_announced_ledger` must expose the I07 interface PC04 needs (canonical_work_id UNIQUE, first_report_id, first_announced_at, merge audit ref). |

Unowned PC02 entities → PC01 adds to `data_owner_of`: `identity_alias`, `identity_merge_audit` → MOD-identity-service; `checkpoint` → MOD-ingest-service; `assignment_lease` → MOD-job-service; `coverage_window` → MOD-report-service; `tag_vector` → MOD-embedding-service; `source_connection` → MOD-settings-service; `outbox_intent` → MOD-delivery-service; `schema_migration` → MOD-data-store.
Verification in both fix packets: set-comparison script, both directions, zero diff (artifacts excluded).

## R-04 (F-A1R1-04, three delete operations — REQ-S7.3-05 XN)
PC01 adds two owner-only http mutations: `data.delete_target` (delete original post/work data for one target; keeps `saved_snapshot` rows (D55) and ledgers; requires explicit confirmation flag; transaction + error map; scenario ref new `SC32`) and `data.purge_all` (delete all data; requires typed confirmation phrase field matching a server-issued challenge; only in `storage.maintenance`; revokes leases; PROVISIONAL semantics for what "all" excludes — e.g. settings/secrets — flagged `OWNER_DECISION_REQUIRED` for those exclusions only). `save.remove.requirement_refs` → `REQ-S7.3-05`. `PROV-PC01-03` rewritten to name both.

## R-05 (F-A1R1-05, ADR headers) — declared exception
ADRs are decision records, not contracts: exempt from the full baseline §3 header. Required ADR front-matter: `adr_id, title, status, date, decision_owner, source_refs, requirement_refs, decision_refs (B/AMD), affected_packages, supersedes`. PC00 declares the exception in `precode/adr/README.md` and its handoff addendum; the Coordinator amends baseline §3 accordingly.

## R-06..R-09 (MINOR)
- F-06: `precode/baseline.json.requirements_csv_contract_header` gains `requirement_refs`; handoff text corrected.
- F-07: PC01 `capabilities.yaml` `item_fields` → structured `{name, type, values, required}` list; add shape assertion to the EV script.
- F-08: `precode/baseline.json` anchors SC19–SC28 individually with plan §13 subjects (order: SC19 tag change after publish before delivery; SC20 stale lease; SC21 ingest ACK lost; SC22 late analysis/backfill crash; SC23 identity conflict; SC24 embedding generation switch; SC25 Telegram relink; SC26 disk full; SC27 restore with old outbox; SC28 worker dies after AI call). Also register SC29 post-only target, SC30 arXiv new version, SC31 ingest-batch schema rejection, SC32 delete-target (from R-04) as anchors `SRC-PLAN:§13-extra`.
- F-09: `REQ-S4-05` notes cross-reference `F-PC00-02` / `REQ-OQ10` (export deferred to P1); similarly ensure `REQ-D37` carries `F-PC00-01`.
