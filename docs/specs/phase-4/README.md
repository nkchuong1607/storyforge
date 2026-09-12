# Phase 4 Specifications — Twist / Promise Ledger

> **Status:** Canonical contract for Phase 4 implementation.  
> **Scope:** Schema, API, web screens, fairness rules, and test strategy only — no feature code in the specs PR.

Phase 4 delivers **fair twist tracking** via the TwistPlan ledger: author-only `secret_truth`, plants with salience, payoff targets with plant-count gates, **foreshadow continuity** category integration, Writer context packs with **plants-only** strip (never `secret_truth`), and the **Twist Board** Kanban UI.

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | `twist_plans`, `twist_plants`, `twist_payoffs`; indexes; status lifecycle; promise reuse |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract extending Phase 3 (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Examples, board views, continuity codes, context-pack strip |
| 4 | [web-screens.md](./web-screens.md) | Twist Board Kanban + Outline tab stub → endpoint mapping |
| 5 | [test-strategy.md](./test-strategy.md) | Unit + Testcontainers; fairness tests; coverage ≥90% local |
| 6 | [fairness-rules.md](./fairness-rules.md) | Min plants, constrained facts, knowledge walls, intentional overrides |

---

## MVP Phase 4 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `011`–`013`: `twist_plans`, `twist_plants`, `twist_payoffs`; enums; board indexes |
| TwistPlan CRUD | Secrets (author-only), plants, payoffs; status lifecycle `seeded` → `planted` → `armed` → `paid_off` / `abandoned` |
| Promise reuse | `twist_plans.kind = promise` — same tables; no separate promise ledger in Phase 4 |
| Continuity | `foreshadow` category: payoff-without-plants **FAIL**; plant-count gates; unseeded reveal **FAIL** |
| Context packs | `POST .../context-packs/twists` — active plants only; **never** `secret_truth` in Writer role |
| Web | Twist Board Kanban (Secrets / Plants / Payoffs / Revealed); Outline tab light stub |
| Board API | Column-grouped list views for Kanban drag/link UX |

### Out of scope (Phase 4)

| Item | Deferred to |
|------|-------------|
| LLM continuity auditor (foreshadow semantic) | Phase 6+ |
| Prompt Edit AI panel (functional) | Phase 6 |
| Psych / OOC deep checks | Phase 5 |
| Power system rank rules | Phase 6 |
| Full Outline tree + Timeline swimlane | Phase 8+ |
| Neo4j relationship graph | Phase 8+ |
| Auto-extract plants from prose | Optional enhancement — manual registration canonical |
| Public bible export of unrevealed secrets | Forbidden — `storyforge-domain-canon` |

---

## Dependencies on Phase 1–3

Phase 4 **requires** Phase 1, Phase 2, and Phase 3 implementation merged:

| Prior artifact | Phase 4 usage |
|----------------|---------------|
| `projects`, `project_members` | ACL; `genre_profile` drives default strictness |
| `chapters`, `scene_beats` | Plant chapter/beat links; payoff target chapter |
| `continuity_reports`, `continuity_overrides` | Extend engine with `foreshadow` category |
| Phase 2 settle | Payoff chapter continuity runs on draft/reviewing; reveal may bump twist → `paid_off` on settle |
| Phase 3 context packs | Writer pack composes character subset + twist plants strip |
| Phase 3 OpenAPI | Unchanged routes retained; Phase 4 openapi supersedes for twist routes |

Do not implement Phase 4 migrations until Phase 3 migrations `008`–`010` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [fairness-rules.md](./fairness-rules.md) — product rules (gates, overrides, genre strictness)
3. [schema.md](./schema.md) — migrations `011`–`013`
4. [openapi.yaml](./openapi.yaml) — route contract
5. [api-contracts.md](./api-contracts.md) — continuity codes, context-pack strip
6. [test-strategy.md](./test-strategy.md) — Testcontainers fairness scenarios
7. Skills: `storyforge-twists`, `storyforge-continuity`, `storyforge-db-design`, `storyforge-api-python`, `storyforge-domain-canon`
8. Product: [04-user-stories.md](../../product/04-user-stories.md) (US-T01, US-T02)

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Twist Board Kanban
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screen **8** (`outline-twist-board.png`)

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 4 specs** (this PR) | Platform |
| 2 | `api/phase-4-implementation` — migrations `011`–`013`, twist CRUD, continuity foreshadow, context-pack strip | Backend agent |
| 3 | `web/phase-4-implementation` — Twist Board Kanban against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

*(Replaces granular build-plan bullets `db/twist_plans`, `api/twist-crud-continuity`, `web/twist-board` — those become implementation tasks inside PR 2/3.)*

---

## Canon invariants (Phase 4)

From `storyforge-twists` + `storyforge-domain-canon`:

1. **`secret_truth` is author-only** — never in Writer context packs, public bible exports, or agent routes without `role=author|architect`.
2. **Payoff without registered plants → FAIL** unless active `continuity_override` (Mark intentional).
3. **Plants-only for Writer** — context pack `twist_relevant[]` contains plant snippets + ids; no ground truth.
4. **Status transitions are validated** — cannot `paid_off` without payoff row; cannot delete twist with settled plants on locked chapters without abandon flow.
5. **Cross-tenant access** → `404 not_found` (unchanged).
6. **Reveal must not contradict settled ledger** without compensating event (WARN/FAIL per constrained facts).

---

## Validation

```bash
make validate-specs   # Phase 1 + Phase 2 + Phase 3 + Phase 4 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md)
- [Phase 2 specs](../phase-2/README.md)
- [Phase 3 specs](../phase-3/README.md)
- [Build plan Phase 4](../../product/06-build-plan.md#phase-4--twist--promise-ledger)
- [Schema draft (Phase 5+ tables)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
