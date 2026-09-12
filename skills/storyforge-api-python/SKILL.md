---
name: storyforge-api-python
description: FastAPI patterns for StoryForge — project scoping, pydantic models, dependency injection, ruff/pytest, and settle transactions.
---

# StoryForge API (Python) Skill

Use when implementing or modifying `apps/api/`.

## Stack

- FastAPI 0.100+
- Python 3.11+
- Ruff (lint + format), pytest
- Alembic for migrations (Phase 1+)

## Project Layout

```
apps/api/
  app/
    main.py           # FastAPI app, routers
    deps.py           # DB session, project ACL
    routers/          # domain routers
    services/         # business logic
    models/           # SQLAlchemy (future)
    schemas/          # Pydantic request/response
  tests/
```

## Conventions

- Type hints on all public functions
- Pydantic v2 models for API boundaries
- `Depends(get_project)` enforces ACL on every project-scoped route
- No bare `except:` — catch specific exceptions
- HTTP errors: `HTTPException` with clear detail codes

## Settle Pattern

Use DB transaction:

```python
async with session.begin():
    append_ledger_events(...)
    create_bible_version(...)
    update_project_version(...)
    mark_chapter_settled(...)
```

Rollback on any failure; idempotency key on settle endpoint (Phase 1).

## Health

`GET /health` returns `{ "status": "ok" }` — used by harness and Docker.

## Testing

- pytest + httpx AsyncClient
- Test files: `tests/test_*.py`
- Run via `make check` or `cd apps/api && pytest`

## Related

- `storyforge-db-design`
- `storyforge-domain-canon`
