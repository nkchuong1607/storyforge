# Phase 5 Test Strategy

> Mandatory quality bar for Phase 5 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 4 test strategy](../phase-4/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [ooc-rules.md](./ooc-rules.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 5 OpenAPI).

---

## Test pyramid (Phase 5 additions)

```text
        Integration (API)     ← OOC FAIL/WARN, psych immutability, settle append
               │
        Unit                  ← psyche validation, boundary keyword match, arc beat order
               │
        Web (Vitest + MSW)    ← Psyche form, timeline chart, OOC issue display
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Psyche card validation | T3 requires value_hierarchy + moral_boundaries |
| OOC keyword matcher | Boundary phrase near character name → issue |
| Value hierarchy jump | Demote top value without trigger → WARN |
| Arc beat ordering | Skip expected beat → WARN |
| Psych proposal builder | Extract produces trigger_event_refs |
| Immutability guard | settled row → reject UPDATE |
| Tier skip | T0 character → no psychology rules |

**Location:** `apps/api/tests/unit/test_psych_*.py`, `test_ooc_rules.py`

### Integration tests (mandatory Phase 5 scenarios)

| # | Scenario |
|---|----------|
| 1 | `GET/PATCH .../psyche-card` — round-trip merge |
| 2 | PATCH invalid T3 card (empty moral_boundaries) → 422 |
| 3 | **OOC FAIL:** T3 character violates moral boundary in prose → `psych_ooc_moral_boundary_violation` |
| 4 | FAIL + `continuity-overrides` → settle proceeds |
| 5 | FAIL + `arc_flags.allow_moral_break` → WARN or pass |
| 6 | **Value jump:** WARN `psych_value_hierarchy_jump` |
| 7 | **Arc skip:** WARN `psych_arc_beat_skip` |
| 8 | Continuity report includes `psych_state_proposals` in state_diff |
| 9 | Settle with approve_state_diff → `psych_states` row; `psych_states_appended: 1` |
| 10 | Duplicate settle same character+chapter → 409 `psych_state_already_settled` |
| 11 | Attempt PATCH settled psych_state → 409 `psych_state_immutable` |
| 12 | `GET .../psych-states` timeline ordered by chapter |
| 13 | `GET .../psych-states/by-chapter/{id}` — 404 before settle |
| 14 | **Context pack:** `POST .../context-packs/psych` — includes psyche_summary + latest_psych_state |
| 15 | **Cross-tenant:** user A cannot read psych states on project B → 404 |
| 16 | T0 extra kills innocent — no psychology issue |

**Markers:** `@pytest.mark.integration`

### OOC-focused test module

Dedicated file `apps/api/tests/integration/test_phase5_ooc.py`:

- Parameterized moral boundary + override paths
- Asserts issue fingerprints stable for Mark intentional
- Verifies FAIL blocks settle without override

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | `app/` including psych routers, services, ooc rules |
| Branch | ≥ 80% stretch | FAIL vs WARN vs skip tier paths |

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

---

## Frontend (`apps/web`)

### Component tests (Phase 5 modules)

| Module | Scenarios |
|--------|-----------|
| PsycheCardForm | Renders all fields; save PATCH |
| ValueHierarchyEditor | Reorder updates payload |
| MoralBoundariesEditor | T3 validation message |
| PsychStateTimeline | Renders stress line + chapter markers |
| StressBeliefChart | Popover shows belief_updates |
| RelationshipsMinimalList | Trust bars from relationship_lens |
| ContinuityGatePsychIssue | Psychology category badge + Mark intentional |
| API client | `psych.ts` types match OpenAPI |

**MSW handlers:** All Phase 5 routes from [openapi.yaml](./openapi.yaml).

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | Phase 5 paths in [web-screens.md](./web-screens.md) |

```bash
make test-web-cov
```

---

## CI matrix (unchanged policy)

| Job | Specs PR | Implementation PR |
|-----|----------|-------------------|
| `make check` | ✅ required | ✅ required |
| `make validate-specs` | ✅ Phase 1–5 OpenAPI | ✅ if specs touched |
| `make test-api-cov` | **local only** | **local only** |
| `make test-web-cov` | skip | ✅ when web tests exist |

---

## Specs PR validation (this PR)

```bash
make validate-specs   # includes docs/specs/phase-5/openapi.yaml
make check
```

No Testcontainers required for specs-only PR.

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [ooc-rules.md](./ooc-rules.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 4 test strategy](../phase-4/test-strategy.md)
