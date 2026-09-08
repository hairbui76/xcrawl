# HANDOFF — `TC-ui-reports-detail`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-UIREPORTS`, then `PKT-TC-UIREPORTS-FIX1` (fixture accounting) — card `agent-tasks/TC-ui-reports-detail.md` (Phase 4, M4, gate G5) |
| worker principal | `worker-W4D` |
| authority_id | `AUTH-COORD-TC-UIREPORTS` (parent `AUTH-OWNER-20260908-10`; record `…/scratchpad/packets/PHASE4-6-card-dispatch.md`) |
| lease_id | `LEASE-TC-UIREPORTS-e1` (card §3 write set + handoff + evidence manifest), then `LEASE-TC-UIREPORTS-e2` (the two test files + handoff + manifest re-issue) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `CONTRACT_READY` for the three reading read models, the provenance/evidence-level vocabulary, and the seven §4 operation wrappers. Card §9 sets `IMPLEMENTATION_VERIFIED` as the ceiling for the read model and the provenance labels, but this record is `SELF_VALIDATION` and protocol §9 caps a self-check at `CONTRACT_READY`. |
| review_type | `SELF_VALIDATION`. No independent audit was run and none is claimed. |
| next actor | Coordinator |
| lease_released_at | `e1` 2026-09-07T21:15Z; `e2` 2026-09-07T22:05Z (host clock; the repo's documents run on a 2026-09-08 calendar — same offset every card in this wave reports) |

`DONE_WITH_CONCERNS` rather than `DONE` for reasons that are contract facts, not defects in
the code, and none of them silent:

1. **Two of the three screens cannot be fed from their own operation's response.**
   `report.get` returns only an `analysis_ref` (a pointer plus a hash), and
   `work.get_detail` returns only the `work | post` union. Neither can carry what
   `contracts/ui/screens.yaml` says those screens display. The read models take the missing
   half as a separate, contract-shaped input and report anything absent as missing;
   `CR-TC-UIREPORTS-01` and `-03` carry the gap. Nothing wire-shaped was invented.
2. **E4 is `NOT_RUN`** and is the level `acceptance/scenarios.yaml` requires for SC10, SC11 and
   SC15. This run establishes their E1 half.
3. **One edit lands inside a sibling's file beyond a pure append** — one type alias widened in
   `web/src/lib/api.ts` so a `DELETE` operation the card must call becomes reachable. It is
   described exactly in §3 below.

---

## 0. Wait gate and baseline

The packet's wait gate was honoured; not one byte was written before all four conditions held.

* **(1) Commit.** `git log -1 --format='%h %s'` on `main` → `fb3944a feat: Phase 3 (M3) +
  Phase 5 (M6, plain text) — AI adapter/analysis/embedding, Telegram linking/saved/delivery;
  REQ-OQ03, REQ-A5, Telegram facts`. Subject begins `feat: Phase 3`.
* **(2) Epoch.** `agent-tasks/README.md` line 124 declares `PC10-PIN-P3b-20260908`, which is
  the epoch this card's §0 names.
* **(3) SG-HASH.** Run **three times**: once while the gate was still closed, once
  immediately after `fb3944a` landed, and once immediately before the first write. All **29**
  sources pinned in card §0 (2 spec/plan + 27 contracts, ADRs and fixtures) were re-hashed with
  `sha256sum` and `diff`ed against the card's table. **0 mismatches on all three runs.**
* **(4) Sibling.** `evidence/handoffs/TC-ui-runs-three-states-handoff.md` present, `status`
  `DONE_WITH_CONCERNS`, `lease_released_at 2026-09-07T21:05Z`, `next actor` naming `W4D` and
  `web/src/lib/api.ts` as the file with content to extend. `LEASE-TC-UIRUNS-e1` released.

**SG-PC09.** `acceptance/scenarios.yaml` was read at its current (deliberately unpinned) bytes.
SC09, SC10, SC11, SC15 and SC49 agree with the card's §8 line for line: SC10's `oracle_vi`
names the same five fields and the same `analysis_id` equality; SC11's names
`comparator='unknown'` and "every novelty statement is `ai_inference`"; SC15's names the
forbidden-phrase sweep; SC09's names the dated prior reference. **No conflict, so no stop.**
One naming divergence is recorded as `CR-TC-UIREPORTS-06`, not acted on.

**SG-STACK, SG-01, SG-02, SG-EDGE, SG-CONTRACT.** No framework or library was chosen — the
toolchain is the one `web/package.json` already ships under ADR-0011 (Vite, React 18, Vitest,
eslint, prettier, `openapi-typescript`). No Settings screen and no `direction_phrasing` path is
touched by this card, so `SG-01` and `SG-02` do not fire here. No new edge, table, secret or
capability was needed. Contract defects found were written down as change requests, never
edited.

No file under `contracts/`, `acceptance/`, `precode/` or `agent-tasks/` was modified —
`git status --porcelain -- contracts acceptance precode agent-tasks` is empty.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `web/src/lib/provenance.ts` | CREATE | ABSENT | `d9561e297fdb7f4e4a368312afe685c0c19b1f2d5422363b5314d2f0743f496f` | 10558 |
| `web/src/routes/reports.ts` | CREATE | ABSENT | `d186b993bc9e7b17daff21599883dbbfc0f3a18d3b65526add4b9ac0cbe18353` | 12733 |
| `web/src/routes/reportDetail.ts` | CREATE | ABSENT | `e847eef67f56ac2c6b9ed5a25bb33851961d64a884cffbfa97ebdaf9413db592` | 15528 |
| `web/src/routes/workDetail.ts` | CREATE | ABSENT | `f637b382313cdb97e3109d9dbd86b206caa4b18a726fa6a554bd4184c926e992` | 12326 |
| `web/src/views/ReportDetail.tsx` | CREATE | ABSENT | `764e559a187006c459b18d3d42429fd770ad5fea5b54f5ec722d2e91407248fe` | 7420 |
| `web/tests/contract/reportReadModel.test.ts` | CREATE | ABSENT | `f193f04fe2059118fc04d4ae795455dc76d03266bcc00e1c4b54ada8dceac639` | 19486 |
| `web/tests/integration/provenanceLabels.test.ts` | CREATE | ABSENT | `4cf7006f80f024db1fdca01b25a641b594bb9a9fcc65f9fd814f48ec3631a512` | 20359 |
| `web/src/lib/api.ts` | MODIFY | `5c3e9630d30093fe939f56422aebf613edf7e64ef946121fbaf383d881442e79` (16889 B) | `c82fb41aa1aa127cae5509aa26e3110e257f30809e9a9a2684a7e717b89aa061` | 24430 |
| `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` | CREATE, then MODIFY (marked `STALE`) | ABSENT | `bb65c4877a200b70be0ed1ad273c171d437fdcee4355233985076e97cc5fc82a` | 19804 |
| `evidence/runs/TC-ui-reports-detail-E1-20260907T220500Z.json` | CREATE (`PKT-TC-UIREPORTS-FIX1` re-issue) | ABSENT | `ed6be440247b7dc705d4a7dee5be3545bf553dedc734e24b6355b4f3bfa92e73` | 22202 |
| `evidence/handoffs/TC-ui-reports-detail-handoff.md` | CREATE | ABSENT | (this file) | — |

**No Alembic migration.** This card owns no table: `web/` is a consumer of the owner HTTP API
and touches no database (`contracts/ui/screens.yaml` §global_rules.no_direct_access, I01).
`server/app/main.py` is likewise untouched — there is no router to register.

### `web/src/lib/api.ts` — what the modify actually is

The before-hash is W4C's released file, exactly as their handoff states it. Three changes:

1. **Append** a delimited block `// >>> TC-ui-reports-detail >>>` … `// <<< … <<<` at the end
   of the file: `DeletePath` / `DeleteOptions` / `DeleteResponse` / `CreatedResponse`, the
   `REPORTS_OPERATION_PATHS` table, and one wrapper per operation of card §4.
2. **Append** a second delimited block *inside* `class ApiClient`, immediately after
   `mutate()`: the `remove()` method. It repeats `mutate`'s obligations exactly — session
   cookie AND `X-CSRF-Token` AND `Idempotency-Key` — because `save.remove` is
   `x-mutation: true` and carries the same required header set in the contract.
3. **One widening edit, the only non-append change:** `export type HttpMethod = 'get' |
   'post'` became `'get' | 'post' | 'delete'`, and the private `send`'s method parameter
   gained `'DELETE'`. Reason: `save.remove` is `DELETE /v1/saved/{target_ref}` in
   `contracts/http/openapi.yaml`, so without it a client cannot reach an operation card §4
   allows. The widening is additive — `GetPath`, `PostPath`, `RequiredHeaders`,
   `OPERATION_PATHS` and every W4C assertion keep their previous meaning, which the sibling's
   own 48-test file confirms (all pass, unchanged).

**`REPORTS_OPERATION_PATHS` is a second table, not an extension of `OPERATION_PATHS`.**
W4C's contract test asserts `Object.keys(OPERATION_PATHS)` equals *exactly* their nine
operations, so appending to it would fail a sibling's oracle on bytes I do not own. Two tables,
one per card, keep both assertions honest. Whether they should later be merged behind a single
"operations this app may call" registry is a Coordinator decision — recorded as
`CR-TC-UIREPORTS-08`, not taken here.

---

## 2. What the code does

Three pure read models, one vocabulary module, one view. **Nothing under `web/src/routes/` or
`web/src/views/` performs I/O**: the HTTP calls live in `web/src/lib/api.ts` and the read models
are functions from a contract-shaped payload to display strings. That is what makes every
oracle in §3 a string comparison or a count rather than a screenshot.

* **`web/src/lib/provenance.ts`** — the three statement kinds, the three evidence levels, the
  comparator projection, the AC-10 completeness check. Every type is taken from the generated
  client (`statement_kind`, `statement`, `comparator`, `evidence_level`, `result_summary`,
  `summary_block`); the module adds display vocabulary and pure projections only.
  `describeComparator` turns absence — `undefined`, `null`, the object form's
  `{kind:'unknown'}` and a Saved snapshot's `'unknown'` enum — into one explicit
  "comparator: unknown", and has no branch that can produce a baseline (B16, grounding.md
  §4.2). `groupStatementsByKind` returns all three buckets **including empty ones**, so "there
  is no verified statement" and "verified statements are not shown" cannot look the same
  (I13).
* **`web/src/routes/reports.ts`** — `SCR-reports`, plus the wire-type aliases the three screens
  share, so the two detail modules do not each re-derive them.
* **`web/src/routes/reportDetail.ts`** — `SCR-report-detail`, including `ac10ChannelPayload`:
  the single projection of the five REQ-AC10 parts that both channels are compared on.
* **`web/src/routes/workDetail.ts`** — `SCR-work-detail` and the four `grounding_rules` of
  screens.yaml, including the `post_only` ⇒ "novelty is inference, not conclusion" notice.
* **`web/src/views/ReportDetail.tsx`** — the labels, per §3's own description of the file's
  role. Source content (paper titles, post text, AI output) is rendered as React children,
  i.e. escaped, and never as HTML; there is no `dangerouslySetInnerHTML` anywhere, which the
  contract test asserts by scanning the bytes (SRC-SPEC §11.4, I11).

**Reuse instead of a second copy.** The delivery-state vocabulary, the storage-health notice
and the five display states are **imported from W4C's `web/src/lib/runState.ts`**, not
redefined. A second copy of the delivery labels would be a second place for `unknown` to drift
into `sent` (I13, AMD-B03). The same applies to the globally forbidden phrase: this card's
tests sweep against W4C's `FORBIDDEN_RUN_LABEL_VI` rather than a second literal. The one thing
added on this side is the case `runState.ts` does not model — storage health **not read at
all**, which is neither `healthy` nor any unhealthy value and must disable mutations rather
than default to "fine".

---

## 3. Verification

Commands are the card's §8 list verbatim, run from the repo root, plus the whole-suite run that
proves the sibling's tests still pass on these bytes.

| Command | Exit | Result |
| --- | --- | --- |
| `npm --prefix web run typecheck` | 0 | `tsc --noEmit` clean over `src`, `tests`, `scripts` |
| `npm --prefix web run test -- reportReadModel` | 0 | **20 passed**, 0 failed |
| `npm --prefix web run test -- provenanceLabels` | 0 | **24 passed**, 0 failed |
| `npm --prefix web run lint` | 0 | `eslint .` clean **and** `prettier --check .` clean |
| `npm --prefix web test` (whole suite) | 0 | 6 files, **126 passed**, 0 failed, 0 skipped |
| `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py` | — | After W6n's fix: **26 checks, PASS 26, FAIL 0, violations 0**. `E0-20` clean for this card via the test-reference branch |

This card contributes **44** tests (38 at first handoff, +6 under `PKT-TC-UIREPORTS-FIX1`).
The other 82 are the sibling's and the skeleton's,
including `generatedClient.test.ts`'s "regenerating produces no diff", which still passes — the
generated client was not hand-edited.

**One failure was observed and is reported rather than hidden.** The first whole-suite run
failed *one* test — the sibling's forbidden-edge sweep (`runReadModel.test.ts` §10), which
greps every file under `src/lib`, `src/routes` and `src/views` for the database engine's name.
A header comment in `web/src/routes/reports.ts` quoted the card's own §5 wording and contained
that word in prose. To a grep, prose and code are the same. The comment was reworded and the
reason recorded in the file so the next author does not reintroduce it. **No test of either
card was modified**, and no oracle was weakened.

Environment: node 22.23.2, npm 10.9.8, TypeScript 5.9.3, Vitest 3.2.7, eslint 9.39.5, prettier
3.9.6, React 18.3.1, jsdom 26.1.0, `openapi-typescript` 7.13.0. **Zero network calls, no
server, no secret, no browser.**

---

## 4. Oracles, and how each was measured

| # | Obligation | Measurement | Observed |
| --- | --- | --- | --- |
| AC-10 | App and Telegram show the same analysis revision | Build the read model from the revision `report_item` froze (fixture `ui/sc10` `given.rows`), compare **field by field** with `expected.channel_payloads.telegram_digest`, iterating the fixture's own `fields_present` list | `analysis_id` and `generation_number` equal; all five fields equal; distinct ids across channels = 1 = `expected.counts.distinct_analysis_id_across_channels` |
| I05 | No channel reaches a post-publish revision | `JSON.stringify(read model)` scanned for AN2's id | 0 occurrences |
| REQ-AC09 / I07 | Already-announced work is a **dated reference** | Fixture `reporting/h` `expected.report` loaded whole; label compared against the fixture's `display_oracles` string | `Đã báo cáo 12/03`; `new_discovery` count 0 = fixture count |
| I07 after merge | Inherited announcement date, still one reference | Fixture `reporting/i` (`merge_audit_id` non-null) | `Đã báo cáo 01/09`, `new_discovery` count 0 |
| REQ-AC11 / B16 | Three kinds never collapsed | `Set` of the three display labels; then each fixture statement located under its own bucket and asserted **absent** from the other two (3×2 cross-check) | 3 distinct labels; 0 leaks |
| I13 | "None" ≠ "hidden" | The empty `source_verified` bucket is rendered with "Không có phát biểu loại này." | present |
| B16 | Missing comparator is stated, never invented | `data-comparator-kind`, plus `describeComparator(undefined)` and `(null)` | all `unknown`, text contains `comparator: unknown` |
| SV-03 | A payload over its evidence ceiling is flagged, not relabelled | Fixture `ai/d` `semantic_variant` (`source_verified` under `post_only`) | 1 violation surfaced; the statement stays under `source_verified`; `ai_inference` bucket unchanged |
| REQ-D21 | Evidence-level labels exact | Label keys compared to the enum of `report.schema.json` | keys equal, 3 distinct strings |
| grounding.md §4.5 / CR-PC06-05 | Analysis date **and** discovery date | Both labels present and different | pass |
| REQ-AC10 | An incomplete item is not shown as complete | Item with no summary | `completeness.complete = false`, "Mục còn thiếu: …" rendered, fields read "chưa có" |
| SRC-SPEC §8.3 | Forbidden phrase | Swept rendered output and the Reports read-model JSON | 0 occurrences |
| REQ-D54 / B14 | Emerging-direction block | Contract constant label; `insufficient_evidence` wording | `ứng viên để đọc sâu`; "Chưa đủ bằng chứng", not "đang nổi" |
| UC-03 / UI-03 | No "edit report"; nothing fails silently | Button inventory of the rendered view | one button (Save); no "Sửa báo cáo"; disabled **with a stated reason** when unwired |
| SG-DENY / SC49 FE-01…FE-04 | The reading screens reach nothing but the owner API | Byte scan of this card's five source files | 0 `fetch(`, 0 absolute URLs, 0 `dangerouslySetInnerHTML`, every import relative |

---

## 5. What is NOT established

* **E4 is `NOT_RUN`.** Card §8 requires a human for the groundedness review
  (`contracts/ai/grounding.md` §6) and for the desktop/mobile/Telegram render review.
  `acceptance/scenarios.yaml` sets `evidence_level_required: E4` for SC10, SC11 **and** SC15.
  Only their E1 half is established here. Card §9's "Chất lượng nội dung là E4" stands.
* **The reviewer question of §12 is not answered by any test.** "Can a reader tell an AI
  inference from a checked fact" is a human judgement. What is established is the mechanical
  precondition: the three kinds are separate, labelled and never merged.
* **No server ran.** None of the seven operations was called over HTTP. The wrappers were
  compiled, not executed: nothing here establishes real CSRF behaviour, real idempotency, or
  any server error code.
* **No Telegram payload was built.** AC-10 is proved by projecting the app side and comparing
  it to the digest payload the fixture pins — not by running `MOD-delivery-service`.
* **jsdom, not a browser.** Layout, readability and phone behaviour are untested.
* **Not an independent audit.** `review_type` is `SELF_VALIDATION`.

---

## 6. Change requests

| ID | Where | What | Proposed disposition |
| --- | --- | --- | --- |
| `CR-TC-UIREPORTS-01` | `contracts/http/openapi.yaml`, `work.get_detail` | The 200 body is `../schemas/target.schema.json`, i.e. the `work \| post` union alone. It cannot carry the eleven fields `screens.yaml` SCR-work-detail's read model names (summary, evidence_level, topic_labels, matched_tags, source_posts, paper_refs, work_versions, analysis_history, related_reported_items, identity_state, content_state). The read model composes its input from contract component types and names its fields exactly as screens.yaml does; no wire body was hand-written. | PC05 to give the operation a response schema, or PC07 to say where the fields come from. |
| `CR-TC-UIREPORTS-02` | same, `report.list` | Declares `limit` and `cursor` query parameters but a 200 body of a **single** `report.schema`. A page cannot be expressed. | PC05: a list envelope, or drop the paging parameters. |
| `CR-TC-UIREPORTS-03` | `contracts/schemas/report.schema.json` | Carries only `analysis_ref` — a pointer with a hash — so the five REQ-AC10 parts cannot be read off a `report.get` response, although `screens.yaml` §ac10_completeness and `delivery.md` §3.1 both require the item to show them. The read model takes summaries as a separate contract-shaped input and reports absences as missing. | PC04/PC06 to decide whether `report.get` embeds the summary payload or the UI makes a second call. |
| `CR-TC-UIREPORTS-04` | `web/src/generated/openapi.d.ts` | `openapi-typescript` lifts a referenced schema's JSON-Schema `$defs` block into a **required** property of the wire type (`report.schema`, `target.schema`), which no response body carries. Worked around by `Omit`. | Generator configuration or a post-processing step in `web/scripts/generate.mjs`. |
| `CR-TC-UIREPORTS-05` | same | The generated constant for `analysis_ref.analysis_result_schema_id` is the bare filename `"analysis-result.schema.json"`, while `report.schema.json` declares the full `$id` URL and **every fixture carries the URL**. A strict consumer of the generated type would reject a valid payload. Field widened to `string`, with the contract followed rather than the generator. | Same owner as `-04`. |
| `CR-TC-UIREPORTS-06` | `acceptance/scenarios.yaml` SC09 | `oracle_vi` names `report_item.reference_date`, a field `report.schema.json` does not define; the schema calls it `first_announced.first_announced_at`. Not a conflict with card §8, so no stop — but the two documents name the same thing differently. | PC09 to align the wording. |
| `CR-TC-UIREPORTS-07` | card §13 vs dispatch write set | §13 asks that the run be registered in `evidence/index.json`; that file is **not** in the granted write set, so it was not touched. Identical to `CR-TC-ANALYSIS-08`. | Coordinator action or a separate packet. |
| `CR-TC-UIREPORTS-08` | `web/src/lib/api.ts` | Each UI card asserts its own operation table is *exhaustive*, so the two cards keep two tables (`OPERATION_PATHS`, `REPORTS_OPERATION_PATHS`). Correct today; a third UI card will make it three. | Coordinator: decide whether a merged registry with per-card views is worth a follow-up packet. |
| `CR-TC-UIREPORTS-10` **(RESOLVED)** | `evidence/tools/e0_check.py` §E0-20 | The check walked `<repo>/tests` only, so no test under `web/tests/` could satisfy it and both TypeScript cards failed E0-20 structurally. The tool is PC09's and not in this card's write set, so it was not touched here. | **Closed by `W6n`**, which extended the walk to `web/tests/`. Re-run after the fix: 26 checks, PASS 26, violations 0. No disposition needed. |
| `CR-TC-UIREPORTS-09` | card §13 vs `evidence/manifest.schema.json` | §13 names the manifest `EVM-TC-ui-reports-detail`, but the schema's `evidence_id` pattern does not admit that shape, and its `unresolved_issue_refs` pattern does not admit `CR-TC-ui-reports-detail-nn` either. The schema won, being the runnable gate: ids are `EV-E1-01-tc-ui-reports-detail` and `CR-TC-UIREPORTS-nn`. Same resolution as `CR-TC-ANALYSIS-07`. | Coordinator to reconcile the card text with the schema. |

---

## 7. Fixture accounting — `PKT-TC-UIREPORTS-FIX1`

Raised by the standing check `E0-20-card-fixture-accounting`, which flagged one §2 fixture of
this card as "referenced by no test and named nowhere in the card's handoff". Two separate
facts sat behind that one line, and both are recorded here rather than papered over.

**Fact 1 — the check could not see this card's tests. Now fixed, by its owner.** At the time
the packet was dispatched, `evidence/tools/e0_check.py` built its `tests_text` by walking
`<repo>/tests`, the Python tree only. Every test this card owns lives under `web/tests/`, which
the walk never visited, so no amount of naming inside a Vitest file could satisfy E0-20 for a
TypeScript card — both UI cards failed it structurally. Raised as `CR-TC-UIREPORTS-10` (W4C
raised the same thing as `CR-TC-uiruns-08`); the tool belongs to PC09 and is not in this card's
write set, so **it was not touched here**. `W6n` has since extended the walk to `web/tests/`,
and the check now reads: "referenced by a file under any TEST tree — `tests/`, `web/tests/`".
**`CR-TC-UIREPORTS-10` is therefore RESOLVED**, and this card passes E0-20 through the
test-reference branch — the honest one — rather than through the handoff-plus-`NOT_RUN`
branch.

**Fact 2 — the fixture really was under-named, and that part is fixed.** The tests read the
JSON straight from `acceptance/fixtures/**` (no copy has ever existed under `web/`), but they
assembled each path from a directory fragment and a base name, so a grep for
`acceptance/fixtures/...` found nothing. Both test files now declare a `FIXTURES` map of full
repository paths and read through it. That is the greppable accounting E0-20 exists to force,
and it is worth having whether or not the tool can see the file.

**No fixture below is recorded as unexercised.** Every one of the seven is loaded by name, by
its full repository path, from a `web/tests/` file listed in the table — the path strings are in
the source, and with W6n's fix in place the check now sees them directly. The `NOT_RUN` entries in
the right-hand column are about **evidence levels and other cards' scopes**, never about whether
this card read the fixture: E4 has not run, and the row oracles that belong to the report,
identity, adapter and ingest cards were not re-proved here. Reading either column as "the fixture
was skipped" would be a misreading, and the wording is deliberate on the Coordinator's
instruction not to record a `NOT_RUN` for a fixture a Vitest test actually loads.

Full accounting of the seven JSON fixtures in the card's §2 read set (the three READMEs are
excluded by the check and by this table):
| §2 fixture | Loaded and asserted by (E1) | Evidence still `NOT_RUN`, and whose it is |
| --- | --- | --- |
| `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json` | `web/tests/contract/reportReadModel.test.ts` — six assertions: `analysis_id` and `generation_number` equal across channels, the five fields compared one by one through the fixture's own `fields_present` list, distinct-id count equal to the fixture's `counts`, and AN2 unreachable | The E4 half. `acceptance/scenarios.yaml` sets `evidence_level_required: E4` for SC10: whether a reader can decide **without opening the source** is a human judgement on a real render, and it is `NOT_RUN`. |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | same file — the dated `prior_reference` label against the fixture's `display_oracles`, the `new_discovery` count against its `counts`, and the two date labels | The ledger-side row oracles belong to `TC-report-coverage-publish-cas`, not to a UI card; `NOT_RUN` here. |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | same file — the inherited first-announcement date after a merge, still rendered as one dated reference | The merge bookkeeping (`moved_counts`, `superseded_by_merge_id`) is the identity card's; `NOT_RUN` here. |
| `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` | `web/tests/integration/provenanceLabels.test.ts` — the three-bucket split with a 3×2 leak check, the empty `source_verified` bucket, `comparator: unknown`, and the `post_only` label | Whether the labels actually stop a reader conflating inference with fact is E4 (§12's question); `NOT_RUN`. |
| `acceptance/fixtures/ai/d-schema-valid-but-uncited.json` | same file — the `semantic_variant`: one ceiling violation surfaced, the statement left under its declared kind | The schema-layer and SV-03 rejections themselves are the adapter card's; `NOT_RUN` here. |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | same file, added under this packet — the receipt's `SOURCE_METADATA_UNAVAILABLE` warning, with the quoted phrase pulled **out of the fixture's own `message_safe`** and asserted to appear in the work-detail notice; plus `state = partial` and no evidence-level upgrade | The ingest behaviour the fixture mainly pins (batch still commits, warning in a 2xx body) is `TC-ingest-idempotent-ack-lost`'s; `NOT_RUN` here. |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `web/tests/contract/reportReadModel.test.ts`, rewritten under this packet — the SG-DENY block no longer hardcodes FE-01…FE-04: it **selects `actor === 'MOD-web-ui'` from the sweep's events** and checks this card's five source files against a token set keyed by the callee the fixture names, so a fifth web-UI edge would be picked up without anyone editing a list | The server half of all 36 edges, and the network-egress half of FE-03/FE-04, cannot be observed from a jsdom test: `NOT_RUN`. |

Net effect on the suite: `reportReadModel` 18 → **20** tests, `provenanceLabels` 20 → **24**,
whole web suite 112 → **126**, all passing. No source file under `web/src/` was changed by this
packet, so §1's hashes for those five files still stand; only the two test files moved.

### 7.1 `STALE_BASELINE` on two §0 pins — observed, reported, not worked around

Re-running SG-HASH during this packet shows **two of the 29 pinned sources have moved** since
the epoch this card names, both of them `precode/` files re-written by the `OD-10` record:

| Pinned source | §0 hash | On disk now |
| --- | --- | --- |
| `precode/baseline.json` | `52af62c8b11e6939a9a34798bd71b4a4e688d8ed85d9c579ee1858ed341037e9` | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` |
| `precode/decision-register.md` | `b26cf51a0d7c73661ab465e5a157aaad7a9ceb6f013926abd5117f6966764a7e` | `8d6a87fb0569e4c36e36722c25e959476f104f7983822205b7d3d0da1a63eca1` |

The other **27** pins are unchanged, including every contract, schema and fixture this card's
oracles depend on: `contracts/ui/screens.yaml`, `contracts/schemas/report.schema.json`,
`contracts/http/openapi.yaml`, `contracts/ai/grounding.md`, `contracts/telegram/delivery.md`
and all seven §2 fixtures. By the byte rule of §0 this is nonetheless a `STALE_BASELINE`: a
pinned file changed, so the epoch name no longer describes the bytes. The Coordinator's
standing instruction for this wave is that `WP` is re-pinning and that a worker should record
the drift and continue rather than stop — recorded here, and the drift is a fact about the
epoch, not a claim that it does not matter.

**What this does and does not touch.** Neither file is read by any oracle of this card: they are
baseline bookkeeping, not behaviour. No test result above depends on their bytes, and no claim
in §5 or in the evidence manifest would change under the new hashes. The manifest keeps the §0
values, verbatim as card §13 requires, and states the drift in its own limitations rather than
silently recording hashes that no longer match disk. If the Coordinator issues a new epoch, this
card needs a re-pin, not a re-run.

---

*`PKT-TC-UIREPORTS` + `PKT-TC-UIREPORTS-FIX1` · `worker-W4D` · `lease_released_at` `e1` 2026-09-07T21:15Z, `e2` 2026-09-07T22:05Z · claim ceiling
`CONTRACT_READY` (card ceiling `IMPLEMENTATION_VERIFIED`; this record is `SELF_VALIDATION`).
After this handoff no further byte is written under this lease.*
