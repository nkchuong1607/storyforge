# Phase 3 Specifications — Progressive Characters + Provisional Inbox

> **Status:** Canonical contract for Phase 3 implementation.  
> **Scope:** Schema, API, web screens, character lifecycle rules, and test strategy only — no feature code in the specs PR.

Phase 3 delivers **large-cast character management** (Kiếm Lai scale): tier model T0–T3, provisional mention inbox, fact extractor v1 (heuristic/rule-based), merge/promote/reject workflow, Characters UI, and **name/alias search v1** for context packs (keyword/ILIKE default; optional pgvector stub documented).

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | `characters` extensions, `character_provisional`, aliases, search indexes, optional pgvector |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract extending Phase 2 (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Examples, merge idempotency, error codes, context-pack subset |
| 4 | [web-screens.md](./web-screens.md) | Characters list + detail + Provisional inbox → endpoint mapping |
| 5 | [test-strategy.md](./test-strategy.md) | Unit + Testcontainers; coverage ≥90% local; merge idempotency |
| 6 | [character-lifecycle.md](./character-lifecycle.md) | T0–T3 rules, extract→approve flow, promote/merge invariants |

---

## MVP Phase 3 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `008`–`010`: extend `characters`, `character_provisional`, alias/search indexes; optional `canon_embeddings` stub |
| Tier model | T0–T3 with manual promote + recurrence **suggest** (never auto T3) |
| Provisional inbox | Extract mentions → pending rows → merge / promote new / reject |
| Fact extractor v1 | Rule/heuristic: name-like tokens, `@mentions`, quoted names; LLM optional later |
| API | Characters CRUD + tier promote; provisional list/merge/reject; extract-from-chapter; alias search / context-pack subset |
| Web | Characters list + detail; Provisional inbox tab/panel; tier badges |
| Search v1 | ILIKE + `aliases` jsonb for context-pack character subset; pgvector documented as optional upgrade |

### Out of scope (Phase 3)

| Item | Deferred to |
|------|-------------|
| Full psych OOC checks | Phase 5 |
| Psyche card editor (full) | Phase 5 — stub tab OK |
| Relationship graph UI | Phase 8+ |
| Twist board | Phase 4 |
| Power system bible | Phase 6 |
| Prompt Edit AI | Phase 6 |
| Neo4j graph | Phase 8+ |
| LLM fact extractor (required) | Optional enhancement — heuristic v1 is canonical |
| Auto-promote to T3 | Never — product rule |
| Ledger writes to provisional IDs | Forbidden — invariant |

---

## Dependencies on Phase 1–2

Phase 3 **requires** Phase 1 and Phase 2 implementation merged:

| Prior artifact | Phase 3 usage |
|----------------|---------------|
| `characters` (T0 list) | Extended with tiers, aliases, status, chapter refs |
| `chapters`, `prose_versions` | Extract source text + `prose_version` pin |
| `scene_beats` | Context-pack scene character hints |
| `ledger_events` | Merge creates canonical `entity_id` only; never provisional |
| Phase 2 settle | Extract may run on draft save or continuity hook; **no ledger on provisional** |
| Phase 2 OpenAPI | Unchanged routes retained; Phase 3 openapi supersedes for character routes |

Do not implement Phase 3 migrations until Phase 2 migrations `004`–`007` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [character-lifecycle.md](./character-lifecycle.md) — product rules (T0–T3, merge flow)
3. [schema.md](./schema.md) — migrations `008`–`010`
4. [openapi.yaml](./openapi.yaml) — route contract
5. [api-contracts.md](./api-contracts.md) — merge idempotency, search semantics
6. [test-strategy.md](./test-strategy.md) — Testcontainers scenarios
7. Skills: `storyforge-characters`, `storyforge-db-design`, `storyforge-api-python`, `storyforge-domain-canon`
8. Product: [04-user-stories.md](../../product/04-user-stories.md) (US-C01, US-C02)

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Characters + Inbox screens
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Wireframes: [05-wireframes.md](../../product/05-wireframes.md) screen **7** (`characters-inbox.png`); psych tab stub per §10

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 3 specs** (this PR) | Platform |
| 2 | `api/phase-3-implementation` — migrations, routers, extractor, search | Backend agent |
| 3 | `web/phase-3-implementation` — Characters list, detail, inbox | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

*(Replaces granular build-plan bullets `db/characters_provisional`, `api/character-tier-promote`, etc. — those become implementation tasks inside PR 2.)*

---

## Canon invariants (Phase 3)

From `storyforge-characters` + `storyforge-domain-canon`:

1. **Canonical UUID stable** — rename updates `display_name` / alias metadata; never change `characters.id`.
2. **No ledger events on provisional IDs** — `character_provisional.id` is not an `ledger_events.entity_id`.
3. **Never auto-promote to T3** — author action or bounded recurrence suggest only.
4. **Merge is idempotent** — duplicate merge request returns same canonical character; provisional → `merged`.
5. **Cross-tenant access** → `404 not_found` (unchanged).
6. **Context packs cap stub count** — scene participants + T3 POV; search ranks by alias match.

---

## Validation

```bash
make validate-specs   # Phase 1 + Phase 2 + Phase 3 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md)
- [Phase 2 specs](../phase-2/README.md)
- [Build plan Phase 3](../../product/06-build-plan.md#phase-3--characters-progressive--provisional-inbox)
- [Schema draft (Phase 4+ tables)](../../schema-draft.md)
- [Domain model](../../domain-model.md)
- [AGENTS.md](../../../AGENTS.md)
