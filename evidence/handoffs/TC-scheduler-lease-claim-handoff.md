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
