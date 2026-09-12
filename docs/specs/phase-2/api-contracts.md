# Phase 2 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 1 api-contracts](../phase-1/api-contracts.md) — Phase 1 routes unchanged unless noted.

---

## Phase 2 delta summary

| Change | Detail |
|--------|--------|
| `chapter_status` | `continuity_pending` renamed → **`reviewing`** |
| `POST .../bible/settle` | **Removed** — use chapter-scoped settle |
| New routes | Chapter detail, beats, prose, continuity, overrides, settle |

---

## Authentication & errors

Unchanged from Phase 1: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 409 | `chapter_locked` | Mutation on `locked` chapter |
| 409 | `continuity_fail_blocks_settle` | Effective FAIL without override |
| 409 | `invalid_chapter_status_transition` | e.g. settle when not `reviewing` |
| 409 | `prose_version_conflict` | Concurrent version race (optional) |
| 422 | `continuity_check_required` | Settle without latest report |

---

## Chapter detail & status

### `GET /projects/{project_id}/chapters/{chapter_id}`

**200 example:**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "number": 1,
  "title": "Chương 1 — Khởi đầu",
  "status": "drafting",
  "word_count": 1842,
  "bible_version_at_draft": 0,
  "current_prose_version": 3,
  "settled_at": null,
  "locked_at": null,
  "created_at": "2026-09-12T10:00:00Z",
  "updated_at": "2026-09-12T11:30:00Z"
}
```

### `PATCH /projects/{project_id}/chapters/{chapter_id}`

**Request:**

```json
{
  "title": "Chương 1 — Khởi đầu (sửa)",
  "status": "drafting"
}
```

**Invariants:**

- Cannot PATCH `status` from `locked`.
- Valid transitions only (see [schema.md](./schema.md)).
- Reject / request revise: `{ "status": "drafting" }` from `reviewing`.

**409 locked:**

```json
{
  "error": {
    "code": "chapter_locked",
    "message": "Chapter is locked after settle"
  }
}
```

---

## Scene beats

Base path: `/projects/{project_id}/chapters/{chapter_id}/beats`

### `GET` — list ordered by `sort_order`

### `POST` — create

```json
{
  "beat_key": "1.3",
  "summary": "Lý Phong gặp sư phụ",
  "sort_order": 3,
  "completed": false
}
```

### `PATCH /beats/{beat_id}` — partial update

### `DELETE /beats/{beat_id}` — **204**

**Invariant:** All beat mutations return **409** when chapter `status = locked`.

---

## Prose versions

Base path: `/projects/{project_id}/chapters/{chapter_id}/prose-versions`

### `GET` — list metadata (newest first)

```json
{
  "items": [
    {
      "version": 3,
      "word_count": 1842,
      "source": "human",
      "created_by": "880e8400-e29b-41d4-a716-446655440003",
      "created_at": "2026-09-12T11:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 3, "total_pages": 1 }
}
```

### `GET /prose-versions/{version}` — full content

```json
{
  "version": 3,
  "content": "Hàn Lập đứng trên vách núi...",
  "word_count": 1842,
  "source": "human",
  "created_by": "880e8400-e29b-41d4-a716-446655440003",
  "created_at": "2026-09-12T11:30:00Z"
}
```

### `POST` — save new version (human)

```json
{
  "content": "Full chapter markdown or plain text..."
}
```

**Side effects (single TXN):**

1. INSERT `prose_versions` version N+1
2. UPDATE `chapters.word_count`, `current_prose_version`
3. If `bible_version_at_draft` IS NULL → set to `projects.bible_version_current`
4. If status was `planned` → `drafting`

**409** if chapter locked.

### `GET /prose-versions/compare?from=1&to=3`

Returns metadata diff only (not full inline diff):

```json
{
  "from_version": 1,
  "to_version": 3,
  "word_count_delta": 420,
  "created_at_from": "2026-09-12T10:00:00Z",
  "created_at_to": "2026-09-12T11:30:00Z"
}
```

---

## Continuity

### `POST /projects/{project_id}/chapters/{chapter_id}/continuity-check`

Sync MVP — blocks until report persisted.

**Request (optional body):**

```json
{
  "prose_version": 3
}
```

Default: latest prose version.

**200:**

```json
{
  "report_id": "990e8400-e29b-41d4-a716-446655440004",
  "chapter_id": "660e8400-e29b-41d4-a716-446655440001",
  "prose_version": 3,
  "result": "fail",
  "stats": { "passed": 12, "warnings": 1, "errors": 1 },
  "issues": [
    {
      "fingerprint": "character:770e8400:character_deceased_appears_alive:abc123",
      "severity": "fail",
      "category": "character",
      "code": "character_deceased_appears_alive",
      "message": "Nhân vật 'Lý Phong' đã chết ở ch.3...",
      "chapter_refs": [1],
      "entity_ids": ["770e8400-e29b-41d4-a716-446655440002"]
    }
  ],
  "state_diff": {
    "ledger_proposals": [],
    "bible_patch_candidates": []
  }
}
```

**Side effect:** chapter status → `reviewing` (if was `drafting`).

### `GET .../continuity-reports/latest`

Same payload shape as check response (without re-running rules).

### `GET .../continuity-reports/{report_id}`

Historical report by id.

---

## Overrides

### `POST /projects/{project_id}/chapters/{chapter_id}/continuity-overrides`

```json
{
  "issue_fingerprint": "character:770e8400:character_deceased_appears_alive:abc123",
  "reason": "Nhân vật chỉ xuất hiện trong hồi tưởng — cố ý"
}
```

**201:**

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "issue_fingerprint": "character:770e8400:character_deceased_appears_alive:abc123",
  "severity_at_override": "fail",
  "reason": "Nhân vật chỉ xuất hiện trong hồi tưởng — cố ý",
  "created_at": "2026-09-12T11:45:00Z"
}
```

**Invariant:** Fingerprint must exist in latest report's `issues_json`.

---

## State diff

### `GET /projects/{project_id}/chapters/{chapter_id}/state-diff`

Query: `prose_version` (optional, default latest).

Returns `state_diff_json` from latest matching report, or computes stub extract if none.

---

## Settle (replaces Phase 1 `POST .../bible/settle` 501)

### `POST /projects/{project_id}/chapters/{chapter_id}/settle`

**Headers:**

| Header | Required | Notes |
|--------|----------|-------|
| `Idempotency-Key` | Recommended | UUID; duplicate success returns cached `200` |

**Request body (optional Phase 2):**

```json
{
  "report_id": "990e8400-e29b-41d4-a716-446655440004",
  "approve_state_diff": true
}
```

**Preconditions:**

1. Chapter `status = reviewing`
2. Latest report exists; `approve_state_diff = true`
3. No effective FAIL issues (see [continuity-rules.md](./continuity-rules.md))

**200:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "locked",
  "bible_version_before": 0,
  "bible_version_after": 1,
  "ledger_events_appended": 2,
  "settled_at": "2026-09-12T12:00:00Z"
}
```

**Atomic transaction (all or nothing):**

1. Append `ledger_events` with `settled_at`
2. INSERT `bible_versions` at N+1 from staging merge
3. UPDATE `projects.bible_version_current`
4. Reconcile `bible_entry_staging`
5. UPDATE chapter → `locked`, timestamps

**409 continuity_fail_blocks_settle:**

```json
{
  "error": {
    "code": "continuity_fail_blocks_settle",
    "message": "Unresolved continuity FAIL blocks settle",
    "details": [{ "fingerprint": "...", "code": "character_deceased_appears_alive" }]
  }
}
```

---

## Global invariants (Phase 2)

| # | Invariant |
|---|-----------|
| 1 | **No settle on FAIL** without active override per fingerprint |
| 2 | **`locked` chapter read-only** — prose, beats, status PATCH (except none) |
| 3 | **Cross-tenant** nested routes → `404` |
| 4 | **`bible_versions` immutable** — settle INSERT only |
| 5 | **`ledger_events` append-only** — only `settled_at` may be set at settle |
| 6 | **Draft pins bible** — `bible_version_at_draft` set on first prose save |

---

## Endpoint summary (Phase 2 new)

| Method | Path | Notes |
|--------|------|-------|
| GET | `.../chapters/{chapter_id}` | Detail |
| PATCH | `.../chapters/{chapter_id}` | Title, status transitions |
| GET/POST | `.../chapters/{chapter_id}/beats` | List, create |
| PATCH/DELETE | `.../beats/{beat_id}` | Update, delete |
| GET/POST | `.../prose-versions` | List, save |
| GET | `.../prose-versions/{version}` | Full content |
| GET | `.../prose-versions/compare` | Metadata compare |
| POST | `.../continuity-check` | Sync audit |
| GET | `.../continuity-reports/latest` | Latest report |
| GET | `.../continuity-reports/{report_id}` | Historical |
| POST | `.../continuity-overrides` | Mark intentional |
| GET | `.../state-diff` | State diff preview |
| POST | `.../chapters/{chapter_id}/settle` | Atomic settle |

**Removed:** `POST /projects/{id}/bible/settle` (Phase 1 returned 501).

---

## Links

- [schema.md](./schema.md)
- [web-screens.md](./web-screens.md)
- [continuity-rules.md](./continuity-rules.md)
- [test-strategy.md](./test-strategy.md)
