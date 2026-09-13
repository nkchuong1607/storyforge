# Phase 8 Test Strategy — Slice 1

> Mandatory quality bar for Phase 8 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 7 test strategy](../phase-7/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), domain rule docs.
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 8 OpenAPI).
5. **Deterministic first** — Scene/relationship/stakes continuity tests use fixed fixtures; no real LLM.
6. **FakeLLM** — Optional scene auditor stub only when `llm_auditor_enabled=true` in test module.

---

## Test pyramid (Phase 8 additions)

```text
        Integration (API)     ← scene FAIL/WARN, graph query, stakes flat-middle, settle append
               │
        Unit                  ← pair normalization, act boundary math, lint rule fingerprints
               │
        Web (Vitest + MSW)    ← Scene lint panel, graph list fallback, stakes board columns
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Scene lint rules | missing outcome → FAIL; missing conflict → WARN |
| Beat order validation | duplicate sort_order → FAIL |
| Relationship pair normalize | swap a/b so a < b |
| Intensity running total | baseline + deltas |
| Act boundary resolver | even split vs chapters_per_act JSON |
| Flat middle detector | sliding window in act middle |
| Stakes level validation | 0–5 bounds |
| Context pack caps | max 8 edges, 12 beats |

**Location:** `apps/api/tests/unit/test_scene_*.py`, `test_relationship_*.py`, `test_stakes_*.py`

### Integration tests (mandatory Phase 8 scenarios)

| # | Scenario |
|---|----------|
| 1 | PATCH beat with goal/conflict/outcome — round-trip |
| 2 | PATCH beat completed=true without outcome → 422 (if server validates) or scene-lint FAIL |
| 3 | `POST .../scene-lint` — missing conflict WARN |
| 4 | Continuity check includes `scene_structure` issues |
| 5 | Scene FAIL + override → settle proceeds |
| 6 | `POST .../relationships` — pair normalization + duplicate 409 |
| 7 | `GET .../relationships/graph` — nodes/edges from settled events |
| 8 | **Relationship FAIL:** betrayal keywords without event proposal |
| 9 | Settle with relationship proposal → `relationship_events` + `ledger_events` row |
| 10 | Settled relationship event immutable → 409 |
| 11 | `POST .../stakes/entries` + `GET .../stakes/board` act columns |
| 12 | **Stakes WARN:** flat_middle in act 2 |
| 13 | **Stakes FAIL:** unresolved past act (strict genre pack) |
| 14 | Settle updates `stakes_ledger_entries.status` + bible `world.stakes` |
| 15 | Context pack relationships — only scene cast edges |
| 16 | Context pack stakes — current act checkpoints only |
| 17 | **Cross-tenant:** user A cannot read relationships on project B → 404 |
| 18 | Optional FakeLLM scene auditor — returns fixture WARN, no FAIL alone |

**Markers:** `@pytest.mark.integration`

### Dedicated test modules

| File | Focus |
|------|-------|
| `test_phase8_scene_lint.py` | S1–S7 rules + fingerprints |
| `test_phase8_relationships.py` | Graph + settle + immutability |
| `test_phase8_stakes.py` | Board + flat middle + snapshot |
| `test_phase8_scene_llm_stub.py` | FakeLLM auditor disabled by default |

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | `app/services/scene_*`, `app/services/relationship_*`, `app/services/stakes_*`, new routers |
| Branch | report only | — |

---

## Frontend (`apps/web`)

### Vitest + MSW (new)

| Component / route | Tests |
|-------------------|-------|
| `SceneBeatStructureFields` | Renders goal/conflict/outcome; shows lint badge |
| `SceneLintPanel` | Groups issues by beat_key |
| `RelationshipGraphList` | a11y fallback renders edges |
| `RelationshipGraphFilters` | act filter calls graph API with params |
| `StakesBoard` | Renders act columns from fixture |
| `StakesCheckpointCard` | Status pill i18n keys |
| `StakesHubBadge` | Shows when continuity fixture has stakes WARN |
| Continuity Gate | New category filter chips |

### jest-axe (extend Phase 7 smoke routes)

Add to smoke list:

- `/projects/[id]/relationships/graph` (list fallback mode)
- `/projects/[id]/stakes`

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | `apps/web/app/**/relationships/**`, `**/stakes/**`, scene lint components under chapter editor |

Config path TBD in implementation PR — mirror Phase 7 `vitest.config.ts` coverage include globs.

---

## CI vs local

| Command | GHA (specs PR) | GHA (impl PR) | Local (impl PR) |
|---------|----------------|---------------|-----------------|
| `make check` | ✅ | ✅ | ✅ |
| `make validate-specs` | ✅ Phase 1–8 OpenAPI | ✅ if specs touched | ✅ |
| `make test-api-cov` | skip | skip | ✅ required |
| `make test-web-cov` | skip | skip | ✅ required |

---

## Fixtures

| File | Purpose |
|------|---------|
| `tests/fixtures/scene_lint_warn.json` | Scene-lint API response |
| `tests/fixtures/relationship_graph.json` | Graph endpoint |
| `tests/fixtures/stakes_board.json` | Board columns |
| `tests/fixtures/scene_llm_audit.json` | FakeLLM auditor output |

Web mirrors under `apps/web/tests/fixtures/phase8/`.

---

## Agent checklist (Phase 8 implementation)

1. Read [README.md](./README.md) + domain docs
2. Implement migrations `020`–`023` before routes
3. Wire continuity categories into existing engine pipeline
4. Run `make test-api-cov` locally — ≥ 90%
5. Run `make test-web-cov` locally — ≥ 90% on scoped paths
6. Run `make check`
7. Update specs first if contract drift

---

## Validation (specs PR)

```bash
make validate-specs   # includes docs/specs/phase-8/openapi.yaml
make check
```

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [Phase 6 test strategy](../phase-6/test-strategy.md)
