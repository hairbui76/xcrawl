# AUDIT_REPORT — A2-R4 — scoped re-review of F-A2R3-01…03 on FC-W4 epoch 7

## 1. Frozen reference

| Item | Value |
| --- | --- |
| Candidate | `FC-W4`, freeze epoch **7** |
| Manifest | `…/scratchpad/audits/FC-W4e7-manifest.txt`, 202 entries |
| `manifest_sha256` declared | `7a9f7b8d430cea39a1e3a600c24d4409c8cea330f1c63b93cff7cd9d38bda631` |
| Recomputed **T0** and **T1** | identical both times — **MATCH**; 202/202 per-entry sha256 + byte counts, 0 missing, 0 drift, order sorted |
| Roles | CANDIDATE 174 · DEPENDENCY 8 · EVIDENCE 18 · SOURCE 2 |
| Fix diff vs epoch 6 | 4 files changed (`precode/review.md` 99604→101710, `evidence/handoffs/PC09-handoff.md`, `evidence/tools/README.md`, `evidence/index.json`); 3 added and 3 removed under `evidence/runs/` (the `…023000Z` triple replacing `…021812Z`). Tightly scoped, exactly as the addendum declares. |

**Not `STALE`** — byte-identical across the review interval. **Not `BLOCKED`.**

## 2. Independence

`auditor-A2`, `AUTH-COORD-A2-R4` / `PKT-A2-R4`, read-only, lease `null`. Authored nothing in the repository. No repository byte written, no `git` mutation, no network, no subagent, no scratch copy needed this round. Helpers under `…/scratchpad/a2/` with `PYTHONDONTWRITEBYTECODE=1`; the E0 tool run with `--json-out` into my scratch directory. Confirmed clean: T1 manifest identical, no `__pycache__`/`.pyc` under the repo.

Findings are **OPEN**; a `VERIFIED` verdict from me is a verification verdict, not a disposition (protocol §8).

## 3. Verification table

| Finding | Verdict | My own reproduction on epoch-7 bytes |
| --- | --- | --- |
| **F-A2R3-01** DoR row 11 asserts a superseded epoch under a false provenance claim | **VERIFIED** | W6 removed the duplicated value rather than reprinting it — the stronger of the two remedies my constraint allowed. Row 11 now reads "18 card đều pin cùng một epoch — **tên epoch được in ở §9.1 và chỉ ở đó**", and records why (`F-A2R3-01`: the row "đã sai ba epoch liên tiếp"). I grepped the whole DoR table for `PC10-PIN`: **no match**. Across all of `review.md` the epoch now appears in exactly one asserting place, §9.1 line 855 (`FCW4f`), plus one correctly-framed history mention. The divergence is now structurally impossible rather than currently absent. |
| **F-A2R3-02** the published derivation command does not return what the text says | **VERIFIED** | The command is now `sed -n 's/^\*\*Pin epoch: `\([A-Za-z0-9-]*\)`.*/\1/p' agent-tasks/TC-*.md \| sort -u`. **I ran it verbatim:** it returns exactly one value, `PC10-PIN-FCW4f-20260907`, emitted by 18 of 18 cards. That value equals §9.1's printed value and equals `card_pin_current` in the registered artefact. The command string is itself now stored as `card_pin_command` in `numbers-20260907T023000Z.json`, byte-identical to what is printed, so the published rule and the generator's rule are the same object rather than two descriptions of one. §9.1 also explains why the old `grep -ho` form returned seven names. |
| **F-A2R3-03** unrendered `%d`/`%s` in §4.1 | **VERIFIED** | Line 363 now reads "**6 AUDIT_REPORT độc lập đã chạy** (`audit_reports`, `audit_reports_count` — đếm từ đĩa):" followed by the six named reports. `audit_reports` in the registered artefact is a six-element list (A1-R1/R2/R3, A2-R1/R2/R3) and a new `audit_reports_count` key backs the numeral. The table below carries six rows. I swept `precode/`, `agent-tasks/`, `contracts/`, `acceptance/`, `evidence/handoffs/` and `evidence/tools/README.md` for surviving `%d`/`%s` placeholders: **none**. |
| **F-A2R1-03 / F-A2R2-01(a)** the PARTIAL residual on DoR row 11 | **VERIFIED — residual closed** | This is the same cell as F-A2R3-01 and it is now free of a transcribed epoch. The thread that ran PARTIAL across epochs 5, 6 and 7 is closed at its root: the value has one emitter, and that emitter is the generator. |

**4 of 4 VERIFIED. 0 PARTIAL, 0 NOT_VERIFIED.**

## 4. Regression check on the fix diff

| Check | Result |
| --- | --- |
| Independent E0 re-run from scratch dir, nothing written into the repo | **22/22 PASS, 0 violations, exit 0** |
| Check-for-check diff vs registered `evidence/runs/E0-20260907T023000Z.json` | **0 differing checks**; `files_scanned` 168 = 168; `baseline_hashes` identical; summaries identical |
| `evidence/index.json` | 58 records, **58/58 validate** against `manifest.schema.json`; all three new `…023000Z` artefacts referenced; **no surviving reference to the superseded `…021812Z` triple** |
| `review.md` headline numbers vs artefacts and vs the registered `numbers` file | DoR table parses **9 ✅ / 1 ⚠️ / 2 ❌** = its own summary = `numbers.dor {met 9, partial 1, not_met 2}`; module table **9 / 16 / 5** = `module_ready` / `module_blocked` / `module_hard_blocked`; requirements 246, operations 85, entities 60, transitions 67, error codes 28, fixtures 86, scenarios 56 — all reproduce |
| Card pins | Cards were not touched by this diff; the 18 cards still declare `FCW4f` unanimously and my last full recompute (483/483) stands on unchanged bytes |
| `evidence/tools/README.md` | Grew by 2582 bytes documenting the pin rule and the rendering fix; no placeholder, no claim above `DRAFT_FOR_REVIEW` |

No regression introduced by the fix diff.

## 5. New finding

### F-A2R4-01 — **LOW** — the audit-status table's Verdict column carries a scope description instead of a verdict for the newest row

- **Ref:** `precode/review.md` §4.1, row `A2-R3` of the audit-rounds table.
- **Observed:** the table's third column is headed *Verdict*. The `A1-R1`/`A1-R2`/`A1-R3` rows carry `FAIL`, `A2-R1` carries "**FAIL cho PC09**", `A2-R2` carries "**PASS tổng thể**". The `A2-R3` row carries "**xác minh bản sửa FIX9**" — a description of the round's scope, not its verdict. My A2-R3 overall verdict was **PASS** (scoped, ceiling `DRAFT_FOR_REVIEW`), stated in §8 of that report.
- **Impact:** low. §4.1 is the declared single source of truth for audit status in this document, and every other section now points at it rather than restating; a reader scanning the Verdict column finds five verdicts and one non-verdict. The adjacent cell is accurate — it records "3 VERIFIED · 2 PARTIAL · 0 NOT_VERIFIED; 3 finding LOW mới … đã sửa ở đợt FIX10", which is a remediation statement a Worker is entitled to make and which my verification this round confirms; it does not assert `VERIFIED` or `CLOSED` on my behalf, so it does not breach protocol §8.
- **Remediation constraint:** the Verdict column must carry the verdict word from the corresponding AUDIT_REPORT's verdict section for every row, or the column must be renamed to what it actually holds. Since §4.1 is now the single source for this status, the value should be taken from the report rather than summarised — the same discipline this wave applied to the epoch name and to the rendered count.

**Severity counts: CRITICAL 0 · MAJOR 0 · MEDIUM 0 · LOW 1.**

## 6. Overall verdict

**PASS**, scoped to the four findings and the fix diff, at completion ceiling `DRAFT_FOR_REVIEW`. Not `STALE`, not `BLOCKED`.

All three F-A2R3 findings and the long-running PARTIAL on DoR row 11 are verified remediated, and each was closed at the level of mechanism rather than of wording: the epoch value now has exactly one emitter, the published command *is* the generator's rule and I ran it to one value, and the rendered count is backed by a keyed artefact. One new LOW finding remains, confined to a single table cell in `precode/review.md`.

Per-package verdicts are unchanged from A2-R2/R3: all eleven **PASS**. No contract, schema, fixture, task card, evidence record or check was touched or broken by this diff.

## 7. Residual open items

Unchanged from A2-R3 §9 items 1–13 and 15 — B01–B17 `OPEN`; `REQ-OQ01`, `REQ-OQ02`, `REQ-OQ03` and the `data.purge_all` exclusions awaiting the Owner; `REQ-A6`, `CR-PC07-04`, `REQ-A5`+B13 and `CR-PC05-03` blocked on the outside world; eight further `KC` rows; no runtime evidence (56 scenarios `NOT_RUN`, `e1_e4_run: 0`); gates G0–G2 `MET_PROVISIONAL`, G3/G4 `PARTIALLY_MET`, G5 and SP1 `NOT_MET`; `NOT_READY_FOR_PRODUCT_CODE`; no OpenAPI 3.1 validator; column gate reaching 45 of 86 fixtures with `CR-PC02-18` `ACCEPTED_AS_LIMITATION`.

**Item 14 is replaced by:** one LOW finding open (`F-A2R4-01`, a Verdict-column cell in `review.md` §4.1). F-A2R3-01…03, F-A2R2-01 and F-A2R1-03 are all now **VERIFIED**; no PARTIAL remains from any round.

`CONTRACT_READY`-upon-ratification scopes are unchanged: **Boundaries and rights**, **Data and identity**, **Workflow and state**, **Reporting and time** are eligible on ratification of their named decisions; **Collector and paper connector**, **AI and grounding**, **App/Save/Telegram** and **Operations** are not eligible on ratification alone.

## 8. Limitations

E0 only — no code exists and nothing was executed against a database or an external service. This was a scoped re-review of four findings plus the fix diff, not a re-derivation of the full baseline. My verification that the published pin command returns one value is a verification of that command against the current 18 cards, not a proof that it stays correct if the card pin line's shape changes. Reference checks find dangling and stale references, not missing ones. Writer quiescence was inferred from the declared lease releases plus start/end rehash showing zero drift, not enforced — the session runs `DOCUMENTARY_DRAFT` with `operational_enforcement_status: NOT_IMPLEMENTED`. My own tooling is unaudited; where I assert a value I have quoted the bytes it came from.

## 9. Completion ceiling

Maximum claim supportable: **`DRAFT_FOR_REVIEW`**. Not established: `CONTRACT_READY` for any scope; anything at or above `IMPLEMENTATION_VERIFIED`; any claim about X, Telegram, an AI provider, a CLI/ACP adapter, or real SQLite behaviour. `NOT_READY_FOR_PRODUCT_CODE` stands and B01–B17 remain `OPEN`.

`F-A2R4-01` is **OPEN**. I close nothing and accept no risk; disposition requires the designated authority, and the author of a fix may not verify it.

---
*Produced by `auditor-A2` under `AUTH-COORD-A2-R4` / `PKT-A2-R4`. Review type: `INDEPENDENT_AUDIT`. Read-only: no repository byte written, no git state mutated, no network, no subagent. Manifest `7a9f7b8d430cea39a1e3a600c24d4409c8cea330f1c63b93cff7cd9d38bda631` verified identical at start and end of review.*
