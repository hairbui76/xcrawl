# AUDIT_REPORT `A3-P5-R2` — scoped verification of `F-A3-P5-01…04` + `CR-P0-10` (FC-P5 epoch 2)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P5-R2` · authority `AUTH-COORD-A3-P5-R2` (parent `AUTH-OWNER-20260908-11`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of every fix addendum. |
| candidate | `FC-P5` epoch 2, 700 entries, `manifest_sha256 = 813892848430a28c76be982724931f06eee5576deaef19f221fcaaae612a4bd8`, epoch `PC10-PIN-P5c-20260909` |
| quiescence | Recomputed start and end: **700/700** identical, header hash reproduces. `git status --porcelain` (excl. `.claude/`) **129** before and after; **0** `__pycache__`. Not `STALE`. |
| method | Items 1–4 re-run **as processes** — real `uvicorn` + `curl` over TCP, console scripts from a temp cwd. Repository never written to. |

## 1. Regression on e2

| Gate | Coordinator | Mine |
| --- | --- | --- |
| `uv run pytest` | 1176 / 3 xfailed / 0 failed | **1176 passed, 3 xfailed, 0 failed** |
| `ruff check` / `format --check` | clean / 188 | `All checks passed!` / `188 files already formatted` |
| `uv run mypy` | Success, 101 | **`Success: no issues found in 101 source files`** |
| gen-check | clean | `generated tree matches a fresh run of the generator` |
| `verify_cards.py` | 13/13 over 20, 3963 | **13 PASS, 3 963 assertions, 0 violations** @ `PC10-PIN-P5c-20260909` — **epoch unchanged, so no pinned file moved**, as claimed |
| `e0_check.py` | 27/27 | **27 PASS · 0 FAIL · 0 violations** |
| socket-blocked suite | — | **repeated** (`wiring.py`, `report/router.py`, `backup_cli.py` are transport-touching): **zero attempts** |

## 2. Finding verdicts

### `F-A3-P5-01` — **VERIFIED**

Run as a process, with accurate exit codes (not masked by a pipe):

| invocation | result |
| --- | --- |
| `rr-backup … maintenance --open` (no `--reason`) | `VALIDATION_ERROR` envelope, `details_safe: {field_path: "--reason", violation_kind: "required_field_missing"}`, `message_safe: "Mở cửa sổ bảo trì cần --reason."` — **exit 2**, no traceback |
| `… maintenance --open --reason restore` | `{"storage_health":"maintenance","transition":"T-ST-03","window_id":"01M22MXF2G…"}` — **exit 0** |
| **fresh process** `… restore --snapshot-id … --request-id … --confirm RESTORE` | passed the maintenance precondition; failed only on my deliberately fake snapshot id — `NOT_FOUND`, **exit 2** |

Spot-check of another guard path (item 1's "every guard exception is enveloped"): running the
CLI against a **migrated but un-bootstrapped** database also returns an envelope, not a
traceback — though its wording is wrong; see `F-A3-P5R2-01`.

### `F-A3-P5-02` — **VERIFIED**, and fixed the right way

`rr-admin status` now prints:

```
not wired : research_connector — SG-DOC: no contract names the arXiv/OpenAlex API host or
            endpoint (endpoint_template is None; CR-PC05-03); SG-LIVE: a real call is E3 …
```

Those are exactly the blockers I identified in `A3-P2-R1`. `PLACEHOLDER_KC` no longer appears
as a *claim* anywhere in `server/` or `tools/` — the five remaining occurrences are the
docstring explaining the history and a **regression test**
(`server/tests/test_wiring.py:313`: `assert "PLACEHOLDER_KC" not in connector, "the stale
REQ-A6 claim is back"`).

Better than asked: the rate-limit half is **read from the contract at run time** —
`wiring.py` loads `contracts/retry-policy.yaml` and only reports a regression if
`research_connector_rate_limit.status != "DOCS_derived"`. The two real blockers stay constants
with a stated reason ("an absence cannot be looked up"), which is the correct split. The
docstring names the finding and why it mattered.

### `F-A3-P5-03` — **VERIFIED; the ruling is right and I would have ruled the same way**

On a real wired server, both routes still answer **HTTP 500 / `INTERNAL`** — but the body is
now a *disclosure*:

> `"Dịch vụ báo cáo chưa được cấu hình trong bản triển khai này (CR-P0-07): chưa có cổng
> tag-service và cổng embedding. Yêu cầu của bạn hợp lệ và không có dữ liệu nào bị đọc hay ghi."`

with `details_safe.operation_id` correct per route (`report.list` vs `report.get`). An
**unauthenticated** call gets `401 UNAUTHORIZED` first, so the unwired state is not disclosed
to a caller who has not logged in.

My finding's substance was that the Owner got *"unexpected error"* with nothing actionable for
an entirely expected gap. That is gone: the message names the cause, the CR, the two missing
ports, and states that nothing was read or written. Keeping `INTERNAL` is the **correct**
call — `openapi.yaml` declares only `200/401/403/500` (and `404`) on these two paths, so
emitting an undeclared `503` would trade an unhelpful message for a wire-contract violation.
W4A chose the honest option available inside the contract.

*Residual, stated not waved away:* the **status code** is still 500, so anything that
classifies by HTTP status alone (a monitor, a proxy) will read a configuration gap as a server
fault. Changing that needs a declared `503` in `openapi.yaml` — a contract change for a later
round, not a code fix. `rr-admin status` separately reports `report_context` unwired with the
same CR reference.

### `F-A3-P5-04` — **VERIFIED**

`[project.scripts]` declares all five: `rr-admin`, `rr-backup`, `rr-collector`, `rr-worker`,
`rr-probe`. Every one runs **from a temp cwd**: `rr-admin status` printed the inventory,
`rr-backup --help` its usage, `rr-collector --check-config` the `refused_to_start /
missing_server_url` envelope, `rr-worker --print-capabilities` its capability JSON, and
`rr-probe --dry-run` reported `wrote_nothing: true` with only `cfg.json` and `rr.db` on disk
afterwards.

**Which way the `sys.path` bootstraps went, as asked: tolerated, not removed.** They remain in
`tools/rr_admin.py` (2 references) and `probe/x_feasibility/run_probe.py` (3); `backup_cli.py`,
`collector/app/main.py` and `worker/app/main.py` still have none. That asymmetry no longer
matters operationally, because the console scripts are now the documented interface and they
work uniformly — but it is residue rather than a cleanup, and worth saying so plainly.

### `CR-P0-10` — **VERIFIED**

From a temp cwd with a plain `RR_DATABASE_URL=sqlite:///<abs path>/rr.db`, `rr-admin migrate`
resolved to the intended absolute path, ran to `0015_tc_storage_maintenance_window`, and left
**exactly one** file in that directory — `rr.db`. No stray file, no database created relative
to the repo.

### Manifests

**No newest-per-card manifest pins `server/app/main.py` at all** — I walked every
`{path, sha256}` pair in the newest record of all 20 cards and found zero. W5B's SAVED-FIX2 and
the tgauth re-issue both dropped it, which also resolves my earlier **`F-A3-P4R2-02`** (the
stale `main.py` pin) as a side effect. Superseded records are retained.

## 3. New finding

### `F-A3-P5R2-01` — LOW — a `NOT_FOUND` from the backup CLI names the wrong resource in its message

On a migrated-but-not-bootstrapped database:

```json
{"code":"NOT_FOUND",
 "details_safe":{"resource_kind":"owner"},
 "message_safe":"Không tìm thấy snapshot được yêu cầu."}
```

`details_safe` is right (`owner`), but the human-readable half says the requested **snapshot**
was not found. The message comes from a per-code table
(`server/app/backup/snapshot.py:187`) that maps `NOT_FOUND` to one snapshot-specific sentence
regardless of what was actually missing.

The consequence is the kind this wave exists to remove: an Owner who runs the backup CLI before
`bootstrap-owner` is told to go looking for a snapshot, when `rr-admin status` would have said
*"no owner row; run `uv run rr-admin bootstrap-owner`"*. It sends them to the wrong place. In
the fix diff (`BACKUP-FIX4` touched this CLI).
**Remediation constraint:** derive `message_safe` from `resource_kind`, or add an
owner-specific entry. Do not fix it by dropping `resource_kind` from `details_safe` — that
field is the part that is currently correct. `OPEN`.

**New findings: 1 — LOW 1. MEDIUM 0 · HIGH 0.**

## 4. Overall and the Owner-can-run answer

**Overall: PASS.** All four findings and `CR-P0-10` verify on my own process-level
reproduction; every regression number matches; the epoch did not move, confirming no pinned
file was touched.

**Can the Owner run it end to end? Still no — but every remaining blocker is now either named
on screen or is a real, undone piece of work, and nothing crashes.**

*Newly working since R1:* `maintenance --open` behaves correctly and reports its own misuse
with an exit code; all five entry points run from anywhere via console scripts; a plain
`sqlite:///` URL resolves properly; `status` and `/v1/reports` both tell the truth about the
report gap instead of misdirecting or saying "unexpected".

*Still cannot:*

1. **Produce or read reports** — `report_context` unwired (`CR-P0-07`): no `TagConfigVersionPort`
   implementation and no real embedding model (`REQ-OQ09`). The product's output does not exist.
2. **Tags** — `MOD-tag-service` still has no card.
3. **Research connector** — unwired on `SG-DOC` (no contract names either API's host/endpoint)
   and `SG-LIVE`.
4. **Any live path** — collector needs `RR_SERVER_URL`, a collector token and a real X session;
   Telegram needs a bot token and webhook secret; both AI adapters remain `enabled: false` on
   unverified isolation. **E3/E4 are `NOT_RUN` everywhere**: SP1 has never run, no live
   AI/Telegram/X call has ever happened, no real restore drill.

So the Owner can stand the system up, log in, inspect it, and drive the backup/maintenance and
probe-dry-run paths. The Owner still cannot make it *do* its job.

## 5. Residual

* `F-A3-P5R2-01` open. `F-A3-P4R2-02` is **resolved** by this round's manifest change;
  `F-A3R4-01`, `F-A3-P2-01/-02`, `F-A3-P4R2-01` remain open from earlier rounds.
* `/v1/reports` keeps a 500 status by contract necessity — a declared `503` would need an
  `openapi.yaml` change.
* `AMD-ENT-maintenance-01` is still a Coordinator technical amendment the **Owner has not been
  asked** about; same shape as `AMD-ENT-owner-01`, which the Owner later ratified. It belongs in
  the next Owner round rather than settling by silence.
* `docs/owner-runbook.md` still carries pre-wave text in §9.4 (the closed G-3 box and the old
  `maintenance --open` command); it needs WS2's post-commit re-verification before an Owner
  follows it.
* Three strict xfails unchanged (`CR-PC07-04`, `CR-TC-AUTH-01`, `CR-TC-IDENTITY-02`).
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
