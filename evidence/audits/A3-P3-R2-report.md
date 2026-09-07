# AUDIT_REPORT `A3-P3-R2` — scoped verification of `F-A3-P3-01…03` (FC-P3 epoch 2)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P3-R2` · authority `AUTH-COORD-A3-P3-R2` (parent `AUTH-OWNER-20260908-10`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of all five FIX1 addenda. |
| candidate | `FC-P3` epoch 2, 545 entries, `manifest_sha256 = 41c475065793ee4ca5993a5ab1f98657fc23d617212ca1452475a9c90f76556a` |
| quiescence | Recomputed start and end: **545/545** identical, header hash reproduces. `git status --porcelain` **89** before and after. Not `STALE`. |
| fix diff | 5 added (re-issued manifests), 0 removed, 21 changed. **No `contracts/`, `acceptance/`, `precode/` or `agent-tasks/` file moved** — consistent with "pins unchanged"; `verify_cards` still reports epoch `PC10-PIN-P3b-20260908` with the same 3 685 assertions. |

## 1. Regression on e2 (verified, not inherited)

| Gate | Coordinator | Mine | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` | 827 / 9 xfailed / 0 failed | **827 passed, 9 xfailed, 0 failed** | REPRODUCED |
| `ruff check .` | clean | `All checks passed!` rc=0 | REPRODUCED |
| **`ruff format --check .`** | clean, 134 files | **`134 files already formatted`, rc=0** | REPRODUCED |
| `mypy --strict` | — | `Success: no issues found in 49 source files` | PASS |
| `verify_cards.py` | 13/13, 3685 | **13 PASS / 0 FAIL, 3 685 assertions**, epoch `PC10-PIN-P3b-20260908` | REPRODUCED |
| `e0_check.py` | 25/25 | **25 PASS · 0 FAIL · 0 violations** | REPRODUCED |
| alembic | one head `0009` | `0009_tc_telegram_unknown_delivery (head)` | REPRODUCED |

**Socket-blocked run: I did repeat it, and it was the right call.** W5A changed
`server/app/telegram/ingress.py` — the module that holds the only live HTTP sender in the
Telegram path — so the previous round's no-network proof no longer covered the shipped bytes.
Whole suite under a total `socket`/`getaddrinfo`/`create_connection`/`gethostbyname` block:
**rc=0, 100%, zero network attempts.**

## 2. Finding verdicts

### `F-A3-P3-01` (MEDIUM, CI-red formatter) — **VERIFIED**

`ruff format --check .` is now **rc=0 over 134 files**; the CI step at
`.github/workflows/python.yml:38` and `Makefile:33` would pass. The addendum accepts the
finding without hedging — it states plainly that `ruff check` was run and recorded as "ruff
clean" while `ruff format --check` never was, that the two are separate required steps, and
that eleven peer handoffs recorded both. `ruff format --check` has been added to the card's
recorded verification set, so the fix lands in the command list and not only in the working
tree — which is the part that stops it recurring.

*Limitation, stated rather than glossed:* the packet asks me to confirm the four files changed
**only** in formatting. I never held the pre-fix bytes — they were untracked working-tree
files — so I cannot diff them and I do not assert semantic equivalence on my own authority.
What I can establish, and did: `mypy --strict` is clean over 49 source files; the full suite is
green at a strictly larger count; and the adapter's two test files now run **49** tests against
the re-issued manifest's `sample_size: 49`, consistent with the addendum's "47 before and
after the reformat" plus the two tests the `F-A3-P3-03` work added. The formatter-only claim is
therefore corroborated but rests on the worker's declaration for the AST-level part.

### `F-A3-P3-02` (LOW, stale/in-wave xfails) — **VERIFIED**, with one disclosed residual

Both in-wave xfails are gone; they are real, running, passing tests:

* `test_save_from_chat_against_the_real_saved_service` now imports
  `TelegramSaveAdapter` from `server.app.saved.service` — **W5B's own adapter, not a local
  double** — and drives `/save` twice through a real database: asserts exactly **one**
  `saved_item`, **one** `saved_snapshot`, **no orphan snapshot** (a `NOT EXISTS` join), and
  **two** replies (`Đã lưu.` then `Mục này đã có trong Saved.`), which is the plain-text half
  of `REQ-D38` / `EDGE-03`. Its docstring then states exactly where the proof stops
  (`report_item_id → target` resolution and the `rv`/`lg` staleness checks, pending
  `CR-PC07-04` and Phase 4's `report_item` table). That is the right shape: prove what exists,
  name what does not.
* `test_the_adapters_sender_can_report_a_provider_message_id` now pairs part id ↔ message id
  **by identity**, zipping the adapter's calls with the sender's ids (`strict=True`) and
  comparing against `part["provider_message_id"]` — not against a constant.

`test_run_now_against_the_real_job_service` was converted to a running strict xfail. The 9
remaining xfails are: `run_now` (scheduler-lease-claim, Phase 6 — `server.app.job.service`
genuinely absent), `pending_item_ledger` and `guard_blocks_before_publish_commit`
(report-coverage-publish-cas), `reconciliation clauses` (backup-restore-drill), the two
pre-existing `denied_edges` and two `identity_merge_audit` declared drifts, and the callback
fixture below.

**Residual, disclosed rather than waved through.** One `run=False` marker survives —
`test_fixture_f_stale_callback_validation_order`, `NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`.
It does not meet the packet's literal criterion ("every remaining xfail is `run=True` and
names a genuinely absent **card**"): it names a contract fact still `KC`, not a card. I judge
it acceptable and say why: implementing the five-step validator against a guessed 64-byte
budget is what card §10 `SG-01` forbids, and unlike the saved-service case this blocker
*cannot* resolve silently — clearing it moves `contracts/telegram/delivery.md` bytes, which
trips every card pin and forces a re-pin. The silent-staleness risk that motivated the finding
does not apply. The Coordinator may still prefer a running marker; that is a ruling, not a
defect.

*Observation:* `test_login_is_refused_while_storage_is_write_blocked` names
`TC-storage-write-blocked-readiness`, a card that shipped in Phase 1. It is `run=True,
strict=True`, so arrival would XPASS loudly — no silent staleness. Pre-existing and accepted
in `A3-R1`; unchanged here.

### `F-A3-P3-03` (LOW, silent fixtures) — **VERIFIED**

All four are now driven **by name from the fixture file**, through the shared loader, and each
is named in its owning card's handoff:

| fixture | test | loader call |
| --- | --- | --- |
| `ai/g-cli-json-embedded-in-prose` | `test_analysis_result_schema.py:494` | `load_fixture("ai/g-cli-json-embedded-in-prose")` |
| `recovery/f-secret-canary-injection` | `test_injection_canary.py:698` | `load_fixture("recovery/f-secret-canary-injection")` |
| `reporting/e-late-analysis-pending-then-late-discovery` | `test_analysis_once_per_key.py:743` | `fixture_loader(...)` |
| `reporting/m-density-worked-example` | `test_embedding_generation_guard.py:74` | `fixture_loader(DENSITY_FIXTURE)` |

No copies: each reads `acceptance/fixtures/**` through `tests/conftest.py`'s loader. The
adapter addendum is also honest about the diagnosis — `ai/g` was *already* reaching the
parametrised `ALL_AI_FIXTURES` sweep, so its payload was being validated; what was missing was
a reference **by name**, which is what made it invisible to my scan and to any reader.

## 3. Re-issued evidence manifests — **VERIFIED**

Five newest-per-card records (adapter `201840Z`, analysis `202638Z`, embedding `201528Z`,
tgauth `202140Z`, delivery `202901Z`). I re-hashed every `{path, sha256}` pair in all 24
manifests on disk:

* **every newest-per-card manifest: 0 mismatched pins**;
* all 24 validate against `evidence/manifest.schema.json` with **0 schema errors**;
* the five superseded records carry `result: "STALE"` and are **retained, not deleted**. The
  only mismatched pins anywhere are inside superseded records (storage `100943Z` 4, tgauth
  `192748Z` 3) — correct: a superseded record should keep the bytes it actually ran against.

I checked one thing that looked like a defect and found it was not: the adapter's superseded
record has an empty `artifacts` array. Empty `artifacts` turns out to be the pre-existing norm
— 20 of 24 manifests across every phase have it, current and superseded alike — so nothing was
stripped in this wave, and the file hashes live elsewhere in the record. Not a finding.

## 4. Per-card claim verdicts (restated)

| card | verdict |
| --- | --- |
| `TC-analysis-adapter-validation` | **may stand** — the `F-A3-P3-01` condition from R1 is **discharged**; `IMPLEMENTATION_VERIFIED` for the API and JSON-extraction paths, `CONTRACT_READY` for CLI/ACP, `REQ-AC16` `BLOCKED` |
| `TC-analysis-once-per-generation` | **may stand, scoped** |
| `TC-embedding-generation-switch` | **may stand, scoped** |
| `TC-telegram-linking-auth` | **may stand, scoped** to plain text; three §3.4 facts remain `BLOCKED_DEPENDENCY` |
| `TC-saved-snapshot` | **may stand, scoped** |
| `TC-telegram-unknown-delivery` | **may stand, scoped** |

The two scope verdicts from `A3-P3-R1` are unaffected and I re-checked the one that could have
moved: `ingress.py`/`commands.py` changed, and the plain-text surface is intact — the sender
signature still admits only `chat_id` and `text`, and the socket-blocked run is still clean.

## 5. Overall

**PASS.** All three findings verify on my own reproduction; the R1 condition on the candidate
is discharged and `FC-P3` epoch 2 is CI-clean as far as every gate I can run. **New findings:
0.** I close nothing — disposition remains the Coordinator's.

## 6. Residual

* One `run=False` xfail (`CR-PC07-04` callback fixture) — disclosed above; Coordinator's ruling.
* Three of five `contracts/telegram/delivery.md` §3.4 facts still `KC` / `BLOCKED_DEPENDENCY`;
  `MOD-telegram-adapter` stays hard-blocked. Next step is a range/offset fetch on the official
  URL — a tool amendment, not a new network grant.
* Both AI adapters remain `enabled: false` on **isolation** (ISO-03/ISO-05); E3 `NOT_RUN`.
* `TC-A5-01` covers Anthropic's terms only; arXiv/OpenAlex/X source policy is still open.
* SP1 has not run; every probe number remains `NOT_RUN`. E3/E4 are 0 everywhere.
* Concurrency remains argued from structure — no multi-process race test exists.
* Open from earlier rounds: `F-A3R4-01`, `F-A3-P2-01`, `F-A3-P2-02`.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
