# AUDIT_REPORT `A3-P5-R3` — one-item verification of `F-A3-P5R2-01` (FC-P5 epoch 3)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P5-R3` · authority `AUTH-COORD-A3-P5-R3` (parent `AUTH-OWNER-20260908-11`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of `PKT-TC-BACKUP-FIX5`. |
| candidate | `FC-P5` epoch 3, 705 entries, `manifest_sha256 = ed0bbf6c74d02c7e4dd92c6266bd84f075afbe00d8e0529b17552e37a7bc515e`, epoch `PC10-PIN-P5c-20260909` |
| quiescence | Recomputed start and end: **705/705** identical, header hash reproduces. `git status --porcelain` (excl. `.claude/`) **134** before and after. Not `STALE`. |

## 1. `F-A3-P5R2-01` — **VERIFIED**, both directions

Process-level, on a database migrated by `rr-admin migrate` and deliberately **not**
bootstrapped:

```
$ uv run rr-backup --database …/n.db --token-file tok maintenance --open --reason restore
{"code":"NOT_FOUND",
 "details_safe":{"resource_kind":"owner"},
 "message_safe":"Chưa có hàng `owner` nào: cơ sở dữ liệu đã migrate nhưng chưa bootstrap.
                 Chạy `uv run rr-admin bootstrap-owner` rồi thử lại."}          EXIT=2
```

The message now names the right resource **and** the exact command to fix it — more than the
finding asked for.

I then checked the fix did not over-correct. After bootstrapping an owner, asking for a
snapshot that does not exist still says *snapshot*:

```
$ uv run rr-backup … verify --snapshot-id 01M22NVQ…ZZ
{"code":"NOT_FOUND",
 "details_safe":{"operation_id":"backup.verify_snapshot","resource_kind":"backup_snapshot"},
 "message_safe":"Không tìm thấy snapshot được yêu cầu."}                        EXIT=2
```

So the message is discriminated by `resource_kind` rather than replaced wholesale, and
`details_safe` — the half that was already correct — is untouched.

## 2. Regression on e3 — reproduced

`1179 passed, 3 xfailed, 0 failed` · `ruff check` clean · `ruff format --check` **188 files** ·
`uv run mypy` **101 files** clean · gen-check clean · `verify_cards` **13/13 over 20 cards,
3 963 assertions, 0 violations** at epoch **`PC10-PIN-P5c-20260909`** (unmoved, so no pinned
file was touched) · `e0_check` **27/27** · one head `0015_tc_storage_maintenance_window`.
No socket-blocked re-run: the only changed transport file is `tools/backup_cli.py`'s message
table, and I exercised that path directly as a process.

> **Method note, recorded because it nearly produced a wrong report.** My first read of the
> regression logs returned Phase-1-era numbers (61 formatted files, 25 mypy files, 18 cards at
> `PC10-PIN-P1d-20260907`, e0 25/25). The cause was mine: I reused the `r3-` log prefix from
> the earlier `A3-R3` round, and read the files before this round's run had overwritten them.
> I caught it on the mtimes, deleted the stale sentinel, waited for the fresh run and re-read.
> Every number above is from logs written after this round started. Reporting a prior epoch's
> numbers as this epoch's is precisely the staleness class I have raised against others four
> times; the same discipline has to apply to my own workspace.

## 3. New finding

### `F-A3-P5R3-01` — LOW — the newest backup manifest is not pin-clean

Packet item 3 asks me to confirm the newest backup manifest is pin-clean. It is not.
`evidence/runs/TC-backup-restore-drill-E1-20260909T100500Z.json` carries **2 stale pins**, both
under `inputs.fixtures`:

* `acceptance/fixtures/recovery/README.md`
* `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json`

Both are tracked-and-modified in the working tree, and the second is exactly the fixture the
`PC02-FIX16…19` purge-count propagation (37/22/2) rewrote. `verify_cards` passes at `P5c`, so
the *cards* were re-pinned after that change — the backup card's manifest kept the
pre-change input hashes instead.

Severity is LOW because these are **read** pins, not produced artefacts: the record does not
misstate what the run output, only what it ran against. The five superseded backup manifests
carry the same drift (4–5 stale pins each) and are correctly retained as history. Same class
as `F-A3R2-03` and `F-A3-P4R2-02`, both of which were closed by re-issuing.

**Remediation constraint:** re-issue the newest backup manifest against current fixture bytes,
or record in it that its inputs were superseded by `PC02-FIX16…19` and why that does not
change the result. Do not edit the hashes of the superseded records — their drift is the
historical fact. `OPEN`.

**New findings: 1 — LOW 1.**

## 4. Overall

**PASS.** `F-A3-P5R2-01` is verified in both directions by process-level runs, and every
regression number reproduces at the frozen epoch. The one new finding is an evidence-currency
detail in the backup card's own manifest, not a defect in shipped behaviour.

Residual unchanged from `A3-P5-R2`: `/v1/reports` keeps a contract-mandated 500;
`AMD-ENT-maintenance-01` still awaits the Owner; `docs/owner-runbook.md` §9.4 still carries
pre-wave text; the Owner still cannot produce or read reports, use tags, reach the research
connector, or run any live path — **E3/E4 remain `NOT_RUN` everywhere**.
