# TASK_PACKET PKT-PC08 — Khóa secrets, Internet boundary, backup và recovery

- packet_id: `PKT-PC08` · assignee_role: Worker · assignee_principal: `worker-W2` (continuation of the PC01 worker; new packet, new lease)
- authority_id: `AUTH-COORD-PC08` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC08-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T08:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w2/`

## Goal
Execute plan §11 **PC08**: authentication/session/CSRF/token contract for the single owner account, secret storage and scoped distribution (B13), Internet boundary rules (URL fetch policy, SSRF/redirect, content rendering, CLI tool access), WAL-safe backup with manifest (B11), restore drill with side-effect lock and reconciliation (I15), RPO/RTO, disk-full/readiness, audit retention, and recovery fixtures.

You already authored `contracts/ops/deployment.md` in PC01. This packet does **not** grant MODIFY on it; if PC08 findings require changes there, raise `CR-PC08-nn` (the Coordinator will issue a separate MODIFY packet).

## Non-goals
No live backup/restore execution (evidence NOT_RUN). No product code. Do not modify earlier packages.

## Read set (frozen; record sha256)
baseline; SRC-PLAN (§3 B11/B13, §3.1 SQLite, §5.1, §6, §6.1, §7 I01/I11/I15, §8.4, §10 STORAGE_WRITE_FAILED/RESTORE_UNVERIFIED, §11 PC08, §13 SC12/SC17/SC18/SC27); SRC-SPEC (§3.1 D05, §6.4, §7.3, §9.3 disk full, §11 all, §12 AC-12/17/18, §13 M8); PC00 `precode/requirements.csv`, `decision-register.md`, `adr/*` (ADR-0005, ADR-0010); PC01 `contracts/modules.yaml`, `capabilities.yaml`, `ports.yaml`, `ops/deployment.md`; PC02 `contracts/data/entities.yaml`; PC03 `contracts/state/storage.yaml`, `run.yaml`, `delivery.yaml`, `errors.yaml`, `retry-policy.yaml`; PC06 (if present when you start — it is being written in parallel; if absent, cite by planned path) `contracts/ai/providers.yaml`; PC07 (parallel; same rule) `contracts/telegram/commands.yaml`; `agent_profile/worker.md`, `protocol.md`.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `contracts/ops/secrets.md` | Front-matter. (1) Owner auth: single account, no signup, no self-service reset (D05), password hashing policy (algorithm class + parameters PROVISIONAL), session token (choose mechanism PROVISIONAL: HttpOnly cookie + CSRF token double-submit, or bearer — state which and why; must match PC05 openapi security scheme — if PC05 chose differently, raise CR), session expiry/idle/absolute, revocation, login rate limiting/lockout, mobile access (D04) and external exposure (TLS required, reverse proxy assumptions); (2) collector/worker tokens: scope per capabilities.yaml, storage on personal machine (config file mode 0600), rotation procedure, revocation, replay protection (request_id/nonce), token never in repo; (3) secret store on server: key-at-rest (envelope encryption with master key from env/file, PROVISIONAL), access API only via secret service scope, redaction in logs (patterns), never to frontend/Telegram/log; (4) per-task scoped delivery to analysis worker (B13): short-lived credential, bound to assignment/lease, revoked at release, cached never on disk; CLI/ACP path: no server secrets, session on personal machine; (5) Chrome: project profile, debug port loopback only, profile excluded from server backups, X session never synced; (6) Telegram: bot token in secret store, webhook secret, link codes one-use/expiry; (7) audit log: what is logged, retention PROVISIONAL, redaction. |
| `contracts/ops/internet-boundary.md` | Front-matter. Outbound policy per module (allowlisted hosts: X via Chrome only from collector; arXiv/OpenAlex from research connector; Telegram API from adapter; AI provider APIs from worker/adapter as configured); URL fetch rules (only URLs extracted by the collector from posts matching allowlisted paper hosts; deny private/link-local/loopback ranges, deny redirects to those, scheme allowlist, size/time caps, no model-directed fetch); inbound: only server ports; personal machine outbound-only; content rendering: source text rendered as text, no HTML/script execution, markdown sanitisation in app, Telegram escaping; CLI tool access from content forbidden (references PC06 providers isolation). Enforcement mechanisms and test oracles (SC17/SC18 relevant parts). |
| `contracts/ops/backup-restore.md` | Front-matter. Backup while DB active: SQLite Online Backup API or `VACUUM INTO` (cite https://www.sqlite.org/backup.html, https://www.sqlite.org/wal.html), why file copy of a WAL DB is insufficient (AMD-B11), schedule PROVISIONAL, backup manifest (DB snapshot sha256 + schema_version + embedding artifacts/config + generation + settings export without secrets + secret recovery plan pointer + created_at + app version), retention PROVISIONAL, integrity check (`PRAGMA integrity_check`, row counts), what is NOT in backup (Chrome profile, worker tokens — documented recovery steps), RPO/RTO targets PROVISIONAL with rationale; restore drill runbook: clean environment, `storage.recovery_required` on start, dispatcher/worker claims locked, outbox not replayed, stale leases revoked, `first_announced` untouched, verification checklist (counts/hashes for Saved/report/ledgers vs manifest), reconciliation of in-flight work (unknown deliveries stay unknown), explicit operator step to re-enable dispatch (`RESTORE_UNVERIFIED` until then), evidence to capture; disk-full/readiness behaviour consistent with storage.yaml; a reader-oriented "what point in time can I recover to and what is lost" section. |
| `acceptance/fixtures/recovery/README.md` | index |
| `acceptance/fixtures/recovery/*.json` | (a) restore with old outbox pending/unknown → nothing sent (SC27/I15); (b) restore then stale lease from pre-backup worker → rejected; (c) disk full mid-ingest → no ACK, cursor unchanged, readiness red (SC26/STORAGE_WRITE_FAILED); (d) WAL-unsafe copy → detected as invalid backup (integrity/manifest mismatch); (e) Saved snapshot hash before backup == after restore (AC-12/SC12); (f) prompt injection attempts to read secret → canary never appears in output/logs (AC-17/SC17 ops side); (g) SSRF: paper URL redirects to 127.0.0.1 → blocked; (h) unauthenticated request to owner API → 401, no side effect; (i) collector token used to call Save → 403 FORBIDDEN_EDGE; (j) restore verification incomplete → dispatch stays locked. Each with given/events/expected/forbidden_effects/scenario_refs/invariant_refs. |
| `evidence/handoffs/PC08-handoff.md` | HANDOFF |

Create `acceptance/fixtures/recovery/`.

## Checklist (plan PC08)
1. [ ] One account, no signup; session expiry/revocation; owner API protection; CSRF if cookie; collector token scope/rotation.
2. [ ] Secret storage/key-at-rest, distribution to worker, Chrome debug loopback, profile excluded from server backup.
3. [ ] URL fetch policy, private-address redirect block, content render safety, CLI tool access from content blocked.
4. [ ] Backup during active DB, manifest contents, embedding artifacts/config, secret recovery plan, retention.
5. [ ] Restore drill runbook with integrity checks, counts/hashes, lease revocation, dispatch lock until reconciliation.
6. [ ] RPO/RTO, disk-full/readiness, audit retention; no claim that transactions cover hardware failure.

## Invariants
I01, I11, I15 with positive + counterexample fixtures.

## Verification (EV-PC08-nn, SELF_VALIDATION)
- EV-01: fixtures parse; every error code/operation/state cited exists in errors.yaml/ports.yaml/storage.yaml (script); misses → CR-PC08-nn.
- EV-02: cross-check: secrets.md auth mechanism vs openapi.yaml security schemes (if PC05 file exists at your start; else record NOT_RUN and CR).
- EV-03: backup manifest field list vs entities/embedding_generation fields (manual diff recorded).

## Stop gates
Baseline §6.
