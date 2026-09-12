---
name: storyforge-web-next
description: Next.js App Router patterns for StoryForge web app — strict TypeScript, API client layer, no direct DB; defer visual design to taste-skill and ui-ux-pro-max.
---

# StoryForge Web (Next.js) Skill

Use when implementing `apps/web/`.

## Before UI Work

Install and follow external skills (see `docs/agent-setup.md`):

1. `npx skills add https://github.com/Leonxlnx/taste-skill`
2. `npx ui-ux-pro-max-cli init --ai cursor`

Or read `skills/storyforge-ui-external/SKILL.md`.

## Stack

- Next.js 15+ App Router
- TypeScript strict mode
- ESLint (next/core-web-vitals)

## Layout

```
apps/web/
  app/              # routes, layouts
  components/       # UI components (future)
  lib/              # api client, utils
```

## Conventions

- Server Components by default; Client Components only when needed
- All canon/ledger access via `apps/api` REST — no secrets in client bundle
- API base URL from `NEXT_PUBLIC_API_URL`
- No `any` without comment justification
- Vietnamese UI strings OK; code identifiers in English

## Wireframe Screens (future, not bootstrap)

- Chapter Editor: beats sidebar, version selector, Prompt Edit panel
- Continuity Gate: issue table, state diff sidebar, settle actions

Implement data hooks against API contracts defined in API skill; mock until endpoints exist.

## Related

- `storyforge-architecture` — web must not call LLM directly
- `storyforge-ui-external`
