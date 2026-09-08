# HANDOFF — `TC-ui-runs-three-states`

| Field | Value |
| --- | --- |
| packet_id | `PKT-TC-UIRUNS` — card `agent-tasks/TC-ui-runs-three-states.md` (Phase 4, M4→M7, gate G5) |
| worker principal | `worker-W4C` |
| authority_id | `AUTH-COORD-TC-UIRUNS` (parent `AUTH-OWNER-20260908-10`; record `…/scratchpad/packets/PHASE4-6-card-dispatch.md`) |
| lease_id | `LEASE-TC-UIRUNS-e1` (exclusive on card §3 write set + handoff + evidence manifest) |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `IMPLEMENTATION_VERIFIED` for the read model of `SCR-runs` / `SCR-run-detail`, which is exactly the ceiling card §9 sets. The rendered experience is **E4 → `NOT_RUN`**. |
| next actor | Coordinator (then `W4D` — `web/src/lib/api.ts` now has content to extend) |
| review_type | `SELF_VALIDATION`. No independent audit was run and none is claimed. |
| lease_released_at | 2026-09-07T21:05Z (host clock; see §5) |

`DONE_WITH_CONCERNS`, for three reasons, all of them scope or contract facts rather than
defects in the code:

1. **`SG-01` fired and is reported, not worked around.** `contracts/ui/screens.yaml
   §global_rules.run_status_labels` names three labels whose conditions **overlap** and
   which together **do not cover** every `status` of `contracts/state/run.yaml §enums`.
   The card forbids inventing a display label for what the contract omits, so nothing was
   invented: `runStatusLabel()` returns `null` for an uncovered triple and the screen shows
   the machine value of `status`. See `CR-TC-uiruns-01`.
2. **The card's §13 asks for registration in `evidence/index.json`**, and that file is not
   in the write set the dispatch grants. It was not touched — `CR-TC-uiruns-05`.
3. **`E4` (render review on desktop and mobile) is `NOT_RUN`** by the dispatch's own
   instruction: a human looks. `SC15` in `acceptance/scenarios.yaml` declares
   `evidence_level_required: E4`, and its `mockable_vi` line is precisely what was proved
   here: "Sự phân biệt của ba bộ ba và sự vắng mặt của cụm bị cấm kiểm được ở E1 bằng grep
   trên copy hiển thị."

---

## 0. Wait gate and baseline

The dispatch note's three-part wait gate was satisfied before the first byte was written:

1. `git log -1 --format=%s` on `main` → `fb3944a `feat: Phase 3 (M3) + Phase 5 (M6, plain text) — AI adapter/analysis/embedding, Telegram linking/saved/delivery; REQ-OQ03, REQ-A5, Telegram facts``.
2. `agent-tasks/README.md` line 124 declares pin epoch **`PC10-PIN-P3b-20260908`**, and
   `evidence/handoffs/PC10-handoff.md` line 3339 carries the `PKT-PC10-FIX25` addendum for
   that epoch with `lease_released_at 2026-09-08T03:05Z`.
3. **SG-HASH**: `sha256sum` re-run against disk on all **26** pinned rows of the card's §0
   immediately before the first write (2 source rows + 24 contract/fixture rows) — **0 mismatches**, both before drafting and again at
   commit time.

No file under `contracts/`, `acceptance/`, `precode/` or `agent-tasks/` was modified. No git
mutation. Network was used only for the `npm` packages that were already installed.

---

## 1. Changes

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `web/src/lib/api.ts` | MODIFY (whole-file rewrite; this card owns it, CR-P0-04) | `a2db648ed78c32d9cedfe34276c4f350986c8a7928d5308bcbf02684a1320669` (2752 bytes) | `5c3e9630d30093fe939f56422aebf613edf7e64ef946121fbaf383d881442e79` | 16889 |
| `web/src/lib/runState.ts` | CREATE | ABSENT | `2993f50b4f36aeff46c8f3ea9386453763bbbbe875410c51ecf6c39ad9490da7` | 18036 |
| `web/src/routes/runs.ts` | CREATE | ABSENT | `3a1583404ee7c0a46e520bad6ae322476b8367b1727e06cf0d1435445b7c4660` | 12171 |
| `web/src/routes/runDetail.ts` | CREATE | ABSENT | `a330d8fcf3d80dc005836d687d57ebcad60facb35e4599b384628d7d282ae98b` | 12831 |
| `web/src/views/RunsList.tsx` | CREATE | ABSENT | `c78540a541197850c41440793a5efdd25cf1f76ba5b6abc79cd6cdea8dd9ce9f` | 5610 |
| `web/src/views/RunDetail.tsx` | CREATE | ABSENT | `f698d0953f6b45ba16a3f004ea7d785be20f5c67fe25eec85603d8c68f3b5a71` | 5474 |
| `web/tests/contract/runReadModel.test.ts` | CREATE | ABSENT | `73463a12a852cd20d02f93a9ac8f4617b5888abfa79a259e78b6d8bfcefabf69` | 28859 |
| `web/tests/integration/threeStatesDistinct.test.ts` | CREATE | ABSENT | `e87abe347891a250fe828e2f126ef0954a1f62e67379f553dac12bb9c1bae2b1` | 17860 |
| `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` | CREATE | ABSENT | (see below) | — |
| `evidence/handoffs/TC-ui-runs-three-states-handoff.md` | CREATE | ABSENT | (see below) | — |

**One superseded artifact is on disk and is disclosed rather than deleted.**
`evidence/runs/TC-ui-runs-three-states-E1-20260907T210226Z.json`
(sha256 `5eb8b10dd5a5dbc264c0d8ce558062cba4c672268f38dc05f9ff33718c75ff1d`, 18308 bytes) is an earlier attempt at the same
E1 manifest. It **fails** `evidence/manifest.schema.json`: its six
`limitations.unresolved_issue_refs` entries used the long CR id form, which the schema's
pattern rejects. The generator writes the file and validates afterwards, so the invalid
file exists. It was **not** removed: the write set this packet grants is `CREATE` of an
evidence manifest, not `DELETE` of one, and quietly erasing an evidence artifact is the
wrong instinct even when the artifact is mine and wrong. **The authoritative manifest is
the `…T210259Z` one**; the Coordinator can dispose of the other under a packet that grants
a delete.

**Nothing else was written.** In particular:

* **`web/src/App.tsx` was not touched**, so the two views are not yet reachable from the app
  shell's `/runs` route — that file belongs to the Phase 0 skeleton and is not in this
  card's §3. The shell still renders its placeholder there. `CR-TC-uiruns-04`.
* **No Alembic revision.** This card owns no entity and writes no server code; §1 of the
  card says "Không viết backend". The migration chain is untouched and still has one head.
* **`web/src/generated/` was not regenerated and not edited.** `contracts/http/openapi.yaml`
  is byte-identical to what `GENERATED_FROM.json` records
  (`28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92`), so
  `node scripts/generate.mjs --check` still reports no diff.

### 1.1 `web/src/lib/api.ts` — ownership handover

Per `CR-P0-04` and `agent-tasks/README.md §5.3`, this file is owned by the two UI cards; the
Phase 0 skeleton shipped a stub that deliberately carried **no CSRF logic**. This card
replaces it with the real client and keeps the stub's public surface (`ApiPath`,
`GetResponse`, `ApiError`, `apiBaseUrl`, `apiGet`) so nothing that compiled before stops
compiling. Nothing else in the repo imported it (`grep -rn 'lib/api' web/src web/tests` →
the file itself only).

**W4D extends, does not recreate.** The extension points are:
`OPERATION_PATHS` (append the `report.*` / `work.*` / `save.*` operations there and the
contract test picks them up automatically), and the `get` / `mutate` pair, which already
type-check any path in the generated contract.

---

## 2. What was built, and against which contract line

| File | Role | Contract it answers to |
| --- | --- | --- |
| `web/src/lib/api.ts` | typed owner-session client | `contracts/http/openapi.yaml` §securitySchemes (`ownerSessionCookie` AND `ownerCsrfToken` in one requirement for mutations), §parameters (`SchemaVersionHeader`, `RequestIdHeader`, `IdempotencyKeyHeader`, `CsrfTokenHeader`), `ErrorEnvelope`, `Ulid` |
| `web/src/lib/runState.ts` | the `(status, outcome, stop_reason)` triple and state → label | `contracts/state/run.yaml §enums` + `§legacy_enum_mapping.ui_three_states_vi` + `§invariants_owned I13`; `contracts/state/delivery.yaml §enums` + `DP-03`; `contracts/state/storage.yaml §ui_read_model UI-01..04`; `contracts/ui/screens.yaml §global_rules` |
| `web/src/routes/runs.ts` | read model + actions for `SCR-runs` | `screens.yaml §screens[SCR-runs]` |
| `web/src/routes/runDetail.ts` | read model + actions for `SCR-run-detail` | `screens.yaml §screens[SCR-run-detail]` |
| `web/src/views/RunsList.tsx` | renders the read model, decides nothing | REQ-AC15, I13, I09 |
| `web/src/views/RunDetail.tsx` | renders the read model, decides nothing | REQ-AC04, AMD-B03, I09, I13 |
| `web/tests/contract/runReadModel.test.ts` | state → view, and contract parity | card §8 oracle 1, 2, 4; §5 R5-01; §7 |
| `web/tests/integration/threeStatesDistinct.test.ts` | the three strings, on fixtures, through the client | card §8 oracle 1, 2, 3 |

### 2.1 The rule the card exists for

`contracts/state/run.yaml §legacy_enum_mapping.ui_three_states_vi` says the three states of
SRC-SPEC §8.3 are told apart by the **triple**, not by one enum. `runState.ts` implements
exactly that, and the tests read the fixture rather than a literal:

| Triple (fixture `m`, `given.rows.run`) | Label (fixture `m`, `expected.ui_labels`) |
| --- | --- |
| `(completed, empty, null)` | `Không có nội dung phù hợp` |
| `(completed, partial, limit_reached)` | `Đợt dừng sớm` |
| `(failed, failed, source_blocked)` | `Đợt thất bại` |

Three distinct strings; `expected.counts.distinct_labels = 3` is asserted as a set size, and
the forbidden phrase `Không có nghiên cứu mới` is asserted absent from the rendered DOM of
every screen state, including the empty one, and from the source of every file under
`src/views/` and `src/routes/`.

### 2.2 needs_user vs blocked vs delivery `unknown`

The contract gives `needs_user` and `blocked` the **same** label (`stopped_early`), so the
screen separates them by what it offers, with no copy written by this card:

* `needs_user` → `ACT-resume-run` / `ACT-resume-run-detail` appear (`visible_when` in
  `screens.yaml`), and `unblock_condition_vi` is `null`.
* `blocked` → **no resume button**, and the server's own `run.unblock_condition_vi` is
  displayed (`run.yaml`: NOT NULL when `status = blocked`).
* delivery `unknown` → `Chưa xác định — có thể đã gửi`, a fourth and independent dimension
  (I09), with the three `unknown_decision` options and the duplicate-message warning shown
  **before** a resend can be chosen (`screens.yaml` ACT-decide-unknown-delivery
  `rule_vi`; fixture `b` `expected.ui_requirement_vi`). The system never picks (AMD-B03) —
  `decideUnknownDelivery()` has no default for `decision`.

`delivery.decide_unknown` addresses a **part** (`/v1/deliveries/parts/{delivery_part_id}/decide`),
so the read model exposes `undecided_parts` and the decision is offered per part, which is
also what DP-02 requires.

### 2.3 Security shape

Reads send the HttpOnly `rr_session` cookie alone (`credentials: 'include'`); mutations send
that cookie **and** `X-CSRF-Token` read from the non-HttpOnly `rr_csrf` cookie, plus
`Idempotency-Key` and `X-Request-Id` as ULIDs matching `components.schemas.Ulid`. When
`rr_csrf` cannot be read, `mutate()` throws `MissingCsrfTokenError` and **issues no
request** — a call that is going to come back `CSRF_REJECTED` is a browser-state problem,
not a server fault, and firing it would hide that.

The CSRF obligation is also enforced at **compile time**: the generated types list
`X-CSRF-Token` in `parameters.header` for every mutation and omit it for reads, and
`runReadModel.test.ts` asserts that with five exported type-level assertions. A contract
edit that dropped the header would fail `tsc`, not a runtime test.

`ApiError.message` is built from `code` and `correlation_id` only; a test feeds an envelope
carrying `details_safe.cookie = 'super-secret-value'` and asserts the message does not
contain it (card §7: no transcript, key or cookie).

### 2.4 `SG-DENY` — the four forbidden edges that touch `MOD-web-ui`

`acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` gives this module four:
FE-01 (→ `MOD-data-store`, `CAPABILITY_DENIED`), FE-02 (→ `MOD-secret-service`,
`UNAUTHORIZED`), FE-03 (→ `EXT-ai-provider-api`, `CAPABILITY_DENIED`), FE-04 (→
`EXT-telegram-api`, `CAPABILITY_DENIED`). Three of the four are enforced at the browser's
network/process boundary, which a unit test cannot observe — the fixture itself says so for
FE-03 (`event_type: local_observation`, "oracle là đếm kết nối từ trình duyệt"). What is
proved here is the **structural** half: no file under `src/lib`, `src/routes` or `src/views`
contains an absolute `http(s)://` URL, the string `api.telegram.org`, the word `sqlite`, or
`secret.issue_task_credential`; and the client can only address the nine `operation_id`s of
card §4, checked against `contracts/http/openapi.yaml`'s own path→method→operationId table.
Observing the refusals as error codes is E3 and is `NOT_RUN` — see §5.

---

## 3. Verification

All commands run from `/mnt/virtual/repo/xcrawl/web`, Node v22.23.2, TypeScript 5.9.3, Vitest 3.2.7, ESLint 9.39.5, Prettier 3.9.6.

| # | Command | Exit | Result |
| --- | --- | --- | --- |
| 1 | `npm run typecheck` (`tsc --noEmit`) | 0 | no output |
| 2 | `npx eslint .` | 0 | no findings |
| 3 | `npx prettier --check .` | 0 | "All matched files use Prettier code style!" |
| 4 | `npm run test -- runReadModel` | 0 | **48 passed**, 0 failed |
| 5 | `npm run test -- threeStatesDistinct` | 0 | **15 passed**, 0 failed |
| 6 | `npm run test` (whole suite) | 0 | **74 passed / 4 files**, 0 failed — the 7 App-shell tests and the 4 generated-client tests are unchanged and still pass |

Card §8 lists its commands as `npm --prefix web run typecheck`, `npm --prefix web run test --
runReadModel` and `npm --prefix web run test -- threeStatesDistinct`; those are the same
commands, run from inside `web/` and also as a whole suite so that the two pre-existing test
files are shown not to regress.

**Card §8 oracles, one by one:**

| Oracle (card §8) | Where it is asserted | Result |
| --- | --- | --- |
| Three states (empty / limit / failed) give three different display strings; compare strings, not images (fixture `m`) | `threeStatesDistinct.test.ts` "fixture m, through the generated client and the rendered screen" | PASS |
| `needs_user` shows resume; `blocked` shows the unblock condition and **not** resume | `threeStatesDistinct.test.ts` "needs_user and blocked are told apart" (list + detail); `runReadModel.test.ts` "needs_user and blocked share the label but never the affordances" | PASS |
| Delivery `unknown` reads "chưa xác định" and offers `delivery.decide_unknown`; never "đã gửi" or "thất bại" | `threeStatesDistinct.test.ts` "delivery unknown" (4 tests) | PASS |
| Every action on the screen is in the `screens.yaml` action map | `runReadModel.test.ts` "action map" (4 tests), read from the contract file | PASS |
| Render review on desktop and mobile | — | **`NOT_RUN` (E4, human review)** |

---

## 4. Change requests

| ID | Severity | Contract | Finding |
| --- | --- | --- | --- |
| `CR-TC-uiruns-01` | **blocking for the labels it names** | `contracts/ui/screens.yaml §global_rules.run_status_labels` | The three label `condition`s **overlap with no stated precedence** and **do not cover** every `run.status`. Overlap: `(failed, failed, source_blocked)` satisfies `stopped_early` *and* `run_failed`; `(completed, empty, limit_reached)` satisfies `no_matching_content` *and* `stopped_early`. `delivery_status_labels` right above it *does* state a precedence (DP-03), so the omission is asymmetric. Coverage gap: `queued`, `running`, `waiting_retry`, `cancelled` and a plain `(completed, complete, null)` match none of the three. Additionally `contracts/state/run.yaml §legacy_enum_mapping.ui_three_states_vi` classifies `(blocked, null, source_blocked)` as **"đợt thất bại"** while `screens.yaml` puts `status = blocked` under **`stopped_early`** — the two contracts disagree on that one triple. **Handled without inventing anything**: precedence `run_failed > stopped_early > no_matching_content` (derived from fixture `m`'s own `ui_labels` for the first, from I13 for the second), and `null` for an uncovered triple with the machine value of `status` rendered instead. **Requested**: a precedence rule and a total label table in `screens.yaml`, and a ruling on the `blocked` disagreement. |
| `CR-TC-uiruns-02` | high | `contracts/http/openapi.yaml`; `contracts/ports.yaml` | `run.list`, `run.get`, `run.run_now`, `run.resume`, `run.cancel`, `worker.get_status` and `delivery.get_status` all answer `GenericObject` (`response_schema_planned: null` in ports.yaml), which `openapi-typescript` renders as `Record<string, never>` — a type that can hold nothing. The UI therefore cannot get its response shape from the generator; it parses defensively against the field names of `screens.yaml §read_model` and `run.yaml §fields`, and `api.ts` widens a placeholder body to an open record. The contract says the owning package must replace these with closed schemas before G3. **Until it does, the UI's field names and W6A's / W5C's actual response keys have not been reconciled against a common schema** — a real integration risk between two cards in the same wave, and the reason this card does not claim `INTEGRATION_VERIFIED`. |
| `CR-TC-uiruns-03` | medium | `contracts/ui/screens.yaml` | No table maps `run.stop_reason` (8 values) to Vietnamese display text, although `SCR-runs.read_model` lists `runs[].stop_reason` as a displayed field and card §8 requires a `blocked` run to show its unblocking condition. `unblock_condition_vi` covers `blocked` (it is server data). For the other seven the screen renders the **enum token** rather than a sentence this card would have had to invent. A phrase table belongs in `screens.yaml`. |
| `CR-TC-uiruns-04` | medium | write-set scope | `web/src/App.tsx` is not in this card's §3, so `/runs` and `/runs/:id` still render the Phase 0 placeholder and the two views are not reachable in the running app. The read model and the views are complete and tested; only the route wiring is missing. Needs a one-line packet amendment, or an owner for `App.tsx`. |
| `CR-TC-uiruns-05` | low | card §13 vs dispatch write set | §13 asks that the run be registered in `evidence/index.json`; that file is not in the granted write set. Not touched. Same finding as `CR-TC-adapter-05`. |
| `CR-TC-uiruns-06` | low | `contracts/ui/screens.yaml §global_rules.five_display_states` | The contract enumerates five *exceptional* states and no name for the ordinary populated render, so a total read-model field is impossible from the contract alone. `ScreenDisplayState = DisplayState \| 'ready'` adds that one name; `'ready'` carries no display string. Worth naming in the contract so two screens do not invent two different words for it. |

The dispatch packet writes CR ids as `CR-<card>-nn`; `evidence/manifest.schema.json` constrains
`limitations.unresolved_issue_refs` to `^CR-TC-[A-Za-z]+-[0-9]{2}$` — one alphabetic token, no
hyphens — so the short form `CR-TC-uiruns-nn` is used, exactly as `TC-analysis-adapter-validation`
used `CR-TC-adapter-nn`. The ids above and in the manifest are the same six.

None of these were worked around by editing a contract, a fixture or an expectation.

---

## 5. Limitations — what is **not** established

* **`E4` is `NOT_RUN`.** No screenshot, no desktop or mobile render review, no human
  reviewer. `SC15` requires E4 for the user-comprehension claim and `screens.yaml` has no
  render fixture. What is proved is the E1 half its own `mockable_vi` line describes.
* **`E2` is `NOT_RUN`** and does not apply: this card writes no state and touches no SQLite.
* **`E3` is `NOT_RUN`**: no live server, no real X / Telegram / AI call, no browser
  automation. The forbidden-edge refusals of FE-01…FE-04 are asserted **structurally**
  (no such string, no such reachable operation), not by making the call and receiving
  `CAPABILITY_DENIED` / `UNAUTHORIZED`. Card §5's R5-01 error-code boundary is therefore
  established for *code selection on the client side* only.
* **The backend is a fixture.** `run.list`, `run.get`, `worker.get_status` and
  `delivery.get_status` are answered by an in-test transport. The scheduler
  (`TC-scheduler-lease-claim`, W6A, same wave) and delivery (`TC-telegram-unknown-delivery`,
  W5C, done) have **not** been exercised against this client. Response *shape* agreement is
  unproven — `CR-TC-uiruns-02`.
* **Self-reference.** The fixture bodies that travel through the client were written by this
  worker, from `screens.yaml`'s field names. Their agreement with the read model proves
  internal consistency, not that a real server sends those keys.
* **Storage health** is read from the `run.list` / `run.get` body. `health.get_readiness` is
  in card §4 and in `OPERATION_PATHS` but **no screen calls it yet** — the readiness screen
  is not this card's. Recorded so the entry is not mistaken for a tested path.
* **`SC20`** (stale lease) and **`SC26`** (disk full) are anchors in card §8 but are
  server-side scenarios; only their UI consequence is exercised here (`storage_health !=
  healthy` ⇒ last-known label + disabled mutations). The state transitions themselves are
  `NOT_RUN` for this card.
* **Accessibility, i18n and visual design are not assessed.** `screens.yaml
  §global_rules.visual_design` (REQ-S4-10) leaves design deliberately open, so the views
  carry no styling; that is a contract position, not a finished appearance.
* This is **`SELF_VALIDATION`**. No independent audit was run. The phrase "independent audit
  passed" appears nowhere in this handoff and would be false if it did.
* Host clock reads 2026-09-07 while the dispatch packet and the pin addendum are dated 2026-09-08. Every timestamp in this handoff and in the manifest is the clock's, not the calendar's.

---

## 6. Evidence

* Manifest: `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (sha256 `943ee72270465cf1950f42b3f147f7f5bb2815bb2a77fac6634af9ec62f6c03f`, 18182 bytes) (`EVM-TC-ui-runs-three-states`, `EV-E1-10-tc-ui-runs-three-states`),
  validated against `evidence/manifest.schema.json` with `jsonschema` Draft 2020-12 and a
  format checker.
* `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`;
  `contract_hashes` copied verbatim from the card's §0.
* `review_type` = `SELF_VALIDATION`; every item that did not run is recorded `NOT_RUN`.

---

## 7. Claim

**Claim.** `IMPLEMENTATION_VERIFIED` for the read model of `SCR-runs` and `SCR-run-detail`
— the mapping from `(status, outcome, stop_reason)`, `delivery.state` and `storage_health`
to display strings and to the contract's action map — and for the owner-session transport's
CSRF and header construction.

**Baseline.** spec `d35e1f2d…`; pin epoch `PC10-PIN-P3b-20260908`, 26 rows re-hashed, 0 mismatches; `CT-ui-screens` 0.1.0, `CT-state-run` 0.6.0, `CT-state-delivery` 0.2.0,
`CT-state-storage` (see manifest), wire contract `info.version` 0.3.0; implementation
revision = the eight files of §1 with the hashes listed there.

**Requirements covered.** REQ-AC15, REQ-S8.3-01/-02/-03, REQ-D57 (empty period visible on
Runs), REQ-D11, REQ-D12 (last_run_at display-only), REQ-D14, REQ-S4-06, REQ-S4-07,
REQ-S5.4-04, REQ-AC04 (alert count surfaced), REQ-AC14 (report readable at every delivery
state — the UI half), REQ-D45. Invariants I13 and I09 are asserted directly.

**Evidence manifest IDs.** `EVM-TC-ui-runs-three-states`.

**Observed result.** 63 card tests, 0 failures; 3 distinct display strings for the three REQ-AC15 triples, matching `expected.ui_labels` of fixture `m` exactly; 0 occurrences of the forbidden phrase in any rendered DOM or in the source of `src/views` and `src/routes`; resume offered on `needs_user` and withheld on `blocked`; delivery `unknown` never rendered as `sent` or `failed`; 0 mutations without `X-CSRF-Token`, 0 reads with one, 0 requests issued when `rr_csrf` was unreadable; 0 actions outside the `screens.yaml` action map; 0 operations outside card §4; 0 absolute URLs in `src/`. `tsc`, `eslint` and `prettier` clean; the generated client still regenerates with no diff.

**Not established.** Everything in §5, and in particular: the rendered experience (E4), the
response-shape agreement with the server cards (`CR-…-02`), the labels for the run statuses
`screens.yaml` does not cover (`CR-…-01`), and the browser-boundary enforcement of FE-01…04.

**Open issues.** `CR-TC-uiruns-01` … `-06`.

**Review type.** `SELF_VALIDATION`.

---

*`PKT-TC-UIRUNS` · `worker-W4C` · `lease_released_at` 2026-09-07T21:05Z (host clock; see §5) · ceiling
`IMPLEMENTATION_VERIFIED` for the read model · no item in this handoff is an independent
audit.*

---

# ADDENDUM — `PKT-TC-UIRUNS-FIX1` (lease `LEASE-TC-UIRUNS-e2`)

| Field | Value |
| --- | --- |
| status | **`STALE_BASELINE`** — see §F5. The work itself is `DONE_WITH_CONCERNS`; the record is stale by the byte rule, not because anything failed. |
| trigger | Coordinator packet `PKT-TC-UIRUNS-FIX1` + its addendum: (a) close `CR-TC-uiruns-02` by recording the real backend responses; (b) mark the superseded manifest `STALE`; (c) answer `E0-20-card-fixture-accounting`. |
| tests | **120 passed / 6 files**, 0 failed. This card: 48 + 23 = **71**. |
| lease_released_at | 2026-09-08T00:55Z (host clock) |

## F1. Changed in FIX1

| Path | Operation | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `web/src/lib/runState.ts` | MODIFY | `fed501e6bd22c47e1d2a82ca723bb312af03ee389e3776fd65425f765048c4ca` | 18506 |
| `web/src/routes/runs.ts` | MODIFY | `3b04fa78495437634f0c2a29349277a75e53b318b37528b4cc6c39f72fd79e67` | 14293 |
| `web/src/routes/runDetail.ts` | MODIFY | `9737b62d5ad8be84db2af95c67695dd460e5cb9def207e3c888e5428f144a775` | 13198 |
| `web/src/views/RunsList.tsx` | MODIFY | `cb6a02674f89fc7543a496da9a8c1d68ce17f51391a2931c24a7f9e1de8f16a9` | 5619 |
| `web/src/views/RunDetail.tsx` | MODIFY | `5cefa65317dad03ba112a2ac1b2f19897f20716150154dd39532d9dd669c00ba` | 5483 |
| `web/tests/integration/threeStatesDistinct.test.ts` | MODIFY | `8e56e4e669dd09c80808434a1fdb77d904721813c091c164b6bf43d824c6a934` | 31743 |
| `evidence/runs/TC-ui-runs-three-states-E1-20260908T005139Z.json` | CREATE | `6ee5b8a3309f1e629559a961d105745e4238b6b39a444a3f59ef8642fb7f2943` | 21933 |

`web/src/lib/api.ts` was **not** touched in FIX1. `TC-ui-reports-detail` (W4D) extended it
after the E1 handoff, adding `REPORTS_OPERATION_PATHS` and a `delete` verb alongside — my
`OPERATION_PATHS` still holds exactly the nine operations of card §4 and my contract test
still asserts that, so the two cards share the file without either owning the other's table.

## F2. `CR-TC-uiruns-02` — the shapes are now recorded, not assumed

The four bodies were recorded from the servers W6A and W5C actually wrote —
`server/app/jobs/router.py` and `server/app/delivery/router.py` — driven through
`fastapi.testclient.TestClient` over a throwaway migrated SQLite file with the owner logged
in through `/v1/auth/login`. The capture script is
`…/scratchpad/w4c/capture.py`; it imports the server package **read-only**, wrote nothing
under `server/`, opened no socket, and deleted its database on exit. All four answered `200`.

Recording them found **four real disagreements** between what `screens.yaml §read_model`
names and what the server sends. All four are now absorbed by the read model, and the
recorded bodies are embedded in `threeStatesDistinct.test.ts` §5 so a future rename fails a
test instead of a screen:

| # | `screens.yaml` / this card expected | The server actually sends | Handling |
| --- | --- | --- | --- |
| 1 | a run row keyed `id` | `run_id` | both accepted, `run_id` first |
| 2 | `as_of` **and** `storage_health` on every business screen (UI-01) | **neither**, on `run.list` or `run.get` | reported: `storage_health` is now `StorageHealth \| null` and the screen renders `—`. It is **not** read as `healthy` — "we were not told" and "the database is fine" are the two things I13 forbids merging. `CR-TC-uiruns-07`. |
| 3 | flat `collector_online_state` + `last_run_at` | `{"workers": [...]}`, per-row `online_state` / `last_run_at` | the collector row is selected out of `workers[]`; an empty list renders `—`, never `offline` (I13) |
| 4 | a delivery part keyed `id` | `delivery_part_id` | both accepted |

Eight new tests assert this. The three REQ-AC15 labels are now derived from the **real**
`run.list` body, `needs_user`/`blocked` keep their affordances through it, and the real
`run.get` + `delivery.get_status` pair drives Run detail: aggregate reads
"Chưa xác định — có thể đã gửi" while the part that really was sent still reads
"Đã gửi Telegram" — DP-01 gives every part its own receipt, and hiding that would be the
opposite error to the one I13 forbids.

`CR-TC-uiruns-02` is **narrowed, not closed**: the wire contract still types these bodies
`GenericObject`, so nothing stops the shapes drifting again tomorrow. What changed is that
the drift would now be caught here.

## F3. New change requests

| ID | Severity | Finding |
| --- | --- | --- |
| `CR-TC-uiruns-07` | high | `run.list` and `run.get` send neither `as_of` nor `storage_health`, which `contracts/state/storage.yaml §ui_read_model UI-01` requires of **every** business screen; and `run.get` sends none of `items_collected`, `items_new`, `checkpoint`, `errors`, `alert_intent_count`, `delivery_status`, all of which `screens.yaml §screens[SCR-run-detail].read_model` lists as fields of the screen. The UI renders them as missing rather than as zero. Owner: `MOD-job-service` (`TC-scheduler-lease-claim`). |
| `CR-TC-uiruns-08` | medium | `E0-20-card-fixture-accounting` walks **only** the Python `tests/` tree, so a card whose §3 write set is entirely under `web/` can never satisfy it by testing. See §F4. |

## F4. `E0-20-card-fixture-accounting` — this card cannot go green honestly

`PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py` → **26 checks, PASS 25,
FAIL 1, 3 violations**; one of the three names this card:

> `agent-tasks/TC-ui-runs-three-states.md`: §2 fixture
> `acceptance/fixtures/telegram/m-three-run-states-distinct-text.json` is referenced by no
> test and named nowhere in the card's handoff

The finding is a **false negative of the checker, and the fixture is exercised.**
`acceptance/fixtures/telegram/m-three-run-states-distinct-text.json` is loaded by name and
used as the oracle in **both** of this card's tests —
`web/tests/contract/runReadModel.test.ts` reads it for the state→label table and the
forbidden-phrase check, and `web/tests/integration/threeStatesDistinct.test.ts` drives its
three `given.rows.run` triples through the generated client into the rendered screen and
compares against its `expected.ui_labels` and `expected.counts.distinct_labels`. Both files
are under `web/tests/`. `check_card_fixture_accounting` builds its `tests_text` by walking
`os.path.join(repo.root, "tests")` only, so `web/tests/` is outside the scanned tree and no
UI card's fixture can ever match.

The other accepted disposition is a handoff paragraph containing `NOT_RUN`. **That would be
false**: this fixture ran, and it is the card's primary oracle. Writing `NOT_RUN` to turn a
check green is the exact failure mode `agent_profile/protocol.md §9` forbids, so the worker
refuses and reports `CR-TC-uiruns-08` instead. The fix belongs in `evidence/tools/e0_check.py`
(walk `web/tests/` as well, or take the language trees from `agent-tasks/README.md §5.3`),
which this card may not write.

The other five §2 fixtures are accounted for: `e-limit-reached-stop`,
`c-challenge-mid-batch`, `d-empty-period-coverage-only`,
`b-response-lost-unknown-operator-decides` and `a-default-deny-sweep-36-edges` are each
named by a Python test as well as by this card's Vitest tests.

## F5. `STALE_BASELINE` — stop and report

Re-running SG-HASH at the end of FIX1 found **two of the 24 pinned contract rows changed
byte on disk while this packet was running**:

| Pinned file | §0 pin | On disk now |
| --- | --- | --- |
| `precode/baseline.json` | `52af62c8…` | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` |
| `precode/decision-register.md` | `b26cf51a…` | `8d6a87fb0569e4c36e36722c25e959476f104f7983822205b7d3d0da1a63eca1` |

`agent-tasks/README.md` still declares `PC10-PIN-P3b-20260908`, and the card's §0 still
names it, so **two different byte sets now carry one epoch name** — the situation
`CR-PC10-15` describes and §0 forbids in as many words: "Quy tắc `STALE` đọc **byte**, không
đọc ý định."

**Impact review.** The remaining **22 of 24** pinned rows match, and they include every
contract this card actually reads: `screens.yaml`, `run.yaml`, `delivery.yaml`,
`storage.yaml`, `openapi.yaml`, `ports.yaml`, `modules.yaml`, `errors.yaml`,
`entities.yaml`, `retry-policy.yaml`, both ADRs and all six fixtures. The two drifted files
are governance documents; no oracle of this card reads either. Both were already `M` in
`git status` before this session and changed again mid-packet, alongside a new
`precode/owner-decisions-10.md`.

Accordingly the FIX1 manifest carries `result: STALE` with a `stale_reason` naming both
hashes — **not** `FAIL`: 120/120 tests pass and no oracle broke. Per SG-HASH the worker
**stopped** at that point: no further code was written after the drift was detected, nothing
was rebased onto the new bytes, and a **new baseline / pin epoch is requested** before this
card is frozen or audited.

## F6. The superseded manifest

`evidence/runs/TC-ui-runs-three-states-E1-20260907T210226Z.json` now carries
**`result: "STALE"`** as instructed, plus a first `not_checked_vi` entry naming the reason
(its six `unresolved_issue_refs` used the long CR id form the schema's pattern rejects, so
the record never validated). It is sha256 `6bd8ee1ad461dfe026ae59b94a028e043d00c883c3f16109d286066051b144ca` at 18980 bytes and was **not**
deleted. The authoritative record for FIX1 is `evidence/runs/TC-ui-runs-three-states-E1-20260908T005139Z.json`.

*`PKT-TC-UIRUNS-FIX1` · `worker-W4C` · `lease_released_at` 2026-09-08T00:55Z ·
status `STALE_BASELINE` · no item in this addendum is an independent audit.*
