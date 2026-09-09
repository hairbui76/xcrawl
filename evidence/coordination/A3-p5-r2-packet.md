# REVIEW TASK_PACKET PKT-A3-P5-R2 — scoped verification of F-A3-P5-01…04 fixes (FC-P5 epoch 2)

- packet_id `PKT-A3-P5-R2` · assignee `auditor-A3` · authority `AUTH-COORD-A3-P5-R2` (parent `AUTH-OWNER-20260908-11`) · lease null (read-only; git-ignored artefacts only; `git status --porcelain` before/after)
- report path `…/scratchpad/audits/A3-P5-R2-report.md`
- Frozen candidate FC-P5 epoch 2: `…/scratchpad/audits/FC-P5e2-manifest.txt` — hash + count in header (filled at freeze; recompute at start and end).
- Inputs: your `A3-P5-R1-report.md`; rulings `packets/FIX-A3P5R1-rulings.md`; addenda PKT-TC-BACKUP-FIX4 (W6B), PKT-P0-FIX8 (WS), PKT-TC-REPORT-FIX3 (W4A); re-issued manifests.

## Scope (process-level again where the finding was process-level)
1. F-A3-P5-01 — `uv run python tools/backup_cli.py maintenance --open` **without** `--reason` ⇒ JSON envelope + documented exit code, no traceback; with `--reason restore` ⇒ window row; a fresh `restore` invocation passes the precondition. Every guard exception is enveloped (spot-check one more path).
2. F-A3-P5-02 — `rr_admin status` and the wiring log name the connector's real blockers (SG-DOC / SG-LIVE), read from `retry-policy.yaml` at run time; the string "PLACEHOLDER_KC" no longer appears for the connector anywhere in `server/app/` or `tools/`.
3. F-A3-P5-03 — on a real wired server, `curl /v1/reports` and `/v1/reports/<id>` return the declared error (status + code cited from `openapi.yaml`) with `details_safe` naming CR-P0-07 — not 500; `rr_admin status` shows `report_context: None` with the reason.
4. F-A3-P5-04 — `[project.scripts]` entries exist and `uv run rr-admin status`, `rr-backup --help`, `rr-collector --check-config`, `rr-worker --print-capabilities`, `rr-probe --dry-run` all run from a temp cwd; `sys.path` bootstraps either removed by their owners or documented as tolerated — say which.
5. Regression on e2: pytest, ruff/format, mypy, web, e0 (27/27), verify_cards (13/13 over 20 @ `PC10-PIN-P5c-20260909` unless a pinned file moved — none should), one head, gen-check, socket-blocked run only if a transport-touching file changed (say which).
6. Re-issued manifests newest-per-card pin-clean; STALE retained. Per-packet verdicts restated; overall; "can the Owner run it end to end?" re-answered; new findings only in the fix diff (`F-A3-P5R2-nn`).

Reply ONLY: verdict per finding (4), overall, the Owner-can-run answer, new finding count, report path (≤15 lines).

## Freeze record (2026-09-09T08:33Z)
- FC-P5 epoch 2 manifest: header of `…/scratchpad/audits/FC-P5e2-manifest.txt`. Epoch `PC10-PIN-P5c-20260909` (no pinned file moved in the fix round — verify).
- Coordinator measurements on the frozen bytes: pytest 1176 passed / 3 xfailed / 0 failed; ruff check + format (188) clean; mypy 101 clean; web 126/126 + tsc + lint; one head `0015`; verify_cards 13/13 over 20 (3963); e0 27/27; gen-check clean; 0 pycache. Process check: `rr-admin migrate`/`status` from a temp cwd with a plain `sqlite:///` URL now creates exactly `rr.db` at the right path (CR-P0-10 fixed — found by the Coordinator's own probe after R1).
- Fix-round addenda: W6B BACKUP-FIX4 (F-01), WS P0-FIX8/9/10 (F-02, F-04 console scripts, CR-P0-10 settings URL resolution), W4A REPORT-FIX3 (F-03: contract declares no 503 on the read routes, so a *disclosed* INTERNAL 500 naming CR-P0-07 with the right operation_id, 401-before-availability — judge that ruling), W5B SAVED-FIX2 (manifest no longer pins main.py). Also verify: no manifest for any of the 20 cards pins `server/app/main.py` as PRODUCED.
- Additional process check for you: `uv run rr-backup --database <db> --token-file <f> maintenance --open` with and without `--reason` (I mis-invoked it myself; you do it right).
