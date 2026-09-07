# Research Radar — developer entry points.
#
# Every target here is exactly what the corresponding CI job runs, so "green locally" and
# "green in CI" mean the same thing. Nothing here is live: no target touches X, an AI
# provider or Telegram (ADR-0011, CI row; E3/E4 are manual by protocol).

export PYTHONDONTWRITEBYTECODE := 1

UV  ?= uv
NPM ?= npm

.DEFAULT_GOAL := help
.PHONY: help setup gen gen-check lint test e0 cards openapi ci clean

help:  ## Show this help
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

setup:  ## Install the Python workspace and the web dependencies
	$(UV) sync --all-packages
	cd web && $(NPM) ci

gen:  ## Regenerate everything that is generated from contracts/
	$(UV) run python shared/rr_contracts/generate.py
	cd web && node scripts/generate.mjs

gen-check:  ## Fail if regenerating would change anything (the no-hand-edit gate)
	$(UV) run python shared/rr_contracts/generate.py --check
	cd web && node scripts/generate.mjs --check

lint:  ## ruff + mypy (server core) + eslint + prettier
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run mypy
	cd web && $(NPM) run lint && $(NPM) run typecheck

test:  ## pytest across the Python workspace, then vitest
	$(UV) run pytest
	cd web && $(NPM) test

# e0_check.py's own README says to run it from a scratch directory so Python cannot drop
# __pycache__ beside it. PYTHONDONTWRITEBYTECODE=1 above removes that reason, and running
# from the repo root keeps `--repo .` honest.
e0:  ## E0 static checks over the contract baseline (read-only)
	$(UV) run python evidence/tools/e0_check.py --repo .

cards:  ## Verify every task card's pinned hashes and the two-language layout rule
	$(UV) run python evidence/tools/verify_cards.py --repo .

openapi:  ## Validate contracts/http/openapi.yaml against OpenAPI 3.1
	$(UV) run openapi-spec-validator contracts/http/openapi.yaml

ci: openapi e0 cards gen-check lint test  ## Everything CI runs, in CI's order

clean:  ## Remove tool caches and build output (never touches contracts/ or evidence/)
	rm -rf .mypy_cache .pytest_cache .ruff_cache web/dist
	find . -name '__pycache__' -type d -prune -not -path './.venv/*' -exec rm -rf {} +
