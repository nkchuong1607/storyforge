# Phase 9 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 8 api-contracts](../phase-8/api-contracts.md) — Phase 1–8 routes unchanged unless noted.

---

## Phase 9 delta summary

| Change | Detail |
|--------|--------|
| New routes | Research notes CRUD, search, links, promote; Series CRUD + attach; Export jobs enqueue/status/download |
| Bible staging | Research promote + series override write `bible_entry_staging` with metadata audit keys |
| Jobs | Redis queue `storyforge:export_jobs`; statuses `pending` / `running` / `done` / `failed` |
| `ContinuityCategory` | Adds **`research`**, **`series`** — **WARN-only** in Phase 9 |
| Continuity codes | Research: `research_link_orphan_*`; Series: `series_parent_slice_updated`, `series_override_without_reason` |
| Settle | Unchanged — research promote and series override still require normal settle for bible version increment |
| Storage | Local artifact dir; `download_url` is relative path to API download route |

---

## Authentication & errors

Unchanged from Phase 1–8: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Note/series/job foreign to tenant |
| 409 | `note_not_editable` | PATCH promoted/archived note |
| 409 | `note_already_promoted` | Second promote without idempotent GET |
| 409 | `project_already_in_series` | Attach project that has `series_id` |
| 409 | `export_job_not_done` | Download while pending/running |
| 409 | `export_job_running` | DELETE while running |
| 422 | `invalid_link_target` | Link type/target mismatch |
| 422 | `invalid_bible_section` | Promote section not allowed |
| 422 | `invalid_export_options` | `selected` scope without chapter_ids |
| 422 | `series_not_attached` | Inherited slice on project without series |

---

## Research

### `POST .../research/notes`

**Request:**

```json
{
  "title": "Lịch sử Huyết Đan trong tông môn",
  "body_md": "Theo **Sử ký Thiên Kiếm**, Huyết Đan chỉ dùng khi...",
  "source_url": "https://example.com/ref",
  "tags": ["cultivation", "sect-history"]
}
```

**201:** `ResearchNote` with `status: active`.

### `GET .../research/notes/search?q=huyết+đan`

**200 example:**

```json
{
  "query": "huyết đan",
  "items": [
    {
      "note": {
        "id": "a1000000-0000-4000-8000-000000000101",
        "project_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Lịch sử Huyết Đan trong tông môn",
        "body_md": "...",
        "tags": ["cultivation"],
        "status": "active",
        "created_at": "2026-09-13T00:00:00Z",
        "updated_at": "2026-09-13T00:00:00Z"
      },
      "rank": 0.82,
      "snippet": "...Huyết Đan chỉ dùng khi..."
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

### `POST .../research/notes/{note_id}/links`

**Request (character):**

```json
{
  "link_type": "character",
  "character_id": "a1000000-0000-4000-8000-000000000001"
}
```

**Request (place):**

```json
{
  "link_type": "place",
  "bible_key": "world.locations.inner_hall"
}
```

### `POST .../research/notes/{note_id}/promote`

**Request:**

```json
{
  "section": "world",
  "title": "Huyết Đan — quy tắc tông môn",
  "content_md": "Theo Sử ký Thiên Kiếm..."
}
```

**200 example:**

```json
{
  "note_id": "a1000000-0000-4000-8000-000000000101",
  "staging_entry_id": "b2000000-0000-4000-8000-000000000201",
  "status": "promoted",
  "message": "Staging entry created — settle separately to commit canon"
}
```

**Side effects:**

1. Insert/update `bible_entry_staging` with `metadata_json.source_research_note_id`
2. Set note `status=promoted`, `promoted_to_staging_id`, `promoted_at`
3. **No** `bible_version++`

**409:** Note already promoted (unless idempotent re-GET returns same staging id).

---

## Series

### `POST /series`

**Request:**

```json
{
  "title": "Thiên Kiếm — bộ ba",
  "slug": "thien-kiem-trilogy",
  "create_hub_project": true,
  "hub_project_title": "Thiên Kiếm — Series Bible Hub"
}
```

**201:** `SeriesDetail` with `hub_project_id`, `slice_version_current: 0`.

### `POST /series/{series_id}/projects`

**Request:**

```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "book_order": 2
}
```

**409:** Project already attached to another series.

### `GET .../projects/{project_id}/series/inherited-slice`

**200 example (child book):**

```json
{
  "project_id": "660e8400-e29b-41d4-a716-446655440001",
  "series_id": "770e8400-e29b-41d4-a716-446655440099",
  "series_title": "Thiên Kiếm — bộ ba",
  "slice_version": 3,
  "last_seen_slice_version": 2,
  "inherited_sections": ["world", "glossary", "style", "power_system"],
  "slice_json": {
    "world": { "rules": { "cultivation_realms": ["Luyện Khí", "Trúc Cơ"] } },
    "glossary": {}
  },
  "read_only": true,
  "drift_warning": true
}
```

### `POST .../projects/{project_id}/series/overrides`

**Request:**

```json
{
  "overrides_series_key": "world.rules.cultivation_realms",
  "section": "world",
  "title": "Cảnh giới — Book 2 extension",
  "content_md": "Book 2 thêm cảnh giới **Kim Đan**...",
  "override_reason": "Book 2 power creep planned"
}
```

**201:** Staging entry with `metadata.series_override: true`.

---

## Export jobs

### `POST .../export/jobs`

**Request (EPUB, settled only):**

```json
{
  "job_type": "epub",
  "options": {
    "chapter_scope": "settled_only",
    "include_bible": true,
    "strip_secrets": true,
    "include_author_notes": false
  }
}
```

**202 example:**

```json
{
  "id": "e1000000-0000-4000-8000-000000000301",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "epub",
  "status": "pending",
  "options": {
    "chapter_scope": "settled_only",
    "include_bible": true,
    "strip_secrets": true
  },
  "artifact_filename": null,
  "download_url": null,
  "created_at": "2026-09-13T01:00:00Z"
}
```

### `GET .../export/jobs/{job_id}` (poll)

**200 done:**

```json
{
  "id": "e1000000-0000-4000-8000-000000000301",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "epub",
  "status": "done",
  "options": { "chapter_scope": "settled_only" },
  "artifact_filename": "thien-kiem-book1.epub",
  "artifact_size_bytes": 245760,
  "download_url": "/projects/550e8400-e29b-41d4-a716-446655440000/export/jobs/e1000000-0000-4000-8000-000000000301/download",
  "result_json": { "chapter_count": 12, "bible_version": 5 },
  "started_at": "2026-09-13T01:00:01Z",
  "finished_at": "2026-09-13T01:00:04Z",
  "created_at": "2026-09-13T01:00:00Z"
}
```

**200 failed:**

```json
{
  "id": "e1000000-0000-4000-8000-000000000301",
  "status": "failed",
  "error_message": "No settled chapters match scope",
  "download_url": null
}
```

### `GET .../export/jobs/{job_id}/download`

- **200:** `Content-Disposition: attachment; filename="..."` binary stream
- **409:** Job not `done`

### Git markdown mirror

**Request:**

```json
{
  "job_type": "git_md_mirror",
  "options": {
    "chapter_scope": "settled_only",
    "git_md_push_stub": true,
    "strip_secrets": true
  }
}
```

**done `result_json` example:**

```json
{
  "chapter_count": 12,
  "bible_version": 5,
  "tree_root": "thien-kiem-book1",
  "push_stub": {
    "remote": "origin",
    "branch": "canon-mirror",
    "status": "skipped_phase9"
  }
}
```

Artifact: `.zip` of markdown tree.

---

## Continuity (WARN-only additions)

Injected during full `POST .../continuity-check` — never block settle with FAIL from these categories.

| code | category | severity | message pattern |
|------|----------|----------|-----------------|
| `research_link_orphan_character` | research | WARN | Note links deleted character |
| `research_link_orphan_bible_key` | research | WARN | Linked bible key missing |
| `series_parent_slice_updated` | series | WARN | Parent slice v{N} > last seen v{M} |
| `series_override_without_reason` | series | WARN | Override staging missing reason |
| `series_inherited_key_conflict` | series | WARN | Staging edits inherited key without override flag |

Authors override via existing `continuity_overrides` flow.

---

## State diff / settle

Phase 9 does **not** add new `state_diff` proposal types. Research promote and series override appear in bible staging; settle merge picks them up via existing Phase 2 staging → snapshot flow.

Optional post-settle hook (implementation detail): enqueue `git_md_mirror` when project setting `auto_mirror_on_settle` enabled — **out of scope** Phase 9 specs default (manual export only).

---

## Links

- [openapi.yaml](./openapi.yaml)
- [research.md](./research.md)
- [series.md](./series.md)
- [export.md](./export.md)
