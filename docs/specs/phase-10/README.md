# Phase 10 Specifications — Real-World Fact Check

> **Status:** Canonical contract for Phase 10 implementation.  
> **Scope:** Schema, API, web screens, provider interfaces, job queue contracts, and test strategy only — no feature code in the specs PR.

Phase 10 delivers **external fact-checking** — verifying chapter claims against outside sources (history, geography, technology, dates, public figures) — **distinct from** the internal **Continuity Gate** (canon, bible, ledgers).

**User priority (2026-09-14):** Real-world fact-check ships **before** genre craft LLM writing packs (Phase 11+).

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [fact-check.md](./fact-check.md) | Claim model, categories, `reality_anchors`, severities, author actions, privacy |
| 2 | [providers.md](./providers.md) | FakeVerifier, HTTP provider interface, rate limits, caching, citation schema |
| 3 | [schema.md](./schema.md) | Tables/migrations sketch (Alembic `028`–`031` after Phase 9 `027`) |
| 4 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract for Phase 10 routes (OpenAPI 3.1) |
| 5 | [api-contracts.md](./api-contracts.md) | Request/response examples, job status, error cases |
| 6 | [web-screens.md](./web-screens.md) | Fact Check panel, project reality settings; i18n `factCheck.*` |
| 7 | [test-strategy.md](./test-strategy.md) | FakeVerifier + Testcontainers ≥90%; Web ≥90% local; no live web in CI |

---

## MVP Phase 10 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `028`–`031`: `fact_check_runs`, `fact_claims`, `fact_citations`, `project_reality_settings` |
| Claim extraction | Deterministic + optional LLM stub from chapter prose + linked research notes; configurable categories |
| Verification jobs | Async Redis queue (export pattern); pluggable providers: FakeVerifier, Wikipedia/Wikidata stub, research-note evidence |
| Fact Check report | Issues with severity, claim span, proposed correction, citations, confidence; author actions |
| Project reality mode | `reality_anchors`: `off` \| `soft` \| `strict` — fantasy can disable; historical fiction uses soft/strict |
| Integration | Separate Fact Check panel; optional WARN-only bridge into Continuity Gate when `strict`; default advisory (never blocks settle) |
| Research link | Promote fact-check citation → research note (Phase 9 module) |
| Web | Fact Check panel on chapter editor; reality settings on project settings; Phase 7 primitives + i18n |

### Out of scope (Phase 11+)

| Item | Deferred to |
|------|-------------|
| Genre craft LLM writing packs (Snowflake, Hero's Journey, style enhancer) | Phase 11+ |
| Neo4j graph backend | Phase 11+ |
| Realtime collaboration / presence | Phase 11+ |
| Paid search APIs as hard dependencies | Phase 11+ |
| Automatic prose rewrite without human apply | Phase 11+ |
| S3 / cloud artifact storage for citation snapshots | Phase 11+ |
| LLM research autofill (Phase 9 deferred) | Phase 11+ (optional overlap) |

---

## Continuity Gate vs Fact Check (boundary)

| Dimension | Continuity Gate | Fact Check |
|-----------|-----------------|------------|
| **Scope** | World-internal: bible, ledgers, character state, twists, psychology, power ranks | Real-world external: dates, places, orgs, tech, historical events, public figures |
| **Source of truth** | Settled canon + append-only ledgers | External providers + author research notes |
| **UI** | Continuity Gate panel (existing) | **Separate** Fact Check panel on chapter editor |
| **Default settle impact** | FAIL blocks settle (Phase 2+) | **Advisory only** — WARN; never blocks settle unless project `fact_check_blocks_settle=true` (default `false`) |
| **Gate bridge** | N/A | When `reality_anchors=strict`, open fact-check issues may surface as **WARN-only** `fact_check` category in Gate — never auto-merged into other categories |
| **Fiction safety** | Intentional overrides per issue | Author marks claim `intentional_fiction` — excluded from FAIL aggregation |
| **Human-in-the-loop** | Override + settle approval | Accept fix → Prompt Edit / staging note; never auto-edit prose |

---

## Dependencies on Phases 1–9

Phase 10 **requires** Phases 1–9 implementation merged:

| Prior artifact | Phase 10 usage |
|----------------|----------------|
| `projects`, ACL | All routes scoped by `project_id` |
| `chapters`, `prose_versions` | Claim extraction input |
| Phase 2 continuity framework | Optional WARN bridge; separate reports |
| Phase 6 Prompt Edit | Accept fix proposal → staging prose edit |
| Phase 7 design system + i18n | Fact Check panel; `factCheck.*` namespace |
| Phase 9 `research_notes` | Evidence store; promote citation → note |
| Phase 9 Redis export pattern | Reuse queue/worker idiom for fact-check jobs |

Do not implement Phase 10 migrations until Phase 9 migrations `024`–`027` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries and Continuity vs Fact Check
2. [fact-check.md](./fact-check.md) — claim lifecycle, author actions, privacy
3. [providers.md](./providers.md) — FakeVerifier, HTTP stub, research evidence
4. [schema.md](./schema.md) — migrations `028`–`031`
5. [openapi.yaml](./openapi.yaml) — route contract
6. [api-contracts.md](./api-contracts.md) — examples, error codes
7. [test-strategy.md](./test-strategy.md) — FakeVerifier, no live HTTP in CI
8. Skills: `storyforge-architecture`, `storyforge-domain-canon`, `storyforge-continuity`, `storyforge-db-design`, `storyforge-api-python`

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Fact Check panel, reality settings
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Phase 7: [design-system.md](../phase-7/design-system.md), [i18n.md](../phase-7/i18n.md)

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.
- **Jobs async:** Fact-check enqueue returns `202` + run id; poll until `done` or `failed`.
- **Human-in-the-loop:** Never auto-edit prose or auto-settle from fact-check results.
- **No live web in CI:** FakeVerifier default; HTTP providers opt-in via env.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 10 specs** (this PR) | Platform |
| 2 | `api/phase-10-implementation` — migrations `028`–`031`, extraction, providers, Redis worker, Testcontainers tests, coverage ≥90% | Backend agent |
| 3 | `web/phase-10-implementation` — Fact Check panel, reality settings against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 10)

From `storyforge-domain-canon` + `storyforge-architecture` + `storyforge-continuity`:

1. **Fact-check is advisory by default** — does not mutate bible versions or ledgers.
2. **Accept fix ≠ settle** — author applies via Prompt Edit or manual edit; normal settle flow unchanged.
3. **Citation snapshots are immutable** — stored at verification time for reproducible reports.
4. **No silent scrape** — HTTP providers only fetch URLs author supplied or public lookup stubs; never scrape private docs.
5. **Fiction-safe** — `intentional_fiction` disposition removes claim from blocking aggregation.
6. **Separate panel** — Fact Check UI distinct from Continuity Gate; bridge is explicit and WARN-only.
7. **Cross-tenant access** → `404 not_found` (unchanged).
8. **Research promote unchanged** — citation → research note creates new note; does not auto-promote to bible staging.

---

## Definition of done (Phase 10)

- [ ] Claim extraction produces typed claims with prose spans from chapter + optional research notes
- [ ] Verification jobs enqueue via Redis; FakeVerifier completes deterministically in tests
- [ ] Report shows issues with severity, citations, proposed corrections; author actions persist
- [ ] `reality_anchors` off/soft/strict filters which claims are verified
- [ ] Promote citation → research note works; link from note back to claim
- [ ] Fact Check panel on chapter editor; reality settings on project settings
- [ ] Continuity bridge: strict mode may WARN in Gate; default never blocks settle
- [ ] `make check` green; `make test-api-cov` / `make test-web-cov` ≥ 90% on scoped modules locally
- [ ] i18n namespace `factCheck.*` documented and wired in web PR

---

## Validation

```bash
make validate-specs   # Phase 1–10 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md) … [Phase 9 specs](../phase-9/README.md)
- [Build plan Phase 10](../../product/06-build-plan.md#phase-10--real-world-fact-check)
- [Domain model](../../domain-model.md)
- [Quality gates](../../engineering/quality-gates.md)
- [AGENTS.md](../../../AGENTS.md)
