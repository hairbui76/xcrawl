# REVIEW TASK_PACKET PKT-A2-R3 — Scoped re-review of F-A2R2-01…04 fixes (FC-W4 epoch 6)

- packet_id: `PKT-A2-R3` · assignee: `auditor-A2` · authority `AUTH-COORD-A2-R3` · lease null (read-only)
- report path: `…/scratchpad/audits/A2-R3-report.md` · helpers under `…/scratchpad/a2/` · PYTHONDONTWRITEBYTECODE=1 · no repo writes, no git mutation, no network
- Frozen candidate FC-W4 epoch 6 manifest: `…/scratchpad/audits/FC-W4e6-manifest.txt` (manifest_sha256 in header). Recompute at start and end.
- completion_ceiling: DRAFT_FOR_REVIEW. This is the scoped re-review that closes the final review loop; no broad re-audit.

## Scope
1. For F-A2R2-01, -02, -03, -04 (and the PARTIAL F-A2R1-03): re-run your reproduction against epoch-6 bytes; verdict VERIFIED | NOT_VERIFIED | PARTIAL with evidence. Inputs: addenda PC01-FIX12 (PC01-handoff), PC09-FIX5 (PC09-handoff), PC10-FIX6 (PC10-handoff); the closing E0 run under `evidence/runs/`.
2. Regression check limited to the fix diff: modules.yaml (five denied cases), boundary fixture (if changed), review.md, gates.yaml, index.json, e0_check.py E0-10b, evidence/runs additions, card pins (recompute all rows; epoch names consistent across precode/README.md, agent-tasks/README.md, review.md).
3. Independent E0 re-run from your scratch dir (write nothing into the repo); compare check-for-check with the registered closing run; confirm the E0-10b promotion by mutating one denied case on a scratch copy.
4. New breakage in the fix diff only → findings `F-A2R3-nn`; out-of-scope observations go to a "deferred" list, not findings.

## Report
Verification table; per-package verdicts unchanged unless the fix diff changed them; overall verdict; residual open items list (re-state your R2 list with any changes); CONTRACT_READY-upon-ratification scopes (re-state). Reply to the Coordinator ONLY: overall verdict; verification verdicts one line each; new finding counts; residual open items (one line each, ≤15); report path (≤30 lines).
