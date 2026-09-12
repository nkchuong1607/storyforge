# StoryForge Roadmap

Phased delivery from harness bootstrap to full author product.

## Phase 0 — Bootstrap (this repo state)

- [x] Monorepo layout, docs, agent skills, Cursor rules
- [x] Harness scripts + CI
- [x] Minimal `apps/web` and `apps/api` stubs
- [x] Docker Compose for Postgres + Redis
- [ ] External UI skills install (developer machine)

## Phase 1 — MVP Core

**Goal:** One project, one chapter, manual bible seed, basic editor, settle loop.

| Item | Deliverable |
|------|-------------|
| Auth + projects | CRUD projects, ACL |
| Bible v1 | Versioned world + character seeds (API + simple UI) |
| Chapter editor | Save prose versions, scene beats list |
| Deterministic continuity | Death, timeline order, location conflicts |
| Settle v1 | State diff preview + approve + ledger append |
| Context pack builder | Beat-scoped pack for future agents |

## Phase 2 — Agent Pipeline

| Item | Deliverable |
|------|-------------|
| LiteLLM integration | Model routing, cost tags |
| Writer + Editor agents | Prompt-edit loop with versioning |
| LLM continuity auditor | Semantic FAIL/WARN |
| Fact extractor | Propose ledger events from prose |
| Job queue | Redis-backed async continuity runs |

## Phase 3 — Cast & Plot Systems

| Item | Deliverable |
|------|-------------|
| Progressive character bible | Tiers, provisional inbox, merge |
| Psyche + PsychState | OOC checks |
| TwistPlan | Plants, payoffs, fairness gate |
| Power system module | Rank ladder, anti-creep rules |
| pgvector retrieval | Bible/snippet search for context packs |

## Phase 4 — Author UX (wireframes)

| Screen | Features |
|--------|----------|
| Chapter Editor | Prompt Edit panel, version compare, beat sidebar |
| Continuity Gate | Issue table, fix-in-editor, intentional marks |
| Bible browser | Characters, world, timeline |
| Twist dashboard | Plant/payoff map |

Defer full UI polish until taste-skill / ui-ux-pro-max installed per `docs/agent-setup.md`.

## Phase 5 — Scale & Export

- Multi-user collaboration
- Git mirror of canon (Markdown/YAML)
- Neo4j optional graph layer
- Export formats (EPUB, DOCX)
- Long-running series optimizations (lazy character depth)

## Non-Goals (bootstrap)

- Full Writer agent implementation
- Production DB migrations beyond schema draft
- Complete Continuity Gate UI
- Payment / billing

## Related

- [Architecture](./architecture.md)
- [Domain model](./domain-model.md)
