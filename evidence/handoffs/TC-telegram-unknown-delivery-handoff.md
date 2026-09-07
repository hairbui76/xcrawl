# HANDOFF — `TC-telegram-unknown-delivery`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-DELIVERY` — card `agent-tasks/TC-telegram-unknown-delivery.md` (Phase 5, M6, plain-text scope `OD-20260908-09`) |
| worker principal | `worker-W5C` |
| authority_id | `AUTH-COORD-TC-DELIVERY` (parent `AUTH-OWNER-20260908-10`, record `packets/OWNER-DECISIONS-20260908-09.md`) |
| lease_id | `LEASE-TC-DELIVERY-e1` (exclusive on card §3 write set + one Alembic revision + handoff + evidence manifest + one delimited include block in `server/app/main.py`) |
| pin epoch | `PC10-PIN-P3-20260908` — verified twice (before the first write and again at handoff): **30/30 pinned files match byte for byte, 0 drift** |
| status | **`DONE_WITH_CONCERNS`** — everything the card asks for exists and runs; nine `CR-TC-DELIVERY-nn` items are open, four of them contract defects that shaped the implementation |
| completion_claim | see §6. The card's ceiling is `IMPLEMENTATION_VERIFIED`; this record is `SELF_VALIDATION`, which the evidence schema caps at `CONTRACT_READY`, so the manifest claims that and no more |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T19:45Z |

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/delivery/__init__.py` | CREATE | ABSENT | `bd6956ddd1fa4555fa2080e8e90b6f30e5b5c1487e2e6914a52b6e635000da5e` | 1302 |
| `server/app/delivery/service.py` | CREATE | ABSENT | `1825a79e953c75aa26c0f947aa77b6bc11e3abffd509de53b5e616ec84edeb08` | 64896 |
| `server/app/delivery/parts.py` | CREATE | ABSENT | `6f388d833072ccced4254d8455339f0dba173c36dc35615fb666a5f19c73d1d5` | 10844 |
| `server/app/delivery/outbox.py` | CREATE | ABSENT | `0610ec6f3869f878bdf1daa2beef6f4d3d7f0924a1f7aa614095349cd923d88a` | 27952 |
| `server/app/delivery/router.py` | CREATE | ABSENT | `37482f0689eba2b851200ebe82381d47e2046b2e365053dde352f9af6eecee47` | 9825 |
| `server/migrations/versions/0009_tc_telegram_unknown_delivery.py` | CREATE | ABSENT | `90a80155de1a775c3d49d5030a932d020b036005f03eb275a5da4d4da336fd9c` | 10658 |
| `tests/integration/test_delivery_unknown_no_retry.py` | CREATE | ABSENT | `21eec633371b3bce9dd9936b092a12b8b002aa7dcf7e7dbee32e9698192cebd3` | 24181 |
| `tests/integration/test_multipart_partial_receipt.py` | CREATE | ABSENT | `c5c59e68c3579fa83af053572abe90962800de822a85cf59fa2de257507014e3` | 17191 |
| `tests/integration/test_permanent_failure_report_intact.py` | CREATE | ABSENT | `50e0a44eaa03f4a7f7e054fb0deb8a8adcad4abdc072ae2cc3163afad6bb5adb` | 20033 |
| `server/app/main.py` | MODIFY (one include block) | (shared file, see §1.1) | `8d534ebea326038a2633e07449a06bb5d71bd3828e9413850936320447cfcb59` | 11088 |
| `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` | CREATE | ABSENT | `a79b766b1cf281ecf917545ef7cbb7746907d103823782d133dffb259a204eb0` | 17266 |
| `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified. No git command that mutates anything was run. No live Telegram
call, no AI provider call, no browser, no secret.

### 1.1 Write-set notes

1. **`server/app/main.py`** carries exactly one delimited block,
   `# >>> TC-telegram-unknown-delivery … # <<< TC-telegram-unknown-delivery`, with the import
   inside the delimiters (`F-A3R1-13`). It calls `install_delivery(app)` with **no** context,
   so a deployment that wires none gets `500 INTERNAL` from the router rather than a router
   that invents a database connection or a Telegram transport. Other cards' blocks were not
   touched. The file's before-hash is not pinned here because three sibling packets of this
   same wave were appending to it concurrently; the after-hash above is the state at handoff.
2. **`server/app/delivery/__init__.py`** is not in the card's §3 table. It is a package
   marker carrying the module docstring, added for parity with `server/app/identity/` and
   `server/app/ingest/`, both of which have one. Reported rather than assumed: if the
   Coordinator reads the write set strictly, deleting it is a one-line packet — the imports
   resolve either way (`server/app/` is a regular package, so the subdirectory would load as
   a namespace portion).
3. **The Alembic revision** is authorised by the dispatch ("plus your Alembic revision(s) …
   must keep ONE head"). It landed **after** three siblings, so it chains onto the head that
   existed at commit time, `0008_tc_saved_snapshot`, rather than adding a fourth branch that
   someone else would have to merge. `alembic get_heads()` returns exactly
   `['0009_tc_telegram_unknown_delivery']`, and the standing gate
   `tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head` passes.
4. **Five tables**, and exactly the five `contracts/data/entities.yaml` assigns to
   `MOD-delivery-service`: `outbox_intent`, `delivery`, `delivery_part`, `delivery_attempt`,
   `delivery_receipt`. No table belonging to another module was created, dropped or rebuilt.

---

## 2. What was built, against which contract row

| Contract row | Where it lives | How it is measured |
| --- | --- | --- |
| `T-DL-00` intent in the publish transaction | `service.create_intent(connection=…)` takes the **caller's** open connection | the intent and the delivery row are committed by the caller's commit; a test seeds through the same path |
| `T-DL-01` attempt row **before** the network call | `service._prepare_dispatch` — the `engine.begin()` block closes before `transport.send_payload` is called | `test_attempt_row_is_committed_before_the_network_call`: the transport reads the DB *during* the send on a separate connection and sees 1 attempt, part `sending`, 0 receipts |
| `T-DL-02` receipt, then retries only return it | `service.record_receipt`, idempotent on `delivery_part_id` | second call returns `created: False` and `COUNT(delivery_receipt) == 1` |
| `T-DL-03` retryable → `retry_wait` | `service._retry_wait` + `backoff_seconds` | `retry_not_due` before the backoff elapses, `sent` after |
| `T-DL-04` uncertain → `unknown`, no auto retry | `service.mark_unknown`, plus the intent parked `held_for_review` | outbound call count frozen at 1 across five further dispatch turns and a 7-day clock jump |
| `T-DL-05` retry due | same `logical_delivery_key`, same `delivery_part_id` | `COUNT(delivery WHERE report_id = R) == 1` after retries |
| `T-DL-06` only the operator leaves `unknown` | `service.decide_unknown`, the **only** caller of `held_for_review → ready` | three decisions asserted; resend refused without `duplicate_risk_accepted` |
| `T-DL-07` budget/window exhausted → `failed` | checked before the attempt row is written | 4 outbound calls, then `failed`; `report` and `run` untouched |
| `T-DL-08` unlink/relink → `cancelled` | generation captured at intent creation, compared before every send | 0 outbound calls, 0 attempts, `cancelled` |
| `T-DL-09` restore locks the dispatcher | `StorageGuard.assert_writable(DELIVERY_DISPATCH_NEXT)` | `RESTORE_UNVERIFIED`, 0 outbound calls, `reconciliation_complete` still `False` |
| `DP-01`/`DP-04` parts | `outbox.insert_part` + `ux_delivery_part_index` | fixture `telegram/a` row counts |
| `DP-02` an `unknown` part is never resent | `_pick_part` skips `unknown`; `claim_intent` never claims `held_for_review` | two independent mechanisms, both asserted |
| `DP-03` aggregate precedence | `parts.aggregate_state` | unit assertions plus the fixture's aggregate |
| §3.5 splitting | `parts.split_plain_text` | never cuts a block; every part ≤ 4096 under **both** counting units |
| `REQ-AC04` one alert per run | partial UNIQUE `ux_outbox_alert_per_run` | enforced by the database, not by a code path |

### 2.1 The 4096 rule, and the one inference made from it

`contracts/telegram/delivery.md` §3.4(c) says the counting **unit** has no source: Unicode
scalars and UTF-16 code units differ for characters outside the BMP, and §3.4 forbids writing
a margin number into the contract while the source is unread. `parts.message_length` therefore
reports the **larger** of the two readings and the 4096 limit is applied to that. A part that
fits under the pessimistic reading fits under both. That is a one-directional safe inference,
not a guess about the number, and no margin constant was invented.

### 2.2 What was deliberately NOT built (binding stop condition, `OD-20260908-09`)

No `parse_mode`, no inline keyboard, no `callback_data`, no multipart branch depending on an
unresolved fact. `TelegramTransport.send_payload` has four parameters and none of them is
markup, which is the enforcement: those payloads cannot be built from any call site. The Save
button of `contracts/telegram/delivery.md` §3.1 item 3 and §8 therefore **does not exist**,
and the tests that would exercise it are recorded **`NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)`**
— not skipped, not faked.

---

## 3. Dependencies that were absent, and how each was handled

| Dependency | Status | What was done |
| --- | --- | --- |
| `TC-report-coverage-publish-cas` (Phase 4) | absent | the published payload arrives through `ReportPayloadPort`; tests use a fake report row and a three-column `report` stand-in table created with `IF NOT EXISTS`, clearly labelled as not `ENT-report` |
| `TC-backup-restore-drill` (Phase 6) | absent | the "dispatch locked until reconciled" check runs against `StorageGuard`, whose `reconciliation_complete` safely answers `False` for every restore; the drill-driven clause-list test is `xfail(strict)` |
| `TC-telegram-linking-auth` (W5A) | **landed** | integrated for real: `test_link_generation_comes_from_the_adapters_own_table` reads the actual `telegram_link` row through `server.app.telegram.linking.active_link`. The adapter that does so lives in the **test**, not in `server/app/delivery/` — see `CR-TC-DELIVERY-07`. One `xfail(strict)` remains for the response half (`CR-TC-DELIVERY-09`) |
| `TC-scheduler-lease-claim` (Phase 6) | absent | not needed by this card; the `run` table is a two-column stand-in in one test, and delivery writes to neither `run` nor `report` (asserted structurally) |

---

## 4. Verification

Commands run, verbatim, from `/mnt/virtual/repo/xcrawl` with `PYTHONDONTWRITEBYTECODE=1`:

```
uv run pytest -p no:cacheprovider tests/integration/test_delivery_unknown_no_retry.py \
  tests/integration/test_multipart_partial_receipt.py \
  tests/integration/test_permanent_failure_report_intact.py
uv run pytest -p no:cacheprovider                      # whole repo
uv run ruff check .        &&  uv run ruff format --check .
uv run mypy                                            # --strict over server/app
```

| Run | Result |
| --- | --- |
| the three card tests | **29 tests: 27 passed, 2 xfailed (strict), 0 failed, 0 error, exit 0** |
| whole repository suite | **828 tests, 0 failed, 0 error, 11 skipped/xfailed, exit 0** |
| `ruff check` / `ruff format --check` | clean on the write set |
| `mypy` (`--strict`, `files = server/app`) | `Success: no issues found in 49 source files` |
| `alembic get_heads()` | `['0009_tc_telegram_unknown_delivery']` — one head |

The two `xfail`s are `strict=True`, so either turning green fails the suite and forces this
record to be revisited:

1. `test_reconciliation_reports_which_clauses_are_unmet` — pending `TC-backup-restore-drill`.
2. `test_the_adapters_sender_can_report_a_provider_message_id` — pending the response half of
   `telegram.send_payload` (`CR-TC-DELIVERY-09`).

**E3 is `NOT_RUN`.** No Telegram Bot API call was made by anything in this packet.

---

## 5. Evidence record

`evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json`, id
`EV-E1-01-tc-telegram-unknown-delivery`, `review_type: SELF_VALIDATION`,
`evidence_level: E2`, `result: PASS`. It validates against `evidence/manifest.schema.json`
with `jsonschema.Draft202012Validator` and a format checker: **0 errors**. It carries the
pinned `spec_sha256`, the §0 contract hashes copied verbatim, every fixture with its hash and
byte count, the exact command, exit code 0, the eight oracles, and nine `not_checked_vi`
entries. It is **not** registered in `evidence/index.json`: that file is PC09's and outside
this card's write set.

---

## 6. Claim

**Claim.** `MOD-delivery-service` implements the six `delivery.*` operations of
`contracts/ports.yaml` against `contracts/state/delivery.yaml` `T-DL-00`..`T-DL-09` and
`DP-01`..`DP-05`, in the plain-text-only scope of `OD-20260908-09`.

**Baseline.** spec `d35e1f2d…`, plan `f65bb046…`, pin epoch `PC10-PIN-P3-20260908` (30/30
files verified, 0 drift); `CT-state-delivery` 0.2.0, `CT-telegram-delivery` 0.2.1,
`CT-arch-ports` 0.1.0; implementation revision = the nine files hashed in §1, alembic head
`0009_tc_telegram_unknown_delivery`.

**Requirements covered.** `REQ-AC14`, `REQ-AC15`, `REQ-AC04`, `REQ-D37`, `REQ-D57` (empty
period creates no digest intent — enforced by the caller passing no intent), `REQ-S9.3-06`;
invariants `I05`, `I09`, `I13`, `I15`; scenarios `SC14`, `SC15`, `SC19`, `SC25`, `SC27`,
`SC49`, `SC50` at the level the fixtures state them.

**Evidence manifest IDs.** `EV-E1-01-tc-telegram-unknown-delivery`.

**Observed result.** 27 pass / 2 xfail / 0 fail on the card's three test files; 828 / 0 fail
across the repository; lint and type gates clean; one migration head.

**Not established.**

- Sending to Telegram works. No Bot API call was made; `AC-14` at level E3 stays `NOT_RUN`.
- The recipient never sees a duplicate. AMD-B03 §5.1 says this is **not** guaranteed, and no
  test here claims it. What is proved is that the *system* never sends a second time on its own.
- The digest's Save button, formatting, and keyboard layout. Three facts remain `KC`
  (`CR-PC07-04`); §3.1 item 3 and §8 of the Telegram contract are unimplemented by design.
- Two-process exclusivity through a durable lease record — no entity exists for one.
- Durable evidence that the operator accepted the duplicate risk — no entity exists for one.
- Anything at `IMPLEMENTATION_VERIFIED`. This is `SELF_VALIDATION`; the schema caps it at
  `CONTRACT_READY`, and reaching the card's ceiling needs an independent audit on a frozen
  candidate. **No independent audit was run on this package.**

---

## 7. Change requests

| ID | Where | What | Why it matters |
| --- | --- | --- | --- |
| `CR-TC-DELIVERY-01` | `contracts/data/entities.yaml` `ENT-delivery-attempt.outcome` vs `T-DL-01` | the column is NOT NULL over `sent \| retryable_error \| permanent_error \| unknown`, but the row must be committed **before** the send, when the outcome is unknown. Fixture `telegram/b`'s `given` row shows `outcome: null`, which the column forbids | resolved in the safe direction: the row is INSERTed with `outcome = 'unknown'`, so a crash leaves the true value already stored. The fixture's **oracle** is unaffected; only an illustrative `given` value disagrees. Asking for either the fixture note or a nullable-until-resolved column |
| `CR-TC-DELIVERY-02` | `contracts/state/delivery.yaml` §enums vs `T-DL-06` / `telegram/delivery.md` §5.2 | `abandon` is specified to put the **part** in `cancelled`, but `delivery_part_state` has no `cancelled` member | implemented as part → `failed` with the *delivery* → `cancelled` when no part was sent. Consequence, asserted in the test: once applied, `abandon` and `mark_not_delivered` are indistinguishable at part level, so a replayed `abandon` cannot raise `IDEMPOTENCY_CONFLICT`. Needs either a fifth part state or a decision column |
| `CR-TC-DELIVERY-03` | `contracts/data/entities.yaml` vs `contracts/ports.yaml` `delivery.decide_unknown` | idempotency is keyed on `delivery_part_id + decision_request_id`, and **no entity stores a decision** | idempotency is derived from the state machine instead. What is lost is the durable evidence `T-DL-06` calls for ("bản ghi quyết định là bằng chứng rằng người đã chấp nhận nguy cơ"). A `delivery_decision` entity is needed |
| `CR-TC-DELIVERY-04` | `contracts/data/entities.yaml` `ENT-delivery` vs `T-DL-03` | the transition writes `next_attempt_at`; the entity has no such column | derived from `updated_at + backoff(attempt_count)` with jitter made deterministic from the delivery id, so the due time survives a restart. A real column would be simpler and auditable |
| `CR-TC-DELIVERY-05` | `ENT-outbox-intent.intent_type` vs `contracts/state/delivery.yaml` `intent_kind` | two spellings of the same two values (`telegram_digest \| telegram_alert` vs `report_digest \| run_alert`); `acceptance/fixtures/recovery/a` uses `report_digest` in an `outbox_intent` row, i.e. the *other* file's vocabulary | mapped at the edge, entity vocabulary stored. Low severity, but a reader cannot tell which is authoritative |
| `CR-TC-DELIVERY-06` | `ENT-delivery.report_id` NOT NULL vs `T-DL-00` `run_alert` | an alert intent has a run and no report, so it cannot have a `delivery` row | `run_alert` creates the `outbox_intent` only; `REQ-AC04` still holds through `ux_outbox_alert_per_run`. Alert **delivery** therefore has no state machine row |
| `CR-TC-DELIVERY-07` | `contracts/ports.yaml` `storage.get_health.caller_modules` vs `contracts/state/delivery.yaml` §sender_lease, and card §4 | the state contract tells the dispatcher to read `storage.get_health` before every dispatch, but `MOD-delivery-service` is not among that operation's callers; card §4 lists it as consumed | the guard is consulted through `StorageGuard.assert_writable(DELIVERY_DISPATCH_NEXT)`, which gives the identical answer without crossing an ungranted edge. Related: `server/app/storage/guard.py::MODULE_RUNTIME` has no `MOD-delivery-service` row, so that module would be refused `CAPABILITY_DENIED` where R5-01 implies `FORBIDDEN_EDGE` — another card's file, not touched, not asserted |
| `CR-TC-DELIVERY-08` | `server/migrations/versions/0009_…` | `delivery.report_id` carries no `REFERENCES report(id)` because `report` does not exist yet | the column keeps name, type and NOT NULL; `TC-report-coverage-publish-cas` must add the constraint in the revision that owns `report` (precedent: `0002b`) |
| `CR-TC-DELIVERY-09` | `server/app/telegram/ingress.py::TelegramSender` | `send_message` returned `None`, carrying neither `provider_message_id` nor an error classification | **RESOLVED by `PKT-TC-TGAUTH-FIX1`** (W5A): the signature now returns `str`. See the addendum — the xfail is gone and replaced by a real per-part assertion. The error-classification half is carried forward as `CR-TC-DELIVERY-10` |

Open items **not** raised by this packet and unchanged by it: `CR-PC07-04` (three Telegram
format facts still `KC`), `REQ-A6` for Telegram (partially resolved: two of five facts).

---

## 8. Stop conditions — how each was met

| ID | Outcome |
| --- | --- |
| `SG-01` | honoured. No multipart branch depends on an unresolved fact; splitting uses only the `DOCS_derived` 4096 length, counted pessimistically (§2.1). Everything that needs `callback_data`, a parse mode or a keyboard is `NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)` |
| `SG-02` | honoured. All six delivery budgets are transcribed from `contracts/retry-policy.yaml` and none was raised; the budget test reads the module constant rather than a second copy of the number |
| `SG-03` | honoured, twice over: `unknown → pending` exists only inside `decide_unknown`, and the intent is parked in a `dispatch_state` the claim query never selects |
| `SG-STACK` | no new framework chosen. FastAPI + SQLAlchemy Core + Alembic + pytest, all already in the tree per ADR-0011 |
| `SG-G5` | the wait gate was observed: no write happened before `agent-tasks/README.md` declared `PC10-PIN-P3-20260908` **and** `evidence/handoffs/PC10-handoff.md` carried the `PKT-PC10-FIX24` addendum with `lease_released_at` |
| `SG-PC09` | `acceptance/scenarios.yaml` was read at its current bytes; no oracle in it contradicts card §8 |
| `SG-DENY` | `FE-24` and `FE-34` are refused `FORBIDDEN_EDGE`; a caller off the server runtime gets `CAPABILITY_DENIED`. Both asserted |
| `SG-HASH` | run twice, 30/30 clean, 0 drift |
| `SG-CONTRACT` | four contract conflicts found (`CR-TC-DELIVERY-01/02/03/04`). None was resolved by editing a contract, a fixture or an expectation; each is reported above with the direction taken and why it is the safe one. None of them contradicts a fixture **oracle**, which is why the packet continued rather than stopping |
| `SG-EDGE` | no new table, edge, secret or capability was taken. The sender lease uses the existing `outbox_intent.dispatch_state`; the decision record was **not** invented, it was raised as `CR-TC-DELIVERY-03` |

---

*`PKT-TC-DELIVERY` · `worker-W5C` · `lease_released_at` 2026-09-07T19:45Z · every result above
is `SELF_VALIDATION`. No item in this handoff is an independent audit.*


---

# ADDENDUM — `PKT-TC-DELIVERY-FIX1`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-DELIVERY-FIX1` · lease `LEASE-TC-DELIVERY-e2` (fencing 2) · worker `worker-W5C` |
| scope | card §3 test files + this handoff + a re-issued evidence manifest. **No source file, no migration, no contract touched.** |
| status | **`DONE`** · ceiling unchanged (see §6) · `lease_released_at` 2026-09-07T20:35Z · next actor `Coordinator` |
| trigger | `PKT-TC-TGAUTH-FIX1` changed `TelegramSender.send_message` to return `str`, which made this card's `strict` xfail XPASS — one red test in the suite |

## A.1 What changed, and why it is a real assertion now

`test_the_adapters_sender_can_report_a_provider_message_id` was an `xfail(strict=True)`
standing in for a signature that did not exist. It is replaced by
**`test_each_part_receipt_records_the_id_the_adapters_sender_returned`**, which drives the
whole path: `MOD-telegram-adapter`'s own `RecordingSender` mints `rec-1`, `rec-2`; a test-side
adapter turns each into `Sent`; `delivery.record_receipt` files it; and the assertion pairs
**part id → message id** twice over — once from `delivery.get_status`, once from a join across
`delivery_receipt`/`delivery_attempt`.

The pairing is by identity, not by count, on purpose. With two parts, a receipt can be right
in number and still be filed against the wrong part, and `DP-01` ("mỗi part có receipt RIÊNG")
is precisely the claim a count would let slip through. The adapter stays in the test: the
delivery package still imports nothing from `server.app.telegram`.

`rec-N` is visibly not a Telegram id, so nothing here can pass by mistaking a recorded id for
a real receipt. **E3 remains `NOT_RUN`** — no Bot API call was made.

## A.2 The other xfail: premise re-checked, still true

`test_reconciliation_reports_which_clauses_are_unmet` stays `xfail`, now written
`strict=True, run=True` so it executes every run and fails loudly the moment it starts
passing. The premise was re-checked against the tree rather than assumed:
`StorageGuard.__init__` still takes only a boolean `reconciliation_check`, there is no
clause-list accessor anywhere under `server/app/`, and no `backup.reconcile_after_restore`
exists. `TC-backup-restore-drill` has not landed.

## A.3 CR movement

| ID | Movement |
| --- | --- |
| `CR-TC-DELIVERY-09` | **RESOLVED by W5A** (`PKT-TC-TGAUTH-FIX1`) for the success branch: the provider message id now travels from the adapter's seam into a per-part receipt, proved by the test above. |
| `CR-TC-DELIVERY-10` | **NEW** — `server/app/telegram/ingress.py::TelegramSender` still has no way to *classify* a failure. It raises rather than returning one of retryable / permanent / uncertain, so the `T-DL-03` vs `T-DL-04` boundary — the most important one in AMD-B03 — is still exercised only through this card's own fake transport. Until the seam can express "not received" apart from "do not know", an adapter-level integration cannot prove that boundary. |

The eight other `CR-TC-DELIVERY-nn` items are unchanged and still open.

## A.4 Files

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `tests/integration/test_multipart_partial_receipt.py` | MODIFY | `c5c59e68c3579fa83af053572abe90962800de822a85cf59fa2de257507014e3` | `fd2364b95e1974c6af5757dd616dc0f5fec102d3be1bc1911dfcab074c1daad6` | 19611 |
| `tests/integration/test_delivery_unknown_no_retry.py` | MODIFY | `21eec633371b3bce9dd9936b092a12b8b002aa7dcf7e7dbee32e9698192cebd3` | `9b8d3fe71da2cb934137bf19db1c5f54b56f1ad69e4e5019d7ab001cc6dc077a` | 24291 |
| `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` | MODIFY (`result` → `STALE` + `stale_reason`) | `a79b766b1cf281ecf917545ef7cbb7746907d103823782d133dffb259a204eb0` | `f0c8bc4828ec590d08c686ec22928e7d29aa9cb4ca65c7b41d190d2bddf2d499` | 17941 |
| `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T202901Z.json` | CREATE | ABSENT | `92356541740be81a69da5218f8a612d11197c6527319013f678436d36791391b` | 18556 |
| `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md` | MODIFY | (§1 row + this addendum) | (this file) | — |

The superseded record is marked `STALE` rather than deleted or edited into agreement: it was
true of the bytes it ran on, and two of its inputs changed byte afterwards. Both records
validate against `evidence/manifest.schema.json` with a format checker, **0 errors** each.

## A.5 Re-verification

```
PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider \
  tests/integration/test_delivery_unknown_no_retry.py \
  tests/integration/test_multipart_partial_receipt.py \
  tests/integration/test_permanent_failure_report_intact.py
PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider          # whole repo
PYTHONDONTWRITEBYTECODE=1 uv run ruff check . ; uv run ruff format ... ; uv run mypy
```

| Run | Result |
| --- | --- |
| the three card tests | **29 tests: 28 passed, 1 xfailed (strict, run), 0 failed, 0 error, exit 0** (was 27 / 2) |
| whole repository suite | **836 tests, 0 failed, 0 error, 9 skipped/xfailed, exit 0** |
| `ruff check` + `ruff format` | clean on the write set |
| `mypy` (`--strict`, `server/app`) | `Success: no issues found in 49 source files` |
| `alembic get_heads()` | `['0009_tc_telegram_unknown_delivery']` — one head |
| `SG-HASH` | 30/30 pinned files match, **0 drift** |

*`PKT-TC-DELIVERY-FIX1` · `worker-W5C` · `lease_released_at` 2026-09-07T20:35Z · every result
here is `SELF_VALIDATION`; no item is an independent audit.*
