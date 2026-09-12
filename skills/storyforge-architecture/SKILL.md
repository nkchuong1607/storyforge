---
name: storyforge-architecture
description: StoryForge monorepo layer boundaries — when to use web vs api vs ledgers vs agents; project isolation and context-pack rules.
---

# StoryForge Architecture Skill

Use when adding features, choosing where code lives, or designing cross-cutting flows.

## Read First

- `docs/architecture.md`
- `AGENTS.md`

## Layer Rules

| Layer | Path | Does | Does NOT |
|-------|------|------|----------|
| Web | `apps/web/` | UI, forms, API client | DB, LLM, ledger writes |
| API | `apps/api/` | REST, ACL, agents, settle txn | React components |
| Ledgers | API + Postgres | Append-only events | In-place canon overwrite |
| Agents | `apps/api/` workers | Stateless generation/audit | Persist without human gate |

## Multi-Project Isolation

Every query and ledger read/write includes `project_id`. Never share bible snapshots across projects.

## Context Packs

Agents receive beat-scoped packs only. Max token budget enforced in API. Include: bible snippets, ledger tail, active twist plants, psych states for scene characters.

## Monorepo Conventions

- Shared types later in `packages/shared/`
- Domain docs in `docs/`, not duplicated in skills
- Small PRs; one concern per change
- Run `make check` before done

## Agent Pipeline Touchpoints

Implement orchestration in API; expose status to web. Continuity runs async (Redis queue in Phase 2).

## Related Skills

- `storyforge-domain-canon` — settle workflow
- `storyforge-api-python` / `storyforge-web-next` — stack patterns
