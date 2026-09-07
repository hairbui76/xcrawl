# HANDOFF — `TC-research-connector-metadata`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-RESEARCH` — card `agent-tasks/TC-research-connector-metadata.md` (Phase 2B, M2) |
| worker principal | `worker-WN` |
| authority_id | `AUTH-COORD-TC-RESEARCH` (parent `AUTH-OWNER-20260907-04`, record `OD-20260907-03`) |
| lease_id | `LEASE-TC-RESEARCH-e1` (exclusive on card §3 write set + migration + handoff + evidence manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED` for this card's scope only, as the card's own front-matter qualifies it: E1 with recorded responses, and the **module** `MOD-research-connector` is **not** `CONTRACT_READY` because REQ-A6 is unresolved. The evidence schema caps a `SELF_VALIDATION` record below that label, so the manifest asserts no `claim` block at all rather than one it may not carry. |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T14:05Z |

Status is `DONE_WITH_CONCERNS`, not `DONE`, for one reason: the Alembic revision this card
is required to add moves the migration head from `0004_merge_phase1_heads` to
`0005_tc_research_connector_metadata`, and
`tests/integration/test_identity_merge_audit.py::test_migration_chain_resolves_to_a_single_head`
asserts that head by **literal id**. The property that test names — exactly one head — still
holds; only the pinned string is stale. That file is another card's write set, so it was not
touched. See `CR-TC-research-01`.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/research/service.py` | CREATE | ABSENT | `6e57c4362e19668f024550382837405747091ee37513533fb231935f748b525a` | 51939 |
| `server/app/research/client_arxiv.py` | CREATE | ABSENT | `761f67819be24ab2e6b7bb381ac4081b5a537e3306db4b2e4e9951c808def742` | 6429 |
| `server/app/research/client_openalex.py` | CREATE | ABSENT | `50173772f7d39d33e453e293a7de2968bdd441960806725fc5160fb661184960` | 5849 |
| `server/app/research/repository.py` | CREATE | ABSENT | `78a0d9b3085728fe5b4d071f6466e9d1facd60a0ff7e695c996412a26469f77b` | 6060 |
| `server/app/research/router.py` | CREATE | ABSENT | `a56d7216fcd6e584d159256ea2a91fd809c4e3689077fdd682740b25d2b1fe11` | 7497 |
| `server/migrations/versions/0005_tc_research_connector_metadata.py` | CREATE | ABSENT | `7ce06bc521a1ff322e2e886bb5b9c0136c4bcf99a28c0570f469455765502f50` | 4218 |
| `tests/contract/test_research_metadata_fixtures.py` | CREATE | ABSENT | `603872b44a7c62a46c7cad06a240a3e74a7adb3ef7952604cfb43a3605946d8d` | 28441 |
| `tests/integration/test_research_connector_health.py` | CREATE | ABSENT | `64f9ddf56889410723c3e2af3703465b5c704c8a7786d7a3517435db0a89e825` | 27617 |
| `evidence/runs/TC-research-connector-metadata-E1-20260907T135805Z.json` | CREATE | ABSENT | `8fddf8556988dd19c0879e68a95153e8da18e91eb69b73686c549923a4271660` | 13069 |
| `evidence/handoffs/TC-research-connector-metadata-handoff.md` | CREATE | ABSENT | (this file) | — |

**Nothing else was written.** No file under `contracts/`, `acceptance/`, `precode/` or
`agent-tasks/` was modified, and `server/app/main.py` was **not** touched.

### 1.1 Write-set notes

1. **No `server/app/research/__init__.py`.** The card's §3 table lists five modules and no
   package marker, and the write set is "card §3 exactly". `server/app/` is a regular
   package, so `server/app/research/` loads as an implicit namespace portion; the import
   `server.app.research.service` was verified to work before any code was written, and
   `mypy --strict` (which runs with `namespace_packages = true`) is clean over it. This is a
   deliberate difference from `TC-storage-write-blocked-readiness`, which declared two
   `__init__.py` files as deviations. If the Coordinator prefers the convention, adding the
   marker is a one-line packet — it is not needed for the code to run.
2. **The Alembic revision** is authorised by Phase 1/2 dispatch rule 2 ("plus the Alembic
   migration(s) your entities need … one revision per card, named after the card"). It
   creates exactly one table, `source_fetch_log`, the one entity
   `contracts/data/entities.yaml` assigns to `MOD-research-connector`.
3. **No route was registered.** `contracts/ports.yaml` types both operations
   `transport: internal`; `server/app/research/router.py` attaches a port object and adds no
   path. A test asserts that `install_research` changes `app.routes` by zero entries.

---

## 2. Source baselines

`sha256sum` was run over every row of the card's §0 pin table **before** the first line of
code and again immediately before this handoff. Both times: **27/27 match**, no drift.

| Path | SHA-256 |
| --- | --- |
| `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` |
| `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` |
| `contracts/data/entities.yaml` | `c61be0a4f8dc5884e82bf1ed79c86f0c38da3d0f6aa41e96205c1089f900a4fc` |
| `contracts/ops/collector-probe.md` | `03e88010ce8d9a8e7ed7afbb5ab01caf4099ac77cde1298fb155731dddd55ca1` |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` |

The full 27-row table, plus the PC09-owned files that §0 deliberately leaves unpinned
(`acceptance/scenarios.yaml` `ca372775e943c49776ae853615bad275054773f8808eab12aa085651ca07ea17`,
`evidence/manifest.schema.json` `25ddb1b7afb529b0ca9500fa2f293897723406a704a25d71b0c0ed187607dfd8`),
is reproduced in `baseline.contract_hashes` of the evidence manifest.

`acceptance/scenarios.yaml` was read before coding, as `SG-PC09` requires. SC07, SC11, SC23,
SC29, SC30 and SC49 were compared against the card's §8 oracle: **no contradiction found**,
so no CR was raised on that ground.

---

## 3. What was built

### 3.1 The refusal is the feature

`contracts/retry-policy.yaml` `research_connector_rate_limit` has four `null` values with
status `PLACEHOLDER_KC`. `contracts/ops/collector-probe.md` §9.2 adds a fifth unresolved
fact, the contact identity OpenAlex requires. The card's `SG-A6` and `SG-IDENT` forbid
guessing any of them.

The connector therefore **reads every rate and identity value from configuration and refuses
to run when any is missing**:

* `ConnectorSettings()` — what a deployment that wires nothing gets — has both sources
  unconfigured. `SourceConfig.require_configured()` raises `ConnectorNotConfigured` naming
  the missing facts.
* `research.fetch_work_metadata` translates that refusal into
  `SOURCE_METADATA_UNAVAILABLE` with `attempt_number = 0` **before a URL is even built**, so
  the item degrades to `post_only` and the run is not blocked (CN-5, `T-RUN-03`). Measured:
  zero requests, zero `source_fetch_log` rows, zero entries in the boundary journal.
* `research.get_connector_health` reports `unavailable` with
  `reason_code = configuration_incomplete` and lists the unresolved facts by name.

`min_interval_ms = 3000` is carried as a self-imposed floor and is labelled as such in the
health payload (`min_interval_ms_status: PROVISIONAL_SELF_IMPOSED_FLOOR`). It is never used
as a stand-in for a documented rate.

`test_the_four_unresolved_facts_are_exactly_the_ones_the_contract_leaves_null` reads the four
`null` keys **out of `contracts/retry-policy.yaml` at run time** and asserts they are a subset
of what the connector reports as missing. The dependency runs the right way: filling a value
into the contract fails the test until the connector is given it, and giving the connector a
number the contract does not have fails it too.

### 3.2 No vendor fact is hard-coded

Host allowlist, endpoint template, contact-identity parameter name and value, and every rate
number are `SourceConfig` fields. `CR-PC05-03` records that **neither pinned source document
contains a documentation URL** for either API, so a path or a parameter name written into the
code would have been a guess wearing an implementation's clothes.
`test_no_rate_number_is_hard_coded_anywhere_in_the_package` parses the package for a literal
assigned to `requests_per_window` or `window_seconds` and fails if it finds one — that is
card §12's second reviewer question, answered by machine.

The **response parsers** are the one place a wire shape is assumed (Atom for arXiv, JSON for
OpenAlex). That is a real limitation and it is recorded as such in §7.

### 3.3 The network boundary

`contracts/ops/internet-boundary.md` §3.2, implemented in `inspect_url` / `GuardedSession`
and exercised rather than asserted: `https` only; host allowlist (an allow list, never a
block list); DNS resolved and **every** returned address checked, with a mixed answer
refusing the whole name rather than filtering it; redirects followed manually with the full
rule set re-applied at each hop, capped at 3; connect/total timeouts; response bytes counted
as they stream and cut off at the cap; no credentials in a URL.

`acceptance/fixtures/recovery/g-ssrf-redirect-private.json` is the oracle for the redirect
case. Its chain ends at `http://127.0.0.1:8080/admin`; the test asserts the refusal lands at
the fixture's pinned `blocked_at_redirect_step = 3`, that the fixture's
`connections_to_loopback`/`connections_to_private_ranges` of `0` are what the journal
observed, and — as the fixture's own note demands — that **both** independent rules fired
(`scheme_not_allowed` and `host_not_in_allowlist`), not just the first.

### 3.4 Provenance

One `source_fetch_log` row per outbound call, **including failed ones** (card §6: a call that
leaves no trace cannot be audited for pacing). `endpoint` is redacted by dropping every query
value, so the contact identity — the one scoped secret this module holds — cannot reach the
log, while the request that actually went out still carries it. `response_hash` is the join
`contracts/data/identity.md` §7 specifies for `identity_alias.evidence_ref`, and a test
asserts the returned provenance and the stored row agree on it.

A transport timeout is recorded as `timeout_unknown`, never `error` (`RP-01`): an unknown
outcome is a different fact from an observed failure.

---

## 4. Verification

All commands were run from `/mnt/virtual/repo/xcrawl` with `PYTHONDONTWRITEBYTECODE=1`.
**No command in this packet touched the network** other than `uv`'s own package resolution
against the existing lockfile.

| # | Command | Result |
| --- | --- | --- |
| V1 | `uv run pytest tests/contract/test_research_metadata_fixtures.py tests/integration/test_research_connector_health.py -p no:warnings` | **56 tests, 0 failures, 0 errors, 0 skipped**, exit 0 |
| V2 | `uv run pytest -p no:warnings` (whole workspace) | **576 tests, 1 failure, 0 errors, 4 xfail**; the single failure is `CR-TC-research-01` below |
| V3 | `uv run ruff check .` | `All checks passed!`, exit 0 |
| V4 | `uv run ruff format --check .` | `87 files already formatted`, exit 0 |
| V5 | `uv run mypy` (`--strict` over `server/app`) | `Success: no issues found in 30 source files`, exit 0 |
| V6 | `uv run python shared/rr_contracts/generate.py --check` | `generated tree matches a fresh run of the generator`, exit 0 |
| V7 | `uv run python evidence/tools/verify_cards.py --repo .` | 13 checks over **19** cards, 13 PASS, 0 FAIL, 3420 assertions, 0 violations, exit 0 |
| V8 | `uv run openapi-spec-validator contracts/http/openapi.yaml` | `OK`, exit 0 |
| V9 | `uv run python evidence/tools/e0_check.py --repo .` | 25 checks, 24 PASS / **1 FAIL** — `E0-12-forbidden-strings`, 1 violation in `precode/owner-decision-request.md`. **Pre-existing and not this card's**: that file was not touched, and the violation is a bare `IMPLEMENTATION_VERIFIED` in its prose |
| V10 | `jsonschema Draft202012Validator` on the manifest against `evidence/manifest.schema.json` | `VALID` |

### 4.1 What the 56 tests measure

Counts and pinned strings, not log reading:

* **SC29 / `identity/b`** — `referenced_links` is empty ⇒ **0 outbound requests**; and every
  un-normalised string (`arXiv:…`, a URL, `…v1`, prose, an upper-case DOI) is refused with
  `VALIDATION_ERROR` at the constructor, before a transport exists. A `landing_url`,
  `openalex` or `pmid` scheme cannot be used as a lookup key at all (`NC-07`, I11).
* **SC07 / `identity/h`** — the fixture's six raw spellings normalise to exactly one base, so
  the source is asked **once**; and a before/after row count of every table shows
  `source_fetch_log` is the only one that changed (`DC-RC-03`).
* **SC30 / `identity/g`** — `canonical_arxiv_base` equals the fixture's expected
  `work.canonical_arxiv_id` (`2503.03333`) with `version_label = "v2"` reported separately;
  the fixture's forbidden effect "Ghi `'2503.03333v2'` vào `work.canonical_arxiv_id`" is
  asserted as a string read out of the fixture.
* **SC11 / `collection/h`** — the expected code is read from the fixture's own
  `warnings[0].code`. Two attempts (`research_connector_attempts = 2`), two log rows,
  `COUNT(work) = 0`, and the error envelope contains no host and no guessed identifier.
* **SC39 / `recovery/g`** — the SSRF case described in §3.3.
* **SC49 / `boundary/a`** — rows 20 and 21 are the only two of the 36 that name this module;
  their `expected_error_code` (`CAPABILITY_DENIED`) is read from the fixture. `FE-20` is
  exercised through the allowlist, `FE-21` through an AST scan of the package's imports.
* **Edges** — `MOD-x-collector` calling either operation is `FORBIDDEN_EDGE` through the
  shared `require_edge`, with zero outbound calls; `MOD-ingest-service` and
  `MOD-health-service` are accepted.
* **Pacing** — a fake clock shows the floor is actually waited for, is **per source**, and
  that a source's `Retry-After` beats the configured value and is never shortened.

---

## 5. Card checklist

| Card item | State | Where |
| --- | --- | --- |
| §3 write set — five `server/app/research/*` modules | DONE | §1 |
| §3 write set — two test files | DONE | §1 |
| §4 produces `research.fetch_work_metadata` | DONE | `service.fetch_work_metadata`, `router.ResearchConnector` |
| §4 produces `research.get_connector_health` | DONE | `service.get_connector_health` |
| §4 consumes nothing | DONE | the package imports no other domain service; `require_edge` is a shared boundary helper, not an operation call |
| §4 one `source_fetch_log` row per outbound call, nothing else written | DONE | `repository.py`, migration `0005`, before/after row-count test |
| §5 callers restricted to ingest / health | DONE | `router.py`, two `FORBIDDEN_EDGE` tests |
| §5 host + scheme allowlist, no arbitrary URL from model or content | DONE | §3.3, `normalized_identifier` |
| §6 I03 / I11 / I13 | DONE | no guessed identifier; no model-chosen URL; `degraded` is a return value and "not observed yet" is never reported as `ok` |
| §6 failed calls are logged too | DONE | error / `timeout_unknown` / `rate_limited` / `not_found` paths all log |
| §7 six error codes with the contract's `details_safe_keys` | DONE | `DETAILS_SAFE_KEYS` refuses an unknown key at construction |
| §8 four fixtures + recorded responses | DONE | §4.1 |
| §8 `e0_check.py` | RUN | V9 — 1 pre-existing FAIL not from this card |
| §8 no network command | DONE | `httpx.MockTransport` everywhere; resolver is a dict |
| §10 `SG-A6` — refuse rather than guess | DONE | §3.1 |
| §10 `SG-IDENT` — no contact identity ⇒ no OpenAlex call | DONE | `test_openalex_without_a_contact_identity_is_never_called` |
| §10 `SG-LIVE` — no live call | DONE | no test opens a socket |
| §10 `SG-DOC` — no invented documentation URL | DONE | §3.2 |
| §10 `SG-HASH` | DONE | §2, run twice |
| §10 `SG-PC09` | DONE | §2 |
| §10 `SG-DENY` | DONE | §4.1, SC49 row |
| §13 evidence manifest, schema-valid | DONE | V10 |
| §13 register the run in `evidence/index.json` | **NOT DONE** | that file is outside the write set — see `CR-TC-research-04` |

---

## 6. Evidence records

| id | type | result | note |
| --- | --- | --- | --- |
| `EV-E1-05-tc-research-connector-metadata` | `SELF_VALIDATION`, E1 | PASS | `evidence/runs/TC-research-connector-metadata-E1-20260907T135805Z.json`; validates against `evidence/manifest.schema.json` |

The manifest carries **no `claim` block**. `evidence/manifest.schema.json` caps a
`SELF_VALIDATION` record at `CONTRACT_READY`, and the label this card's scope reaches is
higher than that; asserting a label the schema permits but the work does not support would be
worse than asserting none. Raising the label is an independent reviewer's decision, not this
worker's. Nothing in this packet is an independent audit.

The manifest's sha256 in §1 was computed after the manifest was closed and before this file
was written, so it is the value on disk; this handoff is the only file whose hash §1 cannot
carry, for the obvious reason.

---

## 7. Limitations — what this packet does **not** establish

1. **No live call happened.** E3 is `NOT_RUN` and is forbidden here (`SG-LIVE`). Nothing
   about the real behaviour, availability or rate of arXiv or OpenAlex is established.
2. **The four REQ-A6 facts are still `null`.** `MOD-research-connector` is therefore **not**
   `CONTRACT_READY` (SRC-PLAN §10). This card does not change that and does not claim to.
3. **Self-reference in the recorded responses.** The synthetic bodies were written by the
   same worker as the parsers that read them. Their agreement is evidence of internal
   consistency and of nothing else — it does **not** establish that a real arXiv Atom feed or
   OpenAlex work document has the shape assumed. This is the single largest gap in the
   packet, and only E3 with real responses closes it.
4. **DNS and sockets are simulated.** The resolver is a dictionary and the transport is
   `httpx.MockTransport`. The rule "resolve, check the address, then connect to *that*
   address" is verified at the decision layer; a production transport must still pin the
   checked address at connect time, and **that is not verified here**.
5. **2 of 36 sweep edges.** Only `FE-20` and `FE-21` touch this module.
6. **E2 not run** for the `source_fetch_log` write path (SQLite fault injection).
7. **PROVISIONAL numbers stay provisional.** Redirect cap 3, timeouts 10 s / 30 s, 10 MiB
   cap, attempts 2, backoff 5/30 s are all `PROVISIONAL` in the contracts. The tests assert
   the code *matches* the contract; they do not assert the numbers are right.
8. **Backoff is configured but not slept.** `research_connector_backoff` values are carried
   in `ConnectorSettings.backoff_s` and are **not** applied between attempts — the pacing gate
   is. Applying both would double-count the wait, and the contract does not say which wins.
   See `CR-TC-research-02`.
9. **OpenAlex abstract reconstruction is lossy.** `abstract_inverted_index` does not record
   original whitespace, so the rebuilt text is single-spaced. It re-orders tokens the source
   supplied and invents none.
10. This is `SELF_VALIDATION`. **No independent audit has been run.**

---

## 8. Change requests

**`CR-TC-research-01` — a migration-head assertion pinned to a literal revision id.**
`tests/integration/test_identity_merge_audit.py:1502` asserts
`heads == ["0004_merge_phase1_heads"]`. The property the test's own docstring names is
"`alembic upgrade head` must be unambiguous", and that still holds: `get_heads()` returns
exactly one element, now `0005_tc_research_connector_metadata`. As written the assertion
breaks for **every** future card that adds a revision, which is all of them. Owner:
`TC-canonical-identity-merge` (the file's write set). Suggested change:
`assert len(heads) == 1, heads`. Not made here — that file is outside this lease.

**`CR-TC-research-02` — no contract code covers two connector failure modes.**
(a) The connector's own provenance write (`source_fetch_log`) failing: card §7's table has no
code for it, `STORAGE_WRITE_FAILED` is not listed for `research.*` in
`contracts/errors.yaml`, and swallowing it would leave an alias citing a row that does not
exist. Current behaviour: the driver exception propagates unwrapped, which is loud but
uncoded. (b) `contracts/retry-policy.yaml` defines both `research_connector_backoff` (5 s,
30 s between attempts) and `research_connector_rate_limit.min_interval_ms` (3000 ms between
calls) for the same operation, without saying whether they compose or which governs a retry.
The implementation applies the pacing gate only. Owner: PC03.

**`CR-TC-research-03` — `ports.yaml` and `entities.yaml` read as contradictory.**
`contracts/ports.yaml` gives `research.fetch_work_metadata` `state_effects_vi: "Không ghi."`,
while `contracts/data/entities.yaml` assigns `source_fetch_log` to `MOD-research-connector`
and the card's §4 requires one row per outbound call. The reading taken here — "Không ghi"
scopes to *business* entities (`work`, `work_version`, `identity_alias`), and the connector's
own provenance log is not one — is the only one under which both files can be satisfied, and
it is what the card orders. Requested: make the scope explicit in `ports.yaml` so the next
implementer does not have to reconstruct it. Owner: PC01.

**`CR-TC-research-04` — two files the card needs but does not authorise.**
(a) Card §13 requires "Đăng ký run vào `evidence/index.json`", but that file is not in the
§3 write set and dispatch rule 2 closes the write set. The run is therefore **not**
registered; the Coordinator should either register it or widen a future packet.
(b) `acceptance/fixtures/recovery/g-ssrf-redirect-private.json` is the only oracle in the
repository for the redirect/SSRF rule this card implements, and it is in neither §0 nor §2.
It was read (read-only, permitted) and is used as an oracle, but because it is unpinned a
change to it would silently invalidate this evidence rather than mark the card `STALE`. Its
hash at run time is recorded in the manifest. Requested: pin it in the card's §0 at the next
re-pin. Owner: PC10.

### 8.1 Observations that are **not** change requests

* **`E0-12-forbidden-strings` fails** with one violation in `precode/owner-decision-request.md`
  (a bare claim label in prose). That file was not touched by this packet and the violation
  pre-dates it; reported so nobody reads V9's exit as caused here.
* **`tests/integration/test_collector_resume_after_challenge.py` failed twice during this
  packet**, with a different test each time, and passed in isolation both times and in the
  final full run. That file was created at 20:52 local while this work was in progress —
  Phase 2A's worker is writing it concurrently. Not investigated further: it is another
  card's file and the observation is consistent with a partially written module, not with a
  defect this card introduced.

### 8.2 Provisional decisions introduced

* **`PROV-WN-01`** — "configured but never called" is reported as
  `state: degraded, reason_code: no_observation_yet`. `contracts/ports.yaml` closes the state
  enum at `ok | degraded | unavailable`, so "not observed yet" has to land on one of the
  three; I13 forbids reporting an undetermined state as a good one, which rules out `ok`, and
  `unavailable` would be false. `degraded` plus an explicit reason code is the least wrong of
  the three. If the health contract would rather see a fourth value, that is an amendment,
  not a code change.

---

*`PKT-TC-RESEARCH` · `worker-WN` · `lease_released_at` 2026-09-07T14:05Z · ceiling as the
card's front-matter states it · no item in this handoff is an independent audit.*


---

# ADDENDUM — `PKT-TC-RESEARCH-2` (REQ-A6 resolved; connector activates on contract-derived rates)

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-RESEARCH-2` |
| worker principal | `worker-WN` |
| authority_id | `AUTH-COORD-TC-RESEARCH` (parent `AUTH-OWNER-20260907-04`) |
| lease_id | `LEASE-TC-RESEARCH-e2` (fencing 2) — `server/app/research/*.py`, the two test files, this addendum, one new evidence manifest |
| status | **`DONE`** |
| next actor | Coordinator |
| lease_released_at | 2026-09-07T16:50Z |

## A.1 Why this packet exists

`contracts/retry-policy.yaml` moved to **0.8.0** and resolved all four REQ-A6 facts under a
new status token `DOCS_derived`, each with a URL, a retrieval date of **2026-09-07** and a
verbatim quotation (`sources[]`). Verified before any edit: the file on disk hashes
`f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a`, its
`research_connector_rate_limit.values` contains **no nulls**, and
`evidence/handoffs/PC03-REQA6-handoff.md` exists. The premise of the first packet's central
refusal is therefore genuinely gone — not asserted to be gone.

| Fact | Value now in the contract |
| --- | --- |
| arXiv rate | 1 request / 3 s |
| arXiv concurrency | **1 connection at a time** (a fact the old floor did not cover) |
| OpenAlex rate | 100 requests / 1 s |
| OpenAlex daily budget | stated in **money**, not calls — run-time only, via `X-RateLimit-*` |
| Identification | **neither** source's current documentation requires any |

## A.2 Changes

| Path | Operation | sha256 | Bytes |
| --- | --- | --- | --- |
| `server/app/research/service.py` | MODIFY | `6803804a503e8550922636f287cebe80f77a81c5a9d51cd3ff055a60aa9f849a` | 70134 |
| `server/app/research/client_arxiv.py` | UNCHANGED | `761f67819be24ab2e6b7bb381ac4081b5a537e3306db4b2e4e9951c808def742` | 6429 |
| `server/app/research/client_openalex.py` | UNCHANGED | `50173772f7d39d33e453e293a7de2968bdd441960806725fc5160fb661184960` | 5849 |
| `server/app/research/repository.py` | UNCHANGED | `78a0d9b3085728fe5b4d071f6466e9d1facd60a0ff7e695c996412a26469f77b` | 6060 |
| `server/app/research/router.py` | UNCHANGED | `a56d7216fcd6e584d159256ea2a91fd809c4e3689077fdd682740b25d2b1fe11` | 7497 |
| `server/migrations/versions/0005_tc_research_connector_metadata.py` | UNCHANGED | `7ce06bc521a1ff322e2e886bb5b9c0136c4bcf99a28c0570f469455765502f50` | 4218 |
| `tests/contract/test_research_metadata_fixtures.py` | UNCHANGED | `603872b44a7c62a46c7cad06a240a3e74a7adb3ef7952604cfb43a3605946d8d` | 28441 |
| `tests/integration/test_research_connector_health.py` | MODIFY | `0c26eed1afb7d9979be44cd3d8bb2d063a3173f66498853a080f21419784aab7` | 42985 |
| `evidence/runs/TC-research-connector-metadata-E1-20260907T164354Z.json` | CREATE | `9b5005813551aba2a3e0c3c03dfcd0110b464816a8167d66f0658fb7dd3fe6d8` | 14318 |

`evidence/handoffs/TC-research-connector-metadata-handoff.md` — MODIFY (this addendum
appended; the sections above it are unchanged and remain the record of `PKT-TC-RESEARCH`).

No contract, fixture, card or other card's file was touched.

## A.3 What changed in the code

**1. Shipped defaults now carry the documented rates.** `DEFAULT_ARXIV` / `DEFAULT_OPENALEX`
replace the unconfigured constants as `ConnectorSettings`' defaults, built from
`CONTRACT_ARXIV_RATE_LIMIT` and `CONTRACT_OPENALEX_RATE_LIMIT`. `SG-A6`'s condition — "the
four values are still `null`" — no longer holds, and `missing_req_a6_facts()` is empty for
both sources out of the box.

**2. The floor was not loosened.** `min_interval_ms = 3000` is unchanged and is still the
binding constraint for **both** sources. `SourceConfig.effective_interval_ms` takes the
*stricter* of floor and documented rate: arXiv 3000 (they coincide), OpenAlex 3000 (not the
10 ms its 100 req/s would permit). The contract's `rationale_vi` asks for exactly this, and a
test asserts the OpenAlex number is 3000 and not 10.

**3. New fact modelled: arXiv's single connection.** `SourceRateLimit.max_concurrent_connections`
and `RateGate.connection()` — a context manager spanning exactly the outbound call, with a
`peak_in_flight` counter a test can assert on. Exceeding the ceiling raises
`ConcurrencyLimitExceeded` rather than queueing: a queue would hide a terms breach behind a
delay, and the connector is single-threaded per source by construction, so reaching it is a
caller defect.

**4. OpenAlex's daily budget is read, never guessed.** `read_budget_headers` captures
`X-RateLimit-Limit/Remaining/Credits-Used/Reset` from **every** response (including a 429 —
the one response whose budget headers matter most) and `research.get_connector_health`
reports them. `credits_used` stays a string because the contract states the budget in money.
A reported `remaining = 0` makes the source `unavailable`; an **absent** header leaves
`budget: null`, because unknown is not zero (I13).

**5. Health now separates two kinds of gap.** `unresolved_facts` (REQ-A6 — now empty) and
`missing_configuration` (deployment — endpoint and host). They were one key while both were
empty for the same reason; now that one is resolved and the other is not, one key would hide
which. `reason_code` is `rate_facts_unresolved` or `endpoint_not_configured` accordingly.

## A.4 `SG-IDENT` — what the code actually does today (coordinator's question 3)

Answering factually rather than changing behaviour, as asked.

* The connector **never sent** a `mailto` or a descriptive `User-Agent` of its own. It sends
  `Accept: */*`; the only `User-Agent` on the wire is httpx's default. So there is no
  "identification-friendly behaviour" to preserve or drop, and **none was added** — inventing
  an identifying string on this module's initiative is a new outbound value no contract asked
  for. A comment at the call site now records that and points at the contract.
* What `SG-IDENT` actually was, and is: a **configuration flag**, `SourceConfig.requires_contact_identity`,
  never a hard-coded requirement. The old default set it `True` for OpenAlex on REQ-D34's
  polite-pool assumption; if left alone it would now wrongly refuse OpenAlex forever. The
  shipped default is now `False` for both sources, taken from the contract's `identification`
  block, so the flag no longer blocks anything.
* **The mechanism was not deleted**, because the contract forbids deleting it:
  "`SG-IDENT` KHÔNG được xoá chỉ vì hôm nay nó không kích hoạt." A source configured with
  `requires_contact_identity=True` and no identity is still refused with zero requests, and
  `test_neither_source_requires_identification_today_and_the_rule_survives_anyway` proves
  both halves at once.
* An OpenAlex `api_key`, which the documentation calls optional and worth 10× the daily
  budget, is an Owner decision and a secret (`contracts/ops/secrets.md`). The
  `contact_identity` / `contact_identity_param` mechanism can carry it; nothing here
  configures one.

## A.5 Verification

| # | Command | Result |
| --- | --- | --- |
| W1 | `uv run pytest tests/contract/test_research_metadata_fixtures.py tests/integration/test_research_connector_health.py -p no:warnings` | **66 passed, 0 failed** (was 56; +10 new), exit 0 |
| W2 | `uv run pytest -p no:warnings` | **586 tests, 0 failures, 0 errors, 4 xfail** — the full suite is **green** |
| W3 | `uv run ruff check .` / `ruff format --check .` | clean, 88 files formatted |
| W4 | `uv run mypy` | `Success: no issues found in 30 source files` |
| W5 | `uv run python shared/rr_contracts/generate.py --check` | no diff |
| W6 | `uv run python evidence/tools/e0_check.py --repo .` | **25 checks, 25 PASS, 0 FAIL, 0 violations** (the `E0-12` violation reported in §4 has since been fixed by its owner) |
| W7 | `uv run openapi-spec-validator contracts/http/openapi.yaml` | `OK` |
| W8 | `uv run python evidence/tools/verify_cards.py --repo .` | **12 PASS / 1 FAIL, 60 violations** — all stale §0 pins, on **all 19 cards**, caused by the REQ-A6 packet. See `CR-TC-research-05` |
| W9 | manifest against `evidence/manifest.schema.json` | `VALID` |

`CR-TC-research-01` (the literal migration-head pin) **is resolved**: its owner fixed the
assertion, and `test_migration_chain_resolves_to_a_single_head` now passes with
`0005_tc_research_connector_metadata` as the head.

### The ten new tests

Contract-driven, not restated: every number is read from `contracts/retry-policy.yaml` at run
time and compared against the code, so editing either side alone fails.

* the four values equal the contract's, no null remains, `status == DOCS_derived`, and every
  source shares the one retrieval date;
* neither source requires identification **and** a source that does is still refused;
* the shipped defaults pass `missing_req_a6_facts()` but still fail `missing_deployment_config()`;
* every rate literal in the package lives in `service.py` and equals a contract value;
* OpenAlex's effective interval is 3000 ms, not 10;
* with only an endpoint added — no rate override — a lookup succeeds and health reads `ok`;
* two arXiv lookups are spaced by exactly 3.0 s on a fake clock;
* `peak_in_flight['arxiv_api'] == 1`, and holding two connections raises;
* budget headers are read and surfaced; `remaining = 0` ⇒ `unavailable`, absent ⇒ `null`;
* **regression**: an explicitly nulled/partial rate still refuses, with zero requests and
  `reason_code = rate_facts_unresolved`.

## A.6 Scope-level blockers for `MOD-research-connector`

| Blocker | State |
| --- | --- |
| REQ-A6 — the four rate/identity facts | **CLEARED** (`contracts/retry-policy.yaml` 0.8.0, `DOCS_derived`) |
| `SG-A6` — refuse while values are null | **no longer fires**; mechanism retained and regression-tested |
| `SG-IDENT` — no identity for a source that needs one | **no longer fires**; mechanism retained (contract requires it) |
| API endpoint / host allowlist | **STILL OPEN** — no contract states either API host; deployment configuration, and still a refusal condition (`SG-DOC`) |
| `contracts/ops/collector-probe.md` §9.2 | **STILL SAYS `KC`** — now contradicts retry-policy 0.8.0; `CR-TC-research-06` |
| E3 (live calls) | **NOT_RUN**, and still forbidden by this card (`SG-LIVE`) |
| Card §0 pins | **STALE** for all 19 cards; `CR-TC-research-05` |

The connector is **not** `CONTRACT_READY` on this worker's say-so. The contract's own
`scope_note_vi` is explicit that resolving the four facts does not confer it: that judgement
belongs to PC05 and the Coordinator, over the module's whole port surface.

## A.7 New change requests

**`CR-TC-research-05` — every card's §0 pin is stale.** The REQ-A6 packet changed
`contracts/retry-policy.yaml`, `precode/decision-register.md` and `precode/baseline.json`.
`verify_cards.py` now reports 60 violations across **all 19 cards**, not only this one. Cards
are outside this lease. Owner: PC10 — a repo-wide re-pin.

**`CR-TC-research-06` — `collector-probe.md` §9.2 contradicts `retry-policy.yaml` 0.8.0.**
`contracts/ops/collector-probe.md` is unchanged (`03e88010…`) and still lists all five REQ-A6
rows as `KC`, still says "Tôi chưa đọc hai tài liệu đó", and still concludes the module may
not be `CONTRACT_READY` because the four values are blank. Two contracts now disagree on a
matter of fact. The code follows `retry-policy.yaml`, which carries URLs, dates and
quotations. Owner: PC05.

*`PKT-TC-RESEARCH-2` · `worker-WN` · `lease_released_at` 2026-09-07T16:50Z · `SELF_VALIDATION`
throughout; no item here is an independent audit.*
