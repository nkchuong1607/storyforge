---
name: storyforge-db-design
description: PostgreSQL schema principles for StoryForge — append-only ledger events, immutable bible versions, indexes, migrations, no silent overwrite of settled state.
---

# StoryForge DB Design Skill

Use when writing migrations, queries, or ledger persistence.

## Read First

- `docs/schema-draft.md`
- `docs/domain-model.md`

## Core Principles

1. **Append-only ledgers** — No UPDATE/DELETE on settled `ledger_events`
2. **Immutable bible versions** — INSERT only into `bible_versions`
3. **Project scoping** — `project_id` on all tenant tables + composite indexes
4. **Settle in one transaction** — Ledger + bible version + chapter status

## Index Guidelines

- `(project_id, entity_type, entity_id, settled_at DESC)` for ledger tail
- `(project_id, version)` UNIQUE on bible_versions
- `(chapter_id, version)` UNIQUE on prose_versions

## pgvector (Phase 3)

Extension enabled in migration; `canon_embeddings` with HNSW index. Embed bible snippets and character aliases.

## Migrations (Alembic)

- One revision per feature
- Never drop ledger columns; deprecate with nullable new fields
- Seed migrations separate from schema

## Query Patterns

- **Current character state** — Latest settled event per entity, not a mutable row
- **Bible at version V** — Single row fetch by `(project_id, version)`
- **Context pack** — Bounded queries with LIMIT; no full-table scans on prose

## Anti-Patterns

- Mutable `characters.status` column without event history
- Updating prose_version in place (always INSERT new version)
- Cross-project JOINs

## Local Dev

`make db-up` starts Postgres 16 + Redis via docker-compose.
