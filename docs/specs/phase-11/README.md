# Phase 11 Specifications — Mystery CraftPack (P11a)

> **Status:** Canonical contract for Phase 11a implementation.  
> **Scope:** P11a = Mystery CraftPack (merged). **P11b** = export harden — see [export-harden.md](./export-harden.md).

Phase 11a delivers **`mystery.fair_play.v1`** as a **new CraftPack domain** distinct from Phase 6 `genre_rule_pack_json`.

**ADR source:** [docs/adrs/ADR-M0-storyforge-gap.md](../../adrs/ADR-M0-storyforge-gap.md)

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [schema.md](./schema.md) | `craft_packs`, `project_craft_packs`, enum extension |
| 2 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract (OpenAPI 3.1) |
| 3 | [api-contracts.md](./api-contracts.md) | Install/activate, continuity codes, context pack |
| 4 | [web-screens.md](./web-screens.md) | Project settings craft pack panel, checklist UI |
| 5 | [test-strategy.md](./test-strategy.md) | Golden MS, FakeLLM ≥90%, regression |
| 6 | [mystery-craft-pack.md](./mystery-craft-pack.md) | Pack JSON schema v1, checklist rules |
| 7 | [export-harden.md](./export-harden.md) | P11b DOCX/git-md UX + quality AC |

---

## MVP Phase 11a scope

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `032`: `craft_packs`, `project_craft_packs`, seed Mystery pack, `craft` continuity category |
| Catalog API | `GET /craft-packs`, `GET /craft-packs/{id}` |
| Project binding | `GET/PATCH .../craft-packs`, install + activate (MVP: one active pack) |
| Continuity | Deterministic checklist → `craft` + `foreshadow` codes; no duplicate plant ledger |
| Context pack | `POST .../context-packs/craft` — beats, open checklist, active clues/misdirections |
| Prompt Edit | Inject craft context slice on instruct/regenerate; **no auto-rewrite** |
| Golden | `apps/api/tests/fixtures/golden/mystery_fair_play/` + web mirror |
| FakeLLM | Craft skill stubs ≥90% coverage on pack modules |

### Out of scope (P11a)

| Item | Deferred |
|------|----------|
| Export harden (DOCX/MD UX) | **P11b** — [export-harden.md](./export-harden.md) |
| Video, Neo4j, multi-model zoo | Non-goals |
| Merge craft into `genre_rule_pack_json` | Forbidden |
| Romance / other craft packs | Future |
| LLM semantic fair-play auditor (beyond soft WARN stub) | Optional flag |

---

## Separation of concerns (StoryMaker freeze)

| Concept | Owns | Does not own |
|---------|------|--------------|
| **Genre rule pack** (P6) | Thresholds, forbidden, module switches | Beat templates, writing skills |
| **Craft pack** (P11a) | Structure beats, checklist, Prompt Edit hooks | Replacing Gate engine; fact check |

Bind via `genre_profile=mystery` + optional `craft_pack_ids[]` on project — **never overwrite** rule pack JSON.

---

## Dependencies

Requires Phase 1–10 merged: TwistPlan/foreshadow (P4), genre rule pack (P6), Prompt Edit (P6), fact-check bridge (P10) unchanged.

---

## Reading order

1. This README
2. [mystery-craft-pack.md](./mystery-craft-pack.md)
3. [schema.md](./schema.md)
4. [api-contracts.md](./api-contracts.md)
5. [test-strategy.md](./test-strategy.md)
6. Skills: `storyforge-twists`, `storyforge-continuity`, `storyforge-domain-canon`

---

## Validation

```bash
make validate-specs   # includes phase-11 OpenAPI
make check
```

---

## Links

- [Phase 6 genre contracts](../phase-6/genre-contracts.md)
- [Phase 4 fairness rules](../phase-4/fairness-rules.md)
- [ADR-M0](../../adrs/ADR-M0-storyforge-gap.md)
- [AGENTS.md](../../../AGENTS.md)
