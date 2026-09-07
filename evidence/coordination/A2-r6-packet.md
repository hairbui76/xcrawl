# REVIEW TASK_PACKET PKT-A2-R6 — Scoped re-review of F-A2R5-01…07 fixes (FC-W4 epoch 9)

- packet_id: `PKT-A2-R6` · assignee: `auditor-A2` · authority `AUTH-COORD-A2-R6` (parent `AUTH-OWNER-20260907-02`) · lease null (read-only)
- report path: `…/scratchpad/audits/A2-R6-report.md` · helpers under `…/scratchpad/a2/` · PYTHONDONTWRITEBYTECODE=1 · no repo writes, no git mutation, no network
- Frozen candidate FC-W4 epoch 9 manifest: `…/scratchpad/audits/FC-W4e9-manifest.txt` (manifest_sha256 in header; the whole `agent_profile/` directory is now included — registry.json CANDIDATE, the rest DEPENDENCY — answering F-A2R5-07). Recompute at start and end.

## Scope
1. For each of F-A2R5-01…07: re-run your reproduction against epoch-9 bytes; verdict VERIFIED | NOT_VERIFIED | PARTIAL. Inputs: rulings `…/scratchpad/packets/FIX-R5-rulings.md`; addenda PC08-FIX4, PC01-FIX14, PC02-FIX10, PC07-FIX5, PC05-FIX6, PC04-FIX6, PC10-FIX11, PC09-FIX8; the closing E0 run under `evidence/runs/` (must pin the frozen bytes — verify `baseline_hashes` against the manifest, the F-A2R5-02 test).
2. Purge-scope consistency: the retained-table list identical (set equality) across entities.yaml TXN-purge-all, ports.yaml, openapi.yaml, secrets.md, backup-restore.md, screens.yaml, scenarios.yaml SC44, recovery fixture l; no OWNER_DECISION_REQUIRED remains for purge scope except as labelled history.
3. Ceiling census: every CONTRACT_READY file is on the E0-12 allowlist and carries a parsed `ratification_ref`; identity/ and reporting/ fixtures now CONTRACT_READY; every other fixture and file DRAFT_FOR_REVIEW; deployment.md carries the scope ruling in its header. Mutations on a scratch copy: M6b (ref moved to prose) must FAIL; out-of-scope CONTRACT_READY must FAIL.
4. Regression sweep limited to the fix diff plus the standard battery (pins 483 rows, epoch `PC10-PIN-OD01c-20260907` unanimous, fixtures/bijection/prose tokens/headers, review numbers reproduce, index.json refs resolve, honesty note correct).
5. Independent E0 re-run (write nothing into the repo), check-for-check vs the registered run.

## Report
Verification table; per-scope CONTRACT_READY verdicts (may each stand unconditionally now?); per-package verdicts; overall verdict; new findings `F-A2R6-nn` (fix-diff only; other observations deferred); residual open items for the Owner (final list). Reply ONLY: overall verdict; per-scope verdicts; verification verdicts one line each; new finding counts; residual open items (≤12 lines); report path (≤35 lines).
