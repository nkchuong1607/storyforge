# Phase 4 Test Strategy

> Mandatory quality bar for Phase 4 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 3 test strategy](../phase-3/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [fairness-rules.md](./fairness-rules.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 4 OpenAPI).

---

## Test pyramid (Phase 4 additions)

```text
        Integration (API)     ← fairness FAIL/WARN, context strip, board, cross-tenant
               │
        Unit                  ← status transitions, plant eligibility, genre strictness
               │
        Web (Vitest + MSW)    ← Twist Board Kanban, payoff alert UI, drawer CRUD
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Status transitions | seeded→planted on first plant; armed→paid_off |
| Plant eligibility | Count plants before payoff chapter number |
| Genre strictness | mystery → FAIL; xianxia → WARN for zero plants |
| Required plant ids | Missing id → issue code |
| Context pack builder | Recursive scan: no `secret_truth` key for writer audience |
| Board column mapper | Cards appear in correct columns by status |
| Payoff uniqueness | Second payoff → 422 |

**Location:** `apps/api/tests/unit/test_twist_*.py`, `test_foreshadow_rules.py`

### Integration tests (mandatory Phase 4 scenarios)

| # | Scenario |
|---|----------|
| 1 | `POST .../twists` create secret → status `seeded` |
| 2 | `POST .../twists/{id}/plants` → twist `planted` |
| 3 | `POST .../twists/{id}/payoffs` → twist `armed` |
| 4 | **Fairness:** continuity check on payoff chapter, 0 plants, mystery → FAIL `foreshadow_payoff_without_plants` |
| 5 | Same project `genre_profile=xianxia` → WARN unless twist strict |
| 6 | `min_plants=2`, 1 plant → FAIL/WARN per strictness |
| 7 | `required_plant_ids` invalid uuid → FAIL `foreshadow_required_plants_missing` |
| 8 | FAIL + `continuity-overrides` → settle proceeds |
| 9 | **Context pack:** `POST .../context-packs/twists` audience=writer — assert no `secret_truth` anywhere in JSON |
| 10 | `GET .../twists/board` returns four columns with expected card types |
| 11 | Plant PATCH on locked chapter → 409 |
| 12 | **Cross-tenant:** user A cannot CRUD twist on project B → 404 |
| 13 | Payoff chapter settle → twist `paid_off`, `revealed_at` set |
| 14 | `kind=promise` twist follows same plant/payoff gates |
| 15 | **Unseeded reveal:** armed twist, zero plants, settle attempt → FAIL `foreshadow_unseeded_reveal` |

**Markers:** `@pytest.mark.integration`

### Fairness-focused test module

Dedicated file `apps/api/tests/integration/test_phase4_fairness.py`:

- Parameterized by `genre_profile` and `genre_strictness`
- Asserts issue fingerprints stable for override flow
- Verifies evidence JSON excludes `secret_truth`

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | `app/` including twist routers, services, foreshadow rules |
| Branch | ≥ 80% stretch | fairness strict vs relaxed paths |

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

---

## Frontend (`apps/web`)

### Component tests (Phase 4 modules)

| Module | Scenarios |
|--------|-----------|
| TwistBoardColumns | Renders 4 columns; secret card shows author-only badge |
| PayoffCard | Red border when `fairness.state=fail` |
| TwistDetailDrawer | Create plant; register payoff |
| FairnessCheckPanel | Links to continuity route |
| Outline stub tabs | Twist Board active; Outline/Timeline show stub banner |
| API client | `twists.ts` types match OpenAPI |

**MSW handlers:** All Phase 4 routes from [openapi.yaml](./openapi.yaml).

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | Phase 4 paths in [web-screens.md](./web-screens.md) |

```bash
make test-web-cov
```

---

## CI matrix (unchanged policy)

| Job | Specs PR | Implementation PR |
|-----|----------|-------------------|
| `make check` | ✅ required | ✅ required |
| `make validate-specs` | ✅ Phase 1–4 OpenAPI | ✅ if specs touched |
| `make test-api-cov` | **local only** | **local only** |
| `make test-web-cov` | skip | ✅ when web tests exist |

---

## Specs PR validation (this PR)

```bash
make validate-specs   # includes docs/specs/phase-4/openapi.yaml
make check
```

No Testcontainers required for specs-only PR.

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [fairness-rules.md](./fairness-rules.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 3 test strategy](../phase-3/test-strategy.md)
