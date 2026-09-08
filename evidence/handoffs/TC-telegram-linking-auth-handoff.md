# HANDOFF — `TC-telegram-linking-auth`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-TGAUTH` — card `agent-tasks/TC-telegram-linking-auth.md` (Phase 5, M6, plain-text scope `OD-20260908-09`) |
| worker principal | `worker-W5A` |
| authority_id | `AUTH-COORD-TC-TGAUTH` (parent `AUTH-OWNER-20260908-10`, record `packets/OWNER-DECISIONS-20260908-09.md`) |
| lease_id | `LEASE-TC-TGAUTH-e1` (exclusive on card §3 write set + Alembic revisions + one delimited include in `server/app/main.py` + handoff + evidence manifest) |
| pin epoch | `PC10-PIN-P3-20260908` — verified on disk before the first write (SG-HASH: 30/30 pinned files, 0 drift) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `CONTRACT_READY` for this card's scope. The card's ceiling is `IMPLEMENTATION_VERIFIED`, and a `SELF_VALIDATION` record cannot support that label (`agent_profile/protocol.md` §9, `evidence/manifest.schema.json` §x-maximum-claim-by-review-type). Raising it needs an independent audit over exactly the bytes listed below. |
| evidence manifest | `evidence/runs/TC-telegram-linking-auth-E1-20260907T192748Z.json` (`EV-E1-01-tc-telegram-linking-auth`, validates against `evidence/manifest.schema.json`, 0 errors) |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T19:45Z |

`DONE_WITH_CONCERNS` rather than `DONE` for one reason, and it is the card's own biggest
stop condition: **`CR-PC07-04` is still open**, so the whole `callback_data` / inline-keyboard
/ parse-mode half of `MOD-telegram-adapter` — including the button that `REQ-D38` describes
for Save — is `NOT_RUN (BLOCKED_DEPENDENCY)`. What was built is the plain-text scope the
Owner opened in `OD-20260908-09`, and nothing was implemented against a guessed number.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/telegram/ingress.py` | CREATE | ABSENT | `3ce33991684d34a3a0bf7106655f7c146f784d82ba8b3d372796d0688317a7f3` | 27859 |
| `server/app/telegram/commands.py` | CREATE | ABSENT | `0ac5f8ae72bf7b1e9f1cad2dd909b9e5c064e54685c5fc8d8bf0265d6b30cd61` | 18053 |
| `server/app/telegram/linking.py` | CREATE | ABSENT | `417794171076abcbc2b0c0fab5e868c6ece1971e76877d7f3533fbcb7d671ee9` | 25082 |
| `server/app/telegram/router.py` | CREATE | ABSENT | `0f6d7b1f72aafe19b97d30f50638f72c84b05e4a98500b52719eaefc37893bd4` | 10383 |
| `tests/contract/test_telegram_command_allowlist.py` | CREATE | ABSENT | `1827d669fd6a735c2de905eae12715e64e58d7b032f4a4c7628e86c27ed0f2c7` | 33144 |
| `tests/integration/test_link_code_once.py` | CREATE | ABSENT | `542aa82ccaaf1c90db32b4c3efc31f537b77cec967d9d5623cdcbaa1e0a41601` | 20080 |
| `tests/integration/test_unknown_chat_silent.py` | CREATE | ABSENT | `c1c57ecadb0c22c2fdac913454a7eedbbb754ffd592bd22a49fc82124385c092` | 17999 |
| `server/migrations/versions/0006_tc_telegram_linking_auth.py` | CREATE | ABSENT | `c6e84237cdae1ad9088cec5835913f08c0c8d7cd71e62b5f960aece19d2e8f68` | 8024 |
| `server/migrations/versions/0007_merge_phase3_5_heads.py` | CREATE | ABSENT | `31e8b1bd9197ec1298ce3ac3e6f4436ae7f0dc89388330529737828b6d65f2b7` | 1825 |
| `server/app/main.py` | MODIFY (one delimited include) | (see §1.1) | `8d534ebea326038a2633e07449a06bb5d71bd3828e9413850936320447cfcb59` | 11088 |
| `evidence/runs/TC-telegram-linking-auth-E1-20260907T192748Z.json` | CREATE | ABSENT | `b40149911a12c26066f9b9180919c3e85cd04b397138e731b632105139448474` | 19160 |
| `evidence/handoffs/TC-telegram-linking-auth-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified. `evidence/index.json` was **not** touched — see `CR-TC-TGAUTH-05`.

### 1.1 Write-set notes

1. **`server/app/main.py`** carries exactly one block, delimited
   `# >>> TC-telegram-linking-auth (MOD-telegram-adapter) >>>` …
   `# <<< TC-telegram-linking-auth <<<`, inserted immediately before the `/healthz` handler.
   The import sits inside the delimiters (F-A3R1-13). The after-hash above is the file as it
   stands at handoff; two sibling cards of this wave were writing their own include blocks
   into the same file concurrently, so the before-hash is not a stable single value and is
   deliberately not asserted here — the Coordinator should rehash the file as a whole.
2. **No `server/app/telegram/__init__.py`.** The write set is "card §3 exactly" and §3 lists
   four modules. `server/app/` is a regular package, so `server/app/telegram/` loads as a
   namespace portion; `mypy --strict` (with `namespace_packages = true`) is clean over it.
   Same choice, same reasoning, as `TC-research-connector-metadata`.
3. **Two Alembic revisions.** `0006_tc_telegram_linking_auth` creates the four tables
   `contracts/data/entities.yaml` assigns to `MOD-telegram-adapter` and nothing else.
   `0007_merge_phase3_5_heads` is a merge point with no DDL: three revisions of this wave
   branched off `0005` at once and `alembic upgrade head` fails outright with three heads.
   Sibling cards have since chained onto that merge; the head at handoff is a single
   revision, and `tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head`
   passes.

---

## 2. What the card asked for, and what is actually there

### 2.1 Ingress (`ingress.py`) — `telegram.receive_update`

`ING-01` the webhook secret is compared with `hmac.compare_digest`; missing **or**
unconfigured is `UNAUTHORIZED`, so a deployment that forgot to install the secret refuses
every update rather than accepting all of them. `ING-02` nothing in the payload is treated as
identity before that check passes. `ING-03` only `message` and `callback_query` are
recognised. `ING-04` `update_id` deduplicates through `ux_telegram_update_id`, and a replay
returns the first disposition with **no** second side effect — notably no second reply; a
concurrent duplicate that slips past the read is caught by the index and handled the same
way. `ING-06` updates older than `telegram_update_max_age` are dropped. `ING-07`/`ING-08` an
unlinked chat gets absolute silence.

The database work is one `BEGIN…COMMIT` and every outbound call happens after it returns
(SRC-PLAN §5.1). That ordering is what makes "outbound call count = 0" a measurement rather
than an assertion about intent.

### 2.2 Linking (`linking.py`) — the B09 exception, and nothing wider

Format first, then rate limit, then lookup. A message that is not a code is never compared
against stored state and writes **no** `telegram_link_attempt` row
(`ENT-telegram-link-attempt.forbidden`). Consuming is a CAS —
`UPDATE … WHERE state = 'active'` with `rowcount == 1` — so the second chat loses at the row,
and `ux_telegram_link_active` makes "one link in force" a property of the schema. Wrong,
expired, already-consumed and rate-limited are four different rows and one identical silence.
An unlinked chat's raw `chat_id` never reaches the disk; only `sha256(chat_id)` does, and a
test scans every text column of every table to prove it.

### 2.3 Commands (`commands.py`) — the closed allowlist

`CMD-status`, `CMD-run-now`, `CMD-save`, each bound to the one operation
`contracts/telegram/commands.yaml` gives it. `assert_no_resume_path()` asserts structurally
that no command and no trigger reaches `run.resume` (`FE-33`, `DC-TGC-01`). Reply text is
the contract's, verbatim, and a test compares the constants with the YAML.

### 2.4 Router (`router.py`) — three routes, no more

`POST /v1/telegram/webhook` (telegramIngressSecret, **always 204** for a transport-valid
update), `POST /v1/telegram/link-codes` and `DELETE /v1/telegram/link` (owner session **and**
CSRF in one requirement). `telegram.execute_command` and `telegram.consume_link_code` are
`transport: internal` and are deliberately not mounted; a test asserts their absence from
`app.routes`.

### 2.5 Interfaces the siblings integrate with (landed early, as asked)

* `server.app.telegram.linking`: `active_link`, `is_linked_chat`, `link_snapshot`,
  `issue_link_code`, `consume_link_code`, `unlink`, `LinkRow`, `LinkingPolicy`.
  **`TC-telegram-unknown-delivery`** reads `LinkRow.generation` to pin a delivery, and
  `unlink`/relink leave the revoked row in place so the pinned generation stays resolvable.
* `server.app.telegram.ingress`: `TelegramContext`, `TelegramSender` (plain text: `chat_id`
  and `text`, no third parameter), `RecordingSender`, `IngressOutcome`, `Disposition`.
* `server.app.telegram.commands`: `SaveCreatePort` / `SaveResult` — **`TC-saved-snapshot`**
  binds `CMD-save` by supplying an object with
  `create_save(*, owner_id, report_item_id, idempotency_key) -> SaveResult` on
  `TelegramContext.ports`. Nothing in this package writes a `saved_item`.

---

## 3. Verification

All records are `SELF_VALIDATION`. No line below is an independent audit.

| Command | Result | Exit |
| --- | --- | --- |
| `pytest tests/contract/test_telegram_command_allowlist.py -q` | **21 passed, 3 xfailed** | 0 |
| `pytest tests/integration/test_link_code_once.py -q` | **8 passed** | 0 |
| `pytest tests/integration/test_unknown_chat_silent.py -q` | **8 passed** | 0 |
| `pytest tests/contract/test_schema_matches_entities.py -q` | **10 passed** (the four `telegram_*` tables equal `entities.yaml` in both directions; one Alembic head) | 0 |
| `ruff check` + `ruff format --check` on this card's files | clean | 0 |
| `mypy` (server core, `--strict`) | `Success: no issues found in 49 source files` | 0 |

Exact commands, environment, input hashes and the oracle/observed pairs are in the evidence
manifest. Every run was offline: `network_access: false`, no bot token in the environment,
no Bot API call.

### 3.1 The four card §8 oracles, measured

| Oracle | Expected | Observed |
| --- | --- | --- |
| Fixture `h` — stranger sends `/status` | outbound = 0, 0 mutations, 0 replies, `run.list` calls = 0 | 0 / 0 / 0 / 0 |
| Fixture `i` — format gate | non-matching text ⇒ 0 lookups, 0 attempt rows; wrong code ⇒ silent, 1 attempt row; right code ⇒ 1 link, 1 reply | as expected |
| Fixture `g` — code used twice | second use silent, `COUNT(telegram_link active) = 1`, chat B does not take over | as expected |
| Fixture `l` — `/run_now` while `needs_user` | no resume, no second run, exactly 1 reply pointing into the app | as expected |
| Allowlist | exactly three, no fourth | 3, and `run.resume` unreachable |

### 3.2 Deliberately NOT_RUN

* **`NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`** — fixture `f-stale-callback-no-save`, the
  five-step `validation_order` of `CMD-save`, `SC46`, and every keyboard/parse-mode path.
  Marked `xfail(run=False)` with that reason in the contract suite, not skipped silently.
  What *is* proved is that the blocked path cannot be entered by accident: a `callback_query`
  is dropped, `save.create` is never called, no row moves, no reply is sent.
* **`pending TC-scheduler-lease-claim`** — `run.list` and `run.run_now` are exercised through
  the `contracts/ports.yaml` signature with a double; `server/app/job/service.py` does not
  exist. The server half of `RN-01` ("run stays `needs_user`, `run__status_changes = 0`") is
  NOT_RUN. Marked `xfail(run=False)`.
* **`pending TC-saved-snapshot`** — `save.create` likewise. The five-presses-one-row oracle
  belongs to that card. Marked `xfail(run=False)`.
* **E2** — no fault-injection run on the Telegram path; the `write_blocked` branch (EDGE-06)
  is implemented and covered only on its "no guard installed" side.
* **E3** — a real send to Telegram. Out of scope by card §8.

---

## 4. Change requests

| ID | Severity | Contract | Finding |
| --- | --- | --- | --- |
| `CR-TC-TGAUTH-01` | medium | `contracts/http/openapi.yaml` | `telegram.receive_update` declares `X-Schema-Version`, `X-Request-Id` and `Idempotency-Key` as **required** parameters (`components.parameters.*.required: true`). Telegram sends none of them — the Bot API sends only `X-Telegram-Bot-Api-Secret-Token`. Enforcing them literally would make the endpoint unusable against the real bot; ignoring them silently would diverge from the wire contract. **This implementation does not enforce them on the webhook** (it mints a correlation id in process memory and deduplicates on `update_id`, which is the operation's own declared idempotency key) and reports the divergence here rather than editing the contract. Requested: openapi marks the three headers not-required for this one path, or states the intended behaviour. |
| `CR-TC-TGAUTH-02` | medium | `contracts/telegram/commands.yaml` §3 `CMD-save` | The contract's only trigger for `CMD-save` is a callback button, which the plain-text scope (`OD-20260908-09`) cannot build while `CR-PC07-04` is open. To give the plain-text scope a Save path at all, this card maps the typed trigger `/save <report_item_id>` at the adapter layer — the same kind of adapter-level mapping the contract already anticipates for `CMD-run-now`. It adds no command and changes no contract. Requested: Owner confirms or replaces the trigger string when the callback path is unblocked. |
| `CR-TC-TGAUTH-03` | low | `contracts/http/openapi.yaml` | Card §7 lists `STORAGE_WRITE_FAILED` as an obligation of this card, and `telegram.issue_link_code` / `telegram.unlink` both declare a 503 for it — but `telegram.receive_update` declares no 503 (its responses are 204/401/403/409/422/429/500). A storage refusal on the webhook is therefore reported as `INTERNAL` (500), which at least makes Telegram retry rather than dropping the update. A test asserts the 503 is still absent, so closing this CR will surface as a failing assertion rather than as silence. |
| `CR-TC-TGAUTH-04` | medium | `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` vs `contracts/telegram/commands.yaml` | The sweep fixture's `expected.telegram_ingress_vi` says the three `UNAUTHORIZED_COMMAND` edges (FE-30/31/33) get **no reply at all**, citing `REQ-S11.3-02`/`AC-18`. But `commands.yaml` `silent_drop_summary` and `EDGE-05` say a **linked** chat that sends an out-of-allowlist string gets "một câu ngắn nêu ba lệnh khả dụng", and `REQ-S11.3-02`/`AC-18` are rules about *unlinked* chats. This implementation follows `commands.yaml` (the owning contract for command semantics) and records `UNAUTHORIZED_COMMAND` as the audit code with no domain mutation. Requested: a ruling on which text governs a **linked** chat; the fixture was not edited. |
| `CR-TC-TGAUTH-05` | low | `evidence/index.json` | Card §13 asks for the run to be registered in `evidence/index.json`, but that file is outside this card's write set and three cards of this wave were writing evidence concurrently — appending from here would have raced. The manifest is complete and self-describing at `evidence/runs/TC-telegram-linking-auth-E1-20260907T192748Z.json`; registration is left to the Coordinator. |

**Open stop conditions carried forward, unchanged:** `SG-01` (`CR-PC07-04`, the largest risk
in the Telegram package — three format facts still `KC`), `SG-03` (`CR-PC07-05`,
`telegram_update_max_age` PROVISIONAL 24 h), `SG-04` (`CR-PC07-03`, the constant-time rule is
still not in openapi — implemented anyway, per `secrets.md` §7). `SG-02` (`CR-PC07-01`) was
treated as the Owner-accepted working values it says it is: the three parameters are read
from settings and a test binds them to the contract, which does **not** make them final.

---

## 5. What this does not establish

Real Telegram behaviour (no Bot API call was made); the callback/button half of
`MOD-telegram-adapter`; the server side of `run.run_now` and `save.create`; delivery
cancellation on relink; behaviour under a real write-blocked store; and anything about
independent review — every record here is `SELF_VALIDATION`.

Two tests in `tests/integration/test_multipart_partial_receipt.py` were failing in the
whole-suite run at handoff time. That file belongs to `TC-telegram-unknown-delivery`, which
was still in flight; it is outside this card's scope and is reported, not touched.

---

*`PKT-TC-TGAUTH` · `worker-W5A` · pin epoch `PC10-PIN-P3-20260908` ·
`lease_released_at` 2026-09-07T19:45Z · claim `CONTRACT_READY` · no item here is an
independent audit.*

---

# ADDENDUM — `PKT-TC-TGAUTH-FIX1`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-TGAUTH-FIX1` · lease `LEASE-TC-TGAUTH-e2` (fencing 2) · worker `worker-W5A` |
| authority_id | `AUTH-COORD-TC-TGAUTH` (unchanged parent chain) |
| driven by | audit finding `F-A3-P3-02` (`…/scratchpad/audits/A3-P3-R1-report.md`) and `CR-TC-DELIVERY-09` |
| status | **`DONE`** · ceiling unchanged (`CONTRACT_READY`; `SELF_VALIDATION` cannot support `IMPLEMENTATION_VERIFIED`) |
| evidence | `evidence/runs/TC-telegram-linking-auth-E1-20260907T202140Z.json` (`EV-E1-02-…`, `PASS`, 0 schema errors). The previous record `EV-E1-01-…` is now `result: STALE` with a `stale_reason` naming this packet — it was true of bytes that no longer exist. |
| pin epoch | `PC10-PIN-P3-20260908` re-verified before the first write: 28/28 §0 rows + both source files, 0 drift |
| lease_released_at | 2026-09-07T20:30Z |

## A.1 Changes

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/telegram/ingress.py` | MODIFY | `3ce33991684d34a3a0bf7106655f7c146f784d82ba8b3d372796d0688317a7f3` | `354a8d174d3127d7374a0832c372a6487e4a44eecdfe106bfea491153bff82d6` | 30277 |
| `server/app/telegram/commands.py` | MODIFY | `0ac5f8ae72bf7b1e9f1cad2dd909b9e5c064e54685c5fc8d8bf0265d6b30cd61` | `a3c56856c470617ce9d12055b435ff3a5f4f695fafdccb9411ad4b0a86bca275` | 19894 |
| `tests/contract/test_telegram_command_allowlist.py` | MODIFY | `1827d669fd6a735c2de905eae12715e64e58d7b032f4a4c7628e86c27ed0f2c7` | `6c13c7a63a0db41a3182287a672ecd53caf44a821dd3f6b27f40228b3328fc3b` | 40477 |
| `tests/integration/test_unknown_chat_silent.py` | unchanged bytes (port double reformatted, then restored) | — | `c1c57ecadb0c22c2fdac913454a7eedbbb754ffd592bd22a49fc82124385c092` | 17999 |
| `evidence/runs/…-E1-20260907T192748Z.json` | MODIFY (→ `STALE`) | `b40149911a12c26066f9b9180919c3e85cd04b397138e731b632105139448474` | `9aeecbae9058747d036103b5a1d6597205875e39b4a18dea923c0a9675923843` | 20004 |
| `evidence/runs/…-E1-20260907T202140Z.json` | CREATE | ABSENT | `3c2f76b0ff913fe12deeb617b6586235abd79b8445826b3c8608401d6b99c873` | 22440 |
| `evidence/handoffs/TC-telegram-linking-auth-handoff.md` | MODIFY (this addendum) | — | (this file) | — |

`linking.py`, `router.py`, both migrations and `server/app/main.py` are **unchanged** —
`linking.py` `417794…1ee9`, `router.py` `0f6d7b…3bd4`, `0006` `c6e842…8f68`, `0007`
`31e8b1…f2b7`, `main.py` `8d534e…cb59`. No sibling card's file was touched.

## A.2 Item 1 — the save xfail is now a real test

`test_save_from_chat_against_the_real_saved_service` runs. It wires
`TC-saved-snapshot`'s own `server.app.saved.service.TelegramSaveAdapter` into
`CommandPorts.save_create` — W5B's object, not a copy of it here — and drives
`/save work:<ulid>` through the full ingress path twice. Real service, real
`TXN-save-target`, real database: **1** `saved_item`, **1** `saved_snapshot`, **0** orphan
snapshots, **2** replies (`Đã lưu.` then `Mục này đã có trong Saved.`), `save_channel =
'telegram'`. A second test asserts the adapter forwards a malformed argument instead of
parsing it, and that the refusal is `VALIDATION_ERROR` from `save.create` itself.

**Where it stops, exactly.** The argument carried is a **target reference**
(`work:<ulid>` / `post:<ulid>`), not the `report_item_id` the contract's `ii` names. Two
things are missing for that: the callback path (`CR-PC07-04`, still `KC`) and the
`report_item` table (`TC-report-coverage-publish-cas`, Phase 4). So `report_item_id → target`
resolution and the `lg`/`rv` staleness checks around it stay NOT_RUN. W5B reached the same
conclusion independently — their `TelegramSaveAdapter` docstring and `CR-TC-SAVED-07` say it
in the same words — which is why the port keeps the parameter name `report_item_id`: it is
the published interface their shipped adapter binds to, and renaming it broke their
`test_cmd_save_goes_through_this_service` on the first attempt. **New: `CR-TC-TGAUTH-06`** —
when `report_item` lands, `TelegramSaveAdapter` is the one place that changes.

One behaviour change came out of this: the Save idempotency key is now scoped to the target
(`tg-cmd:<argument>`) rather than to the press. `contracts/ports.yaml` `save.create` keys on
`owner_id + target_ref`, and a per-press key made the unique index the only arbiter of "five
presses, one row" — correct, but for the wrong reason.

## A.3 Item 2 — `send_message` returns the provider message id

`TelegramSender.send_message(*, chat_id: str, text: str) -> str`. **The new return type is
`str`**: the provider's `message_id`, as a string.

* `RecordingSender` returns deterministic ids `rec-1`, `rec-2`, … and keeps them in
  `.message_ids`. The prefix is deliberately unlike a Telegram id, so no test can pass by
  treating a recorded id as a real receipt.
* `HttpxTelegramSender` reads `result.message_id` from the 200 body and raises
  `TelegramError(INTERNAL)` if a 200 carries none — a receipt for a message nobody saw would
  be worse than an error.
* `IngressOutcome` gained `message_ids: tuple[str, ...]`, in send order; a silent path returns
  the empty tuple, which is the absence of a receipt rather than an empty one.

The signature still has no `parse_mode` and no `reply_markup` parameter, so the plain-text
stop condition is unchanged and its source-scanning test still passes.

## A.4 Item 3 — xfail discipline

`test_run_now_against_the_real_job_service` is now
`xfail(strict=True, run=True, reason="pending TC-scheduler-lease-claim …")`: when that card
lands it XPASSes loudly instead of staying a quiet green. The callback xfail
(`test_fixture_f_stale_callback_validation_order`) keeps `run=False` on purpose — it is not
waiting for a sibling card but for a **contract fact** (`CR-PC07-04`), and running a body
that cannot exist would say nothing. That is the one deliberate exception to the new rule and
it is named here rather than left to be noticed.

## A.5 Verification

| Command | Result | Exit |
| --- | --- | --- |
| `pytest tests/contract/test_telegram_command_allowlist.py -q` | **24 passed, 2 xfailed** | 0 |
| `pytest tests/integration/test_link_code_once.py -q` | **8 passed** | 0 |
| `pytest tests/integration/test_unknown_chat_silent.py -q` | **8 passed** | 0 |
| `pytest tests/contract/test_schema_matches_entities.py -q` | **10 passed** (one Alembic head) | 0 |
| `ruff check .` / `ruff format --check .` | clean / 134 files already formatted | 0 |
| `mypy` | `Success: no issues found in 49 source files` | 0 |
| `pytest` (whole suite) | **826 passed, 9 xfailed, 1 failed** | — |

The single whole-suite failure is
`tests/integration/test_multipart_partial_receipt.py::test_the_adapters_sender_can_report_a_provider_message_id`,
which is `xfail(strict=True)` in `TC-telegram-unknown-delivery`'s file and now **XPASSes**
because the id it was waiting for exists. That is exactly the signal the Coordinator said W5C
would act on; their file was not touched. `TC-saved-snapshot`'s
`test_cmd_save_goes_through_this_service` now **passes** against this package.

*`PKT-TC-TGAUTH-FIX1` · `worker-W5A` · `lease_released_at` 2026-09-07T20:30Z · claim
`CONTRACT_READY` · no item here is an independent audit.*

---

# ADDENDUM — `PKT-TC-TGAUTH-FIX2`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-TGAUTH-FIX2` · lease `LEASE-TC-TGAUTH-e3` (fencing 3) · worker `worker-W5A` |
| status | **`DONE`** · ceiling unchanged (`CONTRACT_READY`; `SELF_VALIDATION`) |
| evidence | `evidence/runs/TC-telegram-linking-auth-E1-20260908T004625Z.json` (`EV-E1-03-…`, `PASS`, 0 schema errors). `EV-E1-02-…` is now `result: STALE` with a `stale_reason` naming this packet. |
| pin epoch | `PC10-PIN-P3-20260908`, re-verified: 28/28 §0 rows, 0 drift |
| lease_released_at | 2026-09-08T01:00Z |

## B.1 Changes

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `tests/contract/test_telegram_command_allowlist.py` | MODIFY | `6c13c7a63a0db41a3182287a672ecd53caf44a821dd3f6b27f40228b3328fc3b` | `5ea8e6bd586c4b28d897b18488073e1b826189f06fad1dcc73a60f2c134fbc18` | 49310 |
| `tests/integration/test_unknown_chat_silent.py` | MODIFY | `c1c57ecadb0c22c2fdac913454a7eedbbb754ffd592bd22a49fc82124385c092` | `f08643629c8e40a120db26221e9a410f15652970368b5633335ec0b68f65301d` | 18732 |
| `evidence/runs/…-E1-20260907T202140Z.json` | MODIFY (→ `STALE`) | `3c2f76b0ff913fe12deeb617b6586235abd79b8445826b3c8608401d6b99c873` | `0ed19b5d28837672d7e9daa163fd16a9b2ad07a8a5f31aa3688ea1d2f40a46df` | 23080 |
| `evidence/runs/…-E1-20260908T004625Z.json` | CREATE | ABSENT | `1c3b281f7f1b637b538bf9a69adc8557186d0bb57318e4ea128eddfa54396dcb` | 24606 |
| `evidence/handoffs/TC-telegram-linking-auth-handoff.md` | MODIFY (this addendum) | — | (this file) | — |

**No product code changed.** `commands.py` (`a3c56856…a275`), `ingress.py` (`354a8d17…82d6`),
`linking.py` (`41779417…1ee9`), `router.py` (`0f6d7b1f…3bd4`), both migrations and
`server/app/main.py` are byte-identical to FIX1 — the lease's conditional permission to touch
`commands.py` was not needed, because the `RunNowPort` / `RunListPort` signatures already fit
`server.app.jobs.service` without changing either side. `tests/integration/test_link_code_once.py`
is unchanged (`542aa82c…1601`). No sibling card's file was touched.

## B.2 The run-now xfail is now four real tests

The premise no longer holds — `TC-scheduler-lease-claim` landed as
`server/app/jobs/service.py` — so `test_run_now_against_the_real_job_service` was **deleted**
rather than restated, and replaced by four tests driving `server.app.jobs.service` through
`JobContext` and the real `run` table:

* **`test_fixture_l_run_now_against_the_real_job_service`** — fixture `l`, end to end. A run is
  created through the real service and parked in `needs_user`; `/run_now` from the linked chat
  leaves **every column of the run row identical** (`run__status_changes: 0`), `COUNT(run) = 1`,
  `COUNT(assignment)` unchanged, and produces exactly one reply pointing into the app. It also
  asserts the job service was genuinely asked (`run_now_calls == 2`) — otherwise the test would
  also pass for an adapter that refused on its own and never called, which is a different
  system.
* **`test_run_now_with_no_active_run_queues_one_real_run`** — `RN-03`: one `manual`/`queued` run.
* **`test_run_now_twice_coalesces_onto_the_same_run`** — `RN-02`/`T-RUN-21`: the reply changes,
  the row count does not.
* **`test_status_against_the_real_job_service_mutates_nothing`** — `ST-01` through the real
  `run.list`.

The double-based `test_fixture_l_run_now_does_not_pass_a_needs_user_run` stays. It tests this
adapter's **mapping** (`created: False` + `status: needs_user` → `blocked_needs_user`) in
isolation, which is a different question from whether the two sides agree; both are now
asserted. One `xfail` remains in the card — the callback path — and it keeps `run=False`
because it waits on a **contract fact** (`CR-PC07-04`), not on a sibling card.

## B.3 A latent flake found and fixed while doing it

Both suites stamped `message.date` with a frozen `2026-09-07`. When the wall clock crossed
2026-09-08T00:00Z that timestamp aged past `telegram_update_max_age`, `ING-06` began dropping
those updates, and twelve tests failed. The behaviour was **correct**; the tests were wrong,
and worse than wrong: the ones asserting "nothing happened" would have kept passing for the
wrong reason. `_message` now stamps **now** by default; where a test pins the server clock it
pins the update's `date` to the same instant; and the age test sets both ends explicitly. Found
because this packet happened to run after midnight — recorded in the manifest's limitations so
the class of defect is visible rather than the incident.

## B.4 Owner decisions `OD-20260908-10`, items 2 and 3

Both close CRs this card raised, both in favour of what shipped, and neither needs a code
change:

* **Item 2** closes `CR-TC-TGAUTH-02`: `/save <id>` **stays** as the plain-text trigger until
  the inline button is feasible, mapped onto the existing `CMD-save`, with no new contract
  command. Still exactly three commands (`AMD-B10`).
* **Item 3** closes `CR-TC-TGAUTH-04`: a **linked** chat that sends text outside the allowlist
  gets the short three-command reminder; an **unlinked** chat stays silent with 0 outbound. The
  decision says the shipped code stands and the boundary-sweep fixture row is corrected in the
  next contract round (a CR for PC08) — so `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`
  is still, today, inconsistent with `commands.yaml` on this row, and this card did not touch it.

`CR-TC-TGAUTH-01`, `-03`, `-05` and `-06` remain open, as do `CR-PC07-01`, `-03`, `-04`, `-05`.

## B.5 Verification

| Command | Result | Exit |
| --- | --- | --- |
| `pytest tests/contract/test_telegram_command_allowlist.py -q` | **28 passed, 1 xfailed** | 0 |
| `pytest tests/integration/test_link_code_once.py -q` | **8 passed** | 0 |
| `pytest tests/integration/test_unknown_chat_silent.py -q` | **8 passed** | 0 |
| `pytest tests/contract/test_schema_matches_entities.py -q` | **10 passed** (one Alembic head) | 0 |
| `ruff check .` / `ruff format --check .` (this card's files) | clean / clean | 0 |
| `mypy` | `Success: no issues found in 64 source files` | 0 |
| `pytest` (whole suite) | **1022 passed, 7 xfailed, 0 failed, 0 error** | 0 |

The whole suite is green: the strict XPASS that FIX1 left in
`TC-telegram-unknown-delivery`'s file is gone — they un-xfailed it, as the Coordinator said
they would.

*`PKT-TC-TGAUTH-FIX2` · `worker-W5A` · `lease_released_at` 2026-09-08T01:00Z · claim
`CONTRACT_READY` · no item here is an independent audit.*

## B.6 Baseline drift observed at release — `STALE_BASELINE` for the *next* write

Re-checking `SG-HASH` at handoff, **two of the 28 pinned rows had drifted** while this packet
ran, both written by the `OD-20260908-10` decision round:

| Path | Card §0 pin | On disk at handoff |
| --- | --- | --- |
| `precode/baseline.json` | `ffd1efb3588f8750…` | `e8cf3910c6f23512…` |
| `precode/decision-register.md` | `058621d0649b798c…` | `8d6a87fb0569e4c3…` |

Reported, not absorbed. Per `SG-HASH` the pin epoch `PC10-PIN-P3-20260908` is now `STALE` and
**a further write to this card needs a new baseline** — the Coordinator's re-pin, not this
worker's judgement. This packet's *content* is unaffected: neither file is read by any line of
this card's code (they are decision minutes, not contracts `MOD-telegram-adapter` depends on),
and the 26 rows that matter — both Telegram contracts, `entities.yaml`, `ports.yaml`,
`errors.yaml`, `modules.yaml`, `capabilities.yaml`, `openapi.yaml`, `secrets.md`, the ADRs and
all seven fixtures — are byte-identical to the pin. The manifest records the **observed**
hashes with the drift spelled out, rather than the pinned ones, because a baseline block that
claims bytes that were not there is worse than one that admits what moved.

---

# ADDENDUM — `PKT-TC-TGAUTH-FIX3`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-TGAUTH-FIX3` · lease `LEASE-TC-TGAUTH-e4` (fencing 4) · worker `worker-W5A` |
| driven by | audit finding **`F-A3-P4R2-02`** (LOW) |
| status | **`DONE`** · ceiling unchanged (`CONTRACT_READY`; `SELF_VALIDATION`) |
| write set | handoff + manifest re-issue only. **No code, no test, no migration changed.** |
| governing manifest | `evidence/runs/TC-telegram-linking-auth-E1-20260908T015949Z.json` (`EV-E1-04-…`, `PASS`, 0 schema errors) |
| lease_released_at | 2026-09-08T02:05Z |

## C.1 The finding

`EV-E1-03-…` pinned `server/app/main.py` by whole-file sha256 in `artifacts` and named it in
`invalidated_by_paths`. That hash had already moved: siblings appended their own delimited
include blocks to the same file. The record was therefore stale for a reason that has nothing
to do with anything it asserts — no byte of this card's behaviour changed.

## C.2 Ruling, recorded for every card that follows

> **A card manifest must not pin the shared application factory `server/app/main.py` by
> whole-file hash, and must not list it in `invalidated_by_paths`. Pin only the card's own
> delimited include block — or omit the file entirely.**

The reason is that the file is shared **by design**: the Phase 1 dispatch rule tells every
card to append one clearly delimited block to it, so its hash is a function of how many
siblings have landed. A per-card record that pins it is asserting something it does not own
and cannot keep true.

What `EV-E1-04-…` pins instead is this card's own block —
`# >>> TC-telegram-linking-auth (MOD-telegram-adapter) >>>` … `# <<< TC-telegram-linking-auth <<<`,
**620 bytes, sha256 `cfa96b64eea978af6d105e26f191002b7adc9a13d34db3a1cd821fcb02a6c93b`** —
recorded in `baseline.implementation_revision`. `server/app/main.py` no longer appears in
`artifacts` or in `invalidated_by_paths`.

The trade-off is written into the manifest's own limitations rather than left implicit: a
change elsewhere in the factory (include order, the `create_app` signature) will **not** mark
this record stale, so it must not be read as evidence about the factory as a whole. That
evidence comes from the tests that mount the real application — `test_the_three_routes_are_mounted_and_no_internal_operation_is`,
`test_the_owner_routes_refuse_without_a_session`, `test_the_webhook_answers_204_even_when_it_stays_silent`,
`test_a_wrong_secret_processes_nothing_at_all` — all of which build `create_app()` and ran in
the command this record names.

## C.3 Verification

Re-run at 2026-09-08T01:59Z against current bytes: the three card suites together are
**44 passed, 1 xfailed**, exit 0. The one xfail is still the callback path
(`NOT_RUN`, `BLOCKED_DEPENDENCY CR-PC07-04`, `run=False`). Code, tests and migrations are
byte-identical to `PKT-TC-TGAUTH-FIX2`: ingress `354a8d17…82d6`, commands `a3c56856…a275`,
linking `41779417…1ee9`, router `0f6d7b1f…3bd4`, `0006` `c6e84237…8f68`, `0007` `31e8b1bd…f2b7`,
allowlist test `5ea8e6bd…c18`, unknown-chat test `f0864362…301d`, link-code test `542aa82c…1601`.

`EV-E1-03-…` is now `result: STALE` (`4a4c36737f04e184d2b84e12a7badce3bd89a32e84b8765e2c6adb18d45db960`,
26385 bytes) with a `stale_reason` naming this packet and this finding. The
`STALE_BASELINE` note of §B.6 still stands unchanged: the card's §0 pin epoch
`PC10-PIN-P3-20260908` needs a Coordinator re-pin before any further write, for the two
`precode/` files that `OD-20260908-10` moved.

*`PKT-TC-TGAUTH-FIX3` · `worker-W5A` · `lease_released_at` 2026-09-08T02:05Z · claim
`CONTRACT_READY` · no item here is an independent audit.*
