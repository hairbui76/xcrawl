# AUDIT_REPORT — A2-R7 — scoped review of two new documents (no freeze manifest)

## 1. Reference

No freeze manifest for this round by the Coordinator's instruction (cards are being re-pinned concurrently). The two documents in scope were hashed at start and at end of review:

| File | sha256 (start) | sha256 (end) | Bytes |
| --- | --- | --- | --- |
| `docs/master-plan.md` | `3b8bbae757a6c34140b2a0fe178506c7f6322c1e92f7a81dec43ae5fa6eec019` | **identical** | 37512 |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `745f4017f7cca0c20f96c2acc2b8b76ed18ef435ac664eef915b44d3d1ddad5f` | **identical** | 12584 |

Both match the hashes in the dispatch. Neither file drifted during the review. `agent-tasks/` and `precode/README.md` drift is excluded per the packet and is not reported as a finding — I confirmed it is real and benign (card pin rows are mid-re-pin at 501 rows / 144 files against the plan's 483 / 143, and `agent-tasks/README.md`'s pinned hash in the plan's front-matter no longer matches; both are exactly the concurrent re-pin the packet excludes).

Read-only: no repository byte written, no `git` mutation, no network, no subagent. Helpers under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`.

## 2. Method and evidence

| ID | Procedure | Observed |
| --- | --- | --- |
| EV-A2R7-01 | Hash both files at start and end | identical, matching the dispatch |
| EV-A2R7-02 | Resolve **every** cited id in `master-plan.md` — SC, REQ, TC card, MOD, invariant, ADR, error code, operation, entity.field — against the owning contract | **0 unresolved.** The only two tokens my sweep flagged are `delivery.unknown` (a delivery *state*, correctly used) and `pyproject.toml` (a filename my suffix filter missed) |
| EV-A2R7-03 | Recompute the fidelity numbers against `precode/gates.yaml`, `precode/review.md`, `precode/owner-decisions.md`, `agent_profile/registry.json`, `requirements.csv`, `traceability.csv`, the ADR set and the fixture directories | all reproduce **except** the reporting-fixture count (F-A2R7-01) |
| EV-A2R7-04 | Verify the three source hashes pinned in the plan's front-matter | `precode/owner-decisions.md` **match**; `precode/review.md` **match**; `agent-tasks/README.md` mismatch — excluded drift |
| EV-A2R7-05 | Compare the plan's open-item list and Owner-touchpoint table against my A2-R6 residual list | all five touchpoints the packet named are present and correctly placed; **one residual item is missing** (F-A2R7-02) |
| EV-A2R7-06 | Row-by-row diff of ADR-0011 against the Coordinator's ruling | **14/14 decision rows present** and faithful; front-matter `status: provisional-accepted`, `ratified_by: null`, `decision_owner: Coordinator (Owner-delegated, may object)`, `claim_ceiling: DRAFT_FOR_REVIEW`, `depends_on: [ADR-0006]` |
| EV-A2R7-07 | Resolve every id in ADR-0011; check `PROV-PC00-07` and the cited entities exist | **0 unresolved**; `PROV-PC00-07` present in `precode/decision-register.md`; `assignment`, `assignment_lease`, `schedule_occurrence` all exist in `entities.yaml` |
| EV-A2R7-08 | Check ADR-0011 against the contracts the packet named | `REQ-D07` SQLite **XN**; `REQ-D09` project Chrome profile **XN**; `REQ-D48`/`REQ-D50` local embedding **XN**; `REQ-D49` linear scan **UQ**; `REQ-D59` multilingual **UQ**; `REQ-S6.4-02` host processes **XN**; auth matches `openapi.yaml` (`ownerSessionCookie` + `ownerCsrfToken`) and `secrets.md` (Argon2id, CSRF double-submit); Telegram row correctly grounds the no-framework choice in `AMD-B03` — **all consistent** |
| EV-A2R7-09 | Arithmetic checks | P0 rows in `traceability.csv` = **234**, and 192 + 31 + 11 = 234 ✓; effort table sums to 75–109 person-days as stated ✓; 10 ADRs `accepted` and ADR-0011 `provisional-accepted` ✓ |

## 3. Verdict per document

- **`docs/master-plan.md` — PASS with findings** (3 LOW). Fidelity, honesty and structure are otherwise sound.
- **`precode/adr/ADR-0011-frameworks-and-toolchain.md` — PASS with findings** (2 LOW). Faithful to the delegation and to the contracts.

Neither document claims anything above its evidence, and neither is a `CONTRACT_READY` artefact — both carry `claim_ceiling: DRAFT_FOR_REVIEW`.

## 4. What the packet asked me to check

**(1) Fidelity.** The plan's statements about the baseline agree with the sources on every point I recomputed: 17 blockers `RATIFIED` and `open_product_blockers: []`; stack B; timezone; the purge scope with backups kept; the four `CONTRACT_READY` scopes and the four still `DRAFT`; G0–G2 `MET`, G3/G4 `PARTIALLY_MET`, G5 `NOT_MET` with `G5-X4` correctly named as the single missing exit condition (I confirmed `G5-X1…X4` and `G4-X7` exist in `gates.yaml`); the fifteen `KC` rows listed individually and matching `requirements.csv` exactly; the open-items table matching my A2-R6 residual list except for one omission. Every cited card, SC, REQ, operation, module, invariant and ADR id resolves.

**(2) Honesty.** Strong. The opening block states in the first sentence that the file is a plan and not evidence, that E1–E4 are projected, that no product code exists, and that estimates are relative person-days with no calendar. Every phase's evidence line is a projection and is written as one. §4 lists five named assumptions and says plainly that if they are wrong the numbers are wrong — including that assumption 3 (fixtures usable directly as test data) **has never been tried**. §7.5 is a dedicated "what this plan does not establish" section that disclaims card sufficiency, estimate accuracy and every `KC` row, and declares that `precode/README.md`, `agent-tasks/README.md` and `gates.yaml` win over this file on conflict. P0 coverage is quoted exactly as the packet requires: "**192/234 mạnh**, không phải 223 và không phải 234". `REQ-AC16` is consistently `BLOCKED`, never `FAIL`. Stop conditions repeatedly forbid the specific dishonest move available at that point — no CAPTCHA evasion, no guessed rate numbers, no character-count message splitting, no threshold tuning to pass, no "independent audit passed" without one.

**(3) Structure.** All eight phases (0–7) carry entry gate, cards, external steps, evidence artefacts, DoD, claim ceiling, stop conditions and an estimate. Phases 0 and 7 correctly declare **no cards** with a reason (infrastructure with no business behaviour; observation rather than building). Ceilings escalate defensibly and never overreach: `IMPLEMENTATION_VERIFIED` per card, `INTEGRATION_VERIFIED` only where `SC50` or full E2 justifies it, `LIVE_FEASIBILITY_VERIFIED` for SP1 "and only under the recorded conditions", `PRODUCT_ACCEPTED` only "within the published measurement limits". Owner touchpoints: all five the packet named are present — `REQ-OQ03` (#3, before phase 3), SP1 runs (#5, plus #6 X login), Telegram/arXiv-OpenAlex/CLI-terms facts (#7/#8/#9), ADR-0011 accept-or-object (#2, before phase 0), and the `CR-PC02-22` round (#13, with the right framing: re-present package-approved numbers one at a time as "what this value changes about what you will see"). The critical path is identified and the plan names the one place worth shortening (asking `REQ-OQ03` early). The risk register has ten rows, each with an *observable* trigger rather than a feeling, and it closes two risks that ratification retired rather than leaving them to worry about.

**(4) ADR-0011.** `status: provisional-accepted` with `ratified_by: null` — correct, and the document says in its own words why: "ADR này **không** được ghi `accepted`: không có quyết định nào của Owner phê chuẩn nội dung của nó." The delegation is described accurately ("You pick, record as ADR"), the objection clause is explicit, and the cost of a reversal is stated honestly — cards and code, not `contracts/`, `acceptance/` or `precode/`. Every one of the 14 rows carries a rationale. Consistency with the named contracts is exact (EV-A2R7-08). Two touches are better than the ruling they came from: the CLI/ACP row grounds `subprocess` in `ADR-0010`'s process-level isolation requirement rather than merely asserting it, and the "Bất biến được giữ" section ties the two riskiest choices back to `I11` and `I15`. The "Việc còn lại" section honestly lists three things this package did **not** do, including the E0 check for generated-code drift that §2.3 of the plan depends on.

## 5. Findings

### F-A2R7-01 — **LOW** — `master-plan.md` §1.2 understates the reporting fixture count

- **Ref:** `docs/master-plan.md` §1.2, row "Báo cáo và thời gian": "coverage half-open, backfill ledger, **12 fixture `reporting/`**".
- **Observed:** `acceptance/fixtures/reporting/` holds **14** JSON fixtures, all fourteen at `claim_ceiling: CONTRACT_READY` with a header `ratification_ref` (I verified this in A2-R6 and again here). The adjacent row for identity correctly says 14.
- **Impact:** minor, but it is a count in the table that tells the Owner what the ratified scopes contain, and the corpus has an established discipline of deriving such counts rather than typing them.
- **Remediation constraint:** the number must come from the same derivation that produces `numbers.json`'s `fixtures` and `fixture_directories`, or be dropped in favour of a pointer to that artefact.

### F-A2R7-02 — **LOW** — the plan carries every A2-R6 residual item except the OpenAPI 3.1 validator gap, which its own toolchain now depends on

- **Ref:** `docs/master-plan.md` §1.5 (open items), §5 (risk register), §7.5 (what this does not establish), §2.4 (CI jobs).
- **Observed:** my A2-R6 residual list item 11 — `contracts/http/openapi.yaml` (227 KB) **has never been checked by an OpenAPI 3.1 validator** — appears nowhere in the plan; the string "validator" does not occur. The three CI jobs in §2.4 are `e0_check` + card-pin verifier, `pytest`, and `vitest` + `tsc`; none validates the OpenAPI document. This matters more now than it did in R6: §2.1 makes `openapi.yaml` the **generator input** for the FastAPI/Pydantic request-response models, and §2.3 makes it the generator input for the TypeScript client via `openapi-typescript`. A document that has never been validated against its own specification is about to become the single source from which both language tiers are generated, and §2.3's rule that generated files may never be hand-edited means a specification defect would surface as a generation failure or a silently wrong model rather than as a contract review comment.
- **Impact:** the plan's open-item list is otherwise a faithful superset of my residual list, so a reader will reasonably treat it as complete. Two smaller R6 residuals are also absent — purge-table enumerations in prose are not machine-compared, and `E0-06`/`E0-07` do not scan prose inside `evidence/handoffs/` — but those are tool limitations already disclosed in `evidence/tools/README.md`; the validator gap is the one that sits directly under a phase-0 deliverable.
- **Remediation constraint:** the plan must carry the item, and phase 0's evidence or CI job list should say whether an OpenAPI 3.1 validation step is in scope for the `e0` job. If it is deliberately deferred, the deferral belongs in §7.5 with the reason, so that "CI is green" is never read as "the wire contract is valid".

### F-A2R7-03 — **LOW** — the gate table uses evidence vocabulary for SP1

- **Ref:** `docs/master-plan.md` §1.3, row `SP1`, column "Trạng thái": **`NOT_RUN`**.
- **Observed:** `precode/gates.yaml` records SP1 with `current_status: NOT_MET`. `NOT_RUN` belongs to the evidence-result vocabulary (baseline §3), not the gate-status vocabulary, whose four values `gates.yaml` declares as `MET_PROVISIONAL`, `PARTIALLY_MET`, `NOT_MET`, `NOT_APPLICABLE_YET`. Every other row of the plan's table uses the gate vocabulary correctly.
- **Impact:** cosmetic, and the meaning is not lost — SP1 has indeed not run. Recorded because this corpus has spent several rounds establishing that one fact lives in one place with one vocabulary, and a table headed "Cổng / Trạng thái" should read from `gates.yaml`.
- **Remediation constraint:** the cell must carry `gates.yaml`'s `current_status` for SP1; if the plan wants to add that no probe has run, that is a separate column or a note.

### F-A2R7-04 — **LOW** — ADR-0011 attributes its repo layout to a section that declares six of its seven directories

- **Ref:** `precode/adr/ADR-0011…md`, "Bố cục repo (**đã được `agent-tasks/README.md` §5.3 khai**)"; the same claim in the Coordinator's ruling.
- **Observed:** `agent-tasks/README.md` §5.3 declares `server/`, `collector/`, `worker/`, `probe/`, `tests/` and `web/` — six. It does **not** declare `shared/rr_contracts/`, which is the seventh entry in the ADR's list and the one that carries the load for §2.3's generate-don't-hand-edit rule. The string `rr_contracts` does not occur anywhere in `agent-tasks/README.md`. The defect originates in the Coordinator's ruling, which makes the same parenthetical claim; W1 transcribed it faithfully.
- **Impact:** small, and it will be overtaken by the concurrent re-pin — but as frozen the ADR cites an existing document as already having declared something it has not, which is the class of provenance claim this project has spent three rounds tightening.
- **Remediation constraint:** either §5.3 gains `shared/rr_contracts/` (the natural fix, since the cards will need it), or the ADR's parenthetical is narrowed to the six directories §5.3 actually declares and `shared/rr_contracts/` is introduced as new. The ruling should be corrected in the same pass so the two do not diverge again.

### F-A2R7-05 — **LOW** — four of ADR-0011's fourteen decision rows have no alternatives and no statement that none were considered

- **Ref:** `precode/adr/ADR-0011…md`, "Phương án đã cân nhắc" table.
- **Observed:** the alternatives table has **10 rows** — Packaging, Server API, Persistence, Queue, Collector, Analysis worker, Embedding, Telegram, Web, Auth. The decision table has **14**: Test, Lint/format, CI and Đóng gói/triển khai have no entry. The Coordinator's ruling marks those four cells "—", which at least records that the cell was considered and left empty; the ADR drops the marker, so a reader cannot tell whether alternatives were weighed and rejected or never examined.
- **Impact:** ADR-0011 is the document the Owner will read to decide whether to object to any row. Four rows offer no basis for an objection — and one of them (packaging/deploy, Docker Compose plus mounted secret files) is the row that touches the Owner's own machines.
- **Remediation constraint:** each of the four rows needs either an alternatives entry or an explicit "none considered — conventional default, reversible at no contract cost" line, so that the Owner's objection right in the Status section applies uniformly to all fourteen rows.

**Severity counts: CRITICAL 0 · MAJOR 0 · MEDIUM 0 · LOW 5** — three against `master-plan.md`, two against `ADR-0011`.

## 6. Deferred (out of scope, recorded not lost)

1. `agent-tasks/README.md` §5.3 still says "**framework chưa được chốt** … card nào cần chọn framework phải DỪNG và raise CR", which ADR-0011 supersedes. This is the concurrent re-pin the packet excludes; it must not survive that re-pin.
2. The plan's `agent-tasks/README.md` front-matter pin and its "483 dòng hash / 143 file" CI figure are both stale against the mid-re-pin tree (now 501 / 144). Expected drift, excluded by the packet, but both must be refreshed when the re-pin lands.
3. ADR-0011 and the plan both depend on an E0 check that does not exist yet — "generated files match the contract hash". Both disclose it honestly (ADR "Việc còn lại" (b), plan §2.3). It becomes a real gate obligation at phase 0.

## 7. Limitations

This was a two-document review with no freeze manifest, so I cannot certify the surrounding tree and did not try: my fidelity checks read the current bytes of `gates.yaml`, `review.md`, `owner-decisions.md`, `requirements.csv`, `traceability.csv` and the contracts, which are themselves unfrozen this round. Both documents' own hashes were stable start to end. I verified that cited identifiers resolve and that quoted numbers reproduce; I did not re-derive the underlying baseline, which A2-R6 covered on a frozen manifest. Effort estimates are unfalsifiable by inspection — I checked that they are labelled relative, that their assumptions are stated, and that they sum as claimed, which is all an auditor can do with a forecast. Reference checks find dangling and stale references, not missing ones; F-A2R7-02 is a *missing* item and I found it only because I held the plan against my own R6 residual list, which is exactly the check that does not generalise.

## 8. Completion ceiling

Both documents declare `claim_ceiling: DRAFT_FOR_REVIEW` and neither asserts more. Nothing in this review establishes `CONTRACT_READY` for any scope beyond the four already ratified, and nothing establishes any runtime claim: the plan is a forecast, and ADR-0011 is a delegated technical choice the Owner may still reverse. `NOT_READY_FOR_PRODUCT_CODE` stands; G5 remains `NOT_MET` on `G5-X4`.

The five findings are **OPEN**. I close none and accept no risk; disposition requires the designated authority, and the author of a fix may not verify it.

---
*Produced by `auditor-A2` under `PKT-A2-R7`. Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent. Both reviewed files hashed identical at start and end.*
