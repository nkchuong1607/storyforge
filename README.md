# StoryForge

**StoryForge** is an AI-assisted long-form fiction writing system for novels and serial fiction — from xianxia/tu tiên epics to mystery and literary fiction. Canon (Story Bible + append-only ledgers) is the source of truth; prose is versioned and must pass continuity gates before state is settled.

> **Tóm tắt (VI):** StoryForge hỗ trợ viết tiểu thuyết dài với AI, quản lý bible/canon có phiên bản, ledger sự kiện, kiểm tra continuity, và vòng lặp human-in-the-loop trước khi “settle” trạng thái câu chuyện.

## Status

This repository is in **bootstrap phase**: monorepo layout, domain docs, portable agent skills, Cursor rules, dev harness, and minimal app stubs. **Product UI (Chapter Editor, Continuity Gate) is not implemented yet.**

## Stack (planned)

| Layer | Tech |
|-------|------|
| Web | Next.js (TypeScript, App Router) |
| API | FastAPI (Python) |
| Data | PostgreSQL + pgvector, Redis |
| LLM | LiteLLM |
| Mirror | Markdown/YAML Git export of canon (later) |

## Quick Start

```bash
git clone https://github.com/nkchuong1607/storyforge.git
cd storyforge
make setup
make db-up      # optional: Postgres + Redis
make check
```

- API stub: http://localhost:8000/health (`make api-dev`)
- Web stub: http://localhost:3000 (`make web-dev`)

## Documentation

| Doc | Purpose |
|-----|---------|
| [AGENTS.md](./AGENTS.md) | **Start here** if you are an AI coding agent |
| [docs/architecture.md](./docs/architecture.md) | System design, agent pipeline |
| [docs/domain-model.md](./docs/domain-model.md) | Entities, ledgers, settlement |
| [docs/roadmap.md](./docs/roadmap.md) | MVP → later phases |
| [docs/schema-draft.md](./docs/schema-draft.md) | Postgres sketch (not migrated) |
| [docs/agent-setup.md](./docs/agent-setup.md) | External skills, local setup |
| [docs/aas-selection.md](./docs/aas-selection.md) | Vendored AAS stack (Next/FastAPI/Postgres) |

## AI Agent Workflow

1. Run `bash scripts/harness/agent-preflight.sh`
2. Read [AGENTS.md](./AGENTS.md) → relevant docs → `skills/storyforge-*/SKILL.md`
3. For generic Next/FastAPI/Postgres craft, see `skills/storyforge-aas-stack/` → `vendor/aas-skills/`
4. Follow `.cursor/rules/` (Cursor applies these automatically)
5. Run `make check` before finishing

### First-party skills (`skills/`)

Domain and stack skills: architecture, canon, continuity, characters, twists, psychology, power system, API, web, DB design, UI external wrapper, AAS stack pointer.

### Vendored AAS skills (`vendor/aas-skills/`)

20 curated implementation-craft skills (Next.js, FastAPI, Python, PostgreSQL) pinned at v17.1.0. Manifest: [`aas-stack.json`](./aas-stack.json). Details: [docs/aas-selection.md](./docs/aas-selection.md). StoryForge domain skills take precedence.

### External UI skills (install locally)

Not vendored — install on your machine for frontend work:

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
npx ui-ux-pro-max-cli init --ai cursor
```

See [docs/agent-setup.md](./docs/agent-setup.md).

## Repo Layout

```
apps/web/          Next.js placeholder
apps/api/          FastAPI placeholder
docs/              Architecture & domain
skills/            Portable first-party agent skills
vendor/aas-skills/ Vendored AAS stack (20 skills)
aas-stack.json     AAS release pin and skill IDs
.cursor/rules/     Cursor rules
scripts/harness/   check.sh, agent-preflight.sh
packages/shared/   Shared types (future)
```

## License

MIT — see [LICENSE](./LICENSE).
