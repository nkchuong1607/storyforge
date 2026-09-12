# Phase 3 Web Screens

> Maps [openapi.yaml](./openapi.yaml) → UI from [05-wireframes.md](../../product/05-wireframes.md).  
> **Phase 3 screens:** Characters list + detail (#7), Provisional inbox panel.  
> **Stub only:** Psych + Relationships tabs — link to wireframe §10; full editor Phase 5.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–2 |
| Types | Extend from Phase 3 OpenAPI |
| MSW | Handlers for all Phase 3 character routes |
| Routing | `/projects/[projectId]/characters`, `/projects/[projectId]/characters/[characterId]`, inbox as tab or `/characters/inbox` |

---

## Hub updates (Phase 3 delta on Screen 2)

**Wireframe:** [project-hub.png](../../wireframes/images/project-hub.png)

| UI change | Behavior |
|-----------|----------|
| Characters nav | Link to Characters screen |
| Inbox badge | `pending_count` from `GET .../characters/provisionals?status=pending` (first page meta) |

| UI action | Endpoint |
|-----------|----------|
| Inbox badge count | `GET /projects/{id}/characters/provisionals?status=pending&page_size=1` |

---

## Screen 7 — Characters list (`/projects/[projectId]/characters`)

**Wireframe:** [characters-inbox.png](../../wireframes/images/characters-inbox.png) — main table zone  
**Stories:** US-C01, US-C02

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Top bar | `CharactersHeader` | project title, "Thêm nhân vật" |
| Filters | `CharacterFilters` | tier, status, search `q` |
| Main table | `CharacterTable` | `GET .../characters` |
| Inbox panel | `ProvisionalInboxPanel` | `GET .../characters/provisionals` |
| Empty state | `CharactersEmptyState` | when items empty |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load cast | `GET /projects/{id}/characters?tier=&status=&q=` |
| Create seed | `POST /projects/{id}/characters` |
| Open detail | Navigate → `GET .../characters/{characterId}` |
| Promote tier (quick) | `POST .../characters/{id}/promote-tier` |
| Load inbox | `GET .../characters/provisionals?status=pending` |
| Merge | `POST .../provisionals/{id}/merge` |
| Promote new | `POST .../provisionals/{id}/merge` `{ create_new: true }` |
| Reject | `POST .../provisionals/{id}/reject` |
| Run extract (toolbar) | `POST .../chapters/{chapterId}/extract-characters` — from chapter picker modal |

### Character table columns

| Column | Field |
|--------|-------|
| Tier | `tier` badge T0–T3 + `tier_suggest` dot |
| Name | `display_name` |
| Role | `role_one_liner` |
| Appearances | `appearance_count` / last chapter number |
| Status | `status` (hide archived by default) |
| Actions | View, Promote, Archive |

### Provisional inbox panel

| Column | Field |
|--------|-------|
| Mention | `mention_text` + `snippet` tooltip |
| Chapter | `chapter_number` |
| Suggested match | `matched_character_id` → search link |
| Actions | Merge ▼ (pick existing), Promote new, Reject |

### States

| State | Trigger | UI |
|-------|---------|-----|
| Loading | Initial | Skeleton table + inbox |
| Empty cast | No characters | "Thêm nhân vật seed hoặc viết prose để extract" |
| Inbox empty | `pending_count=0` | Tab hidden or badge 0 |
| Merge conflict | Side-by-side modal | Pick canonical fields before merge |
| Error 404 | Wrong tenant | "Không tìm thấy dự án" |
| Error 409 | Archived target | Toast "Nhân vật đã lưu trữ" |

---

## Screen 7b — Character detail (`/projects/[projectId]/characters/[characterId]`)

**Wireframe:** [characters-inbox.png](../../wireframes/images/characters-inbox.png) — detail tabs  
**Stories:** US-C01 (partial), US-C02

### Tabs

| Tab | Phase 3 scope | Data |
|-----|---------------|------|
| **Overview** | Full | `GET .../characters/{id}` — tier, role, aliases, chapter refs |
| **Psyche** | **Stub** | Read-only if `psyche_card` present; "Chỉnh sửa đầy đủ — Phase 5" banner. See [psych-relationships.png](../../wireframes/images/psych-relationships.png) |
| **Relationships** | **Stub** | Placeholder list from `metadata.relations`; full graph Phase 8+ |
| **Ledger tail** | Read-only | Last N `ledger_events` for entity (reuse Phase 2 API pattern or inline in character GET future) |
| **Appearances** | List | `first_seen` / `last_seen` + appearance_count |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load detail | `GET /projects/{id}/characters/{characterId}` |
| Save overview | `PATCH .../characters/{characterId}` |
| Promote tier | `POST .../characters/{characterId}/promote-tier` |
| Add alias | `PATCH` with updated `aliases` array |
| Archive | `PATCH` `{ "status": "archived" }` |

### Psych tab stub (Phase 3)

Per wireframe [psych-relationships.png](../../wireframes/images/psych-relationships.png):

- Show read-only psyche fields if populated (traits, goals).
- Disabled edit controls with Phase 5 badge.
- No PsychState timeline (Phase 5).

---

## Chapter Editor hook (Phase 3 delta on Screen 3)

Optional entry point from [Chapter Editor](../phase-2/web-screens.md):

| UI action | Endpoint |
|-----------|----------|
| "Quét nhân vật" button | `POST .../chapters/{chapterId}/extract-characters` |
| On success | Toast + link to inbox with `?chapter_id=` filter |

Extract disabled when chapter `status=locked`.

---

## Out of scope Phase 3

- Full psyche editor (Phase 5)
- Relationship graph (Phase 8+)
- LLM extractor UI toggle (optional hidden flag OK)
- Bulk merge / bulk reject (future)
- Vector search UI (keyword search only in autocomplete)

---

## MSW / test modules (coverage scope)

Phase 3 web coverage gate applies to:

- `apps/web/src/app/projects/[projectId]/characters/**`
- `apps/web/src/components/characters/**`
- Inbox panel components shared with characters route

See [test-strategy.md](./test-strategy.md).

---

## Links

- [api-contracts.md](./api-contracts.md)
- [character-lifecycle.md](./character-lifecycle.md)
- [Phase 2 web screens](../phase-2/web-screens.md)
