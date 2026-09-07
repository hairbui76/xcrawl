# AUDIT_REPORT — A2-R5 — verification of the Owner-ratification changes (FC-W4 epoch 8)

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch **8** (ratification epoch) |
| Manifest | `…/scratchpad/audits/FC-W4e8-manifest.txt`, **241** entries |
| `manifest_sha256` declared | `f70100a040146407dc0b117684b4d3209d700d05d5e48f3a9ff4edd4f7e3cfbe` |
| Recomputed **T0** and **T1** | identical both times — **MATCH**; 241/241 per-entry sha256 + byte counts, 0 missing, 0 drift, order sorted |
| Roles | CANDIDATE 176 · DEPENDENCY 4 · EVIDENCE 59 · SOURCE 2 |
| Delta vs epoch 7 | 72 changed · 45 added (the 7 audit reports and 8 manifests into `evidence/audits/`, 22 coordination packets/rulings into `evidence/coordination/`, the `…044549Z` run triple, `precode/owner-decisions.md`) · 6 removed (3 `agent_profile/*`, the `…023000Z` run triple) · `agent_profile/registry.json` DEPENDENCY → CANDIDATE |
| Manifest completeness | repo holds 246 files; 5 are outside the manifest — the 2 declared-historical documents **plus 3 `agent_profile/` files that were entries in epochs 4–7 and are now dropped with no exclusion record** → F-A2R5-07 |

**Not `STALE`** — byte-identical across the review interval. **Not `BLOCKED`.**

## 2. Independence

`auditor-A2`, `AUTH-COORD-A2-R5` (parent `AUTH-OWNER-20260907-02`), read-only, lease `null`. I have authored nothing in the repository. The seven audit reports now inside `evidence/audits/` are copies of my own and A1's reports; I verified all seven are **byte-identical** to the originals in the Coordinator's scratch directory, so no Worker altered an Auditor's words. Their presence does not make me a co-author of the candidate: I wrote them as an Auditor before they were copied, and I have not written or reviewed any candidate byte.

No repository byte written, no `git` mutation, no network, no subagent. Helpers under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`; the E0 tool run with `--json-out` into my scratch directory; all four mutation tests on a full scratch copy (`a2/mut/`, deleted after use). Confirmed clean at T1: manifest identical, no `__pycache__`/`.pyc` under the repo.

Findings are **OPEN**. I close nothing, accept no risk, and supply no patches.

## 3. Evidence records (`INDEPENDENT_AUDIT`, producer `auditor-A2`)

| ID | Procedure | Observed | Exit | Status |
| --- | --- | --- | --- | --- |
| EV-A2R5-01 | `a2/manifest_check.py` at T0 and T1 | declared hash both times, 0 drift | 0 | PASS |
| EV-A2R5-02 | manifest ↔ repo tree; epoch7↔epoch8 diff | 3 `agent_profile/` files silently dropped | 0 | FAIL (scoped) |
| EV-A2R5-03 | Row-by-row diff `OWNER-DECISIONS-20260907.md` ↔ `precode/owner-decisions.md` | **25/25 rows present, 0 missing, 0 extra**; differences are Vietnamese translation per baseline §3; every value preserved (Asia/Ho_Chi_Minh, stack B, N=7, 200 posts/30 min, 08:00/20:00, RPO 24 h / RTO 2 h, Argon2id, 12 h/30 d, purge keep-list, backups not deleted) | 0 | PASS |
| EV-A2R5-04 | `requirements.csv` status sweep | 246 rows; **KC count unchanged at 15** (nothing upgraded on the strength of a decision); D08/D09/D42/D50 ĐX→XN each with an `OD-20260907-01` note; REQ-OQ01/OQ02 → XN "ĐÃ TRẢ LỜI"; **REQ-OQ03 stays ĐX with `OWNER_DECISION_REQUIRED`** | 0 | PASS |
| EV-A2R5-05 | `agent_profile/registry.json` structural diff | `open_product_blockers: []`; `ratified_product_blockers` lists B01–B17; new `ratification_evidence: "precode/owner-decisions.md (OD-20260907-01)"`; `product_status` still `NOT_READY_FOR_PRODUCT_CODE`; `specialist_status DISABLED`, `operational_enforcement_status NOT_IMPLEMENTED`, `session_drafting_mode DOCUMENTARY_DRAFT` unchanged | 0 | PASS |
| EV-A2R5-06 | Header-level `claim_ceiling` census across the whole candidate | **21 files at CONTRACT_READY**: 18 inside the four scopes, **3 outside** | 0 | FAIL (scoped) |
| EV-A2R5-07 | Independent E0 run, output into scratch | **23/23 PASS, 0 violations, exit 0** | 0 | PASS |
| EV-A2R5-08 | Check-for-check diff vs registered `E0-20260907T044549Z.json` | **`baseline_hashes` NOT equal** — 2 of 136 differ (`precode/baseline.json`, `precode/requirements.csv`); `E0-12` 699 vs 697 items. My hashes equal the frozen bytes; the registered run's do not | 0 | FAIL (scoped) |
| EV-A2R5-09 | **Mutation M5** — `contracts/ai/tasks.yaml` → CONTRACT_READY (ineligible scope) | `E0-12` FAIL ×2 (no `ratification_ref`; outside the four scopes) and `E0-12b` FAIL ×1 — **caught** | 1 | PASS |
| EV-A2R5-10 | **Mutation M6b** — move `ratification_ref` out of `contracts/state/storage.yaml`'s header into a prose line | **`E0-12` PASS, `E0-12b` PASS — NOT caught** | 0 | FAIL |
| EV-A2R5-11 | **Mutation M6c** — remove every mention from the same file | `E0-12` FAIL ×2, `E0-12b` FAIL ×1 — caught | 1 | PASS |
| EV-A2R5-12 | Cards: recompute every pinned hash; published pin command | **483/483 verify**; the command returns exactly one value, `PC10-PIN-OD01b-20260907`, from 18/18 cards | 0 | PASS |
| EV-A2R5-13 | `purge_all` keep/delete list across `ports.yaml`, `entities.yaml` TXN-purge-all, `secrets.md`, `backup-restore.md`, fixture `l`, `scenarios.yaml`, `openapi.yaml`, `screens.yaml`, `recovery/README.md` | 2 files updated and ratified; **6 still assert `OWNER_DECISION_REQUIRED` / `PROV-PC01-03`** | 0 | FAIL |
| EV-A2R5-14 | Regression battery (bijection, 318 fixture events, full traceability, entity↔owner, prose tokens, evidence schema) | 36↔36 bijection; 318 events 0 problems; 0 dangling refs; 0 unowned entities / 0 orphan tokens; **0 unresolved prose operation tokens**; **59/59 evidence records valid** | 0 | PASS |
| EV-A2R5-15 | Byte-compare the 7 audit reports copied into `evidence/audits/` | **7/7 identical** to the originals | 0 | PASS |

## 4. Findings

### F-A2R5-01 — **MAJOR** — the ratified `data.purge_all` exclusion list was applied in two contracts and left unapplied in six artefacts, one of which is the acceptance oracle

- **Ref:** applied correctly in `contracts/ports.yaml` (`exclusions_status: ACCEPTED`, `ratification_ref`, full keep-list and rationale) and `contracts/data/entities.yaml` (`TXN-purge-all.tables.retained_by_owner_decision`, 20 tables, `backup_artifacts_rule`, `never_purged`). **Not applied in:** `acceptance/scenarios.yaml` L2122 (SC44's oracle — "**Phạm vi LOẠI TRỪ vẫn `OWNER_DECISION_REQUIRED`** (`PROV-PC00-01` / `PROV-PC01-03`)"); `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` L63 and L256 ("Danh sách LOẠI TRỪ vẫn OWNER_DECISION_REQUIRED … fixture này KHÔNG khẳng định gì"); `acceptance/fixtures/recovery/README.md` L147; `contracts/ops/secrets.md` L321 ("vẫn ở trạng thái **`OWNER_DECISION_REQUIRED`** … File này **không** giải quyết nó"); `contracts/ops/backup-restore.md` L286; `contracts/http/openapi.yaml` L5064; `contracts/ui/screens.yaml` L562–563 (`status: OWNER_DECISION_REQUIRED_SCOPE`).
- **Reproduce:** repo-wide sweep for `OWNER_DECISION_REQUIRED` restricted to `contracts/` and `acceptance/`, then set-compare the keep-list of each artefact against `TXN-purge-all`.
- **Expected vs observed:** the Owner answered item 24 unambiguously — research data only; keep login, secrets, Telegram link, provider config, schedule; backups not deleted. `contracts/modules.yaml` L1703 now asserts "**Không còn phần nào của REQ-S7.3-05 ở trạng thái OWNER_DECISION_REQUIRED**". Six artefacts contradict that assertion. Fixture `l` names only 8 of the 20 retained tables and explicitly declines to assert counts for the rest "vì thêm khẳng định bây giờ là tự quyết thay Owner" — a reason that was correct before the interview and is now false.
- **Impact:** this is the single decision the Owner was warned carried the highest consequence (lock-out risk; data surviving in backups), and it is the one whose propagation is incomplete. SC44 is the acceptance oracle for `data.purge_all`; as frozen, the corpus simultaneously reports the decision as ratified and as pending, and a reader of the fixture would build a test that asserts nothing about the keep-list. No check catches it: there is no rule that a ratified item's `OWNER_DECISION_REQUIRED` markers must be cleared everywhere. The routing appears to be the cause — PC05, PC07, PC08 and the acceptance owner received no fix packet in this wave — so I attribute this to the dispatch, not to those packages' authors.
- **Remediation constraint:** every artefact naming the purge exclusion scope must state the ratified list and cite `OD-20260907-01`, and fixture `l` plus SC44 must assert the full 20-table keep set, the purge set, and the backups-untouched rule with a disclosure oracle. A standing check should assert that no `OWNER_DECISION_REQUIRED` / `PROV-PC00-01` / `PROV-PC01-03` marker survives for an item the ratification record resolves — the general form being: a decision id that appears in `owner-decisions.md` must not appear anywhere as unresolved. Verification must be by an independent principal on a new epoch.

### F-A2R5-02 — **MEDIUM** — the registered closing E0 run is stale against the epoch it certifies

- **Ref:** `evidence/runs/E0-20260907T044549Z.json` `baseline_hashes`.
- **Reproduce:** re-run the tool and set-compare `baseline_hashes`; then hash the two divergent files on disk.
- **Expected vs observed:** of 136 recorded input hashes, **2 do not match the frozen bytes** — `precode/baseline.json` (registered `b1ba31e8…`, frozen `e0405a1b…`) and `precode/requirements.csv` (registered `63aa6b27…`, frozen `fbe59d0e…`). My run's hashes equal the frozen bytes in both cases, and `E0-12` counts 699 items against the registered 697, consistent with `requirements.csv` having grown after the run. PC00-FIX11 evidently landed after PC09-FIX7 executed, and no re-run was registered.
- **Impact:** the verdict is unaffected — I reproduce 23/23 PASS with 0 violations on the frozen bytes, so the conclusion holds. What does not hold is the pinning: the closing evidence artefact for the ratification epoch does not pin the candidate it is offered as certifying, which is precisely the failure `INV-06`/`INV-09` exist to name and which `review.md` §13 item 4 describes as making the record `STALE`. PC09 previously waited for a lease release before its final run for exactly this reason; that discipline lapsed in the wave where it matters most.
- **Remediation constraint:** the closing run must be executed after the last content-bearing packet of the wave and its `baseline_hashes` must equal the frozen manifest bytes for every entry it records; the freeze should not be declared until that equality is checked. A cheap standing guard is to compare the run's `baseline_hashes` against the manifest at freeze time and refuse the freeze on any mismatch.

### F-A2R5-03 — **MEDIUM** — the ratification gate is satisfied by textual presence, and its eligibility rule is a denylist where the ruling states an allowlist

- **Ref:** `evidence/tools/e0_check.py` `contract_ready_eligible()`, `ratification_ref_of()`, checks `E0-12` / `E0-12b`.
- **Reproduce:** mutations M5, M6b, M6c on a scratch copy.
- **Expected vs observed:** (a) **M6b** moved `ratification_ref` out of `contracts/state/storage.yaml`'s header and left a single prose line mentioning the string; both checks **PASSED**, and `E0-12b`'s item count merely dropped by one — the file left the checked set instead of being flagged. Only total absence (M6c) is caught. The oracle is therefore "the string appears somewhere and resolves", not "the contract header carries it" — the same *presence-is-not-sufficient* class that produced `CR-PC01-11` and `F-A2R1-05`. (b) `contract_ready_eligible()` is written as a list of **ineligible** prefixes with a default of eligible for anything under `contracts/` or `acceptance/`. The Owner's record states the inverse — CONTRACT_READY "only in the four scopes A2-R4 named eligible". Under the implemented polarity, any file added under those trees outside the listed prefixes is ratified-eligible by default and no one is told.
- **Impact:** the gate that enforces the boundary of the Owner's ratification can be crossed two ways without failing. (b) is the direct cause of F-A2R5-04. Neither is theoretical: I demonstrated (a) by mutation and (b) is realised today in three files.
- **Remediation constraint:** `ratification_ref` must be read from the file's declared contract header (front-matter, top-level YAML key, or `x-contract`) and nowhere else, and a CONTRACT_READY file whose header lacks it must fail. Eligibility must be expressed as the explicit allowlist of files the Owner ratified, so that a new file is ineligible until someone adds it deliberately. The scope list belongs in a data file that cites `OD-20260907-01`, not in a source comment.

### F-A2R5-04 — **MEDIUM** — three files carry a ratified `CONTRACT_READY` outside the four scopes, two of them above every file they index

- **Ref:** `acceptance/fixtures/identity/README.md` L26, `acceptance/fixtures/reporting/README.md` L33, `contracts/ops/deployment.md` L46. All three appear in the registered `numbers…json` `contract_ready_files` list of 21.
- **Expected vs observed:** the four eligible scopes, as my R1–R4 reports named them and as the Owner's record incorporates by reference, are *boundaries and rights* (`modules.yaml`, `capabilities.yaml`, `ports.yaml`), *data and identity* (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schemas), *workflow and state* (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) and *reporting and time* (`time-and-tags.md`, `selection.md`, `report.schema.json`) — 18 files, all 18 correctly raised. The three additional files were raised by the fixing side. Two of them are directory indexes whose **28 indexed fixtures all remain `DRAFT_FOR_REVIEW`** (identity 14/14, reporting 14/14): an index asserting a higher ceiling than every file it indexes is incoherent, and the index is what a reader consults. `contracts/ops/deployment.md` is carved in by a source comment asserting it "belongs to boundaries and rights"; my reports named three files for that scope and placed Operations in the *not eligible* list, and the other Operations contracts (`secrets.md`, `internet-boundary.md`, `backup-restore.md`) were correctly left at DRAFT.
- **Impact:** the ratification boundary is the Owner's, and it was widened by three files without an Owner or Coordinator ruling. I do not assert that widening is wrong on the merits — a case exists for `deployment.md` as PC01's fourth deliverable, and for fixture READMEs as part of the scopes they serve — but it is an adjudication, not a drafting choice, and it is currently recorded only in a code comment.
- **Remediation constraint:** either the Coordinator issues a ruling extending the ratified scope to these three files (recorded in `owner-decisions.md` or a ruling the record cites, with the fixture-ceiling incoherence resolved by raising the fixtures or lowering the README), or the three revert to `DRAFT_FOR_REVIEW`. Whichever way it goes, the eligible set must become explicit data per F-A2R5-03.

### F-A2R5-05 — **LOW** — three ratified schema files omit the required "runtime evidence is NOT_RUN" statement

- **Ref:** `contracts/schemas/target.schema.json`, `report.schema.json`, `ingest-batch.schema.json` — each carries `x-contract.claim_ceiling: CONTRACT_READY`, `status: accepted` and `ratification_ref: OD-20260907-01`, and contains no `NOT_RUN` statement or equivalent evidence key. The other 18 ratified files carry one.
- **Impact:** small but it is condition (d) of the ratification discipline, and these are the three schemas a consumer is most likely to read as "done".
- **Remediation constraint:** each must carry the same explicit statement the other ratified files carry — that the contract is ratified and E1–E4 remain `NOT_RUN` — in a field a checker can read, and `E0-12b` should assert it rather than leaving it to review.

### F-A2R5-06 — **LOW** — `evidence/index.json`'s honesty note is now false

- **Ref:** `evidence/index.json` `honesty_note_vi`: "Ba AUDIT_REPORT độc lập của auditor-A1 (A1-R1, A1-R2, A1-R3) tồn tại **NGOÀI repo** … và **KHÔNG được đăng ký** ở đây".
- **Observed:** there are now **seven** independent audit reports (A1-R1/R2/R3, A2-R1/R2/R3/R4), they are **inside** the repository under `evidence/audits/`, and all seven are manifest entries with role EVIDENCE. `summary.independent_audit_records_in_repo: 0` remains literally true of *records* but now invites the wrong reading.
- **Impact:** the note was written as a piece of deliberate honesty and has become the opposite through a change made around it — the same staleness class as the earlier "A2 chưa chạy" sentences. It is the note a reader uses to judge how much of the evidence base is self-validation.
- **Remediation constraint:** the note must state what is now true: seven reports, archived in-repo byte-identically, still not registered as evidence records because a Worker may not write a record on an Auditor's behalf — which remains the correct principle and is worth keeping visible. The count should be derived, not written.

### F-A2R5-07 — **LOW** — the manifest silently narrowed its scope

- **Ref:** `FC-W4e8-manifest.txt` header; `agent_profile/README.md`, `examples.json`, `packets.schema.json`.
- **Observed:** these three were entries in the epoch-4 through epoch-7 manifests and are absent from epoch 8. The manifest header carries no `exclusions` record; protocol §6 requires the full scope and its exclusions to be recorded and forbids dropping a dependency needed to conclude. `agent_profile/registry.json` — now a CANDIDATE entry precisely because the ratification modified it — names `packets.schema.json` and `examples.json` in its own `schema_file` / `examples_file` keys.
- **Impact:** low for this review (I needed none of the three to conclude), but a manifest that quietly shrinks between epochs is the one artefact whose completeness the whole scheme rests on.
- **Remediation constraint:** the manifest must carry an explicit exclusions block naming any file dropped from the previous epoch with the reason, or the three must be restored as DEPENDENCY entries.

**Severity counts: CRITICAL 0 · MAJOR 1 · MEDIUM 3 · LOW 3 · total 7.**

## 5. Ratification fidelity and ceiling discipline — summary of the checks the packet named

| Packet item | Result |
| --- | --- |
| 1. Transcription fidelity | **PASS** — 25/25 rows, no deviation, translation only. REQ-OQ03 remains `OWNER_DECISION_REQUIRED`; the KC set is unchanged at 15; nothing KC was upgraded |
| 2. Ceiling discipline (a) in-scope | **FAIL** — 18 of 21 in scope; 3 outside (F-A2R5-04) |
| 2. (b) `ratification_ref` resolving | **PASS** on content — all 21 cite `OD-20260907-01`, which resolves to `precode/owner-decisions.md`; **but the gate accepts a prose mention** (F-A2R5-03) |
| 2. (c) no KC dependency without a note | **PASS** — each ratified file's remaining KC links carry a per-item note; no ratified file depends on `REQ-A5`/`REQ-A6`/`CR-PC07-04` silently |
| 2. (d) states runtime evidence NOT_RUN | **FAIL** for 3 of 21 (F-A2R5-05) |
| 2. nothing claims IMPLEMENTATION_VERIFIED or above | **PASS** — the only such labels are the 18 task cards' permitted future ceilings, which `E0-12` records as a note with the ruling's reasoning, and `agent-tasks/` is outside its scan scope by design |
| 3. Consistency | **PASS** except purge (F-A2R5-01): B01–B17 `RATIFIED`; ADRs `accepted`; ADR-0006 title, `status: accepted`, `ratified_by`, decision = **B**, filename retained with `filename_note_vi`; registry blockers empty with evidence ref and otherwise unchanged; D08/D09/D42/D50 → XN |
| 4. Cards | **PASS** — 483/483 pins recompute; 18/18 declare `PC10-PIN-OD01b-20260907` (the packet says `OD01`; the cards and the published command are the authority, and they agree unanimously — a run-time value under the rule settled in A2-R4, not a defect); §3/§8 rewritten for stack B; stop conditions retain the KC and REQ-OQ03 conditions |
| 5. E0 + mutations | **PARTIAL** — 23/23 reproduced; M5 and M6c caught; **M6b not caught** (F-A2R5-03) |
| 6. Gates / review | **PASS** — G0/G1/G2 `MET`, G3/G4 `PARTIALLY_MET`, G5/SP1 `NOT_MET`; DoR table parses 10 ✅ / 2 ⚠️ / 0 ❌, matching its own summary and `numbers.dor`; module table 16 READY / 9 BLOCKED / 7 hard-blocked, matching; all headline counts reproduce |
| 7. Regression | **PASS** — no regression detected in any prior finding class |

## 6. Definition of Ready — my own assessment on epoch 8

| # | Item | R3 | **R5** | Note |
| --- | --- | --- | --- | --- |
| 1, 2 | snapshot/registry; XN/UQ/P0 mapping | MET | **MET** | 246 rows, 0 ORPHAN |
| 3 | B01–B17 resolved or scoped-blocked | MET_PROV | **MET** | All 17 `RATIFIED` by `OD-20260907-01`; registry blockers empty |
| 4 | ownership, ports, denied edges, negative cases | MET_PROV | **MET** | 36↔36 bijection; the null-operation rule now enforced |
| 5 | every operation complete | MET | **MET** | 85/85 with scenario and error refs |
| 6 | every error code complete | MET | **MET** | 28/28 |
| 7 | race/crash oracles | MET | **MET** | — |
| 8 | Telegram/CLI/backup/secrets unambiguous | NOT_MET | **NOT_MET** | `review.md` marks this ⚠️; I hold **NOT_MET** — one of the four sub-items (Telegram format limits, `CR-PC07-04`) is entirely absent and hard-blocks a module. The difference is a judgement call, recorded rather than argued |
| 9 | AC + SC with fixtures and oracles | MET | **MET_PROVISIONAL** | 56 scenarios all with fixtures and oracles, but SC44's oracle contradicts the ratified purge decision (F-A2R5-01) |
| 10 | E0 run with manifest; E1–E4 NOT_RUN | MET | **MET_PROVISIONAL** | 23/23 reproduced and 59/59 records valid, but the registered run is stale by two files (F-A2R5-02) |
| 11 | cards pin baseline, paths/stack, contracts | NOT_MET | **MET_PROVISIONAL** | Stack B chosen and cards rewritten; 483/483 pins verify; no implementation repo exists yet, so §3 paths remain forward-looking |
| 12 | readiness report per module | MET_PROV | **MET** | 25 modules, counts derived and correct |

**DoR: MET 8 · MET_PROVISIONAL 3 · NOT_MET 1** (R3 was 7 / 3 / 2). The ratification moved items 3, 4 and 11 and is the largest single improvement of the project.

## 7. Per-scope `CONTRACT_READY` verdict

| Scope | May `CONTRACT_READY` stand? |
| --- | --- |
| **Boundaries and rights** (`modules.yaml`, `capabilities.yaml`, `ports.yaml`) | **YES** for the three named files. All ratification conditions met on content; `AMD-B12` and B13 ratified; `REQ-OQ01` answered. `contracts/ops/deployment.md`'s inclusion in this scope is unadjudicated (F-A2R5-04) and must be settled either way |
| **Data and identity** (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schemas) | **YES, conditional** on F-A2R5-05 (the two schemas gaining the NOT_RUN statement). `AMD-B05`, `AMD-B15`, B06 ratified; `TXN-purge-all` correctly carries the ratified keep-list |
| **Workflow and state** (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) | **YES.** `AMD-B02`, `AMD-B10` ratified; `PROV-PC03-04` accepted; all seven files clean on every condition |
| **Reporting and time** (`time-and-tags.md`, `selection.md`, `report.schema.json`) | **YES, conditional** on F-A2R5-05 (`report.schema.json`). `AMD-B01`, `AMD-B04`, `AMD-B17`, B14 ratified; `PROV-PC04-09` accepted as option (b); `REQ-OQ04` answered (N = 7). The threshold remains `uncalibrated`, which does not block the contract but blocks any claim of meeting SRC-SPEC §1.4 |

All four rest on `E0-12`/`E0-12b`, whose oracle I have shown can be satisfied without a header reference (F-A2R5-03); the verdicts above are therefore based on my own file-by-file census, not on the gate's PASS.

**None of the four is undermined by F-A2R5-01**: every stale purge assertion lies in files that are *not* at CONTRACT_READY (`openapi.yaml`, `screens.yaml`, `secrets.md`, `backup-restore.md`, `scenarios.yaml`, fixture `l`). But the ratification cannot be reported to the Owner as *applied* while six artefacts say the decision is still pending.

## 8. Per-package verdicts

PC00 **PASS** (transcription faithful; registry, requirements, ADRs, baseline all correct — though its FIX11 landing after the closing run is the proximate cause of F-A2R5-02) · PC01 **PASS** · PC02 **PASS** (`TXN-purge-all` is the model of how the decision should have been applied everywhere) · PC03 **PASS** · PC04 **PASS** · PC05 **PASS** (stale purge line in `openapi.yaml`; no fix packet was routed to it) · PC06 **PASS** · PC07 **PASS** (stale purge lines in `screens.yaml`; no fix packet routed) · PC08 **PASS** (`secrets.md` and `backup-restore.md` still say the exclusion list is undecided; no fix packet routed — a dispatch omission, not an authoring defect) · PC09 **FAIL** (its own deliverables: the stale registered run, both `E0-12`/`E0-12b` weaknesses, the stale index honesty note, and SC44's contradicting oracle) · PC10 **PASS** (483/483 pins, stack B rewritten, epoch unanimous).

## 9. Overall verdict

**FAIL**, scoped to what I checked, at completion ceiling `DRAFT_FOR_REVIEW`. Not `STALE`, not `BLOCKED`.

The ratification itself is faithfully transcribed and, in the four eligible scopes, correctly applied: 25/25 Owner answers preserved, 17 blockers ratified, the registry cleared with an evidence reference, the stack decision recorded as B with the filename anomaly disclosed, 483 card pins recomputing, and 23/23 E0 checks reproducing on my own run. Nothing KC was upgraded on the strength of a decision and `REQ-OQ03` was correctly left open. That is a large and careful piece of work.

It fails on one MAJOR and three MEDIUM findings that share a shape: the ratification was applied where it was routed and not swept for everywhere it reaches. The Owner's most consequential answer is contradicted by six artefacts including the acceptance oracle that tests it; the closing evidence run does not pin the bytes it certifies; and the gate that guards the ratification boundary can be satisfied by a prose mention and treats eligibility as a denylist. `PASS` cannot be signed while a decision is recorded as both ratified and pending in the same frozen candidate.

## 10. Residual open items — for the Owner

**Now closed by `OD-20260907-01`:** B01–B17 (all 17 `RATIFIED`); `REQ-OQ01` (dedicated Chrome profile); `REQ-OQ02` (stack B); B08 timezone `Asia/Ho_Chi_Minh`; the purge scope decision itself (research data only, backups kept — *subject to F-A2R5-01 propagation*); the OQ default set; the PC04 and PC08 parameter sets; both technical changes. `MOD-data-admin-service` is unblocked in principle.

**Still open:**

1. **`REQ-OQ03` — provider and model.** Deliberately deferred by the Owner; `OWNER_DECISION_REQUIRED`; blocks M3 and `MOD-settings-service`.
2. **`REQ-A6` / `REQ-D34`** — arXiv/OpenAlex call rates: `KC`, four values `PLACEHOLDER_KC`. Hard-blocks `MOD-research-connector`. Ratification does not read documentation.
3. **`CR-PC07-04`** — Telegram Bot API format limits: `KC`. Hard-blocks `MOD-telegram-adapter` and the multipart branch; keeps DoR item 8 unmet.
4. **`REQ-A5` + adapter isolation** — vendor terms unread, no adapter through the probe, all `enabled=false`. B13 is ratified but **AC-16 stays `BLOCKED`**. Hard-blocks `MOD-ai-adapter`, `MOD-analysis-worker`, `MOD-secret-service`.
5. **`REQ-A1`, `REQ-A7`** — collector viability and X account restrictions: `KC`; SP1 has never run. Hard-blocks `MOD-x-collector`.
6. **`REQ-A2`, `REQ-A3`, `REQ-D47`, `REQ-OQ08`, `REQ-OQ09`** — embedding threshold, multilingual quality, specific model: `KC` by the Owner's own instruction that values stay unset until measured. Hard-blocks `MOD-embedding-service`.
7. **`REQ-A4`** — whether vector density finds real emerging directions: `KC`, needs 3–4 real periods.
8. **`CR-PC05-03`** — no official documentation URLs exist in either source; none were invented.
9. **No runtime evidence.** All 56 scenarios `NOT_RUN`; `e1_e4_run: 0`. No code, collector run, AI call, Telegram send or restore drill.
10. **Gates:** G0/G1/G2 `MET`; G3/G4 `PARTIALLY_MET`; G5 `NOT_MET` (no implementation repo yet); **SP1 `NOT_MET`**; G6/G7 `NOT_APPLICABLE_YET`. `NOT_READY_FOR_PRODUCT_CODE` stands.
11. **`contracts/http/openapi.yaml` has never been checked by an OpenAPI 3.1 validator.**
12. **Seven findings from this audit are OPEN** — one MAJOR (`F-A2R5-01`, the purge decision not fully propagated, including SC44's oracle), three MEDIUM (`-02` stale closing run, `-03` gate satisfiable by a prose mention and a denylist eligibility rule, `-04` three files ratified outside the four scopes), three LOW (`-05`…`-07`).

## 11. Limitations

E0 only; no code exists and nothing was executed against a database or an external service. I verified the Owner's answers against the Coordinator's written record, not against the Owner — I have no independent access to the interview, and the record's `evidence_ref` is a session id I cannot open; the fidelity verdict is therefore transcription fidelity, not proof of what was said. My four scopes are the ones my own earlier reports named, and the ratification record incorporates them by reference; where the fixing side read them more broadly (F-A2R5-04) that is a difference of reading, and I have flagged it for adjudication rather than asserting my reading is the Owner's. Mutation testing proves the checks fire or fail to fire on the specific defects I injected. Reference checks find dangling and stale references, not missing ones. Writer quiescence was inferred from declared lease releases plus start/end rehash, not enforced. My own tooling is unaudited; every assertion above quotes the bytes it came from.

## 12. Completion ceiling

Maximum claim supportable: **`DRAFT_FOR_REVIEW`** for the candidate as a whole, with `CONTRACT_READY` supportable in the four named scopes on the conditions in §7. Not established: anything at or above `IMPLEMENTATION_VERIFIED`; any claim about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands.

Ratification changes what is *decided*; it changes nothing about what has been *observed*. Every KC item and all of E1–E4 stand exactly where they stood before the interview, and the seven findings above are **OPEN**. I close nothing and accept no risk; disposition requires the designated authority, and the author of a fix may not verify it.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R5` / `PKT-A2-R5` (parent `AUTH-OWNER-20260907-02`). Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent; all mutation tests ran on a scratch copy. Manifest `f70100a040146407dc0b117684b4d3209d700d05d5e48f3a9ff4edd4f7e3cfbe` verified identical at start and end of review.*
