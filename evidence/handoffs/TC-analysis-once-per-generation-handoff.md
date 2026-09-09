# HANDOFF — `TC-analysis-once-per-generation`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ANALYSIS` — card `agent-tasks/TC-analysis-once-per-generation.md` (Phase 3, M3, gate G5) |
| worker principal | `worker-W3B` |
| authority_id | `AUTH-COORD-TC-ANALYSIS` (parent `AUTH-OWNER-20260908-06` / `-09`; records `precode/owner-decisions-06.md`, `packets/OWNER-DECISIONS-20260908-08.md`) |
| lease_id | `LEASE-TC-ANALYSIS-e1` (exclusive on card §3 write set + migration + handoff + evidence manifest + one delimited block in `server/app/main.py`) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `CONTRACT_READY` for the seven `analysis.*` operations and invariants I04/I10/I14/I16. The card's §9 ceiling is `IMPLEMENTATION_VERIFIED`, but this record is `SELF_VALIDATION` and protocol §9 caps a self-check at `CONTRACT_READY`. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T19:45Z (host clock; the repo's documents run on a 2026-09-08 calendar — see §7) |

`DONE_WITH_CONCERNS` rather than `DONE` for three reasons, all recorded below and none of
them a silent gap: the card's §13 asks that the run be registered in `evidence/index.json`
and that file is **not** in the granted write set (§2); one obligation of the card is `xfail`
pending a Phase 4 card (§4); and one semantic check, SV-05, is not implemented because the
input it compares against has no path into this service yet (`CR-TC-ANALYSIS-05`).

---

## 0. Wait gate and baseline

The packet's wait gate was honoured before the first byte was written.

* `agent-tasks/README.md` line 124 declares pin epoch **`PC10-PIN-P3-20260908`**.
* `evidence/handoffs/PC10-handoff.md` line 3269 carries the **`PKT-PC10-FIX24`** addendum,
  `lease_released_at 2026-09-08T00:45Z`, packet `PKT-PC10-FIX24` / lease `LEASE-PC10-e25`.
* **SG-HASH**, re-run against disk immediately before the first write: the card's §0 pins
  **26 sources** (2 spec/plan + 24 contracts and fixtures); every one was re-hashed with
  `sha256` and compared on both digest **and** byte count. **0 mismatches.** The card's own
  epoch line reads `PC10-PIN-P3-20260908`, and
  `grep -ho 'Pin epoch: ...' agent-tasks/TC-*.md | sort -u` resolves to exactly that one name
  across all 19 cards.
* **SG-PC09**: `acceptance/scenarios.yaml` was read at its current bytes (it is deliberately
  unpinned). SC28's `oracle_vi` — one valid row per `(K, g)` after every step, total model
  calls ≤ `analysis_attempts_per_item` = 2, `usage.unknown` with three nulls, an attempt never
  counted as a result — agrees with the card's §8 line for line. No conflict, no CR.

No file under `contracts/`, `acceptance/`, `precode/` or `agent-tasks/` was modified.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/analysis/key.py` | CREATE | ABSENT | `cca4d9291d025041759816c4121d02a43a63afa448f710b3d092efe41be8b2f9` | 10956 |
| `server/app/analysis/repository.py` | CREATE | ABSENT | `648ae9b428b366ac7afa1827303a52deee73ee7cf8cfdf8c7eeb0f7a898bd204` | 24428 |
| `server/app/analysis/service.py` | CREATE | ABSENT | `a95b78401683a077775c2333f07d375296a161b23bc19825fe94cec129ed3991` | 83223 |
| `server/app/analysis/router.py` | CREATE | ABSENT | `e08ae84fa63b0fe7ac95f2dfb168ffc51a9ed6c269a46a00840b276f26038d73` | 18369 |
| `server/migrations/versions/0006_tc_analysis_once_per_generation.py` | CREATE | ABSENT | `a12bc6e493a9f8c3bda9b534128ed54af56466d6a5788532a7afec52532c8c0f` | 14210 |
| `tests/contract/test_analysis_key.py` | CREATE | ABSENT | `70db817c5969cac7a1c121c4ac5a570e87605641d77305d78f091220d08b9a90` | 10852 |
| `tests/integration/test_analysis_once_per_key.py` | CREATE | ABSENT | `f00d16a69355ef4a379de3495cd8ac85a850b19fefbccb41239a7cc35d72109e` | 25344 |
| `tests/integration/test_attempt_not_result.py` | CREATE | ABSENT | `7e6d533d99ada902596fd92b90a62fd8960eda03f0a0d36f5cc6b2cb9d807134` | 25637 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json` | CREATE | ABSENT | `3e2cce7c7ec7cca33f8bd54a5fa8b1e8563f1aa5771f0b3fa7460e2aa2df9e9f` | 18329 |
| `evidence/handoffs/TC-analysis-once-per-generation-handoff.md` | CREATE | ABSENT | (this file) | — |
| `server/app/main.py` | MODIFY | see below | `8d534ebea326038a2633e07449a06bb5d71bd3828e9413850936320447cfcb59` | 11088 |

**`server/app/main.py` is shared and five sibling cards appended to it in this same wave.**
The before-hash of *this* card's edit is therefore not the `HEAD` blob
(`2adbf75e…`, 7696 bytes) and the after-hash above will keep moving as siblings land — that
is a fact about the file, not a claim about this delta. What this card changed is exactly one
delimited block, lines 184–200:

```
    # >>> TC-analysis-once-per-generation (MOD-analysis-service) >>>
    ...
    from server.app.analysis.router import install_analysis_error_handlers
    from server.app.analysis.router import router as analysis_router

    install_analysis_error_handlers(app)
    app.include_router(analysis_router)
    # <<< TC-analysis-once-per-generation <<<
```

Both imports sit **inside** the delimiters (finding `F-A3R1-13`). No byte outside that block
was touched; the eight blocks in the file at handoff time (`grep -n '>>>\|BEGIN include'`)
are seven siblings' plus this one.

The **Alembic graph has exactly one head.** A sibling in this wave had already written
`0007_merge_phase3_5_heads`, whose `down_revision` tuple already names
`0006_tc_analysis_once_per_generation`, so this card wrote no merge revision of its own:
one would have created a second head rather than removed one.
`tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head` passes,
and the assertion is structural (`len(heads) == 1`), never a literal.

---

## 2. Scope: what is NOT in this delta, and why

* **`evidence/index.json`** — card §13 asks for the run to be registered there. The dispatch
  packet grants card §3 + the migration + this handoff + the evidence manifest, and that file
  is outside it. It was not touched, and no sibling in this wave has registered either.
  Registration is a Coordinator action or a separate packet (`CR-TC-ANALYSIS-08`).
* **`analysis` and `work_label`** — created by `0002b_shared_move_set_tables` as custodian
  *on behalf of this module*. This card takes ownership of the rows; it issues no second
  `CREATE TABLE`, which is precisely the defect `F-A3R1-01` was. What `analysis` still lacks
  is two `REFERENCES` clauses — see `CR-TC-ANALYSIS-03`.
* **`pending_item_ledger`, `provider_config`, `post`, `work_version`** — owned by
  `MOD-report-service`, `MOD-settings-service` and the ingest/identity cards. Reached through
  ports (`PendingLedgerPort`, `ProviderConfigPort`, `TaskInputPort`), never read directly. The
  repository in this package is scoped to five tables and would not compile a query against
  any of them.

---

## 3. What was built

### 3.1 The key is the whole of AC-06

`server/app/analysis/key.py` builds the seven components of `ENT-analysis.analysis_key` and
**refuses** the names the contract excludes on purpose — the tag family, the provider/model
family, the report family — rather than ignoring them. This matters more than it looks:
"removing and re-adding a tag calls no model" is not a branch anyone can inspect, it is a
property of the key. If a tag were an input, no downstream care could keep the promise;
because it is not, the promise holds for code paths nobody has written yet. Silently dropping
an excluded field would keep today correct and make tomorrow's regression invisible, so the
refusal names the offending field at the call site.

### 3.2 The two tables that make I16 structural

`analysis_attempt` records every try. `analysis` records results. There is exactly one
function in the package that inserts into `analysis` (`_commit_result`) and it is reachable
only after **both** validation gates pass. No branch anywhere falls back to reading
`analysis_attempt` when the result query comes back empty.

An attempt row is opened **at claim time** as `timeout_unknown` with `cost_uncertain = 1`.
That is not a placeholder — it is the honest state: from the moment the work is handed out
until an outcome is reported, the server does not know whether the model ran, and SRC-PLAN §10
forbids claiming that no cost was incurred for something nobody knows. A worker that dies
mid-flight therefore leaves exactly the row fixture `i` expects, with no recovery code having
to reconstruct it, and the database CHECK
`outcome <> 'timeout_unknown' OR cost_uncertain = 1` makes the dishonest combination
unrepresentable.

### 3.3 A rejected result is persisted, not rolled back

`analysis.submit_result` validates on a **read** snapshot and then chooses which transaction
the consequences belong in. A rejection has durable consequences of its own (T-AN-04: the
attempt closes `schema_invalid`, the budget is spent, the task goes to `retry_wait` or
`failed`), and those must survive; rolling them back together with the insert that never
happened would lose the record of the try. The accept path re-checks the lease **inside** the
write transaction, because a sweep may have taken the task away between the read and the
write — checking only on the read snapshot is precisely the stale-writer hole I10 names.

### 3.4 Provider `enabled: false` is honoured at two gates

`contracts/ai/providers.yaml` ships both Anthropic adapters `enabled: false` (ISO-03/ISO-05
unverified). `claim_task` hands out **no task** for a task type whose provider is disabled:
dispatching a task whose only possible next step is a call the Owner has not enabled would be
handing a worker an instruction to break the contract. `verify_task_lease` refuses to
authorise a credential for the same reason. An **unwired** provider registry counts as
not-enabled: an undetermined state is never converted into a good one (CAP-P5, I13).

No provider was called from the server in any run, and none can be: `ai.run_inference_task`
belongs to `MOD-analysis-worker` on the personal machine.

---

## 4. Verification

Command, run from `/mnt/virtual/repo/xcrawl`, `PYTHONDONTWRITEBYTECODE=1`:

```sh
python -m pytest tests/contract/test_analysis_key.py \
                 tests/integration/test_analysis_once_per_key.py \
                 tests/integration/test_attempt_not_result.py -p no:warnings -p no:cacheprovider -q
```

`2026-09-07T19:42:47Z` → `19:42:57Z`, **exit 0**, **33 tests: 32 passed, 1 xfailed, 0
failed.** The card's §8 lists the three commands separately; they were also run that way and
give 10 / 12 / 11 (`10 passed`, `12 passed`, `10 passed + 1 xfailed`).

Gates re-run in the same tree:

| Gate | Result |
| --- | --- |
| `tests/contract/test_schema_matches_entities.py` | **PASS**, 10 tests. The four new tables match `entities.yaml` field-for-field in **both** directions, every pinned unique key is on disk (including the partial `ux_analysis_task_open`), and the DDL is byte-identical under all four traversal orders. `test_alembic_has_exactly_one_head` PASS. |
| full `pytest` | **817 passed, 11 xfailed, 0 failed**, exit 0, 101 s |
| `ruff check` + `ruff format --check` | clean on `server/app/analysis/`, the migration and the three test files |
| `mypy --strict` (repo config) | `Success: no issues found in 49 source files` |

The one **xfail** is deliberate and `strict=True`:
`test_a_failed_item_is_recorded_in_the_pending_item_ledger` — `pending_item_ledger` belongs to
`MOD-report-service` (`TC-report-coverage-publish-cas`, Phase 4, absent). The B04/B17
obligation "a budget-exhausted item must not simply vanish from the report" is therefore
**NOT established** by this run. `ledger_state()` reports the port as unwired rather than the
service pretending the entry was made.

### 4.1 The oracles, as numbers

Every oracle in the card's §8 is a row count, a hash comparison or an error code — never a
log read.

* **AC-06.** After a result is committed, the report-builder enqueue path is run **again**
  over the same target, exactly as it would be after a tag edit. Result: `created == []`,
  `skipped == [{"target_key": …, "reason": "already_valid"}]`, and three deltas measured by
  SQL are zero — `COUNT(analysis_generation)`, `COUNT(analysis_attempt)`, provider call
  counter. The point of re-running the path rather than not calling anything is that "we
  didn't call it" would prove nothing.
* **Resubmit same key.** Fixture `j` events 1–3: `COUNT(analysis WHERE status='valid') = 1`
  after all three; event 2 returns `duplicate_replay` with the same `payload_hash` and
  `analysis_id`; event 3 raises `IDEMPOTENCY_CONFLICT` (409) and the stored `payload_hash` is
  unchanged.
* **Crash after provider.** Fixture `i`: the expected attempt row is compared **column by
  column** (`outcome`, `error_code`, `started_at`, `ended_at IS NULL`, `worker_lease_id`,
  `cost_uncertain`, `attempt_number`), and the fixture's `counts` are asserted —
  `analysis[status='valid'] = 0`, `analysis_attempt[cost_uncertain=true] = 1`.
* **The forbidden effects, as counterexamples.** Fixture `i` forbids "recovering the result
  from the worker's log and writing it as valid". The test has the old worker come back with a
  perfectly well-formed result: refused `WORKER_LEASE_EXPIRED` (412), `COUNT(valid)` still 0.
* **I16 as the query the system runs.** `find_valid_by_key` returns `None` while
  `COUNT(analysis_attempt) = 1`.
* **SG-DENY / R5-01.** `enqueue_tasks` from `MOD-x-collector`, `MOD-analysis-worker` and
  `MOD-telegram-adapter` raises **`FORBIDDEN_EDGE` (403)** — not `UNAUTHORIZED` — and all four
  tables stay empty. `analysis.enqueue_tasks` has `transport: internal`, so the only way to
  reach it is an in-process call, which is row 2 of the boundary table.
* **E2.** `WriteFaultInjector.disk_full()` around `submit_result`: `STORAGE_WRITE_FAILED`
  (503), `COUNT(valid) = 0`, the task still `running` (not stranded, not finished), the
  attempt not concluded — and the very same submit commits once the disk returns.

### 4.2 Type agreement with `TC-analysis-adapter-validation`

W3A's `worker/app/adapter/` landed during this packet, so the agreement is tested for real
rather than xfailed: the payload of `analysis.get_task_input` is fed straight into the
adapter's `TaskInput`, and `input_source_ids` (the closed set SV-02 holds every citation to)
and `timeout_seconds` are asserted to match what the server granted. The import is guarded
with `importorskip(reason="pending TC-analysis-adapter-validation")` so the file stays honest
if the sibling is ever rolled back.

---

## 5. Change requests

| ID | Against | Finding |
| --- | --- | --- |
| `CR-TC-ANALYSIS-01` | `contracts/data/entities.yaml` `ENT-assignment-lease`, ownership | This migration creates `assignment_lease` as **custodian**. The table's `owner_module` is `MOD-job-service` and `owned_by_package` is PC03; the card that takes it over is `TC-scheduler-lease-claim`, which must **extend** revision `0006_tc_analysis_once_per_generation` rather than issue a second `CREATE TABLE` — two definitions of one table is exactly `F-A3R1-01`. It had to be created here because `contracts/state/analysis.yaml` T-AN-02/T-AN-11 and `contracts/ports.yaml` state the whole analysis claim in terms of `lease_id` + `lease_epoch`, and `ENT-assignment-lease` is the only place the contract gives the epoch a home; without it this card's stale-worker oracle cannot run at all. Same pattern and same reasoning as `0002b_shared_move_set_tables`. |
| `CR-TC-ANALYSIS-02` | `contracts/data/entities.yaml` `ENT-assignment-lease.run_id`, `ENT-analysis-task` | `assignment_lease.run_id` is `NOT NULL` and points at `run`, but an **analysis** claim is not scoped to a collector run: labelling is enqueued after an ingest commit, and `summary` is enqueued by the report builder, which has no run at all. `ENT-analysis-task` has no column that could carry one, so the value cannot be recovered at claim time from stored state. The service does **not** invent one: `claim_task` refuses with an internal-dependency error (`INTERNAL`, never a 4xx) when no run id is wired. Change control should either make the column nullable for non-collector jobs or give `ENT-analysis-task` a run reference. |
| `CR-TC-ANALYSIS-03` | `server/migrations/versions/0002b_shared_move_set_tables.py` vs `ENT-analysis` | `analysis.analysis_generation_id` and `analysis.accepted_from_attempt_id` are declared as foreign keys in `entities.yaml` but carry no `REFERENCES` clause on disk: `0002b` created the table before either referenced table existed. Both now exist. Adding the clauses means rebuilding the table under SQLite, and `work_label.analysis_id` references `analysis` — the "recreate" this card was told not to do. Both references are enforced in `TXN-analysis-accept` instead, which reads the generation row and the attempt row in the same transaction as the insert. A rebuild belongs in its own packet. |
| `CR-TC-ANALYSIS-04` | `contracts/ports.yaml` `analysis.claim_task`, `analysis.request_reanalysis` | Both declare `idempotency: required: true` (`claim_request_id`, `request_id`), but no entity has a column to store either key. The implementation keeps a **process-local** registry and says so in the code: after a restart, the same `claim_request_id` can issue a fresh lease. What is durable is the property that matters — `UPDATE … WHERE state = 'pending'` plus `ux_lease_job_epoch` mean no task ever has two live leases, and `ux_analysis_valid_key` means no key ever has two results. Making the wire-level idempotency durable needs a column, which is change control, not a card. |
| `CR-TC-ANALYSIS-05` | `contracts/ai/tasks.yaml` SV-05, `contracts/ports.yaml` `analysis.get_task_input` | SV-05 requires `member_refs` to equal the input `member_target_keys` and every number in the text to match the input `density`. Both are computed by `MOD-report-service` **before** the task exists (CR-PC04-05), and `analysis.get_task_input`'s response has no field to carry them — so the server has nothing to compare against and SV-05 is **not implemented**. SV-01…SV-04, SV-06 and SV-07 are implemented and tested. Either `get_task_input` gains the two fields or the check moves to the report side. |
| `CR-TC-ANALYSIS-06` | `contracts/ports.yaml` `analysis.request_reanalysis` vs `ENT-analysis-generation.reason` | `ports.yaml` writes the wire reasons as `manual` \| `new_paper_version`; `entities.yaml` owns the stored enum as `owner_reanalysis` \| `new_work_version`. The code accepts both spellings and **stores** the entities.yaml value (ruling R-03: entities.yaml is authoritative). The same class of divergence as CR-PC03-05 for `task_type`, and it should be converged the same way. |
| `CR-TC-ANALYSIS-07` | card §13 vs `evidence/manifest.schema.json` | The card names the manifest `EVM-TC-analysis-once-per-generation`; the schema constrains `evidence_id` to `^EV-(PC[0-9]{2}\|A[0-9]\|E[0-4]\|COORD)-[0-9]{2,3}(-[a-z0-9-]+)?$`, which that name cannot match. The schema wins because it is a gate that runs; the manifest uses `EV-E1-01-tc-analysis-once-per-generation`. Every other Phase 1–5 card has done the same. |
| `CR-TC-ANALYSIS-08` | card §13, dispatch write set | The card asks for registration in `evidence/index.json`; the write set does not grant it. Not touched. Coordinator action or a separate packet. |

Nothing in `contracts/`, `acceptance/`, `precode/` or any fixture was edited to make a test
pass.

---

## 6. Evidence record

`evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json`,
`evidence_id` `EV-E1-01-tc-analysis-once-per-generation`, `review_type`
**`SELF_VALIDATION`**, `evidence_level` `E1` (with the E2 fault-injection case noted inside
it), `result` `PASS`. It validates against `evidence/manifest.schema.json` under
`Draft202012Validator` with the format checker enabled: **0 errors**. Its
`baseline.contract_hashes` are copied verbatim from the card's §0 (24 entries plus the card's
own hash), and `implementation_revision` carries the sha256 of all eight source files.

Nothing here is an independent audit. `audit_route` for this card remains
`INDEPENDENT_REQUIRED`; the reviewer scope is card §12 (13 transitions of
`contracts/state/analysis.yaml`, ADR-0008, fixtures `i` / `j` / `b`, and the two mandatory
questions: does a tag edit move the key, and can an attempt reach the result view).

---

## 7. Limits, side effects, and what is not established

* **Not established: `IMPLEMENTATION_VERIFIED`.** That is the card's ceiling, not a
  self-check's. It needs an independent audit over these exact bytes.
* **Not established: anything about a real AI provider.** Zero provider calls, zero network
  calls, zero secrets. E3/E4 `NOT_RUN`. `REQ-OQ03` leaves both adapters disabled, and
  `REQ-AC16` is out of this card's scope entirely — where it is reported, it must be
  `BLOCKED`, never `FAIL` (`providers.yaml` §4).
* **Not established: the pending-item ledger obligation** (xfail, pending
  `TC-report-coverage-publish-cas`).
* **Not established: SV-05** (`CR-TC-ANALYSIS-05`).
* **Not established: durable idempotency** for `claim_task` / `request_reanalysis` across a
  process restart (`CR-TC-ANALYSIS-04`).
* **Not established: behaviour under real concurrency.** "Two workers, one lease" is proved
  by two **sequential** calls resting on `UPDATE … WHERE state='pending'` and
  `ux_lease_job_epoch`. Correct at the constraint layer; not measured under real contention.
* **Tool side effects.** `PYTHONDONTWRITEBYTECODE=1` throughout — no `__pycache__` exists
  anywhere in the tree. `.pytest_cache/` at the repo root was already present (PC10-FIX23
  records it) and pytest runs in this packet wrote to it; the final full run used
  `-p no:cacheprovider`. Temporary databases were created only under pytest `tmp_path` and
  one probe database under this worker's scratch directory, never inside the repo. No git
  mutation of any kind.
* **Clock.** The host clock reads 2026-09-07 while the packet, the pin epoch and the sibling
  handoffs run on a 2026-09-08 calendar. Timestamps in the manifest and in the run filename
  are the **host** clock, unadjusted, so they can be checked against the tool output that
  produced them. The wait-gate check does not depend on this: it read the two documents, not
  the clock.

---

*`PKT-TC-ANALYSIS` · `worker-W3B` · `lease_released_at` 2026-09-07T19:45Z · claim
`CONTRACT_READY` · `SELF_VALIDATION` — no item in this handoff is an independent audit.*

---

# ADDENDUM — `PKT-TC-ANALYSIS-FIX1` (audit finding `F-A3-P3-03`)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ANALYSIS-FIX1` · lease `LEASE-TC-ANALYSIS-e2` (fencing 2) · `worker-W3B` |
| scope granted | card §3 test files + this handoff + manifest re-issue |
| finding | `F-A3-P3-03` (`…/scratchpad/audits/A3-P3-R1-report.md`): `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` sits in the card's §2 read set but was neither exercised by a test nor recorded `NOT_RUN`. |
| status | **`DONE`** — the finding is addressed both ways: the part of the fixture this card owns is now executed, and the part it does not own is recorded `NOT_RUN` with the concrete reason. |
| claim change | **none.** Still `CONTRACT_READY` / `SELF_VALIDATION`. |
| lease_released_at | 2026-09-07T20:30Z |

## A.1 What was done with `FX-RP-E`

The fixture was read in full and split along the module boundary rather than being handled as
one thing, because it is not one thing: four of its five oracles are report-service oracles
and one is this card's.

**Exercised** — new test
`tests/integration/test_analysis_once_per_key.py::test_a_late_summary_commits_and_touches_no_published_period`:

* **event 1** — E1 (`work:01JWRKE1000000000000000000`, taken from the fixture's own
  `given.rows.work`) was selected but has no summary, so the report builder enqueues one.
  Asserted: exactly one task created, for exactly that target key.
* **event 3** — the summary arrives at 18:00, five hours after period 2 was published at
  13:00:05, and commits normally. The fixture's `forbidden_effects` include *"sửa report kỳ 2
  để chèn summary về muộn (I05)"*. Read from this side the prohibition is stronger than "do
  not amend": `contracts/modules.yaml` FE-13 gives this module no edge to
  `MOD-report-service` at all. So the oracle is measured as **row counts of every table in
  the schema**, enumerated from `sqlite_master` rather than hand-listed, before and after the
  late commit: the set that moved must be a subset of the five tables this module writes and
  must contain `analysis`. A `report`, `saved_*`, `tag`, `delivery` or `coverage_window` table
  that moved would fail the assertion, and a table added by a future migration is covered the
  day it appears.
* The committed row is compared against the fixture's own
  `expected.report.items[0].analysis`: `task_type = summary`, `generation_number = 1`,
  `evidence_level = abstract`, `analyzed_at = 2026-09-06T18:00:00.000Z`.
* A second build for the same target afterwards enqueues nothing — the same skip AC-06 rests
  on, now shown on the late-discovery path too.

One detail worth recording because it looked like a bug and is not: the first draft claimed
at 13:00 and submitted at 18:00, and was correctly refused `WORKER_LEASE_EXPIRED` —
`lease_ttl_analysis` is 900 s. The five-hour gap in the fixture is between the *publish* and
the *result*, not between the claim and the result, so the worker picks the task up shortly
before finishing. The test says so in its docstring rather than leaving the timing as a
magic number.

**`NOT_RUN`, with the reason** — everything else in `FX-RP-E` belongs to
`MOD-report-service` (`TC-report-coverage-publish-cas`, Phase 4, absent), and there is no
table in the schema to read it from: `pending_item_ledger` moving `pending` →
`resolved_reported_late` inside the period-3 publish transaction; the `late_discovery` label
with `item_type` staying `new_discovery`; period 2 carrying `quality='partial'` with
`summary_state='pending'`; and coverage advancing past E1's `discovered_at` (I06). This card
may not create those tables, so the obligations are recorded `NOT_RUN` in the re-issued
manifest's `limitations.not_checked_vi` — not silently skipped. This is the same dependency
that already holds `test_a_failed_item_is_recorded_in_the_pending_item_ledger` at `xfail`.

No fixture byte was edited. The submitted document is fixture `j`'s canonical result with its
`analysis_key.target_key` pointed at E1, because the key is a function of the assignment and
E1 is the target `FX-RP-E` assigns: the identities come from `FX-RP-E`, the document shape
from `FX-AI-J`, and nothing is invented.

## A.2 Hashes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `tests/integration/test_analysis_once_per_key.py` | MODIFY | `f00d16a69355ef4a379de3495cd8ac85a850b19fefbccb41239a7cc35d72109e` (25344 B) | `35cf9c70fa1752c153396ca7aa7aaef11e350b97e64b74f535489cbda92a9029` | 33739 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260907T202638Z.json` | CREATE | ABSENT | `61dbbd2a8313505949cf05d5774f329793712255dba2dc51ff0b144818d3a66d` | 22533 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json` | MODIFY | `3e2cce7c7ec7cca33f8bd54a5fa8b1e8563f1aa5771f0b3fa7460e2aa2df9e9f` (18329 B) | `7c151fe89b9ab72e376fa30bd210d4cfad16fb03b1c436d1098b660e8805a82f` | 18983 |
| `evidence/handoffs/TC-analysis-once-per-generation-handoff.md` | MODIFY | — | (this file) | — |

`tests/contract/test_analysis_key.py` (`70db817c…`) and
`tests/integration/test_attempt_not_result.py` (`7e6d533d…`) are **unchanged**, as is every
file under `server/`. Nothing under `contracts/`, `acceptance/`, `precode/` or `agent-tasks/`
was touched.

The old manifest is now `result: "STALE"` with a `stale_reason` naming this packet and the
byte change that caused it; the re-issued one is
`EV-E1-02-tc-analysis-once-per-generation`, `result: "PASS"`, and carries an
`invalidation.invalidated_by_paths` list plus `INV-06` so the next byte change invalidates it
by rule rather than by someone remembering. Both validate against
`evidence/manifest.schema.json`: **0 errors each.**

## A.3 Verification

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contract/test_analysis_key.py \
  tests/integration/test_analysis_once_per_key.py \
  tests/integration/test_attempt_not_result.py -p no:warnings -p no:cacheprovider -q
```

`2026-09-07T20:26:38Z` → `20:26:47Z`, **exit 0**, **34 tests: 33 passed, 1 xfailed, 0
failed** (was 33/32/1). Per file: 10 / 13 / 10+1xfail. Adding
`tests/contract/test_schema_matches_entities.py` to the same invocation: **44 tests, 43
passed, 1 xfailed, exit 0**, one Alembic head. `ruff check`, `ruff format --check` and
`mypy --strict` (49 files) clean.

**Full suite: `1 failed, 826 passed, 9 xfailed`, exit 1.** The failure is
`tests/integration/test_multipart_partial_receipt.py::test_the_adapters_sender_can_report_a_provider_message_id`
(`TC-telegram-unknown-delivery`), and it **passes when run alone**. A run one minute earlier
in the same tree showed a second, different failure —
`tests/integration/test_concurrent_save.py::test_cmd_save_goes_through_this_service`, a
`TypeError` on `TelegramSaveAdapter.create_save(target_ref=…)` — which had cleared by the next
run. Five sibling cards are editing this working tree concurrently, so the suite is in flux;
no file of this card's write set is involved in either failure, no test of this card is
affected, and the 19:4xZ run recorded in the superseded manifest was `817 passed, 0 failed`.
Reported as observed rather than smoothed over.

## A.4 CRs

No new change requests. `CR-TC-ANALYSIS-01`…`-08` stand unchanged. `F-A3-P3-03` is addressed
and needs no contract change: the fixture was usable, it just had to be split along the
module boundary the fixture itself crosses.

---

*`PKT-TC-ANALYSIS-FIX1` · `worker-W3B` · `lease_released_at` 2026-09-07T20:30Z · claim
unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) — no item here is an independent audit.*

---

# ADDENDUM 2 — `PKT-TC-ANALYSIS-FIX2` (pending-ledger xfail re-checked)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ANALYSIS-FIX2` · lease `LEASE-TC-ANALYSIS-e3` (fencing 3) · `worker-W3B` |
| scope granted | card §3 test files + this handoff + manifest re-issue |
| status | **`DONE`** — premise re-checked against the tree, half flipped to a real passing test, half kept `xfail` with the measured reason. |
| claim change | **none.** Still `CONTRACT_READY` / `SELF_VALIDATION`. |
| lease_released_at | 2026-09-08T00:52Z |

## B.1 The premise, checked rather than assumed

W4A's `pending_item_ledger` (revision `0010_tc_report_coverage_publish_cas`) and W4B's
`server/app/report/pending.py` are both on disk, and `EngineBoundPendingLedger` implements
`record_pending(*, target_key, reason)` — exactly the `PendingLedgerPort` Protocol this
service has carried since Phase 3. So the port fits. The question CR-TC-BACKFILL-02/-08 left
open is whether it fits **at the call site that matters**, and that was measured with a probe
before any test was touched:

```
call OUTSIDE a transaction          -> ok in 0.00s
call INSIDE an open write txn       -> FAILED after 5.01s:
                                       OperationalError: database is locked
```

`_fail_task` calls the ledger from inside `TXN-analysis-*`. The port takes no connection, so
`EngineBoundPendingLedger` opens a **second** one; on SQLite the outer transaction already
holds RESERVED, so the inner INSERT waits out `busy_timeout` and dies. That is W4B's own
`CR-TC-BACKFILL-02` ("the port should carry the connection"), now with a measurement attached
rather than a prediction. Fixing it means changing the port signature or using a
connection-carrying variant — a `server/` edit, which this packet's lease does not cover, and
a retry loop would be the wrong answer anyway.

## B.2 What changed in the tests

**New, passing** — `test_the_pending_ledger_port_is_wired_and_speaks_this_card_s_vocabulary`.
Everything that is genuinely real now is asserted through W4B's actual implementation, no
stub: `ledger_state()` flips to `wired: True` (the honest signal, now honest in the other
direction); both `reason` values this card produces — `analysis_failed` (T-AN-07) and
`analysis_unknown` (T-AN-10) — are members of W4B's closed `REASONS` enum, asserted because
two modules agreeing on a vocabulary is the kind of thing that goes quietly false after one
refactor; and a real `record_pending` writes exactly one row with `state='pending'` and
`first_pending_window_id` pinned to a `coverage_window` seeded from fixture `reporting/e`'s
own row, with a second call a no-op through `ux_pending_owner_target_open`.

**Kept `xfail`, much tighter** — `test_a_failed_item_is_recorded_in_the_pending_item_ledger`.
It was `xfail(strict=True)` asserting one line, with the reason "the table does not exist".
It is now `xfail(strict=True, run=True, raises=OperationalError)` and **drives the real
obligation end to end**: two unknown outcomes exhaust the attempt budget,
`auto_rerun_unknown_attempt` moves the task to `failed`, and the ledger row is asserted. Three
things improved: the test actually runs, the failure mode is pinned (a *different* breakage
now fails rather than passing as expected-failure), and the day the port grows a connection
parameter this flips to a failure someone has to look at instead of sitting green. The
adapter's engine gets a 200 ms `busy_timeout` of its own so the proof costs a fifth of a
second rather than five.

## B.3 Hashes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `tests/integration/test_attempt_not_result.py` | MODIFY | `7e6d533d99ada902596fd92b90a62fd8960eda03f0a0d36f5cc6b2cb9d807134` (25637 B) | `6bb729cecde8cd525fd999a90320ed08114f395e10a20399f44ecb221526f1ba` | 33753 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260908T004550Z.json` | CREATE | ABSENT | `a9a6e088e068b966cc05ceee77c253e7e6c1ae14f6af1466a655ee394e219ec1` | 24756 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260907T202638Z.json` | MODIFY | `61dbbd2a…` (22533 B) | `01fe7860069174769660050037eb40d9960f266e3b478872d342e5bcb1bde054` | 23113 |
| `evidence/handoffs/TC-analysis-once-per-generation-handoff.md` | MODIFY | — | (this file) | — |

`tests/contract/test_analysis_key.py` (`70db817c…`) and
`tests/integration/test_analysis_once_per_key.py` (`35cf9c70…`) are **unchanged**, as is
every file under `server/`. Nothing under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was touched. The chain of evidence records is now
`EV-E1-01` (STALE) → `EV-E1-02` (STALE) → **`EV-E1-03` (PASS)**, each carrying a
`stale_reason` naming the packet and the byte change that retired it; all three validate
against `evidence/manifest.schema.json` with **0 errors**.

## B.4 Verification

Card command, `2026-09-08T00:45:50Z` → `00:45:59Z`, **exit 0**, **35 tests: 34 passed, 1
xfailed, 0 failed** (was 34/33/1). Per file: 10 / 13 / 12. `ruff check`,
`ruff format --check` and `mypy --strict` (64 source files now) clean.

**Full suite: `1022 passed, 7 xfailed, 0 failed`, exit 0** (125.6 s). A run a few minutes
earlier showed 7 *errors* in `tests/integration/test_permanent_failure_report_intact.py` —
fixture-setup errors visible only in a whole-suite run, which passed 7/7 when that file was
run alone and were gone by the next full run. The Phase 4/6 sibling cards were landing during
that window; no file of this card's write set is involved.

## B.5 CRs

No new change requests of this card's own. `CR-TC-ANALYSIS-01`…`-08` stand.
**`CR-TC-BACKFILL-02` (W4B's) is now supported by a measurement** rather than by inspection,
and this card is a concrete consumer blocked by it: until the port carries a connection, the
B04/B17 end-to-end obligation cannot be satisfied from inside `TXN-analysis-*`. Recorded in
the manifest's `unresolved_issue_refs`.

---

*`PKT-TC-ANALYSIS-FIX2` · `worker-W3B` · `lease_released_at` 2026-09-08T00:52Z · claim
unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) — no item here is an independent audit.*

### B.6 Correction to §7 of the base handoff

§7 recorded "no `__pycache__` exists anywhere in the tree". That was true when it was
written and is **no longer true**: `tests/__pycache__` and
`shared/rr_contracts/rr_contracts/__pycache__` exist as of this addendum. Every command in
all three of this card's packets ran under `PYTHONDONTWRITEBYTECODE=1`, including the mypy and
schema-validation invocations, so they are not this worker's — they appeared during the window
in which the Phase 4/6 sibling cards were landing. They are left in place rather than deleted:
removing another worker's tool output is a mutation outside this lease. Recorded here so the
earlier sentence is not read as still current.

---

# ADDENDUM 3 — `PKT-TC-ANALYSIS-FIX3` (pending-ledger obligation closed)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ANALYSIS-FIX3` · lease `LEASE-TC-ANALYSIS-e4` (fencing 4) · `worker-W3B` |
| scope granted | `server/app/analysis/service.py` (the `_fail_task` call), `tests/integration/test_attempt_not_result.py`, this handoff, manifest re-issue |
| status | **`DONE`** — B04/B17 is now a real assertion. **Zero xfails remain from this card.** |
| claim change | **none.** Still `CONTRACT_READY` / `SELF_VALIDATION`. |
| lease_released_at | 2026-09-08T01:12Z |

## C.1 The change

W4B closed `CR-TC-BACKFILL-02` by giving `PendingLedgerPort.record_pending` an optional
`connection` (`CR-TC-BACKFILL-02b`); both their implementations now accept it. `_fail_task`
passes its own:

```python
ctx.pending_ledger.record_pending(
    target_key=task.target_key, reason=reason, connection=connection
)
```

**Two regions of `service.py` changed, not one**, and the second is not optional: the
`PendingLedgerPort` Protocol in this file declares the signature being called, so passing a
keyword it did not admit fails `mypy --strict` before it fails anything else. The Protocol now
declares `connection: Connection | None = None` with a docstring saying why it is optional on
the wire and mandatory in practice here. Reporting this rather than quietly stretching "one
line": the packet named the call site, and the type declaration of that call site is part of
making the call correct.

The docstrings that described the old state were corrected in the same edit — `_fail_task` no
longer says the table "does not exist yet", and now says what passing the connection buys:
the pending row commits in the **same transaction** as the `failed` state that caused it, so
there is no window in which an item is marked failed with nothing in the ledger, and the port
cannot deadlock against the write lock the caller already holds.

## C.2 The test

`test_a_failed_item_is_recorded_in_the_pending_item_ledger` is no longer marked at all. It
drives the whole obligation and asserts it: two unknown outcomes exhaust
`analysis_attempts_per_item`, `auto_rerun_unknown_attempt` returns `failed`, the task row is
`failed`, and exactly one `pending_item_ledger` row exists with `state='pending'`,
`reason='analysis_unknown'`, the right `target_key`, and `first_pending_window_id` pointing at
the `coverage_window` taken from fixture `reporting/e`.

Worth recording because it is the reason this was cheap: the previous packet did not leave a
plain `xfail`. It left `xfail(strict=True, run=True, raises=OperationalError)` — the test ran,
and the failure mode was pinned to the *measured* deadlock. A bare `xfail` would have turned
green the moment W4B shipped the fix and told nobody; `strict` turned it into an XPASS the
coordinator could act on. The `busy_timeout_ms` knob in `_wire_real_ledger` is kept, with its
comment rewritten: nothing needs it today, and a future caller that forgets to pass a
connection deserves to find out in a fifth of a second rather than five.

## C.3 Hashes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/analysis/service.py` | MODIFY | `a95b78401683a077775c2333f07d375296a161b23bc19825fe94cec129ed3991` (83223 B) | `21d40f835bead5653b40c8cd68881df6b65e73e2252d75b2b081b676322e66a7` | 84252 |
| `tests/integration/test_attempt_not_result.py` | MODIFY | `6bb729cecde8cd525fd999a90320ed08114f395e10a20399f44ecb221526f1ba` (33753 B) | `edaa07b673b57dfe0c6b521ecf5056aea50acb90df365664edebddfd4d69d461` | 33727 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260908T010738Z.json` | CREATE | ABSENT | `0a150783080b0020527248087b68b26956bf6e3bba02bdc12a8fa72a0dba0e65` | 23937 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260908T004550Z.json` | MODIFY | `a9a6e088…` (24756 B) | `3600363210cdf869f3b58fe100e3a294becfc5fb20c01b0bf726482e4b0802b6` | 25442 |
| `evidence/handoffs/TC-analysis-once-per-generation-handoff.md` | MODIFY | — | (this file) | — |

`key.py`, `repository.py`, `router.py`, the migration, `tests/contract/test_analysis_key.py`
and `tests/integration/test_analysis_once_per_key.py` are **unchanged**. Nothing under
`contracts/`, `acceptance/`, `precode/` or `agent-tasks/` was touched. Evidence chain:
`EV-E1-01` → `EV-E1-02` → `EV-E1-03` (all `STALE`, each with a `stale_reason` naming its
packet) → **`EV-E1-04` (`PASS`)**; all four validate with **0 errors**.

## C.4 Verification

Card command, `2026-09-08T01:07:38Z` → `01:07:45Z`, **exit 0**, **35 tests: 35 passed, 0
xfailed, 0 failed** (was 34 passed + 1 xfail). Per file: 10 / 13 / 12.
**Full suite: `1028 passed, 6 xfailed, 0 failed`, exit 0** (123.9 s) — none of the six
remaining xfails belongs to this card. `ruff check`, `ruff format --check` and `mypy --strict`
(64 source files) all clean.

## C.5 CRs

`CR-TC-BACKFILL-02` is **closed** from this consumer's side and removed from the manifest's
`unresolved_issue_refs`; `CR-TC-BACKFILL-02b` is the fix that closed it.
`CR-TC-ANALYSIS-01`…`-08` stand unchanged. The "not established" list in the manifest loses
its pending-ledger entry: that obligation is now established.

---

*`PKT-TC-ANALYSIS-FIX3` · `worker-W3B` · `lease_released_at` 2026-09-08T01:12Z · claim
unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) — no item here is an independent audit.*

---

# ADDENDUM 4 — `PKT-TC-ANALYSIS-FIX4` (`CR-TC-adapter-10`: the task input carries the key)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ANALYSIS-FIX4` · lease `LEASE-TC-ANALYSIS-e5` (fencing 5) · `worker-W3B` |
| scope granted | `server/app/analysis/{service,router,repository}.py`, this card's tests, handoff, manifest re-issue |
| status | **`DONE`** — no STOP was required; the schema not only permits the field, it requires it. |
| claim change | **none.** `CONTRACT_READY` / `SELF_VALIDATION`. |
| lease_released_at | 2026-09-08T06:50Z |

## D.1 Schema check first — and it settled the question

The packet's STOP condition did not fire, for a stronger reason than "the schema permits it":

* `contracts/http/openapi.yaml` types the 200 of `/v1/analysis/tasks/{task_id}/input` as
  `GenericObject` — `type: object` with no `additionalProperties: false`, and its own
  description says the real shape belongs to another package and must arrive before G3.
* `contracts/ai/tasks.yaml` §2 is that package, and it lists **`analysis_key` in
  `input.required` for all three task types**, described as "Bảy thành phần §1".

So the field was never optional. Omitting it was a defect on this side, not a gap needing a
contract change, and `CR-TC-adapter-10` is a correct finding against this card. Nothing was
sent out-of-band and no new field was invented.

## D.2 What carried the key, and the one thing that had to be reworked

`analysis.get_task_input` now returns `analysis_key` with all seven ADR-0008 components,
computed by `analysis_key_for()`:

| component | source |
| --- | --- |
| `owner_id`, `target_key`, `task_type`, `generation_number` | the `analysis_generation` row — the durable record of the assignment |
| `source_fingerprint` | `derived_source_fingerprint()` over the sources the task-input port is about to hand the model — which is what `ENT-analysis.source_fingerprint` is *defined* to be |
| `prompt_version`, `schema_version` | the per-task-type constants of `contracts/ai/tasks.yaml` §2, quoted the way the retry budgets already are. They are configuration, not row data: that is why `ENT-analysis-generation.reason` has `prompt_version_change` and `schema_version_change` as reanalysis triggers |

The load-bearing part is that the key is now **one value in three places** — the enqueue
"already analysed?" lookup, the task input, and the committed row. Three spellings of it would
not have read as a bug; it would have read as the model being called again, which is REQ-AC06
failing silently. So `enqueue_tasks` derives the fingerprint too.

**The rework, reported because it matters.** The first version made a disagreeing
caller-supplied `source_fingerprint` a `VALIDATION_ERROR`. That is defensible in the abstract
and was wrong in practice: it broke **7 landed tests in W3A's `tests/integration/
test_worker_loop.py`**, whose fake task-input port does not hash to the fingerprint their
enqueue call passes. A design in which one card's test double can refuse another card's work
is a worse failure than the one it prevents. The field is now **advisory**: the derived value
always wins, and a disagreement is *reported* in the response entry as
`source_fingerprint_hint_ignored` — not obeyed, not silently dropped, and not fatal.
`CR-TC-ANALYSIS-10` proposes removing the field from the port entirely, which is the real fix.
W3A's suite is 18/18 green.

`router.py` and `repository.py` were in the lease and needed no change: the key is assembled
in the service and travels in the existing payload, so no route, no column and no SQL moved.

## D.3 `CR-TC-adapter-08`, recorded from this side

`contracts/ports.yaml` has no `analysis.release_task`, and this card did **not** invent one.
The consequence, stated as measured behaviour: when a worker refuses *before* calling the
provider — the credential is refused, or the adapter is `enabled: false` — it has no way to
hand the task back. The task sits `running` until `lease_ttl_analysis` (900 s) elapses and
`reap_expired_leases` returns it to `pending`. The worker is right not to call
`report_attempt_unknown` there: no inference ran, so `cost_uncertain = true` would be a claim
the system cannot support. So a task is parked for fifteen minutes by a refusal that was
instant and certain. This is a contract change request, not a code defect, and it is recorded
in the manifest's `unresolved_issue_refs`.

## D.4 Hashes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/analysis/service.py` | MODIFY | `21d40f835bead5653b40c8cd68881df6b65e73e2252d75b2b081b676322e66a7` (84252 B) | `6e07239edf68c2f669475491ba0709ca1ef448b63600c30e2701dab420413725` | 89567 |
| `tests/integration/test_analysis_once_per_key.py` | MODIFY | `35cf9c70…` (33739 B) | `30a87681f4cb6d757b39203a7c0dbb0ab573493184fa0f1542f2aec2bf454f96` | 41482 |
| `tests/integration/test_attempt_not_result.py` | MODIFY | `edaa07b6…` (33727 B) | `f76f26ff247471a2789853a36064f46fadf5d6cc349a4400ce102c3543ca29c1` | 34466 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260908T064438Z.json` | CREATE | ABSENT | `c288dd8ed7d162f3e102d3bf5deb2e6522a9109fe67b5f706086bedddb367ca5` | 27482 |
| `evidence/runs/TC-analysis-once-per-generation-E1-20260908T010738Z.json` | MODIFY | `0a150783…` (23937 B) | `afa090fd419aed135d8a62d8d550c89e7ebee1deba48a23ce988a0f2cc8b9325` | 24433 |
| `evidence/handoffs/TC-analysis-once-per-generation-handoff.md` | MODIFY | — | (this file) | — |

`router.py` (`e08ae84f…`), `repository.py` (`648ae9b4…`), `key.py`, the migration and
`tests/contract/test_analysis_key.py` (`70db817c…`) are **unchanged**. Nothing under
`contracts/`, `acceptance/`, `precode/`, `agent-tasks/` or `worker/` was touched. Evidence
chain `EV-E1-01`…`-04` are all `STALE` with reasons; **`EV-E1-05`** is `PASS`; all five
validate with 0 errors.

## D.5 Verification

Card command `2026-09-08T06:44:38Z` → `06:44:48Z`, exit 0: **36 tests, 36 passed, 0 xfailed,
0 failed** (10 / 15 / 11), up from 35. The new tests are the fingerprint/hint behaviour and
**`test_the_worker_loop_completes_a_whole_cycle_against_this_service`** — W3A's
`AnalysisWorkerLoop` driven over real HTTP against this card's router with
`analysis_key_resolver=None`, reaching `CycleOutcome.SUBMITTED` with one valid row and one
attempt, and the key the adapter received asserted to have all seven components.

Full suite: **1128 passed, 3 xfailed, 2 failed**, exit 1. Both failures are
`tests/integration/test_collector_loop.py` strict-XPASS on that card's own
`CR-TC-COLLECTOR-11`/`-12` — their pinned expectations flipped because someone else's fix
landed; nothing to do with analysis. `ruff check`, `ruff format --check` clean on this card's
three test files and `server/app/analysis/`; `mypy` reports 0 errors in `server/app/analysis`.
The tree currently carries ruff/mypy errors in `server/app/secret/`,
`server/app/settings_service/` and two other cards' test files — outside this lease.

---

*`PKT-TC-ANALYSIS-FIX4` · `worker-W3B` · `lease_released_at` 2026-09-08T06:50Z · claim
unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) — no item here is an independent audit.*

### D.6 `STALE_BASELINE` — reported, not worked around

An SG-HASH re-check run immediately before releasing this lease found **three of the card's
§0 pinned sources changed byte-for-byte while this packet was running**:
`contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/http/openapi.yaml`.

The diff was read rather than assumed. It is entirely inside the `data.purge_all` prose — the
purge keep-list grows to 22 tables with `maintenance_window`, and the entity total goes 60 →
61. Filtering all three diffs for `analysis` returns nothing: no `analysis.*` operation, no
`MOD-analysis-service` edge, no `/v1/analysis/**` route is touched. So the PASS above is
still true of the bytes it ran against, and nothing in this addendum's reasoning depends on
the changed text.

It is still a stop condition. SG-HASH reads **bytes, not intent** — that is the whole reason
the mechanism exists — so the card is `STALE` and owes a PC10 re-pin before the next packet.
This worker did not touch §0 and did not adjust the manifest's `contract_hashes` to match
disk: rewriting the recorded baseline to make a check pass is the defect the check is for.
The manifest records the drift in `limitations.not_checked_vi`; the Coordinator holds the
re-pin.
