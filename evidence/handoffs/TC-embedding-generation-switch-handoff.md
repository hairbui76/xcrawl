# HANDOFF — `TC-embedding-generation-switch`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-EMBED` — card `agent-tasks/TC-embedding-generation-switch.md` (Phase 3, M3 → M5, gate G5) |
| worker principal | `worker-W3C` |
| authority_id | `AUTH-COORD-TC-EMBED` (parent `AUTH-OWNER-20260908-06` / `-09`, records `precode/owner-decisions-06.md`, `packets/OWNER-DECISIONS-20260908-08.md`) |
| lease_id | `LEASE-TC-EMBED-e1` (exclusive on card §3 write set + one Alembic revision + this handoff + one evidence manifest) |
| pin epoch | `PC10-PIN-P3-20260908` — all 22 sources of card §0 recomputed with `sha256sum` before the first write; **22 of 22 match**, byte counts included |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `CONTRACT_READY` for what this record supports; the card's ceiling is `IMPLEMENTATION_VERIFIED` and reaching it needs the independent review of card §12. See §5. |
| review_type | `SELF_VALIDATION`. Nothing here is an independent audit. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T19:40Z (execution-host UTC clock; see §6.4) |

Status is `DONE_WITH_CONCERNS` rather than `DONE` for two reasons, both recorded below and
neither self-resolvable: the card's stated dependency `TC-report-coverage-publish-cas` does
not exist, so one required ordering proof is `xfail` (§3.2); and four contract-level
discrepancies were found and **not** fixed, because `contracts/`, `acceptance/` and
`agent-tasks/` are read-only to this card (§4).

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/embedding/generation.py` | CREATE | ABSENT | `9a622ddf611222168b5a96fb213d2c947ed66b379a84a5a78d51d86850311b79` | 27192 |
| `server/app/embedding/repository.py` | CREATE | ABSENT | `78de3da8428bfe6a41eb9254cee691edef45b8217be3abbfcd4a56722bede13c` | 19701 |
| `server/app/embedding/service.py` | CREATE | ABSENT | `be0d9530f51cd0eb371986fea26e871b4bd951c081132baac82d8fcc88d241e6` | 30676 |
| `tests/contract/test_embedding_generation_guard.py` | CREATE | ABSENT | `3c3ab7bee4503f74d5833afe864964b5f4478a6c144861c891f1064ecf58726d` | 22561 |
| `tests/integration/test_generation_activation.py` | CREATE | ABSENT | `8cf838b05bf37c3630b85c6f6dcbe366e8c5c5bfd42be235e509b5ab89443532` | 29950 |
| `server/migrations/versions/0006_tc_embedding_generation_switch.py` | CREATE | ABSENT | `cac9da6e6a2232cb3c373177aa0e7d51b2b5e976639dfa4ec5604bff94674010` | 7637 |
| `evidence/runs/TC-embedding-generation-switch-E1-20260907T192842Z.json` | CREATE | ABSENT | `fba983f6e368cd6d4e1f1f4813b9e0c9b08d9d83347b9330cea73f7c73500969` | 15807 |
| `evidence/handoffs/TC-embedding-generation-switch-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified; `server/app/main.py` was **not** touched; no git operation was
performed; `PYTHONDONTWRITEBYTECODE=1` for every command, so no `__pycache__` was produced.

### 1.1 Write-set notes

1. **No `server/app/embedding/__init__.py`.** Card §3 lists three modules and no package
   marker, and the write set is "card §3 exactly". `server/app/` is a regular package, so
   `server/app/embedding/` loads as an implicit namespace portion — the same shape
   `server/app/research/` already ships in. `mypy --strict` (with `namespace_packages =
   true`) is clean over it.
2. **No `router.py`.** All four `embedding.*` operations are `transport: internal` in
   `contracts/ports.yaml`, so there is no HTTP path to register and no shared-file edit.
3. **The Alembic revision** is authorised by the dispatch's lease rule ("plus your Alembic
   revision(s), must keep ONE head"). It creates exactly the two entities
   `contracts/modules.yaml` assigns to this module in `data_owner_of`:
   `embedding_generation` and `tag_vector`. **One head:** a sibling in this wave landed
   `0007_merge_phase3_5_heads`, which merges `0006_tc_embedding_generation_switch` with the
   two other `0006_*` branches; `alembic heads` now reports the single head
   `0009_tc_telegram_unknown_delivery`, and
   `tests/integration/test_generation_activation.py::test_the_migration_graph_has_exactly_one_head`
   asserts `len(heads) == 1` **structurally**, never against a literal revision id.

---

## 2. What was built

### 2.1 The four operations (card §4, `contracts/ports.yaml`)

| operation id | entry point | transaction |
| --- | --- | --- |
| `embedding.generate_vectors` | `EmbeddingService.generate_vectors` | one per batch |
| `embedding.get_active_generation` | `EmbeddingService.get_active_generation` | none (read) |
| `embedding.start_generation_rebuild` | `EmbeddingService.start_generation_rebuild` | one |
| `embedding.activate_generation` | `EmbeddingService.activate_generation` | `TXN-activate` — one `BEGIN…COMMIT` |

### 2.2 I12 is a guard, not a convention

The design decision worth the Coordinator's attention: **there is no unguarded dot product
in this package**. `generation.py` pairs every vector with the fingerprint
`(generation_id, model_name, model_version, dimension, normalization)`, and `cosine()`
refuses before multiplying when two fingerprints differ. The alternative — a check inside
the report builder — is a check a builder can forget, and fixture `l`'s oracle is *"0 phép
cosine chéo generation"*, which is a claim about what the similarity function was ever asked
to do.

The instrument fixture `n` asks for (`given.instrumentation_vi`: a counter around the
similarity function recording `(generation_a, generation_b)` of **every** cosine) is
`ComparisonLedger`. It counts **performed** and **refused** separately, because
`selection.md` §5 says the negative oracle alone cannot distinguish a correct
implementation from one that blocks everything. Both are asserted.

### 2.3 Atomicity is an index, not care

`ux_embedding_generation_active` is `UNIQUE(owner_id) WHERE state = 'active'`. With it in
place there is no observable instant with zero or two active rows, and the retire/activate
pair cannot half-apply.
`test_the_unique_index_makes_two_active_rows_impossible` asserts this **with the service
bypassed entirely** — raw SQL, second `active` row, `UNIQUE constraint failed` — so the
property belongs to the schema and not to the caller's discipline. Every `active_count()`
read in the integration test goes through a **separate connection**, so "no observer sees
two" is about committed state.

### 2.4 The activation guard

`built_vector_count >= expected_vector_count`, re-evaluated on a fresh `COUNT(*)` **inside**
the activation transaction, before any `UPDATE` is issued. A refusal therefore commits
nothing, which is what fixture `n`'s `after_event_7.row_oracles` requires ("Từ chối KHÔNG
đổi state của G1 hay G2; không có transaction nào commit"); the test compares every column
of both rows before and after.

`expected_vector_count IS NULL` answers **False**, not True: `ports.yaml` wants "bằng chứng
đã đủ vector" and a row that never recorded a target has produced none. Answering True would
make the guard vacuous for exactly the generations most likely to be half-built.

### 2.5 The local model (`REQ-D48`/`REQ-D50`, `AC-16`)

`LocalEncoder` is a port with **nowhere to put a credential or a base URL** — that is the
enforcement of `network_egress: []` / `secret_access: none`, not a convenience.
`SentenceTransformersEncoder` (the ADR-0011 adapter) imports the library lazily via
`importlib` and constructs it with `local_files_only=True`; nothing in this repository
constructs one.

**No model was downloaded or loaded.** `server/pyproject.toml` (Phase 0) already declares
`sentence-transformers` under an optional extra that CI does not install and states "No
model is ever downloaded by this repo's test or CI paths". The dispatch's fallback therefore
applies: tests use `DeterministicHashEncoder`, an offline SHA-256 stand-in, and **the
real-model dimension check is recorded `NOT_RUN`**. Choosing a model is `REQ-OQ09` behind
`REQ-A3` and card §10 `SG-01` forbids it here; the encoder takes its model name, version and
dimension from the caller and chooses nothing.

---

## 3. Verification

### 3.1 Commands and results

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_embedding_generation_guard.py \
  tests/integration/test_generation_activation.py -p no:warnings
```

`45 passed, 1 xfailed` · exit code **0** · 2026-09-07T19:28:42Z → 19:28:49Z.
The two commands card §8 names (`-q` on each file separately) were run first and are the
same set of tests; the combined form above is what the evidence manifest pins.

Gates re-run in the same tree:

| Command | Result |
| --- | --- |
| `pytest tests/contract/test_schema_matches_entities.py` | PASS — the two new tables equal `entities.yaml` field-for-field, under all four traversal orders |
| `pytest tests/integration/test_denied_edges.py` | PASS — unchanged |
| `ruff check` + `ruff format --check` on the write set | clean |
| `mypy --strict` | `Success: no issues found in 47 source files` |
| `alembic heads` | one head |
| evidence manifest vs `evidence/manifest.schema.json` (Draft 2020-12, format checker on) | 0 errors |

A **full** `pytest` run in the same working tree showed 2 failures in
`tests/integration/test_concurrent_save.py`, a file belonging to a sibling card
(`TC-saved-snapshot`) landing in the same wave. No file of this card's write set is
involved. Reported, not touched.

### 3.2 The one thing not proven — `xfail`, with the reason the card gives

`tests/integration/test_generation_activation.py::test_the_guard_blocks_before_the_publish_commit`
is `@pytest.mark.xfail(reason="pending TC-report-coverage-publish-cas", strict=True,
raises=ModuleNotFoundError)`.

Card §11 makes this card depend on the report card to prove *"chặn xảy ra trước publish
commit"*. There is no publish transaction to order the refusal against, so the ordering
claim is **not established**. What *is* implemented and tested on its own terms is the
predicate `contracts/state/report.yaml` `ownership_boundary` requires PC04 to hand PC03:
`embedding_generation_matches(expected_embedding_generation_id)`, side-effect-free, spelled
exactly as `contracts/reporting/time-and-tags.md` §4.5 spells it. `strict=True` means the
day the report card lands, an unexpected pass fails the suite — the marker cannot rot.

### 3.3 Oracles, measured

| Oracle (source) | Expected | Observed |
| --- | --- | --- |
| cross-generation cosines performed (fixture `l`, `n`, SC52) | 0 | 0 |
| same-generation cosines performed (`selection.md` §5, O-5b) | > 0 | 2 in the ledger test |
| `embedding_generation[state='active']` after every event (fixture `n`) | 1 | 1 |
| rows changed by the refused activation (fixture `n` event 7) | 0 | 0 |
| G1 rows deleted after the switch (`REQ-D48`, `REQ-S7.3-03`) | 0 | 0 |
| network calls made | 0 | 0 |
| unregistered caller → error code (ruling R5-01 row 2) | `FORBIDDEN_EDGE` | `FORBIDDEN_EDGE` |

`SG-DENY`: the two forbidden edges touching this module are `FE-22` (→ `EXT-ai-provider-api`,
`CAPABILITY_DENIED`) and `FE-23` (→ `MOD-tag-service`, `FORBIDDEN_EDGE`). Both are
`ENF-import-rule` edges, and that half is asserted against the **AST of the shipped source**:
no `httpx`, `requests`, `urllib`, `socket`, `http`, `subprocess`, `anthropic`, `openai` or
`server.app.tag` import in any file of `server/app/embedding/`. The *sandbox* half of
`FE-22` (an empty container egress) remains what
`tests/integration/test_denied_edges.py` already records it as —
`NOT_TESTABLE_AT_THIS_LAYER` — and this card does not claim to have closed it.

---

## 4. Change requests — contract defects found, **not** fixed

Per card §10 `SG-CONTRACT` and dispatch rule 3, none of these was edited to make code pass.

### `CR-TC-embedding-01` — `work_label.embedding_generation_id` has no foreign key

`contracts/data/entities.yaml` declares it "FK → embedding_generation.id (I12)". The column
shipped in `0002b_shared_move_set_tables` before this table existed, so no `REFERENCES`
clause was possible then, and SQLite cannot add one to an existing table without rebuilding
it. Rebuilding a table this card does not own (`MOD-analysis-service`) to add a constraint no
test in this card needs was judged the larger risk. **Severity: medium** — a `work_label` row
can currently name a generation that does not exist. Proposed disposition: the analysis card
or a schema-repair packet rebuilds `work_label` with the FK.

### `CR-TC-embedding-02` — card §4 lists a `Consumes` the registry does not grant

Card §4 lists `storage.get_health` under *Consumes*. But `contracts/ports.yaml` gives that
operation `caller_modules: [MOD-health-service, MOD-job-service]`, and
`contracts/modules.yaml` `allowed_edges` has **no** `MOD-embedding-service → MOD-data-store`
row. Under `default_deny` those two cannot both be right, and the card is not the naming
authority for edges. **The module therefore does not call that port.** It accepts an
optional `StorageGuardPort` the caller already holds — the same shape
`server/app/ingest/service.py` uses — and the `STORAGE_WRITE_FAILED` obligation of card §7 is
met by mapping operational SQLite failures on its own writes. Proposed disposition: either
add the edge by change control, or drop the line from card §4.

### `CR-TC-embedding-03` — `errors.yaml` `operations` lists disagree with `ports.yaml` `error_codes`

`contracts/ports.yaml` assigns the `embedding.*` operations five codes; four of them
(`VALIDATION_ERROR`, `NOT_FOUND`, `IDEMPOTENCY_CONFLICT`, `STORAGE_WRITE_FAILED`) do not name
any `embedding.*` operation in their own `operations:` list in `contracts/errors.yaml`, and
`EMBEDDING_GENERATION_MISMATCH` names only `embedding.activate_generation`, not
`generate_vectors` or `start_generation_rebuild`. The code follows `ports.yaml` and card §7.
**Severity: low** (documentation consistency), but it makes the two files disagree about
which codes an operation may raise.

### `CR-TC-embedding-04` — `acceptance/scenarios.yaml` SC52 step numbers drift inside the entry

SC52's `expected_durable_state_vi` says "sau bước 4, mọi selection dùng G2" and "Report ở
bước 5 ghi `embedding_generation_id = G2`", while its own `event_order` puts activation at
step 7 and the mid-rebuild publish at step 6. Fixture `n` is unambiguous and was used as the
oracle, so this is prose drift, **not** an oracle contradiction — hence a CR rather than an
`SG-PC09` stop. `acceptance/scenarios.yaml` is deliberately unpinned in card §0 (PC09-owned).

---

## 5. Completion claim

**Claim:** `CONTRACT_READY` supported by this record.
**Baseline:** spec `d35e1f2d…e0e26`; pin epoch `PC10-PIN-P3-20260908`, all 22 sources of card
§0 rehashed and matching; implementation revision = the six sha256 values in §1.
**Requirements covered:** `REQ-D48`, `REQ-D49`, `REQ-D50`, `REQ-D59`, `REQ-S7.3-03`,
`REQ-AC16` (structurally: no provider path exists), invariants `I12` and `I05`.
**Evidence manifest:** `EVM-TC-embedding-generation-switch` →
`evidence/runs/TC-embedding-generation-switch-E1-20260907T192842Z.json` (`EV-E1-08-…`).
**Observed result:** PASS — 45 passed, 1 xfailed, exit 0.

**Not established.**

1. **`IMPLEMENTATION_VERIFIED`.** That is the card's ceiling, not a self-check's.
   `evidence/manifest.schema.json` caps a `SELF_VALIDATION` record at `CONTRACT_READY`
   (`allOf` clause 6, protocol §9), and the manifest says so in its own `claim` block. The
   independent review of card §12 is what would raise it.
2. **That the block happens before the publish commit** — card §11's dependency; `xfail`.
3. **Anything about a real embedding model.** No model loaded; real-model dimension check
   `NOT_RUN`; `REQ-OQ09` open.
4. **Similarity-threshold quality** (`REQ-A2`/`REQ-A3`, E4). The `0.8000` bootstrap was
   neither read nor changed.
5. **Behaviour under real storage failure.** E2 (SQLite fault injection via
   `server/app/db/faults.py`) has **not** been run against the `tag_vector` write path or the
   activation transaction; `STORAGE_WRITE_FAILED` is mapped in code but never triggered.
6. **Behaviour under real concurrency.** "Two rebuilds, one wins" is proven at the constraint
   level with two sequential calls, not with two racing processes.
7. Card §9's note stands: `contracts/http/openapi.yaml` still declares
   `claim_ceiling: DRAFT_FOR_REVIEW` in its own header (verified with `grep`), so the
   contract floor under this card is not uniformly `CONTRACT_READY`.

**Review type: `SELF_VALIDATION`.** No independent audit was run, and no line of this
handoff should be read as one.

---

## 6. Stop gates, checked

| ID | Outcome |
| --- | --- |
| `SG-HASH` | **PASS.** All 22 pinned sources rehashed before the first write; 22/22 match on hash and byte count. |
| `SG-STACK` | No framework chosen. Everything used — FastAPI-free service layer, SQLAlchemy 2 Core, Alembic, pytest — was already fixed by ADR-0011 and the Phase 0 skeleton. |
| `SG-G5` | Wait gate honoured: no write occurred until `agent-tasks/README.md` declared `PC10-PIN-P3-20260908` **and** `evidence/handoffs/PC10-handoff.md` carried the `PKT-PC10-FIX24` addendum with `lease_released_at 2026-09-08T00:45Z`. Polled at 60 s intervals until then. |
| `SG-PC09` | `acceptance/scenarios.yaml` read fresh (unpinned). SC24 and SC52 do **not** contradict card §8; the numbering drift inside SC52 is `CR-TC-embedding-04`. |
| `SG-DENY` | FE-22 and FE-23 handled — §3.3. Error codes are the R5-01 ones; `FORBIDDEN_EDGE`, not `UNAUTHORIZED`, for an in-process unregistered edge. |
| `SG-CONTRACT` | Four discrepancies found; **none** fixed. Raised as `CR-TC-embedding-01…04`. |
| `SG-EDGE` | No new edge taken. `storage.get_health` explicitly **not** called — `CR-TC-embedding-02`. |
| `SG-01` | No threshold read or changed. |
| `SG-02` | Not reached: `insufficient_evidence` / density belongs to the report card. |

### 6.4 Two housekeeping facts

1. **Clock.** The execution host's UTC clock reads `2026-09-07`, while the dispatch epoch is
   named `PC10-PIN-P3-20260908`. Every timestamp in the manifest and in this handoff is the
   **measured** clock, not the epoch name; the evidence record says so in `inputs.clock`.
2. **`evidence/index.json` was not updated.** Card §13 asks for the run to be registered
   there, but that file is PC09-owned and outside this packet's write set. The Coordinator or
   a PC09 packet should add `EV-E1-08-tc-embedding-generation-switch`.

---

*`PKT-TC-EMBED` · `worker-W3C` · `lease_released_at` 2026-09-07T19:40Z · claim
`CONTRACT_READY` · `SELF_VALIDATION` — no item here is an independent audit.*

---

# ADDENDUM — `PKT-TC-EMBED-FIX1` (audit finding `F-A3-P3-03`)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-EMBED-FIX1` · lease `LEASE-TC-EMBED-e2` (fencing 2) · worker `worker-W3C` |
| finding | `F-A3-P3-03` (`…/scratchpad/audits/A3-P3-R1-report.md`): `acceptance/fixtures/reporting/m-density-worked-example.json` is in card §2 but was neither exercised nor recorded `NOT_RUN` |
| status | `DONE` · claim unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) · next actor `Coordinator` |
| lease_released_at | 2026-09-07T20:22Z |

## A.1 The finding was correct, and the fixture splits in two

The audit is right that the fixture was silently unread. Reading it showed it is not wholly
out of scope, which is why the answer is **both** halves of the packet's instruction rather
than only `NOT_RUN`:

* `FX-RP-M` carries `invariant_refs: ["I12"]` and `scenario_refs: ["SC08"]` — and `SC08` is
  one of the four anchors in card §8. Its `forbidden_effects` list includes one line that is
  squarely this module's: *"So sánh với kỳ trước thuộc embedding generation khác (I12)."*
* Everything else in it — `m_t`, `density_prior`, `delta`, the `evidence_state` decision — is
  the density algorithm, which card §1 lists as a **non-goal** and assigns to
  `TC-report-coverage-publish-cas`.

## A.2 Exercised (it did drop into the existing test in one step)

Three tests added to `tests/contract/test_embedding_generation_guard.py`, under a section
comment that states the split above:

| Test | What it measures |
| --- | --- |
| `test_the_density_example_never_spans_two_generations` | Walks the **whole** fixture: 3 full `embedding_generation` descriptors and 6 `embedding_generation_id` references (`given`, `expected.report`, `variant_below_min_sample`, `variant_cold_start`) collapse to **exactly one** `GenerationFingerprint`. So the forbidden effect above cannot occur in this worked example. Then runs `assert_single_generation` over the set with `total_refused == 0` — the positive half: the guard does **not** block a period that is legal. |
| `test_the_cold_start_period_after_a_switch_has_no_prior_baseline` | `variant_cold_start` pins `insufficient_reason = 'generation_reset'`, empty `member_target_keys`, and a direction whose `embedding_generation_id` is the **current** generation, not the retired one — the I12 face of "periods under the old generation are not a baseline". |
| `test_the_density_parameters_are_left_untouched_by_this_card` | Asserts the two parameters that describe the *comparison function* against shipped code (`metric == "cosine"`, `rounding_decimals == SCORE_DECIMALS == 4`), and asserts the other six are still `PROVISIONAL_BOOTSTRAP` — the boundary made measurable instead of described. |

The walk is deliberately two walks (full descriptors, and bare ids): a report can name a
generation without restating the model, and a stray id is exactly how a second generation
would enter a density baseline unnoticed. The first draft of the test used one walk, found 3
blocks where it asserted 4, and **failed** — the assertion was corrected to what the fixture
actually contains rather than the threshold lowered blindly.

## A.3 Recorded `NOT_RUN`, with the concrete reason

**The density arithmetic of `FX-RP-M` is `NOT_RUN`.** Reason, stated concretely rather than
as "out of scope": the six parameters `radius`, `min_members`, `comparison_window_k`,
`min_prior_windows`, `min_delta`, `prior_floor` carry `parameters_status:
PROVISIONAL_BOOTSTRAP` and sit behind gates `REQ-A4` / `REQ-OQ08`, which are unresolved; and
the computation of `m_t`, `density_prior`, `delta` and the `evidence_state` decision belongs
to `MOD-report-service` via `TC-report-coverage-publish-cas`, which card §1 names as a
non-goal of this card and which does not exist yet. **No density number is computed anywhere
in this card's code.** This is now in the manifest's `limitations.not_checked_vi` (entry 4)
as well as here.

## A.4 Files, tests, and the superseded record

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `tests/contract/test_embedding_generation_guard.py` | MODIFY | `3c3ab7be…f58726d` | `bbce004a655197442b53d9ff0144c88785938e4073818fc6c4a9e8eda7cc08dd` | 29692 |
| `evidence/runs/TC-embedding-generation-switch-E1-20260907T201528Z.json` | CREATE | ABSENT | `67e31e5a2f1fe15067125a5e7296c6bec3d7bcab157f3ad6a9f011ae6343208e` | 18144 |
| `evidence/runs/TC-embedding-generation-switch-E1-20260907T192842Z.json` | MODIFY | `fba983f6…3500969` | `357ff1158ca851fc1bd32c8a14a2706d80d2c77bc1aead1b7daae14ac9b44d17` | 16309 |
| `evidence/handoffs/TC-embedding-generation-switch-handoff.md` | MODIFY | `50013440…db1b0288` | (this file) | — |

The `20260907T192842Z` record is now `result: STALE` with a `stale_reason` naming this packet
and `INV-06`: its `implementation_revision` pinned the previous bytes of the test file. The
`20260907T201528Z` record supersedes it, adds `m-density-worked-example.json` (sha256
`719f9c4d…`, 29177 bytes) to `inputs.fixtures`, and validates against
`evidence/manifest.schema.json` with **0 errors**. So does the stale one.

**No production file changed** — `server/app/embedding/*` and the migration are byte-identical
to §1, so §2 and §4 of this handoff stand unaltered and the six `CR-TC-embedding-0x` items are
unchanged. **No claim change.**

### Tests

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_embedding_generation_guard.py \
  tests/integration/test_generation_activation.py -p no:warnings
```

**48 passed, 1 xfailed** · exit 0 · 2026-09-07T20:15:28Z → 20:15:36Z (was 45 passed, 1
xfailed). `ruff check` and `ruff format --check` clean; no production file touched, so
`mypy --strict` is unaffected.

Full suite: **821 passed, 3 failed, 10 xfailed** in 101 s. The three failures are in sibling
cards' files landing in this same wave — `tests/integration/test_analysis_once_per_key.py`,
`tests/integration/test_concurrent_save.py`,
`tests/integration/test_multipart_partial_receipt.py` — and their assertion messages name
`analysis_attempt` / `assignment_lease` and `TelegramSaveAdapter.create_save`. The only
mentions of "embedding" in the whole run log are the Alembic upgrade lines for
`0006_tc_embedding_generation_switch`. Reported, not touched.

---

*`PKT-TC-EMBED-FIX1` · `worker-W3C` · `lease_released_at` 2026-09-07T20:22Z · claim unchanged
`CONTRACT_READY` · `SELF_VALIDATION` — no item here is an independent audit.*

---

# ADDENDUM — `PKT-TC-EMBED-FIX2` (post-wave rulings `CR-TC-REPORT-04`, `-08`)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-EMBED-FIX2` · lease `LEASE-TC-EMBED-e3` (fencing 3) · worker `worker-W3C` |
| rulings | `…/scratchpad/packets/FIX-P4-wave-rulings.md` — `CR-TC-REPORT-04` (rounding) and `CR-TC-REPORT-08` (xfail target) |
| status | `DONE` · claim unchanged (`CONTRACT_READY`, `SELF_VALIDATION`) · next actor `Coordinator` |
| lease_released_at | 2026-09-08T00:52Z |

## B.1 `CR-TC-REPORT-04` — the rounding was half-to-even, and the contract says half-up

`contracts/reporting/selection.md` §3 says it twice: *"Mọi giá trị similarity được làm tròn
**half-up** về 4 chữ số thập phân"*, and the parameter table repeats `rounding: half-up`.
`cosine` used Python's built-in `round`, which rounds half to **even**. The two disagree on
exactly one class of input — a tie — and a tie is a score sitting on the threshold the
comparison is about, so this is the worst possible place for the two rules to differ.

`generation.py` now has `round_half_up`, using `decimal.ROUND_HALF_UP` at `SCORE_DECIMALS`.
`Decimal` rather than an `int(x * 10**n + 0.5)` trick: the trick is wrong for negative values,
and cosine is legitimately negative.

Two boundary tests added, and the choice of constant matters: `0.15625` is `5/32`, so it is
**exactly** representable in binary and really is a tie — most decimal-looking ties (`0.12345`)
are not, and a test built on one would have passed under both rules and proved nothing.

| input | contract (half-up) | Python `round` |
| --- | --- | --- |
| `0.15625` | `0.1563` | `0.1562` |
| `0.03125` | `0.0313` | `0.0312` |
| `-0.15625` | `-0.1563` | `-0.1562` |

`test_rounding_is_half_up_and_not_pythons_half_to_even` asserts **both** the expected value
and the divergence from `round`, so restoring `round` fails rather than passing on a platform
that happens to agree. `test_cosine_rounds_its_own_result_with_the_half_up_rule` recomputes the
raw quotient and checks `cosine` applies that rule — otherwise the rule could be right in
isolation while `cosine` quietly kept the built-in.

## B.2 `CR-TC-REPORT-08` — the xfail pointed at a module that never existed, and is now real

The marker imported `server.app.report.service`. That card's §3 never creates it; W4A's entry
point is `server.app.report.publisher.publish_report`. Re-pointed — **and made real**, because
the ruling's condition holds: the guard call is observable. W4A calls this card's predicate as
check 3 of the six-check CAS, with a real `EmbeddingService` as `embedding_port`:

```python
if not context.embedding_port.embedding_generation_matches(
    snapshot.owner_id, snapshot.generation.generation_id
):
```

`test_the_guard_blocks_before_the_publish_commit` now walks the whole sequence: `build_report`
pins G1 → `record_build` writes the `building` row (T-RP-01) → `generate_vectors` +
`activate_generation` switch to G2 *between build and publish* → `publish_report` refuses.

Three assertions, and the last two are what make it an **ordering** claim rather than a repeat
of the predicate's unit test: the code is `EMBEDDING_GENERATION_MISMATCH`;
`COUNT(report WHERE status='published')` is unchanged (fixture `l`); and the build row carries
`abort_reason = 'embedding_generation_mismatch'` (T-RP-04) — which only happens *inside* the
publish path, so the refusal provably occurred there and not before it was entered.

Getting there needed one correction: without `record_build` the publisher answers `NOT_FOUND`
at its idempotency check and never reaches the embedding guard (`publish_cas.idempotency_rule_vi`
case 4, "publish does not create a build"). The first draft omitted it and failed with
`NOT_FOUND` — a green test that skipped the guard would have been worse than a red one.

**Card §11's dependency is discharged.** The stale "not established" line has been removed from
the manifest's `claim` block rather than left standing.

## B.3 Files, tests, and the superseded record

| Path | Operation | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/embedding/generation.py` | MODIFY | `9a622ddf…50311b79` | `c1c5df0dfc61fbf8fb8894ab251fc1fa5ffd6a398223d05067107ccfd990bdf1` | 29115 |
| `tests/contract/test_embedding_generation_guard.py` | MODIFY | `bbce004a…a7cc08dd` | `d700e74c2bdeab86a1a872d7850072034a7eee7ccc6e9725677322e576e24c58` | 32304 |
| `tests/integration/test_generation_activation.py` | MODIFY | `8cf838b0…89443532` | `9cdaa42b50cbde75655014e9dbf854c69cd310a7a07fac090b71b1298ffe63fe` | 33749 |
| `evidence/runs/TC-embedding-generation-switch-E1-20260908T004611Z.json` | CREATE | ABSENT | `d0eeabb649064aef456257ac0ff97c13b43670e068060426be9055d66fad54c2` | 19138 |
| `evidence/runs/TC-embedding-generation-switch-E1-20260907T201528Z.json` | MODIFY | `67e31e5a…6343208e` | `0639eda088d56815d06d7e21d95edce97717f5dcfb8d2e0814e9e156d83a1203` — now `result: STALE` | 18749 |
| `evidence/handoffs/TC-embedding-generation-switch-handoff.md` | MODIFY | `ca26615c…5e2d29a70` | (this file) | — |

`server/app/embedding/{service,repository}.py` and the migration are **byte-identical** to §1,
so §2 and §4 stand and `CR-TC-embedding-01…04` are unchanged.

### Tests

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  tests/contract/test_embedding_generation_guard.py \
  tests/integration/test_generation_activation.py -p no:warnings
```

**51 passed, 0 xfailed** · exit 0 · 2026-09-08T00:46:11Z → 00:46:19Z (was 48 passed, 1 xfailed:
+3 rounding/ordering tests, and the one xfail became a pass). `ruff check`, `ruff format --check`
and `mypy --strict` all clean for `server/app/embedding`.

Full suite: **1012 passed, 0 failed, 7 xfailed, 7 errors** in 136 s. All 7 errors are in
`tests/integration/test_permanent_failure_report_intact.py`, which `CR-TC-REPORT-09` assigns to
W5C (its report stand-in does not satisfy the real `report` schema). Down from 18 as W5C's fix
lands; none involves this card's files.

The `20260907T201528Z` record is now `result: STALE` with a `stale_reason` naming this packet,
both rulings and `INV-06`. The new record supersedes it and validates against
`evidence/manifest.schema.json` with **0 errors**; so does the stale one.

---

*`PKT-TC-EMBED-FIX2` · `worker-W3C` · `lease_released_at` 2026-09-08T00:52Z · claim unchanged
`CONTRACT_READY` · `SELF_VALIDATION` — no item here is an independent audit.*
