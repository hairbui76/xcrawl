# AUDIT_REPORT `A3-P5-R1` — independent review of the integration wiring wave — FC-P5

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P5-R1` · authority `AUTH-COORD-A3-P5-R1` (parent `AUTH-OWNER-20260908-11`) · lease null |
| reviewer | `auditor-A3` — authored nothing; no repo write. Independent of every wiring packet. |
| candidate | `FC-P5`, 692 entries, `manifest_sha256 = d4d7f219fa525b785b587a1bfe60caf6deca11868e33c0e4eb92204109d593b4`, epoch `PC10-PIN-P5c-20260909`, 20 cards |
| quiescence | Recomputed start and end: **692/692** identical, header hash reproduces. `git status --porcelain` (excl. `.claude/`) **113** before and after; **0** `__pycache__`. Not `STALE`. |
| method note | Everything in §2 was run **as an operating-system process** — real `uvicorn`, real `curl` over TCP, separate CLI invocations — not through `TestClient`. All artefacts went to a scratch directory; the repository was never written to. |

## 1. Regression — every Coordinator number reproduced

| Gate | Coordinator | Mine |
| --- | --- | --- |
| `uv run pytest` | 1161 / 3 xfailed / 0 failed | **1161 passed, 3 xfailed, 0 failed** |
| `ruff check` / `format --check` | clean / 187 | `All checks passed!` / `187 files already formatted` |
| `uv run mypy` | Success, 101 files | **`Success: no issues found in 101 source files`** |
| gen-check / OpenAPI | clean / OK | `generated tree matches…` / `contracts/http/openapi.yaml: OK` |
| `verify_cards.py` | 13/13 over 20 cards, 3962 | **13 PASS, 3 962 assertions, 0 violations** @ `PC10-PIN-P5c-20260909` |
| `e0_check.py` | 27/27 | **27 PASS · 0 FAIL · 0 violations** |
| no-network whole suite | — | **rc=0, zero attempts** (new processes included) |

## 2. Running it as a process — what actually happened

**Composition root and `rr_admin` (WS).** From a **temp directory**, `RR_DATABASE_URL=… uv run
python tools/rr_admin.py migrate` ran the chain to `0015_tc_storage_maintenance_window` and
printed `done`. `bootstrap-owner` created the owner (password read from non-TTY stdin; there
is deliberately no `--password` flag). `status` printed a genuinely useful, honest inventory —
eleven wired components, and seven **named** unwired ones each with a reason and a CR
reference. That command alone answers most of what the runbook wave existed to answer.

`uvicorn server.app.main:app` started from the repo root and reached `Application startup
complete`. Over real HTTP:

| request | result |
| --- | --- |
| `GET /healthz` | **200** `{"status":"up","schema_version":"0.3.0"}` |
| `POST /v1/auth/login` (bad headers) | **422** proper `ErrorEnvelope`, `violation_kind: required_header_missing` |
| `POST /v1/auth/login` (correct) | **200**; `Set-Cookie: rr_session=…; HttpOnly; Max-Age=43200; Path=/; SameSite=lax; Secure` and `rr_csrf=…` **without** HttpOnly |
| `GET /v1/health/readiness` | **200** |
| `GET /v1/runs` | **200** `{"runs":[]}` |
| `GET /v1/settings` | **200** |
| `GET /v1/saved` | **200** |
| `GET /v1/reports` | **500 `INTERNAL`** — see `F-A3-P5-03` |

This is the first time the cookie flags I verified structurally in Phase 1 have been seen on
the wire, and they are exactly what `secrets.md` §2.3 requires.

**Persisted storage health (WR) — the headline of packet item 2, and it works.** Process 1:
`backup_cli … maintenance --open --reason restore` → `{"storage_health": "maintenance",
"transition": "T-ST-03", "window_id": "01M22K2MQ4…"}`. A row landed in `maintenance_window`
(`opened_by: ACT-backup-operator`, `reason: restore`, `closed_at: NULL`). Process 2, a
**completely separate invocation**, ran `restore` and got past the maintenance precondition —
it failed only on my deliberately fake snapshot id, with a clean `NOT_FOUND` envelope. **G-3 is
genuinely closed**: the window survives across processes. But see `F-A3-P5-01` — the command
*as the runbook documents it* crashes.

**Probe (WX) — verified, including the negative.** From a temp cwd with a config whose
`output_dir` is the relative `evidence/runs/SP1-x-feasibility`, `--dry-run` reported
`"wrote_nothing": true` and resolved the path against **cwd**, stating the rule in its own
output. I then checked the filesystem: only `cfg.json` existed afterwards — no `evidence/`
tree, no `probe.log`, nothing. G-5 closed and the dry-run really is inert.

**Collector (WC) and worker (W3A).** Both refuse without configuration, with a named,
actionable reason and no default: collector `--check-config` →
`{"status":"refused_to_start","reason":"missing_server_url","message":"RR_SERVER_URL is not
set; the collector has no default server address"}`; worker `--run` →
`{"started": false, "reason": "server_url_not_configured"}`. Neither wrote a row
(`analysis_attempt` = 0). `--print-adapters` shows both Anthropic adapters `enabled: false`,
`reason_code: isolation_unverified`, `ac16: BLOCKED` — unchanged from what I verified in P3.
*Scope*: I could not drive the disabled-adapter **backoff loop** against a live server without
`RR_SERVER_URL` plus a collector token, so that specific behaviour rests on the card's tests
and on my P3 verification of the adapter refusal itself, not on this round's process run.

**Secret/settings service (WAI, 20th card).** The master-key split ruling behaves exactly as
ruled, both halves: **unset** → the app runs and `status` says `secret_store … RR_SECRET_MASTER_KEY
is not set; secret.* operations refuse (REQ-D51: a key is not mandatory). No key is ever
generated or defaulted.`; **malformed** → the process **refuses to start**:
`RuntimeError: RR_SECRET_MASTER_KEY is set but unusable: … Refusing to start rather than run
with no envelope encryption (contracts/ops/secrets.md §4.1)`. On disk,
`provider_config` carries `CHECK (enabled = 0 OR terms_check_at IS NOT NULL)` — the claimed
constraint, present verbatim — `settings` exists once (taken over from `0013`, and my
schema-vs-entities sweep is still 0 differences in both directions), and `task_credential` is
empty.

## 3. Findings

### `F-A3-P5-01` — MEDIUM — the runbook's `maintenance --open` crashes with a traceback

`docs/owner-runbook.md` §9.4 documents, and marks `đã chạy ở đây`:

```bash
uv run python -m tools.backup_cli --database var/research-radar.db maintenance --open
```

Run exactly as written, it dies:

```
MaintenanceWindowRequired: a persisted guard needs reason= and opened_by= to open a window
(ENT-maintenance-window: both columns are NOT NULL)
```

The G-3 fix that made the window persist also made `reason` mandatory, but `--reason` is still
**optional** in argparse and the exception is not routed through the CLI's JSON envelope —
which the same CLI produces correctly for `UNAUTHORIZED` and `NOT_FOUND`. So the operator's
first backup command fails with a Python traceback instead of a usage error or a typed
refusal. Adding `--reason restore` works and everything downstream is correct.

**Remediation constraint:** make `--reason` required when `--open` is given (argparse), or map
`MaintenanceWindowRequired` onto the envelope; update §9.4's command. Do not close this by
defaulting the reason — it is a recorded column and a default would fabricate an audit value.
`OPEN`.

### `F-A3-P5-02` — MEDIUM — `rr_admin status` gives a reason that has been false for three phases

`server/app/wiring.py:476` (and the docstring at `:42`) hard-codes:

```
not wired : research_connector — REQ-A6 facts still PLACEHOLDER_KC
```

That is not true and has not been since Phase 2. On these very bytes,
`contracts/retry-policy.yaml` `research_connector_rate_limit.status` is **`DOCS_derived`** with
all six values populated, and `precode/requirements.csv` has `REQ-A6` at **`XN`**. I re-derived
those four facts from the primary documentation myself in `A3-P2-R1`. The real blockers — which
I verified in that same round — are `SG-DOC` (no contract names either API's host or endpoint;
the shipped config carries `endpoint_template = None`) and `SG-LIVE`.

The conclusion is right and the connector should indeed be unwired; the **reason** is wrong,
and it is printed on the one screen this wave built for the Owner to learn what works. Someone
reading it would go re-resolve a requirement that is already closed.

**Remediation constraint:** state the actual blocker (`SG-DOC` / `SG-LIVE`, `CR-PC05-03`), and
prefer deriving the line from the contract rather than restating it in a literal — a hard-coded
status string is exactly what went stale here. `OPEN`.

### `F-A3-P5-03` — MEDIUM — `GET /v1/reports` answers 500 `INTERNAL` on the shipped process

On the running server, `/v1/reports` returns:

```json
{"code":"INTERNAL","message_safe":"Có lỗi không mong đợi.","details_safe":{"operation_id":"report.get"}}
```

To be fair to it: this is **contract-conformant** — `openapi.yaml` declares `500` for that
path, the body is a well-formed `ErrorEnvelope`, no traceback or internal detail leaks, and
`rr_admin status` separately and honestly says `report_context` is unwired (`CR-P0-07`).

But this wave's stated premise was that *"`auth.login` → 500 outside tests"* was a gap worth a
wave. `/v1/reports` now has the same shape: the single owner-facing route that does not work
reports itself as **unexpected** when it is entirely expected, and gives the Owner nothing
actionable. Every other unwired dependency in this codebase surfaces as a typed refusal with a
reason code — storage health, the connector, the adapters, the collector, the worker — so the
precedent for doing better is the codebase's own.

**Remediation constraint:** a typed refusal naming the missing ports (`tag_port`,
`embedding_port`) and citing `CR-P0-07`, as `rr_admin status` already does in prose; or, if the
contract will not carry such a code, say so in the runbook so the Owner is not surprised.
`OPEN`.

### `F-A3-P5-04` — LOW — half the entry points self-bootstrap `sys.path` and half do not

| entry point | `sys.path` bootstrap | run by path |
| --- | --- | --- |
| `tools/rr_admin.py` | yes | works |
| `probe/x_feasibility/run_probe.py`, `probe/go_no_go.py` | yes | works |
| `tools/backup_cli.py` | **no** | `ModuleNotFoundError: No module named 'server'` |
| `collector/app/main.py`, `worker/app/main.py` | **no** | `ModuleNotFoundError` |

No runbook command is broken — the runbook uses `-m` for all three of the latter, and I
confirmed each works that way. But `rr_admin.py` teaches the operator that `python tools/<x>.py`
is fine, and the sibling CLI in the same directory then dies with a bare traceback. Cheap to
make uniform. `OPEN`.

**New findings: 4 — MEDIUM 3, LOW 1. HIGH 0.** I close nothing and supply no patches.

## 4. Per-packet verdicts

| packet | verdict |
| --- | --- |
| **WS** — composition root, `rr_admin`, cwd-independent alembic | **PASS**, carrying `F-A3-P5-02` and `F-A3-P5-03`. Migrate/bootstrap/status/serve/login all work as processes. |
| **WR** — persisted storage health (`0015`) | **PASS** — cross-process window proved by two separate invocations. Carries `F-A3-P5-01`. |
| **WX** — probe `output_dir` + `--dry-run` | **PASS** — resolved against cwd; dry-run wrote nothing, verified on the filesystem. |
| **WC** — collector loop | **PASS** — refuses with a named reason, no default, no rows. |
| **W3A** — worker loop | **PASS** — refuses with a named reason; adapters still `enabled: false`; backoff loop not exercised as a process (scope stated above). |
| **WAI** — secret/settings, 20th card | **PASS** — master-key split correct in both directions; `provider_config` CHECK present; `settings` taken over; `task_credential` empty. |
| **Regression** | **PASS** — every number reproduced, no-network run clean. |

## 5. Can the Owner run it end to end?

**No — but far more of it than before, and the gaps are named.**

**Works now, verified by me as processes:** create/upgrade the database from any directory ·
bootstrap the owner · `status` telling the truth about what is wired · start the server ·
log in over HTTP with correct cookie flags · readiness · runs · settings · saved · open a
maintenance window that a second process can see · a probe dry-run that writes nothing ·
collector and worker refusing safely without configuration.

**Still cannot:**

1. **Reports at all** — `report_context` unwired (`CR-P0-07`); `/v1/reports` is a 500. No report
   can be built or published, which is the product's output.
2. **`maintenance --open` as documented** — crashes without `--reason` (`F-A3-P5-01`).
3. **Tags** — `MOD-tag-service` has no card (`CR-TC-SCHED-06`, `CR-TC-BACKFILL-07`).
4. **Research connector** — unwired; the real reason is `SG-DOC`/`SG-LIVE`, not what `status`
   prints (`F-A3-P5-02`).
5. **Any live path** — collector needs `RR_SERVER_URL`, a collector token and a real X session;
   Telegram needs a bot token and `RR_TELEGRAM_WEBHOOK_SECRET`; both AI adapters are
   `enabled: false` on unverified isolation. **E3/E4 are `NOT_RUN` everywhere** — SP1 has never
   run, no live AI/Telegram/X call has ever happened, no real restore drill.

So: the Owner can now stand the system up, log in, and inspect it — which is new and is what
this wave promised. The Owner cannot yet make it *do* anything end to end.

## 6. Residual

* `F-A3-P5-01…04` open; `F-A3R4-01`, `F-A3-P2-01/-02`, `F-A3-P4R2-01/-02` open from earlier rounds.
* Three strict xfails unchanged (`CR-PC07-04`, `CR-TC-AUTH-01`, `CR-TC-IDENTITY-02`); three
  `delivery.md` §3.4 facts still `BLOCKED_DEPENDENCY`.
* `AMD-ENT-maintenance-01` is a **Coordinator technical amendment — the Owner has not been
  asked**. It is the same shape as `AMD-ENT-owner-01`, which the Owner later ratified; it
  should go to the next Owner round rather than settle by silence.
* `docs/owner-runbook.md` still carries WS's pre-wave text: §9.4's G-3 box describes a gap that
  is now closed, and its `maintenance --open` command is the one that crashes. It needs WS2's
  post-commit re-verification before an Owner follows it.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product acceptance,
  not a security assessment, no live API calls.
