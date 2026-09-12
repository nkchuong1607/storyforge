# Agentic Awesome Skills (AAS) — StoryForge Stack

Curated, vendored implementation-craft skills from [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills). This is **not** the full 2000+ catalog — only 20 skills matching StoryForge's Next.js, FastAPI, and PostgreSQL stack.

## Pin

| Field | Value |
|-------|-------|
| Upstream repo | https://github.com/sickn33/agentic-awesome-skills |
| Release | **v17.1.0** |
| Verified commit | `392a9b0133e4c077db5877ba042347c780db4a35` |
| Install path | `vendor/aas-skills/` |
| Manifest | [`aas-stack.json`](../aas-stack.json) (repo root) |
| Wrapper skill | `skills/storyforge-aas-stack/SKILL.md` |

## When to Use AAS vs First-Party Skills

| Layer | Read first | Then (if needed) |
|-------|------------|------------------|
| **Product / canon / ledgers** | `skills/storyforge-*` domain skills | — |
| **StoryForge stack conventions** | `storyforge-api-python`, `storyforge-web-next`, `storyforge-db-design` | Matching AAS skill for general craft |
| **Generic implementation craft** | Relevant AAS skill in `vendor/aas-skills/` | — |

**Rule:** Domain and StoryForge-specific conventions always win. AAS skills add general patterns (FastAPI routing, React hooks, Postgres indexing) but must not override ledger immutability, settle workflows, or project layout in `docs/architecture.md`.

### Overlap examples

| First-party | AAS complement | Who wins for StoryForge |
|-------------|----------------|-------------------------|
| `storyforge-api-python` | `fastapi-pro`, `python-fastapi-development` | First-party for paths, deps, settle transactions; AAS for generic FastAPI craft |
| `storyforge-web-next` | `nextjs-app-router-patterns`, `react-best-practices` | First-party for API client layer, no direct DB; AAS for App Router/React patterns |
| `storyforge-db-design` | `database-design`, `postgres-best-practices` | First-party for append-only ledgers and bible versioning; AAS for general SQL/Postgres tuning |

## Installed Skills (20)

### Next.js / React / TypeScript

| ID | Why |
|----|-----|
| `nextjs-app-router-patterns` | App Router layouts, loading/error boundaries |
| `nextjs-best-practices` | Performance and project structure |
| `react-nextjs-development` | React + Next data fetching and components |
| `react-best-practices` | Hooks, composition, state patterns |
| `typescript-pro` | Strict typing for apps/web |

### FastAPI / Python

| ID | Why |
|----|-----|
| `fastapi-pro` | Advanced routers, deps, async endpoints |
| `fastapi-templates` | Scaffolding reference as API grows |
| `python-fastapi-development` | Models, routes, testing workflow |
| `async-python-patterns` | Async I/O for LLM and DB |
| `python-pro` | Python idioms and typing |
| `python-patterns` | Service-layer design patterns |
| `pydantic-models-py` | Pydantic v2 schemas |
| `backend-dev-guidelines` | Errors, logging, API design |

### Database (PostgreSQL)

| ID | Why |
|----|-----|
| `database-design` | Relational modeling for ledgers |
| `database-architect` | Schema evolution, multi-tenant layout |
| `database-optimizer` | Query plans and index tuning |
| `postgres-best-practices` | Core Postgres conventions |
| `postgresql-optimization` | Deep performance tuning |
| `database-migrations-sql-migrations` | Safe reversible migrations |
| `supabase-postgres-best-practices` | Portable Postgres optimization rules (see note below) |

### Skipped

None — all 20 requested IDs existed upstream at v17.1.0.

### `supabase-postgres-best-practices` note

**Kept.** The skill bundles general Postgres guidance (indexes, query plans, connection pooling, schema design) sourced from Supabase's agent-skills repo. StoryForge uses **plain PostgreSQL** (Docker Compose), not Supabase Auth, Dashboard, or RLS. Agents should apply the portable SQL/performance rules and **ignore** Supabase-specific API sections unless the project adopts Supabase.

## Refresh / Reinstall

Preview:

```bash
npx agentic-awesome-skills@17.1.0 --path vendor/aas-skills \
  --skills nextjs-app-router-patterns,nextjs-best-practices,react-nextjs-development,react-best-practices,typescript-pro,fastapi-pro,fastapi-templates,python-fastapi-development,async-python-patterns,python-pro,python-patterns,pydantic-models-py,backend-dev-guidelines,database-design,database-architect,database-optimizer,postgres-best-practices,postgresql-optimization,database-migrations-sql-migrations,supabase-postgres-best-practices \
  --release 17.1.0 --dry-run
```

Install (after reviewing dry-run):

```bash
npx agentic-awesome-skills@17.1.0 --path vendor/aas-skills \
  --skills <same-comma-list> --release 17.1.0
```

Then update `aas-stack.json` with the new release/commit.

## License & Attribution

Skills are vendored from [agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) (MIT). Individual skills may carry additional upstream attribution in their `SKILL.md` frontmatter (`source`, `license`, `source_repo`). Do not remove upstream attribution files inside `vendor/aas-skills/`.

`supabase-postgres-best-practices` originates from [supabase/agent-skills](https://github.com/supabase/agent-skills) (MIT) via the AAS catalog.
