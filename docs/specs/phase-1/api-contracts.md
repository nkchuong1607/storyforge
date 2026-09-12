# Phase 1 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.

---

## Authentication (MVP stub)

| Header | Required | Value |
|--------|----------|-------|
| `X-User-Id` | Yes (except `/health`) | UUID string |

Missing header → `401`:

```json
{
  "error": {
    "code": "unauthorized",
    "message": "X-User-Id header is required"
  }
}
```

Phase 2+ may replace with JWT; `project_members.user_id` remains the ACL key.

---

## Error model

All non-2xx responses use:

```json
{
  "error": {
    "code": "string",
    "message": "Human-readable summary",
    "details": []
  }
}
```

| HTTP | code | When |
|------|------|------|
| 400 | `validation_error` | Pydantic / business validation |
| 401 | `unauthorized` | Missing `X-User-Id` |
| 404 | `not_found` | Project/resource missing **or** user lacks membership |
| 409 | `slug_conflict` / `entry_key_conflict` / `chapter_number_conflict` | Unique constraint |
| 501 | `not_implemented` | `POST .../bible/settle` in Phase 1 |

**Cross-tenant rule:** User A requesting User B's `project_id` → `404 not_found` (not `403`).

---

## Pagination

Query: `page` (default 1), `page_size` (default 20, max 100).

Response envelope:

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 42,
    "total_pages": 3
  }
}
```

List endpoints: `GET /projects`, bible entries/versions, chapters, characters.

---

## Health

### `GET /health`

No auth.

**200:**

```json
{ "status": "ok" }
```

---

## Projects

### `GET /projects`

List projects where caller is `project_members.user_id`.

| Query | Default | Notes |
|-------|---------|-------|
| `status` | `active` | Use `archived` to include archived |
| `q` | — | Title substring search |

**200 example:**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "slug": "kiem-lai",
      "title": "Kiếm Lai",
      "description": "Kiếm hiệp tu tiên",
      "language": "vi",
      "genre_profile": "xianxia",
      "template": "xianxia_starter",
      "status": "active",
      "bible_version_current": 0,
      "progress_percent": 0,
      "updated_at": "2026-09-12T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 }
}
```

### `POST /projects`

Wizard submit — creates project + owner membership + bible v0 + template seeds.

**Request:**

```json
{
  "title": "Kiếm Lai",
  "description": "Hành trình tu tiên",
  "language": "vi",
  "genre_profile": "xianxia",
  "template": "xianxia_starter"
}
```

**201:** `ProjectDetail` with `chapter_count`, `bible_entry_count`.

**409 slug conflict:**

```json
{
  "error": {
    "code": "slug_conflict",
    "message": "Slug 'kiem-lai' already exists",
    "details": [{ "suggested_slug": "kiem-lai-2" }]
  }
}
```

**Invariants:**

- Single transaction: project, member, bible v0, staging seeds.
- `bible_version_current` = 0.
- Creator auto-added as `owner`.

**Idempotency:** Not required Phase 1. Client should disable double-submit on wizard Confirm.

### `GET /projects/{project_id}`

**200:** Full `ProjectDetail`.

**404:** Not member or unknown id.

### `PATCH /projects/{project_id}`

**Request (partial):**

```json
{
  "title": "Kiếm Lai — bản mới",
  "description": null,
  "status": "archived"
}
```

**200:** Updated detail. Slug is **immutable** in Phase 1.

### `DELETE /projects/{project_id}`

Soft archive (`status = archived`). **204** empty body.

---

## Bible (staging + versions)

### Canon invariants

1. **Staging writes** → `bible_entry_staging` only.
2. **`bible_versions`** → INSERT at project create (v0) only in Phase 1; no UPDATE ever.
3. **Settle** → `POST /projects/{id}/bible/settle` returns **501** in Phase 1.

### `GET /projects/{project_id}/bible/entries`

Optional `section` filter.

**200:** Paginated `BibleEntry` list from staging table.

### `POST /projects/{project_id}/bible/entries`

**Request:**

```json
{
  "entry_key": "world_rules.cultivation.realms",
  "section": "world_rules",
  "title": "Cảnh giới tu luyện",
  "content_md": "## Luyện Khí\n\n...",
  "metadata": { "type": "canon", "status": "active" }
}
```

**201:** Created entry with `base_bible_version` = current project version.

**409:** Duplicate `entry_key` within project.

### `GET /projects/{project_id}/bible/entries/{entry_id}`

**404** if entry id wrong **or** entry belongs to different project (same response).

### `PATCH /projects/{project_id}/bible/entries/{entry_id}`

**Request:**

```json
{
  "title": "Cảnh giới (cập nhật)",
  "content_md": "Updated markdown..."
}
```

Does not change `entry_key` or `base_bible_version`.

### `DELETE /projects/{project_id}/bible/entries/{entry_id}`

Removes staging row only. **204**.

### `GET /projects/{project_id}/bible/versions`

Metadata list (no full snapshot).

### `GET /projects/{project_id}/bible/versions/{version}`

**200:**

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": 0,
  "settled_from_chapter_id": null,
  "created_at": "2026-09-12T10:00:00Z",
  "entry_count": 5,
  "snapshot_json": {
    "version": 0,
    "entries": []
  }
}
```

**404:** Version does not exist for project.

### `POST /projects/{project_id}/bible/settle` (Phase 2 stub)

**501:**

```json
{
  "error": {
    "code": "not_implemented",
    "message": "Bible settle is scheduled for Phase 2"
  }
}
```

---

## Chapters

### `GET /projects/{project_id}/chapters`

Ordered by `number` ASC.

**200 example:**

```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "number": 1,
      "title": "Chương 1 — Khởi đầu",
      "status": "planned",
      "word_count": 0,
      "bible_version_at_draft": null,
      "created_at": "2026-09-12T10:00:00Z",
      "updated_at": "2026-09-12T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 }
}
```

### `POST /projects/{project_id}/chapters`

Optional stub create for hub empty-state testing.

**Request:**

```json
{ "number": 2, "title": "Chương 2", "status": "planned" }
```

**409:** Duplicate `number` within project.

Phase 1 UI may omit create; template seed may pre-create chapters.

---

## Characters (T0 list)

### `GET /projects/{project_id}/characters`

Read-only in Phase 1. Seeds inserted at project create from template.

**200 example:**

```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "Lý Phong",
      "role_one_liner": "Nhân vật chính — kiếm tu",
      "tier": 0,
      "psyche_card": {},
      "created_at": "2026-09-12T10:00:00Z",
      "updated_at": "2026-09-12T10:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 }
}
```

No POST/PATCH in Phase 1 API.

---

## Cross-tenant isolation test (required)

```text
Given user U1 owns project P1
And user U2 owns project P2
When U1 GET /projects/{P2}/bible/entries with X-User-Id: U1
Then 404 not_found
And no P2 data in response body
```

Same pattern for every `{project_id}` route.

---

## Idempotency notes

| Operation | Phase 1 behavior |
|-----------|------------------|
| Create project | Client-side dedupe (disable Confirm button) |
| Create bible entry | Unique `entry_key` → 409 on retry |
| Archive project | Idempotent — second DELETE → 404 or 204 (pick one; prefer 204 if already archived) |
| Settle | N/A Phase 1 |

Phase 2 settle should accept `Idempotency-Key` header.

---

## Endpoint summary

| Method | Path | Phase 1 |
|--------|------|---------|
| GET | `/health` | ✅ |
| GET | `/projects` | ✅ |
| POST | `/projects` | ✅ |
| GET | `/projects/{id}` | ✅ |
| PATCH | `/projects/{id}` | ✅ |
| DELETE | `/projects/{id}` | ✅ archive |
| GET | `/projects/{id}/bible/entries` | ✅ |
| POST | `/projects/{id}/bible/entries` | ✅ |
| GET | `/projects/{id}/bible/entries/{entry_id}` | ✅ |
| PATCH | `/projects/{id}/bible/entries/{entry_id}` | ✅ |
| DELETE | `/projects/{id}/bible/entries/{entry_id}` | ✅ |
| GET | `/projects/{id}/bible/versions` | ✅ |
| GET | `/projects/{id}/bible/versions/{version}` | ✅ |
| POST | `/projects/{id}/bible/settle` | 501 stub |
| GET | `/projects/{id}/chapters` | ✅ |
| POST | `/projects/{id}/chapters` | ✅ optional |
| GET | `/projects/{id}/characters` | ✅ |

---

## Links

- [schema.md](./schema.md)
- [web-screens.md](./web-screens.md)
- [test-strategy.md](./test-strategy.md)
