# Phase 1 Test Strategy

> Mandatory quality bar for implementation PRs (API + web). Specs PR adds config stubs only.

---

## Principles

1. **Spec-first** — Tests assert behavior defined in [openapi.yaml](./openapi.yaml) and [schema.md](./schema.md).
2. **Real Postgres in integration tests** — [Testcontainers](https://testcontainers.com/) (Python); no mocked DB for integration layer.
3. **Coverage gate** — Line coverage ≥ **90%** hard fail in CI for `apps/api`; Phase 1 UI modules in `apps/web` ≥ **90%**.
4. **Cross-tenant test** — Required integration test; CI fails without it.

---

## Test pyramid (Phase 1)

```text
                    ┌─────────────┐
                    │  E2E (defer)│  Playwright — Phase 7
                    └──────┬──────┘
               ┌───────────┴───────────┐
               │ Integration (API)     │  Testcontainers Postgres + httpx
               └───────────┬───────────┘
        ┌──────────────────┴──────────────────┐
        │ Unit (services, schemas, utils)     │
        └─────────────────────────────────────┘
               ┌───────────────────────────────┐
               │ Web component + MSW tests     │  Vitest + Testing Library
               └───────────────────────────────┘
```

---

## Backend (`apps/api`)

### Unit tests

| Target | Examples |
|--------|----------|
| Pydantic schemas | Valid/invalid `ProjectCreateRequest` |
| Slug generation | Title → slug, conflict suffix |
| ACL helpers | `require_project_access` membership checks |
| Template seed builders | xianxia_starter JSON shape |
| Error mappers | Exception → `ErrorResponse` |

**Location:** `apps/api/tests/unit/`

**Markers:** `@pytest.mark.unit`

### Integration tests (Testcontainers)

| Requirement | Detail |
|-------------|--------|
| Library | `testcontainers[postgres]>=4.0` |
| Image | `postgres:16-alpine` (match docker-compose) |
| Migrations | Run Alembic upgrade head per session/module |
| Client | `httpx.AsyncClient` against FastAPI app |
| Isolation | Transaction rollback or fresh DB per module — pick one pattern, document in conftest |

**Location:** `apps/api/tests/integration/`

**Markers:** `@pytest.mark.integration`

**Mandatory scenarios:**

| # | Scenario |
|---|----------|
| 1 | Health returns 200 without auth |
| 2 | Create project → 201, bible v0 exists, owner membership |
| 3 | List projects scoped to user |
| 4 | Bible staging CRUD does not mutate bible_versions row |
| 5 | List chapters / characters for project |
| 6 | **Cross-tenant:** user A cannot read user B project (404) |
| 7 | Missing `X-User-Id` → 401 |
| 8 | `POST .../bible/settle` → 501 |

**Redis:** Not required Phase 1. Skip Testcontainers Redis until Phase 2 queue work.

### Coverage policy

| Metric | Gate | Tool |
|--------|------|------|
| **Line coverage** | ≥ **90%** | `pytest-cov` — **hard fail** |
| Branch coverage | ≥ 80% stretch | `--cov-branch`; document if below 90% |
| Scope | `app/` package | Omit `tests/`, alembic env |

**Config:** `apps/api/pyproject.toml` `[tool.coverage.run]` and `[tool.coverage.report]`.

**Command:**

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

**Implementation PR:** All tests must pass with gate enabled.

**Specs PR:** Gate documented; `make test-api-cov` skips gracefully if no integration tests yet (see harness).

---

## Frontend (`apps/web`)

### Stack

| Tool | Purpose |
|------|---------|
| Vitest | Test runner (add in implementation PR) |
| `@testing-library/react` | Component tests |
| MSW 2.x | Mock API from OpenAPI |
| `@vitest/coverage-v8` | Coverage |

### Unit / component tests

| Target | Examples |
|--------|----------|
| Dashboard | Empty, loading, populated grid |
| Wizard | Step validation, submit disabled while loading |
| Hub | Chapter table renders statuses |
| Bible | TOC selection, edit save calls PATCH |
| API client | Attaches `X-User-Id` header |

**Location:** `apps/web/**/*.test.tsx` colocated or `apps/web/tests/`

### MSW contract tests

Handlers generated or hand-written from [openapi.yaml](./openapi.yaml). Contract test: smoke call each Phase 1 route against MSW server.

### Coverage policy

| Metric | Gate |
|--------|------|
| Line coverage | ≥ **90%** for Phase 1 modules listed in [web-screens.md](./web-screens.md) |
| Scope | `components/dashboard`, `components/wizard`, `components/hub`, `components/bible`, `lib/api` |

**Command (implementation PR):**

```bash
cd apps/web && npm run test:coverage
```

**Config:** `vitest.config.ts` with `coverage.thresholds.lines: 90`.

---

## CI enforcement

Update `.github/workflows/ci.yml` in **implementation PRs** (not required to fail specs PR):

```yaml
# API
- run: make test-api-cov

# Web (after vitest added)
- run: make test-web-cov
```

**Specs PR CI:** `make check` must stay green (no failing cov gate until tests exist).

### Harness behavior (post-specs)

| Target | Specs PR | After API impl |
|--------|----------|----------------|
| `make test-api` | runs pytest (existing health test) | full suite |
| `make test-api-cov` | skip with message if no `--cov` tests | fail if <90% |
| `make test-web-cov` | skip if script missing | fail if <90% |

---

## Cross-tenant isolation test (spec)

```python
@pytest.mark.integration
async def test_cross_tenant_project_access_denied(client, db, user_a, user_b):
    project_b = await create_project(db, owner=user_b)
    response = await client.get(
        f"/projects/{project_b.id}/bible/entries",
        headers={"X-User-Id": str(user_a.id)},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
```

---

## Test data fixtures

| Fixture | Contents |
|---------|----------|
| `user_a`, `user_b` | Fixed UUIDs |
| `xianxia_project` | Created via POST with template |
| `blank_project` | Minimal seed |

Use factory helpers in `tests/factories.py`; no production secrets.

---

## What not to test (Phase 1)

- Settle transaction logic (Phase 2)
- LLM / LiteLLM calls
- pgvector search
- E2E Playwright (optional smoke later)

---

## Definition of done (implementation PRs)

- [ ] Unit + integration tests pass locally and in CI
- [ ] Testcontainers integration suite runs in CI (Docker available on `ubuntu-latest`)
- [ ] Line coverage ≥ 90% API; ≥ 90% Phase 1 web modules
- [ ] Cross-tenant test present and passing
- [ ] `make check` green

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [openapi.yaml](./openapi.yaml)
- [schema.md](./schema.md)
