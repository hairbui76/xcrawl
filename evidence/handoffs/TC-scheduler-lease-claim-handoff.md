# HANDOFF — `TC-scheduler-lease-claim`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-SCHED` — card `agent-tasks/TC-scheduler-lease-claim.md` (Phase 6, M7, gate G5) |
| worker principal | `worker-W6A` (same agent as `worker-W3C`; reused per the Phase 4/6 dispatch) |
| authority_id | `AUTH-COORD-TC-SCHED` (parent `AUTH-OWNER-20260908-10`) |
| lease_id | `LEASE-TC-SCHED-e1` (card §3 write set + two Alembic revisions + one `main.py` block + handoff + manifest) |
| baseline | commit `fb3944a` on `main`; pin epoch `PC10-PIN-P3b-20260908`; **29/29 §0 pins match on hash and byte count** |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `CONTRACT_READY` for what this record supports; the card's ceiling is `IMPLEMENTATION_VERIFIED` and reaching it needs the independent review of card §12. |
| review_type | `SELF_VALIDATION`. No item here is an independent audit. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T21:40Z |

`DONE_WITH_CONCERNS` for two reasons, neither self-resolvable: five contract-level defects
were found and **not** fixed (§4), and two sibling-card collisions are visible in the full
suite that this card neither caused nor may repair (§3.3).

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/scheduler/evaluator.py` | CREATE | ABSENT | `656a0356a64a5753ab5f131f4d4b1b4135ac9716895fd7c353a94ab1ca06085c` | 17609 |
| `server/app/jobs/lease.py` | CREATE | ABSENT | `00eb8421360e83750f3b3e05edf1a904498b555e6435b68e0c08d17e2c523e8b` | 20531 |
| `server/app/jobs/service.py` | CREATE | ABSENT | `8003525fe25550e64d77b73d4d1ef43062c2b55be3f44815c29c8361f9dd7999` | 69868 |
| `server/app/jobs/router.py` | CREATE | ABSENT | `285da7b65243e730583aadff43fc7557a1d73c7ac7a49127503f6d908aa9385f` | 18522 |
| `server/migrations/versions/0010_tc_scheduler_lease_claim.py` | CREATE | ABSENT | `55de48ef3d6454871d658c2e5b857e02714c6c3b443f8b2ca2a104eafab8e79d` | 16518 |
| `server/migrations/versions/0011_merge_phase4_6_heads.py` | CREATE | ABSENT | `f1ea8f31599469797ae68efbc763fefadf95293932c49109de998dd35d0ca9d4` | 2554 |
| `tests/contract/test_worker_assignment_schema.py` | CREATE | ABSENT | `9fa7c4c5475054d18b5293d68b8b3779fe34b55695efe5bbfe3e4a701f808415` | 15140 |
| `tests/integration/test_scheduler_catchup.py` | CREATE | ABSENT | `162401f492a1581f5354866e09be7f2fb781210316ec3e10b6a17ae33a37568d` | 24587 |
| `tests/integration/test_lease_two_claimants.py` | CREATE | ABSENT | `513c9bd522c57a4f560b0c9dc5317f4b650c460f541005dbad6be2cdc77c22f5` | 36136 |
| `server/app/main.py` | MODIFY | (one delimited block appended) | `73392a3c3dadd1b07a3f58383d014c1dbfdb1c4d4e0fe3727679980ca0ff8d97` | 13222 |
| `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` | CREATE | ABSENT | `c22de26ec5dfa04d50fa2abc8cad1ccf9197b3ab655e77ca4769997a66ad8208` | 20669 |
| `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/`; **no collector file** (the dispatch forbids it — see §2.5); no git operation;
`PYTHONDONTWRITEBYTECODE=1` throughout, so no `__pycache__`.

`server/app/main.py` carries exactly one block, `# >>> TC-scheduler-lease-claim` …
`# <<< TC-scheduler-lease-claim`, with its imports inside the delimiters (`F-A3R1-13`).

### 1.1 Write-set notes

1. **No `__init__.py`** under `server/app/jobs/` or `server/app/scheduler/`. Card §3 lists four
   modules and no package marker; `server/app/` is a regular package, so both load as implicit
   namespace portions, exactly as `server/app/research/` already does. `mypy --strict` is clean
   over both.
2. **Two Alembic revisions, one head.** `0010_tc_scheduler_lease_claim` is this card's; the
   sibling `TC-report-coverage-publish-cas` landed `0010_tc_report_coverage_publish_cas` on the
   same parent while this card was being written, so `0011_merge_phase4_6_heads` joins them.
   It issues **no DDL** — the two branches create disjoint tables. `alembic heads` reports one
   head, and both this card's test and the schema gate assert `len(heads) == 1` **structurally**,
   never against a literal id.

---

## 2. What was built

### 2.1 The fourteen operations

`scheduler.evaluate_due` is pure and lives in `server/app/scheduler/evaluator.py` — no database
handle, no clock, `now` is an argument. The other thirteen are in `server/app/jobs/service.py`;
`server/app/jobs/router.py` exposes the eleven that `contracts/http/openapi.yaml` gives an HTTP
path. The three `internal` ones (`scheduler.evaluate_due`, `job.enqueue_scheduled_run`,
`job.coalesce_overdue`) are **not** routed: publishing them would let something outside the
server start a run.

### 2.2 `assignment_lease` was EXTENDED, not recreated

`CR-TC-ANALYSIS-01` told this card to take over the custodian table without a second
`CREATE TABLE`. There is none — asserted, not asserted-in-prose:
`test_the_custodian_lease_table_was_extended_not_recreated` parses every migration, strips the
module docstring, and checks that `CREATE TABLE assignment_lease` appears in the **code** of
exactly one file (`0006_tc_analysis_once_per_generation.py`). The docstring test matters: this
card's own migration *quotes* that statement while explaining the rule it follows, and a raw
byte search would have called that a violation.

What was added is one index:

```
ux_assignment_lease_one_held  UNIQUE (owner_id, job_id) WHERE state = 'held'
```

`lease_model` LM-02 says "Một job có tối đa một lease `held`", and the existing
`ux_lease_job_epoch` does **not** say that — it forbids reissuing the *same* epoch, a different
claim. Without this index two racing claimants could each insert a `held` row at epochs 2 and 3
and both believe they hold the job, which fixture `collection/f` lists as a forbidden effect.
Plus `ix_assignment_lease_expiry` for the 15 s sweep, which would otherwise scan the table on
the hot path of every claim.

### 2.3 The single place an epoch is checked

Card §12 gives the reviewer one question: *is there any path by which a worker holding an old
epoch can write?* The answer is `lease.assert_current_lease`, and it is the only place. It
raises rather than returning a flag, because a boolean a caller forgets to check is exactly the
I10 counterexample `contracts/state/run.yaml` writes out. Its four refusals are ordered, and the
order is load-bearing: no lease → `NOT_FOUND`; **restore pending → `STALE_LEASE` before the
epoch is even compared** (LM-08 — after a restore the clock jumped and a matching epoch proves
nothing); epoch behind or lease not `held` → `STALE_LEASE`; epoch matches but the clock passed
→ `WORKER_LEASE_EXPIRED`.

`tests/integration/test_lease_two_claimants.py` attacks that question from four directions:
through the service, through HTTP, around the service with raw SQL (where the index refuses),
and after the fact by comparing every column of every lease row before and after a refused call.

### 2.4 DST as two formulas, not two special cases

`resolve_local_to_utc` implements the contract's own formulas. The repeated hour takes
`min{ t : local(t) == nominal }` — comparing the two `fold` conversions. The missing hour takes
`min{ t : local(t) >= nominal }` by **bisection** on the instant axis, because a closed form
would have to know where the transition is and by how much the offset moved, which is knowledge
the tz database holds and this module should not duplicate.

`occurrence_id` is derived from the **nominal local time**, never the resolved instant — the one
sentence in `occurrence_identity.rule_vi` that makes a repeated hour produce one occurrence
instead of two, and which fixture `collection/j` names as a forbidden effect if got wrong.

`Asia/Ho_Chi_Minh` has no DST, so the fixture deliberately leaves the zone abstract ("some IANA
timezone WITH DST"). The tests use `America/New_York` for those two rules and the configured
zone everywhere else; both are passed as configuration, and `ScheduleSettings` has **no default
for the slots or the timezone** (card §10 `SG-02`, `REQ-OQ05`).

### 2.5 Consumers

* **Collector.** `collector/app/client.py` already posts to `/v1/workers/registrations`,
  `/v1/workers/assignments/claim`, `.../heartbeat`, `.../stop`, `.../release`. This router
  serves those exact paths, so its `worker.*` stub becomes a real round trip. **No collector
  file was edited**; the integration is that the two halves already agree, and
  `test_a_stale_heartbeat_over_http_is_refused_with_the_registered_envelope` exercises the
  server half through the same path with the same headers.
* **W4C (UI runs).** `run.list`/`run.get` return the triple `(status, outcome, stop_reason)`
  **unflattened**. Deciding which of the three I13 states to display is the UI card's job;
  flattening in the read model would make that decision in the wrong place.
* **W5A (`/run-now` from Telegram).** `POST /v1/runs/run-now` accepts the owner session (with
  CSRF) **or** the Telegram ingress secret, which is the contract's two-alternative `security`
  block. Their xfail is theirs to turn green.

---

## 3. Verification

### 3.1 Commands and results

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_worker_assignment_schema.py \
  tests/integration/test_scheduler_catchup.py \
  tests/integration/test_lease_two_claimants.py -p no:warnings
```

**60 passed, 0 failed** · exit code **0** · 2026-09-07T21:23:30Z → 21:23:44Z
(19 contract + 16 catch-up + 25 lease). The three commands card §8 names are these three files.

| Gate | Result |
| --- | --- |
| `ruff check` + `ruff format --check` on the write set | clean |
| `mypy --strict` | clean for `server/app/jobs`, `server/app/scheduler`, `server/app/main` |
| `alembic heads` | one head |
| manifest vs `evidence/manifest.schema.json` (Draft 2020-12, format checker on) | 0 errors |
| `tests/contract/test_schema_matches_entities.py` | 9 passed, 1 failed — **not this card's**, see §3.3 |

### 3.2 Oracles, measured

| Oracle (source) | Expected | Observed |
| --- | --- | --- |
| runs from three overdue slots (`reporting/f`, REQ-D15) | 1 | 1 |
| runs from six overdue slots (`catch_up.oracle_vi`) | 1 | 1 |
| `len(run.schedule_occurrence_ids)` for that run | 6 | 6 |
| `COUNT(assignment_lease WHERE state='held')` with two claimants (`collection/f`) | 1 | 1 |
| lease rows changed by a stale heartbeat | 0 | 0 |
| runs created by five `run_now` presses (`collection/i`) | 0 | 0 |
| occurrences per DST boundary slot (`collection/j`) | 1 | 1 |
| runs cancelled from the five non-terminal states (`collection/k`) | 5 | 5 |
| rows deleted by cancel | 0 | 0 |
| `CREATE TABLE assignment_lease` statements in the tree | 1 | 1 |
| network calls | 0 | 0 |

`SG-DENY`: this card's boundary is enforced by the contract's own auth matrix — a collector
token on `run.*` and an analysis-worker token on `worker.claim_assignment` are both
`UNAUTHORIZED` (R5-01 row 1), because all of these are HTTP operations with a declared
principal class. The 36-edge sweep itself is `tests/integration/test_denied_edges.py` and is
unchanged.

### 3.3 Full suite, and two sibling collisions this card must not repair

`907 passed, 9 xfailed, 18 errors, 0 failed` in 122 s.

**All 18 errors are one collision, and no file of this card's write set is involved.**
`tests/integration/test_delivery_unknown_no_retry.py` and
`tests/integration/test_permanent_failure_report_intact.py` (card `TC-telegram-unknown-delivery`)
insert a three-column `report` row; the sibling card `TC-report-coverage-publish-cas` has since
created the real `report` table with `owner_id NOT NULL`. The failing statement is
`INSERT INTO report (id, status, content_hash)`. This card neither creates nor writes `report`.

The one schema-gate failure is the same shape: `report_item.target_key` is a generated column
added by that sibling, and `test_schema_matches_entities.py` pins the generated set to three
tables by literal. None of this card's four tables has a generated column, and every other
assertion in that file passes for them. Both belong to `TC-report-coverage-publish-cas` and
`TC-telegram-unknown-delivery` to settle; changing either test file would be writing outside
this card's write set.

`mypy --strict` also reports 17 pre-existing errors in `server/app/report/` — same sibling,
same reason, untouched.

---

## 4. Change requests — contract defects found, **not** fixed

### `CR-TC-SCHED-01` — `assignment_lease.run_id` stays `NOT NULL` (refusal, as instructed)

Inherited `CR-TC-ANALYSIS-02`: a `NOT NULL run_id` is meaningless for an *analysis* claim, which
is not scoped to a collector run. The dispatch allowed relaxing it "only if `entities.yaml`
permits". It does not — `ENT-assignment-lease` declares `run_id` `nullable: false` — so the
column is unchanged and this is re-filed rather than resolved by a migration that would put the
schema and the contract in disagreement. `test_the_lease_run_id_is_still_not_null_as_the_contract_declares`
asserts both halves, so a later "helpful" migration cannot quietly relax it.
**Coordinator ruling received: refuse-nullable is correct.**

### `CR-TC-SCHED-02` — card §10 `SG-01` is stale against the pinned `run.yaml`

`SG-01` says `CR-PC03-02` is open and no operation may take a run out of `blocked` except
`run.cancel`. The pinned `contracts/state/run.yaml` has **T-RUN-23** (`blocked → queued`,
`owner_declares_unblocked`) and `contracts/ports.yaml` `run.resume` documents the mandatory
`unblock_reason` for that path. No operation was invented; the one implemented is in both
contract files. **Coordinator ruling received: the pinned contract wins.** The card's prose
needs updating in the contract round.

### `CR-TC-SCHED-03` — `skipped_stale` vs the closed enum

`run.yaml` CU-04 marks an over-aged occurrence `skipped_stale`; `entities.yaml`
`schedule_occurrence.state` closes the enum at `due | coalesced | dispatched | skipped`.
**Coordinator ruling received: `entities.yaml` wins.** The code writes `skipped`.

### `CR-TC-SCHED-04` — `assignment_lease.run_id` has no `REFERENCES run (id)`

It could now that `run` exists, but adding a foreign key to an existing SQLite table needs the
12-step rebuild, and `analysis_attempt` already points *into* `assignment_lease`. Rebuilding a
parent table under a live child reference, to add a constraint no oracle in this card needs, is
the larger risk. **Severity: medium** — a lease can name a run that does not exist.

### `CR-TC-SCHED-05` — claim idempotency is satisfied in effect, not in form

`ports.yaml` promises "Cùng `claim_request_id` trả cùng assignment; không cấp hai lease". The
second half holds structurally (`ux_assignment_lease_one_held` refuses a second holder, and the
caller gets `no_work`/`assignment_already_held`). The first half does not: `ENT-assignment-lease`
has **no column** for `claim_request_id`, so a replayed claim cannot be recognised and handed
back the same assignment object. The seam is `service._lease_held_by` (documented, returns
`None`). Resolving it needs a column `entities.yaml` does not declare. **Severity: medium** —
a worker retrying after a `claim_request_timeout` gets a correct but different answer.

### Observation, not a defect

`entities.yaml` stores `worker_kind` as `x_collector | analysis_worker`; `ports.yaml` and
`worker-assignment.schema.json` put `collector | analysis` on the wire. Two vocabularies, each
authoritative for its own layer, mapped explicitly in `WIRE_TO_STORED_WORKER_KIND` and asserted
against both sides in the contract test.

---

## 5. Completion claim

**Claim:** `CONTRACT_READY` supported by this record.
**Baseline:** spec `d35e1f2d…e0e26`; pin epoch `PC10-PIN-P3b-20260908`, 29/29 §0 sources rehashed
and matching; commit `fb3944a`; implementation revision = the hashes in §1.
**Requirements covered:** `REQ-D11`, `REQ-D13`, `REQ-D14`, `REQ-D15`, `REQ-D16`, `REQ-AC02`,
`REQ-AC04` (pointer only), `REQ-S8.2-08`; invariants `I01`, `I10`, `I13`.
**Evidence manifest:** `EVM-TC-scheduler-lease-claim` →
`evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (`EV-E1-14-…`).
**Observed result:** PASS — 60 passed, exit 0.

**Not established.**

1. **`IMPLEMENTATION_VERIFIED`** — the card's ceiling, not a self-check's.
   `evidence/manifest.schema.json` caps a `SELF_VALIDATION` record at `CONTRACT_READY`
   (`allOf` clause 6, protocol §9). Card §12's independent review is what would raise it.
2. **Real concurrency.** "One winner" is proven sequentially and at the constraint, not with two
   processes racing under load.
3. **Real storage failure.** E2 (`server/app/db/faults.py`) has not been run against claim,
   heartbeat or cancel; `StorageGuardPort` is wired but defaults to `None` in tests.
4. **A live collector run** (E3, AC-01) — SP1/M0, out of scope.
5. **That 08:00/20:00, 200 posts and 30 minutes are right** — `REQ-OQ05` re-measures after M0.
6. **Claim idempotency in the contract's own form** — `CR-TC-SCHED-05`.
7. Card §9's note stands, verified by `grep`: `contracts/http/openapi.yaml` **and**
   `contracts/schemas/worker-assignment.schema.json` both still declare
   `claim_ceiling: DRAFT_FOR_REVIEW` in their own headers.

**Review type: `SELF_VALIDATION`.** No independent audit was run, and no line of this handoff
should be read as one.

---

## 6. Stop gates, checked

| ID | Outcome |
| --- | --- |
| `SG-HASH` | **PASS.** 29/29 §0 sources rehashed before the first write; hash and byte count both match. Re-run after the gate opened. |
| `SG-G5` | Wait gate honoured: no write until `git log -1` showed `feat: Phase 3 …` (`fb3944a`), the epoch `PC10-PIN-P3b-20260908` was declared, and SG-HASH passed. Polled at 60 s intervals meanwhile. |
| `SG-01` | **Raised, not improvised.** The stale premise is `CR-TC-SCHED-02`; the Coordinator ruled and the pinned contract was implemented. No operation was invented. |
| `SG-02` | 08:00/20:00 and `Asia/Ho_Chi_Minh` are read from `ScheduleSettings`, which has **no defaults**; a test asserts the constructor refuses without them. |
| `SG-STACK` | No framework chosen — FastAPI, SQLAlchemy 2 Core, Alembic and pytest were all fixed by ADR-0011 and the Phase 0 skeleton. |
| `SG-PC09` | `acceptance/scenarios.yaml` read fresh (unpinned); SC01/02/20/33/34/35 do not contradict card §8. |
| `SG-DENY` | Auth matrix taken from the contract's `security` blocks; R5-01 codes used. The 36-edge sweep is unchanged. |
| `SG-CONTRACT` | Five discrepancies found; **none** fixed. Raised as `CR-TC-SCHED-01…05`. |
| `SG-EDGE` | No new edge taken. Only `ingest.get_checkpoint` (read) and `delivery.create_intent` (alert), both through injected ports that default to `None`. |

### 6.1 Housekeeping

**`evidence/index.json` was not updated.** Card §13 asks for it, but that file is PC09-owned and
outside this packet's write set. `EV-E1-14-tc-scheduler-lease-claim` still needs registering.

**Clock.** The execution host's UTC clock reads `2026-09-07` while the dispatch epoch is named
`PC10-PIN-P3b-20260908`. Every timestamp here and in the manifest is the **measured** clock;
`inputs.clock` says so.

---

*`PKT-TC-SCHED` · `worker-W6A` · `lease_released_at` 2026-09-07T21:40Z · claim `CONTRACT_READY`
· `SELF_VALIDATION` — no item here is an independent audit.*

---

# ADDENDUM — `PKT-TC-SCHED-FIX1` (WC's real collector wiring: `CR-TC-COLLECTOR-11`, `-12`)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-SCHED-FIX1` · lease `LEASE-TC-SCHED-e2` (fencing 2) · worker `worker-W6A` |
| findings | `CR-TC-COLLECTOR-11` (blocking) and `CR-TC-COLLECTOR-12`, both raised by WC wiring the real collector loop against this router |
| status | `DONE` · claim unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) · next actor `Coordinator` |
| lease_released_at | 2026-09-08T06:55Z |

Both findings were correct, and both were defects a test that builds its own objects cannot
find. That is the lesson worth recording: this card's contract test validated payloads *it*
constructed, so it was green while the payload the **service** built failed the same schema in
seven places. WC's loop found it in one run against the real router.

## C.1 `CR-TC-COLLECTOR-11` — the alert port opened a second SQLite writer

`report_stop` called `alert_port.create_alert_intent` from inside its own open
`session_scope`, and the adapter the composition root installs opened its own connection.
SQLite has one writer: `database is locked`. On a real deployment the **first challenge of the
first run** would have raised inside `report_stop`, and the Owner would never have been told
the run was waiting for them.

`AlertIntentPort.create_alert_intent` now takes `connection`, and `report_stop` passes the one
it is holding. `delivery.create_intent` already accepted `connection=` for exactly this — its
docstring calls it the outbox pattern — so the fix costs nothing and makes the requirement
structural rather than a rule each adapter has to remember.

There were **two** reasons, and only one of them is about locking. `run.alert_intent_id` is
`REFERENCES outbox_intent (id)`, so the intent row and the pointer to it have to land in one
commit; an adapter that committed separately would leave a window in which the pointer names a
row that does not exist yet, and a crash inside that window leaves it naming one that never
will. A port that merely avoided the deadlock — by not writing at all — would have failed the
foreign key instead.

`test_the_alert_intent_is_written_in_the_callers_transaction` uses a port that **writes a real
`outbox_intent` row through the connection it is handed**, not a mock that records the call: a
port that never writes could not have reproduced either failure. It asserts the port received a
connection, that exactly one `telegram_alert` intent exists, and that `run.alert_intent_id`
points at it — and since `foreign_keys=ON` on every connection this engine hands out, that last
UPDATE would fail outright were the intent not already in the same transaction. So "one commit"
is measured, not inferred. A companion test pins `REQ-AC04`: a second `report_stop` does not
call the port at all.

## C.2 `CR-TC-COLLECTOR-12` — the claim response did not satisfy its own schema

`contracts/ports.yaml` names `worker-assignment.schema.json` as the response schema of
`worker.claim_assignment`, and the document is `additionalProperties: false` with an explicit
`required` list. The live response failed it in seven places:

| what was wrong | now | why the contract asks for it |
| --- | --- | --- |
| `x_coverage_note_vi` absent | built from the run's own limits | AMD-B05: `completed` must never be read as "all of X was swept". The collector copies it verbatim into the run metadata. |
| `source_limits: {}` | the five `const` values | `contracts/ops/collector-probe.md` §8: sent *"để collector không phải suy diễn"*. An empty object told the collector none of it. |
| `tag_config_version_id: null` | a ULID-shaped value | `search_config` is the immutable search snapshot (REQ-D24). |
| `catch_up_window` missing `occurrence_count` | included | REQ-D15: "three periods, from X to Y" is the sentence Telegram quotes. |

**The `tag_config_version_id` default is a visible placeholder, not a fabricated id.**
`contracts/modules.yaml` gives `MOD-job-service` four outbound edges and `MOD-tag-service` is
not among them, so this module may not ask the tag service what the tags are — it receives
them as configuration on `JobContext.search_config`. No card creates `tag_config_version`
either (the same gap `CR-TC-REPORT-01` records on the report side). So the default reads as
`PENDNGTAGSERVCE00000000000` — spelled without `I`/`L`/`O`/`U` because Crockford base32
excludes them — which is obvious in a stored payload rather than plausible. `tags` defaults to
**empty**: this module has no way to know them and will not invent a search term.
**`CR-TC-SCHED-06`.**

`is_resume` was wrong too and is fixed in passing: it read `bool(occurrence_ids) and
attempt_count > 0`, which made every scheduled run's first claim a "resume". It is now
`attempt_count > 1` — the claim increments the counter, so a first claim reads 1.

### The test fix the ruling asked for

The contract test now validates **the payload the service builds** against a real migrated
database, and `tests/integration/test_lease_two_claimants.py` validates **the actual HTTP
response body** through the app factory, token registry and router. Both branches of the
`oneOf` are covered — `assignment` and `no_work`.

## C.3 Files, tests, and the superseded record

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/jobs/service.py` | MODIFY | `8003525f…61f9dd7999` | `6017cd71924999aab3afa3bd3aafe3e3171a6a3a462229c0d66c2cbe364510fe` | 75869 |
| `tests/contract/test_worker_assignment_schema.py` | MODIFY | `9fa7c4c5…01f808415` | `9d51f7324fae43136f0c61b23dde1652e29ca5c931a7cd2d7364835d5fbfdcd4` | 20748 |
| `tests/integration/test_lease_two_claimants.py` | MODIFY | `513c9bd5…d77c22f5` | `1650c03e2ba6506d84fff0aa997608b099bc4ea5c412aed95f43e3f8aa9e122f` | 44250 |
| `evidence/runs/TC-scheduler-lease-claim-E1-20260908T064307Z.json` | CREATE | ABSENT | `ff2652079a457ed34de1b6d9b88d6f860f489c7abf7950c9ca47526bfa36e439` | 22202 |
| `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` | MODIFY | `c22de26e…66ad8208` | `808d2876d205152553f6e1fc52b11aa4096509b4c547b13f42f06575bc87c129` — now `result: STALE` | 21314 |
| `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` | MODIFY | `4aacc27d…8667b37d68` | (this file) | — |

`server/app/jobs/{router,lease}.py`, `server/app/scheduler/evaluator.py`, both migrations and
`server/app/main.py` are **byte-identical** to §1 — the router needed no change, because the
defect was in the payload the service handed it. `CR-TC-SCHED-01…05` are unchanged; `-06` is new.

### Tests

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_worker_assignment_schema.py \
  tests/integration/test_scheduler_catchup.py \
  tests/integration/test_lease_two_claimants.py -p no:warnings
```

**66 passed, 0 failed** · exit 0 · 2026-09-08T06:43:07Z → 06:43:21Z (was 60; +2 schema tests,
+2 HTTP tests, +2 alert-transaction tests). `ruff check`, `ruff format --check` clean;
`mypy --strict`: **no issues in 100 source files**.

**WC's two strict xfails now XPASS** — `tests/integration/test_collector_loop.py`: 13 passed,
2 `XPASS(strict)`. A strict xfail that passes is reported as a failure by design; that is the
signal both fixes landed, and removing the markers (plus the app fixture's `alert_port=None`)
is WC's edit, not this card's.

Full suite: **1119 passed, 3 xfailed, 11 failed** in 193 s. Two of the eleven are those
XPASSes. The other nine are in `tests/integration/test_task_credential_lease.py` (2) and
`tests/integration/test_worker_loop.py` (7), owned by the secret/settings and analysis-worker
cards landing in the same round — a timestamp format string, a `task_credential` UNIQUE
violation and an analysis `source_fingerprint` mismatch. Neither file imports
`server.app.jobs` or `server.app.scheduler`.

The `20260907T212330Z` record is now `result: STALE` with a `stale_reason` naming this packet,
both findings and `INV-06`. The new record supersedes it; both validate against
`evidence/manifest.schema.json` with **0 errors**.

---

*`PKT-TC-SCHED-FIX1` · `worker-W6A` · `lease_released_at` 2026-09-08T06:55Z · claim unchanged
`CONTRACT_READY` · `SELF_VALIDATION` — no item here is an independent audit.*

---

# ADDENDUM — `PKT-TC-SCHED-FIX2` (`CR-TC-COLLECTOR-16`: the `report_stop` response shape)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-SCHED-FIX2` · lease `LEASE-TC-SCHED-e3` (fencing 3) · worker `worker-W6A` |
| finding | `CR-TC-COLLECTOR-16` — `worker.report_stop`'s response disputed three ways; ruling: **the fixture is the oracle** |
| status | `DONE` · claim unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) · next actor `Coordinator` |
| lease_released_at | 2026-09-09T07:48Z |

The finding was right and the ruling settles it cleanly. `contracts/http/openapi.yaml` types
this response as a `GenericObject`, so the fixtures are the only concrete shape there is, and
`acceptance/fixtures/README` §3.2 makes them the sole oracle. This card answered
`{run_status, stop_reason, alert_created}` — three keys, none of them the fixture's — and
because `collector/app/client.py` reads the fixture's keys, **every field of its `StopAck` came
back blank against the real server**.

## D.1 What the four pinned events actually say

Surveying every `worker.report_stop` response in `acceptance/fixtures/**` gives four events
across three files, and they do not all say the same thing — which is why the shape was
derived from all of them rather than from the one the CR quoted:

| fixture | reason | status | body |
| --- | --- | --- | --- |
| `collection/c` seq 3 | `challenge_required` | **200** | `{run{status,phase,outcome,stop_reason}, alert_intent_created, alert_intent_id}` |
| `collection/c` seq 4 | `challenge_required` (replay) | 200 | `alert_intent_created: false`, **id unchanged** |
| `collection/e` seq 2 | `limit_reached` | 200 | `run` **adds** `limit_hit`/`limit_kind`; **no** `alert_intent_id` key |
| `collection/a` seq 2,3 | `source_layout_changed` | **409** | `{error, run, alert_intent_created, alert_intent_id}`, `run` adds `unblock_condition_vi` |

Four things follow that a reasonable implementation would get wrong:

1. **`run` is a nested block, not flattened fields.** `status`, `phase`, `outcome` and
   `stop_reason` are the state *quadruple* of `contracts/state/run.yaml`; reading any one alone
   is how I13's three outcomes get collapsed into one.
2. **A replay keeps the id.** `REQ-AC04` is "do not create a second intent", not "forget the
   first". Answering `null` on the repeat would tell the collector the alert does not exist.
3. **An absent key is not `null`.** A limit stop creates no alert, and the fixture omits
   `alert_intent_id` entirely. `null` would claim there is an alert with no id.
4. **`limit_reached` moves the phase to `enriching`** (T-RUN-02). This card left it at
   `collecting`, so even the corrected shape would have carried a wrong value. AMD-B02:
   hitting a budget is not failing. That pulled in `limit_kind` — the `run` CHECK requires it
   when `limit_hit` — which only the collector knows, so it is read from the request and a
   missing one is `VALIDATION_ERROR` rather than a guess. `x_coverage_note_vi` comes with it
   (AMD-B05), from the request or from the run's own budget.

## D.2 The 409 echo path, and where the extra fields ride

`collection/a` answers **409 to a successful report**: the run really did move to `blocked` and
the alert really was created. The 409 is the server saying "acknowledged, and here is the code
for what you reported", and the collector knows not to retry it (`client._STOP_ECHO_CODES`).
So `StopEcho` is raised **after** the transaction commits, and the test asserts the durable
state — run `blocked`, exactly one `outbox_intent` — before checking the status code.

`run` and `alert_intent_created` are **siblings of `error`**, not entries in `details_safe`.
That is not a preference: `contracts/errors.yaml` closes `SOURCE_LAYOUT_CHANGED`'s
`details_safe_keys` to six keys, none of them `run`, and `JobError` drops anything outside the
allowlist — putting them there would have silently lost them. The fixture agrees, and the test
asserts the envelope's `details_safe` stays inside its six.

**`CR-TC-SCHED-08`:** `collector/app/client.py:457-460` reads `run` and `alert_intent_created`
out of `error.details_safe`, where the contract forbids them and the fixture does not put them.
Its `_envelope` already parses the nested `{error, run, …}` shape, so the fix is on the
`ServerError` side — one file, and it is WC's, not this card's.

**`CR-TC-SCHED-07`:** only `source_layout_changed` is pinned as a 409. `challenge_required`
(`collection/c`) and `limit_reached` (`collection/e`) are pinned as 200. `session_expired`,
`source_blocked` and `rate_limited` are pinned by nothing, and no contract rule derives the
200/409 split — so they answer 200 and the gap is reported rather than guessed. The collector
accepts either nesting, so a later ruling costs no client change.

## D.3 Files, tests, and the superseded record

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/jobs/service.py` | MODIFY | `6017cd71…364510fe` | `9b3a3118dcd1aaac4bd64a6ee57efd00cdb932f3530948d0702f718bb182ca51` | 84818 |
| `server/app/jobs/router.py` | MODIFY | `285da7b6…08aa9385f` | `6884711a7714983dd1dfedc70fcd64a5d0cfb4cbf1b8ba499f0fafda13fc818f` | 19679 |
| `tests/integration/test_lease_two_claimants.py` | MODIFY | `1650c03e…8aa9e122f` | `e7ea9bd96effc278ea89144bbc0cb69cc5eb18f00aa67f9b3ea7e087b4e5f89e` | 54818 |
| `evidence/runs/TC-scheduler-lease-claim-E1-20260909T073930Z.json` | CREATE | ABSENT | `37fe6c86468e9f1e1e54c191758a92244bf6973e1c183eed47a1d2c34cc309d5` | 24940 |
| `evidence/runs/TC-scheduler-lease-claim-E1-20260908T064307Z.json` | MODIFY | `ff265207…36bfa36e439` | `8c62f19a1e78995903b9e26f4eeb573591718742ba4528d6feeec18e08c46983` — now `result: STALE` | 22839 |
| `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` | MODIFY | `4ef8e76e…c2b7d01bb8` | (this file) | — |

`server/app/jobs/lease.py`, `server/app/scheduler/evaluator.py`, both migrations,
`server/app/main.py` and `tests/contract/test_worker_assignment_schema.py` are **byte-identical**
to the previous addendum. `CR-TC-SCHED-01…06` unchanged; `-07` and `-08` are new.

### Tests

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_worker_assignment_schema.py \
  tests/integration/test_scheduler_catchup.py \
  tests/integration/test_lease_two_claimants.py -p no:warnings
```

**71 passed, 0 failed** · exit 0 · 2026-09-09T07:39:30Z → 07:39:43Z (was 66; +5 stop-response
tests). Each of them reads the expected key set **out of the fixture** rather than typing it,
so a change to a pinned example fails the test instead of leaving it agreeing with a stale
copy of itself. Both the 200 and the 409 are read from the real HTTP body through `TestClient`.

`ruff check` and `ruff format --check` clean. `mypy --strict` clean for `server/app/jobs` and
`server/app/scheduler`; one `unused-ignore` remains in `server/app/secret/store.py`, a sibling
card's file.

Full suite: **1153 passed, 3 xfailed, 1 failed** in 170 s. The single failure is an
`XPASS(strict)` in `tests/integration/test_collector_loop.py` for `CR-TC-COLLECTOR-15`, whose
own marker text attributes the defect to `server/app/wiring.py` and states this card's service
is correct; WS fixed it, so removing the marker is WC's edit. WC's two earlier markers
(`CR-TC-COLLECTOR-11`/`-12`) are gone, and the nine secret/settings and worker-loop failures
seen at FIX1 are gone too.

The `20260908T064307Z` record is now `result: STALE` with a `stale_reason` naming this packet,
the finding and `INV-06`. Both records validate against `evidence/manifest.schema.json` with
**0 errors**.

---

*`PKT-TC-SCHED-FIX2` · `worker-W6A` · `lease_released_at` 2026-09-09T07:48Z · claim unchanged
`CONTRACT_READY` · `SELF_VALIDATION` — no item here is an independent audit.*
