# AUDIT_REPORT — A2-R1 — final independent audit of the Pre-code baseline (FC-W4, epoch 4)

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch 4 |
| Manifest | `…/scratchpad/audits/FC-W4-manifest.txt`, 200 entries |
| `manifest_sha256` declared | `07dcf969f420ebfacddc9226f688d0f862297c2f020d89b9fa464ae15ac449ef` |
| Recomputed at **start** (T0, algorithm `sha256-path-role-hash-bytes-v1`, protocol §6) | `07dcf969f420ebfacddc9226f688d0f862297c2f020d89b9fa464ae15ac449ef` — **MATCH** |
| Recomputed at **end** (T1) | `07dcf969f420ebfacddc9226f688d0f862297c2f020d89b9fa464ae15ac449ef` — **MATCH** |
| Per-entry rehash | 200/200 sha256 **and** byte counts match; 0 missing, 0 drift, entry order sorted by UTF-8 path |
| Roles | CANDIDATE 174 · DEPENDENCY 8 · EVIDENCE 16 · SOURCE 2 |
| Sources | `research-radar-pre-code-plan.md` `f65bb046…707f40` (64915 B) · `research-radar-spec.md` `d35e1f2d…5e0e26` (41770 B) — both match baseline §2 |
| Manifest completeness | The repository holds 202 non-`.git`/`.claude` files; the 2 not listed are `project-overview.md` and `master-interview-prompt.md`, which baseline §2 declares historical context only. No file in review scope is omitted. |

**Not `STALE`.** The snapshot was byte-identical across the whole review interval. **Not `BLOCKED`** — every artefact needed to conclude was readable at the frozen bytes.

## 2. Reviewer identity and independence declaration

Principal `auditor-A2`, dispatched by the Coordinator under `AUTH-COORD-A2-R1` / packet `PKT-A2-R1`, read-only, lease `null`.

I have authored, co-authored and reviewed **nothing** in `/mnt/virtual/repo/xcrawl`. I did not write, patch, rename or delete any repository byte during this audit; no `git` command that mutates state was run; no network was used; no subagent was spawned. All helper scripts live under `…/scratchpad/a2/` and were run from that directory with `PYTHONDONTWRITEBYTECODE=1`. My single execution of the project's own `evidence/tools/e0_check.py` used `--json-out` pointed **into my scratch directory**, so it wrote nothing into `evidence/` (the tool writes only when that flag is given; verified by reading `main()` before running it).

Per `auditor.md` I close no finding, accept no risk, and supply no patch or candidate bytes. Every finding below is **OPEN** and carries a remediation *constraint*, not a fix.

I read A1's three reports and the four Coordinator rulings **only after** forming my own view from the sources and the frozen bytes, as the packet directs.

## 3. Scope checked / excluded

**Checked.** All 200 manifest entries; `SRC-PLAN` and `SRC-SPEC` in full; all of `precode/`, `contracts/`, `acceptance/`, `agent-tasks/`, `evidence/`; the E0 tool re-run and diffed against the registered run; my own independent cross-package checkers (§4) written without reference to the project's tool.

**Excluded.** Runtime behaviour of anything (no code exists). OpenAPI 3.1 specification conformance of `contracts/http/openapi.yaml` (227 KB) — no validator is available and the packet forbids installing one; reported as an explicit limitation, matching PC09's own §13 item 8. Word-by-word fidelity of all 246 requirement rows against the sources — I sampled and A1-R1 verified 25 rows plus all blockers/amendments/ADRs; I re-verified the structural properties (anchors, status enums, ID forms) mechanically. Provenance of the two source documents themselves, which rests on the registry pin.

## 4. Evidence records (all `INDEPENDENT_AUDIT`, producer `auditor-A2`)

| ID | Command / procedure | Oracle | Expected vs observed | Exit | Status |
| --- | --- | --- | --- | --- | --- |
| EV-A2-01 | `python3 a2/manifest_check.py …/FC-W4-manifest.txt` (T0 and T1) | protocol §6 algorithm; per-entry sha256 + bytes | expected declared hash; observed identical both times, 0 drift | 0 | PASS |
| EV-A2-02 | `find` over repo minus `.git`/`.claude`, set-compare against manifest paths | manifest covers full review scope | expected ⊆ complete; observed 2 declared-historical files outside, 0 in-scope omissions | 0 | PASS |
| EV-A2-03 | `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py --repo … --json-out <scratch>` | tool's own 19 checks | expected reproduction of registered run; observed **19/19 PASS, 0 violations, exit 0** | 0 | PASS |
| EV-A2-04 | Diff of EV-A2-03 output vs `evidence/runs/E0-20260907T004621Z.json` | check-by-check equality | 18/19 identical; `E0-01-parse` 115 vs 114 and `files_scanned` 169 vs 168 — the tool scans `evidence/`, so the registered run's own output file did not yet exist when it scanned. Baseline hashes, environment, limitations, summary identical. | 0 | PASS (delta explained; see F-A2R1-11) |
| EV-A2-05 | `python3 a2/c1_edges.py` — forbidden_edge ↔ denied_case bijection, caller/callee equality, operation ownership | 36 edges each covered by exactly one case whose `attempted_edge` equals the edge | bijection and caller/callee: **36/36 exact**. Operation ownership: 12 cases name an operation the callee does not own; see F-A2R1-05 | 0 | FAIL (scoped) |
| EV-A2-06 | `python3 a2/c2_prose_ops.py`, `c3_alltok.py` — every backticked `<domain>.<verb>` token in `contracts/`, `acceptance/`, `precode/`, `agent-tasks/` resolved against `ports.yaml`, `entities.yaml` fields and filenames | free-prose operation citations resolve | **9 distinct non-existent operation ids in 8 scenarios**; see F-A2R1-01 | 0 | FAIL |
| EV-A2-07 | `python3 a2/c8_fixev.py` — every fixture event: operation exists, actor is an allowed caller, `edge_assertion: forbidden` events are *not* allowed callers, `operation: null` carries `event_type` | R4-01/R4-02 + default deny | **318 events, 0 problems** | 0 | PASS |
| EV-A2-08 | `python3 a2/c10_trace.py` — full (not sampled) chain over all 246 traceability rows and all 53 scenarios | scenario/contract/error refs resolve; every scenario has an existing fixture, oracle, durable state, forbidden effects, evidence level, polarity | 0 dangling scenario refs, 0 missing contract files, 0 dangling error codes, 0 missing fixture files, AC-01…AC-18 each mapped 1:1 to SC01…SC18 | 0 | PASS |
| EV-A2-09 | `python3 a2/c5_cards.py` — recompute every pinned contract hash in all 21 files under `agent-tasks/` | pinned sha256 + bytes equal actual | **483/483 pins verify**, 0 bad | 0 | PASS |
| EV-A2-10 | `python3 a2/c4_evidence.py` — validate `evidence/index.json` records against `evidence/manifest.schema.json` with format checking | every record validates | **55/55 records valid**; the wrapper is declared an index, not a manifest, in `shape_note_vi` | 0 | PASS |
| EV-A2-11 | `python3 a2/c6_numbers.py`, `c9_dor.py`, `c11_misc.py` — recount every headline number in `precode/review.md`; completeness of `errors.yaml`, `ports.yaml`, auth-scope convergence; forbidden status strings | review.md numbers reproduce | 246/246 rows, coverage-status distribution, 85 ops, 99+36 edges, 60 entities, 28 error codes, 53 scenarios **all reproduce**; **4 numbers do not** — see F-A2R1-02. 0 `status: CLOSED/ACCEPTED`, 0 asserted `TBD`, all 17 blockers `PROVISIONAL`, 10/10 auth scopes converge with `capabilities.yaml`, 6 OpenAPI security schemes map per the recorded rule | 0 | FAIL (scoped) |
| EV-A2-12 | `python3 a2/v_a1r1.py`, `v_a1r1b.py`, `v_a1r2.py`, `v_a1r3.py` — independent reproduction of all 20 A1 findings | each finding's original condition | **20/20 VERIFIED as remediated**; table in §6 | 0 | PASS |
| EV-A2-13 | `python3 a2/c12_prose_ids.py` — prose-cited error codes, SC, REQ, I and ADR ids | every prose-cited id is registered | 1 unregistered error code (`SAVE_ALREADY_EXISTS`); REQ range-shorthands and my extractor's invariant misses are false positives | 0 | FAIL (scoped) |
| EV-A2-14 | Manual reading walkthrough of `agent-tasks/TC-collector-checkpoint-resume.md` and `TC-telegram-unknown-delivery.md` end to end against their read sets | can an agent work from card + refs alone? | Yes — see §8 | n/a | PASS |

No secrets appear in any output. Runtime: python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3, linux — identical to the environment recorded in the registered E0 run.

## 5. Findings

All findings are **OPEN**. I do not close, waive or accept them. No patches, no candidate bytes.

### F-A2R1-01 — **MAJOR** — nine non-existent operation ids inside eight scenarios' `event_order`; the remediation that claims to have closed this class fixed one scenario of two

- **Ref:** `acceptance/scenarios.yaml` SC01, SC12, SC24, SC27, SC42, SC43, SC53 (and the correction note in SC52); `precode/review.md` §8.1 and §3.3; `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json` `operation_name_note_vi`.
- **Reproduce:** `python3 a2/c3_alltok.py` — extract every backticked `<domain>.<verb_noun>` token and resolve it against `contracts/ports.yaml.operations[].operation_id`.
- **Expected:** `contracts/ports.yaml` is the naming authority for operations (baseline §3); an acceptance scenario's event order names real operations, because it is the oracle an implementer and a test harness are built from.
- **Observed:** nine ids that do not exist in the 85-operation inventory —
  `job.enqueue_run` (SC01; authoritative `job.enqueue_scheduled_run`) ·
  `backup.create`, `backup.restore` (SC12; `backup.create_snapshot`, `backup.restore_snapshot`) ·
  `embedding.start_generation`, `embedding.switch_generation` (SC24; `embedding.start_generation_rebuild`, `embedding.activate_generation`) ·
  `backup.restore`, `backup.reconcile` (SC27) · `backup.reconcile` (SC42, SC53; `backup.reconcile_after_restore`) · `backup.verify` (SC43; `backup.verify_snapshot`).
  Separately, SC12 step 3 invokes `post.mark_source_deleted`, an operation PC01 **explicitly rejected** (`contracts/ports.yaml` records the ruling in `PKT-PC01-FIX1`: the observation is a field `source_deleted_observed_at` on an `ingest.submit_batch` item, "**không** phải một operation riêng"), so that step names a path the contract says does not exist.
  The two `embedding.*` names are the exact defect raised as `CR-PC04-11`. `precode/review.md` §8.1 states it "**được đóng ở đây**" and §3.3 states the names "**nay là**" the authoritative ones; the fixture's `operation_name_note_vi` says the same. The fix was applied to **SC52 only**. SC24 still carries both wrong names, and the six `backup.*`/`job.*` cases were never noticed at all.
- **Impact:** this is the class of defect the E0 tool provably cannot see — `E0-04` reads structured fields, `event_order` is a list of sentences, and `precode/review.md` §13 item 7 names this exact risk in writing. A remediation was reported as complete while 8 of the 53 scenarios still carry it, so the corpus's honest self-disclosure of a blind spot was not converted into a sweep. Four of the affected scenarios (SC27, SC42, SC43, SC53) are the restore/reconciliation oracles that `I15` and `RESTORE_UNVERIFIED` depend on; SC01 is `AC-01`.
- **Remediation constraint:** every free-prose list in `acceptance/scenarios.yaml` (`event_order`, `input_vi`, `oracle_vi`, `expected_durable_state_vi`, `forbidden_effects_vi`) must be swept for operation-shaped tokens and each resolved against `ports.yaml`, and the sweep must become a standing automated check (the natural home is `E0-04` extended to free text, which is also what `CR-PC09-08` asks for in a different dimension). SC12's `post.mark_source_deleted` step must be re-expressed in terms of the sanctioned field on `ingest.submit_batch`, not renamed to a near-miss. `CR-PC04-11` must not be recorded as closed until every scenario is clean and an independent verifier — not the author of the fix (protocol §8) — has re-run the sweep on a new epoch.

### F-A2R1-02 — **MAJOR** — four headline numbers in the claim-bearing readiness report contradict the artefacts and the E0 run it cites, including its own tables

- **Ref:** `precode/review.md` §1 (paragraph 1), §9 (summary line under the module table), §11 (summary line under the DoR table, and row 9).
- **Reproduce:** `python3 a2/c6_numbers.py`; and count the rows of review.md's own two tables.
- **Expected vs observed:**

  | Claim in review.md | Actual (my recount) | Source of truth |
  | --- | --- | --- |
  | "63 transition trên năm máy trạng thái" | **67** | `contracts/state/*.yaml` `transitions[]`; the registered E0 run's `E0-09-state-lint` reports `items_checked: 67` |
  | "**87 fixture trên chín thư mục**" (§1 and §11 row 9) | **86** | `acceptance/fixtures/**/*.json`; the registered run's `E0-15` directory table sums to 11+1+12+1+14+13+14+18+2 = 86 |
  | "**10 module ở `READY_FOR_CARD` có điều kiện … 15 `BLOCKED`**" | **9** and **16** | review.md's own §9 table, 25 rows, parsed mechanically |
  | "**10 đạt, 0 đạt một phần, 2 chưa đạt**" (DoR §17) | **9 ✅, 1 ⚠️, 2 ❌** | review.md's own §11 table — and its very next sentence says "Dòng #8 vẫn ⚠️" |

- **Impact:** `precode/review.md` is the document the Coordinator reports to the Owner, and it opens by asserting "Mọi con số đến từ một lần chạy thật của `evidence/tools/e0_check.py`". Two of the four numbers contradict that run; two contradict tables on the same page. Both errors move in the flattering direction — one more module ready than the table shows, one more DoR item met and the partial one erased. Ruling `R5-08` explicitly tasked this wave with "update `review.md` numbers"; that instruction is not fully discharged. The hard-blocked count (5) and every other number I recounted (246 rows and their coverage distribution, 85 operations, 99 allowed + 36 forbidden edges, 60 entities, 28 error codes, 53 scenarios, 0 ORPHAN) **do** reproduce exactly, which makes the four outliers stale rather than systematic — but a reader cannot tell which is which without recounting.
- **Remediation constraint:** every number in §1, §9, §11 must be regenerated from the artefacts by a script whose output is retained as the evidence record, not carried forward by hand between revisions; where a number is also produced by the registered E0 run, the review must cite the run's field rather than restate it. The summary line of any table must be derived from that table, not written beside it. A re-count by the same principal is not sufficient to close this (protocol §8).

### F-A2R1-03 — **MEDIUM** — two `precode/` files name a superseded card pin epoch, one of them under the heading "Pin hiện tại"

- **Ref:** `precode/README.md` §6 line 156; `precode/review.md` §9.1 line 632.
- **Reproduce:** `grep -ro "PC10-PIN-[A-Za-z0-9-]*" agent-tasks precode` and compare.
- **Expected vs observed:** all 18 task cards declare **`PC10-PIN-FCW4b-20260907`** (18/18, verified). `precode/README.md` states "**Pin hiện tại.** Card mang pin epoch **`PC10-PIN-FCW4-20260907`**" and `precode/review.md` §9.1 states the 18 cards were "được pin lại theo epoch **`PC10-PIN-FCW4-20260907`**". `FCW4b` supersedes `FCW4` (the cards themselves record the supersession and the reason: `contracts/modules.yaml` and the boundary fixture changed in PC01-FIX8/FIX9).
- **Impact:** `README.md` is the entry point and it makes a positive assertion about the *current* pin that is false. A reader validating a card against `FCW4` hashes would either find no such epoch or validate against superseded bytes — precisely the `INV-06`/`INV-09` staleness the pin mechanism exists to catch.
- **Remediation constraint:** both files must name `PC10-PIN-FCW4b-20260907` and, where they narrate history, mark the older epoch as superseded. The epoch name must be sourced from the cards (or from `evidence/handoffs/PC10-handoff.md` §ADDENDUM) rather than transcribed, so a future re-pin cannot leave these two files behind again.

### F-A2R1-04 — **MEDIUM** — the consolidated change-request register omits 15 CRs raised by PC00–PC08, including one still recorded as awaiting Coordinator approval inside a frozen contract

- **Ref:** `precode/review.md` §8.2 ("70 CR đã được phát ra bởi PC00–PC08. Bảng dưới gộp theo trạng thái"); `contracts/modules.yaml` `default_deny.error_code_refinement_vi`; `acceptance/fixtures/boundary/README.md`.
- **Reproduce:** `python3 a2/c7_odr.py` — collect every `CR-PC\d\d-\d\d` in the repository, restrict to PC00–PC08, set-subtract the ids appearing in review.md §8.2.
- **Expected vs observed:** 75 distinct PC00–PC08 CRs exist, not 70. Fifteen appear in **no** status row of §8.2 and in no section of `precode/owner-decision-request.md`: `CR-PC00-01`, `-03`, `-09`, `-10`, `CR-PC01-02`, `-09`, `-10`, `-11`, `CR-PC02-07`, `-12`, `-18`, `CR-PC04-10`, `CR-PC07-07`, `-08`, `-09`. Two of them are material: **`CR-PC01-09`** is recorded inside `contracts/modules.yaml` itself as *"gửi kèm `CR-PC01-09` **xin Coordinator phê chuẩn**"* for the two error codes (`UNAUTHORIZED_COMMAND`, `RESTORE_UNVERIFIED`) used outside the four-row R5-01 boundary table, and `acceptance/fixtures/boundary/README.md` repeats that it is "đang chờ phê chuẩn"; **`CR-PC02-18`** asks PC09 to decide whether the R4-01 column gate extends to fixtures that do not use `rows[]` — the exact scoping question behind F-A2R1-08.
- **Impact:** the register is the Coordinator's inventory of what is still owed. A CR that sits inside a frozen contract asking for ratification, and appears in no consolidated list, is a decision that can be shipped as settled without anyone having settled it. Several of the fifteen were raised after PC09's handoff, which explains but does not repair the omission: the frozen candidate is what the Owner will be shown.
- **Remediation constraint:** §8.2 must be regenerated from a mechanical sweep of the repository for CR ids rather than transcribed, must state a status for every id found, and must reconcile its own count with that sweep. `CR-PC01-09` needs an explicit Coordinator ruling recorded where the two codes are used, or the codes must be brought inside the R5-01 table; it must not stay in the state "awaiting approval" inside a contract offered as ready.

### F-A2R1-05 — **MEDIUM** — a denied case and its boundary-sweep event name an operation the callee cannot serve, in the direction opposite to the forbidden edge

- **Ref:** `contracts/modules.yaml` `denied_cases[NC-28]`; `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` event `seq: 26`. Related, lower severity: NC-04, NC-07, NC-13, NC-17, NC-25, NC-29.
- **Reproduce:** `python3 a2/c1_edges.py` — for each denied case, check that `attempted_edge.operation` is owned by `attempted_edge.callee`.
- **Expected vs observed:** the forbidden edge `FE-26` is `MOD-scheduler → MOD-x-collector`. `NC-28` and sweep event 26 give `operation: worker.claim_assignment`. That operation is owned by **`MOD-job-service`** and its only declared caller is `MOD-x-collector` — i.e. it runs in the **opposite** direction and the collector neither owns nor exposes it. The case's own `enforcement_detail_vi` says so: *"Máy cá nhân KHÔNG lắng nghe cổng nào; collector KÉO việc (D11). **Không có đích để gọi tới.**"* An event that names an operation asserts an oracle of the form "call it, assert `CAPABILITY_DENIED`", which is unrunnable when there is no endpoint; the honest form is the one NC-12 and NC-24 already use — `operation: null` plus `event_type: local_observation` plus `operation_absent_reason_vi`. Six further cases name an internal port for an edge whose callee is an external system (`telegram.send_payload` for `EXT-telegram-api`, `research.fetch_work_metadata` for `EXT-arxiv-api`, `ai.run_inference_task` for `EXT-ai-provider-api`); these are defensible as "the effect of that port attempted directly" but the convention is written down nowhere. Also, NC-08, NC-15, NC-22 and NC-24 carry `operation: null` without the `operation_absent_reason_vi` key that NC-12 carries (the corresponding sweep events do carry it).
- **Impact:** this is the same defect *class* the Coordinator says escaped the tool once already (`FE-20`/`FE-21`, now correctly fixed and honestly documented in the fixture's `bijection_note_vi`). `E0-10b` checks that the case's caller/callee equal the edge — which they do — and never asks whether the callee can serve the named operation; `E0-14` checks that a fixture actor is an allowed caller, which for a `forbidden` assertion is satisfied by *not* being one. So the gate that was tightened after the last occurrence still does not cover this one. The concrete cost is an unimplementable negative test for the one edge that protects "nothing calls into the personal machine".
- **Remediation constraint:** `attempted_edge.operation` must be non-null only when the **callee** owns that operation; otherwise `null` with `event_type` and `operation_absent_reason_vi`, applied uniformly to NC-08/15/22/24 as well. The external-system convention must be written into `modules.yaml.default_deny` if it is to be kept, or those six cases moved to the `local_observation` form. The bijection gate must be extended to assert callee-ownership, since a rule that is not machine-checked has now drifted twice.

### F-A2R1-06 — **LOW** — an error code is used in a contract but is not registered in the single error catalogue

- **Ref:** `contracts/data/entities.yaml` line 262 (`saved_item` UNIQUE `guarantees[]`); `contracts/errors.yaml`; `contracts/ports.yaml` `save.create.error_codes`.
- **Reproduce:** `python3 a2/c12_prose_ids.py`.
- **Expected vs observed:** baseline §3 requires new codes be "registered in `contracts/errors.yaml`", and `errors.yaml` declares itself "danh mục duy nhất của mã lỗi". `entities.yaml` states that in a concurrent Save "transaction kia nhận `SAVE_ALREADY_EXISTS` và trả về hàng đã tồn tại". That code is not among the 28 registered, and `save.create.error_codes` lists neither it nor `CONFLICT` in its place. It escaped `E0-05` because the citation lives inside a prose string rather than a structured field — the same blind spot as F-A2R1-01.
- **Impact:** small in blast radius but it lands on `AC-13`/`SC13`/`I08` (concurrent Save from app and Telegram), where the oracle depends on what the losing transaction observes. Two contracts currently give different answers to that question.
- **Remediation constraint:** either register `SAVE_ALREADY_EXISTS` in `errors.yaml` with the ten fields the other 28 carry and add it to `save.create.error_codes`, or restate the guarantee in terms of a registered code; the choice must be reflected in `SC13` and in `telegram/j-concurrent-save-app-telegram.json` so all three agree. The error-code reference check must be extended to prose, not only structured fields.

### F-A2R1-07 — **LOW** — invariants I16 and I17 are in production use without the decision record the baseline requires for them

- **Ref:** `contracts/data/invariants.md` (`## I16 (mới)`, `## I17 (mới)`); `precode/baseline.json` `id_conventions.invariant` and `source_anchors.SRC-PLAN.invariants`; `precode/decision-register.md`.
- **Reproduce:** `grep -n "I16\|I17" precode/decision-register.md` (0 hits); list the labels of `baseline.json`'s invariant anchors (I01…I15 only); read `baseline.json` `id_conventions.invariant.form` ("I01..I15") and `note_vi` ("I16+ chỉ khi có decision record").
- **Expected vs observed:** baseline §3 admits `I16+` "only with a decision record". I16 and I17 are cited by `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `contracts/data/entities.yaml` and `precode/review.md`. Their justification exists — and is well argued — but only inside `contracts/data/invariants.md`, the file that introduced them. The decision register never mentions them; `baseline.json` neither anchors them nor updates the convention that still reads "I01..I15".
- **Impact:** the corpus's own rule for admitting a new invariant points at a place that does not record the admission, so the rule cannot be checked where it is stated. `E0-07` passes because it asks only whether a cited id is *defined somewhere*.
- **Remediation constraint:** I16 and I17 need an entry in `precode/decision-register.md` with the same shape as the other self-made decisions (justification, owner, `PROVISIONAL`, blocked scope), an anchor in `baseline.json` alongside I01–I15, and an updated `id_conventions.invariant.form`. Defining an invariant inside the contract that consumes it is what the rule exists to prevent.

### F-A2R1-08 — **LOW** — the disclosed blind spot of the column gate is narrower than the blind spot

- **Ref:** `precode/review.md` §13 item 5; the registered E0 run's `E0-15` directory notes.
- **Reproduce:** count fixtures per directory that contain no `rows` key at all.
- **Expected vs observed:** §13 item 5 discloses that "`collection/` và `recovery/`" state their oracles in prose so the column gate does not reach their original fixtures. Measured: **ai 9 of 11**, **collection 8 of 12**, **recovery 10 of 13**, **telegram 5 of 18** (the five negative wire fixtures), **reporting 1 of 14**, **boundary 1 of 1** carry no `rows[]`. `E0-15`'s per-directory `columns_checked` corroborates this (ai 40 columns across 11 files versus reporting 475 across 14). The disclosure is honest in kind but omits `ai/` — the directory holding the adversarial prompt-injection and grounding fixtures — and the telegram negative set.
- **Impact:** "0 unresolved" is reported per directory and reads corpus-wide; for three directories it covers a minority of the files. `CR-PC02-18` asked exactly this question and, per F-A2R1-04, has no recorded answer.
- **Remediation constraint:** the disclosure must name every directory whose files fall outside the gate and give the covered/total count per directory, taken from the run rather than from memory; `E0-15` should report `files_without_rows` per directory so the number cannot drift from the prose. Whether the gate is extended to non-`rows` fixtures is `CR-PC02-18`'s decision and belongs to the Coordinator, not to a re-wording.

### F-A2R1-09 — **LOW** — DoR item 5 is asserted met without disclosing five operations that fail one of its legs

- **Ref:** `precode/review.md` §11 row 5; `contracts/ports.yaml`.
- **Reproduce:** `python3 a2/c9_dor.py`.
- **Expected vs observed:** row 5 covers "schema, auth, transaction, idempotency, concurrency, error **và evidence**" and is marked ✅ with the evidence "85 operation; 0 mutation thiếu idempotency; 54 operation HTTP có wire contract". I reproduce those three statements exactly. But `scenario_refs` is empty for `auth.logout`, `auth.get_session` and `save.export`, and `error_codes` is empty for `research.get_connector_health` and `health.get_liveness`. `save.export` is defensible (`REQ-OQ10`, deferred to P1); the other four are not annotated anywhere.
- **Impact:** small, but it is the same pattern as F-A2R1-02 — a row marked fully met where the corpus itself would have supported "met with three named exceptions", which is the more useful statement and the one the plan's own tone demands.
- **Remediation constraint:** the row must state the exceptions with their reasons, or the four operations must gain a scenario and error map. The count must come from a script, and the DoR table should carry the exception list rather than a bare ✅.

### F-A2R1-10 — **LOW / INFO** — the invariant-polarity check treats `mixed` as both poles, so three invariants have no scenario declared purely negative

- **Ref:** `evidence/tools/e0_check.py` `E0-11b`; `acceptance/scenarios.yaml` polarity values (`mixed` 23, `negative` 19, `positive` 11).
- **Observed:** I04, I14 and I16 are referenced only by scenarios whose polarity is `positive` or `mixed`; I14 by `mixed` only. `E0-11b`'s oracle accepts `mixed` for both, so it reports every invariant covered.
- **My assessment:** I read SC16 and SC28 in full. The counterexamples are genuinely encoded — `forbidden_effects_vi` names "ghi usage không rõ thành 0" and "coi một attempt là một kết quả", and the oracles are count-zero assertions (`COUNT(analysis WHERE usage_unknown=true AND tokens_in IS NOT NULL) = 0`). **SRC-PLAN §7's substance is satisfied**; I record this as an observation, not a defect.
- **Remediation constraint (advisory):** the check's title claims more than its oracle delivers. Either `mixed` scenarios should declare which assertions are the negative ones, or the check should be renamed to say that `mixed` counts for both, so a reader cannot infer a dedicated counterexample where there is a combined one.

### F-A2R1-11 — **INFO** — the registered E0 run's own file counts are not reproducible, by construction

- **Ref:** `evidence/runs/E0-20260907T004621Z.json` `files_scanned: 168`, `E0-01-parse items_checked: 114`.
- **Observed:** my re-run reports 169 and 115. The tool's `SCAN_DIRS` includes `evidence/`, and the registered run's own output file did not exist when it scanned. Everything else — all 19 statuses, all other item counts, `baseline_hashes`, environment, limitations, summary — is identical.
- **Impact:** none on any verdict; recorded because an auditor comparing counts must not read the delta as drift, and because a registered artefact that cannot reproduce its own scan count is worth stating rather than discovering.
- **Remediation constraint (advisory):** exclude `evidence/runs/` from the scan, or record the count as "before writing this file". No re-run is required.

**Severity counts: CRITICAL 0 · MAJOR 2 · MEDIUM 3 · LOW 4 · INFO 2 · total 11.**

## 6. Verification of every A1 finding, by my own reproduction

| Finding | Sev (A1) | My reproduction | Verdict |
| --- | --- | --- | --- |
| F-A1R1-01 checkpoint has three accounts | MAJOR | `checkpoint` is a single entity owned solely by `MOD-ingest-service`; `run_checkpoint_pointer` removed from `MOD-job-service`; `ingest.commit_checkpoint.state_effects_vi` states the single-owner rule and cites ruling R-01; I02's old counterexample-2 wording is gone | **VERIFIED** |
| F-A1R1-02 fixture actors assert forbidden edges | MAJOR | 318 fixture events swept across all 9 directories: 0 operation/actor violations, 0 `edge_assertion: forbidden` events naming an allowed caller | **VERIFIED** |
| F-A1R1-03 nine entities unowned; `identity_merge_audit` never reported | MAJOR | 60 entities, 63 owner tokens, 3 declared artifacts: **0** entities without an owner, **0** owner tokens without an entity, **0** tokens owned by two modules; `identity_merge_audit` → `MOD-identity-service` | **VERIFIED** |
| F-A1R1-04 two of three §7.3 operations missing | MAJOR | `save.remove`, `data.delete_target`, `data.purge_all` all present; all three cite `REQ-S7.3-05`; the registry row names all three | **VERIFIED** |
| F-A1R1-05 ADR headers undeclared deviation | MINOR | Exemption declared in `precode/adr/README.md` and in `precode/decision-register.md` under ruling R-05; baseline §3 amended accordingly | **VERIFIED** |
| F-A1R1-06 `requirements_csv_contract_header` missing `requirement_refs` | MINOR | Field present (plus a `requirement_refs_note_vi`) | **VERIFIED** |
| F-A1R1-07 `item_fields` entries parse as mappings | MINOR | 0 single-key-mapping list items anywhere in `capabilities.yaml` | **VERIFIED** |
| F-A1R1-08 SC19–SC28 collapsed into one anchor | MINOR | 53 individual anchors SC01–SC53, each with `line`, `subject_vi`, `source_form`; SC19–SC28 subjects match SRC-PLAN §13's list **in order** | **VERIFIED** |
| F-A1R1-09 `REQ-S4-05` does not record the export deferral | MINOR | Row now carries an explicit "CẢNH BÁO PHẠM VI" citing `F-PC00-02`, `REQ-OQ10` and `save.export`'s `deferred_p1` | **VERIFIED** |
| F-A1R2-01 `report_build_id` persisted nowhere | MAJOR | `report_build_id` is a field of the `report` entity; 12 occurrences in `entities.yaml` (was 0); `report.publish.idempotency.key` resolves to it | **VERIFIED** |
| F-A1R2-02 10 of 51 reporting fixture events violate | MAJOR | Covered by the 318-event sweep: 0 violations | **VERIFIED** |
| F-A1R2-03 backfill fixtures assert non-existent columns | MAJOR | `backfill_ledger` now carries `entitlement`, `entitlement_reason`, `subscription_identity_hash`; fixture (j) resolves with no `pending_cr` marker needed | **VERIFIED** |
| F-A1R2-04 CP-07 sanctions what CP-04 and PC02 forbid | MINOR | CP-04, CP-07 and `TXN-checkpoint-only` now state the same rule; the correction and its reason are recorded in place | **VERIFIED** |
| F-A1R2-05 stray `SC29+` anchor label | MINOR | 53 anchors, every label matches `SC\d\d`; no stray | **VERIFIED** |
| F-A1R2-06 `data.purge_all` has no scenario | MINOR | `scenario_refs: [SC44]`; SC44 exists with a two-phase-confirmation oracle and negative cases | **VERIFIED** |
| F-A1R3-01 mandated column gate reported PASS while 89 columns unresolved | MAJOR | My independent re-run under the R4-01 rule: **0 unresolved column occurrences in 0 files**, across all 9 directories | **VERIFIED** |
| F-A1R3-02 `operation_id` vs `operation` key split silently skips PC05 | MINOR | Single key `operation` across all 311 occurrences in all 9 directories; `edge_assertion` convention is documented in the boundary fixture's `event_type_convention_vi` | **VERIFIED** |
| F-A1R3-03 SC45–SC48 unanchored | MINOR | All four anchored; allocation arbitration recorded in `baseline.json.scenario_id_allocation` through SC53 | **VERIFIED** |
| F-A1R3-04 5 telegram fixtures missing from README | MINOR | 18/18 listed; all nine directory READMEs are complete (0 missing across 86 fixtures) | **VERIFIED** |
| F-A1R3-05 undeclared `allOf`/`if-then` deviation | MINOR | `DEV-PC06-01` declared in `x-contract.deviations` with ruling ref R4-04, the two conventions deviated from, and the reason; the E0 tool itself flags that the deviation object uses non-ratified field names — a cosmetic residue, honestly surfaced | **VERIFIED** |

**20 of 20 A1 findings VERIFIED as remediated by my own reproduction. 0 NOT_VERIFIED, 0 PARTIAL.** No regression of any earlier finding was detected by the accumulated checks.

**Were the rulings applied consistently?** Yes, with one exception. R-01 (checkpoint), R-03 (entity naming authority), R-04, R4-01/R4-02/R4-03/R4-04, R5-01 through R5-07 all reproduce in the frozen bytes — including R5-07's four separate obligations (`change-control.md` cites rather than redefines `INV-01..INV-10`; `CONTRACT_ONLY` is gone from every card, surviving only in historical narrative; the card front-matter exception is declared in `agent-tasks/README.md` and `decision-register.md`; all 18 cards re-pinned with 483/483 hashes verifying). The exception is **R5-08**, which required "update `review.md` numbers": four of them are wrong (F-A2R1-02) and one epoch name is stale (F-A2R1-03). `CR-PC04-11`, recorded as closed under that same wave, is not (F-A2R1-01).

## 7. Definition of Ready — SRC-PLAN §17, item by item, on my own evidence

| # | Item | My verdict | My evidence |
| --- | --- | --- | --- |
| 1 | Spec snapshot/hash and atomic registry exist | **MET** | Both source copies under `precode/source/` are byte-identical to the pinned sources (sha256 recomputed); `requirements.csv` has 246 rows with unique ids; all 246 source anchors resolve |
| 2 | All XN/UQ/P0 mapped; remaining ĐX/KC have status and a gate | **MET** | `traceability.csv` 246 rows, id-set equal to the registry, **0 `ORPHAN`**; status distribution XN 144 / UQ 39 / ĐX 48 / KC 15; every KC has a gate row in `gates.yaml` and `review.md` §6.2 |
| 3 | B01–B17 resolved **or** explicitly scoped-blocked | **MET_PROVISIONAL** | All 17 `OPEN` in `agent_profile/registry.json`, all 17 carry a `PROVISIONAL` resolution in the decision register with quoted conflict, oracle change and an "if the Owner rejects" clause; 84 registry rows carry the blocked marker; 14 amendments complete. Explicitly scoped-blocked, not resolved. (review.md self-assesses ❌ — a stricter reading than the plan's wording, and an acceptable one.) |
| 4 | Module ownership, ports, denied edges; negative cases sufficient | **MET_PROVISIONAL** | 25 modules, 99 allowed and 36 forbidden edges; **36↔36 exact bijection** forbidden edge ↔ denied case ↔ sweep event, verified independently; 0 entities unowned. Reduced by F-A2R1-05 (one case's operation unrunnable as written) |
| 5 | Every operation has schema, auth, transaction, idempotency, concurrency, error, evidence | **MET_PROVISIONAL** | 85 operations; every one has `auth_scope`, `state_effects_vi` and a request/response contract source; all 58 mutations carry an idempotency rule; 10/10 auth scopes converge with `capabilities.yaml` and map to the 6 OpenAPI security schemes. Reduced by F-A2R1-09 (3 without scenario, 2 without error codes) |
| 6 | Every error code has a target state, recovery condition and forbidden behaviour | **MET** | 28/28 codes carry `target_states`, `data_kept_vi`, `forbidden_vi`, `oracle_vi`, `scenario_refs`, `retry_class`, `scope`, `invariant_refs`, `requirement_refs` — checked mechanically, no exceptions |
| 7 | Coverage/backfill/pending/tag version and identity/analysis/Saved have race/crash oracles | **MET** | SC08, SC13, SC21, SC22, SC28, SC37, SC38 plus the CAS, crash-mid-builder and concurrent-publisher fixtures; each has a durable-state and forbidden-effects oracle; all fixture files exist |
| 8 | Telegram unknown, CLI capability, backup WAL/restore, secrets unambiguous | **NOT_MET** | Three of four are closed with numbers and oracles. `contracts/telegram/delivery.md` §3.4 holds **five** format limits at `KC` (max message length, callback-data length, parse mode and escape table, buttons per row, send rate limit) under `CR-PC07-04`. No value is fabricated — the correct behaviour — but the item is not met |
| 9 | AC-01–18 and the supplementary SCs have fixtures, oracles, evidence level; amended ACs faithful | **MET_PROVISIONAL** | AC-01…AC-18 map 1:1 onto SC01…SC18; all 53 scenarios have an oracle, durable state, forbidden effects, evidence level, polarity and **at least one fixture that exists on disk** (0 `MISSING`). Reduced by F-A2R1-01 (8 scenarios name operations that do not exist) |
| 10 | E0 actually run with a manifest; E1–E4 recorded `NOT_RUN` | **MET** | I re-ran the tool myself: **19/19 PASS, 0 violations, exit 0**, matching the registered run check for check; `evidence/index.json` holds 55 records, all 55 validating against `evidence/manifest.schema.json`, all `SELF_VALIDATION`, 32 explicit `NOT_RUN` placeholders, `e1_e4_run: 0`; no Worker record claims independent audit, and the index says so in writing |
| 11 | Cards pin baseline, paths/stack, contracts and proof obligations | **NOT_MET** | 18 cards exist and pin exceptionally well — **483/483 pinned hashes and byte counts recompute exactly**, with the deliberate no-hash set for PC09-owned files justified by ruling. But the stack is `ADR-0006` `status: proposed` / `REQ-OQ02` unanswered, so every write-set path is conditional. This is an Owner decision, not a drafting gap |
| 12 | Readiness report lists which modules are READY/BLOCKED | **MET_PROVISIONAL** | `review.md` §9 covers all 25 modules from `modules.yaml` with no omissions or extras, each with a named blocker. Reduced by F-A2R1-02 (the summary line contradicts the table) and F-A2R1-03 (stale pin epoch) |

**DoR summary: MET 5 · MET_PROVISIONAL 5 · NOT_MET 2.**

## 8. Task-card walkthrough (method E) — my own view

I read `TC-collector-checkpoint-resume.md` and `TC-telegram-unknown-delivery.md` end to end against their read sets.

Both are usable by an agent from card plus references alone, and I would not need to guess at communication or state. §0 pins every source and contract with hash and byte count and instructs `sha256sum` before starting, with `STALE` → stop; §2's read set *is* that list; §4 names exact operation ids and states that the card produces none; §5 gives the allowlist and denied paths; §7 maps each error code to a target state and says who retries; §8 gives scenario ids and the oracles; §9 sets the claim ceiling honestly (the collector card forbids claiming the collector works on real X; the SP1 card caps at `LIVE_FEASIBILITY_VERIFIED` "only under the recorded conditions" and forbids inferring AC-01/AC-04); §10 carries stop conditions that include the live blockers (`REQ-OQ01`, B13, `CR-PC07-04`). No card is "build everything" — the 18 split by deliverable exactly as SRC-PLAN §15 requires. The write set is correctly marked PROVISIONAL on ADR-0006 with the statement that only §3 and §8 change if the Owner picks another stack. Ten sections present in both; the front-matter deviation from the baseline §3 contract header is declared in three places.

Two observations, neither a finding: the cards are the strongest artefact in the candidate on the mechanical measure I can apply (483/483 pins), and they are the only place where the current pin epoch is stated correctly (F-A2R1-03).

## 9. Per-package verdicts

| Package | Verdict | Basis |
| --- | --- | --- |
| **PC00** `precode/` baseline, registry, decisions, ADRs, ODR | **PASS** | 246 atomic rows, 0 orphans, all anchors resolve including the 53 individual scenario anchors and I01–I15; 17 blockers × `PROVISIONAL` with amendments; 10 ADRs, 9 `proposed` + 1 `provisional-accepted`; ODR covers B01–B17 plus stack, timezone, defaults, purge scope, PC04/PC08 parameters. Findings F-A2R1-03 (README pin epoch), F-A2R1-07 (I16/I17 not registered), part of F-A2R1-04 — all LOW/MEDIUM traceability, none defeating the package's purpose |
| **PC01** `modules/capabilities/ports/deployment` | **PASS** | 85 operations, 99 allowed + 36 forbidden edges, 36↔36 bijection exact, 0 unowned entities, 0 orphan owner tokens, auth scopes fully converged. All four MAJOR A1 findings against it verified fixed. F-A2R1-05 is MEDIUM and confined to one denied case's operation field plus an undocumented convention |
| **PC02** `data/`, `schemas/`, `identity/` fixtures | **PASS** | 60 entities with owners, 8 transactions, target union, all A1 findings verified fixed including the column-gate MAJOR; 14 identity fixtures with 0 unresolved columns. F-A2R1-06 (LOW) is one unregistered code in a prose guarantee |
| **PC03** `state/*`, `errors.yaml`, `retry-policy.yaml` | **PASS** | 67 transitions across 5 machines, state lint clean, terminal-state rule corrected under R5-04 and consistent; 28 error codes complete on all ten fields; 41 budgets with units and rationale; `PLACEHOLDER_KC` used honestly where `REQ-A6` blocks. No finding of mine lands here |
| **PC04** `reporting/`, `report.schema.json`, reporting fixtures | **PASS** | Coverage windows half-open and contiguous, tag-freeze at publish, backfill entitlement modelled, density worked example present; `PROV-PC04-09` correctly surfaced as contrary to the Coordinator's recommendation rather than buried. Touched by F-A2R1-01 only through SC24 |
| **PC05** `openapi.yaml`, worker/receipt schemas, collector probe | **PASS** (scope-blocked) | 54 HTTP operations 1:1, no internal operation exposed, error envelope set-equal to `errors.yaml`, CSRF on every owner mutation; rate limits held at `null`/`PLACEHOLDER_KC` with the module self-declared not `CONTRACT_READY` — the correct handling of `REQ-A6`. Unvalidated against an OpenAPI 3.1 validator: a stated limitation, not a defect |
| **PC06** `ai/`, `analysis-result.schema.json`, ai fixtures | **PASS** | Three task contracts with per-task input carrying source ids and evidence level; schema closed at every object; `DEV-PC06-01` now declared; 11 adversarial fixtures each landing at a declared check. AC-16 correctly `BLOCKED`, never `FAIL`. Reduced only by F-A2R1-08's coverage note |
| **PC07** `ui/`, `telegram/`, `saved-snapshot.schema.json` | **PASS** (scope-blocked) | 10 screens with resolved operation refs, exactly three commands, `delivery.unknown` faithful to PC03, 18 telegram fixtures all listed and clean, five negative wire fixtures present. `CR-PC07-04` honestly `KC` and honestly blocking — the multipart branch is not claimed |
| **PC08** `ops/`, `recovery/` fixtures | **PASS** (scope-blocked) | Backup on the Online Backup API / `VACUUM INTO` with the WAL hazard stated, manifest and restore-record modelled, dispatch locked until reconciliation, SSRF/loopback rules with oracles; `data.purge_all` exclusions correctly held at `OWNER_DECISION_REQUIRED` rather than guessed |
| **PC09** `scenarios.yaml`, `traceability.csv`, `gates.yaml`, `manifest.schema.json`, `e0_check.py`, `review.md` | **FAIL** | The traceability and evidence work is excellent and reproduces in full — 0 orphans, 0 dangling refs, every scenario with an existing fixture, 55/55 evidence records valid, 19/19 E0 reproduced, gates honestly graded `PARTIALLY_MET`/`NOT_MET`, and §13's eleven self-declared limitations are the most valuable page in the corpus. It fails on evidenced defects in its own deliverables: **F-A2R1-01** (8 scenarios name 9 non-existent operations, in the exact class §13 item 7 declares, while `CR-PC04-11` is reported closed) and **F-A2R1-02** (four headline numbers in the claim-bearing report contradict the artefacts and two of its own tables), plus F-A2R1-04, -08, -09 |
| **PC10** `agent-tasks/`, `change-control.md`, `precode/README.md` | **PASS** | 18 cards, 483/483 pins recompute, ten sections each, honest ceilings, stop conditions carrying the live blockers, `CONTRACT_ONLY` removed per R5-07, `INV-01..INV-10` cited rather than redefined, walkthrough passes on both cards I read. F-A2R1-03's `README.md` half is PC10-owned and is the only mark against it |

## 10. Overall verdict

**FAIL**, scoped to what I checked, at completion ceiling `DRAFT_FOR_REVIEW`.

Not `STALE` — the manifest and every one of its 200 entries were byte-identical at T0 and T1. Not `BLOCKED` — every artefact needed to conclude was readable.

This verdict rests on two MAJOR findings and should be read next to what it does not say. Twenty of twenty findings from three prior independent audits are verified fixed by my own reproduction, with no regression; the 36↔36 denied-edge bijection, the 318-event fixture sweep, the full 246-row traceability chain, the 483 card pins, the 55 evidence records and the 19 E0 checks all reproduce cleanly on my own tooling. The corpus is honest about what it has not done: `E1–E4` are `NOT_RUN` everywhere, no Worker claims an independent audit, `AC-16` is `BLOCKED` rather than `FAIL`, four `KC` items are left empty with gates rather than filled with invented numbers, and `review.md` §13 lists its own blind spots including the one that produced F-A2R1-01.

It fails because a remediation was reported as complete when it covered one of two affected scenarios and six further instances were never swept, and because the readiness report the Owner will be shown contains four numbers that contradict its own tables and the run it cites — both errors in the flattering direction. Neither is a design defect; both are verification defects, in the two documents whose entire job is verification. That is the class of error that matters most here, because every other claim in this baseline is mediated by them.

## 11. Which scopes may be called `CONTRACT_READY` upon Owner ratification

My view, offered as an assessment and not as a grant. None of these is `CONTRACT_READY` **now**: B01–B17 are `OPEN`, and F-A2R1-01/-02 must be remediated on a new epoch and independently verified by a principal who did not author the fix (protocol §8).

**Eligible once the Owner ratifies the named decisions and the two MAJOR findings are cleared:**

1. **Boundaries and rights** — `modules.yaml`, `capabilities.yaml`, `ports.yaml`. Conditions: ratification of `AMD-B12` and B13; an answer to `REQ-OQ01`; F-A2R1-05 corrected; `CR-PC01-09` ruled on. No scenario in F-A2R1-01's set touches this scope.
2. **Data and identity** — `entities.yaml`, `identity.md`, `invariants.md`, `target.schema.json`, `ingest-batch.schema.json`. Conditions: ratification of `AMD-B05`, `AMD-B15` and B06; `CR-PC01-05` closed; SC12's two names and its rejected-operation step corrected; F-A2R1-06 registered. The SQLite partial-index and generated-column assumptions remain untested and belong to E1, which `CONTRACT_READY` does not require.
3. **Workflow and state** — `state/*.yaml`, `errors.yaml`, `retry-policy.yaml`. Conditions: ratification of `AMD-B02`, `AMD-B10` and `PROV-PC03-04`; SC01's `job.enqueue_run` corrected.
4. **Reporting and time** — `time-and-tags.md`, `selection.md`, `report.schema.json`. Conditions: ratification of `AMD-B01`, `AMD-B04`, `AMD-B17` and B14; `PROV-PC04-09` confirmed or rejected; an answer to `REQ-OQ04`; SC24's two names corrected. An uncalibrated similarity threshold does **not** block this scope — what it blocks is any claim of meeting SRC-SPEC §1.4, which the corpus already states.

**Not eligible on ratification alone** — each is blocked by something only the external world can supply, and no amount of drafting or Owner signature clears it:

5. **Collector and paper connector** — `REQ-A6`: four rate-limit values are `PLACEHOLDER_KC`. Also wants an OpenAPI 3.1 validator run.
6. **AI and grounding** — `REQ-A5` unread for every provider, B13 unproven, no adapter through the isolation probe; every adapter is `enabled=false` and AC-16 stays `BLOCKED`.
7. **App, Save and Telegram** — `CR-PC07-04`: five Bot API format limits still `KC`, which blocks the multipart delivery branch.
8. **Operations: secrets, boundary, backup** — the `data.purge_all` exclusion list is `OWNER_DECISION_REQUIRED` with no default, and it is a question, not a parameter. Four of the affected restore scenarios (SC27, SC42, SC43, SC53) also carry F-A2R1-01's wrong operation names.

And a cross-cutting condition: `acceptance/scenarios.yaml` is the shared oracle catalogue for all eight scopes, so F-A2R1-01 must be cleared corpus-wide before *any* scope's evidence leg can be said to hold, even where that scope's own scenarios are clean.

## 12. Limitations

1. **E0 only.** Everything I verified is static consistency of text. No code exists, nothing was executed against a database, no external service was contacted. A reproduced `PASS` proves internal consistency of the checked subset and nothing about runtime — the corpus states this itself and I restate it because a favourable audit is the moment the distinction is most likely to be lost.
2. **No OpenAPI 3.1 validator.** 227 KB of `contracts/http/openapi.yaml` is unverified against the specification. I checked its internal consistency (security schemes, error envelope, operation coverage) but not its conformance.
3. **Reference checks find dangling references, not missing ones.** F-A2R1-01, -06 and -07 are all instances of the *dangling* class, which is the class a checker can find. A relationship nobody wrote down is invisible to every check in this report — mine included.
4. **My prose sweeps use heuristics.** F-A2R1-01's finding set comes from matching `<domain>.<verb>` tokens against known operation domains and filtering entity fields and filenames; a wrong operation name written without backticks, or in a domain that is not an operation domain, would not appear. The finding is therefore a lower bound.
5. **Requirement fidelity was not re-sampled word by word.** I verified the structural properties of all 246 rows and relied on A1-R1's 25-row fidelity sample for wording. A paraphrase that drifts in an unsampled row would not have been caught by either of us.
6. **Writer quiescence was inferred, not enforced.** The session runs in `DOCUMENTARY_DRAFT` with `operational_enforcement_status: NOT_IMPLEMENTED`; there is no OS-level fence. I rely on the declared lease releases plus my own start/end rehash showing zero drift. That is quiescence by observation, as protocol §2 requires be stated.
7. **I judged design semantics by reading.** The identity, transaction, coverage and delivery designs are coherent and well grounded in the sources in my reading, but reading is not execution, and I make no claim about how they behave.
8. **My own tooling is unaudited.** The eleven scripts under `…/scratchpad/a2/` were written by me for this audit and reviewed by no one. Where my result agrees with the project's tool, that is two tools agreeing; where it disagrees (F-A2R1-01, -02, -05, -06), I have quoted the underlying bytes so the disagreement can be checked without trusting my script.

## 13. Completion ceiling statement

The maximum claim supportable by this audit is **`DRAFT_FOR_REVIEW`**, the candidate's own declared ceiling, and no file in the candidate asserts more — I verified that mechanically (0 occurrences of a higher label as an asserted status; the `IMPLEMENTATION_VERIFIED` and `LIVE_FEASIBILITY_VERIFIED` values in the task cards are permitted *future* ceilings under SRC-PLAN §15 item 9, not present claims).

Specifically **not** established by this report: `CONTRACT_READY` for any scope; anything at or above `IMPLEMENTATION_VERIFIED`; any statement about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands and B01–B17 remain `OPEN` in `agent_profile/registry.json`.

All eleven findings are **OPEN**. Per protocol §8 I neither close them nor accept risk on any of them. A Worker may return remediation evidence under a new packet and a new freeze epoch; disposition to `CLOSED` requires the designated authority after independent verification of that new epoch, and that verification may not be performed by the principal who authored the fix. I have not been assigned a re-review turn and will not continue tracking this candidate unless dispatched.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R1` / `PKT-A2-R1`. Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte was written, no git state mutated, no network used, no subagent spawned, and no candidate bytes were supplied for a later self-audit. Manifest `07dcf969f420ebfacddc9226f688d0f862297c2f020d89b9fa464ae15ac449ef` verified identical at start and end of review.*
