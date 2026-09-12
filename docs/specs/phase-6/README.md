# Phase 6 Specifications — Power System + Genre Contracts + Prompt Edit

> **Status:** Canonical contract for Phase 6 implementation.  
> **Scope:** Schema, API, web screens, power rules, genre contracts, prompt-edit contract, and test strategy only — no feature code in the specs PR.

Phase 6 delivers **xianxia anti-creep** (rank ladder, techniques, cultivation ledger on settle), **genre rule packs** (formalized `genre_profile` JSON tuning continuity severity), and **Prompt Edit** (LiteLLM-backed Editor agent with Apply / Regenerate / Compare, defaulting to **FakeLLM** in tests).

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | `power_ranks`, `power_techniques`, cultivation ledger events, `genre_rule_pack`, prompt-edit sessions/turns |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract extending Phase 5 (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Examples, continuity codes, settle extract, LiteLLM env, FakeLLM default |
| 4 | [web-screens.md](./web-screens.md) | Power System bible UI, Prompt Edit panel (replaces stub), genre settings |
| 5 | [test-strategy.md](./test-strategy.md) | Unit + Testcontainers; FakeLLM mock; coverage ≥90% local |
| 6 | [power-rules.md](./power-rules.md) | Deterministic anti-creep rules v1 |
| 7 | [genre-contracts.md](./genre-contracts.md) | Genre promises/forbidden/expected payoffs; continuity tuning |
| 8 | [prompt-edit.md](./prompt-edit.md) | Context pack inputs, LiteLLM interface, Apply/Regenerate/Compare UX |

---

## MVP Phase 6 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `016`–`019`: power system tables, genre rule pack column, prompt-edit tables, ledger event types |
| Power bible API | CRUD staging `power_ranks`, `power_techniques`; GET/PATCH `power-system/settings` |
| Cultivation ledger | `cultivation_change`, `technique_learned`, `resource_consumed` on settle via `state_diff` |
| Continuity | `power_system` category: rank jump without breakthrough FAIL, technique eligibility |
| Genre packs | `GET/PATCH .../genre-rule-pack` — JSON rule pack per project |
| Prompt Edit API | Instruct → proposed prose; Apply / Regenerate / Compare; instruction log |
| LiteLLM | Server-side via env (`LITELLM_*`); **FakeLLM** default for CI/local tests |
| Web | Power System bible (#9); Chapter Editor Prompt Edit panel (functional); genre step/settings |

### Out of scope (Phase 6)

| Item | Deferred to |
|------|-------------|
| Full UI polish, design tokens, dark mode | Phase 7 |
| Neo4j relationship graph | Phase 8+ |
| Export EPUB/DOCX | Phase 8+ |
| Multi-user realtime collab | Phase 8+ |
| LLM continuity auditor (full semantic) | Optional thin note — deterministic first |
| Partial state_diff approval UI | Future — approve-all bundle unchanged |

---

## Dependencies on Phase 1–5

Phase 6 **requires** Phase 1–5 implementation merged:

| Prior artifact | Phase 6 usage |
|----------------|---------------|
| `projects`, `project_members` | ACL; `genre_profile` enum; new `genre_rule_pack_json` |
| `bible_versions`, bible staging | Power system snapshot in `snapshot_json.world.power_system` on settle |
| `chapters`, `scene_beats`, `prose_versions` | Prompt Edit target; `source=ai_editor` versions |
| Phase 2 settle + `ledger_events` | Extend with cultivation event types |
| `continuity_reports`, `continuity_overrides` | Power + genre-tuned foreshadow severity |
| Phase 4 twist framework | Genre pack tunes `foreshadow` strictness (formalized) |
| Phase 5 psych routes | Unchanged; context packs compose with power snippets |
| Phase 5 OpenAPI | Phase 6 openapi supersedes for power/genre/prompt-edit routes |

Do not implement Phase 6 migrations until Phase 5 migrations `014`–`015` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [power-rules.md](./power-rules.md) — deterministic anti-creep
3. [genre-contracts.md](./genre-contracts.md) — rule pack JSON + severity tuning
4. [prompt-edit.md](./prompt-edit.md) — LiteLLM + FakeLLM + safety
5. [schema.md](./schema.md) — migrations `016`–`019`
6. [openapi.yaml](./openapi.yaml) — route contract
7. [api-contracts.md](./api-contracts.md) — examples, error codes
8. [test-strategy.md](./test-strategy.md) — FakeLLM, power FAIL scenarios
9. Skills: `storyforge-power-system`, `storyforge-continuity`, `storyforge-domain-canon`, `storyforge-db-design`, `storyforge-api-python`
10. Product: [04-user-stories.md](../../product/04-user-stories.md) (US-W03, US-PW01, US-PW02)

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Power bible, Prompt Edit panel, genre settings
4. [prompt-edit.md](./prompt-edit.md) — Apply/Regenerate/Compare UX contract
5. [api-contracts.md](./api-contracts.md) — request/response shapes
6. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
7. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screens **3** and **9**

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.
- **LLM default:** Tests use **FakeLLM**; real LiteLLM opt-in via `STORYFORGE_LLM_PROVIDER=litellm` + env keys.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 6 specs** (this PR) | Platform |
| 2 | `api/phase-6-implementation` — migrations `016`–`019`, power routes, genre pack, prompt-edit + FakeLLM, power continuity, settle extract | Backend agent |
| 3 | `web/phase-6-implementation` — Power bible, Prompt Edit panel, genre settings against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 6)

From `storyforge-power-system` + `storyforge-domain-canon` + `storyforge-continuity`:

1. **Power ranks in staging tables** — CRUD on `power_ranks` / `power_techniques`; settled snapshot copied to bible version on settle.
2. **Cultivation ledger append-only** — rank changes commit only via approved `state_diff.ledger_proposals` at settle.
3. **Rank jump without breakthrough** → FAIL (when `power_system` module enabled for genre).
4. **Genre off switch** — non-progression genres disable power checks; mystery strictens foreshadow.
5. **Prompt Edit proposals are draft** — Apply creates `prose_versions` with `source=ai_editor`; no auto-settle.
6. **LiteLLM keys server-side only** — never in repo; FakeLLM for default tests.
7. **Cross-tenant access** → `404 not_found` (unchanged).

---

## Validation

```bash
make validate-specs   # Phase 1–6 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md)
- [Phase 2 specs](../phase-2/README.md)
- [Phase 3 specs](../phase-3/README.md)
- [Phase 4 specs](../phase-4/README.md)
- [Phase 5 specs](../phase-5/README.md)
- [Build plan Phase 6](../../product/06-build-plan.md#phase-6--power-system--genre-contracts)
- [Schema draft (Phase 7+ tables)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
