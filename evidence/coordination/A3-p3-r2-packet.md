# REVIEW TASK_PACKET PKT-A3-P3-R2 — scoped verification of F-A3-P3-01…03 fixes (FC-P3 epoch 2)

- packet_id `PKT-A3-P3-R2` · assignee `auditor-A3` · authority `AUTH-COORD-A3-P3-R2` (parent `AUTH-OWNER-20260908-10`) · lease null (read-only; git-ignored artefacts only; `git status --porcelain` before/after — 89 lines now)
- report path `…/scratchpad/audits/A3-P3-R2-report.md`
- Frozen candidate FC-P3 epoch 2: `…/scratchpad/audits/FC-P3e2-manifest.txt`, manifest_sha256 `41c475065793ee4ca5993a5ab1f98657fc23d617212ca1452475a9c90f76556a`, 545 entries. Recompute at start and end.
- Inputs: your `A3-P3-R1-report.md`; rulings `packets/FIX-A3P3R1-rulings.md`; addenda PKT-TC-ADAPTER-FIX1 (W3A), PKT-TC-ANALYSIS-FIX1 (W3B), PKT-TC-EMBED-FIX1 (W3C), PKT-TC-TGAUTH-FIX1 (W5A), PKT-TC-DELIVERY-FIX1 (W5C); re-issued manifests (adapter 201840Z, analysis 202638Z, embedding 201528Z, tgauth 202140Z, delivery 202901Z; older ones marked STALE).
- Coordinator's own read-only measurement on e2: 827 passed / 9 xfailed / 0 failed; `ruff check` + `ruff format --check` clean (134 files); one head `0009`; verify_cards 13/13 (3685, pins unchanged — no precode/contract file moved since P3b); e0 25/25. Verify, don't inherit.

## Scope
1. F-A3-P3-01 — `ruff format --check .` rc=0 on the whole tree (CI step); the four files changed only in formatting (diff is whitespace/layout — confirm no semantic change).
2. F-A3-P3-02 — the two xfails are real tests now: W5A's save-from-chat test drives `server.app.saved.service`; W5C's provider-message-id test pairs part id ↔ message id by identity; every remaining xfail is `strict=True, run=True` and names a genuinely absent card (report-coverage-publish-cas / scheduler-lease-claim / backup-restore-drill) — 9 xfailed total, list them.
3. F-A3-P3-03 — `ai/g`, `recovery/f`, `reporting/e`, `reporting/m`: each either driven by name in a test (verify the test actually reads the fixture file, not a copy) or recorded NOT_RUN with a concrete reason in the owning handoff and manifest.
4. Re-issued manifests: newest per card registered-able (sha256 of every artefact matches disk); superseded ones marked STALE, not deleted; both validate.
5. Regression on e2: full suite, ruff/format, mypy, e0, verify_cards, one head; socket-blocked run not required again unless a transport-touching file changed (W5A's `ingress.py`/`commands.py` did — decide and say).
6. Per-card claim verdicts restated (6); overall; new findings only in the fix diff (`F-A3-P3R2-nn`).

Reply ONLY: verdict per finding (VERIFIED | PARTIAL | NOT_VERIFIED), overall, per-card verdicts, new finding count, report path (≤15 lines).
