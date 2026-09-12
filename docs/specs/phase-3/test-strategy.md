# Phase 3 Test Strategy

> Mandatory quality bar for Phase 3 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 2 test strategy](../phase-2/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [character-lifecycle.md](./character-lifecycle.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 3 OpenAPI).

---

## Test pyramid (Phase 3 additions)

```text
        Integration (API)     ← merge TXN, extract, cross-tenant, idempotency
               │
        Unit                  ← heuristic extractor, tier validation, alias normalize
               │
        Web (Vitest + MSW)    ← Characters list, detail, inbox merge flows
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Heuristic extractor | VI capitalized names; `@mention`; quoted strings; beat summary tokens |
| Extract dedupe | Skip existing display_name; skip pending fingerprint |
| Tier promote validation | T3 requires psyche minimum; reject auto T3 |
| Alias normalization | Case-fold match; append on merge |
| Context pack builder | Cap stubs; POV + T3 priority |
| Search keyword | Prefix match display_name; alias jsonb containment |

**Location:** `apps/api/tests/unit/test_character_*.py`, `test_extractor_*.py`

### Integration tests (mandatory Phase 3 scenarios)

| # | Scenario |
|---|----------|
| 1 | `POST .../characters` create T0; list filter by tier |
| 2 | `PATCH .../characters/{id}` update aliases; canonical id unchanged |
| 3 | `POST .../promote-tier` T0→T1; T2→T3 with psyche → 200; T2→T3 without psyche → 422 |
| 4 | `POST .../extract-characters` on drafting chapter → provisionals created |
| 5 | Extract on locked chapter → 409 |
| 6 | `POST .../provisionals/{id}/merge` into existing → alias appended, status merged |
| 7 | **Merge idempotency:** duplicate merge → 200, `idempotent=true`, no duplicate alias |
| 8 | `POST .../merge` promote new → character row + `merged_from_provisional_id` |
| 9 | `POST .../reject` → status rejected; merge after reject → 409 |
| 10 | **Cross-tenant:** user A cannot merge/extract on project B → 404 |
| 11 | `GET .../characters/search?q=` matches alias |
| 12 | `POST .../context-packs/characters` respects `max_stubs` cap |
| 13 | Verify **no** `ledger_events.entity_id` equals provisional id after merge |

**Markers:** `@pytest.mark.integration`

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | `app/` including character routers/services |
| Branch | ≥ 80% stretch | extractor + merge modules |

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

---

## Frontend (`apps/web`)

### Component tests (Phase 3 modules)

| Module | Scenarios |
|--------|-----------|
| CharacterTable | Renders tier badges; filter changes query params |
| ProvisionalInboxPanel | Pending rows; merge modal; reject |
| CharacterDetail Overview | PATCH save; promote tier button |
| Psych tab stub | Read-only display; Phase 5 banner present |
| Extract button | Calls extract endpoint; navigates to inbox |

**MSW handlers:** All Phase 3 routes from [openapi.yaml](./openapi.yaml).

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | Phase 3 paths in [web-screens.md](./web-screens.md) |

```bash
make test-web-cov
```

---

## CI matrix (unchanged policy)

| Job | Specs PR | Implementation PR |
|-----|----------|-------------------|
| `make check` | ✅ required | ✅ required |
| `make validate-specs` | ✅ Phase 1+2+3 OpenAPI | ✅ if specs touched |
| `make test-api-cov` | **local only** | **local only** |
| `make test-web-cov` | skip | ✅ when web tests exist |

---

## Specs PR validation (this PR)

```bash
make validate-specs   # includes docs/specs/phase-3/openapi.yaml
make check
```

No Testcontainers required for specs-only PR.

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 2 test strategy](../phase-2/test-strategy.md)
