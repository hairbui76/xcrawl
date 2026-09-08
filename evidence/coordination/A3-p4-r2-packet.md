# REVIEW TASK_PACKET PKT-A3-P4-R2 — scoped verification of F-A3-P4-01…03 fixes (FC-P4 epoch 2)

- packet_id `PKT-A3-P4-R2` · assignee `auditor-A3` · authority `AUTH-COORD-A3-P4-R2` (parent `AUTH-OWNER-20260908-11`) · lease null (read-only; git-ignored artefacts only; `git status --porcelain` before/after)
- report path `…/scratchpad/audits/A3-P4-R2-report.md`
- Frozen candidate FC-P4 epoch 2: `…/scratchpad/audits/FC-P4e2-manifest.txt` — hash + count in header (filled at freeze; recompute at start and end).
- Inputs: your `A3-P4-R1-report.md`; rulings `packets/FIX-A3P4R1-rulings.md`; addenda PKT-TC-REPORT-FIX2 (W4A), PKT-TC-BACKFILL-FIX2 (W4B), PKT-P0-FIX4 (WS), PKT-PC00-FIX32 (W1n, ADR-0011 amendment), PKT-TC-IDENTITY-FIX3 (WM), W6n's E0-21 tool addendum; re-issued manifests; re-pin epoch `PC10-PIN-P4b-20260908`.

## Scope
1. F-A3-P4-01 — `_write_first_announcements` announces only items whose summary is final (clause cited); pending item not announced at publish, announced exactly once when its summary lands; W4B's CR-09 test is a real assertion (`late_discovery`, not `prior_reference`, per fixture `reporting/e`); W4A's handoff names CR-TC-BACKFILL-09 and states REQ-D29/I07 coverage truthfully.
2. F-A3-P4-02 — mypy `files` covers `server/app`, `worker/app`, `collector/app`, `probe`; `--strict` retained; `uv run mypy` clean across the widened scope; `types-PyYAML`/`types-jsonschema` in dev deps (CR-TC-adapter-06 closed); `server/tests/test_smoke.py` typing resolved or explicitly excluded with a reason; CI step/Makefile names truthful; `.gitignore` covers `__pycache__/`; ADR-0011 amended accordingly (scope + `tools/` correction, CR-PC00-35), amendment block in the ADR's convention, register/change-control entries.
3. F-A3-P4-03 — identity card's fixture-`i` test real against `publish_report`-seeded rows; E0-21 (stale-xfail rule) exists, mutation-tested both directions, reports 0 on current bytes (or exactly the honest residue, named).
4. Regression on e2: pytest, ruff check/format, mypy (widened), web (Vitest/tsc/eslint/prettier), e0 (27/27 expected if E0-21 landed), verify_cards @ P4b, one head, schema-vs-entities; socket-blocked run only if a transport-touching file changed (say which).
5. Re-issued manifests newest-per-card pin-clean; superseded STALE retained. Per-card verdicts restated (6 new + identity); overall; new findings only in the fix diff (`F-A3-P4R2-nn`).

Reply ONLY: verdict per finding, overall, per-card verdicts, new finding count, report path (≤15 lines).

## Freeze record (2026-09-08T02:0xZ)
- FC-P4 epoch 2 manifest_sha256 `d6d507588c4c50aa05476dd03aa2e1656a256fc1e2b21d8ce7b760b3e73e8037`, 645 entries. Epoch `PC10-PIN-P4b-20260908`.
- Coordinator's read-only measurements on the frozen bytes: pytest 1042 passed / 3 xfailed / 0 failed; ruff check + format (165) clean; `uv run mypy` Success **87 files** (scope widened: server/app, worker/app, collector/app, probe); web 126/126 + tsc + eslint/prettier clean; one head `0013`; verify_cards 13/13 (3730) @ P4b; e0 **27/27** (E0-21 live); 0 `__pycache__`.
- Addenda to verify: W4A REPORT-FIX2 (`time-and-tags.md` §5.3 b3 + §8.2 r2; 2 new tests; coverage claim corrected), W4B BACKFILL-FIX2 (flip + converse test), WS P0-FIX4 (mypy scope, stubs, test_smoke typed, .gitignore, CI names), W1n PC00-FIX32 (AMD-ADR0011-01; CR-PC00-37 flagged citation), WM IDENTITY-FIX3, WA AUTH-FIX3 + FIX4 (self-fulfilling xfail replaced by 6 real tests; CR-TC-AUTH-11 real bug fixed: `sqlite3.Error` → 503; `authenticate()` idle-slide made best-effort), W6n E0-21 tool. The 3 remaining xfails are all `strict=True` contract-divergence markers (CR-TC-IDENTITY-02, CR-TC-AUTH-01, one more — list them).
