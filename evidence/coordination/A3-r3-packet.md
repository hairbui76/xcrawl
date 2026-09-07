# REVIEW TASK_PACKET PKT-A3-R3 — Quick scoped verification of F-A3R2-01…04 + PC09 registration (FC-P1 epoch 3)

- packet_id: `PKT-A3-R3` · assignee: `auditor-A3` · authority `AUTH-COORD-A3-R3` (parent `AUTH-OWNER-20260907-03`) · lease null (read-only; git-ignored artefacts only; `git status --porcelain` before/after)
- report path: `…/scratchpad/audits/A3-R3-report.md`
- Frozen candidate FC-P1 epoch 3 manifest: `…/scratchpad/audits/FC-P1e3-manifest.txt` (manifest_sha256 in header; includes the copied audit reports under evidence/audits/ as EVIDENCE). Recompute at start and end.

## Scope
1. F-A3R2-01/-04 — change-control entry and amendment block wording now cite rules that exist (or record a deviation with the Coordinator ruling and CR-PC10-13); regeneration claim corrected (entities.yaml not a generator source). Verdict per finding.
2. F-A3R2-02 — `test_schema_matches_entities.py` uses `table_xinfo`, asserts containment in both directions, still checks four traversal orders; run it; mutate a copy (drop one entity field from a scratch copy of entities.yaml or add a column to a scratch DB) to confirm both directions bite.
3. F-A3R2-03 — every card's registered manifest (the newest per card) pins sha256 values that match disk; superseded manifests marked; `evidence/index.json` registers exactly the newest ones plus the INDEPENDENT_AUDIT records citing A3-R1/R2; no stale pin registered.
4. PC09-P1 (F-A3R1-03 DEFERRED → now): `evidence/index.json` valid against the schema; gates.yaml G5 statement matches conditions; traceability/scenarios statuses moved only where an A3 report reproduced them; E0 rule change (claims up to IMPLEMENTATION_VERIFIED only under evidence/ with an A3 citation) — mutate a scratch copy to prove it fails outside evidence/ and without a citation; E0-19 exists and passes; review.md Phase 0/1 section numbers reproduce (test counts 303/4/0, per-card claims as R2 stated).
5. Regression: full suite, ruff, mypy, web, e0, verify_cards @ `PC10-PIN-P1d-20260907`, one alembic head; contracts/acceptance unchanged vs epoch 2 except entities.yaml amendment-block prose (diff it: no field/constraint change).

## Report
Verification table (F-A3R2-01…04 + PC09 items); overall verdict; per-card claims re-stated; residual list (what remains NOT_RUN / KC / open CRs for the next contract round). Reply ONLY: verdict per item, overall, new finding count, report path (≤15 lines).
