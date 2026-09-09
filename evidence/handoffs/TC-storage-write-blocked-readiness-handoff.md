# HANDOFF — `TC-storage-write-blocked-readiness`

| Field | Value |
| --- | --- |
| packet_id | `TC-storage-write-blocked-readiness` (Phase 1, M1) |
| worker principal | `worker-WR` |
| authority_id | `AUTH-COORD-TC-STORAGE` (parent `AUTH-OWNER-20260907-03`, record `OD-20260907-02`) |
| lease_id | `LEASE-TC-STORAGE-e1` (exclusive on card §3 write set + migration + handoff + evidence manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED` for this card's scope — but see `CR-TC-storage-02`: the evidence schema caps a `SELF_VALIDATION` record at `CONTRACT_READY`, so the manifest itself asserts `DRAFT_FOR_REVIEW`. Raising the label needs independent review. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T10:15Z |

Status is `DONE_WITH_CONCERNS` rather than `DONE` for one reason: routing
`health.get_readiness` — which this card exists to do — makes the Phase 0 tripwire
`server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` fail. That test lives
in a file this card may not write. It fired exactly as its own docstring says it should, and
retiring it belongs to the owner of that file (`CR-TC-storage-01`).

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/storage/__init__.py` | CREATE | ABSENT | `539e2d15ad3b7ce50be07bfa167ed1e5495edf1a7833b3d0e214dc16fe73f2bb` | 1195 |
| `server/app/storage/health.py` | CREATE | ABSENT | `3d72bf1558e63a1bfde107ab757f5f6773d2415fce7e9b2269448ed2798a06f2` | 19460 |
| `server/app/storage/guard.py` | CREATE | ABSENT | `c0b19706ca99563ac408626ca3385a05acd7c6ebbc624d6fe5ea9172f2867877` | 17093 |
| `server/app/health/__init__.py` | CREATE | ABSENT | `3cdf6a70cf7f2a57378dbca2bf09bc21c4c5e8e2d4c3b894d72aa260931a4351` | 751 |
| `server/app/health/router.py` | CREATE | ABSENT | `7351fedde1963e130d53f7c4b1791dda7a2b99cab566d745bcfe3854c80e58e0` | 11376 |
| `server/app/db/faults.py` | CREATE | ABSENT | `035547f389346549729b15df3b3e8e253d3b6c48610ea5ea5e13520faaf2eb8c` | 4274 |
| `tests/integration/test_disk_full_no_ack.py` | CREATE | ABSENT | `4196bb092e566e9e60eae60014a7e68f49ff09b2ce164c8f8bd4f02547d03140` | 18743 |
| `tests/integration/test_readiness_independent_channel.py` | CREATE | ABSENT | `b0d9a4603fa8add3f04b060b8ae7a20afdb35526fe8f16d1b72f7132bc74d680` | 20795 |
| `server/app/main.py` | MODIFY (one delimited include block) | Phase 0 skeleton | `145e1df15573729550f21a30ab620a39d8341595647c3f7922f8c4c3939e1814` | 7081 |
| `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json` | CREATE | ABSENT | `b590e531aadfd6c91c9ac9eacd848f6abf2ce55a1c6edf2529e0e0c4da75bf3e` | 11727 |
| `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md` | CREATE | ABSENT | (this file) | — |

### 1.1 Write-set deviations, declared

Three files are not literally in the card's §3 table. Each is declared rather than assumed:

1. **`server/app/storage/__init__.py`, `server/app/health/__init__.py`** — package markers.
   The card names `server/app/storage/health.py` and `server/app/health/router.py`; neither
   is importable as `server.app.storage.*` without them, and `server/app/db/` carries one
   for the same reason. They contain only a docstring and re-exports.
2. **`server/app/db/faults.py`** — authorised by the Coordinator's dispatch note ("SQLite
   failure injection: extend/use the wrapper in `server/app/db/`"). Added as a **new sibling
   module** rather than an edit to `engine.py`, so no existing file changed and no export in
   `server/app/db/__init__.py` moved.
3. **`server/app/main.py`** — the router registration the Phase 1 dispatch template §2
   permits ("edited **only** by appending one clearly delimited include line"). The block is
   fenced by `# --- BEGIN include: TC-storage-write-blocked-readiness ---` /
   `# --- END include ---`, sits inside `create_app`, and does three things: swaps the Phase
   0 `StubReadinessProvider` for the real provider when no provider was injected, installs
   the error handler, and includes the router with `include_liveness=False`.

**No Alembic migration was written.** This card needs no table. `contracts/state/storage.yaml`
`T-ST-01.transaction_vi` requires the opposite of a table: *"KHÔNG có transaction DB. Trạng
thái này được giữ TRONG BỘ NHỚ tiến trình"*, and `forbidden_transitions` row 4 makes it a
violation for a state to need a DB write before it takes effect. Adding a `storage_health`
table would have been the defect the contract names.

---

## 2. Source baselines relied on

Verified with `sha256sum` at start **and** immediately before this handoff.

### 2.1 Matching the card's §0 pin exactly

| Path | sha256 |
| --- | --- |
| `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` |
| `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` |
| `contracts/data/entities.yaml` | `766fe760bf487781a0b75f070d21960d84d52bccff0465fdaac65dd6ad140ce7` |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` |
| `contracts/ui/screens.yaml` | `e1a57407c0733aa709b464b61da3313f0f6109f5696bd8b39b7e77fc5d5d9074` |
| `precode/adr/ADR-0005-backup-method.md` | `889de2812a8736e328eb7823a82e2b5dab1f46aee13257bfcfedd08d4668bd5c` |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` |
| `acceptance/fixtures/recovery/c-disk-full-mid-ingest.json` | `8f6379b4b0c633ca7d3b48be039671b17ece9da58c1f96067003bf2fb0194092` |
| `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json` | `b518ea3ac66e00e2c117b6586eadb648746fe71947b0c37a17ab50f81cdf7e82` |
| `acceptance/fixtures/recovery/README.md` | `982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8` |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` |
| `acceptance/fixtures/collection/l-storage-write-blocked-mid-run.json` | `7f5f751e9f23ea48ddb0623ce38a168967e621a014f2ca954b5852add193aeaf` |

**Every contract and every fixture in the read set matched, byte for byte, at both checks.**
No oracle drifted while this card was implemented.

### 2.2 Pin drift observed — three decision-record files (`CR-TC-storage-05`)

| Path | Card §0 pin | Observed at handoff |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `6be9189a5e61b03e…` (18989 B) | `da5181b288867413…` |
| `precode/baseline.json` | `d25e2edd05437dc4…` | `d25e2edd05437dc4…` (matches) |
| `precode/decision-register.md` | `4d1a5d6e5d2a4f0a…` | `4d1a5d6e5d2a4f0a…` (matches) |

Sequence of events, recorded because it matters for how the drift should be read:

* At the **start** of this session all three differed from the card's §0. The card was then
  re-pinned on disk (epoch `PC10-PIN-OD01e-20260907`) and all three matched — so work began
  on a clean `SG-HASH`.
* During the session `ADR-0011` was edited again by a concurrent actor. The diff is the
  `OD-20260907-02` ratification (`status: provisional-accepted → accepted`, `ratified_by`
  filled in) plus a repo-layout table now labelled epoch **`PC10-PIN-P1-20260907`**.

I did **not** declare `STALE_BASELINE`, and the reasoning is on the record so the Coordinator
can overrule it: `ADR-0011` is a decision record, not an oracle; the drift touches its status
header and a layout table that says in the same breath that card §3 paths **stay as pinned**;
none of the 14 toolchain rows this card's §8 commands depend on changed; and the file's own
new epoch name indicates a Coordinator-run re-pin in progress rather than an uncoordinated
edit. Every file that *is* an oracle matched. `CR-TC-storage-05` asks for the §0 re-pin to
`PC10-PIN-P1-20260907` so the next card starts clean.

---

## 3. What was built

### 3.1 `server/app/storage/health.py` — the state machine

`T-ST-01`..`T-ST-09` as a closed allowlist (`TRANSITIONS`); any edge not in that tuple raises
`ForbiddenTransition`. Per-state refusals (`REFUSALS`) are transcribed from
`contracts/state/storage.yaml` §2 `refuses`, with the two codes kept distinct —
`STORAGE_WRITE_FAILED` (`retryable_with_budget`) for `write_blocked`/`maintenance`,
`RESTORE_UNVERIFIED` (`operator_decision`) for `recovery_required`.

Numbers come from `contracts/retry-policy.yaml`: probe interval 30 s, 3 consecutive
successes, claim grace 0 s. Guards that are contract text, not defensiveness:

* a probe closer than 30 s to the previous one does not count (so three probes in a
  millisecond cannot "recover");
* a single failed probe resets the streak;
* leaving `write_blocked` goes to `recovery_required`, not `healthy`, whenever a
  `restore_record` is outstanding (`T-ST-08`) — `forbidden_transitions` row 3;
* `T-ST-09` (`write_blocked → maintenance`) is refused while a restore is outstanding, so it
  cannot be used as a laundering route to `healthy` via `T-ST-04`;
* `T-ST-07` keeps `pending_restore_id`, so a disk incident cannot erase a reconciliation debt.

### 3.2 `server/app/storage/guard.py` — the refusal surface

`assert_writable()`, `current_health()`, `enter_maintenance()`, `leave_maintenance()`,
`mark_recovery_required(restore_id)`, `reconciliation_complete(restore_id)`,
`complete_reconciliation()`, `record_write_failure()`, `record_probe()`, and
`get_health(caller_module=…)` (the `storage.get_health` port).

`reconciliation_complete` is the deferred interface the Coordinator asked for: it returns
`False` for every restore until `TC-backup-restore-drill` injects a real
`reconciliation_check`. `False` is not a placeholder chosen for convenience — fixture `j` is
the case that proves it must be the default: integrity `ok`, every count matching the
manifest, and reconciliation still incomplete because the operator had not acknowledged.

The **call contract for `worker-WI`** is the module docstring, and it already matches: the
ingest card landed during this session and its `StorageGuardPort` protocol quotes it.

Error envelopes are built from the generated `SCOPE`/`RETRY_CLASS` maps (never chosen by
hand) and filtered against each code's `details_safe_keys`; `correlation_id` is a ULID
generated in process memory, per `error_envelope.correlation_rule_vi`, because it must exist
precisely when the database cannot supply one.

### 3.3 `server/app/health/router.py` — the independent channel

`health.get_liveness` (unauthenticated, `security: []`, only `status` + `schema_version`) and
`health.get_readiness` (`ownerSessionCookie`). `StorageReadinessProvider` projects the
in-memory machine onto `contracts/ops/deployment.md` §5 rows: `healthy → ok`,
`maintenance → degraded`, `write_blocked`/`recovery_required` → `down`. `maintenance` stays
`degraded` deliberately, so an operator can tell their own window from an incident (`I13`).

Rows owned by other cards (`scheduler`, `embedding`, `research_sources`, `telegram_link`,
`collector`, `analysis_worker`) report `None` = *not computed*, never `ok`.

Auth resolves `server.app.auth.middleware.require_owner_session` by import; when that module
is absent the fallback `owner_session_absent` **denies** every request with the contract's
`UNAUTHORIZED` envelope. The dispatch note allowed an `xfail` here; it turned out
`TC-owner-auth-session` had landed, so the wiring assertion is a real (passing) test and the
deny-fallback is asserted separately by passing it explicitly.

### 3.4 `server/app/db/faults.py` — fault injection

`WriteFaultInjector` arms an engine via `before_cursor_execute` so DML and `COMMIT` raise the
real `sqlite3.OperationalError("database or disk is full")`, with no filesystem side effect.
It also **counts** statements, which is what makes several oracles measurable: "no write was
attempted" is a stronger and more useful claim than "the write failed".

---

## 4. Evidence records

### `EV-E1-01-tc-storage-write-blocked-readiness` — type `SELF_VALIDATION`, level E2

* **Command:** `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/integration/test_disk_full_no_ack.py tests/integration/test_readiness_independent_channel.py -q`
* **Working directory:** `/mnt/virtual/repo/xcrawl` · **Started/ended:** 2026-09-07T10:05:00Z / 10:05:04Z
* **Exit code:** `0` · **Result: PASS — 46 passed, 0 failed, 0 xfailed, 0 skipped**
* **Manifest:** `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json`
  (validated against `evidence/manifest.schema.json` with `jsonschema.Draft202012Validator`)

Oracles observed, each measured by a count, a hash or a string comparison — never by reading
a log:

| Oracle | Expected | Observed |
| --- | --- | --- |
| Fixture `c`: mutations refused with the pinned code | `STORAGE_WRITE_FAILED` | same |
| Fixture `c`: statements reaching the DB while blocked | 0 | 0 |
| Fixture `c`: sha256 of the DB file across the fault window | unchanged | unchanged |
| Fixture `c`: readiness red **and** liveness up together | both | both |
| `EPR-01`: DB statements needed to report the error | 0 | 0 |
| Envelope keys outside `details_safe_keys` | none | none |
| Fixture `l`: checkpoint `acked_through_ingest_sequence` | unchanged | unchanged |
| Fixture `l` branch A / branch B | `T-ST-02` → healthy / `T-ST-08` → recovery_required | same |
| Fixture `j`: `reconciliation_complete("RR-03")` | `False` | `False` |
| Fixture `j`: dispatch + worker claim | `RESTORE_UNVERIFIED`, 0 sends | same |
| SC49: FE-01/05/15/18 | `CAPABILITY_DENIED` | same |
| SC49: FE-29 | `FORBIDDEN_EDGE` | same |
| HC-01: liveness with no database at all | 200 `up` | 200 `up` |
| HC-02: DB statements during readiness | 0 | 0 |

### `EV-E1-02` — quality gates, type `SELF_VALIDATION`

| Command | Exit | Result |
| --- | --- | --- |
| `uv run ruff check <this card's files>` | 0 | PASS — "All checks passed!" |
| `uv run ruff format --check <this card's files>` | 0 | PASS |
| `uv run mypy` (gate is `server/app`, strict) | 1 | PASS **for this card** — 0 errors in any file of this write set. The 2 remaining errors are in `server/app/auth/service.py` (lines 456, 639), owned by `TC-owner-auth-session`. Reported, not touched. |

### `EV-E1-03` — full Python suite, type `SELF_VALIDATION`

`PYTHONDONTWRITEBYTECODE=1 uv run pytest` → **1 failed, 117 passed, 2 xfailed**.

The single failure is `server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0`
(`CR-TC-storage-01`). The 2 xfails belong to other cards. Recorded as observed; nothing was
edited to make it green.

### Not run

`E3`/`E4` (live X, Telegram, AI) — `NOT_RUN`, not applicable to this card. A live disk-full
drill against a real full volume — `NOT_RUN`; it is the only way to close `REQ-S9.3-08`.

---

## 5. Card checklist

| Item | State | Where |
| --- | --- | --- |
| §3 `server/app/storage/health.py` — `T-ST-01`..`T-ST-09` | DONE | 9 transitions + 5 forbidden transitions enforced |
| §3 `server/app/storage/guard.py` — block mutation when `write_blocked` | DONE | `assert_writable` raises before any transaction |
| §3 `server/app/health/router.py` — DB-independent channel | DONE | HC-01..HC-04 |
| §3 `tests/integration/test_disk_full_no_ack.py` | DONE | 20 tests |
| §3 `tests/integration/test_readiness_independent_channel.py` | DONE | 26 tests |
| §4 produces `storage.get_health` | DONE | `StorageGuard.get_health` with default-deny |
| §4 produces `health.get_liveness` | DONE | router (app keeps the Phase 0 route; see §1.1) |
| §4 produces `health.get_readiness` | DONE | `GET /v1/health/readiness` |
| §5 denied paths — no ACK, no persisted-error claim, no cursor advance | DONE | tests in `test_disk_full_no_ack.py` |
| §5 R5-01 boundary codes | DONE | driven from the boundary fixture |
| §6 `I02` / `I13` / `I15` | DONE | statement counters, `as_of` + not-computed rows, reconciliation gate |
| §7 `STORAGE_WRITE_FAILED` / `RESTORE_UNVERIFIED` / `UNAUTHORIZED` | DONE | all from `rr_contracts.generated`; no string literals |
| §8 both commands run | DONE | see §4 |
| §10 `SG-01` (independent channel provable) | DONE | proven by statement count, not by status code |
| §10 `SG-DENY` | DONE | 5 edges into `MOD-data-store`, exact codes |
| §10 `SG-HASH` | DONE with concern | §2.2 |
| §13 evidence manifest | DONE | validated |
| UI last-known display (`UI-01`..`UI-04`) | NOT DONE — **out of scope** | card §1 non-goal; `as_of` + `storage_health` are exported for card 16 |
| Backup/restore procedure | NOT DONE — **out of scope** | card §1 non-goal; interface only |

---

## 6. Unresolved refs

### Change requests

**`CR-TC-storage-01` — the Phase 0 readiness tripwire has fired (blocking a green suite).**
`server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` asserts
`GET /v1/health/readiness` returns 404. Its docstring says: *"if a later change quietly adds a
readiness route in the app factory, this test fails and the ownership boundary is re-examined
rather than crossed by accident."* This card is that boundary's owner and the crossing is
deliberate, so the test has done its job and must now be retired or inverted (assert 401/200
instead of 404). The file is outside this card's write set; I left it failing rather than
edit it. Evidence: §4 `EV-E1-03`.

**`CR-TC-storage-02` — the evidence schema cannot express this card's ceiling.**
`evidence/manifest.schema.json` constrains `review_type: SELF_VALIDATION` to
`claim.supports_label ∈ {DRAFT_FOR_REVIEW, CONTRACT_READY}`, while the card's §9 ceiling is
`IMPLEMENTATION_VERIFIED` and the dispatch permits self-validation only. Every Phase 1 card
hits this. The manifest therefore claims `DRAFT_FOR_REVIEW`; reaching
`IMPLEMENTATION_VERIFIED` needs either an independent review record or a schema amendment.
Coordinator ruling required.

**`CR-TC-storage-03` — `create_app()` does not wire `app.state.auth_service`.**
Because `health.get_readiness` correctly uses `server.app.auth.middleware.require_owner_session`,
and the app factory does not set `app.state.auth_service`, a request to
`/v1/health/readiness` on the bare factory raises `RuntimeError` instead of returning 401.
This is a cross-card wiring gap between this card and `TC-owner-auth-session`, not a defect in
either module. I did **not** catch the `RuntimeError` in my exception handler: masking a
wiring bug behind a 500 envelope would hide it. Whoever owns the app-factory integration
should wire the auth service.

**`CR-TC-storage-04` — the probe table `T-ST-02` describes does not exist.**
`contracts/state/storage.yaml` `T-ST-02.guard_vi` says the recovery probe is *"một write NHỎ
vào bảng probe riêng"*, but none of the 60 entities in `contracts/data/entities.yaml` is such
a table. Per `SG-EDGE` I did not invent one: tables are the entity contract's authority. The
probe is implemented as an injection point (`record_probe(success=…)`) with the streak and
spacing rules fully tested, and the actual small write is left to whoever adds the entity.
Either `entities.yaml` needs a `storage_probe` table, or `storage.yaml` should say the probe
writes to an existing table.

**`CR-TC-storage-05` — re-pin card §0 to `PC10-PIN-P1-20260907`.** See §2.2.

### Assumptions introduced (PROVISIONAL)

| Id | Assumption | Why |
| --- | --- | --- |
| `PROV-WR-01` | The refusal code for a caller with no edge to `storage.get_health` is derived from the caller's **runtime**: `RT-server` → `FORBIDDEN_EDGE`, anything else → `CAPABILITY_DENIED`. | Reproduces all five codes pinned in the boundary fixture without a hard-coded per-edge table, and matches `HC-03`'s explicit statement for the collector. An unknown module denies with `CAPABILITY_DENIED` (deny harder when the registry does not know the caller). Verify against ruling R5-01 if a sixth edge appears. |
| `PROV-WR-02` | `job_dispatch` and `delivery_dispatcher` readiness rows are computed by this card. | `contracts/ops/deployment.md` §5 defines both purely in terms of storage health, so leaving them `None` would report "not computed" for something that *is* computed. |
| `PROV-WR-03` | `readiness.as_of` is the moment the storage state was last established or re-confirmed. | `UI-01` requires an `as_of` and defines it as the last successful DB read; with the state living in memory, the state's own observation time is the closest honest value. Card 16 may need a different one when it reads real business rows. |

### Open questions

* The card's §13 names the manifest location as
  `evidence/runs/TC-storage-write-blocked-readiness/manifest.json` (PROVISIONAL); the
  Coordinator's dispatch names `evidence/runs/<card>-E1-<UTC>.json`. I followed the dispatch.
  The run is **not** registered in `evidence/index.json` — that file is PC09's and outside
  this write set.
* `REQ-A1` remains `KC`; nothing here depends on it.

---

## 7. Statement of claim (SRC-PLAN §14.3)

**Claim.** The `storage.health` state machine, the mutation guard and the DB-independent
health channel behave as `contracts/state/storage.yaml` specifies, for the four states, nine
transitions, five forbidden transitions, four `independent_health_channel` rules and the five
forbidden edges into `MOD-data-store`.

**Baseline.** spec `d35e1f2d…`; `contracts/state/storage.yaml` v0.3.0 `a77803f1…`;
`contracts/errors.yaml` `640991c9…`; `contracts/ports.yaml` `c15b676b…`;
`contracts/modules.yaml` `cf536acb…`; implementation revision: uncommitted working tree, file
hashes in §1.

**Requirements covered.** `REQ-S9.3-08` (partially — see *not established*), `REQ-S8.3-01/02/03`,
`REQ-AC15`, `REQ-D58` (gate only), `I02`, `I13`, `I15`.

**Evidence manifest IDs.** `EV-E1-01-tc-storage-write-blocked-readiness`.

**Observed result.** 46/46 tests pass; `ruff` and `mypy --strict` clean on this write set.

**Not established.**

* SQLite's real behaviour on a genuinely full volume. The failure is **injected**; the "do not
  corrupt the SQLite file" half of `REQ-S9.3-08` is `NOT_RUN` and needs a live drill.
* That the post-restore reconciliation is *correct* — only that the gate stays locked while
  the predicate is false.
* That the UI distinguishes last-known state (card 16). This card supplies `as_of` and
  `storage_health`; it does not render them.
* That **every** write path in the system calls the guard. Only `ingest.submit_batch` exists
  today and it does. Each future mutation card must hold that itself.
* The probe's real write (`CR-TC-storage-04`).
* Timing: the 30 s / 3-probe rules were exercised on an injected clock.

**Open issues.** `CR-TC-storage-01` .. `CR-TC-storage-05`; `PROV-WR-01` .. `PROV-WR-03`.

**Review type.** `SELF_VALIDATION`. I wrote both the implementation and the tests that check
it. This is **not** an independent audit and must not be recorded as one.

---

# ADDENDUM — `PKT-TC-STORAGE-FIX1`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-STORAGE-FIX1` |
| worker principal | `worker-WR` |
| authority_id | `AUTH-COORD-TC-STORAGE-FIX1` (parent `AUTH-OWNER-20260907-03`) |
| lease_id | `LEASE-TC-STORAGE-e2` (fencing 2) |
| rulings | `…/scratchpad/packets/FIX-A3R1-rulings.md`; findings `F-A3R1-11`, `-13`, `-09`, `-07` |
| status | **`DONE`** |
| next actor | Coordinator (A3-R2 verification) |
| lease_released_at | 2026-09-07T11:15Z |

## A.1 Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/app/health/router.py` | MODIFY — added `install_storage` | `4cfe39ea4aa777579c287da8c2acb6c88dfbea01cb2154574c8e34ee03c72738` | 14249 |
| `server/app/health/__init__.py` | MODIFY — export `install_storage` | `76e82ad622bb4fb11417ada2f72a203160c9e120f676e7f1c96e25c767f559b7` | 795 |
| `server/app/storage/guard.py` | MODIFY — docstring names `app.state.storage_guard` | `05c2d397ead6f3581413dfdfae9af247669ab12c039a5841c30c89cfe2442e7f` | 17708 |
| `server/app/main.py` | MODIFY — include block only | `1c21e48eca2f8c680612bfb3f6ce721ed8feb1af75f664181b8b4a5353e3a865` | 7830 |
| `tests/integration/test_readiness_independent_channel.py` | MODIFY — 9 bare-factory tests | `d0aae11017a61857b2ac90375ba9d01ad439538850b1ad3cd14cd0f362232ea9` | 26719 |

`tests/integration/test_disk_full_no_ack.py`, `server/app/storage/health.py` and
`server/app/storage/__init__.py` are unchanged. No contract, fixture or migration touched.

## A.2 `F-A3R1-11` — the guard and the reconciliation gate are wired on the shipped factory

`server.app.health.router.install_storage(app, guard=None, *, readiness_provider=None,
reconciliation_check=None, include_liveness=False)`.

**The attribute is `app.state.storage_guard`**, and after `create_app()` it is present on
*every* construction path. That was the defect: the previous include block only built a
guard inside `if readiness_provider is None`, so `create_app(provider)` produced an app with
no `storage_guard` at all, and any write gate looking for one silently did not run.

`install_storage` also installs the readiness provider built from **that same guard**, so the
endpoint and the gate cannot disagree. `test_the_factory_guard_is_the_same_object_the_readiness_endpoint_reads`
drives the guard and reads the provider, so only a shared object passes it — two guards would
be two in-memory machines, and a disk failure seen by the write gate would leave the health
channel still reporting `healthy`.

For `worker-WI`: `IngestContext(engine=…, owner_id=…, storage_guard=app.state.storage_guard)`.
Use that object; do not construct a second `StorageGuard`. This is now stated in the
`server/app/storage/guard.py` module docstring, which is where the ingest card's
`StorageGuardPort` already points.

**Reconciliation gate wired, and shut.** `mark_recovery_required` moves the shipped guard to
`recovery_required` and `complete_reconciliation` refuses with `RESTORE_UNVERIFIED`, because
`create_app` passes no `reconciliation_check`. That is the contract, not an omission (`I15`,
`NC-10`): `TC-backup-restore-drill` supplies the predicate, and
`test_install_storage_passes_the_reconciliation_check_through` exercises the seam end to end
so the hand-off point is proven rather than asserted.

**The recovery probe remains an injection point — `CR-TC-storage-04` stands.** No
`storage_probe` entity exists in `contracts/data/entities.yaml`, so on a real deployment
`write_blocked → healthy` still cannot fire on its own. Any claim mentioning `write_blocked`
end to end must exclude that transition, as A3-R1 §4.1 requires.

Nine tests added, all on `create_app()` or on `install_storage` directly:
guard present and healthy · guard and provider are one object · the gate refuses after a
write failure · the reconciliation gate is reachable and shut · an injected provider still
gets a guard · `install_storage` adopts an existing guard · the `reconciliation_check` seam
works · readiness on the factory answers 401 (reachable **and** guarded — a 404 would mean
the router was never included, and both are "not 200") · liveness stays public.

## A.3 `F-A3R1-13` — include delimiters

This card's block in `server/app/main.py` now opens `# >>> TC-storage-write-blocked-readiness
(MOD-data-store, MOD-health-service) >>>` and closes `# <<< TC-storage-write-blocked-readiness
<<<`, with the import and the single call both inside. The other three cards' blocks were not
touched; the finding named the auth card's top-level import, which is its owner's to move.

## A.4 `F-A3R1-09` — fixture and scenario audit

Every fixture in this card's §2 read set, and every scenario in its §8:

| Fixture (§2) | State | Where / why |
| --- | --- | --- |
| `recovery/c-disk-full-mid-ingest.json` | **EXERCISED** | `test_fixture_c_*` — events, expected codes, readiness pair |
| `recovery/j-restore-verification-incomplete-dispatch-locked.json` | **EXERCISED** | `test_fixture_j_*`, `recovering_guard` |
| `collection/l-storage-write-blocked-mid-run.json` | **EXERCISED** | `test_fixture_l_*` — both recovery branches |
| `boundary/a-default-deny-sweep-36-edges.json` | **EXERCISED (partial, by design)** | `test_default_deny_on_storage_get_health` asserts the 5 events whose callee is `MOD-data-store` (FE-01/05/15/18/29). The other 31 name other callees and are other cards' obligation; per `F-A3R1-08` they are not counted here. |
| `recovery/README.md`, `boundary/README.md` | N/A | Directory documentation, not fixtures. Read as part of the read set. |
| `identity/pos-ingest-batch-valid.json` | **EXERCISED** (not in §2) | Supplies the wire-valid batch for the cross-card ingest test, so that test cannot pass for the wrong reason by failing validation before reaching the gate. |

| Scenario (§8) | State | Reason |
| --- | --- | --- |
| `SC26` | EXERCISED | fixtures `c`, `l` |
| `SC27` | EXERCISED | fixture `j` |
| `SC36` | EXERCISED | fixture `l`, both branches |
| `SC42` | EXERCISED | fixture `j` |
| `SC49` | EXERCISED (5/36 events, see above) | fixture `boundary/a` |
| `SC15` | **`NOT_RUN`** | SC15 is the UI last-known/three-states scenario (`storage.yaml` `ui_read_model`, `UI-01`..`UI-04`). Writing the UI is an explicit **non-goal** of this card (§1: *"Không viết UI (card 16)"*). This card supplies what SC15 needs — `as_of` and `storage_health` on the readiness snapshot, and per-module rows that report `None` rather than `ok` — and asserts those; rendering them as *last-known* is `TC-ui-runs-three-states`. Recorded rather than silently omitted, per dispatch rule 4. |

## A.5 `F-A3R1-07` — `server/app/db/faults.py` ownership transferred

`server/app/db/faults.py` (sha256 `035547f389346549729b15df3b3e8e253d3b6c48610ea5ea5e13520faaf2eb8c`,
4274 bytes) has been **adopted into the Phase 0 skeleton write set by `worker-WS`**. It is no
longer claimed by this card. I did not move, rename or modify it in this packet. This card
remains its principal consumer (both integration test modules import `WriteFaultInjector` and
`DISK_FULL_MESSAGE`); changes to it are now the skeleton owner's to make, and a change to its
counter semantics would invalidate the "no write was even attempted" oracles in §4 of the
main handoff.

The finding's own framing is worth keeping on the record: the Phase 1 dispatch note spoke of
"the wrapper in `server/app/db/`" as though it already existed, so this was a dispatch defect
as much as a Worker one. The correct remedy was an amendment naming the file and its owner,
which is what happened — not a retroactive edit of the card's §3.

## A.6 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/integration/test_disk_full_no_ack.py tests/integration/test_readiness_independent_channel.py -q` | 0 | **55 passed** (46 + 9 new), 0 failed |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest` (full suite) | 0 | **291 passed, 4 xfailed, 0 failed, 0 errors** |
| `uv run ruff check .` | 1 | 2 errors, both `server/migrations/versions/0002b_shared_move_set_tables.py` (E501) — another card's file, reported not touched. 0 in this write set. |
| `uv run ruff format --check <this write set>` | 0 | clean |
| `uv run mypy` | 0 | **Success: no issues found in 25 source files** |

`CR-TC-storage-01` is **resolved**: the skeleton owner inverted the Phase 0 tripwire, which is
now `test_readiness_is_routed_and_denies_an_unauthenticated_caller`. The full suite is green.

`CR-TC-storage-03` is **resolved**: `install_auth(app)` now runs in the factory, so an
unauthenticated `GET /v1/health/readiness` returns 401 with the contract envelope instead of
raising `RuntimeError`. Asserted by `test_readiness_on_the_factory_denies_without_a_session`.

While re-running the full suite mid-wave I twice saw collection errors in
`tests/integration/test_ingest_ack_lost.py` and `test_denied_edges.py` that did not reproduce
when those files were run alone and were gone on the next run. They tracked other workers'
in-flight edits, not this change; the final numbers above are from a clean run.

## A.7 Standing items

`CR-TC-storage-02` (evidence schema caps `SELF_VALIDATION` below the card's ceiling),
`CR-TC-storage-04` (no `storage_probe` entity — `write_blocked → healthy` cannot fire
unaided on a real deployment) and `CR-TC-storage-05` (re-pin card §0) are unchanged and still
open. `PROV-WR-01`..`PROV-WR-03` stand as recorded.

The evidence manifest `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json`
is **not** reissued: its command, oracles and observed values describe the E1/E2 run of the
original packet and remain true. This addendum records the FIX1 run separately; a fresh
manifest for FIX1 was not requested and inventing one would double-count the same evidence.

---

# ADDENDUM — `PKT-TC-STORAGE-FIX2`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-STORAGE-FIX2` |
| worker principal | `worker-WR` |
| authority_id | `AUTH-COORD-TC-STORAGE-FIX2` (parent `AUTH-OWNER-20260907-03`) |
| lease_id | `LEASE-TC-STORAGE-e3` (fencing 3) |
| finding | `F-A3R2-03` — the E1 manifest pinned four files whose sha256 no longer matched disk after FIX1 |
| status | **`DONE`** |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T11:42Z |

## B.1 The finding, confirmed

Recomputed against disk; the drift is exactly the four files FIX1 touched, and nothing else:

| Path | Changed in FIX1 by |
| --- | --- |
| `server/app/health/router.py` | added `install_storage` |
| `server/app/health/__init__.py` | export `install_storage` |
| `server/app/storage/guard.py` | docstring naming `app.state.storage_guard` |
| `tests/integration/test_readiness_independent_channel.py` | 9 bare-factory tests |

Every contract, every fixture and the two source documents still matched. My FIX1 addendum
listed the new hashes in its own change table but did not re-issue the manifest — so the
evidence record kept asserting bytes that had moved. The finding is correct.

## B.2 Changes

| Path | Operation | sha256 | Bytes |
| --- | --- | --- | --- |
| `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T113817Z.json` | CREATE | `93b294ea71d97b5612c58404a0cf16945295394eb8ce3d7d5616498c3e676012` | 14413 |
| `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json` | MODIFY — `result` → `STALE` | `3414d9aa56937b05f8f1a9411a6504e57aee0930bc449d1409884bbd72183455` | 12671 |

No code, contract, fixture or test changed in this packet.

## B.3 The new manifest — `EV-E1-04-tc-storage-write-blocked-readiness`

Re-issued from current bytes and a fresh run, not edited in place:

* **command:** `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/integration/test_disk_full_no_ack.py tests/integration/test_readiness_independent_channel.py -q -p no:cacheprovider`
* **started/ended:** 2026-09-07T11:37:29Z / 11:37:33Z · **exit 0** · **result `PASS`**, level `E2`
* **observed:** 55 passed, 0 failed (46 from the original packet + 9 added by FIX1)
* every artifact, fixture, contract and source hash recomputed; verified afterwards that
  **no pinned hash differs from disk**
* the oracle gained the three FIX1 propositions: `app.state.storage_guard` exists after
  `create_app()`; the guard and the readiness provider are one state machine (drive the
  guard, the endpoint follows); the reconciliation gate is reachable and stays shut without
  a `reconciliation_check`
* `limitations` and `claim.not_established_vi` now state explicitly that
  `write_blocked → healthy` is **not** established on a real deployment, because the probe is
  still an injection point (`CR-TC-storage-04`) — the narrowing A3-R1 §4.1 asked for — and
  that `db/faults.py` is now owned by the skeleton (`F-A3R1-07`)
* the stale `not_checked_vi` line about `app.state.auth_service` being unwired was dropped:
  `install_auth` runs in the factory now, so keeping it would have been a false limitation

**Preventing the recurrence.** The new manifest carries
`invalidation.invalidated_by_paths` — 31 paths covering every artifact, fixture and contract
it pins. Changing any of them now makes this record `STALE` **by rule**
(`precode/gates.yaml` §invalidation_rules), so the next drift is caught mechanically rather
than by an auditor noticing. The original manifest omitted that block and fell back to the
default rules, which is why FIX1 could move four files without anything objecting.

## B.4 How supersession was expressed

The packet allowed `superseded_by` "if the schema allows". It does not:
`evidence/manifest.schema.json` sets `additionalProperties: false` at the top level, so an
extra key would make the record fail its own schema.

The schema-native expression was used instead — `result: STALE` with `stale_reason` naming
the replacement by path and evidence id. This is better than a prose-only note because it is
machine-readable: a consumer reading the old file is told it is superseded without having to
find this handoff. `stale_reason` is exactly what SRC-PLAN §16 defines for evidence whose
inputs have moved.

The old manifest was **not deleted** and its body was **not rewritten**. Only `result` and
`stale_reason` changed. Its `PASS` conclusion remains true of the bytes it pins — 46/46 green
at 10:05Z — and the `stale_reason` says so in as many words; what it no longer does is
describe the current tree. Deleting it would have destroyed the record of a real run, and
silently editing its hashes to match today's disk would have been worse: a manifest whose
execution timestamp and hashes come from different moments is a fabricated one.

Both files were validated with `jsonschema.Draft202012Validator` against
`evidence/manifest.schema.json`: **both VALID**.

## B.5 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/integration/test_disk_full_no_ack.py tests/integration/test_readiness_independent_channel.py -q -p no:cacheprovider` | 0 | **55 passed**, 0 failed |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider` (full suite) | 0 | **303 passed, 4 xfailed, 0 failed, 0 errors** |
| `jsonschema` validation of both manifests | — | both VALID |
| re-verification of every hash pinned by the new manifest | — | 0 mismatches |

The full-suite count rose from 291 to 303 as other cards' fix-wave packets landed; none of
those tests are this card's and none were touched here.

## B.6 Standing items

`CR-TC-storage-02`, `CR-TC-storage-04` and `CR-TC-storage-05` remain open and unchanged.
`PROV-WR-01`..`PROV-WR-03` stand. `CR-TC-storage-01` and `CR-TC-storage-03` stay resolved.

One consequence of this packet is worth flagging for `PKT-PC09-P1` (`F-A3R1-03`, registering
the E1 runs in `evidence/index.json`): this card now has **two** manifests, and the one to
register as current is `…-E1-20260907T113817Z.json`. The 10:09Z record should be registered
as `STALE` or not at all — registering it as a live PASS would reinstate exactly the
mismatch `F-A3R2-03` reported.

---

# ADDENDUM — `PKT-TC-STORAGE-FIX3` — **STOPPED at `SG-EDGE`**

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-STORAGE-FIX3` (wiring wave 1, gap `G-3`) |
| worker principal | `worker-WR` |
| authority_id | `AUTH-COORD-TC-STORAGE-FIX3` (parent `AUTH-OWNER-20260908-11`) |
| lease_id | `LEASE-TC-STORAGE-e4` (fencing 4) |
| status | **`BLOCKED_DEPENDENCY`** — the packet's own stop condition fired |
| change request | **`CR-TC-storage-06`** (below) |
| next actor | Coordinator → whoever owns `contracts/data/entities.yaml` |
| lease_released_at | 2026-09-08T06:45Z |

**No change was made to `server/app/storage/guard.py` or `server/app/storage/health.py`.**
The packet said: *"if an entity/table for storage health/maintenance exists, use it; if none
exists, STOP with a CR naming the missing entity — do not add an undeclared table"*. None
exists. This addendum and the re-issued manifest are the only writes.

## C.1 The gap is real — reproduced end to end

`docs/owner-runbook.md` §9.4 documents a two-step restore: open the window, then restore.
Run against a fresh migrated database with a bootstrapped owner
(scratch dir, never in the repo):

```
inv A  backup_cli snapshot           → backup_snapshot_id 01M1ZJD1VNBKKFG5KHWTAZ89ZB, exit 0
inv D  backup_cli verify             → {"state":"verified","artifact_sha256_matches":true,
                                        "counts_match":true}, exit 0
inv E  backup_cli maintenance --open → {"transition":"T-ST-03",
                                        "storage_health":"maintenance"}, exit 0
inv F  backup_cli restore …          → {"code":"VALIDATION_ERROR",
                                        "details_safe":{"field_path":"storage_health",
                                        "violation_kind":"precondition_not_met",
                                        "operation_id":"backup.restore_snapshot"}}, exit 2
```

Step E reports success and step F — the very next invocation — cannot see the window it
opened. `server/app/backup/restore.py:209` checks `guard.current_health().value != "maintenance"`,
and each CLI process constructs a fresh `StorageGuard()`, which starts at `healthy`
(`contracts/state/storage.yaml` `initial_state`). **The documented restore path is
unreachable**, exactly as `G-3` states.

The cause is mine and I will name it plainly: `StorageHealthMachine` holds its state in
process memory. That was correct for `write_blocked` and is required by `T-ST-01`
(*"KHÔNG có transaction DB … giữ TRONG BỘ NHỚ tiến trình"* — you cannot write "cannot write"
into a database that cannot be written). But `maintenance` is the opposite case: `T-ST-03`
says *"**Ghi một hàng maintenance window** (trạng thái vẫn ghi được ở thời điểm này) + chuyển
cờ trong bộ nhớ"* — a row **and** a flag, precisely because storage is still writable when an
operator opens the window. I implemented the flag and not the row, and no test caught it
because every test of mine lives in one process. The single-process assumption was never
stated in my handoff; it should have been.

## C.2 Why I stopped instead of persisting it

`contracts/data/entities.yaml` (60 entities, sha256 `ebcf460f…` at the time of writing)
declares **no** entity for storage health or a maintenance window. Verified four ways:

1. entity names — none named `storage_health`, `maintenance_window`, `storage_probe`, or
   anything similar; the only `*_window` is `coverage_window`, which is a reporting period;
2. field names — no field anywhere in the 60 entities contains `storage`, `health`,
   `maintenance` or `probe`;
3. transactions — of the 8 declared, only `TXN-purge-all` mentions maintenance, and it
   mentions it as a *precondition read* via `storage.get_health`, not as a row it writes;
4. the shipped schema — 49 tables after `alembic upgrade head`; none of them either.

Every occurrence of "maintenance" in `entities.yaml` points **outward** at
`contracts/state/storage.yaml`. The entity contract treats storage health as state owned
elsewhere; the state contract says a row is written. The two do not meet. That is the defect,
and it is in the contract layer, which this card may not edit (`SG-CONTRACT`, `SG-EDGE`).

The two tables I could have abused, and why I did not:

* **`settings`** (`key`, `value_json`) would hold it fine — but `contracts/modules.yaml`
  gives `data_owner_of: settings` to `MOD-settings-service`. Writing storage state into
  another module's table is a `FORBIDDEN_EDGE` in everything but name, and it would put a
  `MOD-data-store` invariant behind a service that does not exist yet (`G-6`).
* **inventing `storage_maintenance_window`** is what the packet forbids, and
  `tests/contract/test_schema_matches_entities.py` would fail it on assertion 1 ("every table
  has an entity of the same name") — that gate asserts equality in both directions per
  shipped table, so an undeclared table cannot ship even quietly.

## C.3 `CR-TC-storage-06` — the missing entity

**Requested:** an entity in `contracts/data/entities.yaml` owned by `MOD-data-store` that
persists the `maintenance` window `T-ST-03` already says is written. Suggested shape, derived
from `contracts/state/storage.yaml` §3 and nothing else — the contract owner decides:

| field | type | nullable | why the contract needs it |
| --- | --- | --- | --- |
| `id` | `string_ulid` | no | |
| `owner_id` | `string_ulid` | no | single-owner scoping, as every other table |
| `opened_at` | `timestamp_utc_ms` | no | `T-ST-03` is an explicit operator act at a time |
| `opened_by_principal` | `string` | no | `T-ST-03`: *"Hành động EXPLICIT của Operator (`backup_operator` scope)"* — a window with no principal cannot evidence that |
| `reason` | `enum` | no | `snapshot \| migration \| purge_all \| restore` — `maintenance` is entered for four contracted purposes |
| `closed_at` | `timestamp_utc_ms` | yes | NULL = open. This is the field that makes the state readable by the next process |
| `snapshot_verified_at` | `timestamp_utc_ms` | yes | `T-ST-04` forbids closing before `backup.verify_snapshot` passes; without this the guard cannot enforce it across processes |

A partial index on `(owner_id) WHERE closed_at IS NULL` gives "at most one open window",
which is the invariant `T-ST-03`/`T-ST-09` assume when they speak of *the* window.

**Scope of the fix once the entity exists** (ready to execute on a new lease): the guard
loads `maintenance` and `recovery_required` at construction and writes on `T-ST-03`,
`T-ST-04`, `T-ST-09`; `write_blocked` **stays in memory** — persisting it is what `T-ST-01`
and `forbidden_transitions` row 4 forbid; and a test proves a second process on the same
database file observes `maintenance`.

**What is already persistable and is not:** `recovery_required` needs no new entity —
`restore_record` exists with `dispatcher_unlocked_at` and `operator_ack_at`, so "a restore
record whose dispatcher is still locked" *is* `recovery_required` on disk. I did not
implement that half either, because doing so would leave `maintenance` in memory and
`recovery_required` on disk: `T-ST-05` requires `maintenance` first, so the restore path
would still be unreachable and the state machine would be split across two storage models
for no gain. It should land in one change, with the entity.

## C.4 Two defects observed in files outside this card

Reported, not touched:

* `tools/backup_cli.py:187` — `_resolve_owner` raises `BackupError.__new__(BackupError)`
  (bypassing `__init__`), so on a database with no owner row the CLI dies with
  `AttributeError: 'BackupError' object has no attribute 'code'` at
  `server/app/backup/snapshot.py:145` instead of emitting an error envelope. Exit 1 with a
  traceback where the contract wants a `code`. Owner: the backup card.
* `server/app/wiring.py:153` — `mypy` error: *Module "server.app.delivery.service" does not
  explicitly export attribute "DeliveryIntentKind"*. The one `mypy` error in the tree.
  Owner: `PKT-P0-FIX5` (WS).

## C.5 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `uv run pytest tests/integration/test_disk_full_no_ack.py tests/integration/test_readiness_independent_channel.py` | 0 | **55 total, 0 failed, 0 errors, 0 skipped** |
| `uv run ruff check <this card's files>` | 0 | clean |
| `uv run ruff format --check <this card's files>` | 0 | 7 files already formatted |
| `uv run mypy` | 1 | 0 errors in this write set; 1 in `server/app/wiring.py` (above) |
| full suite | varies | **unstable, and not because of this card** — see below |

**The full suite is a moving target right now.** Three consecutive runs during this packet
gave 0, 5 and 29 failures, in `test_collector_loop.py`, `test_analysis_once_per_key.py`,
`test_attempt_not_result.py` and `test_worker_loop.py` — wave-2 files being written while the
suite ran. The clean run recorded **1093 tests, 1088 passed, 5 xfailed, 0 failed**. In every
run, zero failures were in this card's files. I am reporting the instability rather than
picking the green run and calling it the result.

## C.6 Manifest re-issue

| Path | Operation | sha256 | Bytes |
| --- | --- | --- | --- |
| `evidence/runs/TC-storage-write-blocked-readiness-E1-20260908T063909Z.json` | CREATE (`EV-E1-05`, `PASS`) | `4b73f86a35c0e31babc576602e179191cba51c361a2463ab1c406e7b25bf1d40` | 15468 |
| `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T113817Z.json` | MODIFY → `STALE` | `09fa4fcabf7c21c7af63c943a2cf87ab1a150174624d4b4f98944e450ce4acf5` | 15361 |

The 11:38Z record went stale **by its own rule**: five files it pinned changed
(`contracts/retry-policy.yaml`, `contracts/data/entities.yaml`,
`precode/adr/ADR-0011-frameworks-and-toolchain.md`, `precode/baseline.json`,
`precode/decision-register.md`) and all five are in the `invalidation.invalidated_by_paths`
block added in FIX2. That block did the job it was added for.

Worth stating because it bounds the blast radius: **no artifact of this card changed**, the
whole of `contracts/state/storage.yaml` is still byte-identical to the original §0 pin
(`a77803f1…`), and the three constants this card reads from `retry-policy.yaml` are unchanged
(30 s, 3 consecutive probes, grace 0 s). The code is not stale; only the manifest's pinned
baseline was.

Both manifests validate against `evidence/manifest.schema.json`; the new one was re-verified
to have zero hash mismatches against disk.

## C.7 Standing items

`CR-TC-storage-02`, `-04`, `-05` remain open; **`CR-TC-storage-06` is new and blocks `G-3`**.
`CR-TC-storage-01` and `-03` stay resolved. `PROV-WR-01`..`-03` stand.

`CR-TC-storage-04` (no `storage_probe` entity) and `CR-TC-storage-06` (no maintenance-window
entity) are the same defect seen twice: `contracts/state/storage.yaml` describes rows that
`contracts/data/entities.yaml` never declared. They should be fixed in one amendment.

---

# ADDENDUM — `PKT-TC-STORAGE-FIX4` — `G-3` closed at the port

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-STORAGE-FIX4` (wiring wave 1, gap `G-3`) |
| worker principal | `worker-WR` |
| authority_id | `AUTH-COORD-TC-STORAGE-FIX4` (parent `AUTH-OWNER-20260908-11`) |
| lease_id | `LEASE-TC-STORAGE-e5` (fencing 5) |
| gate | `maintenance_window` in `entities.yaml` 0.3.0 (`AMD-ENT-maintenance-01`) **and** `PKT-PC02-FIX16` released — both verified before the first write |
| status | **`DONE_WITH_CONCERNS`** — the port is closed and proven; the CLI caller is another card's file (`CR-TC-storage-07`) |
| next actor | Coordinator → W6B for `tools/backup_cli.py` |
| lease_released_at | 2026-09-09T07:30Z |

## D.1 Changes

| Path | Operation | sha256 | Bytes |
| --- | --- | --- | --- |
| `server/migrations/versions/0015_tc_storage_maintenance_window.py` | CREATE | `82df80ad6352cbcd…` | — |
| `server/app/storage/guard.py` | MODIFY | `1a913367693180ae…` | — |
| `tests/integration/test_readiness_independent_channel.py` | MODIFY (+13 tests) | `2ca9ae0262e7e20b…` | — |
| `evidence/runs/…-E1-20260909T072209Z.json` | CREATE (`EV-E1-06`, PASS) | `9bcc5dde33f7fbf1bf8a91387e4e6ab5e501ca94259571d76b87cb03000d12f6` | 17421 |
| `evidence/runs/…-E1-20260908T063909Z.json` | MODIFY → `STALE` | `efb3dabb35e97148ae04ec10309100e1a3336ebb2fe0e120805fed8e6202926e` | 16145 |

`server/app/storage/health.py` is **unchanged**. The state machine did not need to change:
persistence is a load at construction (`initial=` / `pending_restore_id=`, parameters it
already had) plus writes in the guard. Keeping the machine pure is why `write_blocked` could
not accidentally acquire a persistence path.

**`SG-HASH` note, as the packet predicted:** `contracts/data/entities.yaml` no longer matches
this card's §0 pin — it now carries `AMD-ENT-maintenance-01`, which is the amendment this
packet was waiting for. Expected drift, not staleness; WP re-pins after. Verified that
`contracts/state/storage.yaml` — the card's actual oracle — is still byte-identical to the
original pin `a77803f1…`, so no transition changed under me.

## D.2 The migration

`0015_tc_storage_maintenance_window`, chained off `0014_tc_secret_settings_service`
(`alembic heads` → 1, asserted structurally, not against a literal). Ten columns, three named
CHECKs and the partial unique index, all transcribed from `ENT-maintenance-window` rather
than from my earlier CR draft — the amendment added `storage_health_at_open`, `closed_by` and
`restore_record_id` beyond what I had proposed, and `test_schema_matches_entities.py` asserts
set equality **in both directions**, so a field invented or omitted here fails that gate.
It passes with **0 differences**.

## D.3 What is persisted, and what must never be

The entity's `what_it_is_not_vi` is the whole design, so the code follows it literally:

* **`maintenance` → the table.** One row per window; `closed_at IS NULL` means open.
* **`recovery_required` → `restore_record`, not a new column.** A restore whose
  `dispatcher_unlocked_at` is NULL *is* that state. Reading it there rather than copying it
  means the two can never disagree, and a disagreeing copy is one that unlocks a dispatcher.
* **`write_blocked` → nothing, ever.** `T-ST-01` and `forbidden_transitions` row 4. A row
  read at startup saying "blocked" would refuse writes on a healthy disk; one saying
  "healthy" would let a full disk take assignments, which is what `I02` forbids.
  `test_write_blocked_is_never_loaded_from_disk` asserts a guard that has just gone
  `write_blocked` hands a *fresh* process `healthy`.

**Load order:** an unreconciled restore outranks an open window. `T-ST-05` runs the restore
*inside* the window so both rows can exist at once, and of the two only
`recovery_required` keeps the dispatcher locked — loading `maintenance` would refuse strictly
less than `I15` requires. `test_recovery_required_outranks_an_open_window_on_load` pins it.

**Persistence is opt-in.** `StorageGuard()` with no store behaves exactly as before, because
a dozen other cards construct it bare in their own tests; `StorageGuard.from_engine(engine,
owner_id=…)` is the persisted path. `test_a_guard_without_a_store_is_unchanged` asserts the
default rather than leaving those cards to discover a change.

## D.4 One prohibition that needed a column to survive a process — `PROV-WR-04`

`T-ST-09`'s `forbidden_vi` is *"Dùng đường này để lách sang `healthy`"*: opening maintenance
from `write_blocked` must not become a laundering route to healthy. Inside one process the
probe streak enforced that. Across processes only `storage_health_at_open` can, which is why
the amendment carries that column.

`leave_maintenance(..., write_path_recovered=False)` therefore refuses to close a window
opened from `write_blocked` unless the caller asserts the write path came back. **No tenth
transition was introduced** — `contracts/state/storage.yaml` declares nine and this is
`T-ST-04` being guarded, with the refusal raised as the existing `ForbiddenTransition`,
exactly as `T-ST-09` is already refused while a restore is pending. Recorded as `PROV-WR-04`
because the enforcement point is my choice; the prohibition is the contract's.

Two audit fields are required and **not defaulted**: `opened_by`/`reason` on open,
`closed_by` on close, all `NOT NULL` or CHECK-bound. A fabricated principal in an audit
column is worse than a refused call, because afterwards it reads as evidence. Both are
validated *before* the machine moves, so a refusal leaves memory and disk agreeing — a
half-applied transition is the failure this table exists to fix.

## D.5 Second-process proof

In-test (`test_a_second_process_observes_the_open_maintenance_window`): a new `Engine` on the
same file, so nothing is shared but SQLite. Also reproduced across two real OS interpreters:

```
process 1:  before: healthy   transition: T-ST-03   after: maintenance
process 2:  storage_health: maintenance
            restore precondition (T-ST-05) satisfied: True
```

Before this packet, process 2 read `healthy` and `restore` refused with
`precondition_not_met`. Thirteen tests were added in total, including the unique-index
refusal at the store, the `T-ST-09` close guard, `snapshot_verified_at` being populated, the
`link_restore_record` seam, and the two negative controls above.

## D.6 `CR-TC-storage-07` — the CLI caller is not in this lease

`tools/backup_cli.py:_guard()` still builds an in-memory `StorageGuard`, so the *CLI* chain
`maintenance --open` → `restore` is still not closed end to end. That file belongs to the
backup card. The port is ready and the change is small:

```python
StorageGuard.from_engine(engine, owner_id=owner_id,
                         reconciliation_check=reconcile.reconciliation_complete(engine, owner_id=owner_id))
```

plus `--reason` / operator principal at the `maintenance --open` call site and `closed_by` at
`--close`. Until then, `G-3` is closed at the port and open at the caller — stated that way
rather than claimed as finished.

`link_restore_record()` is the other seam W6B should call, **after** its `restore_record`
INSERT commits: `restore.py` calls `mark_recovery_required` *before* that INSERT and the
column is a foreign key, so the link cannot be written at mark time.

## D.7 Verification

| Command | Exit | Result |
| --- | --- | --- |
| card tests + `test_schema_matches_entities.py` | 0 | **78 tests, 0 failed, 0 errors, 0 skipped** |
| `test_schema_matches_entities.py` alone | 0 | 10/10, **0 differences both ways** |
| `alembic heads` | 0 | **1 head** (`0015_tc_storage_maintenance_window`) |
| full suite | 0 | **1147 tests, 1143 passed, 0 failed, 0 errors, 4 xfailed** |
| `ruff check` / `ruff format --check` | 0 | clean on this write set |
| `uv run mypy` | 0 | **Success: no issues found in 100 source files** |

## D.8 Standing items

`CR-TC-storage-06` is **resolved** by `AMD-ENT-maintenance-01` and this packet.
`CR-TC-storage-07` is **new**. Still open: `CR-TC-storage-02` (evidence schema caps
`SELF_VALIDATION` below the card's ceiling), `CR-TC-storage-04` (no `storage_probe` entity, so
`write_blocked → healthy` still cannot fire unaided on a real deployment), `CR-TC-storage-05`
(§0 re-pin — now also covering `entities.yaml`). `PROV-WR-01`..`-04` stand.

---

# ADDENDUM — `LEASE-TC-STORAGE-e6` — format finding was misattributed; **no change made**

The report was that repo-wide `ruff format --check` is red on
`tests/integration/test_readiness_independent_channel.py`. It is not. That file reports
`1 file already formatted`, exit 0, and its sha256 is unchanged at
`2ca9ae0262e7e20bd5e15bad12e9e5346f0f216d3370ca82a6b17e23372068a7` before and after this
packet — I ran the check, not a reformat, so there is nothing to re-run and nothing to
re-issue.

Reproducing the CI step exactly (`uv run ruff format --check .`, per
`.github/workflows/python.yml:38` and `Makefile:51`) names a different file:

```
Would reformat: tests/integration/test_restore_side_effect_lock.py
1 file would be reformatted, 185 files already formatted
```

That file belongs to `TC-backup-restore-drill`, is outside this lease, **and has uncommitted
changes in the working tree right now** — `git status` shows it modified, and
`ruff format --diff` shows the pending edits are a new CLI test calling
`maintenance --open --reason restore` and asserting `opened["window_id"]`. That is W6B taking
up `CR-TC-storage-07` and wiring `tools/backup_cli.py` to the port this card shipped in FIX4.

So I did not reformat it. Running `ruff format` across another card's file while its author
has it open would collide with in-flight work to fix two lines of line-wrapping, and the two
files are easy to confuse because both are about maintenance windows. The one-line fix is
W6B's to apply with the rest of their change; the diff is trivial (two statements that now
fit on one line).

No manifest re-issue: no pinned artefact's bytes changed.
