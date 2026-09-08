# HANDOFF — `TC-backfill-pending-ledger`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-BACKFILL` — card `agent-tasks/TC-backfill-pending-ledger.md` (Phase 4, M4, gate G5) |
| worker principal | `worker-W4B` |
| authority_id | `AUTH-COORD-TC-BACKFILL` (parent `AUTH-OWNER-20260908-10`, Owner instruction 2026-09-08 "do until finish everything") |
| lease_id | `LEASE-TC-BACKFILL-e1` (exclusive on card §3 write set + one Alembic revision + handoff + evidence manifest) |
| pin epoch | `PC10-PIN-P3b-20260908` — SG-HASH run **twice**, once before any read work and again immediately before the first write: **22/22 pinned files match byte for byte, 0 drift** |
| wait gate | all four conditions verified at 2026-09-07T21:1xZ: (1) `git log -1 --format=%s` on `main` = `feat: Phase 3 (M3) + Phase 5 (M6, plain text) …` (`fb3944a`); (2) `agent-tasks/README.md` line 124 declares `PC10-PIN-P3b-20260908`; (3) SG-HASH clean; (4) **the sibling gate** — `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md` present with `lease_released_at 2026-09-07T21:40Z`. Nothing was written before all four held; the reading phase ran against the working tree under a read-only discipline while polling. |
| status | **`DONE_WITH_CONCERNS`** — every oracle the card §8 names is implemented and green, and **`SG-PC09` fired**: `acceptance/scenarios.yaml` SC22 names two columns that `ENT-pending-item-ledger` does not have. The oracle was **not** edited and the code was **not** written to it; the conflict is handed back as `CR-TC-BACKFILL-11` and needs a ruling before this card's SC22 claim is accepted. Ten further `CR-TC-BACKFILL-nn` items are open, none of them blocking. |
| completion_claim | see §6. The card's ceiling is `IMPLEMENTATION_VERIFIED`; this record is `SELF_VALIDATION`, which `evidence/manifest.schema.json` caps at `CONTRACT_READY`, so the manifest claims that and no more. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T22:10Z |

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/report/backfill.py` | CREATE | ABSENT | `982c51335fef3be31a0dfa0744863e0e208ebbeeedb3d7dd35fce1e3c4d44089` | 24206 |
| `server/app/report/pending.py` | CREATE | ABSENT | `7568d89c1eff16e7fa5e66eeb91b0682bb34cb14b98c6cece00d11e57b88fd34` | 15306 |
| `server/app/tags/rescan.py` | CREATE | ABSENT | `b3959d8b44dcd72729ea0f13893aaac14198713f5e94070ff604c8f1af62813c` | 14100 |
| `server/migrations/versions/0013_tc_backfill_pending_ledger.py` | CREATE | ABSENT | `ca6a45f3c3ba9d1f2a6efb852ab10e09aa14a46ff54ec523f5e93561d6a9c656` | 9142 |
| `tests/integration/test_backfill_once.py` | CREATE | ABSENT | `a1673f368e9451454d6478c49b2add5d1cec80654576ff96b033975a608f734e` | 49511 |
| `tests/integration/test_pending_survives_cursor.py` | CREATE | ABSENT | `1ed74e85f41c4bfec10a5a5f3fb300552fd52f4ec67b3dbe99eba155a64b52c0` | 40758 |
| `evidence/runs/TC-backfill-pending-ledger-E1-20260907T220221Z.json` | CREATE | ABSENT | (validates against `evidence/manifest.schema.json`, 0 errors) | — |
| `evidence/handoffs/TC-backfill-pending-ledger-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified. No other card's package or test file was touched — in particular
`server/app/report/{coverage,builder,publisher,router}.py` were **imported and never edited**,
and neither were W5C's two delivery test files. `server/app/main.py` was **not** touched: this
card creates no HTTP router (see §1.1). No git command that mutates anything was run. No live
X, AI or Telegram call, no browser, no secret, `PYTHONDONTWRITEBYTECODE=1` throughout.

**One tool side effect, declared.** `PYTHONDONTWRITEBYTECODE=1` does not suppress pytest's
assertion-rewrite cache, so running the tests created
`tests/__pycache__/conftest.cpython-312-pytest-8.4.2.pyc`. It is covered by `.gitignore` line 3
(`__pycache__/`) and matches what every sibling's test run produces. Recorded because the worker
profile counts tool side effects as writes, not because it is expected to matter. Passing
`-p no:cacheprovider` avoids it.

### 1.1 Write-set notes

**No `server/app/main.py` include block.** Card §3 grants three source files and none of them
is a router. `tag.rescan_corpus` is an `http` operation in `contracts/ports.yaml`, so it will
need one — but inventing a router file outside §3 is exactly the "write first, legalise later"
the protocol forbids. Recorded as `CR-TC-BACKFILL-12`.

**No `server/app/tags/__init__.py`.** The repository uses namespace packages throughout
(`server/app/saved/`, `server/app/analysis/` and the rest carry no `__init__.py`), so adding
one would have been a file outside §3 *and* an inconsistency.

**`evidence/index.json` was deliberately not edited.** Card §13 asks for the run to be
registered there. It is a shared 94-record file with a `summary` block of derived counters,
three sibling workers in this wave were writing in the same window, and it is **not** in the
write set the dispatch packet grants (`card §3 + Alembic revision(s) + handoff +
evidence/runs/<card>-E1-<UTC>.json`). Registering it is therefore left to the Coordinator, and
is flagged here rather than silently skipped.

---

## 2. What was built, and the one idea behind each file

### `server/app/report/backfill.py` — `MOD-report-service`

The subscription identity, the activation ledger it keys, the §6.3 widening, and conditions 2
and 3 of §6.4.

The load-bearing decision is that entitlement is keyed on **the normalized tag text**, not on
`tag.id`. `ux_tag_owner_text_active` is partial on `state = 'active'`, so removing a tag and
adding the same words back mints a new `tag.id`; an entitlement keyed there is re-granted on
every re-add and REQ-D28's "exactly once" quietly becomes "once per add". `subscription_identity_hash`
is `sha256(owner_id + "\n" + normalize_tag_text(text))`, and the database — not this module's
branch — is what enforces the rule: `ux_backfill_subscription_consumed` =
`UNIQUE(owner_id, subscription_identity_hash) WHERE consumed_in_report_id IS NOT NULL`.

**This module never writes `consumed_in_report_id`.** That UPDATE lives in
`publisher._consume_backfill`, inside `TXN-report-publish`, and leaving it there is what makes
fixture `k` pass structurally rather than by convention: a builder that dies before the commit
cannot reach a line this module does not contain. What this module hands the publisher is the
*list* — `entitlements_to_consume(...)` → `BuildSnapshot.backfill_ledger_ids_applied`.

`N` is read from `settings` and appears nowhere in the source; `test_no_module_in_this_card_hard_codes_the_working_value`
parses the module's AST and asserts `7` is not a parameter default or a module constant, because
`SG-03` is a claim about the source and a hidden default would pass every behavioural test.

### `server/app/report/pending.py` — `MOD-report-service`

The half of the pending ledger that lives **outside** a publish. `publisher._write_pending`
already opens and closes rows inside the publish transaction; this module owns the rest:

* the `PendingLedgerPort` that `server.app.analysis.service.AnalysisContext` has been carrying
  as `None` since Phase 3 — without it, a budget-exhausted item never reaches the ledger, which
  is `I06`'s failure arriving through the analysis door instead of the report door;
* `abandon()`, the Owner's explicit act and the **only** path to `abandoned_by_owner`. There is
  deliberately no reason parameter, no expiry and no bulk form: each would be a way for the
  system to abandon an item on its own, which §5.3 forbids in as many words;
* the reads and the oracles — `carried_forward()` (unfiltered by any window, which is the whole
  of `I06`), `quality_for_window()` (O-5.3), the counters.

No `DELETE` appears anywhere in the file, asserted structurally as well as behaviourally.

### `server/app/tags/rescan.py` — `MOD-tag-service`

`tag.rescan_corpus`, with §7's five negative constraints made structural rather than
aspirational: **every SQL statement in the module names `rescan_ledger`**, plus one existence
read of `tag`. O-7's five counts cannot move because there is no statement that could move
them, and a test asserts that property over the source as well as over one command.

### `server/migrations/versions/0013_tc_backfill_pending_ledger.py`

Creates `tag`, `settings` and `rescan_ledger`. It does **not** recreate `backfill_ledger` or
`pending_item_ledger`: `0010_tc_report_coverage_publish_cas` created both as custodian for this
card and asked the card taking them over to EXTEND rather than issue a second `CREATE TABLE`
(the `F-A3R1-01` rule). `settings` carries the same custodian note forward for
`MOD-settings-service`, which no card owns.

**One head, by chaining not merging.** `0012_tc_backup_restore_drill` had already branched off
`0011` when this landed, so `down_revision` is `0012_tc_backup_restore_drill`. A merge revision
is a *shared* artifact and both remaining migration authors would have had to agree not to write
one — the race that produced `0004`, `0007` and `0011` in the first place. `alembic heads`
returns exactly one revision; `test_the_migration_graph_has_exactly_one_head` computes it rather
than comparing against a literal.

---

## 3. Verification

Every command was run from `/mnt/virtual/repo/xcrawl` with `PYTHONDONTWRITEBYTECODE=1`.

| Command | Result | Exit |
| --- | --- | --- |
| `uv run pytest tests/integration/test_backfill_once.py -p no:randomly --tb=no` | **27 passed** | 0 |
| `uv run pytest tests/integration/test_pending_survives_cursor.py -p no:randomly --tb=no` | **25 passed, 1 xfailed** | 0 |
| `uv run ruff check` (six files of this card) | All checks passed | 0 |
| `uv run mypy` (`--strict`, `server/app`) | Success: no issues found in 64 source files | 0 |
| `uv run pytest -p no:randomly --tb=no` (whole repository) | **990 passed, 10 xfailed, 0 failed, 18 errors** | 1 |

The 18 errors are `CR-TC-REPORT-09`, which W4A's own handoff records: `install_report_stand_in`
in `tests/integration/test_delivery_unknown_no_retry.py` inserts three columns into the now-real
`ENT-report`. Both affected files are W5C's write set and this card did not touch them; the
count is **unchanged** from before this card wrote (verified by running the suite before and
after). Two failures in `tests/contract/test_schema_matches_entities.py` observed mid-session
were W6B's `backup_snapshot.snapshot_request_id` / `restore_record.restore_request_id` and were
resolved by W6B while this card was running; a column-set diff over the final `head` schema
attributes **zero** undeclared or unshipped columns to this card's three tables.

### 3.1 The oracles of card §8, and how each is measured

| Card §8 oracle | Measured by | Result |
| --- | --- | --- |
| Fixture `j`: after add → remove → re-add, `COUNT(backfill_ledger WHERE consumed_in_report_id IS NOT NULL)` equals the number of valid activations — no more | `consumed_count(identity) == 1` while `COUNT(rows for that identity) == 2`, plus the two rows carrying **two different `tag_id`s and one identity hash** | PASS |
| Fixture `k`: after a crash the backfill is still `unconsumed`; the next publish consumes it | build → process dies before `publish_report` ⇒ `consumed == 0`, 0 `report_item`, coverage unmoved; rebuild → publish ⇒ `consumed == 1`. Plus an E2 variant with `WriteFaultInjector` firing **inside** `TXN-report-publish` ⇒ still 0 | PASS |
| Fixture `e`: the pending item appears in the next period with `late_discovery = true`, not dropped | `report_item.selection_reason.late_discovery is True` in period 3, **and** its `discovered_at` asserted to be outside period 3's `[coverage_from, coverage_to)` — the second half is what proves it came from the ledger and not from a window query | PASS (with one xfail, `CR-TC-BACKFILL-09`) |
| `tag.rescan_corpus` changes no `first_announced_ledger` row | O-7's five counts snapshotted before and after a real rescan, taken after two real periods so the held-still numbers are non-zero; `#rescan_ledger` +1 | PASS |

Additional oracles proved: O-6.1 (no identity group exceeds one consumed row, as a `GROUP BY …
HAVING COUNT(*) > 1` query returning empty); the database refusing a second consumption when the
code asks for one anyway; O-5.1's ledger arithmetic across a publish; `SG-DENY` for FE-11 /
FE-12 / FE-23 / FE-30 answering `FORBIDDEN_EDGE` and **not** `UNAUTHORIZED`, with zero rows
written before the refusal; O-6.4 / REQ-AC06 with a **real** tag removal and re-add against the
`tag` table this card creates (`analysis_generation` and `analysis_attempt` unchanged, provider
call delta 0) — the sibling card could only simulate the tag edit, because there was no table.

### 3.2 Not run

E3 / E4 do not apply: card §8 says "Không cần live". No X, AI or Telegram call was made.

---

## 4. Change requests

| ID | To | Item |
| --- | --- | --- |
| `CR-TC-BACKFILL-11` | Coordinator / PC09 | **`SG-PC09` fired — needs a ruling.** `acceptance/scenarios.yaml` SC22 states its oracle as `COUNT(pending_item_ledger WHERE report_id=<kỳ n> AND consumed_at IS NULL) = 2`. `ENT-pending-item-ledger` has **six** columns — `id, owner_id, target_key, reason, first_pending_window_id, state` — and neither `report_id` nor `consumed_at` is among them; fixture `e`, which SC22 itself cites, expects **one** pending item, not two. Per `SG-CONTRACT` the oracle was **not** edited and the code was **not** written to it: this card implemented `entities.yaml` + fixture `e`. Anyone reading `scenarios.yaml` as the authority will reach a different conclusion, so the card's SC22 claim is conditional on this ruling. |
| `CR-TC-BACKFILL-09` | W4A / Coordinator | **A late discovery comes back as `prior_reference`.** Fixture `e`'s `row_oracle` says `item_type` stays `new_discovery`; §5.3 qualifies that with "chưa từng được công bố", and fixture `e` settles what that means — `E1` *was* a `report_item` of period 2 (AMD-B17: a pending item is shown, not hidden) and the fixture still expects `new_discovery` in period 3. `publisher._write_first_announcements` writes a `first_announced_ledger` row for every `new_discovery` **work** item including pending ones, so period 3 sees it as announced. Suggested fix, one condition: skip items whose `summary_state` is `pending`. Captured as `xfail(strict=True)` so it reports an XPASS the day it is fixed. |
| `CR-TC-BACKFILL-05` | W4A / Coordinator | **The builder does not apply the backfill extension.** `selection.md` §2 writes the candidate set as three unions; `builder._candidates` unions the first two, and `BuildSnapshot.backfill_ledger_ids_applied` is derived from `Candidate.backfill_ledger_id`, which nothing sets (`coverage_note["backfill_applied_tag_ids"]` is a hard-coded `[]`). This card supplies the seam — `plan_extension()` + `entitlements_to_consume()` — and its tests compose it with the real `build_report` / `publish_report`, but **a deployment today would never widen a candidate range**. Suggested fix: a `backfill_port` parameter on `build_report`. |
| `CR-TC-BACKFILL-10` | W4A / Coordinator | **`backfill_ledger.tag_id` still has no `REFERENCES tag (id)`.** `entities.yaml` declares it, `0010` deferred it as `CR-TC-REPORT-01` because `tag` did not exist, and `tag` exists as of `0013`. The clause was written, and withdrawn: it fails `tests/integration/test_coverage_contiguous.py::test_a_refused_write_advances_nothing_and_consumes_no_backfill`, which inserts a ledger row with a synthetic `tag_id` and — correctly for a repository without a `tag` table — seeds no `tag` row. The fix is one seeded row in a file this card does not own, not a schema change. `rescan_ledger.tag_id` **does** carry its declared FK, since that table is new here. |
| `CR-TC-BACKFILL-03` | Coordinator | **`tag.rescan_corpus` cannot enqueue analysis.** `time-and-tags.md` §7 rule 5 permits it; `contracts/modules.yaml` gives `MOD-tag-service` only `embedding.*` outbound and carries no `MOD-tag-service → MOD-analysis-service` row, so under `default_deny` the call is `FORBIDDEN_EDGE`. Card §5 settles the precedence (the registry wins) and `SG-EDGE` makes adding an edge change control's job, so the "đào sâu" half of the command is **NOT_RUN**, not implemented against an edge that does not exist. |
| `CR-TC-BACKFILL-02` | W3B / Coordinator | **`PendingLedgerPort.record_pending` carries no connection and no window.** The port is called from inside `TXN-analysis-*`, so an implementation must open its own transaction: the pending row commits separately (safe direction — a spurious pending row is visible and abandonable; the reverse is the loss `I06` forbids) and on SQLite can wait out `busy_timeout`. It also omits `first_pending_window_id`, which the column requires NOT NULL. Suggested signature: `record_pending(connection, *, target_key, reason, first_pending_window_id)`. |
| `CR-TC-BACKFILL-08` | W3B | With `EngineBoundPendingLedger` available, `tests/integration/test_attempt_not_result.py::test_a_failed_item_is_recorded_in_the_pending_item_ledger` (`xfail(strict=True)`) can be turned real by wiring the port into that file's `ctx` fixture. That file is W3B's write set; this card proved the property in its own file instead. |
| `CR-TC-BACKFILL-06` | W4A / Coordinator | **Two insert sites for `pending_item_ledger`.** `publisher._write_pending` and `pending.record_pending` write the same row with the same arbiter. Two spellings of one write is how they drift; the publisher could call the module. |
| `CR-TC-BACKFILL-01` | PC04 / Coordinator | **`time-and-tags.md` §6.5 O-6.2 names an enum member that does not exist.** It says the re-added activation carries `entitlement = 'none'` and `entitlement_reason = 'already_consumed_for_subscription_identity'`. `entities.yaml`, the same file's §6.2 table, the shipped CHECK and fixture `j` all say `denied_already_consumed` with a Vietnamese explanation string. Resolved in favour of `entities.yaml` (which §6.2 itself defers to: *"tên và enum lấy nguyên văn entities.yaml"*); the prose oracle should be corrected. |
| `CR-TC-BACKFILL-04` | PC04 / Coordinator | **`tag.rescan_corpus` idempotency has nowhere durable to live.** `ports.yaml` requires idempotency on `request_id`; `ENT-rescan-ledger` has no column for it, and adding one would break `tests/contract/test_schema_matches_entities.py`, which asserts column-set equality in both directions. The registry is process-local (same disposition as `CR-TC-ANALYSIS-04`); the durable half is `ux_rescan_open`, which is tested. |
| `CR-TC-BACKFILL-07` | Coordinator | **No card implements `tag.create` / `tag.update` / `tag.delete` / `tag.list` / `tag.preview_matches`.** Card §4 lists them as *produces* but §3 grants no file to put a tag service or router in. Only the backfill **state effect** of `tag.create` is implemented (`open_activation`); the `tag` row itself is written as fixture data in the tests. |
| `CR-TC-BACKFILL-12` | Coordinator | `tag.rescan_corpus` has `transport: http` in `ports.yaml` but this card's §3 grants no router file, so no route is registered and `server/app/main.py` was not touched. The service function and its error envelope are ready for whichever card is given the router. |

Also carried forward, unchanged and not this card's to close: `CR-TC-REPORT-01`'s second half —
`report.tag_config_version_id → tag_config_version(id)` — because `tag_config_version` still has
no writer among the 19 cards.

---

## 5. Stop conditions

| ID | Outcome |
| --- | --- |
| `SG-01` | **Did not fire.** The card text says `CR-PC04-02` is "còn OPEN"; it is not. `contracts/reporting/time-and-tags.md` §6.2 and its §9 table both record it as **ĐÃ ĐÁP bởi PC02-FIX3**, and `entities.yaml` carries `subscription_identity_hash`, `entitlement`, `entitlement_reason` and `ux_backfill_subscription_consumed`. Verified against the pinned bytes, not against the card's prose. |
| `SG-02` | Respected. `tag.rescan_corpus` is not enabled by default anywhere; there is no scheduler hook and no default caller. |
| `SG-03` | Respected. `N` is read from `settings['reporting.backfill_days']`; an unconfigured value is `VALIDATION_ERROR`, never a default. Asserted behaviourally **and** over the module's AST. |
| `SG-STACK` | No framework choice was made. Everything used is already in the tree: SQLAlchemy Core, Alembic, pytest — all named by ADR-0011 and already used by the sibling cards. |
| `SG-G5` | Satisfied at the card level by the FC-P3 audit and the wait gate above. |
| `SG-PC09` | **FIRED** — see `CR-TC-BACKFILL-11`. The latest `acceptance/scenarios.yaml` was read before writing; SC22's oracle names two columns `ENT-pending-item-ledger` does not have. The oracle was not edited and was not implemented. |
| `SG-DENY` | Respected and tested: FE-11, FE-12, FE-23, FE-30 each answer `FORBIDDEN_EDGE` with the caller and callee in `details_safe`, and the refusal happens before any write (`#rescan_ledger` = 0 afterwards). The positive control — `MOD-web-ui` — is not refused. |
| `SG-HASH` | Clean, run twice; 22/22 match. |
| `SG-CONTRACT` | Fired twice in the non-blocking direction and both times the contract, fixture and expectation were left untouched: `CR-TC-BACKFILL-01` (a prose oracle naming a non-existent enum member) and `CR-TC-BACKFILL-09` (the fixture and the sibling implementation disagreeing, captured as a strict `xfail`). |
| `SG-EDGE` | Fired once: `MOD-tag-service → MOD-analysis-service` is not in `allowed_edges`, so the enqueue half of rescan was **not** implemented. `CR-TC-BACKFILL-03`. |

---

## 6. Completion claim

**Claim:** `IMPLEMENTATION_VERIFIED` for the scope below — and no further, because this is
`SELF_VALIDATION`, which `evidence/manifest.schema.json` caps at `CONTRACT_READY` for the
manifest record itself.

**Baseline:** spec `d35e1f2d…` (41770 B), plan `f65bb046…` (64915 B), pin epoch
`PC10-PIN-P3b-20260908`, 22 pinned contracts and fixtures matching byte for byte; implementation
revision = the six hashes in §1 on commit `fb3944a`.

**Requirements covered:** REQ-D28 (backfill exactly once per subscription), REQ-D29 and REQ-AC10
(late discovery is reported, not lost), REQ-AC06 (a tag edit calls no model), REQ-OQ04 (N as a
working value read from settings), REQ-S8.2-04, REQ-S10.4-03. Invariants `I06` and `I07`.

**Evidence manifest:** `evidence/runs/TC-backfill-pending-ledger-E1-20260907T220221Z.json`
(`EVM-TC-backfill-pending-ledger`), validated against `evidence/manifest.schema.json` with 0
errors.

**Observed result:** 52 tests of this card pass, 1 `xfail(strict=True)`, `ruff` and
`mypy --strict` clean, whole repository 990 passed / 0 failed / 18 pre-existing errors that
belong to `CR-TC-REPORT-09`.

**Not established.**

* The backfill widening **is not reachable in production**: `builder._candidates` does not union
  the third term, so no deployment consumes an entitlement today (`CR-TC-BACKFILL-05`). The
  tests compose this card's seam with the real builder and publisher, which proves the ledger
  semantics and the publish-time consumption — it does not prove the wiring exists.
* SC22's status is **conditional** on `CR-TC-BACKFILL-11`: it holds against fixture `e` and
  `entities.yaml`, and `acceptance/scenarios.yaml` says something the schema cannot express.
* `item_type` for a late discovery is currently `prior_reference`, contradicting fixture `e`
  (`CR-TC-BACKFILL-09`).
* The analysis-side pending write **does not share a transaction** with the analysis write
  (`CR-TC-BACKFILL-02`).
* No HTTP route exists for `tag.rescan_corpus`, so nothing was exercised over the wire.
* The `tag.*` mutation operations other than the backfill effect of `tag.create` are **NOT_RUN**.
* `backfill_ledger.tag_id` has no referential integrity (`CR-TC-BACKFILL-10`).
* Fixture `j`'s literal hashes are not recomputable from the §6.2 preimage — by design, per
  `acceptance/fixtures/reporting/README.md` §4 — so every hash claim here is about a *relation*.
* E3 / E4: **NOT_APPLICABLE** (card §8: "Không cần live").

**Open issues:** the twelve `CR-TC-BACKFILL-nn` above, of which `CR-TC-BACKFILL-11` is the one
that needs a decision before this card's SC22 claim can be accepted.

**Review type:** `SELF_VALIDATION`. No independent audit was performed and none is claimed.

---

*`PKT-TC-BACKFILL` · `worker-W4B` · `lease_released_at` 2026-09-07T22:10Z · ceiling claimed:
`IMPLEMENTATION_VERIFIED` for the scope in §6, `SELF_VALIDATION` only.*

---

# ADDENDUM — `PKT-TC-BACKFILL-FIX1` (lease `LEASE-TC-BACKFILL-e2`)

| Field | Value |
| --- | --- |
| trigger | Coordinator rulings in `…/packets/FIX-P4-wave-rulings.md` (`CR-TC-BACKFILL-05` → W4A adds `backfill_port`; `-10` FK stays withdrawn; `-11` SC22 → PC09), plus two dispatch addenda: repo-wide `ruff format`, and W3B's **measurement** of `CR-TC-BACKFILL-02` |
| gate | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md` shows the released `PKT-TC-REPORT-FIX1` addendum (`lease_released_at 2026-09-08T00:58Z`). Verified before the first write of this lease. |
| write set | `tests/integration/test_backfill_once.py`, `tests/integration/test_pending_survives_cursor.py`, `server/app/report/pending.py` (lease extension), `ruff format` on the five files this card authored, this addendum, one re-issued manifest |
| status | **`DONE_WITH_CONCERNS`** — one concern left and it is one line in another card's file (`CR-TC-BACKFILL-02b`, below) |
| next actor | Coordinator, then **W3B** (one call-site line, then flip their xfail) |
| lease_released_at | 2026-09-08T01:05Z |

## B.1 Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `tests/integration/test_backfill_once.py` | MODIFY | `64a14f62099583b31432319405ecca91166ba676775480fee360415a96661fa0` | 47822 |
| `tests/integration/test_pending_survives_cursor.py` | MODIFY | `118faad30d45f6aa873e170c77d888dde0479dcd3cf5d5f22e082d2a16b5f5c7` | 44853 |
| `server/app/report/pending.py` | MODIFY | `393c7aff184cf5879afb978551156684f5ea99da6a7772f28c10eb3aab47f905` | 17535 |
| `server/app/report/backfill.py` | MODIFY (format only) | `5dc8646394a8ca5d3de71ed4d84e423aaca988d990c38b9b059af2695b40fb21` | 24178 |
| `server/app/tags/rescan.py` | MODIFY (format only) | `d6c2f27167609a0a1564a1fb549a93ded8c13cd8e410bca82037a212b8aa4206` | 14095 |
| `server/migrations/versions/0013_tc_backfill_pending_ledger.py` | unchanged | `ca6a45f3c3ba9d1f2a6efb852ab10e09aa14a46ff54ec523f5e93561d6a9c656` | 9142 |
| `evidence/runs/TC-backfill-pending-ledger-E1-20260908T010136Z.json` | CREATE | validates, 0 errors | — |
| `evidence/runs/TC-backfill-pending-ledger-E1-20260907T220221Z.json` | → **`STALE`** | superseded by the row above; kept, not edited | — |

`server/app/report/backfill.py` needed **no logic change**: W4A adopted this card's
`plan_extension` / `entitlements_to_consume` signatures unchanged, so the only diff is
formatting. No file of another card was written.

## B.2 The positive path is now real (`CR-TC-BACKFILL-05`)

`build_with_extension` used to compose the two halves by hand — `build_report` for the
in-window snapshot, this card's `plan_extension` + `entitlements_to_consume`, then a
`dataclasses.replace` to graft the widened items on. That proved the ledger semantics and
**not** the wiring, which was the whole of the CR.

It now calls `build_report(..., backfill_port=ServiceBackfill())` and asserts what the real
builder produced: `selected_via_backfill` on the widened item, `coverage_note.backfill_applied_tag_ids
== [tag_v1]`, `backfill_ledger_ids_applied` from this card's own function — and, one step that
matters more than the rest, **`consumed_count == 0` after `build` and `1` after `publish`**,
because §6.4 condition 1 is the COMMIT and nothing else. The hand-rolled `works_in_extension`,
`_fmt` and `_backfill_item` helpers are gone; `apply_extension=False` now exercises the
builder's real `NoBackfill` default rather than skipping a code path.

`plan_for()` remains for the assertions that are genuinely about §6.3's *range* and should not
have to go through selection to be made.

## B.3 `CR-TC-BACKFILL-02` — fixed on this side, one line left on W3B's

W3B measured the defect instead of predicting it: `_fail_task` calls the port from inside an
open `TXN-analysis-*` write transaction; on SQLite the outer transaction holds RESERVED, so a
second connection's INSERT waits out `busy_timeout` and dies `database is locked` — 0.00 s
outside a transaction against 5.01 s to failure inside one.

Both adapters now take an optional `connection`. Given one, the pending row is written on the
caller's connection and so commits and rolls back with the analysis write. The engine-bound
fallback is kept, unchanged, for callers that genuinely have no transaction open.

`test_the_port_joins_the_callers_transaction_when_given_its_connection` asserts **both** sides
against a really held write lock with a 200 ms timeout: without `connection` the call still
raises `OperationalError` (the pinned shape W3B's `strict=True` xfail is written against, kept
intact on purpose), and with `connection` the row is invisible to a second connection before
the commit and present after it — which is the property a retry could never provide, because
the lock is held by the transaction the caller is still inside.

### `CR-TC-BACKFILL-02b` — the remaining line, and the measurement that sizes it

**W3B's xfail did not flip, and it was not expected to.** `server/app/analysis/service.py::_fail_task`
still calls `record_pending(target_key=…, reason=…)` with no connection, and that file is W3B's
write set, not this card's. Verified rather than assumed: the test still reports
`XFAIL … raises=OperationalError`.

The remaining work was then **measured**, not estimated. A scratch-only probe (no repo file
written) monkeypatched exactly that one call to pass `connection=connection` and re-ran W3B's
test:

```
[XPASS(strict)] CR-TC-BACKFILL-02: PendingLedgerPo…
```

So the fix is complete except for one line in `_fail_task`:

```python
ctx.pending_ledger.record_pending(
    target_key=task.target_key, reason=reason, connection=connection
)
```

W3B should make that change and flip the xfail to a real test. The `connection` parameter is
optional precisely so this needs no flag day: `pending.py` accepts both shapes today.

## B.4 `CR-TC-BACKFILL-09` premise re-checked after FIX1

Still valid, so the strict xfail stays. `publisher._write_first_announcements` continues to
filter on `item.item_type` and `candidate.target_kind` only — never on `summary_state` — so an
item carried while pending is still announced, and the late discovery still returns as
`prior_reference` against fixture `e`. W4A's FIX1 touched the builder, not this path.

## B.5 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `pytest tests/integration/test_backfill_once.py -p no:randomly -p no:cacheprovider --tb=no` | 0 | **27 passed** |
| `pytest tests/integration/test_pending_survives_cursor.py …` | 0 | **27 passed, 1 xfailed** |
| `pytest tests/integration/test_attempt_not_result.py … -rxX` | 0 | W3B's file green; the CR-02 xfail still `XFAIL` (see B.3) |
| `ruff check` (six files) | 0 | All checks passed |
| `ruff format --check` (six files) | 0 | 6 files already formatted |
| `ruff format --check .` (repo-wide) | 0 | **165 files already formatted, 0 would reformat** |
| `mypy` (`--strict`, `server/app`) | 0 | Success: no issues found in 64 source files |
| `pytest -p no:randomly -p no:cacheprovider --tb=no` (whole repository) | **0** | **1027 passed, 7 xfailed, 0 failed, 0 errors** |

The 18 setup errors of `CR-TC-REPORT-09` are **gone** — W5C fixed the stand-in in the same FIX
round. The whole repository now exits 0.

`ruff format --check` is recorded as a verification command from this addendum on, per the
Coordinator's instruction (same class as `F-A3-P3-01`). The four files it flagged were this
card's; they are formatted, and the two that remained afterwards were W6B's and were fixed by
W6B in the same round.

## B.6 Baseline drift — noted, not a stop

`SG-HASH` over the card §0 pins now reports **2 of 22 drifted**: `precode/baseline.json`
(`52af62c8…` → `e8cf3910…`) and `precode/decision-register.md` (`b26cf51a…` → `8d6a87fb…`).
This is the expected `OD-10` record with WP re-pinning, and the Coordinator's instruction was
to note it and not stop. The other 20 pins — including every contract and fixture this card
reasons from (`entities.yaml`, `time-and-tags.md`, `selection.md`, fixtures `e`/`j`/`k`,
`boundary/a`) — match byte for byte, so no oracle this card depends on moved. The re-issued
manifest records the new hashes rather than the pinned ones, and says why.

## B.7 Claim after FIX1

Unchanged in kind, stronger in scope: `IMPLEMENTATION_VERIFIED` for the card's scope,
`SELF_VALIDATION` only. What moved out of **not established** is the big one — the widening is
now reachable through the real builder and the entitlement is really spent at the real publish
commit. What remains there: `backfill_port` defaults to `NoBackfill`, so whether a deployment
widens depends on a job-service caller no card has written yet; `CR-TC-BACKFILL-02b` (one line);
`CR-TC-BACKFILL-09`; `CR-TC-BACKFILL-10` (FK, now a PC02 CR by ruling); `CR-TC-BACKFILL-11`
(SC22, now a PC09/PC04 CR by ruling, claim stays scoped); and the `tag.*` HTTP operations,
which no card in the 19 owns.

---

*`PKT-TC-BACKFILL-FIX1` · `worker-W4B` · `lease_released_at` 2026-09-08T01:05Z · ceiling
claimed: `IMPLEMENTATION_VERIFIED` for the scope in §6/B.7, `SELF_VALIDATION` only.*

---

# ADDENDUM 2 — `PKT-TC-BACKFILL-FIX2` (lease `LEASE-TC-BACKFILL-e3`)

| Field | Value |
| --- | --- |
| trigger | `PKT-TC-REPORT-FIX2` closed `CR-TC-BACKFILL-09` (audit finding `F-A3-P4-01`), so this card's `xfail(strict=True)` XPASSed and had to become a real assertion |
| gate | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md` shows the released `PKT-TC-REPORT-FIX2` addendum (`lease_released_at 2026-09-08T01:40Z`), and `publisher._write_first_announcements` now carries `if item.summary_state != SUMMARY_FINAL: continue`. Both verified before the first write. |
| write set | `tests/integration/test_pending_survives_cursor.py`, this addendum, one re-issued manifest |
| status | **`DONE`** for this card's own scope — no `xfail` remains in either of its test files, and every oracle card §8 names is a plain passing assertion. Two items stay open and neither is this card's to close: `CR-TC-BACKFILL-02b` (one line in W3B's file) and the `backfill_port` caller question. |
| next actor | Coordinator |
| lease_released_at | 2026-09-08T01:42Z |

## C.1 Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `tests/integration/test_pending_survives_cursor.py` | MODIFY | `a9912368c58a284b6a7bdb09b704e16d04463ea3634b0733879c543bbff92860` | 47484 |
| `evidence/runs/TC-backfill-pending-ledger-E1-20260908T013901Z.json` | CREATE | validates, 0 errors | — |
| `evidence/runs/TC-backfill-pending-ledger-E1-20260908T010136Z.json` | → **`STALE`** | superseded; kept, not edited | — |

Every other file of this card is byte-unchanged since Addendum 1: `backfill.py`
`5dc86463…`, `pending.py` `393c7aff…`, `rescan.py` `d6c2f271…`,
`0013_tc_backfill_pending_ledger.py` `ca6a45f3…`, `test_backfill_once.py` `64a14f62…`.
No file of another card was written.

## C.2 The flip, and why it is two tests rather than one

`test_fixture_e_the_late_discovery_is_still_a_new_discovery` is now a plain test. It asserts
more than the xfail did, because the xfail only had to name the one value that was wrong:

* `item_type == "new_discovery"` on the **column** and in the **read model** — written from two
  different places in the publisher, so they are two claims and not one;
* `first_announced_report_id IS NULL` — the field that would otherwise carry "already reported
  on day D" to the reader;
* `late_discovery is True` — the display label rides alongside the type, per §5.3;
* exactly **one** `first_announced_ledger` row for the work, pointing at **period 3** — the
  period that actually announced it, not the partial period that merely listed it (`I07`).

A second test, `test_the_partial_period_announced_nothing_it_could_not_show`, covers the
opposite failure mode: an implementation that stopped writing `first_announced_ledger` rows
altogether would also make the first test pass, and would break `I07` in the other direction by
letting a work be announced as new in every period forever. It asserts that after the partial
period 2 the announced set is exactly `{E2}` — the item that had its summary all along — while
`E1` is listed as a report item and not announced.

The `strict=True` is what made this sequence work: the fix announced itself as an XPASS instead
of the test sitting green in the wrong state, and the assertion never had to be weakened to
match the implementation. The test's docstring keeps that history, since the shape of the test
is the evidence for it.

## C.3 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `pytest tests/integration/test_backfill_once.py -p no:randomly -p no:cacheprovider --tb=no` | 0 | **27 passed** |
| `pytest tests/integration/test_pending_survives_cursor.py …` | 0 | **29 passed, 0 xfailed** |
| `ruff check` (six files) | 0 | All checks passed |
| `ruff format --check .` (repo-wide) | 0 | 165 files already formatted |
| `mypy` (`--strict`, `server/app`) | 0 | Success: no issues found in **87** source files |
| `pytest -p no:randomly -p no:cacheprovider --tb=no` (whole repository) | **0** | **1040 passed, 4 xfailed, 0 failed, 0 errors** |

## C.4 Baseline drift

`SG-HASH`: **20 of 22 match**. `precode/baseline.json` (`e8cf3910…`) and
`precode/decision-register.md` (`a38e2ce1…`, moved again since Addendum 1) are the `OD-10` /
WP re-pinning record the Coordinator instructed to note and not stop on. Every contract and
fixture this card reasons from is unmoved — `entities.yaml` `ebcf460f…`, `time-and-tags.md`
`70f4bc57…`, `selection.md`, fixtures `e`/`j`/`k`, `boundary/a`.

## C.5 What remains open

| Item | Owner | Note |
| --- | --- | --- |
| `CR-TC-BACKFILL-02b` | W3B | One line in `service.py::_fail_task` — pass `connection=connection`. Measured: a scratch probe of exactly that line gives `[XPASS(strict)]` on their test. |
| `backfill_port` caller | job service card | `build_report` defaults to `NoBackfill`, so whether a deployment widens depends on a caller no card owns yet. |
| `CR-TC-BACKFILL-10` | PC02 | `backfill_ledger.tag_id` FK stays withdrawn by ruling. |
| `CR-TC-BACKFILL-11` | PC09 / PC04 | SC22's oracle names two absent columns; claim stays scoped by ruling. |
| `CR-TC-BACKFILL-03/-04/-06/-07/-12` | various | Unchanged from the e1 handoff §4. |

**Closed since e1:** `CR-TC-BACKFILL-05` (FIX1, builder unions the widening),
`CR-TC-BACKFILL-09` / `F-A3-P4-01` (FIX2, this addendum),
`CR-TC-BACKFILL-02` on this card's side (FIX1, optional `connection`).

---

*`PKT-TC-BACKFILL-FIX2` · `worker-W4B` · `lease_released_at` 2026-09-08T01:42Z · ceiling
claimed: `IMPLEMENTATION_VERIFIED` for the card's scope, `SELF_VALIDATION` only.*
