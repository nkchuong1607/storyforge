# Phase 8 Specifications — Story Quality (Slice 1)

> **Status:** Canonical contract for Phase 8 **Slice 1** implementation.  
> **Scope:** Schema, API, web screens, deterministic continuity rules, and test strategy only — no feature code in the specs PR.

Phase 8 Slice 1 delivers **story-quality modules** that extend existing chapter / continuity / settle loops:

1. **Scene engine** — beat goal / conflict / outcome lint; scene-level structure checks in Continuity Gate (deterministic first; optional LLM auditor stub)
2. **Relationship arcs** — relationship ledger events + Postgres-backed graph read model (no Neo4j)
3. **Stakes ledger** — act-level escalation tracking; plants into continuity / settle

**Deferred to Phase 9:** Research module, Series projects, Git mirror, EPUB/DOCX export. **Phase 10+:** Neo4j, realtime collaboration.

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [scene-engine.md](./scene-engine.md) | Beat/scene model, lint rules (deterministic), Gate category, API/UI touchpoints |
| 2 | [relationships.md](./relationships.md) | Entities (`Relationship`, `RelationshipEvent`), graph read model, UI, continuity hooks |
| 3 | [stakes.md](./stakes.md) | `StakesLedger` entries, act escalation rules, settle snapshot |
| 4 | [schema.md](./schema.md) | Tables/migrations sketch (Alembic `020`–`023` after Phase 6 `019`) |
| 5 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract for Phase 8 new/changed routes (OpenAPI 3.1) |
| 6 | [api-contracts.md](./api-contracts.md) | Request/response examples, continuity codes, error cases |
| 7 | [web-screens.md](./web-screens.md) | Scene lint panel, Relationship graph, Stakes board; i18n namespaces |
| 8 | [test-strategy.md](./test-strategy.md) | Testcontainers API ≥90%; Web ≥90% local; GHA lightweight; FakeLLM stub |

---

## MVP Phase 8 Slice 1 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `020`–`023`: scene beat structure columns, `relationships` + `relationship_events`, `stakes_ledger_entries`, `act_structure_settings`; ledger enum extensions |
| Scene engine | Extend `scene_beats` with `goal`, `conflict`, `outcome`, `stakes_level`, `pressure_tags`, `pov_character_id`; deterministic lint on continuity check |
| Continuity | New categories: **`scene_structure`**, **`relationship_arc`**, **`stakes`** — FAIL/WARN + overrides unchanged |
| Relationship API | CRUD relationship registry; append `relationship_events` on settle; graph + list read models |
| Stakes API | Act checkpoints CRUD; escalation lint; bible snapshot `world.stakes` on settle |
| Context packs | Progressive slices: `POST .../context-packs/relationships`, `.../stakes` — scene-mentioned edges only |
| Web | Scene lint panel (editor + gate); Relationship graph screen; Stakes board/panel; Phase 7 UI primitives + i18n namespaces |
| LLM stub | Optional scene-structure auditor hook (disabled by default; FakeLLM when enabled in tests) |

### Out of scope (Phase 9+)

| Item | Deferred to |
|------|-------------|
| Research module (notes → bible promote) | Phase 9+ |
| Series / parent bible projects | Phase 9+ |
| Git mirror / markdown export jobs | Phase 9+ |
| Neo4j graph backend | Phase 9+ (Postgres JSON edges sufficient for Slice 1) |
| EPUB / DOCX export | Phase 9+ |
| Realtime collaboration | Phase 9+ |
| Full Outline tree + Timeline swimlane | Phase 9+ (Stakes board is act-level only in Slice 1) |
| Setting-as-pressure subsystem (beyond `pressure_tags` on beats) | Phase 9+ |

---

## Dependencies on Phases 1–7

Phase 8 Slice 1 **requires** Phases 1–7 implementation merged:

| Prior artifact | Phase 8 usage |
|----------------|---------------|
| `projects`, `project_members`, ACL | All new routes scoped by `project_id` |
| `chapters`, `scene_beats`, `prose_versions` | Scene engine extends beats; lint runs on continuity check |
| `characters` | Relationship endpoints; POV on beats; graph nodes |
| Phase 2 settle + `ledger_events` | Relationship + stakes events append on settle |
| `continuity_reports`, `continuity_overrides` | Extend engine with three new categories |
| Phase 5 psyche `relationship_lens` | Complements graph; ledger is SoT for arc history |
| Phase 6 genre rule pack | Tunable strictness for scene/stakes categories |
| Phase 7 design system + i18n | New screens reuse tokens; chrome in `scene.*`, `relationships.*`, `stakes.*` |

Do not implement Phase 8 migrations until Phase 6 migrations `016`–`019` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [scene-engine.md](./scene-engine.md) — deterministic lint rules
3. [relationships.md](./relationships.md) — ledger + graph read model
4. [stakes.md](./stakes.md) — act escalation + settle snapshot
5. [schema.md](./schema.md) — migrations `020`–`023`
6. [openapi.yaml](./openapi.yaml) — route contract
7. [api-contracts.md](./api-contracts.md) — examples, error codes
8. [test-strategy.md](./test-strategy.md) — Testcontainers scenarios
9. Skills: `storyforge-architecture`, `storyforge-domain-canon`, `storyforge-continuity`, `storyforge-db-design`, `storyforge-api-python`
10. Product: [03-domain-and-subsystems.md](../../product/03-domain-and-subsystems.md) §7, §9

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Scene lint panel, Relationship graph, Stakes board
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Phase 7: [design-system.md](../phase-7/design-system.md), [i18n.md](../phase-7/i18n.md)
7. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screens **3**, **10** (extended)

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.
- **Deterministic first:** Same pattern as twist / psych / power continuity categories.
- **Human-in-the-loop settle unchanged:** Gate FAIL/WARN; author approves `state_diff` bundle.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 8 specs** (this PR) | Platform |
| 2 | `api/phase-8-implementation` — migrations `020`–`023`, scene lint, relationship + stakes routes, continuity categories, settle extract | Backend agent |
| 3 | `web/phase-8-implementation` — Scene lint panel, Relationship graph, Stakes board against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 8 Slice 1)

From `storyforge-domain-canon` + `storyforge-continuity` + `storyforge-architecture`:

1. **Relationship history is ledger SoT** — graph UI is derived from settled `relationship_events`; psyche `relationship_lens` is author intent, not history.
2. **Stakes checkpoints append on settle** — act escalation changes commit via approved `state_diff.ledger_proposals` or `stakes_ledger_entries` status updates at settle.
3. **Scene beat structure is staging** — `goal` / `conflict` / `outcome` editable until chapter locked; copied to bible snapshot slice on settle (optional patch).
4. **Continuity categories extend enum** — `scene_structure`, `relationship_arc`, `stakes`; no parallel lint system.
5. **Progressive context** — LLM packs load relationship/stakes slices only for characters/edges mentioned in scene beats or prose token scan.
6. **Neo4j not required** — Postgres adjacency JSON + indexed pair keys suffice for Slice 1 graph queries.
7. **Cross-tenant access** → `404 not_found` (unchanged).

---

## Definition of done (Phase 8 Slice 1)

- [ ] Scene beats support goal/conflict/outcome; lint issues appear in Continuity Gate under `scene_structure`
- [ ] Relationship graph renders from API; settle appends `relationship_change` events
- [ ] Stakes board shows act checkpoints; flat-middle WARN fires deterministically
- [ ] Three new continuity categories active; overrides + settle gate unchanged
- [ ] `make check` green; `make test-api-cov` / `make test-web-cov` ≥ 90% on scoped modules locally
- [ ] i18n namespaces `scene.*`, `relationships.*`, `stakes.*` documented and wired in web PR

---

## Validation

```bash
make validate-specs   # Phase 1–9 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md) … [Phase 7 specs](../phase-7/README.md)
- [Build plan Phase 8](../../product/06-build-plan.md#phase-8--story-quality-slice-1)
- [Domain model](../../domain-model.md)
- [Quality gates](../../engineering/quality-gates.md)
- [AGENTS.md](../../../AGENTS.md)
