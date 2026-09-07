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
