# Phase 9 Specifications — Research, Series, Export (Slice 1)

> **Status:** Canonical contract for Phase 9 **Slice 1** implementation.  
> **Scope:** Schema, API, web screens, job queue contracts, and test strategy only — no feature code in the specs PR.

Phase 9 Slice 1 delivers **author workflow modules** deferred from Phase 8:

1. **Research module** — project-scoped research notes; link to characters/places/facts; search; promote → bible **staging** (human approve before settle)
2. **Series projects** — parent `Series` entity; child projects inherit a read-only parent bible slice; explicit inherit/override rules (never silent overwrite)
3. **Export** — async EPUB/DOCX chapter export jobs + Git markdown mirror job (bible + chapters tree); Redis queue; local artifact path / download URL (no real S3 in Phase 9)

**Deferred to Phase 10+:** Neo4j, realtime collaboration, multi-user ACL beyond current stub, LLM research autofill, Outline tree + Timeline swimlane, motif/ending promises UI.

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [research.md](./research.md) | Notes CRUD, links, search, promote-to-staging workflow |
| 2 | [series.md](./series.md) | Series entity, inheritance rules, child overrides, continuity hooks |
| 3 | [export.md](./export.md) | EPUB/DOCX/git-md jobs, Redis worker pattern, artifact delivery |
| 4 | [schema.md](./schema.md) | Tables/migrations sketch (Alembic `024`–`027` after Phase 8 `023`) |
| 5 | [openapi.yaml](./openapi.yaml) | Machine-readable API contract for Phase 9 routes (OpenAPI 3.1) |
| 6 | [api-contracts.md](./api-contracts.md) | Request/response examples, job status, error cases |
| 7 | [web-screens.md](./web-screens.md) | Research inbox/notes UI, Series hub, Export panel; i18n namespaces |
| 8 | [test-strategy.md](./test-strategy.md) | Testcontainers API ≥90%; Web ≥90% local; GHA lightweight; FakeLLM N/A |

---

## MVP Phase 9 Slice 1 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Database | Alembic `024`–`027`: `research_notes`, links, promote audit; `series` + child linkage; `export_jobs` |
| Research API | CRUD notes; link/unlink entities; full-text search; `POST .../promote` → `bible_entry_staging` row |
| Series API | CRUD series; attach/detach child projects; inherit slice read; explicit override staging for child |
| Export API | Enqueue EPUB/DOCX/git-md jobs; poll status; download artifact from local path |
| Jobs | Redis queue (`export_jobs`); statuses `pending` / `running` / `done` / `failed`; worker stub in API process or sidecar |
| Continuity | WARN-only checks for series slice drift and orphaned research links — Gate unchanged for export |
| Web | Research inbox + note detail; Series hub; Export panel on hub/settings; Phase 7 primitives + i18n |
| Storage | Artifacts under configurable local dir (`/tmp/storyforge-exports` or Testcontainers volume) — no S3 |

### Out of scope (Phase 10+)

| Item | Deferred to |
|------|-------------|
| Neo4j graph backend | Phase 10+ |
| Realtime collaboration / presence | Phase 10+ |
| Multi-user ACL beyond Phase 1 stub (invite flows) | Phase 10+ |
| LLM research autofill / citation extraction | Phase 10+ |
| S3 / cloud artifact storage | Phase 10+ |
| Git push to remote (real credentials) | Phase 10+ — stub download zip only |
| Outline tree + Timeline swimlane | Phase 10+ |
| Motif + ending promises UI | Phase 10+ |

---

## Dependencies on Phases 1–8

Phase 9 Slice 1 **requires** Phases 1–8 implementation merged:

| Prior artifact | Phase 9 usage |
|----------------|---------------|
| `projects`, `project_members`, ACL | All routes scoped by `project_id`; series adds optional `series_id` |
| `bible_entry_staging`, `bible_versions` | Research promote writes staging only; series inherit reads settled parent slice |
| `chapters`, `prose_versions` | Export jobs read chapter order + settled/draft filter |
| `characters`, places in bible | Research note links |
| Phase 2 settle | Unchanged; research promote does **not** auto-settle |
| Phase 7 design system + i18n | New screens reuse tokens; chrome in `research.*`, `series.*`, `export.*` |
| Phase 8 modules | No breaking changes; optional WARN if series world rules conflict with child staging |

Do not implement Phase 9 migrations until Phase 8 migrations `020`–`023` exist on the branch.

---

## Reading order for implementers

### Backend agent (`apps/api`)

1. This README — scope boundaries
2. [research.md](./research.md) — promote → staging, not settle
3. [series.md](./series.md) — inheritance + explicit override
4. [export.md](./export.md) — job lifecycle, Redis, artifact paths
5. [schema.md](./schema.md) — migrations `024`–`027`
6. [openapi.yaml](./openapi.yaml) — route contract
7. [api-contracts.md](./api-contracts.md) — examples, error codes
8. [test-strategy.md](./test-strategy.md) — Testcontainers + Redis scenarios
9. Skills: `storyforge-architecture`, `storyforge-domain-canon`, `storyforge-db-design`, `storyforge-api-python`, `storyforge-continuity`
10. Product: [03-domain-and-subsystems.md](../../product/03-domain-and-subsystems.md) §12–§13

### Web agent (`apps/web`)

1. This README
2. [openapi.yaml](./openapi.yaml) — types / MSW
3. [web-screens.md](./web-screens.md) — Research, Series hub, Export panel
4. [api-contracts.md](./api-contracts.md) — request/response shapes
5. [test-strategy.md](./test-strategy.md) — Vitest + MSW coverage
6. Phase 7: [design-system.md](../phase-7/design-system.md), [i18n.md](../phase-7/i18n.md)
7. User stories: US-E01, US-E02 (export); research/series implied in domain §12–§13

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** API and web PRs may run **in parallel** after this PR merges.
- **Quality gate:** Line coverage ≥ 90% locally; GHA runs `make check` only.
- **Jobs async:** Export enqueue returns `202` + job id; poll until `done` or `failed`.
- **Human-in-the-loop:** Research promote → staging; series inherit → read-only until child override staged; settle unchanged.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 9 specs** (this PR) | Platform |
| 2 | `api/phase-9-implementation` — migrations `024`–`027`, research/series/export routes, Redis worker, Testcontainers tests, coverage ≥90% | Backend agent |
| 3 | `web/phase-9-implementation` — Research UI, Series hub, Export panel against OpenAPI | Web agent |

PRs **2** and **3** may run **in parallel** once PR 1 is merged.

---

## Canon invariants (Phase 9 Slice 1)

From `storyforge-domain-canon` + `storyforge-architecture` + `storyforge-continuity`:

1. **Research is non-canon until promoted** — notes live outside `bible_versions`; promote creates/updates `bible_entry_staging` only.
2. **Promote ≠ settle** — author must still run continuity + approve state diff for bible version increment.
3. **Series parent slice is read-only in child** — child never silently overwrites inherited keys; overrides are explicit staging rows flagged `series_override: true`.
4. **Export is derived** — artifacts built from settled snapshots (default) or include drafts when option set; export never mutates canon.
5. **Git mirror is not SoT** — markdown tree is disposable; Postgres + immutable bible versions remain authoritative.
6. **Job artifacts are ephemeral** — local/tmp storage; TTL cleanup job optional in implementation PR.
7. **Cross-tenant access** → `404 not_found` (unchanged).
8. **Continuity Gate** — export/series/research modules must not block settle; new checks are **WARN-only** (see module docs).

---

## Definition of done (Phase 9 Slice 1)

- [ ] Research notes CRUD + search + entity links work; promote creates staging row with audit link
- [ ] Series CRUD; child project shows inherited slice; override creates flagged staging entry
- [ ] Export jobs enqueue via Redis; EPUB/DOCX/git-md complete with downloadable artifact
- [ ] Job status API: pending → running → done/failed with error message on failure
- [ ] `make check` green; `make test-api-cov` / `make test-web-cov` ≥ 90% on scoped modules locally
- [ ] i18n namespaces `research.*`, `series.*`, `export.*` documented and wired in web PR

---

## Validation

```bash
make validate-specs   # Phase 1–9 OpenAPI YAML
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md) … [Phase 8 specs](../phase-8/README.md)
- [Build plan Phase 9](../../product/06-build-plan.md#phase-9--research-series-export-slice-1)
- [Domain model](../../domain-model.md)
- [Quality gates](../../engineering/quality-gates.md)
- [AGENTS.md](../../../AGENTS.md)
