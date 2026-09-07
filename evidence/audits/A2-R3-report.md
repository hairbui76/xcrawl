# AUDIT_REPORT — A2-R3 — scoped re-review of F-A2R2-01…04 on FC-W4 epoch 6

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch **6** |
| Manifest | `…/scratchpad/audits/FC-W4e6-manifest.txt`, **202** entries |
| `manifest_sha256` declared | `228bf15d0906b92b410a2849c26daf50f5dfbc470cc10aaca3ebc951b9974ab8` |
| Recomputed at **start** (T0) and **end** (T1), algorithm `sha256-path-role-hash-bytes-v1` | identical both times — **MATCH** |
| Per-entry rehash | 202/202 sha256 and byte counts match; 0 missing, 0 drift, order sorted |
| Roles | CANDIDATE 174 · DEPENDENCY 8 · **EVIDENCE 18** (was 16) · SOURCE 2 |
| Delta vs epoch 5 | 31 files changed; **3 added** (`evidence/runs/E0-20260907T021812Z.json`, `numbers-20260907T021812Z.json`, `cr_summary-20260907T021812Z.json`); 1 removed (the epoch-5 run). Repo tree holds 204 files; the 2 not in the manifest are the declared-historical documents. Complete. |

**Not `STALE`** — byte-identical across the review interval. **Not `BLOCKED`.**

## 2. Independence

`auditor-A2`, `AUTH-COORD-A2-R3` / `PKT-A2-R3`, read-only, lease `null`. I have authored nothing in the repository. No repository byte written, no `git` mutation, no network, no subagent. Helpers under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`; the E0 tool run with `--json-out` into my scratch directory; the E0-10b mutation test performed on a full scratch copy (`a2/mut/`, deleted afterwards). Confirmed clean: T1 manifest identical, no `__pycache__`/`.pyc` anywhere under the repo.

Findings are **OPEN**; a `VERIFIED` verdict from me is a verification verdict, not a disposition (protocol §8).

## 3. Evidence records (`INDEPENDENT_AUDIT`, producer `auditor-A2`)

| ID | Procedure | Observed | Exit | Status |
| --- | --- | --- | --- | --- |
| EV-A2R3-01 | `a2/manifest_check.py` at T0 and T1 | declared hash both times, 0 drift | 0 | PASS |
| EV-A2R3-02 | epoch5↔epoch6 manifest diff; manifest ↔ repo tree | 31 changed / 3 added / 1 removed; no in-scope omission | 0 | PASS |
| EV-A2R3-03 | `e0_check.py --repo <repo> --json-out <scratch>` | **22/22 PASS, 0 violations, exit 0** | 0 | PASS |
| EV-A2R3-04 | check-for-check diff vs `evidence/runs/E0-20260907T021812Z.json` | **0 differing checks**; `files_scanned` 168 = 168; `baseline_hashes` identical | 0 | PASS |
| EV-A2R3-05 | **Mutation M4** on scratch copy: delete `event_type` from `NC-12` | expected `E0-10b` FAIL; observed **FAIL, 1 violation**: *"NC-12 (edge FE-03) has operation: null without 'event_type', which default_deny.attempted_edge_operation_rule_vi branch (a) makes mandatory"* — the promotion from note to violation is live | 1 | PASS |
| EV-A2R3-06 | `a2/c1_edges.py` — denied-edge bijection; `null` cases carry `event_type` + reason | 36↔36 exact; **6/6 null-operation cases now carry both**; E0-10b's five "without event_type" notes are gone | 0 | PASS |
| EV-A2R3-07 | `a2/c5_cards.py` — recompute every card pin | **483/483 verify** on epoch-6 bytes; 21 files in `agent-tasks/` declare `PC10-PIN-FCW4f-20260907` | 0 | PASS |
| EV-A2R3-08 | Epoch-name consistency across `precode/README.md`, `agent-tasks/README.md`, `precode/review.md` | README files current (`FCW4f`) with history correctly framed; `review.md` disagrees with itself → F-A2R3-01 | 0 | FAIL (scoped) |
| EV-A2R3-09 | `a2/c4_evidence.py` — records vs `manifest.schema.json`; new artefacts registered | **58/58 valid**; all three new `evidence/runs/` files referenced from `index.json` | 0 | PASS |
| EV-A2R3-10 | Recount review.md headline numbers vs artefacts and vs `numbers-20260907T021812Z.json` | DoR table parse **9 ✅ / 1 ⚠️ / 2 ❌** = its summary = `numbers.dor`; module table **9 / 16 / 5** = its summary; `dor5` = `{without_scenario_refs: [], without_error_codes: [], exceptions_total: 0}` matches `ports.yaml` | 0 | PASS |
| EV-A2R3-11 | `a2/c8_fixev.py`, `c10_trace.py`, prose-token sweep over `contracts/` + `acceptance/` | 318 fixture events 0 problems; 0 dangling refs, 0 missing fixtures; **0 unresolved operation-shaped prose tokens** | 0 | PASS |

## 4. Verification table

| Finding | Verdict | My reproduction on epoch-6 bytes |
| --- | --- | --- |
| **F-A2R2-04** null-operation rule unmet by 5 of 6 cases; check recorded it as a note | **VERIFIED** | All six null-operation denied cases now carry `event_type` **and** `operation_absent_reason_vi` (NC-08/12/22/24 `local_observation`, NC-15/28 `in_process_call`), consistent with their sweep events. `E0-10b`'s oracle text now states the callee-ownership and `EXT-*` branches explicitly, and the five notes are gone. I confirmed the promotion is real, not cosmetic, by deleting `event_type` from NC-12 on a scratch copy: the check **failed with a violation** naming the rule branch. Rule and gate now agree. |
| **F-A2R2-02** DoR row 5 understating the artefacts | **VERIFIED** | Row 5 is now ✅ with the generated key `dor5` and states "0 thiếu `scenario_refs`, 0 thiếu `error_codes`, 0 mutation thiếu khai báo idempotency", plus a note that the five named exceptions were closed in FIX6/FIX7. I re-derived all three counts from `ports.yaml`: all zero. The DoR count moved 8/2/2 → **9/1/2**, which matches both the table and `numbers.dor`. |
| **F-A2R2-03** provenance artefacts outside the candidate | **VERIFIED** | `numbers-20260907T021812Z.json` and `cr_summary-20260907T021812Z.json` are now **in the repository** under `evidence/runs/`, in the manifest (EVIDENCE role, taking the count 200 → 202), registered in `evidence/index.json`, and cited **by full path** in review.md's opening note. I read the registered `numbers` file and every value I recount agrees with it. |
| **F-A2R2-01** three stale sentences contradicting the same file | **PARTIAL** | (b) **fixed** — §9 now reads "điều kiện (d) vẫn sai — **không phải vì A2 chưa chạy**, mà vì bốn finding còn OPEN". (c) **fixed** — §13 item 9 now says "**5** AUDIT_REPORT độc lập" and names all five. A new §4.1 was created as the declared single source of truth for audit status, which is the right structural answer. (a) **not fixed** — DoR row 11 still carries a superseded epoch → F-A2R3-01. |
| **F-A2R1-03** (PARTIAL since R2) superseded pin epoch asserted as current | **PARTIAL** (unchanged) | The residual has moved from `FCW4c` to `FCW4e` but sits in the same DoR row 11. Everything else is current and correctly framed. |

**Verified 3 · Partial 2 · Not verified 0.**

## 5. New findings (fix diff only)

### F-A2R3-01 — **LOW** — DoR row 11 asserts a superseded epoch while claiming to be derived from the key whose registered value contradicts it

- **Ref:** `precode/review.md` DoR row 11 (line 919) vs §9.1 (line 838); `evidence/runs/numbers-20260907T021812Z.json`.
- **Observed:** row 11 reads "18 card pin epoch **`PC10-PIN-FCW4e-20260907`** (`card_pin_current` — đọc từ card, cùng nguồn với §9.1, KHÔNG chép tay)". §9.1 of the same file prints **`PC10-PIN-FCW4f-20260907`** from that same key, and the registered artefact says `card_pin_current: "PC10-PIN-FCW4f-20260907"`, `card_pin_declared: {"PC10-PIN-FCW4f-20260907": 18}`, `card_pin_unanimous: true`. All 18 cards declare `FCW4f`; I verified that directly and all 483 pins recompute.
- **The Coordinator's question, answered: this is a stale assertion, not an acceptable run-time value.** The run-time defence would hold if the document printed one value once, as of a stated instant, with the derivation rule beside it. Here the same document prints two different values for the same key, and the one in the Owner-facing DoR table is the wrong one. Worse, row 11 now carries an explicit provenance claim — "read from the cards, same source as §9.1, not transcribed" — which the registered artefact falsifies: had it been read, it would say `FCW4f`. A false provenance claim is a stronger defect than the bare stale value F-A2R1-03 originally reported, because it tells a reader not to check.
- **Impact:** low in blast radius, but it is the third consecutive epoch in which this one row has been wrong, and the row sits in the table the Coordinator carries to the Owner.
- **Remediation constraint:** row 11 must not restate the epoch at all — it should point to §9.1, which already derives it — or it must be emitted by the same generator pass in the same run as §9.1, so the two cannot diverge. The general rule this baseline already adopted for numbers and then for statuses must extend to this row: one fact, one source, emitted once. Any wave that re-pins the cards after `review.md` is generated must re-emit both places or state the ordering explicitly.

### F-A2R3-02 — **LOW** — the derivation command documented as the authority does not return what §9.1 says it returns

- **Ref:** `precode/review.md` §9.1, the fenced command block; `agent-tasks/TC-*.md` line 26.
- **Observed:** §9.1 presents `grep -ho "PC10-PIN-[A-Za-z0-9-]*" agent-tasks/TC-*.md | sort -u` as the authority and states "Tại thời điểm chạy bản này lệnh đó trả **`PC10-PIN-FCW4f-20260907`**". I ran it verbatim: it returns **seven** values — `PC10-PIN-20260907`, `FCW4`, `FCW4b`, `FCW4c`, `FCW4d`, `FCW4e`, `FCW4f` — because each card's pin line names the current epoch *and* every superseded one on the same line. The generator evidently uses a stricter rule (the first token on the `**Pin epoch:**` line), which is how it produced `card_pin_declared: {FCW4f: 18}`.
- **Impact:** §9.1's entire argument is "do not trust the transcription, run this command". A reader who runs it gets an ambiguous list and no way to tell which is current. This is the same failure mode as F-A2R3-01 one level up: the stated rule and the enforced rule differ.
- **Remediation constraint:** the published command must be the one the generator actually applies, and running it must yield exactly one value; if the rule depends on position within the pin line, the command must encode that. Whatever is printed must be executable by a reader and must reproduce `card_pin_current`.

### F-A2R3-03 — **LOW** — an unrendered format string in the newly created single-source-of-truth block for audit status

- **Ref:** `precode/review.md` §4.1, line 363.
- **Observed:** the section reads verbatim: `**%d AUDIT_REPORT độc lập đã chạy** (`audit_reports`, đếm từ đĩa): %s.` The `%d` and `%s` placeholders were never substituted. The values exist in the registered artefact (`audit_reports` is a five-element list naming A1-R1/R2/R3 and A2-R1/R2), and the table immediately below the sentence is complete and correct, so no information is lost — but the headline sentence of the block is broken.
- **Impact:** cosmetic, and self-limiting because the table follows. It is worth recording because §4.1 was created in this wave specifically to be the one place audit status lives, and because it is the first thing a reader of §4 sees. It also indicates the generator emitted this line without its substitution step being exercised.
- **Remediation constraint:** the line must be rendered from `audit_reports`, and the generator's output for it must be covered by whatever check confirms the other generated values — a generated line that can ship with its placeholders intact is not yet generated.

**Severity counts: CRITICAL 0 · MAJOR 0 · MEDIUM 0 · LOW 3.** All three are documentation-rendering defects confined to `precode/review.md`. **No contract, schema, fixture, task card, evidence record or check was broken by the fix diff.**

## 6. Deferred (out of scope, not findings)

- Six denied cases whose callee is an `EXT-*` system still name an internal port in `attempted_edge.operation`. This is now a written, gated convention (`default_deny.attempted_edge_operation_rule_vi` branch (b)) and my R1 rating of it was LOW; the convention is reproduced correctly in all six. No action sought.
- `E0-06`/`E0-07` still do not scan prose inside `evidence/handoffs/`; unchanged and disclosed.
- SC19+ carry no `ac_ref`, which is correct — they are supplementary scenarios.

## 7. Per-package verdicts

Unchanged from A2-R2; the fix diff changed none of them. PC00 **PASS** · PC01 **PASS** (six null-operation cases now compliant; rule and gate agree) · PC02 **PASS** · PC03 **PASS** · PC04 **PASS** · PC05 **PASS** (scope-blocked) · PC06 **PASS** · PC07 **PASS** (scope-blocked) · PC08 **PASS** (scope-blocked) · PC09 **PASS** (all three new findings are LOW and confined to `review.md` prose; the substantive fixes — E0-10b promotion, DoR row 5, in-repo provenance artefacts, §4.1 single-source block — all verify) · PC10 **PASS** (483/483 pins; `FCW4f` unanimous across 18 cards).

## 8. Overall verdict

**PASS**, scoped to what I checked, at completion ceiling `DRAFT_FOR_REVIEW`. Not `STALE`, not `BLOCKED`.

Three of the four A2-R2 findings are verified remediated, and each was closed at the level of mechanism: the denied-case rule is now enforced by a check I proved live by mutation; the DoR row is generated from `ports.yaml`; the provenance artefacts are inside the candidate, in the manifest and in the evidence index. The fourth is PARTIAL on a single table cell.

The one unresolved thread is narrow and consistent across three epochs: a hand-maintained epoch name in DoR row 11, now accompanied by a provenance claim it does not satisfy, and a published derivation command that does not do what the text says it does. Neither touches a contract, a schema, a fixture, a card or an oracle. `PASS` here means the scope I checked meets its oracle; it is not product acceptance and not `CONTRACT_READY`.

## 9. Residual open items — for the Coordinator to carry verbatim to the Owner

Re-stated from A2-R2, updated at item 14; items 1–13 and 15 are unchanged in substance.

1. **B01–B17 are all `OPEN`** in `agent_profile/registry.json`; every proposed resolution is `PROVISIONAL` and 84 of 246 registry rows change if the Owner rejects the corresponding amendment. Fourteen amendments await ratification; B06, B13 and B14 need a decision with no written amendment.
2. **`REQ-OQ01` — confirm D09 (project-specific Chrome profile).** Blocks M0, gate SP1 and `MOD-x-collector`.
3. **`REQ-OQ02` — choose the stack** (`ADR-0006` recommends Option A / Python, status `proposed`). Blocks M1, gate G5 and the build/test paths in all 18 cards; DoR item 11 cannot be met until it is answered.
4. **`REQ-OQ03` — specific provider and model for labelling and summary.** `OWNER_DECISION_REQUIRED`, no provisional default; blocks `MOD-settings-service` and M3.
5. **`PROV-PC00-01` / `PROV-PC01-03` — what `data.purge_all` must not delete.** `OWNER_DECISION_REQUIRED`, no default. Purging the login credential can lock the Owner out (D05 forbids signup and automatic password recovery), and purged data survives in backups until those are deleted. Blocks `MOD-data-admin-service`.
6. **`REQ-A6` / `REQ-D34` — arXiv and OpenAlex call rates and identification requirements.** `KC`; four values `null`/`PLACEHOLDER_KC` behind one conservative floor (`min_interval_ms = 3000`). Needs the official documentation; no network this session. Hard-blocks `MOD-research-connector`.
7. **`CR-PC07-04` — Telegram Bot API formatting limits** (max message length, callback-data length, parse mode and escape table, buttons per row, send rate). `KC`. Hard-blocks `MOD-telegram-adapter` and the multipart delivery branch.
8. **`REQ-A5` + B13 — each AI vendor's CLI/ACP terms, and provable tool/file/network isolation.** `KC`; no adapter has passed the isolation probe, all are `enabled=false`, and **AC-16 is `BLOCKED`, not `FAIL`**. Hard-blocks `MOD-ai-adapter` and `MOD-analysis-worker`.
9. **`CR-PC05-03` — official documentation URLs for arXiv/OpenAlex.** Neither source contains a URL; PC05 recorded document identifiers and invented none. Needs an Owner-supplied URL or acceptance that it is fixed at implementation time.
10. **`REQ-A1`, `REQ-A2`, `REQ-A3`, `REQ-A4`, `REQ-A7`, `REQ-D47`, `REQ-OQ08`, `REQ-OQ09` remain `KC`** — collector viability, embedding threshold, multilingual embedding quality, whether vector density finds real emerging directions, X's account restrictions, the specific embedding model. Each is gated; none may be declared met by drafting.
11. **No runtime evidence exists.** All 56 scenarios are `NOT_RUN`; E1–E4 have never run (`evidence/index.json`: `e1_e4_run: 0`, `independent_audit_records_in_repo: 0`). No code, no collector run, no AI call, no Telegram send, no restore drill.
12. **Gate status:** G0/G1/G2 `MET_PROVISIONAL`, G3/G4 `PARTIALLY_MET`, G5 `NOT_MET`, **SP1 `NOT_MET`** (the X feasibility probe has never been run), G6/G7 `NOT_APPLICABLE_YET`. Project status stays **`NOT_READY_FOR_PRODUCT_CODE`**.
13. **`contracts/http/openapi.yaml` (227 KB) has never been checked by an OpenAPI 3.1 validator** — none available, installing one out of scope. Internal consistency verified; specification conformance not.
14. **Three LOW findings from this audit are OPEN** (F-A2R3-01…03), all in `precode/review.md` and all documentation-rendering: DoR row 11 asserts the superseded epoch `FCW4e` while claiming derivation from a key whose registered value is `FCW4f`; the derivation command published as the authority returns seven epoch names instead of one; §4.1 carries an unrendered `%d`/`%s` format string. **F-A2R1-03 and F-A2R2-01 remain PARTIAL** on the first of these. No contract, schema, fixture, card or evidence defect is open.
15. **Column-gate coverage:** the `rows[]` field-existence check does not reach 41 of 86 fixtures, disclosed exactly per directory; `CR-PC02-18` is dispositioned `ACCEPTED_AS_LIMITATION`. `E0-06`/`E0-07` still do not scan prose inside `evidence/handoffs/`.

## 10. `CONTRACT_READY` upon Owner ratification — re-stated, unchanged

**Eligible on ratification of the named decisions** (no MAJOR or MEDIUM finding open against any of them):

1. **Boundaries and rights** (`modules.yaml`, `capabilities.yaml`, `ports.yaml`) — ratify `AMD-B12`, B13; answer `REQ-OQ01`.
2. **Data and identity** (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schemas) — ratify `AMD-B05`, `AMD-B15`, B06; close `CR-PC01-05`. The SQLite partial-index and generated-column assumptions are an E1 matter, not a `CONTRACT_READY` condition.
3. **Workflow and state** (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) — ratify `AMD-B02`, `AMD-B10`, `PROV-PC03-04`.
4. **Reporting and time** (`time-and-tags.md`, `selection.md`, `report.schema.json`) — ratify `AMD-B01`, `AMD-B04`, `AMD-B17`, B14; confirm or reject `PROV-PC04-09`; answer `REQ-OQ04`. An uncalibrated similarity threshold does not block the contract; it blocks any claim of meeting SRC-SPEC §1.4.

**Not eligible on ratification alone** — each blocked by a fact only the outside world supplies: **Collector and paper connector** (`REQ-A6`) · **AI and grounding** (`REQ-A5` + B13; AC-16 `BLOCKED`) · **App, Save and Telegram** (`CR-PC07-04`) · **Operations: secrets, boundary, backup** (`PROV-PC00-01`).

The three open F-A2R3 findings are LOW and sit in `precode/review.md`, which is not part of any of the eight scopes above; under protocol §8 they do not block those scopes, but they are open and the readiness report itself should not be described as final while they stand.

## 11. Limitations

1. **E0 only.** No code exists; nothing was executed against a database or an external service. A reproduced `PASS` proves internal consistency of the checked subset and nothing about runtime.
2. **Scoped re-review.** Per the packet I re-ran the fix-diff regression and my standing battery, not the full R1 audit. Areas untouched by the diff were spot-checked, not re-derived from scratch.
3. **Mutation testing** proves `E0-10b` fires on the one defect I injected, not on every variant of that class.
4. **Reference checks find dangling and stale references, not missing ones.** All three new findings are of that class.
5. **No OpenAPI 3.1 validator** (residual item 13).
6. **Writer quiescence was inferred, not enforced** — `DOCUMENTARY_DRAFT`, `operational_enforcement_status: NOT_IMPLEMENTED`. I rely on the declared lease releases plus start/end rehash showing zero drift.
7. **My own tooling is unaudited.** Where I disagree with the fixing side I have quoted the underlying bytes — here, the registered `numbers-20260907T021812Z.json` and the output of the published command — so the disagreement can be checked without trusting my scripts.

## 12. Completion ceiling statement

The maximum claim supportable by this audit is **`DRAFT_FOR_REVIEW`**, verified mechanically: no file asserts more (`E0-12`, reproduced, plus my own sweep). Not established: `CONTRACT_READY` for any scope; anything at or above `IMPLEMENTATION_VERIFIED`; any statement about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands; B01–B17 remain `OPEN`.

Three findings are **OPEN** (F-A2R3-01…03); two prior findings remain **PARTIAL** (F-A2R1-03, F-A2R2-01) on the same DoR cell; all others across four audit rounds are **VERIFIED**. Per protocol §8 I close nothing and accept no risk; disposition requires the designated authority, and the author of a fix may not verify it. I have not been assigned a further turn and will not continue tracking this candidate unless dispatched.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R3` / `PKT-A2-R3`. Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent; the mutation test ran entirely on a scratch copy. Manifest `228bf15d0906b92b410a2849c26daf50f5dfbc470cc10aaca3ebc951b9974ab8` verified identical at start and end of review.*
