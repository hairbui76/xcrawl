# REVIEW TASK_PACKET PKT-A2-R2 — Verification of F-A2R1-01…11 fixes on FC-W4 epoch 5 (whole baseline)

- packet_id: `PKT-A2-R2` · assignee: `auditor-A2` · authority `AUTH-COORD-A2-R2` · lease null (read-only)
- report path: `…/scratchpad/audits/A2-R2-report.md` · helpers under `…/scratchpad/a2/` · PYTHONDONTWRITEBYTECODE=1 · no repo writes, no git mutation, no network
- Frozen candidate FC-W4 epoch 5 manifest: `…/scratchpad/audits/FC-W4e5-manifest.txt` (manifest_sha256 in header). Recompute at start and end.
- completion_ceiling: DRAFT_FOR_REVIEW.

## Inputs
Your own report `A2-R1-report.md`; rulings `…/scratchpad/packets/FIX6-rulings.md`; fix addenda: PC00-FIX5/FIX6 (PC00-handoff), PC01-FIX10 (PC01-handoff), PC02-FIX6 (PC02-handoff), PC09-FIX2 (PC09-handoff), PC10-FIX3 (PC10-handoff); the new E0 run under `evidence/runs/`.

## Method
1. For each F-A2R1-01…11: re-run your original reproduction against epoch-5 bytes; verdict VERIFIED | NOT_VERIFIED | PARTIAL with evidence. Judge whether a divergence from the ruling still satisfies the remediation constraint (e.g. W1's `PROJECT` anchor group for I16/I17; CR-PC01-09 approved by ruling rather than by a new code table).
2. Regression sweep (your own scripts, not the fixing side's): manifest completeness vs handoff change tables; entity↔owner set diff; fixture-actor-edge incl. `operation: null` ⇒ `event_type`; denied-edge bijection with callee-owns-operation; field-existence (rows[] fixtures) with `_` rule; prose operation/error-code tokens across contracts/ and acceptance/ (the new E0-04b class); REQ/SC/I/B/ADR/AMD id resolution across precode/, contracts/, acceptance/, agent-tasks/; card pins recompute (all rows) and epoch names consistent in precode/README.md, agent-tasks/README.md, precode/review.md; review.md headline numbers vs artefacts (recount transitions, fixtures, READY/BLOCKED, DoR, CR count/status coverage = 75+); claim labels; B01–B17 PROVISIONAL; no TBD/CLOSED/ACCEPTED status.
3. Independently re-run `evidence/tools/e0_check.py` from your scratch dir writing nothing into the repo; compare with the registered run check-for-check.
4. Re-state the DoR table and the per-scope CONTRACT_READY-upon-ratification view with any changes since R1.

## Report
Same structure as R1 plus a verification table for F-A2R1-01…11 and a "residual open items" list (KC/BLOCKED/OWNER_DECISION_REQUIRED) that the Coordinator will carry verbatim into the final report to the Owner. Reply to the Coordinator ONLY: overall verdict; per-package verdicts; verification verdicts one line each; new finding counts by severity; residual open items list (one line each); CONTRACT_READY-upon-ratification scopes; report path (≤35 lines).
