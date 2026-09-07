# AUDIT_REPORT `A3-R1` — independent review of Phase 0 + Phase 1, frozen candidate `FC-P1`

## 0. Identity, authority, independence

| Field | Value |
| --- | --- |
| packet | `PKT-A3-R1` · authority `AUTH-COORD-A3-R1` (parent `AUTH-OWNER-20260907-03`) |
| reviewer | `auditor-A3`, fresh principal |
| independence | **DECLARED CLEAN.** I authored and co-authored nothing in `/mnt/virtual/repo/xcrawl`; I hold no write lease; I made no repository write of any kind. All helpers live under `…/scratchpad/a3/` with `PYTHONDONTWRITEBYTECODE=1`. |
| frozen candidate | `FC-P1`, 382 entries, `manifest_sha256 = fec3ced230b76f39b3d0e04cf7b7b0f4bbd86fbbb82188f445c7cf01d8aaf91e` |
| pre-phase commit | `da886f8553b50426d601bfaa8fdad8c4757766dc` (= `HEAD`; the whole candidate is uncommitted working tree) |
| completion ceiling | `SELF_VALIDATION` is what the Workers produced; this report is the first **independent** record. It does not confer product acceptance. |

### 0.1 Snapshot quiescence

Recomputed at start **and** at end of the review. Both times the 382 `path|sha256|bytes`
triples are byte-identical to the manifest, and the SHA-256 over the manifest's entry lines
reproduces `fec3ced2…` exactly. `git status --porcelain` had 59 entries before my first
command and 59 after my last; **no new untracked path appeared outside `.gitignore`**, and
`uv sync`, `pytest`, `npm ci`, `npm test` and the two evidence tools wrote only into
`.venv/`, `web/node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/` — all
git-ignored. Snapshot is **not** `STALE`.

> One operational note for the Coordinator: the packet's method step 1 says `uv sync`.
> Plain `uv sync` **prunes** the workspace members from `.venv` (it removed `fastapi`,
> `sqlalchemy`, `alembic`, `argon2-cffi`, `rr-contracts`, …) and the suite then dies with
> `ModuleNotFoundError: rr_contracts` and 11 collection errors. The repo's own commands
> (`Makefile: setup`, `.github/workflows/python.yml`) use `uv sync --all-packages`. Every
> result below is from `uv sync --all-packages --frozen`. See `F-A3R1-15`.

## 1. Evidence reproduction

Everything the four handoffs and `P0-skeleton-handoff.md` §A.3 claim was re-run by me from
the frozen bytes. Check-for-check:

| Gate | Command I ran | Their claim | My observation | Verdict |
| --- | --- | --- | --- | --- |
| Install | `uv sync --all-packages --frozen` | resolves from `uv.lock` | exit 0, no re-resolution | REPRODUCED |
| Full Python suite | `uv run --frozen pytest` | 263 passed / 4 xfailed / 0 failed | **263 passed, 4 xfailed, 0 failed** (35.1 s), exit 0 | REPRODUCED |
| ruff lint | `uv run --frozen ruff check .` | `All checks passed!` | identical, exit 0 | REPRODUCED |
| ruff format | `uv run --frozen ruff format --check .` | 58 files formatted | `58 files already formatted`, exit 0 | REPRODUCED |
| mypy `--strict` | `uv run --frozen mypy` | no issues, 24 files | `Success: no issues found in 24 source files`, exit 0 | REPRODUCED |
| generated models | `uv run --frozen python shared/rr_contracts/generate.py --check` | matches contracts | `generated tree matches a fresh run of the generator`, exit 0 | REPRODUCED |
| OpenAPI 3.1 | `uv run --frozen openapi-spec-validator contracts/http/openapi.yaml` | `OK` | `contracts/http/openapi.yaml: OK`, exit 0 | REPRODUCED |
| card pins | `uv run --frozen python evidence/tools/verify_cards.py --repo .` | 13/13, 3 211 assertions, 0 violations | **13 PASS / 0 FAIL, 3 211 assertions, 0 violations**, epoch `PC10-PIN-P1b-20260907` | REPRODUCED |
| card-verifier self-test | `verify_cards.py --self-test --self-test-dir <scratch>` | (CI step) | **14/14 mutations caught**, exit 0 | REPRODUCED |
| E0 | `uv run --frozen python evidence/tools/e0_check.py --repo .` | 24/24 PASS | **24 checks — PASS 24 · FAIL 0 · violations 0**, exit 0 | REPRODUCED |
| web install | `cd web && npm ci` | from lockfile | 298 packages, 0 vulnerabilities, exit 0 | REPRODUCED |
| vitest | `npm test` | 11 passed / 2 files | **11 passed (2 files)**, exit 0 | REPRODUCED |
| eslint+prettier | `npm run lint` | clean | clean, exit 0 | REPRODUCED |
| tsc | `npm run typecheck` | clean | clean, exit 0 | REPRODUCED |
| web codegen | `node scripts/generate.mjs --check` | matches | `generated client matches a fresh run of the generator`, exit 0 | REPRODUCED |
| alembic single head | `cd server && alembic heads` | one head | `0004_merge_phase1_heads (head)` — **one head** | REPRODUCED |

Per-file counts named in card §8 (all exit 0):

| File | Their count | Mine |
| --- | --- | --- |
| `tests/contract/test_ingest_batch_schema.py` | 14 | 14 |
| `tests/contract/test_ingest_idempotency.py` | 12 | 12 |
| `tests/integration/test_ingest_ack_lost.py` | 15 | 15 |
| `tests/contract/test_identity_normalization.py` | 75 | 75 |
| `tests/integration/test_identity_merge_audit.py` | 39 + 2 xfail | 39 + 2 xfail |
| `tests/contract/test_auth_scheme_matrix.py` | 17 | 17 |
| `tests/integration/test_denied_edges.py` | 26 + 2 xfail | 26 + 2 xfail |
| `tests/integration/test_disk_full_no_ack.py` | 17 | 17 |
| `tests/integration/test_readiness_independent_channel.py` | 29 | 29 |
| `server/tests/test_smoke.py` | 8 | 8 |

**No test is skipped anywhere.** The four `xfail`s are all `strict=True` and each records a
declared contract/fixture drift or a dependency on a card outside M1
(`CR-TC-AUTH-01`, pending `TC-storage-…`, `CR-TC-IDENTITY-02`, `CR-TC-IDENTITY-03`). None
of them silences a P0 scenario the card was required to prove: each xfailed literal has a
companion **passing** assertion for the part that is not in dispute (e.g. `recovery/h` seq4
`http_status: 403` + `rows_changed: 0` pass; only the `FORBIDDEN_EDGE` vs `CSRF_REJECTED`
literal is xfailed). I accept the four as legitimate.

Evidence manifests: all four `evidence/runs/TC-*-E1-*.json` validate against
`evidence/manifest.schema.json` with **0 schema errors**; all four carry
`review_type: SELF_VALIDATION`; all four carry the correct
`spec_sha256 = d35e1f2d…`; all four list honest `not_established_vi`. See `F-A3R1-03` for
the one manifest obligation that is unmet.

## 2. Independent re-derivation (not their tests)

I did not take the suite's word for the load-bearing invariants. Two harnesses of my own,
`…/scratchpad/a3/schema_check.py` and `…/scratchpad/a3/indep_ingest.py`:

**(a) Schema vs `contracts/data/entities.yaml`.** I built a database with `alembic upgrade
head` and compared every table against the entity contract, using `PRAGMA table_xinfo` so
that STORED generated columns are seen.

* 16 business tables created. Column sets match `entities.yaml` **exactly**, with one
  exception: `owner` carries `password_hash` and `password_updated_at`, which `ENT-owner`
  does not declare (`F-A3R1-02`).
* Every `keys.unique` entry in `entities.yaml` exists on disk, including the partial ones
  (`ux_work_owner_canonical_doi … WHERE canonical_doi IS NOT NULL AND identity_state <>
  'merged'`, `ux_saved_active_owner_target … WHERE state = 'active'`,
  `ux_analysis_valid_key … WHERE status = 'valid'`, `ux_work_version_current … WHERE
  is_current = 1`).
* Nullability matches the contract for every column except the three `target_key` columns,
  which are STORED generated and therefore not declared `NOT NULL`; the paired
  `exactly_one_check` CHECK makes them non-null in practice (`F-A3R1-14` class, noted, not
  a defect).
* `owner_id` is present on every table except `owner` itself, which is correct.

**(b) Ingest invariants, driven through the service layer with the pinned fixture.**

| Assertion | Result |
| --- | --- |
| replay (same key + same `payload_hash`) changes no row count | **TRUE** — `{post:1, ingest_receipt:1, checkpoint:1}` before and after |
| replay returns the same `receipt_hash` | **TRUE** |
| same key + different payload raises | **TRUE**, `IDEMPOTENCY_CONFLICT` |
| the conflict wrote nothing | **TRUE** — counts unchanged |
| I02 `checkpoint.acked_through_ingest_sequence ≤ max(post.ingest_sequence)` | **TRUE** |

I also read the transaction boundaries rather than trusting the docstrings.
`submit_batch` opens exactly one `with ctx.engine.begin()` and builds its response **after**
the block exits, so no ACK can precede COMMIT; the replay branch returns before any write
transaction opens; `commit_checkpoint` is likewise a single block. `identity` uses one
`_transaction()` helper that either opens a transaction or *joins* the caller's, which is
how a merge invoked from ingest stays inside `TXN-ingest-batch` — a correct and deliberate
construction. Failure mapping is right: `OperationalError | IntegrityError | sqlite3.Error`
→ rollback → `STORAGE_WRITE_FAILED` with no SQL text in the envelope.

**(c) Secret and code hygiene.** No error code anywhere in `server/app/` is a string
literal — every one comes from `rr_contracts.generated.errors.ErrorCode`, and `scope` /
`retry_class` are read from the generated `SCOPE` / `RETRY_CLASS` registries rather than
chosen by a handler. There is no `logging`, no `print`, and no credential-shaped literal in
the whole Python tree (the only hits are `AuthScope` enum *member names* from the OpenAPI
security schemes). Argon2id is exactly `contracts/ops/secrets.md` §2.2: `memory_cost
64 MiB`, `time_cost 3`, `parallelism 1`. Session cookie is `HttpOnly + Secure +
SameSite=Lax`; `rr_csrf` is deliberately non-HttpOnly; CSRF is 128-bit and compared with
`hmac.compare_digest`; session tokens are stored and looked up only as `sha256:<hex>`;
a dummy Argon2 hash keeps the unknown-account path timing-equal.

## 3. Findings

Every finding opens at `OPEN`. I close nothing and I supply no patch bytes.

### `F-A3R1-01` — HIGH — the shipped `owner` schema depends on which Alembic branch runs first

* **Where:** `server/migrations/versions/0002_base_entities.py:61-69` and
  `server/migrations/versions/0002_tc_owner_auth_session.py:54-72`.
* **Condition:** two different revisions on two parallel branches off `0001` each issue
  `CREATE TABLE IF NOT EXISTS owner` with **different constraint sets**. Whichever branch
  Alembic traverses first wins; the other statement is a no-op.
* **Expected:** one definition of one table, so `alembic upgrade head` is a function of the
  chain, not of traversal order.
* **Observed (reproduced):** default `upgrade head` runs the auth branch first and yields
  `CONSTRAINT ck_owner_display_name_length CHECK (length(display_name) BETWEEN 1 AND 120)`
  plus a table-level `UNIQUE (singleton_guard)`. Forcing the other order
  (`upgrade 0002_base_entities` then `upgrade head`) yields
  `CREATE TABLE owner (… created_at TEXT NOT NULL, password_hash TEXT, password_updated_at
  TEXT)` — **the display-name CHECK is gone**. `entities.yaml` `ENT-owner.display_name`
  requires `1..120 ký tự`, so one of the two reachable schemas violates the entity contract.
* **Impact:** a contract-mandated constraint is present or absent depending on migration
  order; a fresh deployment and a developer machine can disagree; no test asserts the
  constraint either way, so the divergence is silent.
* **Remediation constraint:** one owner per table. The fix must make a single revision the
  sole `CREATE TABLE owner`, and must be proved by a test that asserts the *constraint set*
  (not just the column set) after `upgrade head`, run from both branch orders. Do not
  resolve it by deleting the CHECK — `entities.yaml` requires it.

### `F-A3R1-02` — HIGH — credential columns shipped for an entity the contract does not declare

* **Where:** `server/migrations/versions/0002_tc_owner_auth_session.py:66-67, 74-78`;
  `contracts/data/entities.yaml` `ENT-owner`.
* **Condition:** `ENT-owner` declares exactly five fields (`id`, `singleton_guard`,
  `display_name`, `timezone_iana`, `created_at`). The auth card ships
  `owner.password_hash` and `owner.password_updated_at`, and `auth.login` depends on them.
* **Expected:** card §10 `SG-CONTRACT` ("thiếu hợp đồng … ⇒ DỪNG và raise CR") and `SG-EDGE`
  ("cần một … bảng, secret … không có trong §5 ⇒ DỪNG"). The absence of any credential
  field on the only entity that could hold one is a missing contract, not an implementation
  detail.
* **Observed:** the Worker raised `CR-TC-AUTH-02` — correctly — and then **proceeded**
  rather than stopping. My schema diff confirms these are the only two columns on the whole
  database that no entity declares.
* **Impact:** `entities.yaml` is no longer the authority for the shipped schema; the
  ratified data scope (`CONTRACT_READY`) now under-describes the database. Any later card
  or E0 check that treats `entities.yaml` as complete will be wrong about `owner`.
* **Remediation constraint:** the columns must be added to `ENT-owner` through change
  control with the Owner's ratification, *or* removed and the credential moved to an entity
  the contract does define. Proof required: an E0-style check that every shipped column
  resolves to an `entities.yaml` field — the check I wrote ad hoc should become permanent.
  A remediation that only edits the handoff is not sufficient.

### `F-A3R1-03` — MEDIUM — no Phase 1 evidence run is registered in `evidence/index.json`

* **Where:** `evidence/index.json`; each card §13 ("Đăng ký run vào `evidence/index.json`").
* **Observed:** `grep` for each of the four run ids returns **0** hits;
  `evidence/index.json` is byte-identical to `da886f8`.
* **Impact:** the four E1 runs exist as files but are not discoverable through the evidence
  index, so the index no longer enumerates the project's evidence. §13 is unmet for all
  four cards simultaneously.
* **Note on responsibility:** `evidence/index.json` is a PC09-owned file and is in no
  card's §3 write set, so the Workers were caught between §13 and their write set. The
  remediation is a Coordinator-level packet, not a re-run of the cards.

### `F-A3R1-04` — MEDIUM — the identity card created five tables owned by other modules

* **Where:** `server/migrations/versions/0003_tc_canonical_identity_merge.py:194-335`.
* **Observed:** `saved_snapshot`, `analysis`, `saved_item`, `work_label` and
  `first_announced_ledger` are created here; `entities.yaml` gives their `owner_module` as
  `MOD-saved-service`, `MOD-analysis-service` and `MOD-report-service`.
* **Assessment:** the *reason* is sound and is declared (`CR-TC-IDENTITY-04`):
  `TXN-identity-merge` is a closed move-set and cannot be proved without the tables it
  moves rows in. The schema produced is faithful — I verified all five against
  `entities.yaml` column-for-column, including the STORED `target_key` generated column and
  the partial unique indexes.
* **Impact:** three future cards inherit a schema they did not author and cannot change
  without a rebuild; the ownership column in `entities.yaml` and the migration authorship no
  longer agree.
* **Remediation constraint:** a recorded Coordinator ruling assigning ownership of these
  five DDL blocks, so the owning cards are dispatched knowing their tables already exist.

### `F-A3R1-05` — MEDIUM — owner scoping and the receipt link are not enforced by the database

* **Where:** `0002_base_entities.py:121-150` (`post.ingest_receipt_id`);
  `0003_tc_ingest_idempotent_ack_lost.py` (`checkpoint.owner_id`, `ingest_receipt.owner_id`).
* **Observed (`PRAGMA foreign_key_list`):** every other table carries
  `REFERENCES owner (id)`; `checkpoint` and `ingest_receipt` carry **none**.
  `post.ingest_receipt_id` is `NOT NULL` with no `REFERENCES ingest_receipt (id)`.
* **Assessment:** the `post` case is declared (`CR-TC-ingest-01`) and its stated reason —
  SQLite cannot add a FK without a twelve-step rebuild of another card's table — is
  correct. The two `owner_id` columns are **not** explained: `owner` exists on both parent
  branches of that revision, so the constraint could have been declared at CREATE time.
* **Impact:** `owner_id` is a value convention rather than a database guarantee on the two
  ingest tables; a wrong `owner_id` is accepted. `REQ-S7.3-01` (owner scoping) is not
  machine-enforced there.
* **Remediation constraint:** either declare the FKs in a coordinated rebuild revision, or
  record an `ACCEPTED_RISK` with authority and expiry — not a comment.

### `F-A3R1-06` — MEDIUM — login lockout is process-local and does not survive a restart

* **Where:** `server/app/auth/service.py:270-309` (`LoginThrottle`), instantiated once per
  `AuthService` at line 336 and held on `app.state`.
* **Observed:** the failure deque and `_locked_until_ms` live only in memory.
  `contracts/ops/secrets.md` §2.3 fixes `login_fail_threshold` 5 / 15 min and
  `lockout_duration` 15 min; `entities.yaml` declares no entity for login attempts.
* **Assessment:** the Worker's reasoning is right (`SG-EDGE` forbids inventing a table) and
  is declared as `CR-TC-AUTH-03`. But the consequence is a security control that a process
  restart clears, and the tests exercise the in-memory object only.
* **Impact:** the rate limit `secrets.md` specifies is not durably enforced; an attacker who
  can cause or await a restart faces no lockout.
* **Remediation constraint:** `entities.yaml` needs a login-attempt entity (change control),
  after which the counter must be proved to survive a restart in a test that actually
  rebuilds the app object.

### `F-A3R1-07` — MEDIUM — `server/app/db/faults.py` is outside every §3 write set

* **Where:** `server/app/db/faults.py` (116 lines), claimed by
  `TC-storage-write-blocked-readiness-handoff.md`.
* **Condition:** the storage card §3 write set is five paths
  (`storage/health.py`, `storage/guard.py`, `health/router.py`, two tests). `db/faults.py`
  is in none of them, and it is not in `P0-skeleton-handoff.md` §2 either — the P0 skeleton
  shipped only `db/engine.py` and `db/__init__.py`.
* **Mitigating:** the Phase 1 dispatch note §4 speaks of "SQLite failure injection via the
  wrapper in `server/app/db/`" as though it already existed. The Worker built what the
  dispatch assumed. This is a dispatch defect as much as a Worker one.
* **Impact:** the write-set discipline that makes parallel cards safe was broken without an
  amendment; `server/app/db/` now has a file no packet authorised.
* **Remediation constraint:** a Coordinator amendment naming the file and its owner. Do not
  fix by silently adding it to the card §3 after the fact — that is editing the oracle.

### `F-A3R1-08` — MEDIUM — `SG-DENY` is demonstrated for a minority of the 36 forbidden edges

* **Where:** `tests/integration/test_denied_edges.py:467-503`;
  `tests/integration/test_readiness_independent_channel.py:265-270`.
* **Observed:** the sweep fixture holds 36 events — 11 expect `UNAUTHORIZED`, 8
  `FORBIDDEN_EDGE`, 15 `CAPABILITY_DENIED`, plus `UNAUTHORIZED_COMMAND` and
  `RESTORE_UNVERIFIED` rows. The auth test asserts only rows whose port is HTTP **and**
  whose expected code is `UNAUTHORIZED`, and it closes with `assert checked >= 5`. The
  storage card asserts exactly five edges into `MOD-data-store` (`FE-01/05/15/18/29`). The
  remaining rows are handled by `test_sc49_non_http_edges_are_declared_out_of_this_layer`,
  which asserts only that each such row *names* an enforcement mechanism — it never asserts
  that any caller is actually refused.
* **Also:** the auth card §8 oracle for `recovery/i` is "`save.create` bằng `collectorToken`
  ⇒ 401, `COUNT(saved_item)` không đổi". The row count is never measured — no `save.*` route
  exists yet — and the test calls the pure function `classify_denial` rather than the HTTP
  stack. `FORBIDDEN_EDGE` *is* genuinely raised in process by
  `server/app/identity/service.py:274` (`_require_edge`) and by the storage guard, so the
  code is not dead; it is the sweep coverage that is thin.
* **Impact:** `SG-DENY` says choosing the wrong code is a FAIL in its own right. A
  `>= 5`-of-36 assertion cannot detect a wrong code on the other 31 rows.
* **Remediation constraint:** the sweep needs an exhaustive, per-edge assertion with an
  explicit, enumerated exclusion list — each excluded edge naming the card that will prove
  it — rather than a floor of five.
* **Fairness:** no forbidden edge in `contracts/modules.yaml` names `MOD-ingest-service` or
  `MOD-identity-service` as caller or callee, so `SG-DENY` is vacuous for those two cards; I
  verified this rather than assuming it.

### `F-A3R1-09` — LOW — two mandatory read-set fixtures are neither exercised nor recorded `NOT_RUN`

* `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json` — named in
  `TC-ingest-idempotent-ack-lost` §2, referenced by no test, and the string "e2e" does not
  occur in that card's handoff.
* `acceptance/fixtures/recovery/g-ssrf-redirect-private.json` — named in
  `TC-owner-auth-session` §2, same situation.
* Dispatch rule 4: "anything not run is `NOT_RUN`". Both are plausibly out of M1 reach; the
  defect is the silence, not the omission.

### `F-A3R1-10` — LOW — `server/app/ingest/` has no `__init__.py`

Every other `server/app/*` subpackage (`auth`, `db`, `health`, `identity`, `storage`) has
one, several with real content. `ingest` has none. It works today only because the tree is
an implicit namespace package on `pythonpath = ["."]` and `rr-server` is
`package = false`, so nothing is built into a wheel. It is an inconsistency that will bite
the first time `server` becomes a real distribution.

### `F-A3R1-11` — LOW — the storage recovery path and the ingest write gate are unwired on the shipped factory

* `contracts/state/storage.yaml` `T-ST-02` defines the recovery probe as "một write NHỎ vào
  bảng probe riêng"; no such entity exists, so `StorageGuard.record_probe()` is an injection
  point only (declared as `CR-TC-storage-04`, and `SG-EDGE` was correctly honoured). The
  consequence is that on a real deployment `write_blocked → healthy` can never fire on its
  own.
* `server/app/main.py:121` builds `app.state.storage_guard`, but nothing wires it into
  `app.state.ingest_context`; `IngestContext.storage_guard` defaults to `None` and
  `_assert_writable` then does not run. The service docstring is honest about this ("when no
  guard is injected the gate simply does not run"), and a real write failure still surfaces
  as `STORAGE_WRITE_FAILED` from the handler — but the *pre-*check is inert on
  `create_app()` as shipped.
* Both belong in the "not established" list of any claim that mentions `write_blocked`
  end to end.

### `F-A3R1-12` — LOW — bearer tokens are matched by plaintext dict lookup

`server/app/auth/middleware.py:163-177` — `TokenRegistry.kind_for` is
`self._tokens.get(token)`: the three bearer credentials are held in clear in process memory
and compared non-constant-time, while session tokens are correctly reduced to
`sha256:<hex>` and CSRF uses `hmac.compare_digest`. Low severity for a single-owner LAN
deployment; inconsistent with how the same file treats the other two credentials.

### `F-A3R1-13` — LOW — one include is not inside its own delimiters

`server/app/main.py:36` — `from server.app.auth.router import install_auth` sits at module
top level while its `# --- BEGIN include: TC-owner-auth-session ---` block (lines 87-99)
contains only the call. The other three cards import inside the factory, within their
delimiters. Dispatch rule 2 asks for "one clearly delimited include line".

### `F-A3R1-14` — LOW — `owner.created_at` carries no timestamp CHECK

`entities.yaml` types it `timestamp_utc_ms`, and `checkpoint.created_at` /
`ingest_receipt.committed_at` enforce that with a `GLOB` CHECK. Neither `owner` definition
does. Same class: the three generated `target_key` columns are `nullable: False` in the
contract but not declared `NOT NULL` (the `exactly_one` CHECK covers it in practice).

### `F-A3R1-15` — LOW — `README.md` prints the `uv sync` form that does not work

`README.md:102` describes the `python` CI job as running `uv sync --frozen`. The workflow
(`.github/workflows/python.yml:31`) and `Makefile: setup` both use `--all-packages`. Running
the README's form prunes the workspace members and produces 11 collection errors. `README.md`
line 22 has the correct form, so the file contradicts itself.

### Not findings — checked and clear

* **Regression (§5).** `git diff da886f8` over `contracts/` and `acceptance/` is **empty**.
  `agent-tasks/` changed only in §0 (pin epoch `PC10-PIN-OD01e` → `PC10-PIN-P1b`, three
  hash rows, and a `dispatch_status:` line whose own template text forbids it from altering
  §1–§13); `precode/` and `agent_profile/` changes are the `PKT-PC00-FIX17` / ratification
  records. No card obligation text moved. `verify_cards.py` `epoch` check passes 22/22.
* **`server/tests/test_smoke.py` was modified after all four card handoffs** — every card
  correctly refused to touch it and reported it as a failing P0 tripwire. I initially read
  this as an unattributed write; it is **not**. `P0-skeleton-handoff.md` §A.1–A.4 records
  the packet that inverted `test_readiness_is_not_routed_in_phase_0` into
  `test_readiness_is_routed_and_denies_an_unauthenticated_caller`, with before/after
  sha256. The two other post-P0 changes (`evidence/tools/verify_cards.py` 9→13 checks,
  `.github/workflows/e0.yml`) are recorded in `PC10-handoff.md` lines 2444 and 2603. The
  hash table in `P0-skeleton-handoff.md` §2 is stale for those two files, which is worth a
  Coordinator note but is not drift in the artefacts themselves.
* **Alembic.** One head, confirmed by running it. `0003_tc_ingest_idempotent_ack_lost`
  merges the identity and auth branches; `0004_merge_phase1_heads` is a no-op merge point
  naming all three. Listing an ancestor alongside its descendants in `0004.down_revision`
  is redundant but harmless — `alembic history` renders the graph correctly and
  `upgrade head` runs all six revisions.
* **`counts.quarantined` (`CR-TC-ingest-05`).** Real and correctly raised:
  `ingest-receipt.schema.json` requires `counts.quarantined` and the arithmetic
  `received = inserted + deduplicated + quarantined + rejected`, while `ENT-ingest-receipt`
  has no quarantine column and its CHECK is
  `posts_inserted + posts_duplicate + items_rejected = items_received`. The implementation
  emits `quarantined: 0` at four sites, which is honest while identity quarantine is a
  declared non-goal. This is a **contract** defect for change control, not a code defect.
* **`identity.record_alias` never called from ingest.** Confirmed; `counts.works_linked` is
  always 0 and a new post is stored `identity_resolution = 'pending'`. Declared as
  **PARTIAL** at `TC-ingest-idempotent-ack-lost-handoff.md:186` with the reasoning. Honest,
  and it bounds the claim rather than breaking it.
* **`discovered_at`** is server-assigned (`service.py:755`, clamped against
  `MAX(post.discovered_at)`), never taken from the worker's clock. ADR-0007 held.
* **Merge cap.** `IDENTITY_MERGE_MAX_MOVED_ROWS = 100_000` matches
  `entities.yaml limits.identity_merge_max_moved_rows`, and exceeding it converts to a
  conflict with nothing written (`service.py:1006`).
* **Skeleton §4.** Layout matches the cards' §3. Four CI workflows exist and cover the four
  jobs plus the OpenAPI validator; the `e0` job additionally runs `verify_cards.py`, its
  self-test, and a `git diff --exit-code && test -z "$(git status --porcelain)"` step that
  proves the tools wrote nothing. `.gitignore` covers `.venv/`, `node_modules/`, `*.db`
  (+ `-wal`/`-shm`), `.env*`, `var/`, the Chrome profile and every tool cache. Both
  lockfiles (`uv.lock`, `web/package-lock.json`) are present and both installs are
  `--frozen`/`ci`. No secret anywhere.
* **Generated-code rule.** Both `--check` generators reproduce their trees byte-for-byte;
  `ruff` excludes the generated tree from style, `mypy` from strict — deliberate and
  documented. No hand edit is possible without the gate catching it.

## 4. Verdicts

### 4.1 Per card

| Card | Verdict | May `IMPLEMENTATION_VERIFIED` stand? |
| --- | --- | --- |
| `TC-ingest-idempotent-ack-lost` | **PASS** | **YES, scoped.** All seven §3 paths exist and nothing outside §3 + its migration + handoff + manifest was written. Every §8 test exists and passes; I re-derived I02, replay identity and `IDEMPOTENCY_CONFLICT` independently. The label must be recorded as covering the four **produced** operations only, and must carry the §4 `PARTIAL` (five consumed operations not called, `works_linked` always 0), `CR-TC-ingest-01` (no FK from `post`) and `F-A3R1-05`. The Worker did not self-award the label — correct. |
| `TC-canonical-identity-merge` | **PASS** | **YES, scoped.** §3 complete, `TXN-identity-merge` is one commit, `_require_edge` genuinely raises `FORBIDDEN_EDGE`, the 100 000-row cap is enforced, and the five foreign tables match `entities.yaml` exactly. Must be recorded with the two strict `xfail`s (`CR-TC-IDENTITY-02/03`) and with `F-A3R1-04` attached. |
| `TC-owner-auth-session` | **FAIL** | **NO — not yet.** Not for the crypto or the session logic, which are the strongest work in the candidate (Argon2id per `secrets.md`, correct cookie flags, `compare_digest` CSRF, hashed session tokens, timing-equal unknown account). It fails on §10: `SG-CONTRACT`/`SG-EDGE` required a **stop** when no entity could hold a credential, and the card shipped two undeclared columns instead (`F-A3R1-02`), and its migration is one of the two divergent `owner` definitions (`F-A3R1-01`). Both are contract-authority breaches, and both are inside this card's own migration. The label may be reconsidered once `ENT-owner` is amended through change control and the `owner` DDL has a single owner. |
| `TC-storage-write-blocked-readiness` | **PASS** | **YES, narrowed.** The state machine, the guard and the DB-independent health channel are real and well tested (46 tests, HC-01..HC-04). The label must exclude the `write_blocked → healthy` recovery transition (no probe table exists, `F-A3R1-11`) and must note `F-A3R1-07` (`db/faults.py` outside §3). |

### 4.2 Skeleton

**PASS with findings.** Layout, CI, lockfiles, `.gitignore`, generated-code gates and the
card verifier (13 checks, self-test 14/14) are all sound and genuinely adversarial —
`verify_cards.py` proving each of its own checks still bites is better practice than the
packet asked for. Findings against it: `F-A3R1-15` (README's `uv sync` form), the stale
hash rows for `verify_cards.py` and `.github/workflows/e0.yml` in `P0-skeleton-handoff.md`
§2, and `F-A3R1-07`/`F-A3R1-13` which are as much dispatch defects as Worker ones.

### 4.3 Overall

**FAIL** for the review scope — on two evidenced HIGH violations, `F-A3R1-01` and
`F-A3R1-02`, both localised in `0002_tc_owner_auth_session.py` and both about the same
thing: the database schema stopped being a function of `contracts/data/entities.yaml`.
Everything else in the candidate is of a quality I want to state plainly, because a bare
`FAIL` would misrepresent it: 263/263 reproduced green, `mypy --strict` clean, both
generators byte-reproducible, 24/24 E0, 13/13 card checks with a passing mutation self-test,
zero string-literal error codes, zero secrets, honest `PARTIAL`s and honest `xfail(strict)`
drift records, and four evidence manifests that refuse to claim a label their review type
cannot support. The failure is narrow and it is fixable without touching the working code.

## 5. Limitations

* This is a review of `FC-P1` at `manifest_sha256 fec3ced2…`. It is not product acceptance
  and it is not a security assessment: I read the auth code and checked it against
  `secrets.md`, but I ran no attack, no fuzzing and no dependency-vulnerability scan beyond
  what `npm ci` reports.
* I ran no live call — no X, no Telegram, no AI provider, no browser. E3/E4 remain
  `NOT_RUN` by protocol.
* I did not audit `contracts/`, `acceptance/` or `precode/` on their merits; I verified only
  that they are unchanged since `da886f8`. The pre-code audit chain `A1-R1…A2-R6` covers
  those and I did not re-open it.
* Concurrency is argued from code structure (single `engine.begin()` blocks, the
  `UNIQUE(owner_id, idempotency_key)` index, the in-transaction re-read) and from
  single-threaded fixtures. I ran no multi-process race test; "two concurrent submissions of
  one key" is **not established** by this review.
* `F-A3R1-01` is proved by forcing the branch order by hand. I did not establish whether
  Alembic's default traversal is stable across versions and filesystems — which is precisely
  why the divergence should not exist.
* Completion ceiling of this report: an independent `AUDIT_REPORT` over the scope above.
  Findings open at `OPEN`; I close none, and I supplied no candidate bytes.
