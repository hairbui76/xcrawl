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
