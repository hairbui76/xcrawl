# HANDOFF — `TC-analysis-adapter-validation`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ADAPTER` — card `agent-tasks/TC-analysis-adapter-validation.md` (Phase 3, M3, gate G5) |
| worker principal | `worker-W3A` |
| authority_id | `AUTH-COORD-TC-ADAPTER` (parent `AUTH-OWNER-20260908-06` / `-09`; records `precode/owner-decisions-06.md`, `packets/OWNER-DECISIONS-20260908-08.md`) |
| lease_id | `LEASE-TC-ADAPTER-e1` (exclusive on card §3 write set + handoff + evidence manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED` for the API path and the JSON-extraction path; **`CONTRACT_READY`** for the CLI/ACP path, exactly as the card's §9 caps it. AC-16 is reported **`BLOCKED`**, never `FAIL`. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T19:40Z (host clock; see §5 on the clock/calendar difference) |

`DONE_WITH_CONCERNS` rather than `DONE` for one reason, and it is a scope reason, not a
defect: the card's §13 asks that the run be registered in `evidence/index.json`, and that
file is **not** in the write set the dispatch packet grants (card §3 + migration + handoff +
evidence manifest). It was not touched. Registration is a Coordinator action or a separate
packet — see `CR-TC-adapter-05`.

---

## 0. Wait gate and baseline

The packet's wait gate was honoured before the first byte was written:

* `agent-tasks/README.md` declares pin epoch **`PC10-PIN-P3-20260908`** (line 124);
* `evidence/handoffs/PC10-handoff.md` carries the **`PKT-PC10-FIX24`** addendum with
  `lease_released_at 2026-09-08T00:45Z` (line 3269);
* SG-HASH re-run against disk immediately before the first write: **32 pinned rows in the
  card's §0, 0 mismatches.** The card's own epoch line reads `PC10-PIN-P3-20260908`, and
  `grep -ho 'Pin epoch: \`PC10-PIN-[A-Za-z0-9-]*\`' agent-tasks/TC-*.md | sort -u` resolves
  to that single current name.

No file under `contracts/`, `acceptance/`, `precode/` or `agent-tasks/` was modified.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `worker/app/adapter/base.py` | CREATE | ABSENT | `82d3a8966ffcea511a94eb30003d4a56028580c083d2d2441278ac7c4988d48f` | 33040 |
| `worker/app/adapter/api_provider.py` | CREATE | ABSENT | `bb562111361b6abc50848a2f85cc5d89c280b3c9028eef09d76af0140e755ebf` | 11215 |
| `worker/app/adapter/cli_acp.py` | CREATE | ABSENT | `6865a0991d6c9117cdca1fcf4adc423ad2dadd0d8cbc44505baa9555ddadf1d9` | 9664 |
| `worker/app/adapter/extract_json.py` | CREATE | ABSENT | `3be004606f2781f2d24a7ae90b8116c45ea3db73f6f3f3e83cac7ee5d405b38e` | 9928 |
| `worker/app/adapter/validate.py` | CREATE | ABSENT | `b6f108c65d08a632d952f17bcedbd34997d594a42682807569fe902c827f36e9` | 18350 |
| `tests/contract/test_analysis_result_schema.py` | CREATE | ABSENT | `ee7fe412474223b78a62b05d4cb38704da76641d7f0fdf57dc0597e3601a6f61` | 24611 |
| `tests/integration/test_injection_canary.py` | CREATE | ABSENT | `4b43ba08efe2142da67f66c2578690853c4eeeaef7466612dda8984a4e4316ec` | 32533 |
| `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json` | CREATE | ABSENT | (see §6) | — |
| `evidence/handoffs/TC-analysis-adapter-validation-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.**

### 1.1 Write-set notes

1. **No Alembic revision.** This card owns no entity. `contracts/data/entities.yaml` assigns
   no table to `MOD-ai-adapter`, the card's §4 says "Adapter **không** ghi state", and
   `contracts/modules.yaml` gives the module `data_owner_of: []`. Adding a migration would
   have created a table nothing writes to. The chain is untouched and still resolves to one
   head.
2. **No `server/app/main.py` include block.** Both operations are `transport: internal`
   (`contracts/ports.yaml`) and the module runs inside the worker process on the personal
   machine, not in the server app. There is no route to register.
3. **No `worker/app/adapter/__init__.py`.** The card's §3 table lists five modules and no
   package marker, and the write set is "card §3 exactly". `worker/app/` is a regular
   package, so `worker/app/adapter/` loads as an implicit namespace portion; imports and
   `mypy --strict` (with `namespace_packages = true`) are both clean over it. Same choice as
   `TC-research-connector-metadata`.

---

## 2. What was built, and why it is shaped this way

### 2.1 The refusals are the feature

`contracts/ai/grounding.md` §5.2 is explicit that the real defence is architecture, not
prompt wording, and that each layer must have a **countable** oracle. The package is built
around that: every guarantee is a counter a test reads, not a sentence a reviewer trusts.

| Guarantee | Where it is enforced | Oracle asserted |
| --- | --- | --- |
| ISO-01 — no tools | `TOOL_DEFINITIONS_REGISTERED = 0` is a constant, and `ProviderRequest.tools` is always `()`; the adapter raises if a request ever carries one | `tool_definitions_registered == 0`, `tool_calls_executed == 0` with `tool_requests_seen == 3` |
| ISO-02 — filesystem | no code path in the package opens a file outside the working dir | `files_read_outside_working_dir == 0` (structural, **not** a syscall observation — see §5) |
| ISO-03 — egress | `_require_allowed_endpoint` compares the destination host to the entry's allowlist *before* the transport is touched; the destination is built from configuration only, so content cannot reach it | `outbound_hosts == [provider host]`, `refused_hosts == ["evil.example"]`, `provider_calls == []` on refusal |
| ISO-04 — Telegram | `outbound_operations: []`: there is no counter Telegram could increment because there is no path | `telegram_calls == 0`; SC49 rows FE-16…FE-19 read from the sweep fixture |
| ISO-05 — credential scope | a credential whose `task_id` differs is refused; a missing one is `AI_PROVIDER_UNAVAILABLE`. Both before the socket | `transport.seen == []`, `credentials_received == 0` |
| I14 — usage | `UsageReport.__post_init__` refuses `unknown=True` with any non-null field | schema also refuses it; both asserted |
| I11 — redaction | `AdapterError` filters `details_safe` against `contracts/errors.yaml` `details_safe_keys` and rejects non-scalar values, so there is **no key a transcript could travel under** | canary count 0 in payload, envelope, `str(exc)` and captured log |

### 2.2 Both registered adapters refuse to dispatch

`load_registered_adapters()` reads `contracts/ai/providers.yaml` §2.1 as data. Both entries
(`anthropic@claude-sonnet-5`, `anthropic@claude-opus-5`) come back `enabled: false` with
`refusal_reason_code = isolation_unverified`, and `run_inference_task` raises
`CAPABILITY_DENIED` **before** the transport, the credential or any host is touched. The
test that proves it loads the real contract, not a copy — so there is no configuration of
this package that makes a live provider call, which is the packet's "no live AI calls"
constraint held structurally rather than by discipline.

The refusal names the right blocker. Terms are *signed* (`OD-20260908-08`); what holds the
entries is isolation (B13). Reporting one as the other would send a reader to re-read a
licence that is already read, so `dispatchable` keeps the three gates independent and
`refusal_reason_code` reports the one that actually failed.

### 2.3 AC-16 is `BLOCKED`

`ac16_status()` returns `BLOCKED` while no CLI adapter is dispatchable, and there is no
branch that returns `FAIL`. ADR-0010 §Hệ quả, `providers.yaml` §4 `ac16_reporting_rule_vi`
and fixture (k)'s forbidden effects all require the distinction: the zero-API-key path was
not tried and found wanting, it was not permitted to run.

### 2.4 The adapter never retries

`contracts/ai/tasks.yaml` §1 `split_rule_vi`: the whole budget sits at the task layer so
that `COUNT(analysis_attempt)` is a direct count of model calls. Three dispatches against an
unavailable provider produce exactly three transport calls, asserted per iteration. And a
second provider is not merely un-called but unreachable — its host is outside the entry's
allowlist, so even a caller who decided to fail over is refused before the socket. That is
what `fallback default: off` has to mean in code.

### 2.5 JSON extraction refuses rather than chooses

Three methods (`native_json`, `fenced_block`, `delimited_envelope`), all deterministic, all
refusing on more than one candidate. `delimited_envelope` is the CLI default because a fence
is a string an attacker can write and a per-run nonce is not; `assert_nonce_absent_from_sources`
raises rather than warns if the nonce ever appears in source text, since the correct response
is a new nonce, not a cautious proceed. Malformed JSON is never repaired.

### 2.6 Boundary with `TC-analysis-once-per-generation` (worker-W3B)

Both packages landed in this wave and **neither imports the other**, deliberately.
`contracts/modules.yaml` permits `MOD-analysis-worker -> MOD-ai-adapter` and nothing else;
`MOD-analysis-service` is not a permitted caller, so a shared type would have to sit on one
side of a forbidden edge. W3B defined its own `SecretPort` / `AdapterCallCounter` protocols
and left `secret.issue_task_credential` out of its own module on the same reasoning
(`server/app/analysis/service.py` line 325).

The two meet structurally instead: `CallAudit.calls` has the shape W3B's
`AdapterCallCounter` protocol asks for, so `MOD-analysis-worker` — which is a permitted
caller of both — can hand this audit across without an import. That is asserted in
`test_provider_unavailable_calls_no_second_provider_and_reports_unknown_usage`.

---

## 3. Verification

| Command | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/contract/test_analysis_result_schema.py tests/integration/test_injection_canary.py -p no:warnings` | **47 passed**, 0 failed, 0 xfail — exit 0 |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:warnings` (full suite) | **795 passed, 10 xfailed**, 0 failed — exit 0 |
| `PYTHONDONTWRITEBYTECODE=1 uv run ruff check worker/app/adapter tests/contract/test_analysis_result_schema.py tests/integration/test_injection_canary.py` | All checks passed |
| `PYTHONDONTWRITEBYTECODE=1 MYPYPATH=.:shared/rr_contracts uv run mypy --strict --namespace-packages --explicit-package-bases --disable-error-code=import-untyped worker/app/adapter` | Success: no issues found in 5 source files |

Split: 33 in `tests/contract/test_analysis_result_schema.py` (11 of them the parametrised
sweep over the whole `acceptance/fixtures/ai/` directory), 14 in
`tests/integration/test_injection_canary.py`.

**On the `mypy` flag.** `--disable-error-code=import-untyped` is there for two third-party
packages that ship no stubs, `yaml` and `jsonschema`, not for anything in this package. The
repo's configured strict gate is `files = ["server/app"]` and adding `types-PyYAML` /
`types-jsonschema` would mean editing `pyproject.toml`, which is outside this write set. See
`CR-TC-adapter-06`.

**On the full suite.** Two earlier runs in this session reported 2–4 failures in
`tests/contract/test_saved_snapshot_schema.py` and
`tests/integration/test_snapshot_survives_delete.py` — worker-W5B's write set, being written
concurrently. The run recorded above is after those stabilised. No run at any point failed
in either of this card's two files, and neither of them imports anything from a sibling
card's package.

### 3.1 What each fixture proved

| Fixture | Verdict it declares | What the test asserts |
| --- | --- | --- |
| `a`, `b`, `f`, `g`, `j`, `k` | `accept` | 0 schema errors on every payload |
| `d` | `reject_schema` | ≥1 error **at the predicted pointer** `/result/statements/0/citation_refs`; the second variant passes the schema and fails SV-03 |
| `c`, `e` | `reject_semantic` | **0 schema errors**, then SV-02 with `validation_failure_kind = citation_unknown_source` |
| `h`, `i` | `not_applicable` | no payload is present to validate |
| `g` (negative variant) | `reject_extraction` | two candidates ⇒ `multiple_json_candidates`, neither first nor last taken |

The `reject_semantic` branch asserts the *absence* of schema errors as carefully as the
presence of semantic ones. README §3.3 makes that the point of the whole split: a fixture
claiming the semantic layer is necessary must not be catchable by the schema, or `EV-PC06-01`
fails because the fixture is overstating that layer.

---

## 4. Change requests

| ID | Severity | Finding |
| --- | --- | --- |
| `CR-TC-adapter-01` | medium | **Card §4 "Consumes: `secret.issue_task_credential`" contradicts `contracts/modules.yaml`.** That file gives `MOD-ai-adapter` `outbound_operations: []`, and `contracts/ports.yaml` names `MOD-analysis-worker` as the operation's only caller. Code follows the contracts: the adapter *receives* a credential through a port the worker satisfies and calls no operation — which is also how the card's own §3 puts it ("đường API, **nhận** credential per-task ngắn hạn"). Requesting a ruling on the card's §4 wording. |
| `CR-TC-adapter-02` | low | **`validation_failure_kind` has no closed enum.** `contracts/errors.yaml` permits the key without listing values; `tasks.yaml` §4 supplies seven (all names of *semantic* checks) and `providers.yaml` §3 adds `multiple_json_candidates`. There is no contract name for "the schema itself refused", while fixture (d) variant 1 labels a schema failure `unsupported_claim_kind` — the semantic name of the same defect. The adapter reports `schema_invalid` for that layer rather than borrowing a semantic name. A closed enum in `errors.yaml` would settle it. |
| `CR-TC-adapter-03` | low | **Fixture count mismatch.** Card §3 says `tests/contract/test_analysis_result_schema.py` covers "9 fixture ai/*"; §2's read set names eight JSON files plus the README; the directory holds eleven (`a`…`k`) and `acceptance/fixtures/ai/README.md` §1 tabulates all eleven. The test drives all eleven — three of them (`a`, `i`, `j`) are the positive controls for I04/I14/I16 that the card does not pin. Requesting that §0/§2/§3 be reconciled to eleven. |
| `CR-TC-adapter-04` | low | **`acceptance/scenarios.yaml` SC11 says `claim_kind='source_verified'`** while `analysis-result.schema.json` names the field `statements[].kind`. Naming only — the rule referenced (SV-03) is the same — but a checker matching field names would not find `claim_kind`. |
| `CR-TC-adapter-05` | low | **`evidence/index.json` registration.** Card §13 requires the run to be registered there; the dispatch packet's write set does not include that file and it is being touched concurrently by other cards in this wave. Not written. Needs a Coordinator action or a packet that owns the file. (`TC-telegram-linking-auth`'s run from the same wave is also unregistered.) |
| `CR-TC-adapter-06` | low | **No type stubs for `yaml` / `jsonschema`.** The strict-mypy command needs `--disable-error-code=import-untyped`. Adding `types-PyYAML` and `types-jsonschema` to the root `[dependency-groups] dev` would remove the flag; `pyproject.toml` is outside this write set. |

No contract, fixture or expectation was edited. Where a contract and a card disagreed
(`CR-TC-adapter-01`), the contract was followed and the disagreement is reported.

---

## 5. Not established

Stated plainly, because the counters above are easy to over-read:

* **No isolation was verified.** E3 is `NOT_RUN` and this packet was forbidden from running
  it. Every row of `contracts/ops/cli-acp-probe.md` §3 — T-ISO, T-JSON-01, T-TIME, T-CONC,
  T-USAGE, T-TASK — remains `NOT_RUN`. What is verified is the adapter's *decisions*: it
  refuses to dispatch, refuses an endpoint outside the allowlist, registers no tool and
  executes none. `isolation.* = unverified` still stands in `providers.yaml` §2.1 and both
  Anthropic entries stay `enabled: false`.
* **ISO-02 is structural, not measured.** `files_read_outside_working_dir` is a counter no
  code path in this package can increment, and the canary check is "the string appears zero
  times", not a syscall observation. T-ISO-02's real form — a canary file outside the working
  directory and an observed `open()` — needs a probe run.
* **ISO-05 is half-covered.** The adapter's half (a mismatched or missing credential costs
  zero provider calls) is asserted. The other half —
  `secret.issue_task_credential` refusing a worker that does not hold the lease — lives in
  `MOD-secret-service` / `MOD-analysis-service` (`verify_task_lease`, card
  `TC-analysis-once-per-generation`) and is not reachable from here.
* **SC28 and SC51 were not run.** Both are card §8 anchors and both sit outside the adapter:
  SC28 in the task lifecycle, SC51 in Settings. `AI_ATTEMPT_UNCERTAIN` has its code and its
  `details_safe_keys` in `base.py` but no test emits it — `NOT_RUN`.
* **SC49 is covered for 4 of 36 edges** (FE-16…FE-19, the ones touching this module), and
  covered by reading the sweep fixture plus asserting that no code path exists for those
  edges — not by making a call and receiving a code.
* **Self-reference.** The recorded provider bodies and CLI transcripts were written by this
  same worker, alongside the extractor and validator that read them. Their agreement shows
  internal consistency, not that a real provider emits that shape. Only E3 closes that gap.
* **Timeouts are `PROVISIONAL`.** The tests assert the code takes the contract's numbers, not
  that 120 / 300 / 180 s are right.
* **E2 does not apply** — the adapter writes no state and does not touch SQLite (FE-18).
  **E4** (`grounding.md` §6 rubric) is `NOT_RUN`: there is no real report period yet.
* **Clock.** The host clock reads `2026-09-07` while the dispatch packet and the
  `PKT-PC10-FIX24` addendum are dated `2026-09-08`. Every timestamp here and in the evidence
  record is the host clock's, recorded as-is rather than adjusted.
* **This is `SELF_VALIDATION`.** No independent audit was run, and nothing in this document
  should be read as one.

---

## 6. Evidence

* **Manifest:** `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json`
* **Manifest ID:** `EVM-TC-analysis-adapter-validation` (record `evidence_id`
  `EV-E1-01-tc-analysis-adapter-validation`, constrained by the schema's id pattern)
* Validates clean against `evidence/manifest.schema.json` (0 errors, Draft 2020-12 with the
  format checker on).
* `baseline.contract_hashes` is copied verbatim from the card's §0 after the SG-HASH re-run,
  plus the four unpinned PC09 files and the three unpinned `ai/` fixtures the tests read.
* The card's §0 epoch name `PC10-PIN-P3-20260908` is recorded in `inputs.protocol_version`,
  because `evidence/manifest.schema.json` types `baseline.candidate_epoch` as an **integer**
  and the epoch is a name.
* No secret, canary or transcript appears in the manifest, in this handoff, or in any test
  output: the canary is generated per test and lives only in `os.environ`.

---

*`PKT-TC-ADAPTER` · worker-W3A · `lease_released_at` 2026-09-07T19:40Z · claim ceiling
`IMPLEMENTATION_VERIFIED` for the API and JSON-extraction paths, `CONTRACT_READY` for
CLI/ACP · REQ-AC16 `BLOCKED` · `SELF_VALIDATION`, no independent audit.*

---

# ADDENDUM — `PKT-TC-ADAPTER-FIX1` (post-audit A3-P3-R1)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-ADAPTER-FIX1` |
| worker principal | `worker-W3A` |
| authority_id | `AUTH-COORD-TC-ADAPTER` (parent `AUTH-OWNER-20260908-10`; rulings `…/scratchpad/packets/FIX-A3P3R1-rulings.md`) |
| lease_id | `LEASE-TC-ADAPTER-e2` (fencing 2) — card §3 files + this handoff + a re-issued manifest |
| findings addressed | `F-A3-P3-01` (MEDIUM, CI-red) and `F-A3-P3-03` (LOW), both `OPEN → FIX_PROPOSED` |
| status | **`DONE`** |
| completion_claim | unchanged: `IMPLEMENTATION_VERIFIED` for the API and JSON-extraction paths, `CONTRACT_READY` for CLI/ACP, REQ-AC16 `BLOCKED`. Neither finding was a behaviour defect and no claim moves. |
| next actor | Coordinator (re-freeze `FC-P3` epoch 2, then A3-P3-R2) |
| lease_released_at | 2026-09-07T20:25Z (host clock) |

**Baseline.** SG-HASH re-run against disk before the first FIX1 write: **32 pinned rows,
0 mismatches**, at epoch **`PC10-PIN-P3b-20260908`** — the card was re-pinned between `e1`
and `e2` and its §0 now carries that name. Nothing under `contracts/`, `acceptance/`,
`precode/` or `agent-tasks/` was touched in this packet either.

## A.1 `F-A3-P3-01` — the formatter

The finding is accurate and the attribution is exact. I ran `ruff check` (lint) and recorded
it as "ruff clean"; I never ran `ruff format --check`, which is a **separate required step**
of `.github/workflows/python.yml:38` and `Makefile:33`. Lint being clean says nothing about
formatting, and the two are easy to conflate — eleven peer handoffs record both, mine
recorded one. As frozen, those four files would have turned CI red.

`ruff format` was run on exactly the four files the report names. The changes are whitespace
and line-wrapping only: no identifier, string, assertion or control-flow construct moved, and
the 47 tests that existed before the reformat produced the same 47 passes after it.

`ruff format --check .` is now in the recorded verification set (§A.4) — the omission was in
the command list, so the fix belongs there too, not only in the working tree.

## A.2 `F-A3-P3-03` — the two silent fixtures

Both were exercisable in one step, so neither is recorded `NOT_RUN` as a whole.

**`acceptance/fixtures/ai/g-cli-json-embedded-in-prose.json`** —
`test_fixture_g_prose_transcript_and_its_negative_variant`. The fixture was in fact already
reaching the parametrised sweep through `ALL_AI_FIXTURES` (which loads the whole directory),
so its `accept` payload was validated; what was missing was any reference by *name*, which a
grep-based audit cannot distinguish from "never exercised" — a fair reading, and the reason
the new test names it. It now drives both halves: the prose-with-nonce transcript extracts to
exactly the fixture's payload and passes the schema, and the `negative_variant` refuses with
its declared `validation_failure_kind` and `error_code` **read out of the fixture**, not
restated in the test.

**`acceptance/fixtures/recovery/f-secret-canary-injection.json`** —
`test_recovery_f_canary_stays_out_of_every_place_the_fixture_names`. It is the CLI-path twin
of `ai/b`: same injection, but on the family where `secret_ref` is NULL, so its sharpest
expectation is `secret_issue_task_credential_called: false` — which the adapter satisfies by
having no path that asks for one, not by declining. Six of its `expected` keys and four of
its `forbidden_effects` are asserted, including that no destination names the link-local
metadata address `169.254.169.254` and that the CLI transcript never reaches a log.

Two things about it are recorded rather than claimed:

* **`expected.canary_in_analysis_row` is `NOT_RUN` for this card.** The adapter writes no
  state and cannot touch SQLite (FE-18, card §4), so there is no `analysis` row here to grep.
  That key belongs to `TC-analysis-once-per-generation`.
* The fixture's `given.canary_vi` quotes a literal `CANARY-8f3a-DO-NOT-EMIT`. It is a
  placeholder committed to a public repo, so it is not used as the secret; the real canary is
  generated per test. Both strings are asserted absent, which is strictly stronger than
  checking only the one in the file.

## A.3 Changes — before / after

| Path | Operation | Before (sha256, bytes) | After (sha256, bytes) |
| --- | --- | --- | --- |
| `worker/app/adapter/api_provider.py` | MODIFY (format only) | `bb562111361b6abc50848a2f85cc5d89c280b3c9028eef09d76af0140e755ebf`, 11215 | `a59ed47c035e245d55ba06113cabd49121238289536f9b2c71da7e7d3d324914`, 11207 |
| `worker/app/adapter/validate.py` | MODIFY (format only) | `b6f108c65d08a632d952f17bcedbd34997d594a42682807569fe902c827f36e9`, 18350 | `96ee0ec78401f290228e13f5510a90a5a46c82b00c1b25df459841cfe30e519e`, 18313 |
| `tests/contract/test_analysis_result_schema.py` | MODIFY (format + one new test) | `ee7fe412474223b78a62b05d4cb38704da76641d7f0fdf57dc0597e3601a6f61`, 24611 | `d6c94a8eb3224b37acb663071423bc9b86ae4f8142ce5c45b8fbb2d2aa99b6ee`, 26799 |
| `tests/integration/test_injection_canary.py` | MODIFY (format + one new test) | `4b43ba08efe2142da67f66c2578690853c4eeeaef7466612dda8984a4e4316ec`, 32533 | `be68bcf1ba767bdfc09983426431d1a50a8bc0c6ebf1bfffbf73d0eae3f973ea`, 37203 |
| `worker/app/adapter/base.py` | unchanged | `82d3a8966ffcea511a94eb30003d4a56028580c083d2d2441278ac7c4988d48f`, 33040 | (same) |
| `worker/app/adapter/cli_acp.py` | unchanged | `6865a0991d6c9117cdca1fcf4adc423ad2dadd0d8cbc44505baa9555ddadf1d9`, 9664 | (same) |
| `worker/app/adapter/extract_json.py` | unchanged | `3be004606f2781f2d24a7ae90b8116c45ea3db73f6f3f3e83cac7ee5d405b38e`, 9928 | (same) |
| `evidence/runs/…-E1-20260907T193158Z.json` | MODIFY (`result` → `STALE` + `stale_reason`) | `0e17503877106a9f8d0e9f082dfa191ba17a7a5d0366c9646b2357f03bfbf9eb` | `6a3464323e8f52113e30c59a46fe6633be63b9241fd5c8b6e0a26752f7369c58` |
| `evidence/runs/…-E1-20260907T201840Z.json` | CREATE | ABSENT | `372320cd92a5fb85c08e9a9185515af7a65c66e12001d0e42cb2d4ec7410a4c5`, 25934 |
| `evidence/handoffs/TC-analysis-adapter-validation-handoff.md` | MODIFY (this addendum) | `d4c40d60a29ca05232e05358f2258d7d69698f65383213333c516a53ee28d40e` | (this file) |

The superseded manifest was **not deleted**: its `result` is now `STALE` and `stale_reason`
names both findings, the four moved files and the epoch change. Its observations remain true
of the bytes it names, and are kept for trace.

## A.4 Verification (re-run in full)

| Command | Result |
| --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 uv run ruff format --check .` | **134 files already formatted** — rc=0 *(the step that was missing; now recorded)* |
| `PYTHONDONTWRITEBYTECODE=1 uv run ruff check worker/app/adapter tests/contract/test_analysis_result_schema.py tests/integration/test_injection_canary.py` | All checks passed! |
| `PYTHONDONTWRITEBYTECODE=1 MYPYPATH=.:shared/rr_contracts uv run mypy --strict --namespace-packages --explicit-package-bases --disable-error-code=import-untyped worker/app/adapter` | Success: no issues found in 5 source files |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/contract/test_analysis_result_schema.py tests/integration/test_injection_canary.py -p no:warnings` | **49 passed**, 0 failed, 0 xfail — exit 0 (was 47; +2 from `F-A3-P3-03`) |
| `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:warnings` (full suite) | 822 passed, 9 xfailed, **2 failed** — both in `tests/integration/test_concurrent_save.py` and `tests/integration/test_multipart_partial_receipt.py`, i.e. the two tests ruling `F-A3-P3-02` hands to W5A → W5C to convert from xfail, mid-sequence. Neither file is this card's, and neither imports from `worker/app/adapter/`. |

Split: 34 contract, 15 integration.

## A.5 One new change request

| ID | Severity | Finding |
| --- | --- | --- |
| `CR-TC-adapter-07` | low | `acceptance/fixtures/recovery/f-secret-canary-injection.json` writes `given.task.task_type = "open_labeling"`. Ruling R-03 makes `contracts/data/entities.yaml` authoritative and the value is `label`; `contracts/ai/tasks.yaml` §0 `alias_map` records `open_labeling` as the pre-FIX3 `ports.yaml` spelling, already converged there (`CR-PC03-05`). The fixture kept the old name. The new test reads the fixture's `expected` keys and its `provider_auth_family`, not its `task_type`, so nothing depends on the stale spelling — but a checker matching task types against the enum would reject this file. Not corrected here: `acceptance/` is read-only to this card. |

`CR-TC-adapter-01` … `-06` from the `e1` handoff are unchanged and still open. `CR-TC-adapter-05`
(the `evidence/index.json` registration the card's §13 asks for) now covers **two** run
records, the STALE one and the re-issued one.

## A.6 Not established — unchanged, plus one

Everything in §5 of the `e1` handoff still holds: E3 `NOT_RUN`, isolation unverified, both
Anthropic adapters `enabled: false`, AC-16 `BLOCKED`, ISO-02 structural rather than measured,
ISO-05 half-covered, SC28/SC51 not run, SC49 at 4 of 36 edges, transports and CLI runners
fake. Added by this packet:

* `recovery/f`'s "0 outbound requests outside the provider endpoint" is counted at the
  adapter's **decision** layer (`audit.outbound_hosts` / `refused_hosts`), not at a socket.
  On the CLI path there is no endpoint at all, so the count is empty rather than
  "attempted and blocked". A socket-level proof is still E3.
* This remains `SELF_VALIDATION`. The audit that produced `F-A3-P3-01` and `F-A3-P3-03` was
  independent; this response to it is not, and nothing here closes either finding — that is
  A3-P3-R2's call on `FC-P3` epoch 2.

---

*`PKT-TC-ADAPTER-FIX1` · worker-W3A · `lease_released_at` 2026-09-07T20:25Z · claim unchanged
· `F-A3-P3-01` and `F-A3-P3-03` `FIX_PROPOSED`, neither closed by me · `SELF_VALIDATION`.*
