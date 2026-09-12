# Phase 2 Test Strategy

> Mandatory quality bar for Phase 2 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 1 test strategy](../phase-1/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [continuity-rules.md](./continuity-rules.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (no Testcontainers on GitHub Actions). Owner cost policy — see [quality-gates.md](../../engineering/quality-gates.md).

---

## Test pyramid (Phase 2 additions)

```text
        Integration (API)     ← settle TXN, continuity, cross-tenant
               │
        Unit                  ← rule engine, state diff stub, settle orchestration
               │
        Web (Vitest + MSW)    ← Chapter Editor, Continuity Gate flows
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Continuity rule engine | R1 death violation; R4 staging conflict |
| Override matching | Fingerprint skip on re-run |
| Settle orchestration | Mock repo — verify step order |
| Prose version numbering | `version = max + 1` |
| Chapter status FSM | Invalid transition rejected |
| State diff stub | Name mention → proposal |

**Location:** `apps/api/tests/unit/test_continuity_*.py`, `test_settle_*.py`

### Integration tests (mandatory Phase 2 scenarios)

| # | Scenario |
|---|----------|
| 1 | Create prose version → `word_count` updated |
| 2 | Scene beats CRUD; locked chapter → 409 |
| 3 | `POST continuity-check` sync → report row; status → `reviewing` |
| 4 | FAIL report blocks `POST settle` → 409 |
| 5 | FAIL + override → settle 200 |
| 6 | **Settle atomicity:** force failure mid-TXN → no bible version bump, no ledger |
| 7 | Successful settle → `bible_version_current++`, chapter `locked`, new `bible_versions` row |
| 8 | **Cross-tenant:** user A cannot check/settle user B chapter → 404 |
| 9 | Locked chapter prose POST → 409 |
| 10 | Idempotency-Key duplicate settle → same response, no double ledger |

**Markers:** `@pytest.mark.integration`

**Redis:** Still not required Phase 2 (sync continuity).

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | `app/` including new routers/services |
| Branch | ≥ 80% stretch | continuity + settle modules |

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

---

## Frontend (`apps/web`)

### Component tests (Phase 2 modules)

| Module | Scenarios |
|--------|-----------|
| Chapter Editor | Beats list, prose save, version dropdown, locked banner |
| Continuity Gate | Issue table FAIL/WARN, Mark intentional modal |
| Continuity Gate | Approve & Settle disabled when FAIL unresolved |
| Continuity Gate | State diff panel renders proposals |
| Hub | Chapter row navigates to editor vs gate by status |

**Scope paths:** `components/chapter-editor/**`, `components/continuity-gate/**`, related routes under `app/projects/[projectId]/chapters/**`

### MSW handlers

Extend OpenAPI Phase 2 routes; contract smoke test for:

- `GET/PATCH .../chapters/{id}`
- Beats CRUD
- Prose versions create/list
- Continuity check + latest report
- Overrides create
- Settle

### Coverage policy

| Metric | Gate |
|--------|------|
| Line coverage | ≥ **90%** for Phase 2 modules in [web-screens.md](./web-screens.md) |

---

## CI enforcement

| Job | GHA (`ubuntu-latest`) | Local (agent) |
|-----|----------------------|---------------|
| `make check` | ✅ | ✅ |
| `make validate-specs` | ✅ (via check) | ✅ |
| `make test-api-cov` | ❌ skip | ✅ required before API PR |
| `make test-web-cov` | ❌ skip | ✅ required before web PR |

---

## Cross-tenant isolation test (spec)

```python
@pytest.mark.integration
async def test_cross_tenant_chapter_settle_denied(client, project_b, chapter_b, user_a):
    response = await client.post(
        f"/projects/{project_b.id}/chapters/{chapter_b.id}/settle",
        headers={"X-User-Id": str(user_a.id), "Idempotency-Key": "test-key"},
    )
    assert response.status_code == 404
```

---

## Settle atomicity test (spec)

```python
@pytest.mark.integration
async def test_settle_rollback_on_bible_insert_failure(client, monkeypatch, ...):
    monkeypatch.setattr("app.services.settle.insert_bible_version", _raise)
    before_version = project.bible_version_current
    response = await client.post(f".../settle", ...)
    assert response.status_code >= 500
    assert await get_bible_version_current(project.id) == before_version
    assert await count_ledger_events(chapter.id) == 0
```

---

## What not to test (Phase 2)

- LLM / LiteLLM continuity
- Redis job queue
- Prompt Edit AI loop
- Twist / power / psych rules
- E2E Playwright (Phase 7)

---

## Definition of done (implementation PRs)

- [ ] All Phase 2 unit + integration tests pass locally
- [ ] Coverage ≥ 90% API and Phase 2 web modules
- [ ] Cross-tenant + settle atomicity + FAIL blocks settle tests present
- [ ] `make check` green
- [ ] `make test-api-cov` green locally before PR

---

## Links

- [Phase 1 test strategy](../phase-1/test-strategy.md)
- [quality-gates.md](../../engineering/quality-gates.md)
- [continuity-rules.md](./continuity-rules.md)
