# REVIEW TASK_PACKET PKT-A2-R5 — Verification of the Owner-ratification changes (FC-W4 epoch 8)

- packet_id: `PKT-A2-R5` · assignee: `auditor-A2` · authority `AUTH-COORD-A2-R5` (parent `AUTH-OWNER-20260907-02`) · lease null (read-only)
- report path: `…/scratchpad/audits/A2-R5-report.md` · helpers under `…/scratchpad/a2/` · PYTHONDONTWRITEBYTECODE=1 · no repo writes, no git mutation, no network
- Frozen candidate FC-W4 epoch 8 manifest: `…/scratchpad/audits/FC-W4e8-manifest.txt` (manifest_sha256 in header). Recompute at start and end.

## What changed and why
The Owner answered the decision request in a structured interview on 2026-09-07 (record: `…/scratchpad/packets/OWNER-DECISIONS-20260907.md`, to be transcribed as `precode/owner-decisions.md`, decision id OD-20260907-01, authority AUTH-OWNER-20260907-02). Notable answers: stack = **B** (not the provisional A); `data.purge_all` = research data only, backups kept; timezone Asia/Ho_Chi_Minh confirmed; REQ-OQ03 (provider/model) deliberately left undecided; everything else = the recommended option. Packets applied: PC00-FIX10, PC01-FIX13, PC02-FIX9, PC03-FIX6, PC04-FIX5, PC10-FIX8, PC09-FIX7.

## Method
1. **Fidelity of transcription**: compare `precode/owner-decisions.md` row by row with the Coordinator's record; any deviation is a finding (the Worker was told to transcribe, not reinterpret). Check that REQ-OQ03 remains OWNER_DECISION_REQUIRED and that nothing KC was upgraded on the strength of a decision.
2. **Ceiling discipline**: every file with `claim_ceiling: CONTRACT_READY` (a) lies inside one of the four eligible scopes named in your R2/R3 reports, (b) carries `ratification_ref: OD-20260907-01` resolving to the record, (c) has no remaining dependency on a KC item without a per-item note, (d) states that runtime evidence is NOT_RUN. Every file outside those scopes still says DRAFT_FOR_REVIEW. No file claims IMPLEMENTATION_VERIFIED or above.
3. **Consistency**: decision register B01–B17 RATIFIED; ADRs accepted; ADR-0006 = B; `agent_profile/registry.json` blockers empty with evidence ref and otherwise unchanged (diff against the FC-W4e7 manifest bytes); requirements.csv D08/D09/D42/D50 → XN with note; `precode/owner-decision-request.md` banner + filled answer sheet; `purge_all` keep/delete lists identical across ports.yaml, entities.yaml TXN-purge-all, secrets.md/backup-restore.md and the recovery fixture l; stack B consistently stated in ADR-0006, deployment.md, cards, READMEs, review.md (grep for "Option A"/"Python toàn bộ" as the chosen stack).
4. **Cards**: 18 cards pinned as `PC10-PIN-OD01-20260907`, all rows recompute; §3/§8 rewritten for B (TypeScript web paths present on UI cards; Python for server/collector/worker); stop conditions: provisional-blocker conditions removed only in the four scopes, KC/REQ-OQ03 conditions retained.
5. **E0**: independent run (write nothing into the repo); `E0-12` now permits ACCEPTED/RATIFIED/CONTRACT_READY only under `ratification_ref` and inside the four scopes — verify by mutating a file outside the scopes to CONTRACT_READY on a scratch copy (must FAIL) and by removing a `ratification_ref` (must FAIL).
6. **Gates/review**: G1/G2 MET, G3/G4 PARTIALLY_MET with KC list, G5/SP1 NOT_MET with the correct reasons (stack chosen but no repo layout; REQ-OQ03; probe not run); review.md numbers reproduce; CR table includes CR-PC01-13, CR-PC02-22.
7. Regression sweep as in R3 (fixtures, bijection, prose tokens, headers, pins).

## Report
Findings `F-A2R5-nn`; per-package verdicts; per-scope claim verdict (may CONTRACT_READY stand for each of the four?); overall verdict; residual open items list for the Owner (re-stated with the ratification applied: what is now closed, what remains KC/undecided). Reply to the Coordinator ONLY: overall verdict; per-scope CONTRACT_READY verdicts; finding counts; five most important findings one line each; residual open items (≤12 lines); report path (≤35 lines).
