# HANDOFF — `TC-report-coverage-publish-cas`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-REPORT` — card `agent-tasks/TC-report-coverage-publish-cas.md` (Phase 4, M4, gate G5) |
| worker principal | `worker-W4A` |
| authority_id | `AUTH-COORD-TC-REPORT` (parent `AUTH-OWNER-20260908-10`, Owner instruction 2026-09-08 "do until finish everything") |
| lease_id | `LEASE-TC-REPORT-e1` (exclusive on card §3 write set + one Alembic revision + handoff + evidence manifest + one delimited include block in `server/app/main.py`) |
| pin epoch | `PC10-PIN-P3b-20260908` — SG-HASH run **twice**, before any read work and again immediately before the first write: **34/34 pinned files match byte for byte, 0 drift** |
| wait gate | all three conditions verified at 2026-09-07T21:0xZ: (1) `git log -1 --format=%s` on `main` = `feat: Phase 3 (M3) + Phase 5 (M6, plain text) …` (`fb3944a`); (2) `agent-tasks/README.md` line 124 declares `PC10-PIN-P3b-20260908`, `evidence/handoffs/PC10-handoff.md` carries the `PKT-PC10-FIX25` addendum with `lease_released_at 2026-09-08T03:05Z`; (3) SG-HASH clean |
| status | **`DONE_WITH_CONCERNS`** — everything the card asks for exists and runs; ten `CR-TC-REPORT-nn` items are open, one of them (**CR-TC-REPORT-09**) breaks 18 tests in another card's files and needs a decision before this wave is packaged |
| completion_claim | see §6. The card's ceiling is `IMPLEMENTATION_VERIFIED`; this record is `SELF_VALIDATION`, which `evidence/manifest.schema.json` caps at `CONTRACT_READY`, so the manifest claims that and no more |
| next actor | Coordinator (then W4B, W4D, W6B, whose wait gate was this handoff) |
| lease_released_at | 2026-09-07T21:40Z |

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/report/coverage.py` | CREATE | ABSENT | `ae331815ee19a763ffbcafbd9a44cbc9062a522be258fc43d0e2a534942e0bf1` | 27952 |
| `server/app/report/builder.py` | CREATE | ABSENT | `181816623458f018329d3b8d1f44cda1ea15b64bfc52da74c20458d43f3c12f1` | 68801 |
| `server/app/report/publisher.py` | CREATE | ABSENT | `2e6beff966a54474f301625d2b4c2de7d0437d608bf7939b37290ec57a74000a` | 60113 |
| `server/app/report/router.py` | CREATE | ABSENT | `aee6114c9e8fdda7c37f075e3a4f3f56648635a7249230af54f83a6a4a82b194` | 12925 |
| `server/migrations/versions/0010_tc_report_coverage_publish_cas.py` | CREATE | ABSENT | `e09879cc76dc36eb1eafa54505930c340012aa975b813fe404625757d6a6ae03` | 23632 |
| `tests/contract/test_report_schema.py` | CREATE | ABSENT | `7c6cb46f1fc58b184454d861dc7082c2ad14a91f49dea7b5c2ff29d0542c6835` | 21249 |
| `tests/integration/test_publish_cas.py` | CREATE | ABSENT | `edc33b6f4525ec7a655d1d1feac6b2e213fa30923cd31819e5b3f1c79e106da5` | 26640 |
| `tests/integration/test_coverage_contiguous.py` | CREATE | ABSENT | `b5a446d2e4933962efcb8b6f038422ce6c11dd1e378dd2b998583fdf96929a0e` | 24078 |
| `server/app/main.py` | MODIFY (one include block) | shared file, see §1.1 | `73392a3c3dadd1b07a3f58383d014c1dbfdb1c4d4e0fe3727679980ca0ff8d97` | 13222 |
| `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` | CREATE | ABSENT | `f867b5f8f058d7cfa8cfdfc626cb31c0287cb465445bb97a42a61864507a2c70` | 14958 |
| `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified; no other card's package or test file was touched. No git command
that mutates anything was run. No live X, AI or Telegram call, no browser, no secret,
`PYTHONDONTWRITEBYTECODE=1` throughout.

### 1.1 Write-set notes

1. **`server/app/main.py`** carries exactly one delimited block,
   `# >>> TC-report-coverage-publish-cas … # <<< TC-report-coverage-publish-cas`, with the
   import inside the delimiters (`F-A3R1-13`). It calls `install_reports(app)` with **no**
   context, so a deployment that wires none gets `500 INTERNAL` rather than a router that
   invents a database or writes its own tag service. `report.build` and `report.publish` are
   **not** routed: both are `transport: internal`, and publishing them would open the edge
   `FE-13` exists to forbid. No other card's block was touched.
2. **No `server/app/report/__init__.py`.** `server/app/analysis/`, `server/app/embedding/` and
   `server/app/saved/` have none either; the subpackage loads as a namespace portion and the
   card's §3 table lists four files, so a fifth was not added.
3. **The four modules are exactly card §3.** The package's shared primitives (the `ReportError`
   envelope, ULID/timestamp helpers, the JCS canonicaliser) live at the top of `coverage.py`
   under a banner rather than in a fifth `errors.py`, because a fifth file would be outside the
   write set. This is stated in that module's docstring, not hidden.
4. **The Alembic revision** chains onto the head that existed at write time,
   `0009_tc_telegram_unknown_delivery`. `TC-scheduler-lease-claim` branched off the same
   revision concurrently, and **its** worker added `0011_merge_phase4_6_heads`, which names
   `0010_tc_report_coverage_publish_cas` and `0010_tc_scheduler_lease_claim` as its two
   parents. That merge revision is **not** in this card's write set and was not authored here;
   it is recorded because it changes the graph this card's tests run on. Re-verified at
   handoff: `ScriptDirectory.get_heads()` returns exactly one head
   (`0011_merge_phase4_6_heads`), asserted structurally (`len(heads) == 1`) and never against a
   literal, and the standing gate
   `tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head` passes.
   All 38 of this card's tests were re-run **after** the merge landed and still pass.
5. **`evidence/index.json` was NOT written.** Card §13 asks for the run to be registered there,
   but that file is outside the dispatch's write set (and is one of the PC09 files SG-PC09
   deliberately leaves unpinned). Registration of
   `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` is left to whoever
   holds that file's lease. Flagged rather than done quietly.

### 1.2 Tables: what was created, what was taken over, what was left alone

| Table | Action | Note |
| --- | --- | --- |
| `report` | CREATE | `ENT-report` in full, including `ck_report_abort_reason` and `ck_report_selection_version_published` transcribed from `entities.yaml` `checks` |
| `report_item` | CREATE | `target_key` is the **domain-written** form + a CHECK that it agrees, not a generated column — see §4 |
| `emerging_direction` | CREATE | `ENT-emerging-direction` |
| `coverage_window` | CREATE | plus `ux_coverage_window_bootstrap`, see §4 |
| `pending_item_ledger` | CREATE | **custodian** for `TC-backfill-pending-ledger`: §4.5 item 6 writes it inside the publish transaction, so the publisher cannot work without it |
| `backfill_ledger` | CREATE | **custodian** for `TC-backfill-pending-ledger`: §4.5 item 7 writes `consumed_in_report_id` inside the same transaction |
| `first_announced_ledger` | **REBUILD** | taken over from `0002b_shared_move_set_tables` (`CR-TC-IDENTITY-13`); the rebuild adds the deferred `first_report_id -> report(id)` foreign key and nothing else. There is no second `CREATE TABLE` in the graph — the old one is dropped in the same revision that replaces it |
| `delivery` | **NOT touched** | `delivery.report_id`'s deferred FK (`CR-TC-DELIVERY-08`) would be a rebuild of **another module's** table. The dispatch says "if it is a rebuild of your own table only, else CR" — so it is `CR-TC-REPORT-10` below, not a silent rebuild |
| `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version`, `settings`, `run` | **NOT created** | they belong to `MOD-tag-service`, `MOD-settings-service` and `MOD-job-service`. See `CR-TC-REPORT-01` |

**W4B, read this:** `pending_item_ledger` and `backfill_ledger` already exist and are
`entities.yaml` column-for-column. **EXTEND** them (a later revision, or a rebuild) — do not
issue a second `CREATE TABLE`. That is the `F-A3R1-01` rule, repeated here for the same reason
`0002b` repeated it for this card.

---

## 2. What was built, against which contract row

| Contract row | Where it lives | How it is measured |
| --- | --- | --- |
| §4.2 / §4.9 O-4.1 contiguity on **both** axes | `coverage.plan_next_window`, `coverage.contiguity_violations` | `test_three_periods_with_an_empty_one_in_the_middle_have_no_gap`, `test_the_loser_rebuilds_and_the_two_windows_are_contiguous` — `window_from[n] == window_to[n-1]` **and** `ingest_sequence_from[n] == ingest_sequence_to[n-1]` |
| §4.3 watermark boundary | `coverage.CommittedRowsWatermark` behind `IngestWatermarkPort` | see `CR-TC-REPORT-03`: the "allocated but uncommitted" half of the rule has no entity behind it |
| §4.4 coverage advances **only** at the publish commit | `publisher._publish_period` / `_publish_empty_period` — the only two `insert_window` call sites | `test_a_tag_edit_between_build_and_cas_aborts_the_build`, `test_a_refused_write_advances_nothing_and_consumes_no_backfill`: `COUNT(coverage_window) == 0` after each abort |
| §4.5 one transaction for all ten rows | one `engine.begin()` in `_publish_period` (the commit point, named in the docstring) | the fault-injection test: refuse the write mid-transaction, and **nothing** survives |
| §4.6 CAS, exactly one winner | `ux_coverage_window_predecessor` (the arbiter) + `_assert_predecessor` (the message) | `test_two_publishers_on_one_predecessor_leave_exactly_one_window`: 1 window, 1 published, 1 `aborted/cas_conflict`, **0** `report_item` for the loser, **0** backfill consumed |
| §4.7 / T-RP-07 empty period | `_publish_empty_period` | `test_an_empty_period_writes_coverage_but_no_report_and_no_intent`: coverage row with `report_id IS NULL`, `abort_reason='empty_period'`, delivery port **never called** |
| §4.7.1 empty-period replay receipt | `_replay` case (1)/(2) | `test_replaying_an_empty_period_returns_the_receipt`: no second window, **not** `CONFLICT` |
| `publish_cas.idempotency_rule_vi` (4 cases) | `_replay` | `test_replaying_a_committed_publish_returns_the_same_report`, `test_reviving_an_aborted_build_is_refused`, `test_publishing_a_build_that_was_never_opened_is_not_found` |
| §3.3 tag freeze at the publish transaction (B01/AMD-B01) | `_check_tag_and_generation` calls `tag.freeze_config_version` | `test_a_published_report_keeps_its_hash_when_the_tag_set_changes` (fixture `c` / O-3.2) |
| §5 / I12 generation pinned, mixing blocked **before** commit | `builder._subject_vectors`, `_label_vectors` (guard before scoring) + CAS check 3 | `test_the_generation_guard_blocks_before_the_publish_commit`: `COUNT(published)` unmoved, 0 coverage rows, `ledger.cross_generation_performed == 0` |
| §7.1 total order, §7.2 limit ⇒ pending | `builder._order_candidates`, `_classify` | `publisher._read_model_sort_key` reproduces it on the read path; the byte-identical round trip is the proof |
| §7.3 / B17 quality rule | `_check_quality_rule`, `_quality_of` | `complete` is **computed**, never accepted from the caller, so "complete with pending items" is not representable |
| §8.1/§8.2 first announcement, no republication | `builder._effective_first_announcement`, `publisher._write_first_announcements` | forced `prior_reference` on the read side, `ux_first_announced_canonical_work` on the write side |
| §8.3 density, deterministic, no AI | `builder._emerging_directions` | fixed-radius neighbourhoods + total seed order; zero provider calls anywhere in the package |
| §8.4 `insufficient_evidence` is required, not an error | `builder._insufficient` | `test_a_cold_start_reports_insufficient_evidence_rather_than_a_direction` |
| I05 immutability | `content_hash = sha256(JCS(read model))`, computed in the transaction and rebuilt from rows on read | `test_the_rebuilt_read_model_is_byte_identical`, `test_the_content_hash_covers_the_object_without_covering_itself` |
| `report.schema.json` | `publisher._assemble_read_model` / `read_model` | 18 assertions in `tests/contract/test_report_schema.py`, including the negative ones |
| R5-01 / SG-DENY | `publisher._require_caller` | `FORBIDDEN_EDGE` with `forbidden_edge_ref = "FE-13"` for `MOD-analysis-worker`; **not** `UNAUTHORIZED` |

### 2.1 The three predicates PC03 asked this package for

`contracts/state/report.yaml` `ownership_boundary.interface_contract_vi` requires three
side-effect-free booleans. All three exist and are pure:

* `coverage.coverage_predecessor_matches(connection, owner_id=…, expected_predecessor_id=…)`
* `tag_config_version_matches` — delegated to the port's `freeze_config_version`, which is the
  operation that *is* the freeze point; the publisher maps its `TAG_VERSION_STALE` to
  `abort_reason = 'tag_version_stale'`
* `embedding_generation_matches` — W3C's
  `EmbeddingService.embedding_generation_matches`, called for real, not reimplemented

### 2.2 Real integrations (siblings that had landed)

* **`server.app.embedding`** — `pin_generation`, `embedding_generation_matches`, `cosine`,
  `Vector`, `ComparisonLedger`, `assert_comparable`. Every similarity in this package goes
  through W3C's guarded `cosine`, so "zero cross-generation comparisons" is instrumented
  rather than argued.
* **`server.app.analysis`** — `builder.ServiceAnalysisEnqueue` adapts `analysis.enqueue_tasks`
  and computes `source_fingerprint` from committed rows via `analysis.key`. It takes
  `prompt_version`/`schema_version` with **no defaults**: those belong to `contracts/ai/`
  (PC06), outside this card's read set, and a guessed value would change the analysis key —
  the one component whose stability makes REQ-AC06's "tag edit ⇒ provider call delta 0" true.
* **`server.app.delivery`** — `publisher.PublishedDigestPort` implements W5C's
  `ReportPayloadPort` from the stored read model, and `DeliveryIntentPort` is called **with the
  publish transaction's own connection** (the outbox pattern). The end-to-end wiring of the two
  is **NOT_RUN** in this card's tests; see §5 and `CR-TC-REPORT-09`.
* **`server.app.identity`** — the §8.3 merge hook already exists in `identity/service.py`
  (`_apply_first_announced`), so this card reads the effective ledger row rather than
  duplicating the policy.
* **`server.app.storage`** / **`server.app.db.faults`** — `StorageGuardPort` is accepted from
  the caller; the E2 tests use the real `WriteFaultInjector`.

---

## 3. Verification

Runtime: Python 3.12.3, pytest 8.4.2, ruff 0.6.9, mypy 1.20.2, SQLAlchemy 2.0.52, alembic
1.19.2, jsonschema 4.26.0. `PYTHONDONTWRITEBYTECODE=1`. No network.

| Command (card §8) | Exit | Result |
| --- | --- | --- |
| `python -m pytest tests/contract/test_report_schema.py -q` | 0 | **18 passed** |
| `python -m pytest tests/integration/test_publish_cas.py -q` | 0 | **11 passed** |
| `python -m pytest tests/integration/test_coverage_contiguous.py -q` | 0 | **9 passed** |
| `python -m ruff check server/app/report … server/app/main.py` | 0 | All checks passed |
| `python -m mypy --strict server/app/report` | 0 | Success: no issues found in 4 source files |
| `python -m pytest` (whole repo) | 1 | **882 passed, 9 xfailed, 0 failed, 18 errors**; re-run after two sibling packets of the wave landed: **907 passed, 9 xfailed, 0 failed, 18 errors**. Zero failures in either run; every error is `CR-TC-REPORT-09` |

Evidence manifest: `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json`,
validated against `evidence/manifest.schema.json` (0 errors). `review_type: SELF_VALIDATION`,
`result: PASS`, `evidence_level: E2`.

**Nothing here is an independent audit.** E3 (live) and E4 (is the content useful?) are
`NOT_RUN` and out of card scope.

---

## 4. Two schema decisions that are mine, and why

**`ux_coverage_window_bootstrap`, an index the contract implies but does not name.**
`entities.yaml` declares `UNIQUE(owner_id, predecessor_window_id)` and §4.9 O-4.1 additionally
requires `#coverage_window[predecessor_window_id IS NULL] = 1`. In SQLite two NULLs are
*distinct* for a UNIQUE index, so the declared index alone would let two bootstrap windows
exist side by side — the CAS failing one row earlier than anyone would look.
`ux_coverage_window_bootstrap` (partial, `WHERE predecessor_window_id IS NULL`) closes it. It
adds **no** constraint the contract does not already state; it makes the stated one
enforceable. `test_the_ledger_never_has_two_bootstrap_windows` is the assertion.

**`report_item.target_key` is domain-written, not generated.** `entities.yaml` §target_union
allows either. The domain-written form was chosen for two reasons: a published item's
`target_key` is frozen (I05, I17 — a merge explicitly does *not* rewrite it) and a generated
column would silently follow any later edit of `target_work_id`; and `analysis_generation` in
`0006_tc_analysis_once_per_generation` already sets this precedent. A CHECK makes disagreement
impossible. This also keeps
`tests/contract/test_schema_matches_entities.py::test_generated_columns_are_visible_to_this_check`
— another card's assertion, which hard-codes the three tables that have generated `target_key`
— true without editing it.

---

## 5. Unresolved / NOT_RUN

1. **`run.status` / `run.outcome` (§4.5 item 10) are NOT written.** `ENT-run` has no table
   (W6A owns it, same wave). `RunOutcomePort` is the seam; when it is absent the publish still
   commits everything this module owns. Recorded as NOT_RUN, not as done.
2. **`delivery.create_intent` end-to-end is NOT_RUN.** The adapter and the port exist and the
   connection is threaded correctly, but the coverage test uses a recording double so that
   "an empty period creates **no** intent" is measured by the port never being reached. The
   real two-module path is blocked behind `CR-TC-REPORT-09`.
3. **Fixture `m` (§8.7 density worked example) is NOT_RUN end to end.** It carries
   `given`/`computation`/`expected` but no `events`, so it is not executable through the
   builder the way `g` and `d` are. The density algorithm is implemented in full; oracles
   O-8.1/O-8.2/O-8.3 are NOT_RUN. A dedicated packet could drive it directly.
4. **Fixtures `b`, `e`, `j`, `k`** (analysis reuse, late discovery, backfill add→remove→re-add,
   builder crash not consuming backfill) belong to `TC-backfill-pending-ledger` (§11 of that
   card). This card proves only the negative half — no consumption on CAS loss or refused write.
5. **`evidence/index.json` registration** — see §1.1 note 5.
6. **`contracts/http/openapi.yaml` still declares `claim_ceiling: DRAFT_FOR_REVIEW`** (card §9,
   re-checked with `grep -h claim_ceiling`). The card's claim therefore cannot exceed
   `IMPLEMENTATION_VERIFIED`, and this self-validation record cannot exceed `CONTRACT_READY`.

---

## 6. Completion claim

**Claim:** the four operations `report.build`, `report.publish`, `report.list`, `report.get`
are implemented against `contracts/reporting/{selection,time-and-tags}.md`,
`contracts/state/report.yaml` and `contracts/schemas/report.schema.json`, and the card's §8
oracles pass on a database built by the real migrations.

* **Baseline:** spec `d35e1f2d…`, plan `f65bb046…`, pin epoch `PC10-PIN-P3b-20260908`
  (34/34 verified), implementation revision = the working tree on `main` `fb3944a` plus the
  files in §1.
* **Requirements covered:** REQ-D23, D27, D28 (negative half), D29, D53, D54, D57, REQ-AC05,
  AC08, AC09, REQ-CTAG. **Invariants:** I05, I06, I07, I12, I13.
* **Evidence manifest:** `EV-E1-01-tc-report-coverage-publish-cas`.
* **Observed:** 38 tests pass across the card's three files; ruff and `mypy --strict` clean;
  one Alembic head.
* **Not established:** `MOD-tag-service` (no table, no card); live Telegram/AI/X; the density
  worked example end to end; the backfill consumption *positive* path; `run` row effects;
  that `0.8000` separates signal from noise (REQ-A2, still `uncalibrated`); that the density
  parameters are right (REQ-A4). **This is not an independent audit.**
* **Open issues:** the ten `CR-TC-REPORT-nn` below.
* **Review type:** `SELF_VALIDATION`.

---

## 7. Change requests

| ID | To | Content |
| --- | --- | --- |
| `CR-TC-REPORT-01` | PC01/PC02 + Coordinator | **No card in the 19 creates `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version` or `settings`.** `MOD-tag-service` and `MOD-settings-service` have no implementation card, yet `report.build` consumes `tag.get_active_config_version` / `tag.freeze_config_version` and `selection.md` §6/§7.2 read four `settings['reporting.*']` keys. Consequence here: `report.tag_config_version_id` and `backfill_ledger.tag_id` carry **no** `REFERENCES` clause (the `0002b` precedent — a clause naming a missing table breaks every INSERT under SQLite), the tag service is a `TagConfigVersionPort`, and the settings are an injected `SelectionSettings` with the contract's values as defaults. Requested: a card (or an amendment naming the owner) for the tag and settings tables, after which the two FKs can be added. |
| `CR-TC-REPORT-02` | PC04 | **§4.3 rule 3 and `CHECK (window_to > window_from)` can contradict each other.** When every item of a non-empty period shares the millisecond on which the previous period ended, `window_to := discovered_at(W)` equals `window_from` and the row is rejected. Resolved here by the smallest rule that keeps both §4.2 and the CHECK true — push the *label* forward by exactly 1 ms; membership is unaffected because it is decided on the sequence axis. Requested: state the rule in `time-and-tags.md` §4.3 (or reject this one and say what to do instead). |
| `CR-TC-REPORT-03` | PC02 | **§4.3 rule 1's watermark is not computable from committed state.** "A sequence allocated but not yet committed blocks the watermark there" needs a record of an allocation that has not committed, and no entity has one. `CommittedRowsWatermark` answers with the highest committed sequence and exposes `outstanding_floor` for a deployment that grows a real allocator; `IngestWatermarkPort` is the seam. Requested: either an allocation record on the ingest side, or a note in §4.3 that the committed maximum is the intended reading. |
| `CR-TC-REPORT-04` | W3C / PC04 | **`server/app/embedding/generation.py::cosine` rounds with `round()` (half-to-even); `selection.md` §3 requires half-up to 4 dp.** Impact is confined to exact ties, which binary floats rarely produce — but §3's stated purpose is that two machines select the same set, and "rarely" is not "never". This card's own arithmetic uses `builder.round_half_up` (Decimal, `ROUND_HALF_UP`) and re-rounds every value it gets back from `cosine`. Requested: change the one `round(...)` in the embedding module, or amend §3. |
| `CR-TC-REPORT-05` | PC02 | **`ENT-report` has no column for `coverage_note`, while `report.schema.json` makes it a required and immutable part of the published read model.** Adding a column would put the schema and `entities.yaml` in disagreement (and `test_schema_matches_entities.py` would catch it), so the report-level note is frozen into `report_item.selection_reason` under the reserved key `report_context` — a column whose shape `entities.yaml` explicitly delegates to this package. It is correct and immutable, but redundant across items. Requested: a proper `report.coverage_note` JSON column. |
| `CR-TC-REPORT-06` | PC01 | **Card §4 lists `storage.get_health` under *Consumes*, but `contracts/modules.yaml` has no `MOD-report-service → MOD-data-store` edge** (only `MOD-health-service` and `MOD-job-service` have one). Identical to `CR-TC-embedding-02` and resolved the same way: this module never calls the operation, it accepts a `StorageGuardPort` the caller already holds. Requested: add the edge, or correct the card. |
| `CR-TC-REPORT-07` | PC01 | **`report.list`'s declared 200 schema is `../schemas/report.schema.json`** — the read model of **one** published report — while its own `description` asks for one row per period. A list cannot be a single report object. This router follows the description and answers `{"reports": [...], "next_cursor": …}`. Requested: a `ReportListPage` schema, or a ruling. |
| `CR-TC-REPORT-08` | W3C / Coordinator | **`tests/integration/test_generation_activation.py::test_the_guard_blocks_before_the_publish_commit` imports `server.app.report.service.publish_report`, a module path this card's §3 does not create.** It stays `xfail(strict=True, raises=ModuleNotFoundError)` and therefore still xfails — correctly, but it will never turn green. The claim it makes is proven from this side by `tests/integration/test_publish_cas.py::test_the_generation_guard_blocks_before_the_publish_commit`. Requested: re-point W3C's test at `server.app.report.publisher.publish_report(context, snapshot)` (the test is theirs; this card did not touch it). |
| `CR-TC-REPORT-09` | W5C / Coordinator | **BLOCKING FOR THE WAVE — 18 setup errors.** `tests/integration/test_delivery_unknown_no_retry.py::install_report_stand_in` does `CREATE TABLE IF NOT EXISTS report (id, status, content_hash)` and then inserts three columns. Its own docstring anticipated this card ("if the real migration lands, the `IF NOT EXISTS` makes this a no-op"), but the **INSERT** was not guarded: against the real `ENT-report` it fails `NOT NULL constraint failed: report.owner_id`. 11 tests in that file and 7 in `tests/integration/test_permanent_failure_report_intact.py` now error at setup. Both files are W5C's write set, so this card did not edit them. Suggested fix (one function): seed a real `owner` + `embedding_generation` row and insert the full `ENT-report` row — `owner_id`, `coverage_from`, `coverage_to`, `tag_config_version_id`, `embedding_generation_id`, `report_build_id`, `status='published'`, `quality`, `published_at`, `content_hash`, `selection_version`, `created_at`, `updated_at`. Their `SELECT content_hash FROM report` oracle then runs against the real table, which is what the docstring said it was written for. |
| `CR-TC-REPORT-10` | W5C / PC02 | **`delivery.report_id -> report(id)` (`CR-TC-DELIVERY-08`) is still deferred.** `report` now exists, so the FK can be added — but only by rebuilding `delivery`, a table this card does not own; the dispatch says "if it is a rebuild of your own table only, else CR". Requested: a small revision from the delivery side (or a packet authorising this card to rebuild it). |

---

*`PKT-TC-REPORT` · `worker-W4A` · `lease_released_at` 2026-09-07T21:40Z · ceiling claimed:
`CONTRACT_READY` on this self-validation record, card ceiling `IMPLEMENTATION_VERIFIED`
pending a non-self check · **no item here is an independent audit**.*

---

# ADDENDUM — `PKT-TC-REPORT-FIX1` (lease `LEASE-TC-REPORT-e2`)

| Field | Value |
| --- | --- |
| trigger | Coordinator ruling `CR-TC-BACKFILL-05` (`…/packets/FIX-P4-wave-rulings.md`): `builder._candidates` never unioned the §6.3 widening, so **no deployment could ever spend a backfill entitlement** — the ledger was written and read by tests and by nothing else |
| write set | `server/app/report/builder.py`, `tests/integration/test_coverage_contiguous.py` (the fix), plus `ruff format` on the eight files this card authored (see §A.3). `publisher.py` needed **no** logic change: consumption already read `snapshot.backfill_ledger_ids_applied` inside `TXN-report-publish` |
| status | **`DONE_WITH_CONCERNS`** — the fix is in and proven; the concern is now `STALE_BASELINE` on the pin epoch, not a defect (§A.4) |
| next actor | Coordinator, then **W4B** (their positive path was gated on this) |
| lease_released_at | 2026-09-08T00:58Z |

## A.1 Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/app/report/builder.py` | MODIFY | `c6282d98499db396dc6f7169c690ce190076cc7da8369730b928789ed8363edc` | 81242 |
| `tests/integration/test_coverage_contiguous.py` | MODIFY | `23403f65ab8aa6d902eda1e17eb162688669407a51bd5e7727d47d045df67f06` | 33954 |
| `server/app/report/coverage.py` | MODIFY (format only) | `a4fd8f83052ee8b001fefb037547a759f5f0da1bbfab6cd7126f16f4a2a94e76` | 28224 |
| `server/app/report/publisher.py` | MODIFY (format only) | `55aebf6c82ce975e54745ae509844f95eacb096a98e2f3258361d54e067c3fda` | 60506 |
| `server/app/report/router.py` | MODIFY (format only) | `b4aac67b1071a5b9bacb057049dac832be7f7a98a75b3f28a90b971b90e81514` | 13055 |
| `server/migrations/versions/0010_tc_report_coverage_publish_cas.py` | MODIFY (format only) | `c6b049cac6b95d84614d134f321da3e548185ae3eae42e4b5c5ded9b9869adce` | 23633 |
| `tests/contract/test_report_schema.py` | MODIFY (format only) | `b6eab9211a567b2a3728d8cf39b46e2e183a16c230d6b355c85e1bd69b1cabf8` | 21189 |
| `tests/integration/test_publish_cas.py` | MODIFY (format only) | `631949fcdc7f47410bddaf3975a02e4ec04a94ce55732cd658ee1824bb0f19aa` | 26604 |
| `evidence/runs/…-E1-20260908T005154Z.json` | CREATE | `0c8ab858257321dd4f10ce95ec8aee837fbea49c9d122994bcb8ab857fbbaa02` | 16042 |
| `evidence/runs/…-E1-20260907T212434Z.json` | MODIFY → **`STALE`** | `1a9881cf9f46d9cab0eae0187ad54ddab2092f91315f2aef5be243a2cd296b85` | 13128 |

`server/app/main.py` is unchanged (`73392a3c…`). **No file of another card was touched** —
notably not `server/app/report/backfill.py`, `server/app/report/pending.py`,
`server/app/tags/rescan.py` or W4B's two tests, which is why four files still fail
`ruff format --check` repo-wide (§A.3).

## A.2 The fix

`build_report` takes a new keyword-only `backfill_port`, defaulting to `NoBackfill` — so every
existing caller keeps exactly the old behaviour rather than silently reaching seven days into
the past. `ServiceBackfill` is the real one; it delegates to **W4B's** `plan_extension` and
`entitlements_to_consume` and reads N with their `TableSettings` on the connection the builder
already holds (a second connection would be a second read snapshot, and "how far back may this
period reach" has to be answered on the snapshot the candidates come from). Their file was
imported, never edited.

The widening is unioned by `_union_backfill_candidates`, which queries **only**
`[range.start, window_from)`. The rest of the range is the ordinary period, already covered by
the sequence-axis query, and querying it twice is precisely how one target becomes two rows.
A target already in the candidate set keeps its original entry, so an in-window item is never
re-labelled a backfill find. Attribution walks ranges in `tag_id` byte order, so a target two
entitled tags could both reach is attributed the same way on every run.

**Consumption did not move.** `publisher._consume_backfill` still writes
`entitlement='consumed'` inside `TXN-report-publish`, because §6.4 condition 1 *is* the COMMIT.
What changed is that `BuildSnapshot.backfill_ledger_ids_applied` now comes from W4B's
`entitlements_to_consume(plan, produced_by_extension)` — conditions 2 and 3 answered by the
module that owns them — instead of from a set comprehension over candidate rows that was always
empty. `coverage_note.backfill_applied_tag_ids` (REQ-D28) is now populated for the same reason.

Two tests, and the second is the one a wrong implementation passes without:

* `test_an_entitled_tag_reaches_back_once_and_the_entitlement_is_spent_at_publish` — the D28
  scenario in full: an item is ingested, the pointer passes it without selecting it, and only
  *then* is the tag added. It asserts the item is in the report, **exactly once**, carries
  `selected_via_backfill` + the ledger id, is **not** consumed after `build`, and **is**
  consumed (`consumed_in_report_id = this report`) after `publish`.
* `test_a_widening_that_finds_nothing_does_not_spend_the_entitlement` — fixture `k`'s
  `variant_empty_extension`. Re-reading an empty range costs no AI, so a once-per-lifetime
  grant must not burn on a no-op.

## A.3 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `pytest tests/contract/test_report_schema.py` | 0 | 18 passed |
| `pytest tests/integration/test_publish_cas.py` | 0 | 11 passed |
| `pytest tests/integration/test_coverage_contiguous.py` | 0 | **11 passed** (9 + the 2 above) |
| `ruff check` (card files) | 0 | All checks passed |
| `ruff format --check` (card files) | 0 | clean after formatting the eight files this card authored |
| `mypy --strict server/app/report` | 0 | Success: no issues found in 6 source files |
| `pytest` (whole repo) | 0 | **1021 passed, 7 xfailed, 0 failed, 0 errors** |
| `ScriptDirectory.get_heads()` | — | `['0013_tc_backfill_pending_ledger']`, `len == 1` |

`ruff format` is a repo gate (`Makefile` `lint`, `.pre-commit-config.yaml` `ruff-format`) that
this card's e1 files were failing. Formatting them is a whitespace-only change — the 40 tests
were re-run after it. Four files still fail it repo-wide (`server/app/report/backfill.py`,
`server/app/report/pending.py` → `server/app/tags/rescan.py`, `tests/integration/
test_backfill_once.py`, `tests/integration/test_pending_survives_cursor.py`); they belong to
W4B and were deliberately left alone.

**`CR-TC-REPORT-09` is closed** — W5C replaced the `report` stand-in, and the 18 setup errors
this card's e1 handoff reported are gone. `CR-TC-REPORT-01…08` and `-10` remain open as written.

## A.4 `STALE_BASELINE` — reported, not worked around

SG-HASH at the end of this packet is **32/34**. `precode/baseline.json` and
`precode/decision-register.md` changed bytes *during* this packet: W1n is recording
`OD-20260908-10` into `precode/`, which is the step the ruling's own order schedules
("W1n records OD-10 (precode, single writer) → WP re-pin"). Both files were byte-identical at
this packet's pre-write check, so nothing here was built on the new bytes, and **neither file is
an input to any oracle in this card** — the card reads them only as pin targets.

Consequence, stated rather than absorbed: the card's §0 epoch `PC10-PIN-P3b-20260908` no longer
matches disk, so **WP must re-pin before FC-P4 freezes**, and this card's §0 must carry the new
epoch. The re-issued manifest records the two files at their **run-time** hashes
(`baseline.json` `e8cf3910…`, `decision-register.md` `8d6a87fb…`) rather than the pinned ones,
so the record says what was actually on disk when the commands ran.

---

*`PKT-TC-REPORT-FIX1` · `worker-W4A` · `lease_released_at` 2026-09-08T00:58Z · manifest
`EV-E1-02-tc-report-coverage-publish-cas`; `EV-E1-01-…` marked `STALE` · **no item here is an
independent audit**.*

---

# ADDENDUM 2 — `PKT-TC-REPORT-FIX2` (lease `LEASE-TC-REPORT-e3`)

| Field | Value |
| --- | --- |
| trigger | Audit `F-A3-P4-01` (MEDIUM, `…/audits/A3-P4-R1-report.md`), ruling `…/packets/FIX-A3P4R1-rulings.md`. The underlying defect is **`CR-TC-BACKFILL-09`**, found and declared by **W4B** and captured by them as `xfail(strict=True)` — and **not mentioned anywhere in this card's e1 handoff, which listed REQ-D29 and I07 as covered**. §B.3 corrects that claim |
| write set | `server/app/report/publisher.py`, `tests/integration/test_publish_cas.py`. `builder.py` needed **no** change: the predicate reads `SelectedItem.summary_state`, which the builder already computes |
| status | **`DONE_WITH_CONCERNS`** — defect fixed and independently observed (W4B's strict xfail XPASSed, then they flipped it); the one remaining concern is `STALE_BASELINE` (§B.5), which is WP's re-pin, not a defect |
| next actor | Coordinator (W4B has already flipped the strict xfail; whole repo green — §B.4) |
| lease_released_at | 2026-09-08T01:40Z |

## B.1 The clause

`contracts/reporting/time-and-tags.md` **§5.3, third bullet**:

> *"`item_type` **không** đổi vì việc này: một mục phát hiện muộn chưa từng được công bố vẫn là
> `new_discovery` (§8). 'Phát hiện muộn' là nhãn hiển thị, không phải loại mục."*

read against **§8.2 rule 2**, which is total — a candidate with an effective ledger row *must*
be `prior_reference`, and *"không có nhánh nào cho phép công bố lại như phát hiện mới"*. The two
are simultaneously satisfiable **only if** an item still waiting for its summary is not
announced. Oracle: `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery`
→ `expected.row_oracles[0]` (*"item_type vẫn = 'new_discovery'"*). Requirements: REQ-D29,
REQ-AC09, invariant I07.

The item is **not** hidden while it waits — §7.3 / AMD-B17 put it in `report_item` with
`summary_state = 'pending'` and make the period `quality = 'partial'`. Appearing in a partial
period is simply not the same event as being *announced*, and the open `pending_item_ledger`
row is the durable record of that difference. The deliberate consequence, stated because it is
the non-obvious part: a work can be listed as `new_discovery` in two consecutive periods, once
without a summary and once with one; §5.3 blesses exactly that, and the second appearance
carries `late_discovery = true` so a reader sees why.

## B.2 Changes

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/app/report/publisher.py` | MODIFY | `2b98235d5c7e3fe26578dbbd114f907354a52c839defa9e7faa170a19b71c7dc` | 63042 |
| `tests/integration/test_publish_cas.py` | MODIFY | `9ae53c2ebc1ed7cea790803db006c870cfe4d2827fc74484c472bda889c96a1a` | 34664 |
| `evidence/runs/…-E1-20260908T013343Z.json` | CREATE | `4b4b6a19045f45914a207bf5a78b12a199c59b0b58bc12903c37ec169442271d` | 18402 |
| `evidence/runs/…-E1-20260908T005154Z.json` | MODIFY → **`STALE`** | `df927edd776b6da446764e6222164a91106469f8981a3cd8d66babc62b6f1480` | 13960 |

`builder.py` (`c6282d98…`), `coverage.py`, `router.py`, the migration and the other two test
files are byte-unchanged since Addendum 1. **No file of another card was touched** — in
particular not `tests/integration/test_pending_survives_cursor.py`, whose strict xfail is
W4B's to flip.

The fix is one condition plus the constant it reads, in
`publisher._write_first_announcements`: skip an item whose `summary_state` is not
`SUMMARY_FINAL` (`"present"`). The full argument above lives in that function's docstring, so
the next reader finds it at the line rather than in a handoff.

## B.3 Correcting this card's REQ-D29 / I07 coverage claim

Addendum-less, the e1 handoff §6 listed **REQ-D29** and **I07** among "requirements covered".
That was over-broad: with the defect present, a late discovery came back as `prior_reference`,
which is the exact failure REQ-D29 forbids. What is proven now, and only this:

* **I07** — one canonical work has at most one *effective* `first_announced_ledger` row
  (`ux_first_announced_canonical_work`, plus the publisher writing at most one row per work per
  period). Proven by `test_publish_cas.py`.
* **REQ-D29 / REQ-AC09** — an announced work returns as `prior_reference` **with its date**
  (fixture `h`, `test_a_published_report_keeps_its_hash_…` and `_classify`'s forced type); and a
  work that was never announced — including one that appeared in an earlier period without a
  summary — is still `new_discovery` when it lands (fixture `e`, the two new tests).
* **Still not this card's**: the post-merge branch of I07 (`time-and-tags.md` §8.3) is
  implemented in `identity/service.py::_apply_first_announced` and proven by
  `TC-canonical-identity-merge`; this card only *reads* the effective row. The e1 handoff should
  have said so.

## B.4 Verification

| Command | Exit | Result |
| --- | --- | --- |
| `pytest tests/contract/test_report_schema.py` | 0 | 18 passed |
| `pytest tests/integration/test_publish_cas.py` | 0 | **13 passed** (11 + the 2 below) |
| `pytest tests/integration/test_coverage_contiguous.py` | 0 | 11 passed |
| `ruff check` / `ruff format --check` / `mypy --strict server/app/report` | 0 | clean (8 card files; 6 source files) |
| `pytest` (whole repo) | 1 → 0 | **1030 passed, 5 xfailed, 1 failed** at 01:33Z, then **1042 passed, 3 xfailed, 0 failed, 0 errors** at 01:50Z once W4B flipped their marker — see below |

New tests, and why there are two:

* `test_a_pending_item_is_not_announced_and_is_announced_once_when_its_summary_lands` — both
  halves of the transition. "Not announced while pending" alone would pass for an
  implementation that never announces anything; "announced when the summary lands" alone would
  pass for the buggy one.
* `test_an_item_that_stays_pending_across_two_periods_is_still_not_announced` — the condition is
  the **summary**, not the wait. Without it, a fix that merely *delayed* the announcement by one
  period would pass.

**Mutation-checked, not self-confirming**: deleting exactly the one line
`if item.summary_state != SUMMARY_FINAL: continue` makes **both** new tests fail; restoring it
makes them pass.

The single whole-repo failure is
`tests/integration/test_pending_survives_cursor.py::test_fixture_e_the_late_discovery_is_still_a_new_discovery`
reporting **`XPASS(strict)`** with reason *"CR-TC-BACKFILL-09: publisher._write_first_announcements
announces an item whose summary_state is still 'pending'…"*. That is the marker doing its job:
W4B wrote it so it would fire the day the defect was fixed, and it has. It is their file, so
flipping it to a plain passing test is theirs — which is the order the ruling sets, and which is
also independent confirmation that this fix is real rather than asserted by its own author.
**W4B has since flipped it**: `tests/integration/test_pending_survives_cursor.py` is 29 passed,
and the whole repo is green. Both observations are recorded in the manifest, because the XPASS
is the evidence and the green run is only the tidy-up.

## B.5 `STALE_BASELINE` — unchanged in kind, larger by one

SG-HASH is now **31/34**: `precode/baseline.json`, `precode/decision-register.md` and
`precode/adr/ADR-0011-frameworks-and-toolchain.md`. All three are W1n's scheduled precode edits
(OD-20260908-10, and the ADR-0011 amendment the ruling orders for `F-A3-P4-02`), batched before
**WP's re-pin to P4b**. None is an input to any oracle here; the card's §0 epoch
`PC10-PIN-P3b-20260908` must be re-pinned before FC-P4 e2 freezes. The re-issued manifest
records all three at their run-time hashes.

---

*`PKT-TC-REPORT-FIX2` · `worker-W4A` · `lease_released_at` 2026-09-08T01:40Z · manifest
`EV-E1-03-tc-report-coverage-publish-cas`; `EV-E1-02-…` marked `STALE` · **no item here is an
independent audit** — the independent signal is W4B's XPASS, which is theirs, not mine.*
