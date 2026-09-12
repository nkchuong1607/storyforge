# StoryForge API

FastAPI backend for canon, ledgers, continuity, and agent orchestration.

## Phase 1 scope

- Alembic migrations for projects, bible staging/versions, chapters, characters
- OpenAPI routes under `docs/specs/phase-1/openapi.yaml`
- Auth stub via `X-User-Id` header + `project_members` ACL
- Bible settle returns `501` (Phase 2)

## Develop

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Or from repo root: `make api-dev`

Requires Postgres (`make db-up` from repo root) with `DATABASE_URL` from `.env`.

## Migrations

```bash
cd apps/api
source .venv/bin/activate
alembic upgrade head
```

## Tests (local only)

Integration tests use **Testcontainers** (`postgres:16-alpine`). Docker must be running.

```bash
# From repo root
make test-api        # pytest (unit + integration)
make test-api-cov    # pytest with line coverage gate (>= 90%)
```

GitHub Actions runs the lightweight harness only (`make check`) — not Testcontainers or full coverage.

## Conventions

See `skills/storyforge-api-python/SKILL.md`.
