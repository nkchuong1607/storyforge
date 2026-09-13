# Phase 9 Test Strategy — Slice 1

> Mandatory quality bar for Phase 9 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 8 test strategy](../phase-8/test-strategy.md).

---

## Principles (unchanged)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), domain rule docs.
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Redis for export jobs** — Testcontainers Redis or `STORYFORGE_EXPORT_SYNC=1` in-process worker for deterministic tests.
4. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
5. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 9 OpenAPI).
6. **No real LLM** — Research module is manual/deterministic; FakeLLM not required Phase 9.
7. **Local artifacts** — Export tests write to temp dir; cleanup in fixture teardown.

---

## Test pyramid (Phase 9 additions)

```text
        Integration (API)     ← promote→staging, series inherit, export job lifecycle, Redis queue
               │
        Unit                  ← FTS query builder, slice merge, EPUB chapter ordering, secret strip
               │
        Web (Vitest + MSW)    ← Research inbox, Series panel, Export poll + download
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Research link validation | character_id required for type=character |
| Promote payload builder | maps note → staging metadata |
| FTS search query | tsquery sanitization |
| Series slice merge | inherited sections overlay read model |
| Override staging metadata | `series_override` flag set |
| Export scope resolver | settled_only filters chapter status |
| Secret strip | removes secret_truth from export payload |
| Git-md tree builder | chapter order by number; frontmatter YAML |
| Job status transitions | pending→running→done valid; running→pending invalid |

**Location:** `apps/api/tests/unit/test_phase9_*.py`

### Integration tests (mandatory Phase 9 scenarios)

| # | Scenario |
|---|----------|
| 1 | `POST .../research/notes` — CRUD round-trip |
| 2 | `POST .../links` character + place — dedupe 409 |
| 3 | `GET .../search?q=` — returns ranked hit |
| 4 | `POST .../promote` — creates staging row; note status promoted |
| 5 | Promote idempotent — second call returns same staging id |
| 6 | Promoted note PATCH → 409 |
| 7 | Continuity check includes `research_link_orphan_*` WARN |
| 8 | `POST /series` — creates hub project optional |
| 9 | Attach/detach child project |
| 10 | `GET inherited-slice` — merged JSON; drift_warning when version ahead |
| 11 | `POST .../series/overrides` — staging with series_override metadata |
| 12 | Continuity `series_parent_slice_updated` WARN — never FAIL |
| 13 | `POST .../export/jobs` epub — 202 pending |
| 14 | Worker processes job → done + artifact_path exists |
| 15 | `GET .../download` — 200 binary when done; 409 when pending |
| 16 | Export `settled_only` skips drafting chapters |
| 17 | Export `include_drafts` includes drafting with marker |
| 18 | `git_md_mirror` — zip contains bible/ + chapters/ tree |
| 19 | `strip_secrets=true` — no secret_truth in output |
| 20 | Failed job — error_message populated |
| 21 | **Cross-tenant:** user A cannot read research note on project B → 404 |
| 22 | Cancel pending job → 204; status cancelled or deleted |

**Markers:** `@pytest.mark.integration`

**Redis:** Start Testcontainers Redis in `conftest.py` Phase 9 fixture, or set `STORYFORGE_EXPORT_SYNC=1` to run worker inline in test process.

### Dedicated test modules

| File | Focus |
|------|-------|
| `test_phase9_research.py` | CRUD, search, promote, links |
| `test_phase9_series.py` | attach, inherit, override, drift WARN |
| `test_phase9_export.py` | job lifecycle, scopes, download |
| `test_phase9_continuity_warn.py` | research + series WARN-only |

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | `app/services/research_*`, `app/services/series_*`, `app/services/export_*`, `app/workers/export_*`, new routers |
| Branch | report only | — |

---

## Frontend (`apps/web`)

### Vitest + MSW (new)

| Component / route | Tests |
|-------------------|-------|
| `ResearchNoteTable` | Renders list; empty state |
| `ResearchNoteDrawer` | Edit save; promoted read-only |
| `ResearchPromoteModal` | Section select; success toast |
| `ResearchSearchBar` | Debounced search MSW |
| `SeriesHubPage` | Book grid; attach modal |
| `SeriesInheritedSlicePanel` | Read-only banner; drift warn |
| `SeriesOverrideModal` | Submits override staging |
| `ExportJobForm` | Scope toggles |
| `ExportJobTable` | Status pills; download link when done |
| `useExportJobPoll` | Polls until done |

**Fixtures:** `tests/fixtures/phase9/*`, `mocks/phase9-handlers.ts`

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | `components/research/*`, `components/series/*`, `components/export/*`, related API clients |

### a11y smoke

- Research inbox route — jest-axe no violations
- Export panel — form labels associated

---

## Specs PR (this PR)

| Job | Specs PR | Implementation PR |
|-----|----------|-------------------|
| `make validate-specs` | ✅ Phase 9 OpenAPI parses | ✅ if specs touched |
| `make check` | ✅ required | ✅ required |
| `make test-api-cov` | skip | ✅ local ≥90% |
| `make test-web-cov` | skip | ✅ local ≥90% |
| Testcontainers | skip | ✅ local |

---

## Environment variables (implementation)

| Variable | Purpose | Test default |
|----------|---------|--------------|
| `STORYFORGE_EXPORT_ARTIFACT_DIR` | Artifact root | temp dir per test session |
| `STORYFORGE_EXPORT_SYNC` | Inline worker (no Redis) | `1` in unit/integration |
| `REDIS_URL` | Queue connection | Testcontainers or memory |

---

## FakeLLM

**Not required** Phase 9 — research is manual promote only. If continuity research WARN uses optional stub hooks, disable in tests.

---

## Links

- [openapi.yaml](./openapi.yaml)
- [schema.md](./schema.md)
- [Quality gates](../../engineering/quality-gates.md)
