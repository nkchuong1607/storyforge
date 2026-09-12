# Phase 5 Specifications — Psych State + OOC

> **Status:** Canonical contract for Phase 5 implementation.  
> **Scope:** Schema, API, web screens, OOC rules, and test strategy only — no feature code in the specs PR.

Phase 5 delivers **earned psychology**: formal `psyche_card` on characters, append-only **`psych_states`** ledger on settle, deterministic **psychology** continuity category (OOC, moral boundary, value hierarchy jump, arc beat skip), **PsychState timeline** UI, and Writer **context packs** with psych snapshots for scene cast.

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | `psyche_card` jsonb schema; `psych_states` table; indexes; immutability |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract extending Phase 4 (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Examples, continuity codes, state_diff psych proposals, context pack |
| 4 | [web-screens.md](./web-screens.md) | Character Psyche tab (replaces stub), PsychState timeline; Relationships minimal |
| 5 | [test-strategy.md](./test-strategy.md) | Unit + Testcontainers; OOC FAIL/WARN; coverage ≥90% local |
| 6 | [ooc-rules.md](./ooc-rules.md) | Deterministic psychology rules v1; earned change; Mark intentional |

---

## MVP Phase 5 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `014`–`015`: formalize `psyche_card`; `psych_states` append-only |
| Psyche card API | `GET/PATCH .../characters/{id}/psyche-card` — structured jsonb |
| PsychState API | Timeline list; get by chapter; read-only after settle |
| Settle extract | `state_diff.psych_state_proposals[]` — author approves before append |
| Continuity | `psychology` category: OOC, moral boundary, value hierarchy jump, arc beat skip |
| Context packs | `POST .../context-packs/psych` — latest psych snapshot per scene character |
| Web | Character detail **Psyche** tab (full editor); **PsychState timeline** chart |

### Out of scope (Phase 5)

| Item | Deferred to |
|------|-------------|
| Power system rank rules | Phase 6 |
| Prompt Edit AI / LiteLLM | Phase 6 |
| Full relationship graph / force-directed view | Phase 8+ |
| LLM psych auditor (voice drift, subtle OOC) | Phase 6+ optional — deterministic first |
| Partial state_diff approval UI | Future — Phase 5 approve-all bundle |
| Neo4j relationship queries | Phase 8+ |

---

## Dependencies on Phase 1–4

Phase 5 **requires** Phase 1–4 implementation merged:

| Prior artifact | Phase 5 usage |
|----------------|---------------|
| `projects`, `project_members` | ACL |
| `characters` (T0–T3, `psyche_card` jsonb) | Psyche card host; T3 gate uses card minimum |
| `chapters`, `scene_beats` | PsychState keyed by `chapter_id`; scene cast resolution |
| Phase 2 settle + `state_diff_json` | Extend extract with `psych_state_proposals` |
| `continuity_reports`, `continuity_overrides` | Psychology category issues + Mark intentional |
| Phase 3 context packs | Compose psych snapshot into Writer pack |
| Phase 4 OpenAPI | Unchanged twist routes; Phase 5 openapi supersedes for psych routes |

Do not implement Phase 5 migrations until Phase 4 migrations `011`–`013` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [ooc-rules.md](./ooc-rules.md) — deterministic psychology rules
3. [schema.md](./schema.md) — migrations `014`–`015`
4. [openapi.yaml](./openapi.yaml) — route contract
5. [api-contracts.md](./api-contracts.md) — continuity codes, settle extract
6. [test-strategy.md](./test-strategy.md) — OOC FAIL/WARN scenarios
7. Skills: `storyforge-psychology`, `storyforge-continuity`, `storyforge-characters`, `storyforge-db-design`, `storyforge-api-python`, `storyforge-domain-canon`
8. Product: [04-user-stories.md](../../product/04-user-stories.md) (US-C03)

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Psyche tab + timeline
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screen **10** (`psych-relationships.png`)

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 5 specs** (this PR) | Platform |
| 2 | `api/phase-5-implementation` — migrations `014`–`015`, psyche/psych routes, psychology continuity, settle extract, context pack | Backend agent |
| 3 | `web/phase-5-implementation` — Psyche tab + PsychState timeline against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 5)

From `storyforge-psychology` + `storyforge-domain-canon`:

1. **`psych_states` is append-only** — no UPDATE/DELETE after `settled_at` is set.
2. **Psyche card changes** — author PATCH or approved extract; not every draft save.
3. **Earned change** — personality/moral shifts need trigger evidence or arc flag; else WARN/FAIL.
4. **Settle commits psych snapshots** only from approved `state_diff.psych_state_proposals`.
5. **Cross-tenant access** → `404 not_found` (unchanged).
6. **Deterministic first** — LLM psych auditor optional later; must not block Phase 5 ship.

---

## Validation

```bash
make validate-specs   # Phase 1–5 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md)
- [Phase 2 specs](../phase-2/README.md)
- [Phase 3 specs](../phase-3/README.md)
- [Phase 4 specs](../phase-4/README.md)
- [Build plan Phase 5](../../product/06-build-plan.md#phase-5--psych-state--ooc)
- [Schema draft (Phase 6+ tables)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
