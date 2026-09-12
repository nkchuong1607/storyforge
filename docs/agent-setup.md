# Agent & Developer Setup

How humans and AI coding agents configure StoryForge for consistent development.

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (for Postgres + Redis)
- Make

## Local Setup

```bash
git clone https://github.com/nkchuong1607/storyforge.git
cd storyforge
make setup      # install deps, copy env example
make db-up      # postgres + redis via docker compose
make check      # harness must pass
```

## External Skills (UI quality)

StoryForge first-party skills cover domain and stack. For **frontend visual quality**, install these third-party skills on your machine (not vendored into the repo):

### taste-skill (anti-slop UI)

Design-taste frontend guidance for landing pages, portfolios, and redesigns.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

Reference: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)

### ui-ux-pro-max-skill

Broader UI/UX patterns and component guidance.

```bash
npx ui-ux-pro-max-cli init --ai cursor
```

For Claude Code or universal agents, see the project's README for alternate init flags.

Reference: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

### Wrapper skill in this repo

`skills/storyforge-ui-external/SKILL.md` reminds agents to install and follow the above before UI work.

## First-Party Skills

Portable skills live in `skills/*/SKILL.md`. Cursor and Claude can load them from this path.

| Skill | Use when |
|-------|----------|
| `storyforge-architecture` | Layer boundaries, monorepo conventions |
| `storyforge-domain-canon` | Bible versioning, settle workflow |
| `storyforge-continuity` | Auditors, PASS/WARN/FAIL |
| `storyforge-characters` | Progressive cast, provisional inbox |
| `storyforge-twists` | TwistPlan fairness |
| `storyforge-psychology` | Psyche cards, earned change |
| `storyforge-power-system` | Cultivation/power ladders |
| `storyforge-api-python` | FastAPI patterns |
| `storyforge-web-next` | Next.js App Router patterns |
| `storyforge-db-design` | Ledger schema, migrations |
| `storyforge-ui-external` | Before UI: install external skills |

## Cursor Rules

Always-on and path-scoped rules in `.cursor/rules/*.mdc`. Agents should read `AGENTS.md` first.

## Agent Workflow

1. Run `bash scripts/harness/agent-preflight.sh`
2. Read docs per task (architecture → domain → relevant skill)
3. Implement with path-scoped rules applied
4. Run `make check` before claiming done

## CI

GitHub Actions runs harness checks and skill frontmatter lint on push/PR.

## Environment Variables

Copy `.env.example` to `.env` after `make setup`. Never commit secrets.
