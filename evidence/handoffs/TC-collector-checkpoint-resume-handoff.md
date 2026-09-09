# HANDOFF — `TC-collector-checkpoint-resume`

| Field | Value |
| --- | --- |
| packet_id | `TC-collector-checkpoint-resume` (Phase 2A, M0 → M1) |
| worker principal | `worker-WC` |
| authority_id | `AUTH-COORD-TC-COLLECTOR` (parent `AUTH-OWNER-20260907-04`, record `…/scratchpad/packets/OWNER-DECISIONS-20260907-03.md`) |
| lease_id | `LEASE-TC-COLLECTOR-e1` (exclusive on card §3 write set + migration + handoff + evidence manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED (E1/E2)` for the collector-side scope of this card only. **No claim of any kind is made about the collector working against real X** — the card's ceiling forbids it and no probe has run. See §6 for the two write-set deviations and §7 for the CRs. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T14:05Z |

Status is `DONE_WITH_CONCERNS` rather than `DONE` for three reasons, none of which is a
failing test: the card's §3 has no row for the X source port the dispatch requires
(`CR-TC-COLLECTOR-02`); three of the six fixtures the dispatch names are not pinned in §0
(`CR-TC-COLLECTOR-03`); and the server side of `worker.*` does not exist, so half of the
challenge oracle is corroborated by a stub rather than proved (§5.2).

**The packet also stopped once and restarted.** It began at `SG-HASH`:
`contracts/data/entities.yaml` did not match the card's pin, and the first evidence record
(`EV-E1-01`, result `STALE`) documents that stop. Mid-packet the Coordinator re-pinned the
card to epoch `PC10-PIN-P2-20260907`; all 30 pinned files were re-verified (30/30 match) and
the work then proceeded. Both records are on disk; the second supersedes the first.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `collector/app/session.py` | CREATE | ABSENT | `d14d7e6f0357c567d4aff8e0d00a9f8341869fee3931412b77726f11199521c0` | 8472 |
| `collector/app/reader.py` | CREATE | ABSENT | `3f1b68a2790ba2e50cb557191e9f1aeb8bad51d3e625ba2aa2851162d80e1aec` | 28700 |
| `collector/app/batcher.py` | CREATE | ABSENT | `ad9f1833e85b0d382161d5dcfd0cd61d9c94f4efeff252fde63d8957b816cac0` | 11886 |
| `collector/app/client.py` | CREATE | ABSENT | `85efa3398b3c76fd52007c8e202d284e2268c55fa9c299d73d7521edb071c439` | 27444 |
| `collector/app/limits.py` | CREATE | ABSENT | `386b19cf6e8db8e52770db7578a5533287096d47039a74cac240755d3d813f14` | 6734 |
| `tests/contract/test_collector_stop_reasons.py` | CREATE | ABSENT | `2628c6e383d78217060a1543f7a10cce591a03fd829f46c45dbb856e4eec5f32` | 41477 |
| `tests/integration/test_collector_resume_after_challenge.py` | CREATE | ABSENT | `9348c18cea38400463d974df1b552a5752c0bb9a29c02d9edd7edb0ac5296595` | 37090 |
| `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T132623Z.json` | CREATE | ABSENT | `12437bbc0c18798bbb955417e69aadc637603c93825fd1dd8e1e9c7707005c27` | 11839 |
| `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json` | CREATE | ABSENT | `8320ffae6120921e10cde1c99e07621c15a69885e9f51d015bb4556e95b26edc` | 19118 |
| `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md` | CREATE | ABSENT | (this file) | — |

Exactly the seven paths of card §3, plus the two evidence records. **No Alembic migration**
— the collector owns no server state (card §4: "Collector **không** sở hữu state nào của
server"), so it needs no table. `server/app/main.py` was not touched; no router was
registered; nothing under `contracts/`, `acceptance/` or `precode/` was edited. No git
command that mutates the repo was run. `PYTHONDONTWRITEBYTECODE=1` throughout; scratch under
`…/scratchpad/wc/`.

Other modified and untracked paths visible in `git status` belong to cards running in
parallel (`TC-x-feasibility-probe`, `TC-research-connector-metadata`, the pin-epoch refresh
across `agent-tasks/`). None of them was written by this packet.

---

## 2. Source baselines

Re-verified against the card's §0 table at pin epoch **`PC10-PIN-P2-20260907`** immediately
before the first line of code and again before this handoff: **30 pinned files, 30 matching**,
byte counts included. The full observed map is in the manifest under
`baseline.contract_hashes`.

The first check, at 13:26Z, was against the previous epoch `PC10-PIN-P1d-20260907` and found
**29 of 30**: `contracts/data/entities.yaml` had moved from `df5e0231…` to `c61be0a4…`. That
was `SG-HASH`, and the packet stopped there. §3 records what the drift turned out to be.

---

## 3. The stop, and why it was a stop

`SG-HASH` is unconditional and the card's §0 forecloses the obvious objection in advance:
"quy tắc `STALE` đọc **byte**, không đọc ý định, và một ngoại lệ 'chỉ là văn xuôi' sẽ biến
cửa pin thành thứ phải phán đoán mới dùng được."

The drift was measured before reporting it, by loading both versions with PyYAML: 25 of 26
top-level keys were byte-identical after parse — including `entities`, `transactions`,
`limits` and `referential_integrity` — and the only difference was one amendment record,
`AMD-ENT-owner-01`, moving `PROVISIONAL` → `ACCEPTED` with `ratified_by: OD-20260907-03`. No
column of `ENT-run` or `ENT-worker-registration` changed, and those are the only two entities
this card's oracle touches.

So the drift was almost certainly harmless — and *proving the scope* is a different act from
*waiving the gate*. Only the second is outside a Worker's authority: renaming the pin epoch
belongs to the Coordinator (`F-A2R1-03`), and `agent_profile/worker.md` says drift is reported,
not judged. The Coordinator then re-pinned to `PC10-PIN-P2-20260907` with exactly that hash,
and the packet resumed against the refreshed card. `EV-E1-01` is kept as the record of the
stop; it is marked `STALE` by `EV-E1-02` because its finding was true at 13:26Z and is not
true now.

---

## 4. What was built

Five modules, each mapped to the role card §3 gives it.

**`limits.py`** — the segment budget. 200 posts / 1800 s from
`contracts/retry-policy.yaml`, `first_of_either` evaluation, `limit_kind` recorded, and a
non-empty `x_coverage_note_vi` produced by the same object that knows why the segment
stopped (T-RUN-02 forbids leaving it blank).

**`session.py`** — the Chrome profile rule (REQ-D09). A platform-default `user_data_dir` is
*refused* with `CAPABILITY_DENIED`, not warned about; the error carries only the directory's
name because the envelope forbids absolute personal-machine paths.
`embedding_supported` is a literal `False` with no way to override it (B12/D50), and
`x_session_state: unknown` is never promoted to `ok`. No Playwright import anywhere.

**`batcher.py`** — `payload_hash` = `sha256(JCS({schema_version, items,
client_checkpoint_proposal}))`, item projection, and a derived idempotency key. The key is
scoped `assignment_id + lease_epoch + batch_seq`; see §4.1.

**`client.py`** — the nine operations card §4 permits and no others. The ack-loss protocol is
structural: the only path back to a resend runs through `ingest.get_receipt`, so "gửi lại mà
chưa tra get_receipt" is absent by construction rather than by discipline. It also holds the
two stop-reason mapping tables and the `ErrorCode`-typed `ServerError`.

**`reader.py`** — the `XSource` port (one method), the parser, and `SegmentRunner`. The
runner has no claim loop: it collects, reports, and returns. That is the structural form of
I10 — there is no code path by which a challenge leads to another attempt.

### 4.1 Two design decisions worth the Coordinator's eye

**The batch idempotency key includes the lease epoch.** The first design keyed on
`assignment_id + batch_seq`, which is what the ports contract's idempotency scope implies.
The resume test then failed with a real `IDEMPOTENCY_CONFLICT`: the first batch of a resumed
segment reuses `batch_seq = 1` under the same assignment, so it collides with the first batch
of the segment it is resuming — same key, different contents — and the server correctly
refuses it, blocking a resume that ought to work. `contracts/retry-policy.yaml`
§`lease_epoch_rule` guarantees the epoch increments on every grant and is never reused, so
including it separates the segments while keeping the key derivable (which is what the
ack-loss path needs). This was found by a test, not by reading.

**Buffered items are discarded on a stop, except for a layout change.** `c-challenge-mid-batch`
is unambiguous — 7 posts downloaded, 0 rows — and §CP-03 says downloaded-but-not-ingested is
not a checkpoint. T-RUN-24 is equally explicit the other way: on a layout change "phần đã bóc
đủ trường VẪN COMMIT bình thường". The difference is that a layout change is a *successful*
request whose parsed items are sound, so the two cases are handled by different branches with
the contract cited at each.

---

## 5. Evidence

### EV-E1-02 — the card's two commands, E1 + E2

| Field | Value |
| --- | --- |
| id | `EV-E1-02-tc-collector-checkpoint-resume` |
| type | `SELF_VALIDATION`, level `E2` |
| manifest | `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json` (19118 bytes, sha256 `8320ffae6120921e10cde1c99e07621c15a69885e9f51d015bb4556e95b26edc`) |
| commands | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" -W ignore::DeprecationWarning tests/contract/test_collector_stop_reasons.py` and the same for `tests/integration/test_collector_resume_after_challenge.py` |
| started / ended | 2026-09-07T13:55:52Z / 2026-09-07T13:56:09Z |
| result | **`PASS`** — 55 tests, 55 passed, 0 failed, 0 xfailed, 0 skipped, exit code 0 (41 + 14) |

The manifest validates against `evidence/manifest.schema.json` with
`jsonschema 4.26.0 Draft202012Validator`: **0 errors**. `claim.supports_label` is deliberately
absent — the schema caps a `SELF_VALIDATION` record at `CONTRACT_READY`, so asserting the
card's `IMPLEMENTATION_VERIFIED` inside the record itself would be asserting something this
run cannot support. Raising the label is the Coordinator's or an Auditor's act.

Static gates: `ruff check` and `ruff format` clean on `collector/` and `tests/`;
`mypy --strict collector/app` → *Success: no issues found in 7 source files*. (`mypy` was run
with an explicit path: `pyproject.toml` scopes the strict gate to `server/app`, and that file
is outside this card's write set.)

Full suite: `571 passed, 1 failed, 4 xfailed`. The one failure is
`tests/integration/test_identity_merge_audit.py::test_migration_chain_resolves_to_a_single_head`,
which asserts the Alembic head is `0004_merge_phase1_heads` while the head is now
`0005_tc_research_connector_metadata` — a revision added by the concurrent
`TC-research-connector-metadata` card. **This packet created no migration**, so the failure is
neither caused nor fixable here (`CR-TC-COLLECTOR-07`).

### EV-E1-01 — the `SG-HASH` stop, now superseded

`evidence/runs/TC-collector-checkpoint-resume-E1-20260907T132623Z.json` (11839 bytes, sha256
`12437bbc0c18798bbb955417e69aadc637603c93825fd1dd8e1e9c7707005c27`), result `STALE`, 0 schema
errors. It records the 29/30 pin check against epoch `PC10-PIN-P1d-20260907` and the measured
scope of the drift. Kept rather than deleted: it is the evidence that the gate was honoured.

### 5.1 What the oracles actually measure

Row counts, source-read counts and hashes — not log lines. The **ingest half runs against the
real server**: `create_app()`, the real `server/app/ingest` service, and a SQLite database
built by `alembic upgrade head`. So "20 rows durable, 7 absent, checkpoint unmoved at 20" is a
`SELECT COUNT(*)` inside the real transaction, which is what
`c-challenge-mid-batch.durable_rows_expected` asks for.

Sixteen measured properties are listed in the manifest's `oracle.statement_vi`. The ones that
carry the card:

- **I02** — after a challenge mid-segment: `COUNT(post) = 20`, the 7 downloaded posts have no
  rows, and `MAX(checkpoint.acked_through_ingest_sequence) = 20` before and after.
- **I10** — `XSource.fetch_page` call count does not increase after the stop is reported;
  `worker.claim_assignment` is never called by the runner; `requires_owner_action` is true.
- **REQ-AC04** — two reports carry the same `stop_report_id`; the second answers
  `alert_intent_created: false`.
- **T-RUN-09** — the collector sends `challenge_required`; the run comes back `captcha`.
- **AMD-B05** — the resumed segment re-reads and the row count goes 20 → 30, not 40. The
  measurement is rows, which the fixture insists on: "request count KHÔNG phải oracle".
- **SG-RATE / T-RUN-25** — rate limiting yields `rate_limited`, a coverage note naming the
  moment, zero alerts, zero further reads, and never `blocked`.
- **T-RUN-24** — 12 of 40 parse: 12 rows commit, `SOURCE_LAYOUT_CHANGED` is reported with the
  missing field *names*, one alert.
- **E2 (T-RUN-19)** — a SQLite write fault injected through `server/app/db/faults.py`: 0 post
  rows, 0 receipts, checkpoint stays 0, no stop reported; then three spaced successful probes
  through the storage guard's own API and the batch commits normally.
- **SC49 / SG-DENY** — `CollectorClient` exposes exactly the nine permitted operations plus
  `close`; a `save`, `storage` or `analysis` method does not exist to be called.
- **Cross-implementation** — the collector's `payload_hash` equals the server's. The collector
  package may not import the server one (default deny, `SL-7`), so the two are independent
  implementations of one definition; the *test* imports both and asserts equality, which turns
  a silent production divergence into a failing assertion.

### 5.2 The boundary this evidence does not cross

`worker.claim_assignment` / `heartbeat` / `report_stop` / `release_assignment` have **no
server implementation** — they belong to `TC-scheduler-lease-claim`, which has not run. They
are served in the integration test by a `WorkerStub` replaying `contracts/http/openapi.yaml`
and the fixtures.

That matters for one oracle in particular. "Exactly one alert intent per run" is counted by
the stub applying the contract's idempotency rule, so what is *established* here is the
collector-side half — that the collector mints one `stop_report_id` per segment and reuses it
on every repeat. The server-side half is the scheduler card's to prove. The test says so in
its own docstring rather than only here.

---

## 6. Write-set deviations, declared

Two, both inside card §3's seven paths rather than adding to them.

1. **The X source port lives in `reader.py`, not in `collector/app/x_source.py`.** The
   dispatch asks for a `collector.app.x_source` protocol; card §3 authorises seven paths and
   says "Mọi file **không** nằm trong bảng này là read-only", and the Phase 1 dispatch
   template §2 says "Write set = card §3 exactly … Nothing else". Creating an eighth module
   would have resolved that conflict by ignoring the card, so the protocol (`XSource`), the
   page type (`FeedPage`) and the test double (`RecordedSource`) live in `reader.py` — the
   file the card describes as "đọc feed, phát hiện challenge / layout changed". The port is
   still narrow: one method, and nothing above it knows what a browser is.
   `CR-TC-COLLECTOR-02` asks for §3 to say which of the two it wants.
2. **`RecordedSource` ships in `reader.py` rather than in a test helper.** Both test files
   need it, `collector/tests/` is not in §3, and its read counter *is* the oracle for "no new
   collection request after the stop". It touches no browser, network or session.

---

## 7. Change requests

| ID | Addressed to | Request |
| --- | --- | --- |
| `CR-TC-COLLECTOR-01` | Coordinator | **Resolved during the packet.** Raised as blocking when `contracts/data/entities.yaml` broke the §0 pin in all 18 cards; the Coordinator re-pinned to epoch `PC10-PIN-P2-20260907`. Recorded because the sequence — Owner ratification edits a pinned contract, every card goes `STALE` — will recur at the next ratification round, and pinning against an uncommitted working tree is what makes it bite. |
| `CR-TC-COLLECTOR-02` | Coordinator + card owner (PC10) | Card §3 has no row for the X source port or its test double. Either add one (`collector/app/x_source.py`), or state that the protocol belongs in `reader.py` — which is where this packet put it. Also no row exists for `collector/tests/`. |
| `CR-TC-COLLECTOR-03` | Coordinator + card owner (PC10) | Fixture reconciliation. The dispatch asks for d/b/c/e/f/g; §0 pins a/b/c/e/h and §8's oracle names a/b/c/e. `d-duplicate-ingest-replay`, `f-two-workers-claim-same-assignment` and `g-schedule-due-claim` were used as instructed but are **neither pinned nor in the read set** — their observed hashes are recorded in the manifest's `inputs.fixtures` so the gap is visible. Pin them into §0 and add their oracles to §8, or drop them from the test list. |
| `CR-TC-COLLECTOR-04` | Coordinator | Card §2 asks that `precode/change-control.md` be checked against the table in `evidence/handoffs/PC10-handoff.md` (`baf10e03…`). That file has been amended repeatedly since and now hashes `21688b45…`. The instruction is unusable as written; point it at a maintained pin. |
| `CR-TC-COLLECTOR-05` | PC01 (`ports.yaml`) + PC03 (`errors.yaml`) | Two pinned contracts disagree. `contracts/ports.yaml` lists `STORAGE_WRITE_FAILED` among `worker.report_stop`'s `error_codes`; `contracts/errors.yaml` does not list `worker.report_stop` among that code's `operations`. Non-blocking — the collector maps `local_storage_unavailable` to no code, since the registry scopes `STORAGE_WRITE_FAILED` to the *server's* store and reusing it would tell an operator the database is in trouble when it is not. A test asserts the current asymmetry so it fails the day either file is corrected. |
| `CR-TC-COLLECTOR-06` | PC02 (`ingest-batch.schema.json`) | The `client_checkpoint_proposal.stop_hint` enum is `none` / `limit_reached` / `captcha` / `session_expired` / `source_blocked`. The two stop reasons added later — `source_layout_changed` (CR-PC05-01) and `rate_limited` (CR-PC10-02) — have no value, so the last batch before either stop can only hint `none`, losing the hint exactly where the run is about to end for a reason a person must act on. |
| `CR-TC-COLLECTOR-07` | Coordinator + `TC-research-connector-metadata` | `tests/integration/test_identity_merge_audit.py::test_migration_chain_resolves_to_a_single_head` fails: it pins the head to `0004_merge_phase1_heads` and the connector card added `0005_tc_research_connector_metadata`. Neither file is in this card's write set. The two cards need to agree on who updates that assertion. |

No contract, fixture, schema or expectation was edited, and no oracle was adjusted to make
anything pass. The two failures this packet did hit were fixed in the collector's own code
(the author projection and the epoch-scoped idempotency key), not in the contracts that
caught them.

---

## 8. Card checklist

| Card item | Status | Where |
| --- | --- | --- |
| §0 baseline pin re-verified before writing code | **DONE** | 29/30 at epoch P1d (stop), 30/30 at epoch P2 (proceed); manifest `baseline.contract_hashes` |
| §2 read set | **PARTIAL** | Read in full or in the sections the work needed: `contracts/ports.yaml` (the nine operations), `contracts/state/run.yaml` (enums, checkpoint_model CP-01..CP-08, transitions T-RUN-01/02/09/10/14/16/17b/19/24/25, lease budgets), `contracts/errors.yaml` (envelope + the eight codes used), `contracts/retry-policy.yaml` (budgets), the three wire schemas, `contracts/ops/collector-probe.md` §4 and §8, `contracts/http/openapi.yaml` (the collector's routes), and the six collection fixtures. **Not** read in full: `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/data/entities.yaml` (parsed structurally, not read), the three ADRs, `precode/README.md`, `precode/change-control.md`. All 30 were hashed. |
| §3 `collector/app/session.py` | **DONE** | D09 profile guard, capabilities, registration payload |
| §3 `collector/app/reader.py` | **DONE** | `XSource` port, parser, `SegmentRunner`; deviation declared in §6 |
| §3 `collector/app/batcher.py` | **DONE** | `payload_hash`, idempotency key, item shaping |
| §3 `collector/app/client.py` | **DONE** | nine operations, ack-loss protocol, stop-reason tables |
| §3 `collector/app/limits.py` | **DONE** | 200/1800, `first_of_either`, coverage note |
| §8 `tests/contract/test_collector_stop_reasons.py` | **DONE** | 41 tests, all passing |
| §8 `tests/integration/test_collector_resume_after_challenge.py` | **DONE** | 14 tests, all passing (12 E1 + 2 E2) |
| §8 live probe | **NOT_RUN** | belongs to `TC-x-feasibility-probe`; `SG-01`/`SG-02` unchanged |
| §13 evidence manifest, validated | **DONE** | `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json`, 0 schema errors |
| §13 registration in `evidence/index.json` | **NOT_DONE** | PC09's file, outside this write set |
| Alembic migration | **NOT_APPLICABLE** | the collector owns no server state (card §4) |

---

## 9. Unresolved refs and stop gates still standing

- `SG-HASH` — fired once at epoch P1d; cleared after the Coordinator's re-pin. §3.
- `SG-01`, `SG-02` — **unchanged and untouched**. `contracts/ops/collector-probe.md` §0 still
  records the probe as `NOT_RUN` and §6 items 2–4 are still unanswered by the Owner
  (`OD-20260907-03` says so). Nothing in this packet opened a browser, imported Playwright,
  reached the network, or asserts anything about X's real behaviour. There is no code that
  interacts with a verification page, rotates an account, changes a user-agent, or retries
  after a challenge — and `test_the_collector_never_writes_the_database_directly` plus the
  client-surface test assert two of those structurally.
- `SG-STACK` — no framework choice was needed beyond what ADR-0011 already names (`httpx`,
  `pytest`); Playwright stays declared-but-unused, as the Phase 0 skeleton left it.
- `SG-PC09` — `acceptance/scenarios.yaml` was **not** read, so the §8-versus-scenarios
  comparison the gate requires has not been made. It was not reached before the work began
  and is still owed; nothing observed here contradicts card §8, but that is an absence of
  evidence, not evidence of absence.
- `SG-RATE` — honoured and tested: `rate_limited` is `partial`, never `blocked`, with the
  coverage note naming `rate_limited_at` and zero in-run retries.
- PROVISIONAL parameters introduced: `LAYOUT_CHANGE_PARSE_FAILURE_TOLERANCE = 0`. Derived
  from T-RUN-24's prohibitions (no guessing, no hollow ingest, no silent drop) rather than
  from a measurement, because there is no measurement — the probe is `NOT_RUN`. A non-zero
  tolerance would be a tuning decision needing real data.

**Lease released at 2026-09-07T14:05Z.** No further writes.

---

# ADDENDUM — `PKT-TC-COLLECTOR-FIX2` (wave 2, gap G-7a)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-COLLECTOR-FIX2` |
| worker principal | `worker-WC` |
| lease_id | `LEASE-TC-COLLECTOR-e3` (`collector/app/main.py`, NEW `collector/app/loop.py`, this card's tests + NEW `tests/integration/test_collector_loop.py`, handoff, manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED (E1)` for the collector process loop against the **real** `jobs` and `ingest` routers. Still no claim about live X: there is no source driver, and `--run` refuses rather than pretend. |
| next actor | Coordinator |
| lease_released_at | 2026-09-08T06:35Z |

`DONE_WITH_CONCERNS` because building the loop against the real server surfaced **four
defects in code this card may not write** — one of which stops the Owner ever being told a
run needs them (`CR-TC-COLLECTOR-11`). Three are pinned by tests that fail the day they are
fixed.

The session was killed by a rate limit mid-packet and resumed; `main.py` and `loop.py` were
already complete on disk, and the test file's harness was rewritten afterwards to use
`server/app/wiring.py`, which had landed in the meantime.

## A1. Changes

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `collector/app/loop.py` | CREATE | ABSENT | `11d434618be3b7ba2ccdd1656942352b4cf640db7d88dc95f198eb30119256eb` | 19945 |
| `collector/app/main.py` | MODIFY (whole file) | `addef73dfcd10d43e3c5879dedad3414713c032cdea59c55e25cf49361c59651` (2715) | `86c85771aac71a93b65a3976d4ae1fc1c0d2783841b741486d0664652b7539a2` | 6897 |
| `tests/integration/test_collector_loop.py` | CREATE | ABSENT | `a1e13c5d910e95385a9d632f95d3eb8d0572399dba3cee25f69809cd6b133a77` | 36140 |
| `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` | CREATE | ABSENT | `5a3ad322610c18047c18959f3eb29c598e05841ec8dd8694ac82e9bfd87d0109` | 15519 |

The five modules and two test files of the original card are **unchanged**. No file outside
the lease was touched: `server/`, `contracts/`, `acceptance/`, `docs/` are all untouched.

## A2. What the loop does

`collector/app/loop.py` — `load_config` (env → `CollectorConfig`, every failure naming its
reason), and `CollectorLoop`: `register` → `claim` → `SegmentRunner` → `release`, with
`run_forever` returning a typed `LoopExit`.

Three refusals give it its shape, and each is measured in §A3:

1. **It will not claim work it cannot do.** A collector whose session is `challenge`,
   `expired` or `unknown`, or whose profile is not ready, exits `SESSION_NEEDS_OWNER` without
   a single claim. `requires_x_session_ok` is `const: true`, so asking would be asking for
   work it knows it cannot do.
2. **It will not resume a run waiting for a person.** After a challenge the loop stops. I10
   forbids the worker resuming itself; only `run.resume` in the app moves the run (T-RUN-10).
3. **It will not treat "nothing to do" as failure.** `no_work` is a 200; the loop waits the
   server's own `retry_after_ms` (`claim_idle_backoff`), not a number it chose (I13).

`collector/app/main.py` — real entry point with three explicit modes and no default action.
Verified by hand, not only by tests:

| Command | Observed |
| --- | --- |
| no arguments | usage error, exit **2** |
| `--print-registration` | the Phase-0 payload, exit **0** (`collector/tests/test_smoke.py` still passes untouched) |
| `--check-config` with nothing set | `{"status":"refused_to_start","reason":"missing_server_url",…}`, exit **3** |
| `--check-config` with a `0644` token file | `reason: token_file_permissions_too_open`, exit **3** (`contracts/ops/secrets.md` §3: refuse, because a silent warning is useless) |
| `--run`, fully configured | `reason: no_x_source_driver`, config echoed with `"token": "<redacted>"`, exit **4** |

Config comes from `RR_SERVER_URL`, `RR_COLLECTOR_TOKEN_FILE` (preferred — the `0600` file
`secrets.md` §3 describes) or `RR_COLLECTOR_TOKEN`, `RR_CHROME_PROFILE_DIR`, and optional
`RR_COLLECTOR_WORKER_ID`. The machine's default Chrome profile is refused at load time
(REQ-D09), so a misconfiguration cannot reach the browser layer at all.

`--run` refusing is the honest state of gap G-7a: the loop exists and is tested, and the
thing it still lacks is a live source driver, which is `TC-x-feasibility-probe`'s behind SP1.
A collector that started and collected nothing would look like "no new research" — exactly the
confusion I13 forbids.

## A3. Evidence

`tests/integration/test_collector_loop.py` — **13 passed, 2 xfailed (strict)**, exit 0:

```
PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" \
  -W ignore::DeprecationWarning tests/integration/test_collector_loop.py
```

The harness is the **real composition root**: `server/app/wiring.upgrade_database` +
`wiring.wire(app, settings)`, a real `Settings` (collector token configured as a digest via
the shipped `hash_bearer_token`), the real `jobs` and `ingest` routers, and a real SQLite
database at `alembic head`. Only three things are adjusted, each for a stated reason: a fake
clock and deterministic ids on `job_context`, and the two objects the composition root does
not build (`CR-TC-COLLECTOR-09`, `-10`). The X source is a `RecordedSource`; the collector
object under test is the production `CollectorClient` and `CollectorLoop`.

Measured on rows the real services wrote:

- **A full cycle** — registration grants no lease (`assignment_lease` stays empty, LM-01);
  after the cycle `post` = 20, `MAX(checkpoint.acked_through_ingest_sequence)` = 20,
  `ingest_receipt` ≥ 1, `run.status` = `running`, lease `released`, and
  `run.current_lease_epoch` = 2 (LM-06's bump lands on the run, not on the retired lease row).
- **A challenge cycle** — `post` = 20 and the 7 downloaded posts have **no rows**; the
  checkpoint does not move; the *server* sets `run.status = needs_user` and
  `run.stop_reason = captcha` from the collector's `challenge_required` (T-RUN-09).
- **No self-resume** — `run_forever(max_cycles=5)` uses one cycle, exits
  `SESSION_NEEDS_OWNER`, and the source read count stops at 3.
- **No claim with a bad session** — starting in `challenge`, zero cycles run and
  `assignment_lease` is never written.
- **A limit stop** — `stop_reason = limit_reached` with no error code (AMD-B02), a non-empty
  coverage note, the lease released, and the run still `running`.
- **Resume from the server's checkpoint** — after `run.resume`, the second cycle re-reads 7
  known posts and adds only the 3 new ones (row count 20 → 30, not 40; AMD-B05).
- **A late repeat report** — once the lease is handed back, a further `report_stop` is
  refused `STALE_LEASE` and nothing changes.
- **Idle** — `no_work` twice, positive sleeps from the server's `retry_after_ms`, zero source
  reads.
- **Config** — five named refusals, the `0600` rule, and a redacted summary with no token.

Evidence manifest: `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json`
(`EV-E1-03`, level E1, result `PASS`, validates against `evidence/manifest.schema.json` with
0 errors). It supplements `EV-E1-02` rather than superseding it: that record measured the
modules, this one measures the process against the real server.

Gates, this card's files: `ruff check` clean, `ruff format --check` clean (12 files), `mypy`
clean on `collector/app` (8 source files) — and `collector/app` is now inside the strict gate,
since `pyproject.toml` `files` lists it. Repo-wide the same three gates were clean when this
work began and are now red on files another card landed meanwhile; see `CR-TC-COLLECTOR-13`.

Full suite, final: **1088 passed, 5 xfailed, 0 failed** (187 s). Three of those xfails were
already in the tree; the two added here are the `CR-TC-COLLECTOR-11` and `-12` pins, both
`strict=True`, so each turns into a failure the moment the defect it describes is fixed. The
`test_migration_chain_resolves_to_a_single_head` failure reported in the first handoff is
gone — another card fixed it, so `CR-TC-COLLECTOR-07` is closed.

## A4. Change requests — four defects found by wiring this up

| ID | To | Finding |
| --- | --- | --- |
| `CR-TC-COLLECTOR-11` | WS (`wiring.py`) + W6A (`jobs/service.py`) | **Blocking for the Owner's first challenge.** `jobs.report_stop` calls `alert_port.create_alert_intent` from *inside* its open `session_scope`; `wiring._AlertIntentAdapter` calls `delivery.create_intent` **without** passing that connection, so SQLite refuses the nested writer — observed: `database is locked` on the `INSERT INTO outbox_intent`. A port that instead returns an id *without* writing fails the other way: `run.alert_intent_id` is `REFERENCES outbox_intent (id)`, so the follow-up `UPDATE run` fails the foreign key. **The alert path therefore cannot succeed in any wiring**, and on a real deployment the first challenge raises inside `report_stop` — the run never reaches `needs_user` and the Owner is never told. `delivery.create_intent` already accepts `connection=` for exactly this ("the outbox pattern"); the fix is to thread the caller's connection through `AlertIntentPort`. Pinned by `test_the_wired_alert_adapter_cannot_create_an_alert_today` (strict xfail). |
| `CR-TC-COLLECTOR-12` | W6A (`jobs/service.py`) | The claim response does **not** validate against `worker-assignment.schema.json`, which `contracts/ports.yaml` names as its response schema — 7 violations, checked against the live response: `x_coverage_note_vi` missing (required; it is the AMD-B05 sentence that stops "completed" being read as "all of X"), `search_config.source_limits` is `{}` where five `const` fields are required, and `tag_config_version_id` is `null` where a ULID is declared. `source_limits` is the block `collector-probe.md` §8 says exists "để collector không phải suy diễn", so an empty one silently withdraws SL-1…SL-6 from the wire. Also absent: `job_id` — the collector needs one for `ingest-batch.schema.json` and now infers `assignment_id`, which is correct (the jobs service sets `assignment_lease.job_id` to it) but undeclared. Pinned by `test_the_claim_response_validates_against_its_own_schema` (strict xfail). |
| `CR-TC-COLLECTOR-09` | WS (`wiring.py`) | The composition root builds `IngestContext` with **no `assignment` port**, so ingest cannot resolve a lease and a wired deployment cannot validate `lease_epoch` on any batch. The test supplies a 20-line `LeaseReader` over `assignment_lease`; production needs the same object, in `wiring.py`. |
| `CR-TC-COLLECTOR-10` | WS (`wiring.py`) | The composition root never sets `app.state.collector_token`, which is what `server/app/ingest/router.py` reads. `RR_COLLECTOR_TOKEN_SHA256` configures `token_registry`, which covers only the `jobs` routes — so a correctly configured deployment answers **401 to every collector ingest call**. Either set the attribute from settings, or move the ingest router onto the registry (preferable: one authentication path, not two). |
| `CR-TC-COLLECTOR-08` | WS2 (`docs/owner-runbook.md`) | §4.4 documents the collector as a Phase-0 stub whose only mode is `--print-registration` and describes gap G-7. That is now stale: `--check-config` and `--run` exist, no-argument exit is still `2` but with a different message, and G-7a is closed except for the source driver. `docs/` is outside this lease. |
| `CR-TC-COLLECTOR-13` | WAI (`TC-secret-settings-service`) + Coordinator | Informational, and **not caused by this packet**: the repo-wide style gates are red on files that landed while this packet ran. `ruff format --check` would reformat `server/app/secret/{repository,service,store}.py`; `ruff check` flags `tests/integration/test_analysis_once_per_key.py`; `mypy` reports 16 errors across `server/app/secret/{router,store}.py` and `server/app/settings_service/{router,service}.py`. The full suite still passes, so these are style/type gates rather than behaviour. Verified clean in isolation for this card's files: `ruff check`, `ruff format --check` and `mypy` are all clean on `collector/` and `tests/integration/test_collector_loop.py`. |
| `CR-TC-COLLECTOR-07` | — | **Closed.** The single-head migration test passes again. |

`CR-TC-COLLECTOR-02`, `-03`, `-04`, `-05`, `-06` from the first handoff are unchanged and
still open.

## A5. Checklist

| Item | Status |
| --- | --- |
| `collector/app/loop.py` — register/claim/heartbeat/collect/ingest/checkpoint/stop/release | **DONE** |
| every `limits.py` stop reason mapped to `report_stop` | **DONE** (`WireStopReason` table; limit, rate-limit, challenge, layout, blocked all exercised) |
| config via env, refusal with a named reason | **DONE** (five reasons + the `0600` rule) |
| in-process harness composing the real app | **DONE** — via `server/app/wiring.py`, which had landed |
| fake X source, fake clock, no browser/network | **DONE** |
| one full cycle + one challenge cycle against real server state | **DONE** (`assignment_lease`, `run`, `checkpoint`, `post`) |
| heartbeat on the contract interval | **PARTIAL** — the interval is read from `assignment.lease.heartbeat_interval_s` and the beat fires from the monotonic clock (covered in the earlier packet's stale-lease test); the loop tests use a frozen clock, so no beat fires in them. A timed-heartbeat test over the real jobs router is not written. |
| full suite, ruff/format/mypy | **DONE** |
| handoff addendum + manifest | **DONE** |

## A6. Stop gates

`SG-01`/`SG-02` unchanged: no browser, no Playwright import, no network, no X session, and
`--run` refuses precisely because the probe gate is still shut. `SG-PC09` remains **not
discharged** — `acceptance/scenarios.yaml` has still not been compared against card §8.

**Lease released at 2026-09-08T06:35Z.**

---

# ADDENDUM — `PKT-TC-COLLECTOR-FIX3` (flip the two pins)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-COLLECTOR-FIX3` · lease `LEASE-TC-COLLECTOR-e4` (`tests/integration/test_collector_loop.py`, handoff, manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| gate | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` carries a released `PKT-TC-SCHED-FIX1` addendum (`lease_released_at` 2026-09-08T06:55Z). Gate open; work proceeded. |
| next actor | Coordinator |
| lease_released_at | 2026-09-09T07:25Z |

## D1. Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `tests/integration/test_collector_loop.py` | MODIFY | `309f666c46792679291c50c04afb047cecc46b0382efb84254d08fb1f86a9bee` | 38189 |
| `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T071605Z.json` | CREATE | `d928570c8825b2f2aecca8a3434b7b46fab67af43973029491f34511ae40698b` | 14171 |

No source file was touched. `collector/app/{loop,main}.py` are unchanged from `FIX2`.

## D2. Three workarounds deleted, not adjusted

`P0-FIX5` made the composition root complete, so the harness now uses it and nothing else.
The `LeaseReader` adapter this card carried is **deleted**; the manual
`app.state.collector_token` assignment is **deleted**; `alert_port=None` is **deleted**. In
their place the fixture asserts the wiring did each job:

```python
assert application.state.ingest_context.assignment is not None   # CR-TC-COLLECTOR-09
assert application.state.collector_token == COLLECTOR_TOKEN      # CR-TC-COLLECTOR-10
```

The only thing still adjusted after `wire()` is determinism — a fake clock and deterministic
ids on `job_context` — because lease expiry and catch-up are statements about time.

**`CR-TC-COLLECTOR-09`, `-10`, `-11`, `-12` are closed.**

## D3. The two pins, flipped

**`CR-TC-COLLECTOR-12` → a passing assertion.** `test_the_claim_response_validates_against_
its_own_schema` validates the **live** claim body against `worker-assignment.schema.json`
and finds zero errors, where it previously found seven. `SCHED-FIX1`'s own note is worth
repeating: this card's contract test was green throughout, because it validated payloads it
built itself. The live-body check is what caught it.

**`CR-TC-COLLECTOR-11` → a passing assertion, split from what remains.** The deadlock is
genuinely gone, and `test_the_alert_intent_lands_in_the_callers_transaction` now asserts the
outcome. It wraps the **wired** adapter in a `RecordingAlertPort` that delegates every call,
so production code is what runs; the wrapper exists only to make the one previously
unobservable thing observable — that `report_stop` passes its open transaction down. Three
measurements: the port is handed a live connection, the call completes rather than
deadlocking, and exactly one `telegram_alert` intent exists afterwards.

## D4. `CR-TC-COLLECTOR-15` — the residual, and it is one line

The intent row lands; the run never points at it. **This is not two cards disagreeing about
a key name.** It is one expression in one file, and the read side is correct:

| Side | Location | What it does |
| --- | --- | --- |
| producer | `server/app/delivery/service.py` **623, 645, 670** | returns `{"intent_id": …, "delivery_id": …, "state": …, "created": …}` — the key is **`intent_id`** |
| consumer | `server/app/wiring.py` **198** | reads `result.get("delivery_intent_id") or result.get("id")` — **neither key exists**, so line 199 returns `None` |
| reader | `server/app/jobs/service.py` **1236–1246** | **correct**: takes the port's return value and skips `UPDATE run SET alert_intent_id` when it is `None` |

Key sets checked mechanically, not by eye: producer keys are
`{created, delivery_id, intent_id, state}`; the adapter reads `{delivery_intent_id, id}`;
**intersection empty**. Note `delivery_id` *is* present and is the trap — it is the delivery
row's id, not the intent's, so the fix is `intent_id` and not the nearest-looking neighbour.

**Fix (WS, one line):** `server/app/wiring.py:198` → `intent_id = result.get("intent_id")`.

Two operator-visible consequences until then. `run.alert_intent_id` stays NULL, so nothing
can navigate from a run to the alert it raised. And `report_stop`'s `alert_created` flag —
the field that says "the Owner has been told" — reports `False` on a report that did create
an alert. `REQ-AC04` survives by luck rather than design: the guard is
`run["alert_intent_id"] is None`, so a second report calls the port again, and only
`create_intent`'s own idempotency plus `ux_outbox_alert_per_run` prevent a duplicate row.

Pinned by `test_the_run_points_at_the_alert_intent_it_caused`, `strict=True, run=True`, with
that file:line detail in the marker's `reason` so the next reader does not have to re-derive
it.

## D5. A leak of my own, found by the full suite

The full suite failed once on
`tests/integration/test_unknown_chat_silent.py::test_over_the_rate_limit_the_code_is_not_
even_looked_up` — a telegram test this packet does not touch. It was mine anyway.

Attributed rather than guessed at: the test passes alone; it passes with this file; the whole
`tests/integration` directory passes **with** this file; and the full suite passes with
`--ignore` on this file (1128 passed) but fails with it (1 failed). That pattern is not a
logical interaction, it is exhaustion — and the cause was in the `app` fixture. Every test
here builds an entire runtime through `wire()`, each runtime holds a SQLAlchemy pool, and the
fixture returned the app without ever disposing the engine. Sixteen leaked pools were enough,
once the contract tests had run first, to push an unrelated test over a file-handle limit.

Fixed by making `app` a generator fixture that disposes `runtime.engine` on teardown. A
fixture that builds a composition root has to take it down again. Full suite after the fix:
**1143 passed, 4 xfailed, 0 failed**.

## D5b. Evidence

`tests/integration/test_collector_loop.py`: **15 passed, 1 xfailed**, exit 0.
All three of this card's test files together: **70 passed, 1 xfailed**.
Full suite: **1143 passed, 4 xfailed, 0 failed** (171 s).

```
PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" \
  -W ignore::DeprecationWarning tests/integration/test_collector_loop.py
```

Gates on this card's files: `ruff check` clean, `ruff format --check` clean, `mypy` clean on
`collector/app` (8 source files).

Manifest: `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T071605Z.json`
(`EV-E1-04`). It supplements `EV-E1-03`; that record's two `xfail` rows are now superseded —
one closed by assertion, one narrowed to `CR-TC-COLLECTOR-15`.

## D6. Baseline drift — `SG-HASH`, reported not judged

The card is at epoch `PC10-PIN-P5-20260908` and **3 of its 30 pinned files no longer match**:

| Path | Pinned | Observed |
| --- | --- | --- |
| `contracts/modules.yaml` | `cf536acb…` (108721) | `7a4e19bd…` (108912) |
| `contracts/ports.yaml` | `c15b676b…` (128850) | `c7c77340…` (128872) |
| `contracts/ops/secrets.md` | `14b3d898…` (25301) | `22f7a007…` (25323) |

The drift is from wave-2 work landing (`MOD-secret-service` / `MOD-settings-service` add
operations, module edges and a secrets section) — it was not caused by this packet, and this
packet wrote no contract. The pin was clean at `PC10-PIN-P4b-20260908` when the work began.

It did not silently invalidate an oracle: `contracts/ports.yaml` is read as an oracle by
`tests/contract/test_collector_stop_reasons.py`, which still passes, and the other two are
not read by any test of this card. That is an observation, not a waiver — re-pinning is the
Coordinator's (`F-A2R1-03`), and this addendum reports the drift rather than deciding it is
harmless.

**Lease released at 2026-09-09T07:25Z.**

---

# ADDENDUM — `PKT-TC-COLLECTOR-FIX4` (gate 1: `CR-TC-COLLECTOR-15` closed)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-COLLECTOR-FIX4` · lease `LEASE-TC-COLLECTOR-e5` |
| gate | `evidence/handoffs/P0-skeleton-handoff.md` §`PKT-P0-FIX7`, `worker-WS`, `lease_released_at` 2026-09-09T08:05Z. Verified present before any edit. |
| status | `DONE` |

WS's one-line fix landed (`server/app/wiring.py` now reads `result["intent_id"]`, and raises
rather than degrading to `None` if that key ever disappears — the better shape, because
absorbing a changed return is how the defect survived its first review). The strict pin
XPASSed, so it became the assertion it was standing in for.

`test_the_run_points_at_the_alert_intent_it_caused` now asserts two things:

- `run.alert_intent_id` names the `outbox_intent` row. Since that column is
  `REFERENCES outbox_intent (id)` and `foreign_keys` is ON, the UPDATE could not have
  committed unless the intent was already present in the same transaction — so "one commit"
  is measured rather than argued.
- the `report_stop` response reports `alert_intent_created: True`, read from the wire.

**One correction for the record.** `PKT-P0-FIX7`'s own note credits this finding as
`CR-TC-COLLECTOR-13`. It is **`-15`**; `-13` is the repo-gates item from `FIX2`.

---

# ADDENDUM — `PKT-TC-COLLECTOR-FIX4` (gate 2: `CR-TC-COLLECTOR-16` and `CR-TC-SCHED-08`)

| Field | Value |
| --- | --- |
| gate | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` §`PKT-TC-SCHED-FIX2`, `worker-W6A`, `lease_released_at` 2026-09-09T07:48Z |
| lease | extended to `collector/app/client.py` for the error-path expression only |
| status | **`DONE`** |

## F1. What was wrong, on both sides

`worker.report_stop`'s response was disputed three ways: the pinned fixture
`collection/c-challenge-mid-batch.json` said `{run{status, phase, outcome, stop_reason},
alert_intent_created, alert_intent_id}`; the service answered `{run_status, stop_reason,
alert_created}`; and this client parsed the fixture. The ruling made the fixture canonical
(`contracts/http/openapi.yaml` types the body as a `GenericObject`, so the fixtures are the
only concrete shape there is), `PKT-TC-SCHED-FIX2` moved the service onto it, and the three
now agree.

`CR-TC-SCHED-08` was the mirror-image defect **in this card's client**, and W6A was right to
raise it. `client.py` read `run` and `alert_intent_created` out of `error.details_safe` on the
409 echo path. Two things wrong with that, and the second is the one that matters:
`contracts/errors.yaml` closes `details_safe` to each code's own `details_safe_keys`, and
`run` is not among them for any code — so it was a contract violation, not merely a wrong
lookup. `a-feed-layout-changed` puts the three fields *beside* `error`, and that is where
they are now read from.

The fix is three small edits serving one expression: `ServerError` carries the whole response
body (an error response can have siblings of `error`, and the envelope alone cannot see
them), `_raise_for_envelope` passes it, and the `report_stop` except-branch reads
`error.body`. `alert_intent_id` is now returned on that path too — it was hard-coded `None`.

## F2. Why the earlier tests did not catch it

They asserted on database rows. That was the right call while the shapes disagreed and the
wrong one afterwards: a `StopAck` whose three fields were all empty passes every row-count
assertion ever written, and a collector process that cannot tell whether the Owner was
alerted is precisely the failure worth catching. The two new tests therefore assert the
**typed object against the wire body**, field by field:

- `test_stop_ack_carries_the_servers_answer_on_a_200` — `ack.run == body["run"]`,
  `status = needs_user`, `stop_reason = captcha` (the stored spelling, T-RUN-09),
  `alert_intent_created is True`, and `ack.alert_intent_id` equals both the body's and the id
  on `run`.
- `test_stop_ack_carries_the_servers_answer_on_a_409` — the layout-changed echo. Asserts the
  three fields are siblings of `error`, that `details_safe` does **not** carry `run`, that
  `ack.echoed_code` is `SOURCE_LAYOUT_CHANGED`, and that the run really landed there (12 of
  40 posts, one alert, `blocked`).

## F3. Evidence

`tests/integration/test_collector_loop.py`: **18 passed, 0 xfailed** — the file now carries
no pins at all, which is the point: `CR-TC-COLLECTOR-09, -10, -11, -12, -15, -16` and
`CR-TC-SCHED-08` are all closed by assertion.

| Path | Operation | sha256 | Bytes |
| --- | --- | --- | --- |
| `tests/integration/test_collector_loop.py` | MODIFY | `0fc21b5230206c26d125cf1cabb2adaf0dd04af3d69ddb5d9270b6a3248fa94c` | 43115 |
| `collector/app/client.py` | MODIFY (error-path expression) | `49d48ac1cd504051b593900fca00ac2a3003e3bfe4b58774aea049228dfa01b2` | 28549 |
| `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T074631Z.json` | CREATE | `0a7b90ea0c79974fd70d6c2778f563878abaafdd816e24171c99b151e8d6dab3` | 12806 |

Full suite: **1161 passed, 3 xfailed, 0 failed** (182 s) — the three remaining xfails belong
to other cards. Gates on this card's files: `ruff check`, `ruff format --check` and `mypy`
all clean. Baseline: pin epoch `PC10-PIN-P5c-20260909`, **30/30 match** — the drift reported
in `FIX3` §D6 has been re-pinned by the Coordinator.

Manifest `EV-E1-05` supersedes `EV-E1-04`: both of that record's strict xfails are now
assertions.

**Lease released at 2026-09-09T10:05Z.**
