# Phase 3 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 2 api-contracts](../phase-2/api-contracts.md) — Phase 1–2 routes unchanged unless noted.

---

## Phase 3 delta summary

| Change | Detail |
|--------|--------|
| `GET .../characters` | Extended filters: `tier`, `status`, `q`; tier 0–3 |
| New routes | Character CRUD, promote-tier, provisionals, extract, search, context-pack |
| `Character.tier` | `0`–`3` (was `[0]` only in Phase 1–2) |
| Ledger | **No** writes to `character_provisional.id` |

---

## Authentication & errors

Unchanged from Phase 1–2: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 409 | `character_archived` | Mutation on archived character |
| 409 | `duplicate_display_name` | Create/patch name collision |
| 409 | `provisional_already_resolved` | Merge/reject on merged/rejected row (non-idempotent reject) |
| 409 | `already_max_tier` | Promote when tier=3 |
| 422 | `tier_requirements_not_met` | Promote without required fields (esp. T3) |
| 422 | `invalid_merge_request` | Both `target_character_id` and `create_new` missing or both set |

---

## Characters

### `GET /projects/{project_id}/characters`

**Query:** `tier`, `status`, `q`, pagination.

**200 example:**

```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "Lý Phong",
      "role_one_liner": "Nhân vật chính — kiếm tu",
      "tier": 2,
      "status": "established",
      "aliases": ["Phong", "Lý đại ca"],
      "psyche_card": { "traits": ["kiên định"], "goals": [" báo thù"] },
      "first_seen_chapter_id": "660e8400-e29b-41d4-a716-446655440001",
      "last_seen_chapter_id": "660e8400-e29b-41d4-a716-446655440003",
      "appearance_count": 5,
      "merged_from_provisional_id": null,
      "metadata": {},
      "tier_suggest": true,
      "created_at": "2026-09-12T10:00:00Z",
      "updated_at": "2026-09-12T14:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 }
}
```

### `POST /projects/{project_id}/characters`

Manual seed (wizard or Characters UI).

**Request:**

```json
{
  "display_name": "Vân Thương",
  "role_one_liner": "Sư muội — kiếm phái",
  "tier": 0,
  "aliases": []
}
```

**Invariants:**

- Cannot create at tier 3 directly.
- `display_name` unique per project (non-archived).

### `PATCH /projects/{project_id}/characters/{character_id}`

**Request:**

```json
{
  "display_name": "Lý Phong (sửa)",
  "aliases": ["Phong", "Lý đại ca", "Kiếm Thánh"],
  "psyche_card": { "traits": ["kiên định"], "moral_boundaries": ["không giết vô tội"] }
}
```

**Invariants:**

- Does not change `id` (canonical).
- Tier changes via `promote-tier` only.

### `POST /projects/{project_id}/characters/{character_id}/promote-tier`

**Request (T3):**

```json
{ "confirm_t3": true }
```

**422 example:**

```json
{
  "error": {
    "code": "tier_requirements_not_met",
    "message": "T3 requires psyche_card traits and moral_boundaries",
    "details": [{ "field": "psyche_card.moral_boundaries", "required": true }]
  }
}
```

---

## Alias search

### `GET /projects/{project_id}/characters/search?q=Phong&limit=10`

**200 example:**

```json
{
  "search_mode": "keyword",
  "items": [
    {
      "character": { "id": "770e8400-...", "display_name": "Lý Phong", "tier": 2, "..." : "..." },
      "match_type": "alias",
      "matched_alias": "Phong",
      "score": 1.0
    }
  ]
}
```

**Vector mode:** `search_mode=vector` returns `501 not_implemented` until pgvector stub populated (optional Phase 3 branch).

---

## Provisional inbox

### `GET /projects/{project_id}/characters/provisionals?status=pending`

**200 example:**

```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440010",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "mention_text": "Hắc Y Nhân",
      "mention_fingerprint": "a1b2c3...",
      "chapter_id": "660e8400-e29b-41d4-a716-446655440001",
      "chapter_number": 1,
      "prose_version": 3,
      "snippet": "...gặp Hắc Y Nhân đứng trước cổng...",
      "proposed_fields": {
        "display_name": "Hắc Y Nhân",
        "role_one_liner": null,
        "suggested_tier": 0
      },
      "status": "pending",
      "extractor_source": "heuristic",
      "matched_character_id": null,
      "merged_character_id": null,
      "resolved_at": null,
      "created_at": "2026-09-12T12:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 },
  "pending_count": 1
}
```

### `POST .../provisionals/{provisional_id}/merge` — merge into existing

**Request:**

```json
{
  "target_character_id": "770e8400-e29b-41d4-a716-446655440002"
}
```

**200 example:**

```json
{
  "provisional": { "id": "880e8400-...", "status": "merged", "merged_character_id": "770e8400-..." },
  "character": { "id": "770e8400-...", "aliases": ["Phong", "Hắc Y Nhân"], "..." : "..." },
  "idempotent": false
}
```

**Idempotent retry:** Same request on already-merged row → `200`, `"idempotent": true`, same `character`.

### `POST .../provisionals/{provisional_id}/merge` — promote new

**Request:**

```json
{
  "create_new": true,
  "display_name": "Hắc Y Nhân",
  "initial_tier": 0,
  "mark_established": true
}
```

Creates new canonical `characters` row; sets `merged_from_provisional_id`.

### `POST .../provisionals/{provisional_id}/reject`

**Request:**

```json
{ "reason": "Địa danh, không phải nhân vật" }
```

---

## Fact extractor v1

### `POST /projects/{project_id}/chapters/{chapter_id}/extract-characters`

**Request:**

```json
{
  "prose_version": 3,
  "extractor_mode": "heuristic",
  "include_beats": true
}
```

**200 example:**

```json
{
  "created_count": 2,
  "skipped_count": 5,
  "skipped_reasons": {
    "duplicate_name": 3,
    "already_pending": 2
  },
  "provisionals": [ { "id": "880e8400-...", "mention_text": "Hắc Y Nhân", "..." : "..." } ]
}
```

**Heuristic v1 rules:**

- Capitalized multi-token sequences (locale-aware VI/EN)
- `@Name` explicit mentions
- Quoted `"Name"` in prose
- Beat `summary` tokens when `include_beats=true`
- Skip tokens in project blocklist (future settings)

**LLM mode:** Optional; returns `501` or falls back to heuristic if no API key.

**409:** Chapter `locked` — extract not allowed.

---

## Context pack subset

### `POST /projects/{project_id}/context-packs/characters`

**Request:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440001",
  "name_hints": ["Hắc Y", "Phong"],
  "max_stubs": 12,
  "include_ledger_tail": true,
  "ledger_tail_limit": 5
}
```

**200 example:**

```json
{
  "entries": [
    {
      "character": { "id": "770e8400-...", "display_name": "Lý Phong", "tier": 3, "..." : "..." },
      "included_reason": "pov",
      "ledger_tail": [
        { "event_type": "location_change", "chapter_number": 2, "payload": { "to": "Thanh Vân Phong" } }
      ]
    }
  ],
  "truncated": false,
  "search_mode": "keyword"
}
```

**Resolution order:**

1. POV character (if `chapters.pov_character_id` set)
2. Characters linked in beat summaries / metadata
3. T3 principals in chapter
4. `name_hints` resolved via search
5. Cap T0/T1 stubs at `max_stubs`

---

## Cross-tenant isolation test (required)

```text
Given user U1 owns project P1 with character C1
And user U2 owns project P2
When U1 POST /projects/{P2}/characters/provisionals/{id}/merge with X-User-Id: U1
Then 404 not_found
```

Same pattern for extract, search, context-pack.

---

## Merge idempotency test (required)

```text
Given pending provisional R1
When U1 POST merge with target_character_id=C1
Then 200, provisional.status=merged, character C1 has new alias

When U1 POST same merge again
Then 200, idempotent=true, no duplicate alias rows
```

---

## Endpoint summary

| Method | Path | Phase 3 |
|--------|------|---------|
| GET | `/projects/{id}/characters` | ✅ extended |
| POST | `/projects/{id}/characters` | ✅ |
| GET | `/projects/{id}/characters/search` | ✅ |
| GET | `/projects/{id}/characters/{character_id}` | ✅ |
| PATCH | `/projects/{id}/characters/{character_id}` | ✅ |
| POST | `/projects/{id}/characters/{character_id}/promote-tier` | ✅ |
| GET | `/projects/{id}/characters/provisionals` | ✅ |
| GET | `/projects/{id}/characters/provisionals/{provisional_id}` | ✅ |
| POST | `/projects/{id}/characters/provisionals/{provisional_id}/merge` | ✅ |
| POST | `/projects/{id}/characters/provisionals/{provisional_id}/reject` | ✅ |
| POST | `/projects/{id}/chapters/{chapter_id}/extract-characters` | ✅ |
| POST | `/projects/{id}/context-packs/characters` | ✅ |

All Phase 1–2 routes remain unchanged.

---

## Links

- [schema.md](./schema.md)
- [character-lifecycle.md](./character-lifecycle.md)
- [web-screens.md](./web-screens.md)
- [test-strategy.md](./test-strategy.md)
