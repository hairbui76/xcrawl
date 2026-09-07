# TASK_PACKET PKT-P0-SKELETON — Phase 0: repo skeleton, generated contracts package, CI

- packet_id: `PKT-P0-SKELETON` · assignee: Worker `worker-WS` · authority `AUTH-COORD-P0-SKELETON` (parent `AUTH-OWNER-20260907-03`, record `…/scratchpad/packets/OWNER-DECISIONS-20260907-02.md`) · lease `LEASE-P0-SKELETON-e1` (exclusive) · expires 2026-09-08T12:00Z · completion ceiling: `IMPLEMENTATION_VERIFIED` for the skeleton itself (CI runs green locally); nothing product-behavioural is claimed.
- Mode: code mutation under message-tracked lease (OD-20260907-02 #3). Capabilities: read the whole repo; write only the paths below; **network allowed only for package installation** (`uv`, `npm`) — no other calls; no secrets; no git commits (Coordinator commits).
- scratch dir for helpers: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/ws/`.

## Read set (binding)
`precode/adr/ADR-0011-frameworks-and-toolchain.md` (the toolchain: uv/Python 3.12, FastAPI + Pydantic v2, SQLAlchemy 2 Core + Alembic, Playwright, httpx, sentence-transformers (declare, do not download models), Vite + React 18 + TypeScript, TanStack Query, openapi-typescript, pytest/pytest-asyncio, Vitest + Testing Library, Playwright Test, ruff, mypy --strict on server core, eslint + prettier, GitHub Actions), `agent-tasks/README.md` §5.3 (seven directories), `docs/master-plan.md` §2 (two non-negotiable rules, four CI jobs + the OpenAPI validator job), `contracts/http/openapi.yaml`, `contracts/schemas/*.json`, `contracts/errors.yaml`, `contracts/ports.yaml` (operation ids), `evidence/tools/e0_check.py` + `evidence/tools/README.md` (how E0 runs), `precode/README.md`, `agent_profile/worker.md`.

## Write set (CREATE unless stated)
| Path | Content |
| --- | --- |
| `pyproject.toml` (root, uv workspace) + `uv.lock` | workspace members `server`, `collector`, `worker`, `shared/rr_contracts`; Python 3.12; dev deps: pytest, pytest-asyncio, ruff, mypy, hypothesis (optional), openapi-spec-validator, datamodel-code-generator (or an in-repo generator — see below), pre-commit |
| `server/pyproject.toml`, `server/rr_server/__init__.py`, `server/rr_server/main.py` (FastAPI app factory, health endpoints `health.get_liveness` / `health.get_readiness` wired to a stub readiness provider), `server/rr_server/db/` (engine factory: SQLite, WAL, `PRAGMA foreign_keys=ON`, connection helper), `server/alembic.ini`, `server/migrations/env.py` + empty initial revision, `server/tests/test_smoke.py` | app boots, health returns per `contracts/state/storage.yaml` readiness shape |
| `collector/pyproject.toml`, `collector/rr_collector/__init__.py`, `collector/rr_collector/main.py` (CLI entry stub: prints capability registration payload shape from `contracts/capabilities.yaml`, no browser launch), `collector/tests/test_smoke.py` | Playwright declared as dependency; browsers NOT installed |
| `worker/pyproject.toml`, `worker/rr_worker/__init__.py`, `worker/rr_worker/main.py` (stub), `worker/tests/test_smoke.py` | |
| `shared/rr_contracts/pyproject.toml`, `shared/rr_contracts/rr_contracts/__init__.py`, `shared/rr_contracts/rr_contracts/generated/` (**generated**: Pydantic v2 models for every `contracts/schemas/*.json`; enums/constants for error codes from `contracts/errors.yaml`, operation ids from `contracts/ports.yaml`, state enums from `contracts/state/*.yaml`), `shared/rr_contracts/generate.py` (deterministic generator; writes a `GENERATED_FROM.json` with sha256 of each source), `shared/rr_contracts/tests/test_generated_matches_contracts.py` (fails if any source hash differs from GENERATED_FROM.json or regenerating produces a diff) | the generate-don't-hand-edit rule made checkable |
| `web/package.json`, `web/package-lock.json`, `web/vite.config.ts`, `web/tsconfig.json`, `web/index.html`, `web/src/main.tsx`, `web/src/App.tsx` (placeholder shell with the five spec §4 navigation entries as routes, no data), `web/src/lib/api.ts` (fetch wrapper: cookie session + CSRF double-submit header, per `contracts/http/openapi.yaml` security schemes), `web/src/generated/openapi.d.ts` (**generated** by openapi-typescript from `contracts/http/openapi.yaml`) + `web/scripts/generate.mjs` + a test that regeneration produces no diff, `web/src/App.test.tsx` (Vitest smoke), `web/.eslintrc.cjs`/`eslint.config.js`, `web/.prettierrc` | |
| `tests/README.md` (how E1 uses `acceptance/fixtures/**` directly as test data; the fixture loader contract), `tests/conftest.py` (fixture loader utilities: load a fixture JSON, expose `given/events/expected`, resolve `rows.<entity>[]`) | shared by Phase 1 cards |
| `probe/README.md` (placeholder pointing to `agent-tasks/TC-x-feasibility-probe.md`; no code) | |
| `evidence/tools/verify_cards.py` | port of PC10's EV-PC10-01 verifier (recompute every card's pinned hashes; fail on mismatch; epoch unanimity; check no `.py` under `web/`, no `.ts` under Python trees). Read the algorithm from `agent-tasks/README.md` §5 and the cards' pin blocks; do not weaken it. |
| `.github/workflows/e0.yml` (runs `evidence/tools/e0_check.py` read-only + `verify_cards.py`), `.github/workflows/openapi.yml` (openapi-spec-validator on `contracts/http/openapi.yaml`, runs before generation jobs), `.github/workflows/python.yml` (uv sync; ruff; mypy on server core; pytest for server/collector/worker/shared incl. the generated-matches test), `.github/workflows/web.yml` (npm ci; eslint; vitest; generated-matches test) | `PYTHONDONTWRITEBYTECODE=1` everywhere; no live jobs |
| `.pre-commit-config.yaml`, `.gitignore` (root: `.venv/`, `__pycache__/`, `node_modules/`, `web/dist/`, `*.db`, `.env*`), `.python-version`, `Makefile` or `justfile` (targets: `gen`, `lint`, `test`, `e0`, `cards`) | |
| `README.md` (root) | how to set up (uv sync, npm ci), run tests, regenerate contracts, run E0; links to `precode/README.md` and `docs/master-plan.md` |
| `evidence/handoffs/P0-skeleton-handoff.md` | HANDOFF per baseline §4 (paths, sha256, commands run with exit codes, limitations) |
| MODIFY `precode/README.md` (one row: repo skeleton exists, how to run), MODIFY `.gitignore` if one exists | |

Nothing else. In particular do not touch `contracts/`, `acceptance/`, `agent-tasks/`, `precode/` (except the one README row), `evidence/` (except the handoff and the new tool).

## Checklist
1. [ ] `uv sync` succeeds; `uv run pytest` green across all four Python packages (smoke + generated-matches).
2. [ ] `npm ci` in `web/` succeeds; `npm run lint`, `npm test` green; generated client matches.
3. [ ] `uv run python evidence/tools/e0_check.py` (read-only mode, output to scratch) still 24/24 PASS after your additions — you added no contract files, so nothing should change; if the tool scans `web/` or `server/` prose and complains, do not edit the tool: report it.
4. [ ] `uv run python evidence/tools/verify_cards.py` PASS 501/501 (or whatever the cards currently pin) — you must not change any pinned file.
5. [ ] `openapi-spec-validator contracts/http/openapi.yaml` result recorded honestly (this is the first time the file is validated; if it FAILS, do not edit it — record every error in the handoff as `CR-P0-01` for PC05; the CI job may be marked `continue-on-error` with an explanatory comment until PC05 fixes it).
6. [ ] All generated files carry a header `# GENERATED — do not edit; source sha256 …` and the diff-on-regenerate test exists for both languages.
7. [ ] No secrets, no `.env` committed, no model downloads, no browser installs.

## Evidence (SELF_VALIDATION, in the handoff)
Exact commands with exit codes and durations for every checklist item; versions of uv, Python, node, npm; package lock hashes; the openapi validator output verbatim (truncated to the first 50 errors if any).

## Stop gates
Baseline §6 plus: if a dependency cannot be installed (no network), stop with BLOCKED_DEPENDENCY and the exact error — do not vendor or stub packages silently. If a card-pinned file would have to change, stop: BLOCKED_SCOPE.

Reply to the Coordinator ONLY: status, created top-level paths, the six checklist results one line each (with exit codes), openapi validator verdict, concerns/CRs (≤30 lines).
