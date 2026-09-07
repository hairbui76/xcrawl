# AUDIT_REPORT — A2-R2 — verification of F-A2R1-01…11 on FC-W4 epoch 5 (whole baseline)

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch **5** |
| Manifest | `…/scratchpad/audits/FC-W4e5-manifest.txt`, 200 entries |
| `manifest_sha256` declared | `d8ef3c8055971b3f685f4081fc9476955812d5bdd26a5279c051f94d83106551` |
| Recomputed at **start** (T0, `sha256-path-role-hash-bytes-v1`, protocol §6) | identical — **MATCH** |
| Recomputed at **end** (T1) | identical — **MATCH** |
| Per-entry rehash | 200/200 sha256 and byte counts match; 0 missing, 0 drift, order sorted |
| Roles | CANDIDATE 174 · DEPENDENCY 8 · EVIDENCE 16 · SOURCE 2 |
| Sources | unchanged and matching baseline §2 (`f65bb046…707f40`, `d35e1f2d…5e0e26`) |
| Delta vs epoch 4 | **87 files changed**, 1 added (`evidence/runs/E0-20260907T015929Z.json`), 1 removed (the epoch-4 run). Manifest remains complete against the repo tree (same 2 declared-historical files outside). |

**Not `STALE`** — byte-identical across the review interval. **Not `BLOCKED`.**

## 2. Reviewer identity and independence

Principal `auditor-A2`, `AUTH-COORD-A2-R2` / `PKT-A2-R2`, read-only, lease `null`. I have authored nothing in the repository and remain the auditor of record for `A2-R1`; verifying my own findings against someone else's fix is the assigned turn and is not a self-audit of authored bytes.

No repository byte was written, no `git` state mutated, no network used, no subagent spawned. Helper scripts under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`. The E0 tool was run with `--json-out` into my scratch directory. **The mutation test the PC09 worker requested was performed on a full copy of the repository inside my scratch directory** (`a2/mut/`, deleted after use); the real tree was never modified — confirmed by the T1 manifest recomputation and by the absence of any `__pycache__`/`.pyc` under the repo.

All findings are **OPEN**. I close nothing, accept no risk, and supply no patches.

## 3. Evidence records (all `INDEPENDENT_AUDIT`, producer `auditor-A2`)

| ID | Procedure | Expected vs observed | Exit | Status |
| --- | --- | --- | --- | --- |
| EV-A2R2-01 | `a2/manifest_check.py` at T0 and T1 | declared hash both times; 0 drift | 0 | PASS |
| EV-A2R2-02 | manifest ↔ repo tree set-compare; epoch4↔epoch5 manifest diff | 87 changed / 1 added / 1 removed; no in-scope omission | 0 | PASS |
| EV-A2R2-03 | `e0_check.py --repo <repo> --json-out <scratch>` | **22/22 PASS, 0 violations, exit 0** | 0 | PASS |
| EV-A2R2-04 | check-for-check diff vs `evidence/runs/E0-20260907T015929Z.json` | **0 differing checks**; `files_scanned` 168 = 168; `baseline_hashes` (136), environment, limitations, summary all identical | 0 | PASS |
| EV-A2R2-05 | **Mutation test M1** on scratch copy: `backup.reconcile_after_restore` → `backup.reconcile` in `scenarios.yaml` | expected `E0-04b` FAIL; observed **FAIL, 1 violation**, message names the four real `backup.*` operations | 1 | PASS (check is live) |
| EV-A2R2-06 | **Mutation test M2/M3** on scratch copy: `report.content_hash` → `report.contents_hash`; `CONFLICT` → `SAVE_ALREADY_EXISTS` | expected `E0-04c` and `E0-04d` FAIL; observed **both FAIL, 1 violation each**, `E0-04b` correctly unaffected | 1 | PASS (checks are live) |
| EV-A2R2-07 | `a2/c3_alltok.py` — operation-shaped prose tokens across `contracts/` + `acceptance/` | **0 unresolved** (was 9 ids in 8 scenarios) | 0 | PASS |
| EV-A2R2-08 | `a2/c1_edges.py` — denied-edge bijection + callee-owns-operation | 36↔36 exact; NC-28 now `operation: null`; six `EXT-*` cases now covered by a written rule | 0 | PASS (residual → F-A2R2-04) |
| EV-A2R2-09 | `a2/c8_fixev.py` — fixture events | 318 events, **0 problems** | 0 | PASS |
| EV-A2R2-10 | `a2/c10_trace.py` — full traceability chain, 246 rows / 56 scenarios | 0 dangling refs, 0 missing fixtures, AC-01…18 mapped 1:1 | 0 | PASS |
| EV-A2R2-11 | `a2/c5_cards.py` — all card pins | **483/483 recompute** against epoch-5 bytes | 0 | PASS |
| EV-A2R2-12 | `a2/c4_evidence.py` — evidence records vs `manifest.schema.json` | **58/58 valid** | 0 | PASS |
| EV-A2R2-13 | `a2/c6_numbers.py`, `c11_misc.py`, `v_a1r1b.py` — recount every headline number; entity↔owner diff; forbidden strings; auth-scope convergence | all recount **correct** (see §5 F-A2R1-02); 0 unowned entities, 0 orphan tokens; 0 `status: CLOSED/ACCEPTED`; 17/17 blockers `PROVISIONAL`; 10/10 auth scopes converge | 0 | PASS |
| EV-A2R2-14 | `a2/c12_prose_ids.py` — prose-cited error/SC/REQ/I/ADR ids | `SAVE_ALREADY_EXISTS` gone; no unregistered code remains | 0 | PASS |

Runtime identical to the registered run: python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3, linux. No secrets in any output.

## 4. Verification of F-A2R1-01 … 11

| Finding | Verdict | My reproduction on epoch-5 bytes |
| --- | --- | --- |
| **F-A2R1-01** nine non-existent operation ids in 8 scenarios | **VERIFIED** | My own token sweep over `contracts/` + `acceptance/` returns **0 unresolved operation-shaped tokens**. All nine corrected; SC12's rejected `post.mark_source_deleted` step rewritten in terms of the sanctioned field. The remaining mentions of the bad names live only in `precode/review.md` as an explicit `wrong→right` remediation table — documentation, not assertion. A new standing check `E0-04b` exists and I proved it live by mutation (EV-A2R2-05). |
| **F-A2R1-02** four headline numbers contradicting artefacts and own tables | **VERIFIED** | Every number regenerated and now correct on my independent recount: 246 requirements, 85 operations, 99+36 edges, 60 entities, **67** transitions (matching `E0-09.items_checked`), 28 error codes, **86** fixtures across **9** directories, 56 scenarios, 0 orphans, 22/22 E0. Module summary now **"9 READY / 16 BLOCKED / 5 hard"** — exactly my mechanical parse of its own table. DoR summary now **"8 ✅, 2 ⚠️, 2 ❌"** — exactly my parse. Both summaries state they are parsed from the table rather than written beside it. |
| **F-A2R1-03** superseded pin epoch asserted as current | **PARTIAL** | `precode/README.md` now reads "Pin hiện tại: `PC10-PIN-FCW4e-20260907`" **and adds a self-checking instruction** naming the cards as the authority — a better fix than I asked for. `review.md` §9.1 is correct (FCW4e, 18/18 cards agree) and §9.1's history line is correctly historical. **But DoR row 11 still asserts "18 card pin epoch `PC10-PIN-FCW4c-20260907`"** while the cards pin `FCW4e`. → F-A2R2-01. |
| **F-A2R1-04** 15 CRs with no status row; count wrong | **VERIFIED** | The register is now generated: 107 CRs — **90 PC00–PC08, 12 PC09, 5 PC10**, which my independent per-package count reproduces exactly (my R1 figure of "75/85" was my own bucketing bug and I record that correction here). **0 CRs appear in neither `review.md` nor the ODR.** The two material items are dispositioned by Coordinator ruling: `CR-PC01-09` **APPROVED**, `CR-PC02-18` **ACCEPTED_AS_LIMITATION`. I judge disposition-by-ruling to satisfy the remediation constraint: the constraint asked for an explicit ruling recorded where the codes are used, and both the ruling and its rationale are now in `modules.yaml` and `review.md` §8.2. |
| **F-A2R1-05** denied case naming an operation the callee cannot serve | **VERIFIED** | `NC-28` is now `operation: null` with `event_type: in_process_call`, an `operation_absent_reason_vi` that states the direction problem in full, and `expected_error_code` corrected `CAPABILITY_DENIED` → `FORBIDDEN_EDGE` with justification against the R5-01 table. The `EXT-*` convention I asked to be written down or removed is now written into `modules.yaml.default_deny.attempted_edge_operation_rule_vi` as an explicit two-branch rule. Residual: the rule's own branch (a) requires `event_type` on null-operation cases and five of six lack it → F-A2R2-04. |
| **F-A2R1-06** unregistered `SAVE_ALREADY_EXISTS` | **VERIFIED** | Remediated via the second branch I allowed: the guarantee is restated with the registered code `CONFLICT`, which is now listed in `save.create.error_codes` **and** in `SC13.error_refs`. All three artefacts agree; the token is gone from the corpus. `E0-04d` now guards the class and I proved it live by mutation (EV-A2R2-06). |
| **F-A2R1-07** I16/I17 used without the required decision record | **VERIFIED (divergence accepted)** | W1 did **not** add them to `source_anchors.SRC-PLAN` — correctly, since they are not in the plan. Instead: a new `source_anchors.PROJECT` group carrying anchor, title, owning contract, decision-record pointer and the positive/negative scenario ids; decision records `PROV-PC00-05`/`-06` at `decision-register.md` §8.8; `id_conventions.invariant.form` updated to `I01..I17` with the provenance rule spelled out. **This is a better answer than my constraint asked for** — it keeps project-originated ids from being misattributed to a source document — and it satisfies the constraint's substance (a decision record exists, in the register, outside the contract that consumes the invariant). |
| **F-A2R1-08** disclosure narrower than the blind spot | **VERIFIED** | §13 item 5 now carries a nine-row table of files / with-`rows[]` / without-`rows[]` per directory, sourced from a new `E0-15.files_without_rows` field. All nine rows match my measurements exactly (ai 11/2/9, boundary 1/0/1, collection 12/4/8, e2e 1/1/0, identity 14/8/6, recovery 13/3/10, reporting 14/13/1, telegram 18/13/5, ui 2/2/0). The scoping question is dispositioned as `CR-PC02-18` ACCEPTED_AS_LIMITATION. |
| **F-A2R1-09** DoR item 5 asserted met without disclosing exceptions | **VERIFIED** | Both halves addressed, and the underlying gap is now fully closed: **all 85 operations carry `scenario_refs`, and all 85 carry `error_codes`** (`auth.logout`/`auth.get_session` → SC40, SC51; `save.export` → SC12; the two health operations → `INTERNAL`). The row was also downgraded ✅ → ⚠️ with the exceptions named — which has now made the row itself stale in the conservative direction → F-A2R2-02. |
| **F-A2R1-10** `mixed` polarity counted for both poles | **VERIFIED** | `E0-11b`'s oracle is rewritten so **`mixed` counts for neither**, and three new scenarios (SC54, SC55, SC56) supply dedicated negatives. My own check: **17/17 invariants now have a scenario declared `positive` and one declared `negative`**; I04 → SC54, I14 and I16 → SC56. The check was tightened and the corpus made to satisfy it, not the reverse. |
| **F-A2R1-11** registered run's own file count irreproducible | **VERIFIED** | `files_scanned` is **168 in both** the registered run and mine, and `E0-01-parse` is 114 in both. The self-counting artefact is excluded from the scan. |

**11 findings: 10 VERIFIED, 1 PARTIAL, 0 NOT_VERIFIED.**

Both MAJORs are cleared, and cleared in the durable way: each is now guarded by a machine check (`E0-04b/04c/04d`; the number-generation script) rather than by a corrected sentence. I confirmed the three new checks are not decorative by injecting one defect of each class into a scratch copy and watching each fail with a precise message.

## 5. New findings (epoch 5)

All **OPEN**. No patches.

### F-A2R2-01 — **LOW** — three stale sentences in `precode/review.md` contradicted by other sections of the same file

- **Ref:** `precode/review.md` DoR row 11 (line 891); §9 (line 757); §13 item 9 (line 995).
- **Observed:** (a) row 11 asserts "18 card pin epoch `PC10-PIN-FCW4c-20260907`" — the cards pin `FCW4e`, and §9.1 line 812 of the same file says so; (b) §9 still explains that readiness condition (d) fails "vì **A2 chưa chạy**"; (c) §13 item 9 says "**Ba** AUDIT_REPORT độc lập … **A2 chưa chạy.**" — while §4.1, retitled "A2 đã chạy một lần và kết luận PC09 FAIL", correctly reports A2-R1's 11 findings; there are now four independent reports, not three.
- **Coordinator's question answered:** the surviving `FCW4c` mention is a **stale assertion, not a historical note**. §9.1's mention of `FCW4`→`FCW4b`→`FCW4c`→`FCW4d`→`FCW4e` is a correctly-framed succession narrative; row 11 states a bare present-tense fact that is false, inside the DoR table the Coordinator reports to the Owner.
- **Impact:** the same class as F-A2R1-03 and F-A2R1-02 — the regenerated sections are right and the hand-written ones next to them were not swept. Low blast radius, but these three sentences sit in the two tables that carry the report's conclusions.
- **Remediation constraint:** the epoch name in any DoR/readiness row must come from the same derivation as §9.1 (read from the cards), not be transcribed; the A2 status sentences must be derived from one place, since the file already maintains that status correctly in §4.1. A file that states the same fact in four places needs one source for it — which is exactly the `numbers.json` discipline this wave adopted for numbers, applied to statuses.

### F-A2R2-02 — **LOW** — DoR row 5 now understates the artefacts

- **Ref:** `precode/review.md` §11 row 5; `contracts/ports.yaml`.
- **Observed:** row 5 is marked ⚠️ and names five operations as current exceptions (`auth.logout`, `auth.get_session`, `save.export` without `scenario_refs`; `research.get_connector_health`, `health.get_liveness` without `error_codes`). On epoch-5 bytes **all five now carry both fields** — the gap F-A2R1-09 reported was fixed as well as disclosed, and the disclosure was not re-derived afterwards.
- **Impact:** the bias is self-deprecating rather than flattering, which is the safer direction, but the row still does not describe the artefacts and it is one of the two rows that moved the DoR count.
- **Remediation constraint:** row 5's exception list must be generated from `ports.yaml` in the same pass as the numbers, so that a closed gap closes the row. If the row stays ⚠️ for a different reason, that reason must be the one written down.

### F-A2R2-03 — **LOW** — the provenance artefacts for every headline number are not in the frozen candidate

- **Ref:** `precode/review.md` §1 ("mọi con số sau đây kèm khóa nguồn trong `numbers.json`"), §8.2 (`cr_summary.json`), and ~30 parenthetical key citations; `evidence/handoffs/PC09-handoff.md` EV-PC09-05.
- **Observed:** `numbers.json` and `cr_summary.json` exist and are correct — I read them in `…/scratchpad/w6/` and their values match my independent recount — but **neither file is in the repository**, and `review.md` cites them by bare filename with no path and no statement that they live in a Worker scratch directory outside the candidate. `EV-PC09-05` documents the generator, which is the right record; the reader of the frozen candidate still cannot resolve the citation.
- **Impact:** the F-A2R1-02 remediation required the generated numbers be backed by "a script whose output is retained as the evidence record". The retention happened in the Worker's scratch space, consistent with baseline §2's "run helper scripts from your scratch directory" and protocol §9's allowance for tool output in messages. What is missing is the disclosure: a citation that looks like an in-repo artefact and is not.
- **Remediation constraint:** either the two JSON files enter the candidate under `evidence/` and the manifest (making them auditable at frozen bytes), or every citation must name them as scratch artefacts of `EV-PC09-05` with the handoff as the resolvable reference. A number's provenance key is only useful if the thing it keys into can be opened.

### F-A2R2-04 — **LOW** — the new `attempted_edge.operation` rule is violated by five of the six cases it governs, and the check records that as a note rather than a violation

- **Ref:** `contracts/modules.yaml` `default_deny.attempted_edge_operation_rule_vi` branch (a); `denied_cases` NC-08, NC-12, NC-15, NC-22, NC-24; `evidence/tools/e0_check.py` `E0-10b`.
- **Observed:** the rule written this wave says a null operation "phải là `null` kèm `event_type` **và** `operation_absent_reason_vi`". Only **NC-28** — the case the rule was written for — carries `event_type`. The other five carry `operation_absent_reason_vi` only. `E0-10b` detects this and emits exactly those five as **notes**: "NC-12 (edge FE-03) has operation: null without event_type", etc., while reporting `violations: 0`, so the run still shows 22/22 PASS with 0 violations.
- **Impact:** small in substance — the corresponding boundary-sweep events *do* carry `event_type`, so no oracle is unrunnable — but it is the recurring pattern this baseline has been fighting: a rule stated in prose and not enforced by the gate that cites it. A note that nobody must act on is how the FE-20/FE-21 defect and F-A2R1-05 both survived.
- **Remediation constraint:** either the five cases gain `event_type` (matching their sweep events) and `E0-10b` promotes the condition to a violation, or the rule's branch (a) is reworded to require `event_type` only where the sweep event does not already carry it — and `E0-10b` enforces whichever wording survives. A rule and its check must not disagree about what is mandatory.

**Severity counts: CRITICAL 0 · MAJOR 0 · MEDIUM 0 · LOW 4 · total 4.** No regression of any A1 or A2-R1 finding was detected.

## 6. Definition of Ready — SRC-PLAN §17, my own evidence, epoch 5

| # | Item | R1 | **R2** | Evidence |
| --- | --- | --- | --- | --- |
| 1 | Spec snapshot/hash + atomic registry | MET | **MET** | Source copies byte-identical; 246 unique rows; all anchors resolve, now including a `PROJECT` group for project-originated ids |
| 2 | XN/UQ/P0 mapped; ĐX/KC have status and gate | MET | **MET** | 246 rows, id-sets equal, 0 ORPHAN; XN 144 / UQ 39 / ĐX 48 / KC 15, every KC gated |
| 3 | B01–B17 resolved or explicitly scoped-blocked | MET_PROV | **MET_PROVISIONAL** | 17 `OPEN` in the registry, 17 `PROVISIONAL` with amendments and "if the Owner rejects" clauses; 84 registry rows carry the marker |
| 4 | Module ownership, ports, denied edges, negative cases | MET_PROV | **MET_PROVISIONAL** | 36↔36 bijection exact; callee-owns-operation now a written, gated rule; NC-28 corrected. Reduced by F-A2R2-04 |
| 5 | Every operation: schema, auth, transaction, idempotency, concurrency, error, evidence | MET_PROV | **MET** | All 85 operations now carry `scenario_refs` **and** `error_codes`; 58 mutations all with idempotency rules; auth scopes fully converged. (review.md's own row still says ⚠️ — F-A2R2-02) |
| 6 | Every error code: target state, recovery, forbidden behaviour | MET | **MET** | 28/28 complete on all ten fields |
| 7 | Coverage/backfill/pending/tag/identity/analysis/Saved race-crash oracles | MET | **MET** | Unchanged and re-verified |
| 8 | Telegram unknown, CLI capability, backup WAL/restore, secrets unambiguous | NOT_MET | **NOT_MET** | `telegram/delivery.md` §3.4 still holds five format limits at `KC` (`CR-PC07-04`). No value fabricated |
| 9 | AC-01–18 + supplementary SCs with fixtures, oracles, evidence level | MET_PROV | **MET** | 56 scenarios, all with an existing fixture and full oracle; AC 1:1 onto SC01–SC18; **0 unresolved operation tokens** |
| 10 | E0 actually run with manifest; E1–E4 `NOT_RUN` | MET | **MET** | 22/22 reproduced check-for-check; 58/58 evidence records valid; `e1_e4_run: 0`; `independent_audit_records_in_repo: 0` |
| 11 | Cards pin baseline, paths/stack, contracts, proof obligations | NOT_MET | **NOT_MET** | 483/483 pins recompute exactly; stack still unchosen (`ADR-0006` `proposed`, `REQ-OQ02`) — an Owner decision |
| 12 | Readiness report lists modules READY/BLOCKED | MET_PROV | **MET_PROVISIONAL** | All 25 modules, counts now correct and mechanically derived. Reduced by F-A2R2-01 |

**DoR: MET 7 · MET_PROVISIONAL 3 · NOT_MET 2** (R1 was 5 / 5 / 2).

## 7. Per-package verdicts

| Package | R1 | **R2** | Basis |
| --- | --- | --- | --- |
| PC00 | PASS | **PASS** | I16/I17 decision records + `PROJECT` anchor group; README pin corrected and hardened with a "verify this line" instruction; CR register complete |
| PC01 | PASS | **PASS** | NC-28 corrected; `attempted_edge.operation` rule written and gated; `CR-PC01-09` approved by ruling. Residual F-A2R2-04 is LOW |
| PC02 | PASS | **PASS** | `SAVE_ALREADY_EXISTS` resolved to `CONFLICT` consistently across entity, port and scenario; entity↔owner sets still exactly closed |
| PC03 | PASS | **PASS** | 67 transitions, state lint clean, 28 error codes complete |
| PC04 | PASS | **PASS** | SC24 operation names corrected; reporting fixtures unchanged in substance |
| PC05 | PASS (scope-blocked) | **PASS (scope-blocked)** | `REQ-A6` rate limits still `PLACEHOLDER_KC` with the module self-declared not `CONTRACT_READY`; still no OpenAPI 3.1 validator |
| PC06 | PASS | **PASS** | Unchanged; AC-16 still correctly `BLOCKED` |
| PC07 | PASS (scope-blocked) | **PASS (scope-blocked)** | `CR-PC07-04` still `KC` and still blocking, honestly |
| PC08 | PASS (scope-blocked) | **PASS (scope-blocked)** | `data.purge_all` exclusions still `OWNER_DECISION_REQUIRED`; restore scenarios' operation names corrected |
| **PC09** | **FAIL** | **PASS** | Both MAJORs cleared and converted into standing machine checks that I proved live by mutation; numbers generated and correct; polarity oracle tightened rather than the corpus loosened; disclosure table now exact. §4.1 states the failure and its cause in the first person without hedging. Residual findings are four LOW |
| PC10 | PASS | **PASS** | 483/483 pins recompute on new bytes; epoch names consistent in the cards and in `agent-tasks/README.md` |

## 8. Overall verdict

**PASS**, scoped to what I checked, at completion ceiling `DRAFT_FOR_REVIEW`. Not `STALE`, not `BLOCKED`.

Ten of eleven A2-R1 findings are verified remediated and the eleventh is PARTIAL on one sentence. Every prior audit finding — 20 from A1, 11 from A2-R1 — is now either verified or reduced to a named LOW residual. The two MAJORs were fixed at the level of mechanism rather than of wording: three new prose-token checks that I confirmed catch injected defects, a number-generation script whose output I recounted independently and found correct in every field, and a polarity oracle that was tightened while the corpus was made to satisfy it.

`PASS` here means the scope I checked meets its oracle. It is **not** product acceptance and not `CONTRACT_READY`: B01–B17 remain `OPEN`, four `KC` items still require the outside world, and no runtime evidence exists anywhere.

## 9. Residual open items — for the Coordinator to carry verbatim to the Owner

1. **B01–B17 are all `OPEN`** in `agent_profile/registry.json`; every proposed resolution is `PROVISIONAL` and 84 of 246 registry rows carry text that changes if the Owner rejects the corresponding amendment. Fourteen amendments (`AMD-B01`…`AMD-B17`) await ratification; B06, B13 and B14 need a decision without a written amendment.
2. **`REQ-OQ01` — confirm D09 (a project-specific Chrome profile).** Blocks milestone M0, gate SP1 and `MOD-x-collector`. No default can be chosen for the Owner.
3. **`REQ-OQ02` — choose the stack** (`ADR-0006` recommends Option A / Python, status `proposed`). Blocks M1, gate G5 and the build/test paths in all 18 task cards; DoR item 11 cannot be met until it is answered.
4. **`REQ-OQ03` — the specific provider and model for labelling and for summary.** `OWNER_DECISION_REQUIRED` with **no** provisional default; blocks `MOD-settings-service` and M3.
5. **`PROV-PC00-01` / `PROV-PC01-03` — what `data.purge_all` must *not* delete.** `OWNER_DECISION_REQUIRED`, no default. Two consequences the Owner must weigh first: purging the login credential can lock the Owner out (D05 forbids signup and automatic password recovery), and purged data survives in backups until those backups are deleted. Blocks `MOD-data-admin-service`.
6. **`REQ-A6` / `REQ-D34` — arXiv and OpenAlex call rates and identification requirements.** `KC`. Four rate-limit values are `null` / `PLACEHOLDER_KC` behind one conservative floor (`min_interval_ms = 3000`). Requires reading the official documentation; this session has no network. Hard-blocks `MOD-research-connector`.
7. **`CR-PC07-04` — Telegram Bot API formatting limits.** `KC`: maximum message length, callback-data length, parse mode and escape table, buttons per row, send rate limit. Hard-blocks `MOD-telegram-adapter` and the multipart delivery branch of `telegram/delivery.md` §3.4.
8. **`REQ-A5` + B13 — each AI vendor's terms for the CLI/ACP path, and provable tool/file/network isolation.** `KC`. No adapter has passed the isolation probe, every adapter is `enabled=false`, and **AC-16 is therefore `BLOCKED`, not `FAIL`**. Hard-blocks `MOD-ai-adapter` and `MOD-analysis-worker`.
9. **`CR-PC05-03` — official documentation URLs for arXiv/OpenAlex.** Neither source document contains a URL; PC05 recorded document identifiers and invented no URL. Needs an Owner-supplied URL or acceptance that it is determined at implementation time.
10. **`REQ-A1`, `REQ-A2`, `REQ-A3`, `REQ-A4`, `REQ-A7`, `REQ-D47`, `REQ-OQ08`, `REQ-OQ09` remain `KC`** — collector viability, embedding threshold, multilingual embedding quality, whether vector density finds real emerging directions, X's account restrictions, the specific embedding model. Each has a gate; none may be declared met by drafting.
11. **No runtime evidence exists.** All 56 scenarios are `NOT_RUN`; E1–E4 have never run; `evidence/index.json` records `e1_e4_run: 0`. No code, no collector run, no AI provider call, no Telegram send, no restore drill.
12. **Gate status:** G0/G1/G2 `MET_PROVISIONAL`, G3/G4 `PARTIALLY_MET`, G5 `NOT_MET`, **SP1 `NOT_MET`** (the X feasibility probe has not been run), G6/G7 `NOT_APPLICABLE_YET`. Project status stays **`NOT_READY_FOR_PRODUCT_CODE`**.
13. **`contracts/http/openapi.yaml` (227 KB) has never been checked by an OpenAPI 3.1 validator** — none is available and installing one is out of scope. Internal consistency was verified; specification conformance was not.
14. **Four LOW findings from this audit are OPEN** (F-A2R2-01…04): three stale sentences in `review.md` including a superseded pin epoch in DoR row 11; DoR row 5 understating the artefacts; `numbers.json`/`cr_summary.json` cited but living outside the candidate; the new null-operation rule unmet by five of six cases with the check recording it as a note.
15. **Column gate coverage:** the `rows[]` field-existence check does not reach 41 of 86 fixtures (disclosed exactly, per directory); `CR-PC02-18` is dispositioned `ACCEPTED_AS_LIMITATION` by the Coordinator. `E0-06`/`E0-07` still do not scan prose inside `evidence/handoffs/`.

## 10. `CONTRACT_READY` upon Owner ratification — updated view

Unchanged in shape from R1, and now with a cleaner path: the cross-cutting blocker I raised in R1 (`scenarios.yaml` carrying non-existent operation names, which touched every scope's evidence leg) is **cleared**.

**Eligible on Owner ratification of the named decisions** — all four now have no open MAJOR or MEDIUM finding against them:

1. **Boundaries and rights** (`modules.yaml`, `capabilities.yaml`, `ports.yaml`) — ratify `AMD-B12`, B13; answer `REQ-OQ01`. F-A2R2-04 is LOW and does not block.
2. **Data and identity** (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schemas) — ratify `AMD-B05`, `AMD-B15`, B06; close `CR-PC01-05`. SQLite partial-index and generated-column assumptions remain an E1 matter, not a `CONTRACT_READY` condition.
3. **Workflow and state** (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) — ratify `AMD-B02`, `AMD-B10`, `PROV-PC03-04`.
4. **Reporting and time** (`time-and-tags.md`, `selection.md`, `report.schema.json`) — ratify `AMD-B01`, `AMD-B04`, `AMD-B17`, B14; confirm or reject `PROV-PC04-09`; answer `REQ-OQ04`. An uncalibrated similarity threshold does not block the contract; it blocks any claim of meeting SRC-SPEC §1.4.

**Not eligible on ratification alone** — each blocked by a fact only the outside world supplies: **Collector and paper connector** (`REQ-A6`), **AI and grounding** (`REQ-A5` + B13; AC-16 `BLOCKED`), **App, Save and Telegram** (`CR-PC07-04`), **Operations: secrets, boundary, backup** (`PROV-PC00-01` purge exclusions).

Protocol §8 applies to all eight: no scope becomes `CONTRACT_READY` while a finding against it is `OPEN` or `FIX_PROPOSED`, and the verifier of any fix may not be its author.

## 11. Limitations

1. **E0 only.** No code exists; nothing was executed against a database or an external service. My `PASS` proves internal consistency of the checked subset and nothing about runtime.
2. **No OpenAPI 3.1 validator** (see residual item 13).
3. **Reference checks find dangling references, not missing ones.** All four of my new findings are of the *dangling or stale* class, which is the class a checker can find. A relationship nobody wrote down is invisible to every check in this report.
4. **My prose sweeps are heuristic** and give a lower bound; a wrong name written without backticks would not appear.
5. **Mutation testing proves the three new checks fire on the defect classes I injected**, not that they fire on every variant of those classes. I injected one instance per check.
6. **I did not re-verify requirement wording** against the sources this round; the 246 rows were checked structurally and I rely on A1-R1's 25-row fidelity sample.
7. **Writer quiescence was inferred, not enforced** — `DOCUMENTARY_DRAFT`, `operational_enforcement_status: NOT_IMPLEMENTED`. I rely on the declared lease releases plus start/end rehash showing zero drift.
8. **My own tooling is unaudited.** Where I disagree with the fixing side I have quoted the underlying bytes so the disagreement can be checked without trusting my scripts. I also correct one error of my own from R1: the "75 CRs" figure in F-A2R1-04 came from a bucketing bug in my script; the correct count was 90 and the review's number was right. The substance of that finding — 15 CRs with no status row — was independently confirmed at the time and has since been remediated.

## 12. Completion ceiling statement

The maximum claim supportable by this audit is **`DRAFT_FOR_REVIEW`**. Verified mechanically: no file asserts more (the `IMPLEMENTATION_VERIFIED` / `LIVE_FEASIBILITY_VERIFIED` values in task cards are permitted *future* ceilings under SRC-PLAN §15 item 9, not present claims).

Not established: `CONTRACT_READY` for any scope; anything at or above `IMPLEMENTATION_VERIFIED`; any statement about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands; B01–B17 remain `OPEN`.

The four new findings are **OPEN**; the eleven from A2-R1 are ten **VERIFIED** and one **PARTIAL**, and a `VERIFIED` verdict from me is a verification verdict, **not** a disposition. Per protocol §8, moving any finding to `CLOSED` requires the designated disposition authority, and the author of a fix may not verify it. I have not been assigned a further turn and will not continue tracking this candidate unless dispatched.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R2` / `PKT-A2-R2`. Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent; the mutation test ran entirely on a scratch copy. Manifest `d8ef3c8055971b3f685f4081fc9476955812d5bdd26a5279c051f94d83106551` verified identical at start and end of review.*
