---
name: storyforge-aas-stack
description: Pointer to vendored Agentic Awesome Skills (AAS) for Next.js, FastAPI, and Postgres craft — load after StoryForge domain skills; see aas-stack.json and docs/aas-selection.md.
---

# StoryForge AAS Stack (Wrapper)

Use when you need **general implementation craft** for Next.js, FastAPI, Python, or PostgreSQL — after reading the relevant first-party StoryForge skill.

## Do Not Duplicate

Upstream skill bodies live in **`vendor/aas-skills/`**. Read them directly; do not copy content into first-party skills.

## Manifest & Docs

- **[`aas-stack.json`](../../aas-stack.json)** — pinned release, skill IDs, rationale
- **[`docs/aas-selection.md`](../../docs/aas-selection.md)** — reading order, overlaps, licenses

## Reading Order

1. **StoryForge domain skill** (`storyforge-domain-canon`, `storyforge-continuity`, etc.) for product logic
2. **StoryForge stack skill** (`storyforge-api-python`, `storyforge-web-next`, `storyforge-db-design`) for repo conventions
3. **AAS skill** from `vendor/aas-skills/<id>/SKILL.md` for generic patterns

Domain and StoryForge conventions **always win** over AAS when they conflict.

## Quick Index (v17.1.0)

| Task | First-party | AAS (vendor path) |
|------|-------------|-------------------|
| FastAPI routes, pydantic | `storyforge-api-python` | `fastapi-pro`, `python-fastapi-development`, `pydantic-models-py` |
| Next.js App Router | `storyforge-web-next` | `nextjs-app-router-patterns`, `react-best-practices` |
| Postgres / migrations | `storyforge-db-design` | `database-design`, `postgres-best-practices`, `database-migrations-sql-migrations` |
| TypeScript strictness | `.cursor/rules/typescript.mdc` | `typescript-pro` |
| Async Python / LLM I/O | `storyforge-api-python` | `async-python-patterns` |

Full list: see `aas-stack.json`.

## Refresh

See `docs/aas-selection.md` for reinstall commands when bumping the upstream release.
