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

## Vendored AAS Stack (implementation craft)

StoryForge vendors a **curated subset** (20 skills) of [agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) at **v17.1.0** in `vendor/aas-skills/`. This is not the full catalog.

| Resource | Purpose |
|----------|---------|
| [`aas-stack.json`](../aas-stack.json) | Pinned release, skill IDs, rationale |
| [`docs/aas-selection.md`](./aas-selection.md) | Selection details, overlaps, licenses |
| `skills/storyforge-aas-stack/SKILL.md` | Agent entrypoint — when to load AAS vs first-party |

### When to load which

1. **StoryForge domain** (`storyforge-domain-canon`, `storyforge-continuity`, …) — product logic, canon, ledgers
2. **StoryForge stack** (`storyforge-api-python`, `storyforge-web-next`, `storyforge-db-design`) — repo layout and conventions
3. **AAS vendored** (`vendor/aas-skills/<id>/SKILL.md`) — generic Next.js, FastAPI, Python, Postgres patterns

First-party StoryForge skills **win** when they conflict with AAS (e.g. append-only ledgers vs generic CRUD examples).

### Refresh vendored skills

```bash
npx agentic-awesome-skills@17.1.0 --path vendor/aas-skills \
  --skills <ids-from-aas-stack.json> --release 17.1.0 --dry-run
```

See [aas-selection.md](./aas-selection.md) for the full comma-separated ID list.

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
| `storyforge-aas-stack` | Pointer to vendored AAS skills in `vendor/aas-skills/` |

## Cursor Rules

Always-on and path-scoped rules in `.cursor/rules/*.mdc`. Agents should read `AGENTS.md` first.

## Agent Workflow

1. Run `bash scripts/harness/agent-preflight.sh`
2. Read docs per task (architecture → domain → relevant skill)
3. **If building Phase 1+ features:** read [docs/specs/phase-1/README.md](./specs/phase-1/README.md) before code
4. Implement with path-scoped rules applied
5. Run tests + coverage per [quality-gates.md](./engineering/quality-gates.md)
6. Run `make check` before claiming done

### Quality gates summary

| Step | Requirement |
|------|-------------|
| Spec-first | OpenAPI + schema in `docs/specs/` before implementation PRs |
| API integration tests | Testcontainers Postgres |
| Coverage | Line ≥ 90% (`make test-api-cov`, `make test-web-cov`) |
| Isolation | Cross-tenant test required |

## CI

GitHub Actions runs harness checks and skill frontmatter lint on push/PR.

## Environment Variables

Copy `.env.example` to `.env` after `make setup`. Never commit secrets.
