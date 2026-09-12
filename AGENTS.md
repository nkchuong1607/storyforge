# StoryForge — Agent Entrypoint

AI coding agents (Cursor, Claude Code, Codex) should read this file first.

## Quick Start

```bash
bash scripts/harness/agent-preflight.sh
make setup    # first time only
make check    # before claiming done
```

## Reading Order

1. **This file** — workflow and pointers
2. **[docs/architecture.md](docs/architecture.md)** — layers, agent pipeline, stack
3. **[docs/domain-model.md](docs/domain-model.md)** — entities, ledgers, settlement
4. **Task-relevant skill** in `skills/*/SKILL.md` (see table below)
5. **Path-scoped rules** in `.cursor/rules/` (auto-applied by Cursor)

## Skill Index

| Task area | Skill |
|-----------|-------|
| Where code goes | `skills/storyforge-architecture/` |
| Bible, settle, canon | `skills/storyforge-domain-canon/` |
| Continuity Gate, auditors | `skills/storyforge-continuity/` |
| Cast, tiers, provisional | `skills/storyforge-characters/` |
| Twists, plants, payoffs | `skills/storyforge-twists/` |
| Psyche, OOC | `skills/storyforge-psychology/` |
| Power ranks, xianxia | `skills/storyforge-power-system/` |
| FastAPI backend | `skills/storyforge-api-python/` |
| Next.js frontend | `skills/storyforge-web-next/` |
| Postgres, migrations | `skills/storyforge-db-design/` |
| UI visual quality | `skills/storyforge-ui-external/` |

## External UI Skills (install on dev machine)

Not vendored in repo. See [docs/agent-setup.md](docs/agent-setup.md):

- `npx skills add https://github.com/Leonxlnx/taste-skill`
- `npx ui-ux-pro-max-cli init --ai cursor`

## Repo Map

```
apps/web/     Next.js (author UI) — stub
apps/api/     FastAPI — stub
docs/         Architecture, domain, roadmap, schema draft
skills/       Portable first-party skills
.cursor/rules/ Cursor rules
scripts/harness/ check.sh, agent-preflight.sh
```

## Hard Rules

- English code; Vietnamese docs/UI copy OK
- No secrets in git
- `make check` must pass before done
- Do not mutate settled canon or ledger history in place
- Bootstrap scope: no full Writer agents or product UI unless task says so

## Docs Index

- [Roadmap](docs/roadmap.md)
- [Schema draft](docs/schema-draft.md)
- [Agent setup](docs/agent-setup.md)
