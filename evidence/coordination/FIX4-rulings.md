# Coordinator rulings — FIX4 wave (after AUDIT_REPORT PKT-A1-R3 on FC-W3 epoch 3) — 2026-09-06T19:25Z

Report: `…/scratchpad/audits/A1-R3-report.md`. Findings stay OPEN → FIX_PROPOSED; verification by the final independent auditor (A2) at FC-W4.

## R4-01 (F-A1R3-01) — fixture annotation convention, binding in ALL six fixture directories
- Under `given.rows.<entity>[]` and `expected.rows.<entity>[]`, every key is either (a) a column that exists in `contracts/data/entities.yaml` for that entity, (b) an annotation whose key **starts with `_`** (`_note`, `_target`, `_note_vi`, `_save_channel_note`, `_created_in_transaction`, `_payload_contains`, …), or (c) a column carrying an in-file `pending_cr: CR-…` marker. No per-package allowlist. Rename the 89 bare annotation keys accordingly (identity 52 / telegram 31 / reporting 6).
- Every package that touches fixtures re-runs a field-level gate that implements exactly this rule over **all six directories** and reports the numbers (files, columns checked, unresolved = 0). PC09's `e0_check.py` implements the same rule as check `fixture-field-existence`; the numbers in handoffs must match an independent run.
- Fixture README of each directory states the rule verbatim (one paragraph) and lists every file in the directory (F-A1R3-04: telegram README must list its five `neg-saved-snapshot-*` files and drop the stale "open pending_cr example" note in §6).

## R4-02 (F-A1R3-02) — event key names and negative-edge marker
- Event objects use the key `operation` (not `operation_id`) everywhere; PC05 renames in `acceptance/fixtures/collection/*` (26 events).
- `edge_assertion: forbidden` is RATIFIED as the marker for a deliberately forbidden-edge event (the actor-edge gate expects the triple to be absent from `allowed_edges` and the expected error to be `UNAUTHORIZED`/`FORBIDDEN_EDGE`/`CAPABILITY_DENIED`). Documented in the READMEs of the directories that use it (collection, recovery) and implemented in `e0_check.py` (`fixture-actor-edge`).

## R4-03 (F-A1R3-03) — scenario anchors
- PC00 anchors SC45–SC48 (telegram: multipart unknown part / lost response / unlink before send / relink — take the subjects from `acceptance/fixtures/telegram/README.md`). SC49+ allocated by PC09 will be anchored in a final PC00 packet after PC09 hands off.

## R4-04 (F-A1R3-05) — analysis-result schema discriminator
- `allOf` + `if/then` is accepted as functionally equivalent to `oneOf`; PC06 declares the deviation in the schema's `x-contract.deviations` and in its handoff addendum, with the reason (per-task required-field sets) and the negative fixtures that prove exclusivity. No structural change required.
