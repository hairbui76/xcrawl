# AUDIT_REPORT `A3-P4-R2` — scoped verification of `F-A3-P4-01…03` (FC-P4 epoch 2)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P4-R2` · authority `AUTH-COORD-A3-P4-R2` (parent `AUTH-OWNER-20260908-11`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of every FIX2 addendum. |
| candidate | `FC-P4` epoch 2, 645 entries, `manifest_sha256 = d6d507588c4c50aa05476dd03aa2e1656a256fc1e2b21d8ce7b760b3e73e8037`, epoch `PC10-PIN-P4b-20260908` |
| quiescence | Recomputed start and end: **645/645** identical, header hash reproduces. `git status --porcelain` **147** before and after. Not `STALE`. |
| fix diff | 10 added, 0 removed, 52 changed. |

## 1. Regression on e2

| Gate | Coordinator | Mine | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` | 1042 / 3 xfailed / 0 failed | **1042 passed, 3 xfailed, 0 failed** | REPRODUCED |
| `ruff check` / `format --check` | clean / 165 | `All checks passed!` / `165 files already formatted` | REPRODUCED |
| `uv run mypy` (widened) | Success, **87 files** | `Success: no issues found in 87 source files` | REPRODUCED |
| `verify_cards.py` | 13/13, 3730 @ P4b | **13 PASS, 3 730 assertions**, epoch `PC10-PIN-P4b-20260908` | REPRODUCED |
| `e0_check.py` | **27/27** (E0-21 live) | **27 PASS · 0 FAIL · 0 violations**, `E0-21-marker-reason-freshness` present | REPRODUCED |
| alembic / schema | one head `0013` | one head; schema-vs-entities still 0 differences | REPRODUCED |
| web | 126/126 + tsc + lint | **no `web/` byte changed since e1**, so my e1 run (126/126, tsc, eslint+prettier clean) stands on identical bytes | UNCHANGED |
| no-network | — | **repeated** (`auth/service.py`, `report/publisher.py` changed): rc=0, **zero attempts** | PASS |

**The 3 remaining xfails, listed as asked** — all `strict=True` contract/fixture-divergence
markers, none naming an absent card: `CR-PC07-04` (`test_fixture_f_stale_callback_validation_order`,
`run=False`, callback_data still `KC`); `CR-TC-AUTH-01` (`test_fixture_h_seq4_literal_expectation`,
`recovery/h` seq4 pins `FORBIDDEN_EDGE` where four sources say `CSRF_REJECTED`);
`CR-TC-IDENTITY-02` (`test_fixture_a_first_announced_literal_null`). The two stale ones from
R1 — `fixture_i` and `login_is_refused_while_storage_is_write_blocked` — are **gone**, now real
tests. 6 → 3.

## 2. Finding verdicts

### `F-A3-P4-01` — **VERIFIED**

`publisher._write_first_announcements` now carries `if item.summary_state != SUMMARY_FINAL:
continue`, so a pending item is not announced. The reasoning is grounded, not convenient: the
docstring derives the condition from `contracts/reporting/time-and-tags.md` **§5.3** third
bullet read against **§8.2 rule 2**, and I confirmed both clauses exist **verbatim in the
unchanged contract** — §5.3 *"`item_type` không đổi vì việc này: một mục phát hiện muộn chưa
từng được công bố vẫn là [new_discovery]"* and §8.2 *"Không có nhánh nào cho phép công bố lại
như phát hiện mới"*. Those two are simultaneously satisfiable only if a still-pending item is
never *announced* in the first place. **The contract was not edited to make the code pass** —
`time-and-tags.md` is byte-unchanged this round.

The disposition half is fixed too, which was the substance of the finding: W4A's handoff now
names `CR-TC-BACKFILL-09` (2 occurrences) and carries a section **"B.3 Correcting this card's
REQ-D29 / I07 coverage claim"**.

### `F-A3-P4-02` — **VERIFIED**

`pyproject.toml` now reads `files = ["server/app", "worker/app", "collector/app", "probe"]`
with `strict = true`, and `uv run mypy` is clean across **87** files (was 64). `types-PyYAML`
and `types-jsonschema` are in the dev group, closing `CR-TC-adapter-06` — the dependency that
was blocked because the deps live in a skeleton file no card may edit. `__pycache__/` is in
`.gitignore`. The CI step and Makefile targets are renamed truthfully ("mypy --strict (all
Python production trees)"), which matters because the original defect was a *name* that
promised more than the command did.

Test trees are excluded with a written reason (untyped pytest fixtures), and the one Phase-0
test named as kept strict-clean by hand is: I ran `mypy --strict` on
`server/tests/test_smoke.py` directly — **Success, no issues**. The claim checks out.

`ADR-0011` carries `AMD-ADR0011-01` in the file's own amendment convention
(`amendment_refs`, `decision_refs` including `F-A3-P4-02` and `CR-PC00-35`), and states in as
many words that it corrects a **fact**, not a technical choice.

### `F-A3-P4-03` — **VERIFIED**, with a gap in the new guard (`F-A3-P4R2-01`)

`test_fixture_i_preserved_published_report_items` is a real test now — no marker — running
against rows seeded by an actual `publish_report(context, snapshot)` call. `E0-21-marker-
reason-freshness` exists, is live in the 27-check run, and reports 0 violations on the current
bytes, which is truthful: the three surviving reasons all describe real divergences, and the
check deliberately does not flag those.

## 3. `CR-TC-AUTH-11` and the idle-slide (beyond the three findings)

**The bug was real and the fix is right, and I verified it by injecting the fault rather than
reading the diff.** `WRITE_FAILURES` now includes `sqlite3.Error` alongside `SQLAlchemyError`,
matching what ingest and identity already do — the gap was that a failure raised from a
connection-level event hook (how `server/app/db/faults.py` reproduces a full disk) arrives
*unwrapped*, so catching only `SQLAlchemyError` let it escape as an unhandled 500.

My harness: bootstrap an owner on a real migrated database, confirm a normal login succeeds,
then log in again under `WriteFaultInjector.disk_full()`:

```
baseline login: ok
AuthError code=ErrorCode.STORAGE_WRITE_FAILED http=503  -> CORRECT
```

No raw `sqlite3.Error` escapes. And the direction is contract-backed: I checked
`contracts/http/openapi.yaml` — `POST /v1/auth/login` declares **503**, so
`STORAGE_WRITE_FAILED` is the right code there.

**The best-effort idle-slide is also contract-driven, not a convenience.** `_slide()` is a
separate transaction that swallows `WRITE_FAILURES` and returns `False`. The justification is
checkable and I checked it: `GET /v1/auth/session` declares **`200 / 401 / 403 / 500` and no
503**, so a failed bookkeeping write must not turn a live session into
`STORAGE_WRITE_FAILED` — nor into the 500 it produced before the transaction was split out.
Extending the idle window is bookkeeping; the session's validity does not depend on it.

## 4. Re-issued manifests

18 of 19 newest-per-card manifests are **pin-clean and schema-valid**; superseded records are
retained. One exception, `F-A3-P4R2-02` below. Two superseded `ui-runs` records carry schema
errors (a CR-id pattern and a missing `stale_reason`), but they are superseded and not the
governing record, so I note rather than raise them.

## 5. New findings

### `F-A3-P4R2-01` — LOW — `E0-21` cannot see a single-line `reason=`

I mutation-tested the new check both directions on a scratch tree. It correctly parses the
multi-line forms — `reason=( "…" )` and `reason="…"` on its own line — but returns **nothing**
for the compact one-line form:

```
@pytest.mark.xfail(strict=True, reason="pending TC-saved-snapshot: does not exist yet")   -> []
```

`marker_reasons()`'s terminator regex is `(?:,\s*\w+\s*=|\)\s*$|\n\s*\))`; under `re.S` the
`$` anchors at end-of-string, so a closing paren in mid-file never terminates the match. A
textbook stale reason — naming a card whose handoff exists — therefore passes E0-21 unseen.
All three current markers use the multi-line form, so today's `0 violations` is honest; the
gap is prospective. The check's own "what it deliberately does NOT flag" paragraph lists one
known cost (a rotted reason with no absence marker) but not this one, so the disclosure is
narrower than the behaviour.
**Remediation:** parse the marker call by paren-matching (or `ast`) rather than a windowed
regex, re-run the mutation set, and extend the disclosure. `OPEN`.

### `F-A3-P4R2-02` — LOW — the newest tgauth manifest pins a stale `server/app/main.py`

`evidence/runs/TC-telegram-linking-auth-E1-20260908T004625Z.json` — the governing record for
that card — pins `server/app/main.py` at a sha256 that no longer matches disk. `main.py` is the
shared app factory every card appends an include to, so it moves after any single card's run;
that makes it the one file a per-card manifest can be expected to go stale on. Same class as
`F-A3R2-03`, which was fixed by re-issuing.
**Remediation:** either re-issue that manifest, or stop pinning the shared factory in per-card
records and say why. `OPEN`.

**New findings: 2 — LOW 2. MEDIUM 0 · HIGH 0.** I close nothing.

## 6. Per-card verdicts

| card | verdict |
| --- | --- |
| `TC-report-coverage-publish-cas` | **may stand, scoped — the R1 exclusion is LIFTED.** REQ-D29 / I07 are now supported by the contract-derived fix and an honest coverage correction. |
| `TC-backfill-pending-ledger` | **may stand, scoped.** |
| `TC-ui-runs-three-states` | **may stand, scoped**; UI render review still E4 `NOT_RUN`. |
| `TC-ui-reports-detail` | **may stand, scoped**; same `NOT_RUN`. |
| `TC-scheduler-lease-claim` | **may stand, scoped.** |
| `TC-backup-restore-drill` | **may stand, narrowed**; real restore drill still E3 `NOT_RUN`. |
| `TC-canonical-identity-merge` | **may stand, scoped** — fixture `i` is a real test now; one strict marker (`CR-TC-IDENTITY-02`) remains a declared contract divergence. |
| `TC-owner-auth-session` | **may stand, scoped** — strengthened this round: a real bug (`CR-TC-AUTH-11`) found, fixed and independently reproduced by me, the self-fulfilling xfail replaced by real tests, and the idle-slide made best-effort on the wire contract's terms. Carries `F-A3-P4R2-02`. |

## 7. Overall

**PASS.** All three findings verify on my own reproduction; the R1 scoping condition on
`TC-report-coverage-publish-cas` is discharged; `CR-TC-AUTH-11` was a genuine bug, correctly
fixed, and I confirmed the corrected behaviour by fault injection rather than by reading. The
two new findings are both LOW and neither touches shipped behaviour.

## 8. Residual

* `F-A3-P4R2-01/-02` open; `F-A3R4-01`, `F-A3-P2-01`, `F-A3-P2-02` still open from earlier rounds.
* Three strict xfails remain, all declared contract/fixture divergences (`CR-PC07-04`,
  `CR-TC-AUTH-01`, `CR-TC-IDENTITY-02`); three `delivery.md` §3.4 facts still
  `BLOCKED_DEPENDENCY`; `MOD-telegram-adapter` hard-blocked.
* Both AI adapters `enabled: false` on isolation. **E3/E4 remain 0 everywhere** — no live AI,
  Telegram or X call, no real restore drill, no UI render review, SP1 never run.
* `MOD-tag-service` still has no card (`CR-TC-BACKFILL-07`); REQ-A2/REQ-A4 `uncalibrated`.
* Concurrency: structure plus the two index-level oracles from R1; still no multi-process race test.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
