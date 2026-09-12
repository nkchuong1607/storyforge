# Phase 1 Specifications — StoryForge MVP Foundation

> **Status:** Canonical contract for Phase 1 implementation.  
> **Scope:** Schema, API, web screens, and test strategy only — no feature code in the specs PR.

Phase 1 delivers project isolation, bible staging CRUD, chapter list metadata, and T0 character seeds so an author can create a project, seed canon, and navigate the hub skeleton. Settlement, continuity, and Prompt Edit are **out of scope** for Phase 1 UI/API (stubbed or deferred where noted).

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | Postgres tables, enums, indexes, append-only rules, multi-tenant invariants |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Human-readable companion: examples, status codes, invariants |
| 4 | [web-screens.md](./web-screens.md) | Screen → endpoint mapping, component/data requirements, states |
| 5 | [test-strategy.md](./test-strategy.md) | Unit/integration split, Testcontainers, coverage gates, CI |

---

## MVP Phase 1 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic migrations for `projects`, `project_members`, `bible_versions`, `bible_entry_staging`, `chapters`, `characters` |
| Auth / ACL | `project_members` table; stub auth via `X-User-Id` header; deny cross-tenant access |
| API | Health, projects CRUD + list, bible staging CRUD + version list/get, chapters list (+ optional stub create), characters list (T0) |
| Web | Dashboard, New Project wizard, Project Hub (read-only stats), Story Bible browser (view/edit staging) |

### Out of scope (Phase 1)

| Item | Deferred to |
|------|-------------|
| Bible settle transaction (`bible_version++` from staging) | Phase 2 |
| Continuity Gate UI / API | Phase 2 |
| Chapter Editor, prose versions, scene beats | Phase 2 |
| Prompt Edit panel | Phase 6 |
| Character provisional inbox, tier promote | Phase 3 |
| Twist board, power system bible UI | Phase 4–6 |
| Full-text / vector bible search (⌘K) | Phase 3+ |
| Real OAuth / JWT auth | Post-MVP (ACL table present now) |
| Redis-backed jobs | Phase 2+ (Postgres only for Phase 1 integration tests) |

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [schema.md](./schema.md) — migrations and query invariants
3. [openapi.yaml](./openapi.yaml) — route contract
4. [api-contracts.md](./api-contracts.md) — edge cases and error codes
5. [test-strategy.md](./test-strategy.md) — Testcontainers + coverage gate
6. Skills: `storyforge-db-design`, `storyforge-api-python`, `storyforge-domain-canon`
7. Product context: [04-user-stories.md](../../product/04-user-stories.md) (US-P01–P03, US-H01, US-B01–B02)

### Web agent (`apps/web`)

1. This README — scope boundaries
2. [openapi.yaml](./openapi.yaml) — generate types / MSW handlers from this file
3. [web-screens.md](./web-screens.md) — screen specs and state matrix
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW + coverage gate
6. Skills: `storyforge-web-next`, `storyforge-domain-canon`
7. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screens 1, 2, 4, 6 only

### Both agents

- **Spec-first:** Do not merge implementation PRs that contradict these docs without updating specs first.
- **Parallel safe:** Backend and web may proceed in parallel after this PR merges; web uses OpenAPI + MSW until API is live.
- **Quality gate:** Line coverage ≥ 90% (`apps/api` pytest-cov; Phase 1 UI modules in `apps/web`). See [test-strategy.md](./test-strategy.md) and [quality-gates.md](../../engineering/quality-gates.md).

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 1 specs** (this PR) | Platform |
| 2 | `api/phase-1-implementation` — migrations, routers, Testcontainers tests | Backend agent |
| 3 | `web/phase-1-implementation` — Dashboard, wizard, hub, bible browser | Web agent |

PRs 2 and 3 may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 1)

From `storyforge-domain-canon`:

1. **`bible_versions` rows are immutable** — INSERT only; never UPDATE settled snapshots.
2. **Bible edits in Phase 1 write to `bible_entry_staging` only** — no silent overwrite of settled `snapshot_json`.
3. **Settle endpoint** — documented in OpenAPI as `501 Not Implemented` or omitted; Phase 2 owns the transaction.
4. **Every tenant query filters by `project_id`** — cross-tenant access returns `404` (preferred) or `403`.

---

## Validation

```bash
# OpenAPI YAML parse (no extra deps)
python3 -c "import yaml; yaml.safe_load(open('docs/specs/phase-1/openapi.yaml'))"

# Full harness (must pass on specs PR)
make check
```

---

## Links

- [Build plan Phase 1](../../product/06-build-plan.md#phase-1--schema--migrations--project--bible-crud)
- [Schema draft (superseded for Phase 1)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
