# AUDIT_REPORT `A3-R2` — scoped re-review of `F-A3R1-01…15` + amendment `AMD-ENT-owner-01` (FC-P1 epoch 2)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-R2` · authority `AUTH-COORD-A3-R2` (parent `AUTH-OWNER-20260907-03`) · lease null |
| reviewer | `auditor-A3` — same principal as `A3-R1`; **independence intact**: I authored nothing in the repo, wrote nothing into it this round either, and I am independent of `AMD-ENT-owner-01` (raised as a finding by me, drafted and signed by PC02/Coordinator, not by me). |
| candidate | `FC-P1` epoch 2, 386 entries, `manifest_sha256 = 4ddb275f4cbb36c8b1619e213a97aca7a69631fe5d0224a40db2da5605c5590d` |
| quiescence | Recomputed at start **and** end: 386/386 `path\|sha256\|bytes` identical, header hash reproduces exactly. `git status --porcelain` 63 entries before and after; no new untracked path outside `.gitignore`. **Not `STALE`.** |
| epoch delta | vs epoch 1: 4 files added (`server/app/ingest/__init__.py`, `server/migrations/versions/0002b_shared_move_set_tables.py`, `tests/contract/test_schema_matches_entities.py`, one re-issued identity evidence manifest), 51 modified, 0 removed. |

## 1. Evidence reproduction (epoch-2 bytes, `uv sync --all-packages --frozen`)

| Gate | Workers' claim | My observation | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` (workspace) | 303 / 4 xfailed / 0 failed | **303 passed, 4 xfailed, 0 failed** (40.7 s), exit 0 | REPRODUCED |
| `ruff check .` | green | `All checks passed!` | REPRODUCED |
| `ruff format --check .` | green | `61 files already formatted` | REPRODUCED |
| `mypy` (strict, `server/app`) | green | `Success: no issues found in 25 source files` | REPRODUCED |
| `generate.py --check` | no diff | `generated tree matches a fresh run of the generator` | REPRODUCED |
| `openapi-spec-validator` | OK | `contracts/http/openapi.yaml: OK` | REPRODUCED |
| `verify_cards.py` | 13/13, epoch `P1c` | **13 PASS / 0 FAIL, 3 214 assertions, 0 violations**, epoch `PC10-PIN-P1c-20260907` | REPRODUCED |
| `e0_check.py` | 24/24 | **24 PASS · 0 FAIL · 0 violations** | REPRODUCED |
| `tests/contract/test_schema_matches_entities.py` | 8/8 | **8 passed** | REPRODUCED |
| `alembic heads` | one head | `0004_merge_phase1_heads (head)` | REPRODUCED |

Still 4 `xfail(strict=True)`, all pre-existing and all declared; still no `skip` anywhere.

## 2. Verification of `F-A3R1-01…15`

| id | verdict | evidence |
| --- | --- | --- |
| `F-A3R1-01` schema depends on branch order | **VERIFIED** | `0002_base_entities` is now the sole `CREATE TABLE owner`, and the auth revision `Revises: 0002_base_entities` instead of `0001`. I built the database under **four** traversal orders (default, auth-branch-first, identity-first, ingest-first) and hashed the full `sqlite_master` (type, name, sql) each time: **one signature, `187f4dfb…`, for all four**. The shipped `owner` now carries `CHECK (length(display_name) BETWEEN 1 AND 120)` **and** the `created_at` GLOB check in every order. |
| `F-A3R1-02` undeclared credential columns | **VERIFIED** | `AMD-ENT-owner-01` declares all four. My own `PRAGMA table_xinfo` sweep over all 16 business tables vs `entities.yaml`: **0 column differences in both directions** — no shipped column is undeclared, and no declared field is missing. (See `F-A3R2-02` on the *guard* for this property, which is weaker than the property itself.) |
| `F-A3R1-03` runs not in `evidence/index.json` | **DEFERRED** (per packet) | Still **0** hits for the run ids; `evidence/index.json` byte-identical to `da886f8`. Not verified, not re-raised. |
| `F-A3R1-04` five foreign tables in the identity revision | **VERIFIED** | New `0002b_shared_move_set_tables.py` creates all five; its header carries the ownership table (`saved_snapshot`/`saved_item` → `MOD-saved-service`/`TC-saved-snapshot`, `analysis`/`work_label` → `MOD-analysis-service`, `first_announced_ledger` → `MOD-report-service`) and keeps the reason. `0003_tc_canonical_identity_merge` now creates only identity's own tables. |
| `F-A3R1-05` unenforced FKs | **VERIFIED** | `PRAGMA foreign_key_list`: `checkpoint` and `ingest_receipt` now both carry `('owner','owner_id','id')`, and `post` now carries `('ingest_receipt','ingest_receipt_id','id')` from the rebuild. Every table except `owner` itself now has the owner FK. |
| `F-A3R1-06` in-process lockout | **VERIFIED** (independently) | `failed_login_count` + `locked_until` on `owner`, written in the login transaction. My own harness: 5 wrong passwords → row `(0, '2026-09-07T11:47:35.812Z')`; then a **brand-new `Engine` and a brand-new `AuthService`** (a real restart, not a reset method) → the *correct* password is refused with `RATE_LIMITED` and a `retry_after_ms`. |
| `F-A3R1-07` `faults.py` outside every write set | **VERIFIED** | `P0-skeleton-handoff.md` §B.1 adopts it into the Phase 0 write set as `ADOPT (không sửa)` with sha256 `035547f3…` / 4 274 B / 116 lines, plus a `server/app/db/` convention entry. Adopted, not retro-edited into a card §3. |
| `F-A3R1-08` `SG-DENY` coverage | **VERIFIED** | The 36 sweep rows are now partitioned and the partition is asserted: `12 UNAUTHORIZED / 10 FORBIDDEN_EDGE / 14 CAPABILITY_DENIED`, `sum == 36`. The 12 are exercised through the scheme decision (`assert len(checked) == 12`), the 10 through `require_edge` raising `ErrorCode.FORBIDDEN_EDGE` (`== 10`), and the 14 are held in `NOT_TESTABLE_AT_THIS_LAYER` with a per-ref reason, asserted non-empty and asserted disjoint from the exercised set. The floor-of-five is gone. |
| `F-A3R1-09` unaccounted fixtures | **VERIFIED** | `e2e/a-happy-path-schedule-to-delivered` — its two `ingest.submit_batch` events are now **executed** against real rows (commit boundary, performer, strictly increasing `max_ingest_sequence`), the other sixteen recorded `NOT_RUN`. `recovery/g-ssrf-redirect-private` — recorded `NOT_RUN` with a substantive reason, and a test asserts every `NOT_RUN` disposition carries one (`len > 60`). |
| `F-A3R1-10` missing `__init__.py` | **VERIFIED** | `server/app/ingest/__init__.py` present with a real module docstring. |
| `F-A3R1-11` unwired guard / no probe table | **PARTIAL** | Wiring half **fixed**: `install_storage()` is called unconditionally and always sets `app.state.storage_guard`; `server/app/ingest/router.py:172-177` adopts that same object into the context at request time, so the gate is live on the bare factory. Recovery half **unchanged**: `T-ST-02`'s probe table still does not exist (`CR-TC-storage-04`), so `write_blocked → healthy` still cannot fire on its own in a deployment. Correctly out of scope for this wave; must stay in the "not established" list. |
| `F-A3R1-12` plaintext bearer lookup | **VERIFIED** | `TokenRegistry.kind_for` hashes the presented token and walks **all** stored digests with `hmac.compare_digest` without early return. |
| `F-A3R1-13` include outside its delimiters | **VERIFIED** | All four includes now import inside their own delimiters. (Three cards use `>>> … <<<` and identity kept `--- BEGIN/END ---`; both are clearly delimited — cosmetic, not raised.) |
| `F-A3R1-14` missing timestamp CHECK | **VERIFIED** | `owner.created_at` now has the millisecond GLOB check, as do `password_updated_at` and `locked_until`, each guarded for NULL. A new generic test asserts every prose CHECK in `entities.yaml` has a matching clause on disk. |
| `F-A3R1-15` README `uv sync` | **VERIFIED** | All three occurrences now read `uv sync --all-packages`, including the CI-job table row at line 102. |

**13 VERIFIED · 1 PARTIAL (`F-A3R1-11`) · 1 DEFERRED (`F-A3R1-03`) · 0 NOT_VERIFIED.**

## 3. Contract amendment `AMD-ENT-owner-01`

`contracts/data/entities.yaml` is the **only** file under `contracts/` that changed since
`da886f8` (`git diff --stat` over `contracts/` shows one file); `acceptance/` is untouched;
`precode/` changes are `change-control.md`, `decision-register.md` plus the previously
recorded PC00 ratification files. File sha256 `f5ea0511f885159fedbb48bf939a9bd1436707f12007403c57808c9f5026c77e`, as the Coordinator stated.

**Verdict: ACCEPT, with one defect (`F-A3R2-01`).** What is right:

* Exactly four fields added after `created_at`; I diffed the five original field lines and
  they are unchanged **character for character**. `version` 0.1.0 → 0.2.0.
* An `amendments:` block at a new §0b with `amendment_id`, `status: PROVISIONAL`,
  `decision_refs: [CR-TC-AUTH-02, CR-TC-AUTH-03]`, `finding_refs: [F-A3R1-02, F-A3R1-06]`,
  before/after, and a `reason_vi` that cites `secrets.md` §2.1–§2.3 and `REQ-D05` — i.e. it
  closes a gap between two already-frozen files rather than inventing a product decision.
* `ratification.kind: coordinator_technical_amendment` with `authority` and
  `parent_authority`, and an explicit `owner_disclosure_vi`: must be put to the Owner next
  round, **"Owner CÓ THỂ phản đối"**, and if so the columns come out. Status is
  `PROVISIONAL`, *not* `ACCEPTED (OD-20260907-01)` — the amendment says in as many words
  that OD-20260907-01 never mentioned these columns.
* `claim_ceiling` stays `CONTRACT_READY` **with** a written re-verification requirement
  naming A3-R2, because A2-R4 certified a version that did not contain these fields. That is
  the honest handling: the ceiling is not silently inherited.
* `not_claimed_vi` explicitly refuses to close `F-A3R1-02` / `F-A3R1-06` — correct, closing
  is disposition authority's, not the author's.
* `change-control.md` §10 carries the CR in the §1 format (`cr_id`, `raised_by`,
  `addressed_to`, `status`, `source_of_change`, `before`, `after`, `reason`, `affected`,
  `migration`), merges `CR-TC-AUTH-03` into one impact set per §6 with a stated reason, and
  records the rollback path. `decision-register.md` carries the row at **PROVISIONAL** with
  the authority chain and "may object". `change-control.md` version 0.1.0 → 0.1.1 (patch),
  correct for an append.
* The four columns are semantically sound: `password_hash` is barred from every read model,
  log and backup export; `locked_until` must not reveal whether the account exists; the
  non-goals explicitly refuse a login-history table and any automated password-recovery
  channel.

## 4. New findings (fix diff only)

### `F-A3R2-01` — MEDIUM — the version-bump justification cites a rule that does not exist

`contracts/data/entities.yaml` `amendments[0].version_rule_vi` justifies "minor" by citing
`precode/change-control.md` §2 **and** "`allowed_without_major_bump` (mục 4, khóa
`additive_only_rules`)". Neither key occurs anywhere in `change-control.md` — I grepped the
whole `precode/` tree and both strings appear **only inside `entities.yaml` itself**, in
this citation. `change-control.md` §4 is "Ma trận vô hiệu hóa bằng chứng", not a bump-rule
exemption list. This matters because it is the *only* support offered for the one column
that is not optional: §2's minor row reads "Thêm trường **optional**", and
`failed_login_count` is `nullable: false`. The three nullable columns are plainly minor; the
NOT NULL one is defensible on migration grounds (constant DEFAULT, no backfill, and the
amendment says so) but the rule as written does not cover it, and the citation offered
instead resolves to nothing. **Remediation constraint:** either add the exemption to
`change-control.md` §2 as a real rule and cite it correctly, or drop the citation and
justify the NOT NULL column on the `migration:` grounds alone. Do not leave a contract
asserting a rule key its own rule file does not define.

### `F-A3R2-02` — MEDIUM — the new schema guard is blind to generated columns and is one-directional

`tests/contract/test_schema_matches_entities.py` uses `PRAGMA table_info` at all four call
sites (lines 144, 154, 171, 228) and `PRAGMA table_xinfo` nowhere. `table_info` does not
list STORED generated columns, so `analysis.target_key`, `saved_item.target_key` and
`work_label.target_key` — real columns, two of them inside declared unique keys — are
checked by **nothing** in this file: not for declaration, not for nullability, not for PK.
They are not exempted, they are invisible. Separately,
`test_every_table_and_column_is_declared_by_an_entity` asserts only `columns <= fields`; a
field declared in `entities.yaml` but never created by a migration would pass. My own
`table_xinfo` sweep confirms there is **no live defect today** (0 differences in both
directions), so this is a gap in the guard, not in the schema — but the guard is the
remediation proof for `F-A3R1-02`, and it is weaker than the claim made for it.
**Remediation constraint:** use `table_xinfo`, assert set equality in both directions, and
give generated columns an explicit, reasoned exemption from the `NOT NULL` rule rather than
letting the pragma hide them.

### `F-A3R2-03` — MEDIUM — three of four cards did not re-issue an evidence manifest after the fix wave

Only `TC-canonical-identity-merge` re-issued (`…E1-20260907T111124Z.json`). The other three
still carry manifests whose `ended_at` predates the fix wave (auth 10:15:29Z, storage
10:05:04Z, ingest 10:27:23Z) while their migrations, routers, services and tests were all
rewritten. This is not merely stale metadata: I re-hashed every `path`+`sha256` pair inside
each manifest, and `TC-storage-write-blocked-readiness-E1-20260907T100943Z.json` pins **4
files whose bytes no longer match disk** — `server/app/storage/guard.py`,
`server/app/health/router.py`, `server/app/health/__init__.py`,
`tests/integration/test_readiness_independent_channel.py`. The manifest certifies a tree
that no longer exists, and its recorded test counts are from before the fix.
**Remediation constraint:** re-issue an E1 manifest per fixed card (as identity did), or
record a superseding note in each manifest. A claim may not rest on a manifest whose own
pinned hashes fail.

### `F-A3R2-04` — LOW — the amendment names a downstream dependency that does not exist

`amendments[0].downstream_vi` says `shared/rr_contracts` "phải sinh lại", and
`change-control.md` §10 lists `shared/rr_contracts` under `affected.generated` as
"PHẢI sinh lại (chủ: WS)". But `entities.yaml` is not a generator input: it appears **0
times** in `GENERATED_FROM.json`, whose sources are the seven `contracts/schemas/*.json`
plus the state and registry files. Regenerating is therefore a guaranteed no-op — which is
what P0-FIX2/FIX3 found and recorded. Harmless in effect, but two contract-level documents
now assert a dependency the generator manifest denies, and a future reader could conclude
the generated tree tracks `entities.yaml` when it does not.

**New finding counts: MEDIUM 3 · LOW 1 · HIGH 0.** All open at `OPEN`; I close none and
supply no patch bytes. Everything else I looked at in the fix diff was clean.

## 5. Verdicts

### 5.1 Per card

| Card | Verdict | May `IMPLEMENTATION_VERIFIED` stand? |
| --- | --- | --- |
| `TC-ingest-idempotent-ack-lost` | **PASS** | **YES, scoped** — four produced operations only, carrying the declared §4 `PARTIAL` (five consumed operations not called, `works_linked` always 0) and `CR-TC-ingest-05`. `F-A3R1-05`/`-09`/`-10`/`-13` all verified; the `post → ingest_receipt` FK now exists. Subject to `F-A3R2-03` (manifest currency). |
| `TC-canonical-identity-merge` | **PASS** | **YES, scoped** — with the two strict `xfail`s (`CR-TC-IDENTITY-02/03`). `F-A3R1-04` verified; it is also the only card that re-issued its evidence manifest. |
| `TC-owner-auth-session` | **PASS** (was FAIL) | **YES, scoped** — the two HIGH findings that failed it are both verified fixed: the `owner` schema is now traversal-order-independent (four orders, one signature) and every shipped column is contract-declared. Lockout is durable, proved by my own restart harness; bearer tokens are hashed and compared constant-time; the 36-edge sweep is exhaustively partitioned. The label rests on `AMD-ENT-owner-01`, which is **PROVISIONAL** — if the Owner objects, this card's schema and this verdict both reopen. Subject to `F-A3R2-03`. |
| `TC-storage-write-blocked-readiness` | **PASS** | **YES, narrowed** — must still exclude `write_blocked → healthy` recovery (`F-A3R1-11` PARTIAL, no probe table). `F-A3R1-07`/`-11` wiring verified. `F-A3R2-03` applies most sharply here: its manifest is stale by hash on four files and should be re-issued before the label is recorded. |

### 5.2 Skeleton

**PASS.** `F-A3R1-15` fixed and `README.md` is now self-consistent on `uv sync
--all-packages`; `faults.py` adopted with a hash rather than retro-fitted into a card;
delimiters normalised; CI, lockfiles, `.gitignore` and both generated-code gates unchanged
and still green.

### 5.3 Overall

**PASS** for the review scope. The two HIGH findings from `A3-R1` are closed by evidence I
re-derived myself rather than by assertion, 13 of 15 findings verify outright, one is
correctly partial and one is deferred by the packet. The remediation was done the right way
round: the contract was amended through change control with an explicit "the Owner may
object" and a `PROVISIONAL` status, instead of the code being quietly blessed. The four new
findings are all in the *proof* of the fixes — a dangling rule citation, a guard test that is
weaker than the property it guards, evidence manifests that were not re-issued, and a
misdescribed generator dependency — not in the fixed behaviour itself. None of them blocks;
all should be closed before the ceiling is recorded.

## 6. Residual

* `F-A3R1-03` — evidence-run registration in `evidence/index.json`. **DEFERRED** to PC09.
* `F-A3R1-11` recovery half — no probe table (`CR-TC-storage-04`); `write_blocked → healthy`
  remains not established at runtime.
* `F-A3R2-01…04` — open, as above.
* `AMD-ENT-owner-01` is `PROVISIONAL`. The Owner has not spoken. Four shipped columns, one
  migration and this round's auth verdict all depend on the Owner not objecting.
* `CR-TC-ingest-05` (`counts.quarantined` in the wire schema vs no column on
  `ENT-ingest-receipt`), `CR-TC-AUTH-01` (fixture `recovery/h` seq4) and
  `CR-TC-IDENTITY-02/03` remain open contract/fixture items, unchanged this round.
* Concurrency is still argued from structure, not from a multi-process race test. "Two
  concurrent submissions of one idempotency key" remains **not established**.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product
  acceptance, not a security assessment, no live calls.

## 7. Post-review snapshot event (disclosed, not concealed)

After my end-of-review recompute passed (386/386, `git status` 63), a **387th** file appeared
in the candidate tree while I was writing this report:
`evidence/audits/A3-R1-report.md`, sha256 `02c9d541dfd1d8dbb7f56391a4fc5e1de9e7a81d310ce4ff08604717763ab498`,
32 850 B, mtime 2026-09-07 18:35:35 +07.

* **I did not write it.** I made no repository write in either round. The file is a
  byte-identical copy of my own `…/scratchpad/audits/A3-R1-report.md` (same sha256), placed
  under `evidence/audits/` by another actor — the same packaging pattern as `PC00-FIX9`,
  which persisted 41 audit artefacts there. Persisting an audit report needs a Worker with
  the right packet; an Auditor may not do it, and did not.
* **Scope of the change:** I re-hashed all 386 manifested entries afterwards. **Every one is
  byte-identical**; the delta is exactly one addition and zero modifications. No artefact
  this report reasons about moved.
* **Consequence:** the verdicts above stand for the 386 bytes reviewed. `FC-P1` epoch 2 as
  frozen is, strictly, no longer the tree on disk, so if the Coordinator intends to commit
  or re-freeze, the manifest should be re-cut at 387 entries with a new `manifest_sha256`
  rather than reusing `4ddb275f…`. I am not declaring `STALE`, because the writer-quiescence
  breach touches no reviewed artefact and the added file is an audit record, not a candidate
  input — but the call to re-freeze is the Coordinator's, and it should be recorded either
  way rather than absorbed silently.
