# AUDIT_REPORT `A3-P3-R1` — independent review of Phase 3 (M3) + Phase 5 (M6 plain-text) — FC-P3

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P3-R1` · authority `AUTH-COORD-A3-P3-R1` (parent `AUTH-OWNER-20260908-10`) · lease null |
| reviewer | `auditor-A3` — authored nothing in the repo; no repo write this round. Independent of all six card packets and of the precode round. |
| candidate | `FC-P3`, 540 entries, `manifest_sha256 = 1c43507bc84a5f627ad2df0d6ad89d99e1b90a4c8ab05228c046280a6fb53db3`, epoch `PC10-PIN-P3b-20260908` |
| quiescence | Recomputed start and end: **540/540** identical, header hash reproduces. `git status --porcelain` **84** before and after. **Not `STALE`** — the declared freeze held. |
| delta vs `FC-P2` | 74 added, 0 removed, 44 changed (118 touched). |
| my network use | Four documentation GETs, all inside granted hosts (`core.telegram.org`, `www.anthropic.com`). No API host contacted. |

## 1. Regression — reproduced, with one exception

| Gate | Coordinator's measurement | Mine | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` | 817 / 11 xfailed / 0 failed | **817 passed, 11 xfailed, 0 failed** (98.8 s) | REPRODUCED |
| `ruff check .` | clean | `All checks passed!` | REPRODUCED |
| **`ruff format --check .`** | (reported as "ruff clean") | **FAILS, rc=1 — 4 files would be reformatted** | **NOT REPRODUCED — see `F-A3-P3-01`** |
| `mypy --strict` | — | `Success: no issues found in 49 source files` | PASS |
| `generate.py --check` | — | `generated tree matches a fresh run of the generator` | PASS |
| OpenAPI 3.1 | — | `contracts/http/openapi.yaml: OK` | PASS |
| `verify_cards.py` | 13/13, 3685 assertions | **13 PASS / 0 FAIL over 19 cards, 3 685 assertions, 0 violations**, epoch `PC10-PIN-P3b-20260908` | REPRODUCED |
| `e0_check.py` | 25/25 | **25 PASS · 0 FAIL · 0 violations** | REPRODUCED |
| alembic head | one, `0009_tc_telegram_unknown_delivery` | one head, confirmed from blank DB | REPRODUCED |
| no-network run | — | whole suite under a total socket/DNS block: **rc=0, zero network attempts** | PASS |

**Branch-order determinism.** I built the schema from a blank database under four traversal
orders (default, embedding-first, analysis-first, telegram-first) and hashed the complete
`sqlite_master`: **one signature, `8d485c5d…`, for all four.** The three parallel `0006`
revisions and the `0007` merge produce an order-independent schema.

**Migration ownership.** `0008` performs a real 12-step rebuild of `saved_snapshot` to add the
contract-declared FK, renaming `saved_item` out of the way first so SQLite rewrites the
child's `REFERENCES` correctly. `PRAGMA foreign_key_list(saved_snapshot)` confirms
`analysis_id_at_save → analysis(id)` and `owner_id → owner(id)`. `saved_item` is **not**
re-created — the `0002b` tables were taken over, as claimed.

**`entities.yaml` is wording-only.** I parsed the pre- and post-round documents and compared
every entity's fields (name, type, nullable, constraints) and keys: **zero structural
differences**, same version 0.2.0. This is the check the packet noted WP could not make.

`research-radar-spec.md` is byte-unchanged (`d35e1f2d…`). `contracts/` changed in exactly the
three declared files (`ai/providers.yaml`, `data/entities.yaml`, `telegram/delivery.md`).

## 2. Scope verdict — AI disabled by default: **VERIFIED**

`contracts/ai/providers.yaml` 0.2.0 registers exactly two entries, both `enabled: false`. No
file anywhere in the repo sets an adapter `enabled: true` — the three grep hits are prose.

I did not take the code's word for the refusal order. I loaded the **real registry** through
`load_registered_adapters()`, constructed each adapter with a transport whose `send()` raises
`AssertionError("TRANSPORT REACHED")`, and called the gate:

```
anthropic@claude-sonnet-5: refused -> AdapterError code=CAPABILITY_DENIED
                                     details={'module_id':'MOD-ai-adapter',
                                              'denied_capability_kind':'isolation_unverified'}
anthropic@claude-opus-5:   refused -> (identical)
```

The exploding transport was **never reached**. `_require_dispatchable()` is the first
statement of `run_inference_task`, ahead of task support, credential, endpoint, request build
and transport. `dispatchable` requires all three of `enabled`, `isolation_verified` and
`terms_outcome == PERMITTED_FOR_THIS_USE`, and `refusal_reason_code` names **isolation**, not
terms — the correct attribution, since the Owner did sign the terms (`OD-20260908-08`) and
isolation (ISO-03/ISO-05) is what actually holds these entries.

`usage.unknown` is enforced at the type level: `UsageReport` **raises** if `unknown` is true
and any token field is filled, and again if `unknown` is false and counts are missing (I14) —
three nulls, never zero. Tool requests are counted and discarded with no dispatcher on the
path, so `tool_calls_executed` stays 0 whatever the model asks for.

## 3. Scope verdict — Telegram plain-text only: **VERIFIED**

I grepped the whole diff, not the handoffs. Every hit for `parse_mode`, `reply_markup`,
`inline_keyboard`, `MarkdownV2` and `callback_data` across `server/app/telegram/`,
`server/app/delivery/`, `server/app/saved/`, `tests/`, `worker/`, `collector/`, `probe/` and
`shared/` is either documentation, a negation, or the inbound-update **kind**
`callback_query`. Structurally:

* `TelegramSender.send_message(*, chat_id: str, text: str)` — there is **no `parse_mode` and no
  `reply_markup` parameter to pass**; the live body is `{"chat_id": …, "text": …}` and nothing
  more. The signature is the enforcement.
* **No `callback_data` parser exists.** `callback_query` is recognised only so a linked chat's
  callback can be logged `DROPPED_INVALID` — the system sends no buttons, so no callback it
  produced can arrive.
* The blocked paths are marked `NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`, not stubbed.

**I reproduced the blocker myself.** Fetching `https://core.telegram.org/bots/api` returns
truncated content that stops before `Available methods`; `sendMessage` and
`InlineKeyboardButton` are unreachable. `contracts/telegram/delivery.md` §3.4 records exactly
this — seven anchors, eight calls, two rounds — and classifies it `BLOCKED_DEPENDENCY` for
**tool capability**, not `BLOCKED_SCOPE` and not "didn't look hard enough". Independently
confirmed.

The §3.4 record is unusually disciplined in two ways worth naming: it states that third-party
pages (n8n, grammY, a blog) **did** supply the missing numbers and were **deliberately not
used**, because `OD-20260908-07` forbids substituting a restatement for the source — even
though those numbers agree with the provisional assumption already in the code. And it
enumerates three things the 4096 figure does **not** establish (counting semantics, unit,
escape interaction), then derives a one-way safe inference for §3.5 rather than assuming.

## 4. Independent re-derivation from primary sources

| fact | as recorded | what I read first-hand | verdict |
| --- | --- | --- | --- |
| Telegram message length | `4096`, quoting `core.telegram.org/bots/tutorial` §Sending Messages | *"A `String` object containing the message text, 1-4096 characters."* | **CONFIRMED verbatim**, and from the page actually cited — not from the unreachable `/bots/api` |
| Anthropic `A5-3` (rights) | *"Customer (a) retains all rights to its Inputs, and (b) owns its Outputs."* | identical, `anthropic.com/legal/commercial-terms` | **CONFIRMED verbatim** |
| Anthropic `A5-5` (`TC-A5-01` basis) | *"Customer further represents and warrants that it has all rights and permissions required to submit Inputs to the Services."* | identical | **CONFIRMED verbatim** |
| Commercial Terms effective date | June 17, 2025 | June 17, 2025 | **CONFIRMED** |

`A5-5` is the clause the Owner's `TC-A5-01` warranty rests on, and it says what the record says
it says. The record is also right that this pushes an open question onto arXiv/OpenAlex/X
source policy, which `OD-20260908-08` explicitly does **not** resolve.

## 5. Lease-overlap incidents (`CR-PC00-32`) and undeclared writes

All six required register sections exist and each reads complete, with no truncation:
§8.14, §8.14.1, §8.14.2, §8.14.3, §8.15, §8.15.1. §8.14.3 in particular runs to a full
conclusion (six attempted routes, the size hypothesis, and a specific ask for the next round).
**I found no evidence of clobbering.**

One observation, not a finding: the packet's shorthand `CR-PC07-04/.a/.b` and
`CR-PC06-OQ03-01…08` does not match literal ids on disk — `CR-PC07-04` appears without `.a`/`.b`
suffixes, and only `CR-PC06-OQ03-01/-02/-08` exist. Having read the surrounding prose, these
read as the Coordinator's shorthand for sub-facts and rounds rather than missing records; the
sections are internally coherent and nothing dangles.

**Undeclared writes**: 118 paths touched; 7 are not named in any handoff/coordination/decision
file, and all 7 are Coordinator packaging artefacts self-identifying by name (the FC-P2
manifest, my own P2 packet copy, two owner-decision copies, the Phase-2 dispatch log, two E0
tool sidecars). None lies inside a card §3. No scope creep by any worker; no lease violation
visible on the final bytes.

## 6. Findings

### `F-A3-P3-01` — MEDIUM — the frozen candidate would fail CI: `ruff format --check` is red

```
Would reformat: tests/contract/test_analysis_result_schema.py
Would reformat: tests/integration/test_injection_canary.py
Would reformat: worker/app/adapter/api_provider.py
Would reformat: worker/app/adapter/validate.py
4 files would be reformatted, 130 files already formatted     (rc=1)
```

This is not a style preference: `uv run ruff format --check .` is a **required step** of the
`python` CI job (`.github/workflows/python.yml:38`) and of `make lint` (`Makefile:33`). A
commit of `FC-P3` as frozen fails that job.

Attribution is exact: **all four files are inside `TC-analysis-adapter-validation`'s §3 write
set**, and that card's handoff is the **only one of the twelve** in the repo that never ran
`ruff format` — every other card's handoff records it. So one worker skipped a gate its eleven
peers all ran, and nothing downstream caught it because `ruff check` (lint) *is* clean and the
two are easy to conflate. The Coordinator's pre-freeze "ruff clean" is true of `ruff check`
and false of `ruff format --check`.

**Remediation constraint:** run the formatter over those four files and re-freeze; the fix
must not be recorded as "no change" — the bytes move, so the epoch and the card pins move with
them. Worth adding `ruff format --check` to whatever pre-freeze script produced the "ruff
clean" line, so the two commands cannot be confused again. `OPEN`.

### `F-A3-P3-02` — LOW — two of the eleven xfails are not cross-phase, and one is already stale

The packet expects all eleven to be cross-phase (report-coverage-publish-cas /
scheduler-lease-claim / backup-restore-drill). Eleven is the right count and none hides an
in-wave failure, but two name cards that shipped **in this same wave**:

* `test_save_from_chat_against_the_real_saved_service` — reason *"pending TC-saved-snapshot"*.
  `TC-saved-snapshot` shipped in this wave; I confirmed `import server.app.saved.service`
  **succeeds**. The marker's premise is false at this epoch.
* `test_the_adapters_sender_can_report_a_provider_message_id` — reason *"pending
  TC-telegram-linking-auth"*. That card also shipped, though here the stated reason is still
  literally true (`TelegramSender.send_message` returns `None`).

The systemic part is the mechanism: all three `run=False` xfails live in
`tests/contract/test_telegram_command_allowlist.py`, and `run=False` means the body never
executes, so such a test can **never XPASS**. A dependency that arrives therefore never
announces itself — which is exactly what happened to the first one. The third (`job.service`)
is genuinely still absent and correct.

**Remediation constraint:** for a dependency-gated marker, prefer a running `xfail(strict=True)`
so arrival is loud; where `run=False` is unavoidable, the reason must name a condition someone
re-checks. `OPEN`.

### `F-A3-P3-03` — LOW — four §2 fixtures neither exercised nor recorded `NOT_RUN`

| fixture | card whose §2 names it |
| --- | --- |
| `acceptance/fixtures/ai/g-cli-json-embedded-in-prose.json` | `TC-analysis-adapter-validation` |
| `acceptance/fixtures/recovery/f-secret-canary-injection.json` | `TC-analysis-adapter-validation` |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | `TC-analysis-once-per-generation` |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | `TC-embedding-generation-switch` |

None is referenced by any test, and none is mentioned in the owning card's handoff (each
appears only in the pre-code PC handoff that created it). Dispatch rule 4: anything not run is
`NOT_RUN`. Coverage of the underlying scenarios is not necessarily missing — the canary
scenario, for instance, is exercised by a purpose-built `test_injection_canary.py` that
deliberately keeps no real canary in the repo — so the defect is the silence, not a hole.
Third recurrence of this class (`F-A3R1-09`, `F-A3-P2-01`); it may be worth a standing check
rather than a per-round finding. `OPEN`.

**New findings: 3 — MEDIUM 1, LOW 2. HIGH 0.** I close nothing and supply no patches.

## 7. Per-card claim verdicts

| card | claim | verdict |
| --- | --- | --- |
| `TC-analysis-adapter-validation` | `IMPLEMENTATION_VERIFIED` (API path); `CONTRACT_READY` for CLI/ACP, `REQ-AC16` BLOCKED | **may stand for behaviour, conditional on `F-A3-P3-01`** — the split of API vs CLI ceiling is honest and the disabled-by-default refusal is proven; but four of its files break a required CI gate, so the card is not release-clean as frozen |
| `TC-analysis-once-per-generation` | `IMPLEMENTATION_VERIFIED` | **may stand, scoped**; carry `F-A3-P3-03` |
| `TC-embedding-generation-switch` | `IMPLEMENTATION_VERIFIED` | **may stand, scoped**; carry `F-A3-P3-03` |
| `TC-telegram-linking-auth` | `IMPLEMENTATION_VERIFIED` | **may stand, scoped** to plain text; three §3.4 facts remain `BLOCKED_DEPENDENCY` |
| `TC-saved-snapshot` | `IMPLEMENTATION_VERIFIED` | **may stand, scoped** |
| `TC-telegram-unknown-delivery` | `IMPLEMENTATION_VERIFIED` | **may stand, scoped** |

## 8. Overall

**PASS with one condition.** Everything the Coordinator measured reproduces exactly —
817/11/0, e0 25/25, verify_cards 13/13 with 3 685 assertions at `PC10-PIN-P3b-20260908`, one
Alembic head — **except** `ruff format --check`, which is red on four files and would fail CI
(`F-A3-P3-01`). Both scope verdicts hold and were proven rather than read: the AI adapters
refuse from the real registry before any transport can be touched, and the Telegram surface
has no formatting affordance to misuse because the parameters do not exist. The four external
facts I re-derived myself — one Telegram, three Anthropic — match the recorded quotes verbatim.

I would not sign a commit of these bytes until the formatter runs; the behaviour is sound, the
gate is not.

## 9. Residual

* `F-A3-P3-01…03` open; `F-A3R4-01`, `F-A3-P2-01`, `F-A3-P2-02` still open from prior rounds.
* Three of five `contracts/telegram/delivery.md` §3.4 facts remain `KC` /
  `BLOCKED_DEPENDENCY` (`CR-PC07-04`): `callback_data` length, the parse-mode escape table,
  buttons per row. `MOD-telegram-adapter` stays hard-blocked. The next round needs a
  **range/offset fetch on the official URL** — a tool amendment, not a new network grant.
* Both AI adapters stay `enabled: false` on **isolation** (ISO-03/ISO-05), not terms. E3 is
  `NOT_RUN`; no live model call has ever happened.
* `TC-A5-01` is accepted by the Owner for Anthropic's terms, but whether arXiv/OpenAlex/X
  policy permits re-processing their content is a **separate, unanswered** question, and
  `OD-20260908-08` says so.
* SP1 has still not run; every probe number remains `NOT_RUN`.
* E3/E4 remain 0 everywhere. Concurrency is still argued from structure — no multi-process
  race test exists.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
