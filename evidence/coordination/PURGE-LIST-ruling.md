# Coordinator ruling — authoritative `data.purge_all` table sets (OD-20260907-01 item 24) — 2026-09-07T05:55Z

Defect (CR-PC05-06): entities.yaml TXN-purge-all listed `schedule_occurrence` in both `purged` and `retained_by_owner_decision`, and purged `worker_registration` and `data_deletion_audit`, which conflicts with ratified items 20/23 (schedule kept; deletion records kept forever) and with the collector's registration being configuration, not research data. Corrected sets (W3 writes them into entities.yaml; every other artefact copies these verbatim):

**purged (37)** (corrected 06:05Z per CR-PC05-07 — `telegram_link_attempt` was named in prose but missing from the enumeration): post, post_work, work, work_version, identity_alias, identity_conflict, identity_merge_audit, work_label, analysis, analysis_generation, analysis_attempt, analysis_task, embedding_generation, tag_vector, report, report_item, emerging_direction, coverage_window, pending_item_ledger, backfill_ledger, first_announced_ledger, rescan_ledger, saved_item, saved_snapshot, delivery, delivery_part, delivery_attempt, delivery_receipt, outbox_intent, run, assignment, assignment_lease, checkpoint, ingest_receipt, source_fetch_log, telegram_update_log, telegram_link_attempt

Coverage check: 37 purged + 21 retained + 2 never_purged = 60 = all entities in entities.yaml; the three sets are pairwise disjoint.

**retained_by_owner_decision (21):** owner, session, secret_ref, task_credential, secret_audit, telegram_link, telegram_link_code, provider_config, provider_test_result, settings, schedule_occurrence, tag, tag_alias, tag_exclusion, tag_config_version, source_connection, backup_snapshot, backup_manifest, restore_record, purge_challenge, worker_registration (reason: collector registration/token binding is configuration; purging would force re-registering the collector and holds no research data)

**never_purged (2):** schema_migration (store structure), data_deletion_audit (deletion records are kept forever per ratified PC08 parameters; the purge writes its own audit row here)

`telegram_link_attempt` (rate-limit counter, 30-day retention): purged — it is operational data, not configuration. Backups and backup artefacts untouched; confirmation dialog states purged data persists in backups.

Header placement for ratified fixtures (F-A2R5-03 / W5's approach): `ratification_ref` and `claim_ceiling` go in the fixture's existing top-level header block, not in a partial `x-contract` object; E0-08 must pass.
