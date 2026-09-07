# Coordinator ruling — framework and toolchain choices for stack B (ADR-0011, provisional-accepted; Owner delegated the pick on 2026-09-07 and may object)

Authority: AUTH-OWNER-20260907-02 (Owner answer: "You pick, record as ADR"). Status: `provisional-accepted` (technical), decision_owner Coordinator, Owner may reverse. Constraints honoured: SQLite is the store (D07), Chrome via Playwright on the personal machine (spec §6.3), embedding local on the server (D48/D50), no external broker, one language per tier (stack B).

| Tier | Choice | Why (conservative default) | Alternatives considered |
| --- | --- | --- | --- |
| Python version / packaging | Python 3.12, `uv` for env + lock, `pyproject.toml` per package (`server`, `collector`, `worker`, shared `rr_contracts`) | reproducible, fast, single lock; matches contracts' schema_version discipline | pip-tools, poetry |
| Server API | FastAPI + Pydantic v2 (request/response models generated from `contracts/schemas/*.json` + `contracts/http/openapi.yaml`, not hand-written) | OpenAPI-native, validates the wire contract, async-capable for Telegram webhook | Flask, Django |
| Persistence | SQLAlchemy 2 Core (no ORM magic) + Alembic migrations, `sqlite3` with WAL, `PRAGMA foreign_keys=ON`; Online Backup API via `sqlite3.Connection.backup` | explicit SQL for transaction maps (TXN-*), partial indexes/generated columns need Core-level control | raw sqlite3 only, Peewee |
| Job queue / scheduler | DB-backed queue tables per `contracts/data/entities.yaml` (assignment, assignment_lease, schedule_occurrence) driven by an in-process scheduler loop (APScheduler not required; a `while` loop with the lease/epoch rules) | contracts already define the queue; a broker would add a second state owner | Celery/Redis, APScheduler |
| Collector | Playwright for Python, persistent context on the project Chrome profile (D09), `httpx` client to server API with bearer token | spec §6.3 recommendation; profile isolation | Selenium |
| Analysis worker | `httpx` to server + provider adapters: API family via provider SDK/httpx; CLI/ACP family via `subprocess` with tool/network flags per `contracts/ai/providers.yaml` | isolation requirements are process-level | LangChain (rejected: hides tool calls) |
| Embedding | `sentence-transformers` (model chosen after A3; multilingual candidate) on the server, vectors stored as BLOB, cosine in Python (D49 linear scan) | local, no key; D59 multilingual | ONNX runtime later if needed |
| Telegram | direct Bot API via `httpx` (sendMessage/webhook), no bot framework | outbox/receipt semantics are ours; a framework's retry would violate B03 | python-telegram-bot |
| Web UI | Vite + React 18 + TypeScript, TanStack Query for the read models, typed API client generated from `openapi.yaml` (openapi-typescript), no UI kit mandated (visual design deliberately open per spec §4) | conventional, generated client keeps wire fidelity | SvelteKit, Next.js |
| Auth | HttpOnly cookie session + CSRF double-submit (PC05/PC08 decision), Argon2id via `argon2-cffi` | already contracted | JWT |
| Tests | Python: `pytest` + fixtures loaded straight from `acceptance/fixtures/**` (E1), `pytest-asyncio`; SQLite fault injection via wrapper; Web: Vitest + Testing Library; E2E: Playwright Test against the server; contract lint: `evidence/tools/e0_check.py` in CI | fixtures are the oracles; no second test data set | — |
| Lint / format | `ruff` (+ format), `mypy --strict` on server core, `eslint` + `prettier`, `PYTHONDONTWRITEBYTECODE` in CI | cheap, standard | — |
| CI | GitHub Actions: E0 job (e0_check + card pin verifier), Python job (pytest E1), web job (vitest), no live jobs (E3/E4 are manual per protocol) | evidence discipline | — |
| Packaging/deploy | Docker Compose for server (web + api + embedding), host processes for collector/worker (spec §6.4), `.env`-free secrets via mounted secret file (PC08) | spec §6.4 | — |

Repo layout (agent-tasks/README.md §5.3 already declares it): `server/` (FastAPI app, domain services by MOD-* ids, migrations), `collector/`, `worker/`, `web/`, `shared/rr_contracts/` (generated models + constants from contracts/), `tests/` (contract, unit, integration), `probe/` (SP1). Each card's §3 paths stay as pinned.

Consequences: generated code from contracts must never be hand-edited (E0 check to add: generated files match contracts hash); any framework change is a new ADR; the Owner may object to any row without affecting contracts.
