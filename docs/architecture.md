# StoryForge Architecture

> **Canonical architecture documentation** lives in the product docs:
>
> **[docs/product/02-architecture.md](./product/02-architecture.md)**

This file is a short index for agents and engineers who expect `docs/architecture.md`.

## Quick reference

| Layer | Technology |
|-------|------------|
| Web | Next.js (App Router, TypeScript) |
| API | FastAPI (Python 3.11+) |
| Database | PostgreSQL + pgvector |
| Cache / queue | Redis |
| LLM | LiteLLM |
| Mirror | Markdown/YAML Git export (later) |

## Core principles

1. Multi-project isolation (`project_id` everywhere)
2. Versioned Story Bible (immutable versions)
3. Append-only ledgers
4. Context packs (never full manuscript dumps)
5. Human-in-the-loop settle (prose → continuity → state diff → approve)
6. Progressive character depth (T0–T3)

## Related

- [Product architecture (full)](./product/02-architecture.md)
- [Domain model](./domain-model.md)
- [Schema draft](./schema-draft.md)
- [Build plan](./product/06-build-plan.md)
- [Wireframes](./product/05-wireframes.md)
- [AGENTS.md](../AGENTS.md)
