.PHONY: setup check api-dev web-dev db-up db-down preflight

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

setup:
	@echo "==> Setting up StoryForge..."
	@test -f .env || cp .env.example .env
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && pip install -q -U pip && pip install -q -e ".[dev]"
	cd apps/web && npm install
	@echo "Setup complete. Run: make check"

check:
	bash scripts/harness/check.sh

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
