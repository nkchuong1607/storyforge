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
2. **[docs/product/02-architecture.md](docs/product/02-architecture.md)** — canonical architecture (layers, agent pipeline, stack)
3. **[docs/domain-model.md](docs/domain-model.md)** — entities, ledgers, settlement
4. **Task-relevant first-party skill** in `skills/storyforge-*/SKILL.md` (see table below)
5. **Product context** (when building UI or author flows) — [docs/product/README.md](docs/product/README.md), [wireframes](docs/product/05-wireframes.md), [user stories](docs/product/04-user-stories.md), [build plan](docs/product/06-build-plan.md)
6. **AAS stack skill** (optional) — `vendor/aas-skills/<id>/SKILL.md` via [`skills/storyforge-aas-stack/SKILL.md`](skills/storyforge-aas-stack/SKILL.md) and [`aas-stack.json`](aas-stack.json) for generic Next/FastAPI/Postgres craft
7. **Path-scoped rules** in `.cursor/rules/` (auto-applied by Cursor)

**Precedence:** StoryForge domain and stack skills win over vendored AAS skills when they conflict.

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
| AAS stack (Next/FastAPI/DB craft) | `skills/storyforge-aas-stack/` → `vendor/aas-skills/` |

## Vendored AAS Skills

20 curated skills from [agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) v17.1.0 live in `vendor/aas-skills/`. See [docs/aas-selection.md](docs/aas-selection.md) for IDs, rationale, and overlap with first-party skills.

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
vendor/aas-skills/  Vendored AAS implementation-craft skills
aas-stack.json    AAS pin manifest (release, IDs)
.cursor/rules/ Cursor rules
scripts/harness/ check.sh, agent-preflight.sh
```

## Hard Rules

- English code; Vietnamese docs/UI copy OK
- No secrets in git
- `make check` must pass before done
- Do not mutate settled canon or ledger history in place
- Bootstrap scope: no full Writer agents or product UI unless task says so

## Quality workflow (Spec → Implement → Test → Coverage)

1. **Specs first** — API/schema/UI contracts in `docs/specs/phase-N/` before feature code
2. **Implement** — match OpenAPI and schema; domain skills override generic patterns
3. **Tests** — unit + integration (API: Testcontainers Postgres)
4. **Coverage** — line ≥ **90%** hard gate for `apps/api` and phase-scoped web modules

See [docs/engineering/quality-gates.md](docs/engineering/quality-gates.md), [docs/specs/phase-1/README.md](docs/specs/phase-1/README.md), [docs/specs/phase-2/README.md](docs/specs/phase-2/README.md), [docs/specs/phase-3/README.md](docs/specs/phase-3/README.md), [docs/specs/phase-4/README.md](docs/specs/phase-4/README.md), [docs/specs/phase-5/README.md](docs/specs/phase-5/README.md), [docs/specs/phase-6/README.md](docs/specs/phase-6/README.md), and [docs/specs/phase-7/README.md](docs/specs/phase-7/README.md).

## Docs Index

### Product

- [Product docs index](docs/product/README.md)
- [Vision & outcomes](docs/product/01-vision-and-outcomes.md)
- [Architecture (canonical)](docs/product/02-architecture.md)
- [Domain & subsystems](docs/product/03-domain-and-subsystems.md)
- [User stories](docs/product/04-user-stories.md)
- [Wireframes](docs/product/05-wireframes.md)
- [Build plan](docs/product/06-build-plan.md)

### Engineering

- [Architecture stub](docs/architecture.md) → product/02
- [Roadmap stub](docs/roadmap.md) → product/06
- [Schema draft](docs/schema-draft.md) → Phase 1–2 canonical in specs
- [Phase 1 specs (canonical API/schema)](docs/specs/phase-1/README.md)
- [Phase 2 specs (chapter editor, continuity, settle)](docs/specs/phase-2/README.md)
- [Phase 3 specs (progressive characters, provisional inbox)](docs/specs/phase-3/README.md)
- [Phase 4 specs (twist / promise ledger, twist board)](docs/specs/phase-4/README.md)
- [Phase 5 specs (psych state, OOC, psyche card)](docs/specs/phase-5/README.md)
- [Phase 6 specs (power system, genre contracts, Prompt Edit)](docs/specs/phase-6/README.md)
- [Phase 7 specs (UI polish, design system, a11n, i18n)](docs/specs/phase-7/README.md)
- [Quality gates](docs/engineering/quality-gates.md)
- [Agent setup](docs/agent-setup.md)
