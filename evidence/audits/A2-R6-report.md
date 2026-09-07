# AUDIT_REPORT — A2-R6 — scoped re-review of F-A2R5-01…07 on FC-W4 epoch 9

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch **9** |
| Manifest | `…/scratchpad/audits/FC-W4e9-manifest.txt`, **244** entries |
| `manifest_sha256` declared | `29fe13a063b07acd045cb653ecdc57bf188b9ee038bb51269601cbeee63fed13` |
| Recomputed **T0** and **T1** | identical both times — **MATCH**; 244/244 per-entry sha256 + byte counts, 0 missing, 0 drift, order sorted |
| Roles | CANDIDATE 176 · DEPENDENCY 7 · EVIDENCE 59 · SOURCE 2 |
| Completeness | repo holds 246 files; the only two outside the manifest are the declared-historical `project-overview.md` and `master-interview-prompt.md`. The whole `agent_profile/` directory is now included — `registry.json` CANDIDATE, the other seven DEPENDENCY |

**Not `STALE`** — byte-identical across the review interval. **Not `BLOCKED`.**

## 2. Independence

`auditor-A2`, `AUTH-COORD-A2-R6` (parent `AUTH-OWNER-20260907-02`), read-only, lease `null`. I have authored nothing in the repository; the seven archived audit reports under `evidence/audits/` are my own and A1's, copied byte-identically and written before archival. No repository byte written, no `git` mutation, no network, no subagent. Helpers under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`; the E0 tool run with `--json-out` into my scratch directory; both mutations on a full scratch copy, deleted after use. Confirmed at T1: manifest identical, no `__pycache__`/`.pyc` under the repo.

Findings are **OPEN**; a `VERIFIED` verdict from me is a verification verdict, not a disposition (protocol §8).

## 3. Verification table

| Finding | Verdict | My own reproduction on epoch-9 bytes |
| --- | --- | --- |
| **F-A2R5-01** (MAJOR) ratified purge scope unapplied in six artefacts | **VERIFIED** | `TXN-purge-all` now carries three sets that I recomputed as **purged 37 · retained 21 · never_purged 2 = 60**, **pairwise disjoint and covering all 60 entities exactly** — a partition, not a list. All eight artefacts named in the packet cite `OD-20260907-01`; the six that enumerate name **21/21** retained tables; `screens.yaml` and `scenarios.yaml` deliberately do not enumerate and instead point at the single source (`screens.yaml` even forbids "giữ một bản sao danh sách bảng trong mã UI"). Every surviving `OWNER_DECISION_REQUIRED` for purge scope is on a line explicitly framed as history ("chỉ còn giá trị LỊCH SỬ", "**Lịch sử:**", "before_ratification_vi"). Worth recording: when W6 reconciled the sets against `entities.yaml` it found the Coordinator's ruling said "purged (36)" while listing 37, **reported the discrepancy back rather than conforming to it**, and the ruling was corrected (`CR-PC05-07`). That is the behaviour the protocol asks for and it is visible in SC44's notes. |
| **F-A2R5-02** (MEDIUM) closing E0 run stale by two files | **VERIFIED** | I compared all **136** `baseline_hashes` of the registered `E0-20260907T052513Z.json` against the frozen manifest bytes: **0 mismatches, 0 entries absent from the manifest**. My independent run reproduces the registered run with **0 differing checks** across all 24, identical `files_scanned` (210), summary and environment. The run now pins the candidate it certifies. |
| **F-A2R5-03** (MEDIUM) gate satisfiable by a prose mention; denylist eligibility | **VERIFIED (both halves)** | (a) `ratification_ref_of()` now reads **only** the parsed contract header (front-matter, top-level YAML, `x-contract`, `info.x-contract`) with an explicit comment that there is deliberately no regex fallback. I re-ran **M6b** — move the reference out of `contracts/state/storage.yaml`'s header, leave a prose line: **both checks now FAIL**, with the message "carries no `ratification_ref` in its parsed contract header (a prose mention does not count)". (b) Eligibility is now an **allowlist read as data** from `precode/gates.yaml.ratified_contract_scopes` (21 files + 2 directories, four scopes, citing `OD-20260907-01` and my A2-R4 §5), with `contract_ready_eligible()` defaulting to **no**. M5 (out-of-scope claim) still fails correctly. |
| **F-A2R5-04** (MEDIUM) three files ratified outside the four scopes | **VERIFIED** | Adjudicated rather than asserted. `contracts/ops/deployment.md` carries `scope_membership: Boundaries and rights` plus `scope_membership_ruling_vi` citing the Coordinator ruling and this finding by id — the decision now lives in the file's header, not in a source comment. The fixture-README incoherence is resolved in the **right direction**: all 28 fixtures in `identity/` and `reporting/` are themselves raised, each with `claim_ceiling: CONTRACT_READY`, a header `ratification_ref`, and `evidence_status: NOT_RUN` — so no index outranks what it indexes. Census: **49 files at header CONTRACT_READY, every one covered by the allowlist; 0 allowlisted files unraised.** |
| **F-A2R5-05** (LOW) three schemas lacked the NOT_RUN statement | **VERIFIED** | All three now carry a `runtime_evidence` field — `target` and `ingest-batch` as `NOT_RUN` with a note naming E1–E4, `report.schema.json` as a structured object with a per-level `NOT_RUN`. |
| **F-A2R5-06** (LOW) index honesty note false | **VERIFIED, and improved beyond the constraint** | The note now reads: seven reports, in-repo at `evidence/audits/`, byte-identical to the Auditor's originals, still not registered as evidence records **because a Worker may not write a record on an Auditor's behalf** — the principle kept visible. The summary now carries **both** numbers (`independent_audit_reports_archived_in_repo: 7`, `independent_audit_records_in_repo: 0`) with a sentence explaining that they measure different things. |
| **F-A2R5-07** (LOW) manifest silently narrowed | **VERIFIED** | The whole `agent_profile/` directory is back in the manifest — `registry.json` CANDIDATE, the seven others DEPENDENCY. Repo-to-manifest set difference is now exactly the two declared-historical documents. |

**7 of 7 VERIFIED. 0 PARTIAL, 0 NOT_VERIFIED.**

### Judgements the packet asked for explicitly

- **Do both fixture READMEs satisfy the parsed-header rule?** **Yes — and both by the same mechanism.** The packet describes identity as using "a complete `x-contract`" and reporting as using "a top-level header"; in the frozen bytes **both** carry a YAML front-matter block whose **top-level** keys include `claim_ceiling: CONTRACT_READY` and `ratification_ref: OD-20260907-01`. Both parse, both are read by `ratification_ref_of`, and both survive the M6b discipline. The rule in `gates.yaml` names all three acceptable holders, so either shape would have been valid; the description in the packet is what differs from the bytes, not the bytes from the rule.
- **`deployment.md` in scope 1.** Accepted. The argument recorded in its header — that where a module runs and what "ready" means for it *are* boundary contract, not operations documentation — is sound, it is now written where a reader of the file will meet it, and it cites the finding that provoked it. The other `contracts/ops/` files remain correctly ineligible and the `ineligible_note_vi` names them.
- **W6 removing the prose-enumeration comparison from E0-18.** **The right call, correctly disclosed.** The first version produced 24 violations of which ~20 were false (any paragraph mentioning "purge" near five table names matched, and `entities.yaml` matched merely for containing every table name). Removing the sub-check rather than loosening its threshold until it fell silent is the better failure mode: a noisy check teaches readers to ignore its output, which is more durable damage than a documented hole. The hole is documented in two places (`evidence/tools/README.md` §5h, `review.md` §3.9) in the plain form "liệt kê purge trong văn xuôi **chưa được đối chiếu tự động** … Đó là một CR mở, không phải một điều bản này ngụ ý đã xong". What E0-18 does check is the load-bearing part: partition integrity, absence of undecided markers, and the structured lists. I record the residual as a limitation, not a finding.

## 4. Regression sweep

| Check | Result |
| --- | --- |
| Independent E0 run, output to scratch | **24/24 PASS, 0 violations, exit 0** |
| Check-for-check vs registered run | **0 differing checks**; `files_scanned` 210 = 210; `baseline_hashes` identical and pinning the frozen bytes |
| `E0-18-purge-set-agreement` (new) | PASS, 17 items; note records "purged 37 · retained 21 · never_purged 2 · union 60 of 60 entities" — matches my independent recomputation exactly |
| Card pins | **483/483 recompute**; published `sed` command returns exactly one value, `PC10-PIN-OD01c-20260907`, from 18/18 cards |
| Fixture events | 318 events, **0 problems** |
| Denied-edge bijection | 36↔36, callee-ownership rule intact |
| Traceability | 0 dangling refs, 0 missing fixtures, AC-01…18 mapped 1:1 |
| Entity ↔ owner | 0 unowned entities, 0 orphan tokens, 0 double-owned |
| Prose operation tokens across `contracts/` + `acceptance/` | **0 unresolved** |
| Evidence | **60/60 records validate**; `evidence/runs/` fully referenced from `index.json`; **no dangling `…044549Z` references** |
| Review numbers | DoR table parses 10 ✅ / 2 ⚠️ / 0 ❌ = its summary = `numbers.dor`; modules 16 READY / 9 BLOCKED / 7 hard-blocked = the generated keys |
| Gates | G0/G1/G2 `MET`; G3/G4 `PARTIALLY_MET`; G5/SP1 `NOT_MET`; G6/G7 `NOT_APPLICABLE_YET` |

No regression introduced by the fix diff.

## 5. New findings

**None.** CRITICAL 0 · MAJOR 0 · MEDIUM 0 · LOW 0.

Every check I ran against the fix diff and the standing battery reproduces cleanly, and the two mutations the packet mandated both fail as required. This is the first epoch of this candidate against which I have raised no finding.

**Deferred (not findings, recorded so they are not lost):**

1. Prose enumerations of purge tables are not machine-compared (disclosed by W6 as an open CR — see §3). An artefact mistyping a table name mid-sentence would still pass.
2. `E0-06`/`E0-07` still do not scan prose inside `evidence/handoffs/`; unchanged and disclosed.
3. `SC19+` carry no `ac_ref`, which is correct — they are supplementary scenarios.

## 6. Per-scope `CONTRACT_READY` verdict — may each stand unconditionally now?

| Scope | Verdict |
| --- | --- |
| **1. Boundaries and rights** (`modules.yaml`, `capabilities.yaml`, `ports.yaml`, `ops/deployment.md`, +2) | **YES — unconditional.** The `deployment.md` question that qualified my R5 verdict is adjudicated and recorded in the file's header. All six files allowlisted, header-ratified, `NOT_RUN` stated |
| **2. Data and identity** (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schemas, `fixtures/identity/`) | **YES — unconditional.** The R5 condition (missing `NOT_RUN` on two schemas) is cleared; the 14 identity fixtures are raised coherently with the README |
| **3. Workflow and state** (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) | **YES — unconditional.** Unchanged and clean since R5 |
| **4. Reporting and time** (`time-and-tags.md`, `selection.md`, `report.schema.json`, `fixtures/reporting/`) | **YES — unconditional.** The R5 condition on `report.schema.json` is cleared; the 14 reporting fixtures are raised coherently |

Unlike R5, these verdicts are now corroborated by the gate as well as by my own census: `E0-12`/`E0-12b` read an explicit allowlist from data and accept only a parsed header, and I proved both properties by mutation rather than by reading.

**Not eligible, unchanged:** `contracts/http/`, `contracts/ai/`, `contracts/ui/`, `contracts/telegram/`, all `contracts/ops/` except `deployment.md`, the four remaining schemas, and every other fixture directory — each named in `gates.yaml.ineligible_note_vi` so a reader need not infer it.

## 7. Per-package verdicts

PC00 **PASS** · PC01 **PASS** · PC02 **PASS** (the purge partition is the single source and it is exact) · PC03 **PASS** · PC04 **PASS** · PC05 **PASS** (scope-blocked on `REQ-A6`; the stale purge line is gone; `CR-PC05-07` correctly raised the ruling discrepancy) · PC06 **PASS** (scope-blocked) · PC07 **PASS** (scope-blocked on `CR-PC07-04`) · PC08 **PASS** (`secrets.md` and `backup-restore.md` now carry the ratified list) · **PC09 FAIL → PASS** (the closing run pins the frozen bytes; both gate weaknesses fixed and mutation-proven; `E0-18` added; the index honesty note is accurate and its limitation disclosed) · PC10 **PASS** (483/483 pins, epoch unanimous).

## 8. Overall verdict

**PASS**, scoped to what I checked, at completion ceiling `DRAFT_FOR_REVIEW`, with `CONTRACT_READY` supportable **unconditionally in all four ratified scopes**.

All seven A2-R5 findings are verified remediated, and each was closed at the level of mechanism rather than of wording: the purge decision became a set partition with a check that asserts it; the closing run's `baseline_hashes` now equal the frozen manifest; the ratification gate reads a data allowlist and a parsed header, both of which I broke on purpose and watched fail; the scope extension became a header ruling; the manifest recovered its scope. Nothing in the fix diff regressed, and I raise no new finding.

`PASS` means the scope I checked meets its oracle. It is not product acceptance. Ratification settled what is *decided*; it produced no evidence about what *works*, and every KC item and all of E1–E4 stand exactly where they stood before the Owner's interview.

## 9. Residual open items — final list for the Owner

**Closed by `OD-20260907-01`** and verified applied across the corpus: B01–B17 (all 17 `RATIFIED`, registry `open_product_blockers: []`); `REQ-OQ01` (dedicated Chrome profile); `REQ-OQ02` (stack **B** — Python workers + TypeScript web); B08 timezone `Asia/Ho_Chi_Minh`; the `data.purge_all` scope (research data only — 37 purged, 21 retained, 2 never purged, backups **not** deleted and the confirmation dialog required to say so); the OQ default set; the PC04 and PC08 parameter sets; both technical changes.

**Still open — none of these is closable by drafting or by ratification:**

1. **`REQ-OQ03` — provider and model.** The Owner deferred it deliberately; `OWNER_DECISION_REQUIRED`; blocks M3 and `MOD-settings-service`.
2. **`REQ-A6` / `REQ-D34`** — arXiv and OpenAlex call rates: `KC`, four values `PLACEHOLDER_KC` behind a conservative 3000 ms floor. Hard-blocks `MOD-research-connector`. Needs the official documentation.
3. **`CR-PC07-04`** — Telegram Bot API format limits (message length, callback-data length, parse mode and escape table, buttons per row, send rate): `KC`. Hard-blocks `MOD-telegram-adapter` and the multipart delivery branch; keeps DoR item 8 unmet.
4. **`REQ-A5` + adapter isolation** — vendor terms unread, no adapter through the isolation probe, all adapters `enabled=false`. B13 is ratified but **AC-16 remains `BLOCKED`, not `FAIL`**. Hard-blocks `MOD-ai-adapter`, `MOD-analysis-worker`, `MOD-secret-service`.
5. **`REQ-A1`, `REQ-A7`** — collector viability and X account restrictions: `KC`; **SP1 has never run**. Hard-blocks `MOD-x-collector`.
6. **`REQ-A2`, `REQ-A3`, `REQ-D47`, `REQ-OQ08`, `REQ-OQ09`** — embedding threshold, multilingual quality, specific model: `KC` by the Owner's own instruction that these stay unset until measured. Hard-blocks `MOD-embedding-service`.
7. **`REQ-A4`** — whether vector density finds real emerging directions: `KC`; needs 3–4 real reporting periods.
8. **`CR-PC05-03`** — neither source document contains an official documentation URL; none was invented.
9. **No runtime evidence anywhere.** All 56 scenarios `NOT_RUN`; `e1_e4_run: 0`. No code, no collector run, no AI provider call, no Telegram send, no restore drill.
10. **Gates:** G0/G1/G2 `MET`; G3/G4 `PARTIALLY_MET`; G5 `NOT_MET` (no implementation repository exists yet); **SP1 `NOT_MET`**; G6/G7 `NOT_APPLICABLE_YET`. Project status remains **`NOT_READY_FOR_PRODUCT_CODE`**.
11. **`contracts/http/openapi.yaml` (227 KB) has never been checked by an OpenAPI 3.1 validator** — none is available and installing one is out of scope.
12. **Two disclosed check gaps:** purge-table enumerations written in prose are not machine-compared (open CR), and `E0-06`/`E0-07` do not scan prose inside `evidence/handoffs/`.

**No finding from any of the six audit rounds remains open.** Across A1-R1…R3 and A2-R1…R6, 20 + 11 + 4 + 3 + 7 = 45 findings were raised; all are now VERIFIED remediated by independent reproduction. Disposition to `CLOSED` remains the designated authority's, not mine.

## 10. Limitations

E0 only — no code exists and nothing was executed against a database or an external service; a reproduced `PASS` proves internal consistency of the checked subset and nothing about runtime. This was a scoped re-review of seven findings plus the fix diff and my standing battery, not a re-derivation of the full baseline. Mutation testing proves the two checks fire on the two defects I injected, not on every variant. My verification of the Owner's answers remains transcription fidelity against the Coordinator's written record — I have no independent access to the interview. Reference checks find dangling and stale references, not missing ones; the purge prose gap is a live example. Writer quiescence was inferred from declared lease releases plus start/end rehash showing zero drift, not enforced — the session runs `DOCUMENTARY_DRAFT` with `operational_enforcement_status: NOT_IMPLEMENTED`. My own tooling is unaudited; every assertion above quotes the bytes it came from.

## 11. Completion ceiling

Maximum claim supportable: **`DRAFT_FOR_REVIEW`** for the candidate as a whole, and **`CONTRACT_READY`** in the four ratified scopes, unconditionally, upon the designated authority recording it. Not established: anything at or above `IMPLEMENTATION_VERIFIED`; any claim about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands.

I raise no finding in this round. I close none of the 45 raised across the six rounds: a `VERIFIED` verdict is a verification verdict, and disposition requires the designated authority, with the author of a fix barred from verifying it. I have not been assigned a further turn and will not continue tracking this candidate unless dispatched.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R6` / `PKT-A2-R6` (parent `AUTH-OWNER-20260907-02`). Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent; both mutation tests ran on a scratch copy. Manifest `29fe13a063b07acd045cb653ecdc57bf188b9ee038bb51269601cbeee63fed13` verified identical at start and end of review.*
