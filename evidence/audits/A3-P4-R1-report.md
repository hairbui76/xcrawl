# AUDIT_REPORT `A3-P4-R1` — independent review of Phase 4 (M4/M5) + Phase 6 (M7/M8) — FC-P4

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P4-R1` · authority `AUTH-COORD-A3-P4-R1` (parent `AUTH-OWNER-20260908-11`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of all six card packets and the fix round. |
| candidate | `FC-P4`, 635 entries, `manifest_sha256 = 04d4215d36c153f41500e06489ed3c84f5b42f3049e19248979cecca51508a2a`, epoch `PC10-PIN-P4-20260908` |
| quiescence | Recomputed start and end: **635/635** identical, header hash reproduces. `git status --porcelain` **118** before and after; **0** `__pycache__` dirs. Not `STALE`. |

## 1. Regression — every Coordinator number reproduced

| Gate | Coordinator | Mine | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` | 1028 / 6 xfailed / 0 failed | **1028 passed, 6 xfailed, 0 failed** | REPRODUCED |
| `ruff check .` | clean | `All checks passed!` | REPRODUCED |
| `ruff format --check .` | 165 files clean | `165 files already formatted`, rc=0 | REPRODUCED |
| `uv run mypy` (CI scope) | Success, 64 files | `Success: no issues found in 64 source files` | REPRODUCED |
| web Vitest | 126/126 | **126 passed (6 files)** | REPRODUCED |
| web lint / tsc / codegen | clean | eslint+prettier clean, `tsc --noEmit` clean, generated client matches | REPRODUCED |
| `verify_cards.py` | 13/13, 3730 | **13 PASS / 0 FAIL, 3 730 assertions, 0 violations** @ `PC10-PIN-P4-20260908` | REPRODUCED |
| `e0_check.py` | 26/26 | **26 PASS · 0 FAIL · 0 violations** | REPRODUCED |
| OpenAPI 3.1 | — | `contracts/http/openapi.yaml: OK` | PASS |
| alembic | one head `0013` | one head, both branch orders | REPRODUCED |
| no-network | — | whole suite socket+DNS blocked: **rc=0, zero attempts** | PASS |

The no-network run mattered this round: `tools/backup_cli.py`, the report router and the jobs
router are new transports. Nothing in them reaches the network under test.

**Migrations.** `0010` report and `0010` scheduler both branch off `0009` and merge at `0011`;
`0012`, `0013` linear after. I built the schema from blank under **three** traversal orders
(default, report-first, scheduler-first) and hashed the whole `sqlite_master`: **one
signature, `920a1f09…`.** 48 tables.

**Schema vs contract, both directions, my own sweep (`PRAGMA table_xinfo`, so generated
columns are visible):** 48 tables, **every one declared by an entity**, and **0 column
differences in either direction**. W6B's two undeclared idempotency columns are genuinely
gone and nothing else undeclared exists. `0002b`'s tables are taken over, not recreated.

## 2. Oracles I re-derived rather than read

**Scheduler lease (`ux_assignment_lease_one_held`).** Not read — exercised. The index is
`UNIQUE (owner_id, job_id) WHERE state = 'held'`. Inserting a first `held` lease succeeds;
inserting a **second `held` lease for the same job by raw SQL** is refused by the database:
`UNIQUE constraint failed: assignment_lease.owner_id, assignment_lease.job_id`. The claim
"raw SQL refused by the index" is literally true, and the partial predicate is what lets a
released lease coexist.

**Publish CAS.** The arbiter is a real database constraint, not a read-then-write:
`ux_coverage_window_predecessor` — `UNIQUE (owner_id, predecessor_window_id) WHERE
predecessor_window_id IS NOT NULL` — plus `ux_coverage_window_bootstrap` for the first
window. Both exist on disk. The publisher's own docstring gives the right reason ("a
read-then-write check is a race: two builders that both read predecessor `P` both pass it"),
the loser catches `IntegrityError`, rolls back everything, and is aborted with
`cas_conflict` in a **separate** transaction — correct, since the losing transaction is
already discarded.

**`OD-20260908-10` items 1–3, in code.** Item 1: save without analysis writes the fixed
literal `SUMMARY_NOT_ANALYSED = "(chưa phân tích)"` into `content_vi`/`novelty_vi`/
`limitation_vi` with `evidence_level = post_only` — a constant, not inferred text — and my
schema sweep confirms **no undeclared column** was added to carry it. Item 2: `/save` is still
in the command allowlist. Item 3: `REPLY_COMMAND_REMINDER = "Ba lệnh khả dụng: /status,
/run_now, /save."` is returned for a non-command message from the linked chat.

## 3. Findings

### `F-A3-P4-01` — MEDIUM — a known defect in the report publisher sits under a claim that covers the requirement it breaks

`CR-TC-BACKFILL-09`: `publisher._write_first_announcements` writes a `first_announced_ledger`
row for **every** `new_discovery` work item **including ones whose `summary_state` is still
`pending`**. Period 3 therefore sees the item as already announced, and a genuine late
discovery comes back as `prior_reference` instead of `new_discovery` — which is fixture `e`'s
row oracle, i.e. REQ-D29 / REQ-AC09 / I07.

W4B found it, declared it precisely, named the one-condition fix (skip items whose
`summary_state` is `pending`) and captured it as `xfail(strict=True)` so it XPASSes the day it
is fixed. That part is exemplary — the defect is **not hidden**. What is wrong is its
disposition:

* it is **not ruled** — `FIX-P4-wave-rulings.md` rules on `CR-TC-BACKFILL-05/-10/-11` and
  `CR-TC-REPORT-04/-08/-09`, and **not** on `-09`;
* the owning card's handoff (`TC-report-coverage-publish-cas-handoff.md`) **never mentions
  it** — 0 occurrences — and its "Open issues" list is only the ten `CR-TC-REPORT-nn`;
* that card's claim lists **REQ-D29** and **I07** among *"Requirements covered"* and
  *"Invariants"*, and its "Not established" list does not mention first-announcement
  correctness.

So the card claims the requirement the defect breaks. The defect is in W4A's file, raised by
W4B against W4A, and W4A's record does not carry it.

**Remediation constraint:** either fix the one condition and drop the xfail (an XPASS is the
proof), or rule it explicitly and move REQ-D29 / I07 out of W4A's "covered" list into "not
established". Do not close it by editing fixture `e`. `OPEN`.

### `F-A3-P4-02` — MEDIUM — the type gate is now narrower than the codebase (answering the packet's question)

Reproduced: `mypy --strict server worker collector probe` gives **7 errors in 3 files** — 5 in
`server/tests/test_smoke.py` (a Phase-0 skeleton test) and 2 `import-untyped` for
`yaml`/`jsonschema` in `worker/app/adapter/{base,validate}.py`.

**My judgement on whether these should block: no, and the CI scope is defensible for *this*
candidate.** `pyproject.toml` sets `files = ["server/app"]`, and ADR-0011's ratified row says
`mypy --strict` **"cho lõi server"** — the server core. CI matches the ADR exactly, so nothing
in FC-P4 is in breach, and the two adapter errors are missing *stubs*, not type defects; the
fix is blocked only because the dev deps live in the root `pyproject.toml`, a skeleton file no
card may edit (`CR-TC-adapter-06`).

**But the bar itself has quietly stopped covering the product.** ADR-0011 was written when
`server/app` was the only production Python. Since then `worker/app`, `collector/app` and
`probe/` have shipped **23 production `.py` files** — the AI adapter, the collector, the probe
tooling — and **none of them is type-checked by any CI job**. That gap widened silently across
four phases; it is not something this wave's workers introduced, and it is not visible from
inside any single card.

**Remediation constraint:** an ADR-0011 amendment widening `files` (with the two `types-*` dev
deps added under the same change, since one is blocked on the other), not a per-card fix.
Should not block FC-P4. `OPEN`.

### `F-A3-P4-03` — LOW — one xfail reason survived the staleness sweep

`test_fixture_i_preserved_published_report_items` still reads *"needs the `report` and
`report_item` tables, owned by the reporting card (not in Phase 1 M1)"*. Both tables now exist
— I built them from the migrations and checked. The sweep that re-pointed the other stale
`pending TC-…` markers missed this one, most likely because it names the card in prose rather
than with the `pending TC-…` string the sweep matched.

Nothing is concealed: the marker is `run=True, strict=True` and the suite is green with it
xfailing, so the test genuinely still fails — but for a reason its text no longer states.
Fourth recurrence of this class (`F-A3R3-03`, `F-A3-P2-01`, `F-A3-P3-02`); worth a standing
check on xfail reasons rather than another per-round finding. `OPEN`.

**New findings: 3 — MEDIUM 2, LOW 1. HIGH 0.** I close nothing and supply no patches.

## 4. Per-card claim verdicts

| card | verdict |
| --- | --- |
| `TC-report-coverage-publish-cas` | **may stand, scoped — MINUS REQ-D29 / I07 first-announcement correctness**, which `F-A3-P4-01` shows is not established. The CAS itself, coverage windows and the four operations verify. |
| `TC-backfill-pending-ledger` | **may stand, scoped.** This is the card that found `CR-TC-BACKFILL-09` and declared it properly; the finding is against its disposition, not against this card. |
| `TC-ui-runs-three-states` | **may stand, scoped** — 126/126 Vitest, tsc and eslint clean; UI *render* review remains E4 `NOT_RUN`. |
| `TC-ui-reports-detail` | **may stand, scoped** — same basis and same `NOT_RUN`. |
| `TC-scheduler-lease-claim` | **may stand, scoped** — lease exclusivity verified by me at the database level, including the raw-SQL refusal. |
| `TC-backup-restore-drill` | **may stand, narrowed** — CLI-only by ruling (no router); the **real restore drill is E3 `NOT_RUN`**, so no claim exists that a restore has ever been performed. |

**Prior cards whose claim moved.** `TC-saved-snapshot`'s scope was *widened* by
`OD-20260908-10` item 1 (save permitted with no analysis); I verified the implementation uses
a fixed literal and no new column, so the widened claim is supported. The adapter/analysis/
embedding/tgauth/delivery fix addenda change no claim. The stale-xfail cleanup is real and
visible in the counts: 11 → 9 → **6** xfails across the last three epochs.

## 5. Overall

**PASS with one scoping condition.** Every number the Coordinator measured reproduces exactly,
the schema is order-independent and contract-exact in both directions, the two structural
oracles I re-derived (lease exclusivity, publish CAS) are enforced by real database
constraints rather than by application-level checks, and the whole suite runs clean with the
network physically blocked. The condition is `F-A3-P4-01`: `TC-report-coverage-publish-cas`
must not carry REQ-D29 / I07 as covered while `CR-TC-BACKFILL-09` stands unruled and unlisted
in its own handoff. That is a disposition and scoping fix, not a code emergency.

## 6. Residual

* `F-A3-P4-01…03` open; `F-A3R4-01`, `F-A3-P2-01`, `F-A3-P2-02` still open from earlier rounds.
* `CR-TC-BACKFILL-09`, `-11`, `CR-TC-REPORT-*` and the rest of the ~50 wave CRs remain the
  Coordinator's to dispose of; I reviewed the one that touches a claimed requirement.
* One `run=False` xfail (`CR-PC07-04` callback fixture); three `delivery.md` §3.4 facts still
  `BLOCKED_DEPENDENCY`; `MOD-telegram-adapter` hard-blocked.
* Both AI adapters still `enabled: false` on isolation; **E3/E4 remain 0 everywhere** — no live
  AI, Telegram or X call, no real restore drill, no UI render review, SP1 never run.
* `MOD-tag-service` has no card (`CR-TC-BACKFILL-07`); REQ-A2/REQ-A4 calibration still
  `uncalibrated`.
* Concurrency remains argued from structure plus the two index-level oracles above; there is
  still no multi-process race test.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
