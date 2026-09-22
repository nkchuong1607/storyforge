# Phase 11b — Export Harden (DOCX + Git Markdown)

> **Status:** Canonical contract for Phase 11b implementation.  
> **Scope:** Harden Phase 9 export job UX and artifact quality — **not** a format rewrite or new storage layer.  
> **ADR:** [ADR-M0 §5](../../adrs/ADR-M0-storyforge-gap.md)

Phase 11b improves **job polling → downloadable artifact** UX and **DOCX / git-md mirror** quality. EPUB remains shipped; regression tests must keep EPUB working.

---

## In scope

| Area | Deliverable |
|------|-------------|
| Job UX | Enqueue → poll → download; visible **failed** state with `error_message`; **retry** re-enqueues same type + options |
| Defaults | `chapter_scope=settled_only`, `strip_secrets=true` when options omitted |
| DOCX | Valid OOXML zip (Word / Google Docs); XML-escaped text; chapter headings; paragraph breaks |
| Git-md | Phase 9 tree layout; YAML frontmatter; `bible/`, `chapters/`, `manifest.json` |
| Security | No `secret_truth` in artifacts when `strip_secrets=true` (default) |
| Golden | `apps/api/tests/fixtures/golden/export_golden/` + integration test |
| Sync mode | `STORYFORGE_EXPORT_SYNC=1` for deterministic tests (existing Phase 9 env) |

## Out of scope

| Item | Reason |
|------|--------|
| S3 / presigned URLs | Phase 9 local path only |
| Real git push | Stub only (`git_md_push_stub`) |
| New export formats | EPUB/DOCX/git-md only |
| Bible / Continuity / CraftPack seams | Frozen — export reads state only |

---

## Acceptance criteria (QC)

### Job lifecycle UX

1. **Enqueue** — `POST .../export/jobs` returns `202` with job row.
2. **Poll** — UI polls `GET .../jobs/{id}` every ~2s until `done` or `failed`.
3. **Download** — When `done`, download button fetches `GET .../download` and saves `artifact_filename`.
4. **Failed** — Row shows failed badge; `error_message` visible (tooltip or inline).
5. **Retry** — Failed row offers retry; creates a **new** job with same `job_type` + `options`.

### Defaults (API + UI)

| Field | Default | Verification |
|-------|---------|--------------|
| `chapter_scope` | `settled_only` | Drafting chapters excluded unless `include_drafts` |
| `strip_secrets` | `true` | `secret_truth` absent from DOCX, zip, EPUB |

### DOCX quality

- Opens in Microsoft Word and Google Docs without repair prompt.
- Contains `[Content_Types].xml`, `word/document.xml`, `word/styles.xml`.
- Project title as document title; each chapter as heading + prose paragraphs.
- Special XML characters (`&`, `<`, `>`) escaped in text nodes.

### Git-md mirror layout

```text
{project_slug}/
  README.md
  bible/
    world.md
    characters/{slug}.md   # when bible entries exist
    glossary.md
  chapters/
    01-{slug}.md           # YAML frontmatter + markdown body
  manifest.json
```

### EPUB keep-alive

- Existing EPUB builder unchanged in behavior; integration test confirms non-empty `.epub` download.

---

## API surface (unchanged)

Phase 9 export routes remain the contract. See [phase-9/export.md](../phase-9/export.md) and [phase-9/openapi.yaml](../phase-9/openapi.yaml).

| Method | Path | Notes |
|--------|------|-------|
| POST | `/projects/{id}/export/jobs` | Retry = new POST with prior payload |
| GET | `/projects/{id}/export/jobs/{job_id}` | Poll |
| GET | `/projects/{id}/export/jobs/{job_id}/download` | `done` only |

---

## Web touchpoints

| Component | P11b delta |
|-----------|------------|
| `ExportEnqueueButton` | Loading + error feedback |
| `ExportJobTable` | Failed error display; retry action |
| `ExportDownloadLink` | Unchanged — download when `done` |
| `useExportJobPoll` | Stop interval on terminal status |

See [phase-9/web-screens.md](../phase-9/web-screens.md) for base layout.

---

## Golden fixture

Path: `apps/api/tests/fixtures/golden/export_golden/`

| File | Purpose |
|------|---------|
| `scenario.json` | Project title, chapter prose, bible entry with `secret_truth` |
| `expected_paths.json` | Required zip paths for git-md export |
| `expected_manifest.json` | Manifest shape after export |

Integration test seeds a settled chapter, enqueues DOCX + git-md with **empty options**, asserts defaults, downloads artifacts, validates structure and secret stripping.

---

## Test strategy

| Layer | Tests |
|-------|-------|
| Unit | DOCX OOXML parts, XML escape, git-md tree paths, YAML frontmatter |
| Integration | Golden export lifecycle; default options; EPUB regression |
| Web (MSW) | Failed job row + retry; enqueue loading |

Run with `STORYFORGE_EXPORT_SYNC=1` (default in `conftest.py`).

---

## Links

- [Phase 9 export](../phase-9/export.md)
- [Phase 11 README](./README.md)
- [ADR-M0](../../adrs/ADR-M0-storyforge-gap.md)
