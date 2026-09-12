.PHONY: setup check validate-specs test-api test-api-cov test-web-cov api-dev web-dev db-up db-down preflight

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

setup:
	@echo "==> Setting up StoryForge..."
	@test -f .env || cp .env.example .env
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && pip install -q -U pip && pip install -q -e ".[dev]"
	cd apps/web && npm install
	@echo "Setup complete. Run: make check"

check:
	bash scripts/harness/check.sh

validate-specs:
	bash scripts/harness/validate-specs.sh

# API tests (implementation PRs: full suite + Testcontainers)
test-api:
	cd apps/api && . .venv/bin/activate && pytest -q

# Coverage gate: line >= 90% (skips gracefully if pytest-cov not installed)
test-api-cov:
	cd apps/api && . .venv/bin/activate && \
	if python -c "import pytest_cov" 2>/dev/null; then \
	  pytest --cov=app --cov-report=term-missing --cov-fail-under=90 -q; \
	else \
	  echo "SKIP: pytest-cov not installed (run: pip install -e '.[dev]')"; \
	fi

# Web coverage gate (implementation PR — requires vitest coverage script)
test-web-cov:
	@if [ -f apps/web/package.json ] && grep -q '"test:coverage"' apps/web/package.json; then \
	  cd apps/web && npm run test:coverage; \
	else \
	  echo "SKIP: apps/web test:coverage script not configured yet"; \
	fi

preflight:
	bash scripts/harness/agent-preflight.sh

api-dev:
	cd apps/api && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

web-dev:
	cd apps/web && npm run dev

db-up:
	docker compose up -d

db-down:
	docker compose down
