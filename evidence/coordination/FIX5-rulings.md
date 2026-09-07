# Coordinator rulings — FIX5 wave (after PC09 handoff + E0 run E0-20260906T193716Z) — 2026-09-06T19:50Z

Inputs: `evidence/handoffs/PC09-handoff.md` §6 (CR-PC09-01…07), `precode/review.md`, `evidence/runs/E0-20260906T193716Z.json`. Findings/CRs stay OPEN → FIX_PROPOSED; verification by A2 at FC-W4.

## R5-01 (CR-PC09-02) — error code boundary for denied edges (binding)
| Situation | Code |
| --- | --- |
| HTTP request by a principal class not allowed for that operation (e.g. collector token → `save.create`) | `UNAUTHORIZED` (401) |
| In-process call/import across an edge absent from `allowed_edges` (e.g. collector → analysis worker data path FE-08, scheduler → Telegram) | `FORBIDDEN_EDGE` |
| Process/network/filesystem/tool capability absent for the actor (adapter opens a socket, connector drives Chrome) | `CAPABILITY_DENIED` |
| Owner-session mutation without valid CSRF token | `CSRF_REJECTED` |
Every one of the 36 `forbidden_edges` in `contracts/modules.yaml` gets a `denied_cases[]` entry with `expected_error_code` from this table, enforcement mechanism, and `scenario_refs: [SC49]`.

## R5-02 (CR-PC09-01) — the 12 missing fixtures, owners and directories
| SC | Subject | Owner / directory |
| --- | --- | --- |
| SC49 | default-deny sweep over all 36 forbidden edges | W2 → new dir `acceptance/fixtures/boundary/` (README + one fixture per edge group or one fixture with 36 events, each `edge_assertion: forbidden`) |
| SC32, SC44 | `data.delete_target`, `data.purge_all` (two-phase confirmation, maintenance precondition, lease revocation, negatives) | W2 → `acceptance/fixtures/recovery/` |
| SC53 | post-restore reconciliation complete → dispatch re-enabled | W2 → `acceptance/fixtures/recovery/` |
| SC33–SC36 | PC03 scenario definitions already in run.yaml (data only) | W4 → `acceptance/fixtures/collection/` |
| SC50 | end-to-end success run: schedule → claim → collect → ingest → analyse → publish → deliver sent | W4 → new dir `acceptance/fixtures/e2e/` (structured `rows.<entity>[]` so the field gate is not vacuous) |
| SC52 | embedding generation switch, positive face (rebuild → verify → atomic activate) | W5 → `acceptance/fixtures/reporting/` |
| SC10 | same analysis revision rendered in app and Telegram with all D20 fields | W3 → new dir `acceptance/fixtures/ui/` |
| SC51 | first-time setup flow (spec §5.1 steps 1–5) | W3 → `acceptance/fixtures/ui/` |
All fixtures obey R4-01/R4-02 (structured rows, `_` annotations, `operation` key, actors = allowed callers, `edge_assertion: forbidden` for negatives), carry the baseline §3 header (or README-level header), and are listed in their README.

## R5-03 (CR-PC09-03) — requirement_refs to move PARTIAL → COVERED (only the "real" group)
- W3 (PC07): `contracts/ui/screens.yaml` cites `REQ-S4-01, -08, -09, -10, REQ-S5.3-01, -03, REQ-S5.1-01..03` (setup screens/flows) where the screen/action implements them.
- W2 (PC08): `contracts/ops/secrets.md` / `internet-boundary.md` cite `REQ-S11.2-05, -06`; `contracts/ops/deployment.md` (PC01 file, W2 authored) cites `REQ-S6.1-01`.
- W4 (PC03/PC05): `contracts/state/run.yaml` or `collector-probe.md` cites `REQ-S5.4-03` (resume step).
Milestone/success-metric rows stay PARTIAL (PC09 is right: covered by gates, not by contracts).

## R5-04 (CR-PC09-04) — W4: TSR-A01 reworded: "`valid` is terminal **within a generation**; the only transitions leaving it are T-AN-12/T-AN-13 (reanalysis / new paper version → new generation, old result kept)".
## R5-05 (CR-PC09-05) — W2: recovery README + fixture (i) `oracle_vi` say `UNAUTHORIZED` consistently.
## R5-06 (CR-PC09-06) — W1: anchors SC49–SC53 from `acceptance/scenarios.yaml` `subject_vi`; anchor completeness 01–53.
## R5-07 (CR-PC09-07) — W7 (PC10-FIX1, after FIX5 lands): `change-control.md` cites INV-01..INV-10 from `precode/gates.yaml` instead of redefining; replace `CONTRACT_ONLY` by plan §2 labels; declare card front-matter exception in `agent-tasks/README.md`; re-pin all 18 cards against the FC-W4 freeze (contract hashes only; cite PC09 files by path + SC id, not by hash).
## R5-08 — W6 (PC09-FIX1, after FIX5 lands): fill `fixture_refs` for the 12 scenarios; re-run E0 (new run file), update `evidence/index.json`, `traceability.csv` coverage, `gates.yaml` status, `review.md` numbers and the A1-R3/FIX4/FIX5 state; keep any residual FAIL honest.
