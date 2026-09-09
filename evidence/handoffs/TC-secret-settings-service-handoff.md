---
contract_id: CT-handoff-TC-secret-settings-service
version: 1.0.0
status: draft
document_type: HANDOFF
card_ref: agent-tasks/TC-secret-settings-service.md
packet_id: PKT-PC10-FIX28 (implementer half) + PKT-TC-SECRET-FIX1 (real cipher)
worker: worker-WAI
authority: "AUTH-COORD-TC-SECRET (cha AUTH-OWNER-20260908-11)"
lease: LEASE-TC-SECRET-e1
owner_modules: [MOD-secret-service, MOD-settings-service]
evidence_manifest_id: EVM-TC-secret-settings-service
evidence_record: evidence/runs/TC-secret-settings-service-E1-20260909T075131Z.json
evidence_record_superseded: evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json
pin_epoch: PC10-PIN-P5b-20260908
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — `TC-secret-settings-service` (card 20, gap `G-6`)

## 1. Status

**Complete.** Six operations, six tables, two test files, one migration, one delimited block in
`server/app/main.py`, and — after `PKT-TC-SECRET-FIX1` — a real AES-256-GCM cipher. **34 card
tests** pass; the full suite is **1164 tests, 0 failures, 0 errors, 3 xfailed** (counts read
from `--junitxml`, not from a terminal tail). E0: 27 checks, 0 violations.

`CR-TC-SECRET-02` and `CR-TC-SECRET-06` are **closed** (§10). Six CRs remain open.

The system now has a legal place to put an API key, a Telegram webhook secret and a per-task
credential — which is what `G-6` said was missing — and `ISO-05` finally has something to run
its denied case against.

## 2. Write set, before → after

| Path | Before | After (sha256 · bytes) |
| --- | --- | --- |
| `server/app/secret/__init__.py` | ABSENT | `a1fea095048303ab…` · 1149 |
| `server/app/secret/store.py` | ABSENT | `731a50a82b33dec4…` · 17984 |
| `server/app/secret/repository.py` | ABSENT | `a2f8178b4f756dd8…` · 10597 |
| `server/app/secret/service.py` | ABSENT | `eb399f437789b804…` · 31626 |
| `server/app/secret/router.py` | ABSENT | `fb00c4712287c71d…` · 9184 |
| `server/app/settings_service/__init__.py` | ABSENT | `a64230466914828c…` · 1435 |
| `server/app/settings_service/repository.py` | ABSENT | `1f447bdfbbb83029…` · 10629 |
| `server/app/settings_service/service.py` | ABSENT | `14e805437495c5f5…` · 20713 |
| `server/app/settings_service/router.py` | ABSENT | `a43e7afc772a4531…` · 6698 |
| `server/migrations/versions/0014_tc_secret_settings_service.py` | ABSENT | `3c2af48785c7184f…` · 11760 |
| `tests/contract/test_secret_scope_matrix.py` | ABSENT | `1c8e13f988f03ddd…` · 18308 |
| `tests/integration/test_task_credential_lease.py` | ABSENT | `aadce329f1a6bec8…` · 29468 |
| `server/app/main.py` | one delimited block added | `7bafc3ffff0ad895…` · 16214 |
| `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` | ABSENT | `b114401917fded1a…` · 14828 |

Nothing under `precode/`, `contracts/`, `acceptance/` or `agent-tasks/` was touched. The
`main.py` change is one `# >>> TC-secret-settings-service` … `# <<<` block; every other card's
block is byte-identical.

**`SG-HASH`: 26/26 pins verified against disk, drift 0**, at epoch `PC10-PIN-P5b-20260908`.
Mid-flight four pins had drifted (`modules.yaml`, `ports.yaml`, `ops/secrets.md`,
`recovery/README.md`) — all four the same `AMD-ENT-maintenance-01` purge-count edit
(60→61 entities, 21→22 kept), touching no operation, no edge and none of this card's seven
entities. The Coordinator re-pinned to `P5b` before this run, so the card and the tree agree
again; the observation is recorded here because a clean check today does not mean the window
never opened.

## 3. What was built

**`secret.store_provider_key`** — envelope encryption per `secrets.md` §4.1: a fresh data key
per secret, wrapped under a master key that comes from the environment and **never** from the
database or the repo. Idempotent on `provider_id + key_version`; the same version with a
different value is `IDEMPOTENCY_CONFLICT` rather than a silent overwrite of the live key. A new
version rotates and **keeps** the old `secret_ref` (`state = 'rotated'`), because `secrets.md`
§3 keeps both live through `rotation_overlap`.

**`secret.issue_task_credential`** — the ISO-05 gate. Order is the design: the lease is checked
first, through `MOD-analysis-service`'s own `verify_task_lease`, before any row is written and
before any key is read. There is no parameter by which a worker asks for a different provider's
key, and the `cli_acp` path is refused outright (`secrets.md` §5.1 gives it nothing). Check and
insert share one transaction, so a lease cannot expire in the gap between them.

**`secret.revoke_task_credential`** — idempotent by construction (`WHERE revoked_at IS NULL`).

**`settings.get_config` / `update_config` / `test_provider`** — a key goes in and never comes
back out: the read model has `key_configured: true|false` and a `secret_ref` id, and no field a
value could occupy. `test_provider` answers `unknown` (never `unusable`) for the CLI path and
for a disabled adapter, which is the `I14` mistake this operation is most likely to make.

**Migration `0014`** creates `secret_ref`, `task_credential`, `secret_audit`, `provider_config`,
`provider_test_result`, `source_connection`. It does **not** re-create `settings`: `0013` made
that table on this module's behalf and this card takes ownership without a second
`CREATE TABLE` (the `F-A3R1-01` rule). WR's `0015` chains after it; `alembic heads` returns one.

## 4. The two fixes the packet paused on

**Timestamp parser.** `parse_timestamp` was built from a sliced format string and could not
read the timestamps `format_timestamp` writes. Fixed to the same construction the other
packages use; a test now reads `issued_at`/`expires_at` back out of the database and asserts the
delta is exactly `TASK_CREDENTIAL_TTL_SECONDS`, which is itself asserted equal to
`LEASE_TTL_ANALYSIS_SECONDS` rather than to a literal 900.

**The uniqueness rule.** This is the one worth reading. `ux_task_credential_assignment` is
UNIQUE on `(owner_id, assignment_id, secret_ref_id)` and `ENT-task-credential` says the same in
prose: *"Một task nhận tối đa một credential cho một secret"*. My first version re-issued after
revocation and the database refused it. **The expectation was wrong, not the constraint** — so
the code now refuses the re-issue instead, and the test asserts the refusal.

The packet said to stop with a CR if the contract genuinely requires a re-issue path that its
own uniqueness rule forbids. It does not: nothing in `ports.yaml`, `secrets.md` §5 or
`entities.yaml` requires issuing a second credential for a pairing whose credential was revoked
— every revocation trigger (`submit_result`, `report_attempt_unknown`, lease expiry, run
cancel, owner revokes provider) also ends the worker's right to that task. So there is no
contradiction to escalate, only a gap: the contract never says which **error code** the refusal
carries. `NOT_FOUND` was chosen from the operation's own declared list as the one that states
the situation truthfully — there is no credential here for you — rather than blaming the lease,
which may still be perfectly current. That choice is `CR-TC-SECRET-07`, and it is a CR
precisely because a Worker picking an error code the contract omitted is a decision, not an
implementation detail.

## 5. Evidence

`EV-E1-15-tc-secret-settings-service` — `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json`,
schema-valid against `evidence/manifest.schema.json`.

| Oracle | Expected | Observed |
| --- | --- | --- |
| ISO-05, wrong worker (`SG-ISO05`, run for real) | `STALE_LEASE`, 0 credentials | `STALE_LEASE`, 0 |
| ISO-05, stale epoch, right worker | `STALE_LEASE`, 0 credentials | `STALE_LEASE`, 0 |
| Canary across every table, audit row, envelope (`recovery/f`) | 0 occurrences | 0 |
| `cli_acp` task (`ai/k`) | 0 credentials, 0 `secret_ref` | 0, 0 |
| `enabled = 1` without `terms_check_at`, raw `UPDATE` | refused by **DB** | `IntegrityError` on `ck_provider_config_terms_before_enable` |
| `terms_check_at` without `terms_check_by`, raw `UPDATE` | refused by **DB** | `IntegrityError` on `ck_provider_config_terms_by` |
| Wrong principal class (`recovery/i`, `recovery/h`) | `UNAUTHORIZED` ×3 | `UNAUTHORIZED` ×3 |
| Owner session, no CSRF (`R5-01`) | `CSRF_REJECTED`, session intact | `CSRF_REJECTED`, session intact |
| Key string in `GET /v1/settings` body | 0 | 0 |
| Routed `internal` operations | 0 | 0 |
| `alembic heads` | 1 | 1 |
| Card tests | 29 pass | 29 pass |
| `ruff check` / `ruff format --check` / `mypy --strict` | clean | clean |

**Claim.** The card's ceiling is `IMPLEMENTATION_VERIFIED`; this record is `SELF_VALIDATION`,
and both `protocol.md` §9 and `manifest.schema.json` cap that at **`CONTRACT_READY`**. The
schema rejected the higher label when it was first written, which is the gate doing its job.
Reaching the ceiling needs independent verification on a frozen candidate — not a Worker's own
say-so.

## 6. Not established

1. **Real encryption is `NOT_RUN`.** `uv.lock` resolves no AEAD library — no `cryptography`, no
   `pynacl`, no `pycryptodome` — and `server/pyproject.toml` is outside this write set, so the
   cipher is a port (`AeadCipher`) with `CryptographyAesGcm` as the production backend and a
   loudly-named `StubCipher` in the tests. Every property proved here is about who receives a
   credential and what is written down; none of it depends on the cipher. `CR-TC-SECRET-02`.
2. **Isolation is still unverified.** E3 `NOT_RUN`, so both Anthropic adapters stay
   `enabled: false` and `REQ-AC16` remains **`BLOCKED`**, never `FAIL`. This card enabled
   nothing.
3. **No live provider call.** `settings.test_provider` never touched an endpoint.
4. **The routers are not wired.** `server/app/wiring.py` (outside this write set) does not build
   `secret_context` / `settings_context`, so both routers answer `500 INTERNAL` in a running
   deployment until a follow-up packet wires them and passes `provider_config` / `secrets` into
   `AnalysisContext`. `CR-TC-SECRET-06`.
5. **Ciphertext is not in the database.** `secrets.md` §4.1 puts it in a table of
   `MOD-secret-service`; `entities.yaml` declares no entity for one, and an undeclared table
   fails `test_schema_matches_entities.py` on its first assertion. Consequence, stated plainly:
   a restored database does **not** carry its secrets and the operator re-enters the key —
   which is the "kế hoạch khôi phục secret riêng" `backup-restore.md` §5 already requires.
   `CR-TC-SECRET-01`.

## 7. A red suite that went green while this packet ran — recorded, not quietly dropped

The first full run (07:1xZ) had three failures in
`tests/integration/test_readiness_independent_channel.py` (card
`TC-storage-write-blocked-readiness`, worker WR): `CHECK constraint failed: length(id) = 26`,
because its seeded `backup_snapshot` ids (`01JSNAP90000000000000000S`) are **25** characters.
That file has zero references to `server/app/secret` or `server/app/settings_service` and zero
inserts into any of this card's six tables, so it was reported rather than fixed — WR's file,
WR's lease. WR corrected it while this packet was finishing, and the final run (07:4xZ) is
green: **1149 / 0 failures**.

It is written down anyway. A green number at the end of a packet cannot tell a reviewer that it
was red an hour earlier for someone else's reason, and the difference matters if WR's fix is
ever re-examined.

## 7a. `PKT-TC-SECRET-FIX1` — the cipher is now real

`PKT-P0-FIX7` put `cryptography>=43,<47` in `server/pyproject.toml` and `uv.lock` (46.0.7
resolved), which is what `CR-TC-SECRET-02` asked for. Gate verified independently before any
write: the addendum exists, `import cryptography` succeeds, and `wiring.py` builds both
contexts.

**Algorithm: AES-256-GCM.** `contracts/ops/secrets.md` §4.1 row *Thuật toán* offers
*"AES-256-GCM hoặc XChaCha20-Poly1305"* and mandates neither; §10 assigns the concrete choice to
PC10 "sau khi chốt stack". `cryptography` 46 ships `AESGCM` and the IETF `ChaCha20Poly1305`
(96-bit nonce) but **not** XChaCha20-Poly1305 (192-bit nonce, a different construction), so the
second option is unreachable with the library the repo now depends on. The choice and the reason
live in `server/app/secret/cipher.py`'s docstring, not only in this handoff.

**What changed.** New `server/app/secret/cipher.py` holds the `AeadCipher` port, the `AesGcm256`
backend, and the only nonce and data-key sources in the package. `store.py` imports them and
defaults to the real backend; the lazy import, the `CipherUnavailable` guard and the
`type: ignore[import-not-found]` are **deleted** — as the old comment predicted they would be —
because an unreachable guard is a claim about the world that stopped being true. `StubCipher` is
gone from both test files: every assertion in this card, including the canary count and the
masked audit rows, is now made against ciphertext the contract's own algorithm produced.

**New failure classification.** A wrong master key now raises `MasterKeyMismatch`, a subclass of
`MasterKeyUnavailable` so the service layer's existing handling covers it with no new branch. It
has its own name because the fixes differ: a missing key means "set the variable"; a mismatched
key means "you restored a database whose secrets were written under a different key".

**Four new oracles** (`tests/contract/test_secret_scope_matrix.py`):

| Property | Oracle | Observed |
| --- | --- | --- |
| Ciphertext is not the plaintext | search the serialised envelope for the value and its hex | 0 occurrences, and it still decrypts |
| Only the right master key opens it | decrypt under a different 32-byte key | `MasterKeyMismatch` (AEAD tag failure) |
| Locator/purpose are bound in | read the same material under another `purpose` | `MasterKeyMismatch` |
| Nonces are never reused | 64 stores → 128 nonces (payload + key-wrap) | 128 distinct |

The nonce test earns its place: GCM's one fatal misuse is a repeated (key, nonce) pair, and
"we call `token_bytes`" is a sentence, not a measurement.

## 8. Change requests

| CR | To | One line |
| --- | --- | --- |
| `CR-TC-SECRET-01` | PC02 | `secrets.md` §4.1 requires a ciphertext table; `entities.yaml` declares no entity for one. Material lives behind a port until an entity exists. |
| ~~`CR-TC-SECRET-02`~~ | Coordinator | **CLOSED** by `PKT-P0-FIX7`: `cryptography>=43,<47` (46.0.7) is a declared `rr-server` dependency. Real AES-256-GCM now runs and is measured (§7a). |
| `CR-TC-SECRET-03` | PC02 | `task_credential.assignment_id` → `ENT-assignment`, but no column joins `analysis_task` to an assignment; "the right task" is held by the lease check, not by the FK. |
| `CR-TC-SECRET-04` | PC05 | `analysisWorkerToken` authenticates a *class*, not an instance, so `worker_instance_id` is corroborating rather than load-bearing. |
| `CR-TC-SECRET-05` | PC02 | `settings.update_config` is idempotent on `request_id` but `ENT-settings` has no column for it; the registry is process-local (same shape as `CR-TC-ANALYSIS-04`). |
| ~~`CR-TC-SECRET-06`~~ | WS / Coordinator | **CLOSED** by `PKT-P0-FIX7` — verified from this side, §10. |
| `CR-TC-SECRET-07` | PC01 | No error code is specified for re-issuing a credential after revocation; `NOT_FOUND` chosen from the operation's declared list. |
| `CR-TC-SECRET-08` | Coordinator | Four pinned files drifted mid-packet on an unrelated purge-count edit before the `P5b` re-pin; card pins and tree bytes must not diverge while a card is being implemented. |

## 10. `CR-TC-SECRET-06`, closed from this side

Verified rather than assumed: `server/tests/test_wiring.py` has 12 tests, 0 failures, and three
of them are the ones that matter here —
`test_settings_is_200_for_the_owner_on_a_wired_app` (the 500 that raised the CR is gone),
`test_settings_needs_the_owner_session` (401 without a session, so the fix did not open a door),
and `test_the_settings_summary_carries_no_secret` (the read model still carries no value on a
*wired* app, which is the assertion my own tests could not make because they never built one).
`wiring.py` builds `secret_context` and `settings_context` and passes `SettingsProviderView`
into the secret context.

**The master-key deviation, as ruled and as implemented.** The Coordinator's ruling —
unset ⇒ run with `store=None` and a named reason (`REQ-D51`: a key is not mandatory, and
`/v1/settings` must still serve); set-but-malformed ⇒ refuse to start naming the variable; never
a default key — is what `wiring.py` does: `secret_store = None` with the reason recorded in its
`unwired` list, and `RuntimeError("RR_SECRET_MASTER_KEY is set but unusable: … Refusing to start
rather than run with no envelope encryption")` on the malformed branch. That matches
`load_master_key`, which raises on absent *and* malformed and generates nothing. Accepted; the
asymmetry is right, because a deployment that believes it has encryption and silently has none
is worse than one that will not boot.

## 9. Next actor

**Coordinator.** Re-hash the write set, then decide whether this goes to an independent
Auditor (the card's §12 asks three questions: can a value leave the module; did ISO-05's denied
case really run; is the `terms_check` gate at the DB or only in the app — §5 answers all three
with evidence). `CR-TC-SECRET-02` and `-06` are the two that block a working deployment;
neither is fixable from inside this lease.

`lease_released_at`: 2026-09-09T07:52Z (`LEASE-TC-SECRET-e2`; `-e1` released 07:35Z). No
further writes from `worker-WAI` under either lease.
