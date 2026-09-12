# Phase 2 Specifications — Chapter Draft, Continuity Gate, Settle v1

> **Status:** Canonical contract for Phase 2 implementation.  
> **Scope:** Schema, API, web screens, continuity rules, and test strategy only — no feature code in the specs PR.

Phase 2 delivers chapter draft/edit with prose versions and scene beats, **deterministic continuity** (no LLM auditor), Continuity Gate UI, state diff preview, and the **settle v1 transaction** (ledger append + `bible_version++` + chapter lock).

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | New tables, enum migration, indexes, settle transaction rules |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract extending Phase 1 (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Examples, invariants, error codes, settle atomicity |
| 4 | [web-screens.md](./web-screens.md) | Chapter Editor + Continuity Gate → endpoint mapping |
| 5 | [test-strategy.md](./test-strategy.md) | Unit + Testcontainers; coverage ≥90% local; GHA lightweight |
| 6 | [continuity-rules.md](./continuity-rules.md) | Deterministic rules v1 — FAIL vs WARN, override semantics |

---

## MVP Phase 2 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `004`–`007`: `scene_beats`, `prose_versions`, `ledger_events`, `continuity_reports`, `continuity_overrides`; enum `reviewing` |
| Chapter workflow | Status transitions: `planned` → `drafting` → `reviewing` → `settled` / `locked` |
| API | Chapter get/update status; beats CRUD; prose versions list/get/create/compare; continuity check + latest report; overrides; **chapter settle** |
| Continuity | Deterministic rules v1 (death/status, timeline mono, location, bible staging conflicts) — sync MVP OK |
| State diff | Manual + simple extract stub in report or `GET .../state-diff` |
| Settle | Atomic TXN: append ledger, bump `bible_version`, merge staging → snapshot, lock chapter |
| Web | Chapter Editor (beats + prose + versions); Continuity Gate (issue table, Mark intentional, Approve & Settle) |

### Out of scope (Phase 2)

| Item | Deferred to |
|------|-------------|
| LLM continuity auditor | Phase 6+ |
| Prompt Edit AI panel (functional) | Phase 6 — UI stub OK |
| Twist board, plant/payoff rules | Phase 4 |
| Power system rank rules | Phase 6 |
| Psych / OOC deep checks | Phase 5 |
| Provisional auto-extract inbox | Phase 3 — manual state diff OK |
| Redis async continuity queue | Optional post-MVP; sync check is canonical for Phase 2 |
| Real OAuth / JWT | Post-MVP |

---

## Dependencies on Phase 1

Phase 2 **requires** Phase 1 implementation merged:

| Phase 1 artifact | Phase 2 usage |
|------------------|---------------|
| `projects`, `project_members` | ACL unchanged |
| `bible_versions`, `bible_entry_staging` | Settle merges staging → new snapshot |
| `chapters` | Extended with prose/beats FKs; status workflow |
| `characters` | Ledger entity targets for death/location rules |
| Phase 1 OpenAPI routes | Unchanged; Phase 2 openapi supersedes for new routes |

Do not implement Phase 2 migrations until Phase 1 migrations `001`–`003` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [schema.md](./schema.md) — migrations `004`–`007`, settle transaction
3. [continuity-rules.md](./continuity-rules.md) — rule engine contract
4. [openapi.yaml](./openapi.yaml) — route contract
5. [api-contracts.md](./api-contracts.md) — edge cases, atomic settle
6. [test-strategy.md](./test-strategy.md) — Testcontainers scenarios
7. Skills: `storyforge-continuity`, `storyforge-domain-canon`, `storyforge-db-design`, `storyforge-api-python`
8. Product: [04-user-stories.md](../../product/04-user-stories.md) (US-W01–W02, US-CO01–CO03)

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Chapter Editor + Continuity Gate
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screens **3** and **5** (Prompt Edit panel stub only)

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run in parallel after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only (see [test-strategy.md](./test-strategy.md)).

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 2 specs** (this PR) | Platform |
| 2 | `api/phase-2-implementation` — migrations, routers, continuity engine, settle TXN | Backend agent |
| 3 | `web/phase-2-implementation` — Chapter Editor + Continuity Gate | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 2)

From `storyforge-domain-canon` + [continuity-rules.md](./continuity-rules.md):

1. **`bible_versions` rows remain immutable** — settle INSERTs version `N+1` only.
2. **`ledger_events` append-only** — settle sets `settled_at`; never UPDATE payload in place.
3. **FAIL blocks settle** unless every blocking issue has an active `continuity_override`.
4. **`locked` chapters are read-only** — prose, beats, status PATCH return `409 chapter_locked`.
5. **Cross-tenant access** → `404 not_found` (unchanged from Phase 1).
6. **Draft pins bible version** — first save sets `chapters.bible_version_at_draft = projects.bible_version_current`.

---

## Validation

```bash
make validate-specs   # Phase 1 + Phase 2 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md)
- [Build plan Phase 2](../../product/06-build-plan.md#phase-2--chapter-draft--edit-versions--basic-continuity)
- [Schema draft (Phase 3+ tables)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
