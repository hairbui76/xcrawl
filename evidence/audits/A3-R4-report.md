# AUDIT_REPORT `A3-R4` — scoped verification of `F-A3R3-01…03` (FC-P1 epoch 4)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-R4` · authority `AUTH-COORD-A3-R4` (parent `AUTH-OWNER-20260907-03`) · lease null |
| reviewer | `auditor-A3` — authored nothing in the repo; no repo write this round. Independent of `PKT-PC09-P1-FIX1`; `F-A3R3-02` concerns records written in my name, and I judge them here as their subject, not their author. |
| candidate | `FC-P1` epoch 4, 413 entries, `manifest_sha256 = 576a7572c8ac25852a5a44a200c1593c1f80887970755d5c6473e5105d40bd36` |
| quiescence | Recomputed start and end: **413/413** identical, header hash reproduces. `git status --porcelain` 101 before and after. Not `STALE`. |
| fix bytes | `evidence/index.json` `55e0c796…` · `evidence/manifest.schema.json` `25ddb1b7…` · `evidence/tools/e0_check.py` `02d6885a…` · `precode/review.md` `9c2b7973…` — all four match the Coordinator's stated hashes. |

## 1. Regression

`305 passed / 4 xfailed / 0 failed` (44.6 s) · `e0_check.py` **25 checks — PASS 25 · FAIL 0 ·
violations 0** · `verify_cards.py` **13/13**, epoch `PC10-PIN-P1d-20260907` · `ruff` clean ·
`mypy --strict` 25 files clean · `alembic heads` → `0004_merge_phase1_heads`, one head.

## 2. `F-A3R3-02` — execution provenance — **VERIFIED**

All seven records (`EV-A3-01…06` plus the new `EV-A3-07-round3`) now read:

* `producer_principal: "worker-W6n (transcription of auditor-A3)"`, `producer_role: "Worker"`;
* `execution.kind: "manual_procedure"`, **`command: null`** in all seven, **`exit_code: null`**
  in all seven, `working_directory` outside the repo;
* `manual_procedure` opens "KHÔNG CÓ LỆNH NÀO ĐƯỢC CHẠY CHO BẢN GHI NÀY" and states that
  `started_at`/`ended_at` (12:35:37→12:35:42Z) are W6n's **transcription** window, not an
  auditor run.

My own commands and numbers are now *quoted* under `oracle.observed.auditor_reported` with
`quoted_from` pointing at the report sections. I checked every quoted figure against my own
reports: 263/4/0 (35.1 s), 303/4/0 (40.7 s), 305/4/0 (45.5 s); e0 24/24 then 25/25;
verify_cards 3 211 then 3 214 assertions; epochs `P1c`/`P1d`; schema gate 8 then 10 tests; one
head. **Every one matches.** No claim of a command execution in my name survives anywhere in
the index.

`EV-A3-07` also states, unprompted, that the PC09 fix it describes "CHƯA được ai độc lập kiểm"
— which was true when written and is what this round supplies.

## 3. `F-A3R3-01` — E0-12 reach and the schema cap — **VERIFIED**

`E0-12`'s `checked` count rose 779 → 1 027: `evidence/runs/` is now walked (the tool's own note
says "18 run file(s) walked separately, 175 structured claim/status field(s) examined").
Mutation battery on a scratch copy (nothing in the repo touched); control PASS, restored PASS:

| mutation | expected | observed |
| --- | --- | --- |
| run record, `INTEGRATION_VERIFIED` | FAIL | **FAIL** (1 violation) |
| run record, `IMPLEMENTATION_VERIFIED`, no A3 citation | FAIL | **FAIL** (1 violation) |
| run record, `IMPLEMENTATION_VERIFIED`, **with** A3 citation | PASS | **PASS** |
| `evidence/index.json` record → `PRODUCT_ACCEPTED` | FAIL | **FAIL** (1 violation) |
| `IMPLEMENTATION_VERIFIED` into `precode/gates.yaml` (R3 control) | FAIL | **FAIL** |

`evidence/manifest.schema.json` tested directly, per review_type:

| review_type | `CONTRACT_READY` | `IMPLEMENTATION_VERIFIED` | `INTEGRATION_VERIFIED` | `LIVE_FEASIBILITY_VERIFIED` | `PRODUCT_ACCEPTED` |
| --- | --- | --- | --- | --- | --- |
| `SELF_VALIDATION` | accepted | **rejected** | **rejected** | **rejected** | **rejected** |
| `INDEPENDENT_AUDIT` | accepted | accepted | **rejected** | **rejected** | **rejected** |

That is the half that was missing in R3 (an `INDEPENDENT_AUDIT` record could previously carry
`PRODUCT_ACCEPTED`). All **72/72** live records still validate.

The two controls compose, and neither alone is sufficient — worth stating because that is the
actual argument: E0-12 decides *tree and citation* but not review_type (a `SELF_VALIDATION`
record claiming `IMPLEMENTATION_VERIFIED` *with* a citation still passes E0-12 — I mutated it);
the schema decides *review_type and label* but reads no citation. Together they close the gap
`F-A3R3-01` described.

### 3.1 Judgement on the two disclosed extensions

**(a) Rule applied to `evidence/index.json` (CR-PC09-17) — does NOT weaken; it strengthens.**
The index is where claims are aggregated and where a reader looks first, so a claim rule that
skipped it would police the parts and not the whole. Mutating an index record to
`PRODUCT_ACCEPTED` now fails. Strictly a widening of scope, ratified and disclosed.

**(b) `evidence/coordination/**` exempt from the free-text label sweep — does NOT materially
weaken, with one caveat.** The rationale is sound: a packet or ruling *quotes* the label it
dispatches about; it makes no claim, and it is not an evidence or ratification surface. I
verified the exemption is exactly as narrow as advertised:

* coordination `.md`, bare prose `PRODUCT_ACCEPTED` → passes (the exemption);
* **`evidence/handoffs/` is not exempt**: the same bare prose in a handoff → **FAILS**. Claim-
  bearing records are still swept;
* coordination **`.yaml`** with `claim_ceiling: PRODUCT_ACCEPTED` → **FAILS**, so the note's
  "their STRUCTURED fields are still checked" is verified, not merely asserted;
* skipped occurrences are counted and disclosed in the tool's own output rather than hidden.

Caveat, and the one new finding below: "structured fields are still checked" holds for
`.yaml`/`.json`, **not** for Markdown front matter — which the claim rule reads nowhere.

## 4. `F-A3R3-03` — stale epoch-2 statements — **VERIFIED**

`precode/review.md` §14 now reads "**305 passed / 4 xfailed / 0 failed** (45,5 s), một head
Alembic, cổng schema-vs-entities **10 test**", explicitly says these replace `303/4/0` and
`8/8`, and explains the +2 as the two tests the `F-A3R2-02` fix added. `F-A3R2-02` is listed
`VERIFIED (A3-R3 §2, mutation-tested)` and no longer appears in any
`limitations.unresolved_issue_refs`; the seven EV-A3 records now list `F-A3R3-01/02/03` there
instead, which is what was open when they were written.

The three `F-A3R3-*` rows carry status `FIX_PROPOSED`, **not** `CLOSED` — correct: a finding is
closed by the designated disposition authority after independent verification, which is what
this report supplies. I close nothing here.

## 5. New finding

### `F-A3R4-01` — LOW — "structured fields are still checked" does not cover Markdown front matter

`evidence/tools/e0_check.py`, E0-12 note: *"dispatch records (evidence/coordination/) are exempt
from the free-text claim sweep … their STRUCTURED fields are still checked."* True for
`.yaml`/`.json` (proved: a coordination `.yaml` with `claim_ceiling: PRODUCT_ACCEPTED` fails).
Not true for Markdown front matter: I put `claim_ceiling: PRODUCT_ACCEPTED` in the front matter
of a coordination `.md` — **passes**; and, to isolate the cause, in a **non-exempt**
`evidence/handoffs/` `.md` — **also passes**. So the claim rule reads `.md` front matter
nowhere; this is a pre-existing property, not something the exemption introduced. The
consequence specific to the exemption is that `evidence/coordination/*.md` now has **no**
claim-label control at all: the prose sweep was the only one reaching it.

Exposure is small — coordination records are dispatch artefacts whose labels carry no
evidentiary force, and `evidence/handoffs/**` (which does make claims) keeps the prose sweep.
**Remediation constraint:** either extend the structured claim scan to `.md` front matter (the
parsed front matter is already available as `rel + "#frontmatter"`), or narrow the note to say
"structured `.yaml`/`.json` fields". Do not leave a disclosure note asserting a reach the check
does not have — that is the same class of defect as `F-A3R3-01` itself. `OPEN`; no patch supplied.

**New findings: 1 (LOW). HIGH 0 · MEDIUM 0.**

## 6. Verdict

**Overall: PASS.** `F-A3R3-01`, `-02` and `-03` all VERIFIED by my own reproduction; both
disclosed extensions judged sound, one of them strengthening the gate. Per-card claim verdicts
are unchanged from `A3-R2` §5.1 and `A3-R3` §4 — auth's label still rests on the
`PROVISIONAL` `AMD-ENT-owner-01`, storage's is still narrowed to exclude
`write_blocked → healthy`. Residual list of `A3-R3` §5 stands unchanged, plus `F-A3R4-01`.
Completion ceiling: independent `AUDIT_REPORT` over the scope above — not product acceptance,
not a security assessment, no live calls.
