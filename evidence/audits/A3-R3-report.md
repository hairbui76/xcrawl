# AUDIT_REPORT `A3-R3` — scoped verification of `F-A3R2-01…04` + PC09 registration (FC-P1 epoch 3)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-R3` · authority `AUTH-COORD-A3-R3` (parent `AUTH-OWNER-20260907-03`) · lease null |
| reviewer | `auditor-A3` — authored nothing in the repo, wrote nothing into it this round. Independent of `AMD-ENT-owner-01`, of PC09-P1 and of the EV-A3 transcripts (§3.2 is a finding *against* records written in my name). |
| candidate | `FC-P1` epoch 3, 395 entries, `manifest_sha256 = 5f5b8aa425219de2621ef0a75a18ff3c6ed00a09b685cf6c13deeceeb12362b4` |
| quiescence | Recomputed at start and end: 395/395 identical, header hash reproduces. `git status --porcelain` 81 before and after. **Not `STALE`.** |
| delta vs epoch 2 | 9 added, 0 removed; exactly **one** code file changed: `tests/contract/test_schema_matches_entities.py`. `web/` 20 files byte-identical to epoch 2, so my epoch-1 web results still hold without re-running. |
| my archived reports | `evidence/audits/A3-R1-report.md` `02c9d541…` and `A3-R2-report.md` `75f2ac45…` — **both byte-identical** to my scratch originals. |

## 1. Regression (packet §5)

`305 passed / 4 xfailed / 0 failed` (45.5 s) — matches the Workers' claim; the +2 over epoch 2
is exactly the two tests added to the schema gate. `ruff` clean · `ruff format` 61 files ·
`mypy --strict` 25 files clean · `generate.py --check` no diff · `openapi-spec-validator` OK ·
`verify_cards.py` **13/13, 3 214 assertions, epoch `PC10-PIN-P1d-20260907`** · `e0_check.py`
**25/25, 0 violations**, `E0-19-generated-matches` present and passing (18 sources) ·
`alembic heads` → `0004_merge_phase1_heads`, one head.

`contracts/` diff vs `da886f8`: `entities.yaml` only. I parsed both versions and compared
entity by entity — the **only** entity whose `fields` or `keys` differ is `owner`, gaining
exactly the four amendment columns. The epoch-2→3 change to that file is therefore
prose-only, as claimed. `acceptance/scenarios.yaml` changed only in scenario `status` /
`status_evidence_refs` / `status_scope_vi`.

## 2. Verification table

| item | verdict | evidence |
| --- | --- | --- |
| `F-A3R2-01` dangling rule citation | **VERIFIED** | `version_rule_vi` now opens by stating the previous citation was wrong, quotes the four §2 rows of `change-control.md` verbatim, and concludes that `failed_login_count` (NOT NULL + constant DEFAULT) falls in a **gap** in §2 — handled as additive on migration evidence, *not* on a rule row — and says explicitly that `entities.yaml`'s own §4 key "KHÔNG phải của `precode/change-control.md`, và nó không tự cấp quyền chọn bậc version". It declares the gap rather than inventing a rule, and `CR-PC10-13` ("§2 thiếu hàng cho cột NOT NULL có DEFAULT hằng số") carries it to the next contract round. Better than what I asked for. |
| `F-A3R2-04` false generator dependency | **VERIFIED** | `downstream_vi` now says the earlier "phải sinh lại" was **SAI**, names the 15 real generator sources, cites `generate.py`'s own statement that an entity amendment "correctly produces no diff here" and `CR-P0-06`, and replaces the false dependency with the two real, hand-written paths (base Alembic revision; the schema-vs-entities test) plus the caveat that contract↔migration is therefore proved only *indirectly*. |
| `F-A3R2-02` guard blind to generated columns / one-directional | **VERIFIED (mutation-tested)** | `table_xinfo` at every call site, `table_info` nowhere; 10 tests. I ran my own mutation harness against the real test functions: dropping a declared field (`owner.locked_until`) → **caught**; adding an undeclared column (`owner.sneaky_backdoor`) → **caught**; declaring a NOT NULL column nullable → **caught**. Set equality now holds in both directions. Generated columns are not merely exempted: `test_nullability_matches_the_contract_in_both_directions` detects `hidden ∈ {2,3}` and holds them to a *stronger* rule — every source column of the generating expression must itself be NOT NULL or CHECK-guarded — and a companion test asserts the premise that `table_info` still hides them, so the check goes loud rather than quiet if SQLite changes. My fourth mutation (flipping `analysis.target_key` to NOT NULL in the contract) correctly did **not** fire, because the stronger source-column rule genuinely passes. |
| `F-A3R2-03` stale / unre-issued manifests | **VERIFIED** | Four newest per-card manifests, one per card; I re-hashed every `{path, sha256}` pair in all eight on disk: **all four registered ones have 0 stale pins**. The only manifest with stale pins is the superseded storage one, and it is not registered. `evidence/index.json` registers exactly the four newest by `evidence_id` (`EV-E1-02` ×3, `EV-E1-04` storage) and lists the four superseded ones under `superseded_card_runs` with `superseded_by` and a per-file `produced_pins_stale` / `read_pins_stale` breakdown that names the four storage files by path. |
| `F-A3R1-03` (was DEFERRED) index registration | **VERIFIED** | `evidence/index.json` holds 71 records and **71/71 validate** against `evidence/manifest.schema.json`. Summary is internally consistent (65 SELF_VALIDATION + 6 INDEPENDENT_AUDIT; E3 = E4 = 0). |
| PC09 · gates `G5` | **VERIFIED** | `PARTIALLY_MET`, not `MET`, with the reason stated: all four exit conditions `G5-X1..X4` are met, but G5's **entry** condition (G4) is still `PARTIALLY_MET`, and an open item blocks M3. It refuses to promote a gate on the strength of four cards. Conservative and correct. |
| PC09 · scenario statuses | **VERIFIED** | Exactly 4 moved (`SC21`, `SC26` → `PASS (E2)`; `SC29`, `SC31` → `PASS (E1)`), 52 remain `NOT_RUN`. Each carries `status_evidence_refs` pointing at the *current* manifest, the test file and both my reports, plus a `status_scope_vi` that restates the measurement. `SC21`'s scope text matches what I re-derived myself in `A3-R1` §2(b). No scenario moved on evidence I did not reproduce. |
| PC09 · `E0-19` | **VERIFIED** | Present, 18 sources checked, 0 violations; it is the standing guard for `F-A3R2-04`'s class. |
| PC09 · `E0-12` CR-P0-02 rule | **PARTIAL — see `F-A3R3-01`** | Mutation-tested on a scratch copy. Label outside the two evidence trees → **FAILS correctly** (`precode/gates.yaml` mutated: violations 0 → 1). Label inside `evidence/runs/` without an A3 citation → **does not fail**, because `in_scope_for_refs()` excludes `evidence/runs/` outright. |
| PC09 · `review.md` numbers | **VERIFIED as of epoch 2** | §Phase 0/1 states `303 passed / 4 xfailed / 0 failed` and "schema-vs-entities 8/8", attributed to A3-R1/R2 — correct for the epoch those reports covered. At epoch 3 the tree is 305/4/0 and the gate is 10 tests, so the section is one epoch behind (`F-A3R3-03`). |

**4 of 4 `F-A3R2-*` VERIFIED. `F-A3R1-03` closed by registration. One PC09 item PARTIAL.**

## 3. New findings

### `F-A3R3-01` — MEDIUM — the CR-P0-02 rule text claims to police `evidence/runs/**`; the check never reads that tree

`evidence/tools/e0_check.py:741-748` — `in_scope_for_refs()` returns `False` for anything
under `evidence/runs/` ("tool output"), and `E0-12`'s loop starts with
`if not in_scope_for_refs(rel): continue`. But the rule's own text (lines 1568-1571, and the
oracle string at 1685) says `IMPLEMENTATION_VERIFIED` "is permitted inside
`evidence/handoffs/**` **and `evidence/runs/**`** when the file CITES an A3 report", and that
`INTEGRATION_VERIFIED` / `LIVE_FEASIBILITY_VERIFIED` / `PRODUCT_ACCEPTED` "stay forbidden
everywhere".

Reproduced on a scratch copy (nothing in the repo touched):

| mutation | expected | observed |
| --- | --- | --- |
| `IMPLEMENTATION_VERIFIED` into `precode/gates.yaml` | FAIL | **FAIL**, 1 violation — the outside-evidence half works |
| new `evidence/runs/*.json` with `claim_ceiling: IMPLEMENTATION_VERIFIED`, no A3 citation | FAIL | **PASS**, and `checked` stayed 779 — the file was never examined |
| same with `claim.supports_label` | FAIL | **PASS** |
| same with `INTEGRATION_VERIFIED` ("forbidden everywhere") | FAIL | **PASS** |

The backstop is real but narrower than the rule reads. I tested
`evidence/manifest.schema.json` directly: it rejects `IMPLEMENTATION_VERIFIED`,
`INTEGRATION_VERIFIED` and `PRODUCT_ACCEPTED` on a `SELF_VALIDATION` record — that cap is
genuine and is what actually stops a Worker self-awarding. But on a record declaring
`review_type: INDEPENDENT_AUDIT` the schema **accepts all three**, including
`PRODUCT_ACCEPTED`. So for records under `evidence/runs/` that declare themselves
independent, no machine check constrains the label at all: not E0-12 (tree excluded) and not
the schema (cap lifted). Today nothing abuses this — the six such records are the honest W6n
transcripts — but the control the rule text advertises does not exist.
**Remediation constraint:** either bring `evidence/runs/` into `E0-12`'s scope for the claim
rule specifically (keeping it excluded from the free-text id sweeps it was excluded for), or
narrow the rule text to say `evidence/handoffs/**` only and state plainly that run records
are governed by the schema alone. Do not leave the oracle describing an enforcement the tool
does not perform. Proof required: the mutation table above, inverted.

### `F-A3R3-02` — MEDIUM — the EV-A3 transcripts carry an `execution` block that reads as my run log

The six `EV-A3-0*` records name `producer_principal: auditor-A3`, `producer_role: Auditor`,
`review_type: INDEPENDENT_AUDIT`, and each carries
`execution: {command: "uv sync --all-packages --frozen && uv run --frozen pytest && uv run
--frozen mypy && cd server && alembic heads", started_at: 2026-09-07T12:08:36Z, ended_at:
2026-09-07T12:08:40Z, exit_code: 0, attempts: 1}` (and for `EV-A3-05`, `npm ci && npm test &&
npm run lint && npm run typecheck` in the same four seconds).

**I did not run anything at 12:08:36Z, and none of those chains completes in four seconds** —
my `pytest` alone measured 35–45 s across the three rounds, and `npm ci` pulls 298 packages.
Those are W6n's transcription timestamps sitting in the schema field that means *when the
evidence-producing command ran*, attributed to me.

The authorship disclosure elsewhere is genuinely good — `limitations.not_checked_vi[0]` states
that the record is a transcript written by `worker-W6n`, that the Auditor did not write the
JSON, that the report wins on divergence, and it pins both report hashes; the index's
`honesty_note_vi` repeats it. That is why this is MEDIUM and not HIGH. But the disclosure
covers *authorship*, not *execution provenance*, and a later reader or gate computing
`ended_at − started_at` gets a false run record in my name.
**Remediation constraint:** for a transcribed record, `execution` must describe the
transcription (`kind: manual_procedure`, or the real timestamps of W6n's work) and the
Auditor's own timings must either be quoted from the report or omitted. An evidence record
must not assert a command execution that did not happen as described.

### `F-A3R3-03` — LOW — two epoch-2 statements are carried forward into an epoch-3 index

The `EV-A3-*` records list `F-A3R2-02` in `limitations.unresolved_issue_refs`, and
`precode/review.md` §Phase 0/1 states `303 passed / 4 xfailed / 0 failed` and "8/8" for the
schema gate. Both were true at epoch 2 and both are superseded at epoch 3: I have now
verified `F-A3R2-02` fixed (mutation-tested above), and the tree is 305/4/0 with a 10-test
gate. The records are not dishonest — each `uncertainty_vi` scopes the verdict to "FC-P1
epoch 2" and names the files that changed after that freeze — but the index they sit in is
generated at epoch 3 and presents them as current. The Coordinator anticipated this for the
residual note; the same staleness applies to the two numbers in `review.md`.

**New findings: MEDIUM 2 · LOW 1 · HIGH 0.** All `OPEN`; I close none and supply no patches.

## 4. Verdict and per-card claims

**Overall: PASS.** All four `F-A3R2-*` verify, `F-A3R1-03` is closed by real registration, and
the one PARTIAL is a gap in a gate's reach rather than in the candidate. The remediation
pattern this round is the same one that made R2 credible: where a rule did not cover the case,
the amendment **declared the gap and raised a CR** instead of manufacturing a rule.

Per-card claim verdicts are unchanged from `A3-R2` §5.1 and re-stated here:

* `TC-ingest-idempotent-ack-lost` — `IMPLEMENTATION_VERIFIED` **may stand, scoped** to the four
  produced operations, carrying the declared §4 `PARTIAL` and `CR-TC-ingest-05`.
* `TC-canonical-identity-merge` — **may stand, scoped**, with the two strict `xfail`s.
* `TC-owner-auth-session` — **may stand, scoped**, and the label **rests on
  `AMD-ENT-owner-01`, still `PROVISIONAL`**: if the Owner objects, this card's schema and this
  verdict reopen together.
* `TC-storage-write-blocked-readiness` — **may stand, narrowed** to exclude
  `write_blocked → healthy` recovery (no probe table, `CR-TC-storage-04`).
* Skeleton — **PASS**.

## 5. Residual for the next contract round

* **`AMD-ENT-owner-01` is `PROVISIONAL`.** The Owner has not spoken. Four shipped columns, one
  migration and the auth card's verdict depend on no objection.
* `CR-PC10-13` — `change-control.md` §2 has no row for "add a required column with a constant
  DEFAULT"; the version tier for such a change currently rests on migration evidence, not a rule.
* `CR-TC-storage-04` (no probe table → `write_blocked → healthy` not establishable at runtime),
  `CR-TC-ingest-05` (`counts.quarantined` in the wire schema vs no column on
  `ENT-ingest-receipt`), `CR-TC-AUTH-01` (fixture `recovery/h` seq4 pins `FORBIDDEN_EDGE`),
  `CR-TC-IDENTITY-02/03`, `CR-P0-06` (no generated entity registry, so contract↔migration is
  proved only through one test).
* `F-A3R3-01…03`, open.
* **Coverage reality:** 52 of 56 scenarios `NOT_RUN`; E3 and E4 are **0 everywhere** — no live
  call to X, Telegram, an AI provider or a browser has ever happened. `G5` is `PARTIALLY_MET`
  and `G4` remains `PARTIALLY_MET` above it.
* 14 of the 36 forbidden edges remain `NOT_TESTABLE_AT_THIS_LAYER` — not passed.
* Concurrency is still argued from structure. "Two concurrent submissions of one idempotency
  key" remains **not established**; no multi-process race test exists.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live calls.
