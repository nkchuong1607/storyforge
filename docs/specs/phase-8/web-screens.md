# Phase 8 Web Screens — Slice 1

> Maps [openapi.yaml](./openapi.yaml) → UI. Reuses Phase 7 design system and i18n infrastructure.  
> **Phase 8 screens:** Scene lint panel (Chapter Editor + Gate), Relationship graph, Stakes board.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| Design system | Phase 7 tokens, `Button`, `Badge`, `Table`, `Modal`, `Skeleton`, `Empty` — [design-system.md](../phase-7/design-system.md) |
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–7 |
| Types | Generated / hand-written from Phase 8 OpenAPI |
| MSW | Handlers for scene-engine, relationships, stakes routes |
| i18n | New namespaces `scene.*`, `relationships.*`, `stakes.*` — VI primary, EN secondary |
| a11y | WCAG AA; keyboard nav on graph list fallback |
| Route loading | `loading.tsx` skeletons per Phase 7 [performance.md](../phase-7/performance.md) |

---

## i18n namespaces (implementers)

Add keys under `apps/web/messages/vi.json` and `en.json`:

### `scene.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `scene.panel.title` | Cấu trúc cảnh | Editor lint panel header |
| `scene.fields.goal` | Mục tiêu | Beat form label |
| `scene.fields.conflict` | Xung đột | |
| `scene.fields.outcome` | Kết quả | |
| `scene.fields.stakes_level` | Mức stakes | 0–5 slider |
| `scene.fields.scene_type` | Loại cảnh | Select |
| `scene.lint.missing_outcome` | Thiếu outcome | Inline badge |
| `scene.lint.missing_conflict` | Thiếu xung đột | |
| `scene.gate.category` | Cấu trúc cảnh | Continuity Gate filter |

### `relationships.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `relationships.graph.title` | Sơ đồ quan hệ | Page title |
| `relationships.list.title` | Quan hệ nhân vật | List view |
| `relationships.types.ally` | Đồng minh | relation_type label |
| `relationships.types.rival` | Đối thủ | |
| `relationships.intensity.label` | Cường độ tin cậy | -5..+5 |
| `relationships.events.timeline` | Lịch sử | Event list |
| `relationships.empty` | Chưa có quan hệ | Empty state |
| `relationships.gate.category` | Cung quan hệ | Gate filter |

### `stakes.*`

| Key | VI example | Usage |
|-----|------------|-------|
| `stakes.board.title` | Bảng stakes | Page title |
| `stakes.act.label` | Hồi {n} | Act column header |
| `stakes.status.planned` | Đã lên kế hoạch | Status pill |
| `stakes.status.planted` | Đã gieo | |
| `stakes.status.resolved` | Đã giải quyết | |
| `stakes.target_level` | Mức mục tiêu | |
| `stakes.flat_middle.warn` | Giữa truyện phẳng | Hub badge |
| `stakes.gate.category` | Stakes | Gate filter |

---

## Screen 3 delta — Chapter Editor Scene lint panel

**Wireframe base:** [chapter-editor.png](../../wireframes/images/chapter-editor.png)  
**Stories:** US-W01 (extended)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Beats sidebar (extended) | `SceneBeatStructureFields` | PATCH beat with goal/conflict/outcome |
| Beat row badge | `SceneLintBadge` | `POST .../scene-lint` or cached from last check |
| Collapsible panel | `SceneLintPanel` | Lint issues for current chapter |
| Stakes hint | `ActStakesHint` | `GET .../stakes/entries?act_number=current` |

### Beat form fields (below summary)

| Field | Control | Validation |
|-------|---------|------------|
| goal | textarea | min length hint from settings |
| conflict | textarea | |
| outcome | textarea | required when completed checked |
| stakes_level | slider 0–5 | optional |
| scene_type | select | scene/sequel/transition/exposition |
| pov_character_id | character combobox | scene cast |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Save beat structure | `PATCH .../beats/{beat_id}` |
| Quick lint | `POST .../chapters/{id}/scene-lint` |
| Full check | `POST .../continuity-check` (existing) |
| Act context | `GET .../stakes/board?act_number=N` |

### States

| State | UI |
|-------|-----|
| **Drafting** | Fields editable; lint on blur debounced |
| **Lint WARN** | Amber badge on beat row |
| **Lint FAIL** | Red badge; tooltip with message |
| **Locked chapter** | Read-only fields; lint panel historical |
| **Empty beats** | CTA "Thêm beat đầu tiên" (Phase 2) |
| **Loading lint** | Skeleton badges |

---

## Continuity Gate delta — Scene / Relationship / Stakes filters

**Wireframe:** [continuity-gate.png](../../wireframes/images/continuity-gate.png) (Phase 2)

| Addition | Component |
|----------|-----------|
| Category filter chips | Add `scene_structure`, `relationship_arc`, `stakes` |
| Issue row icon | Map category → icon from design system |
| Deep link | "Sửa beat" → Chapter Editor scroll to `beat_id` |
| Relationship link | "Xem quan hệ" → graph with `character_ids` prefilled |
| Stakes link | "Mở bảng stakes" → board filtered to act |

---

## Screen 10 delta — Relationship graph

**Route:** `/projects/[projectId]/relationships/graph`  
**Wireframe base:** [psych-relationships.png](../../wireframes/images/psych-relationships.png) — **graph replaces list-only view**  
**Stories:** US-C03 (extended)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `RelationshipGraphHeader` | title + filters |
| Filter bar | `RelationshipGraphFilters` | act, types, min intensity |
| Canvas | `RelationshipGraphCanvas` | `GET .../relationships/graph` |
| List fallback | `RelationshipGraphList` | Same data — a11y primary path |
| Side panel | `RelationshipDetailPanel` | selected edge → events timeline |
| Actions | `RelationshipRegisterButton` | → modal create pair |

### Graph rendering (Slice 1)

| Approach | Detail |
|----------|--------|
| Primary | Canvas/SVG force layout **or** simple circular layout — implementation choice |
| a11y fallback | Sortable table: Character A, Character B, type, intensity |
| No Neo4j | All data from Postgres graph endpoint |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load graph | `GET .../relationships/graph` |
| Register edge | `POST .../relationships` |
| View timeline | `GET .../relationships/{id}/events` |
| Edit metadata | `PATCH .../relationships/{id}` |

### States

| State | UI |
|-------|-----|
| **Empty** | Illustration + "Đăng ký quan hệ đầu tiên" |
| **Loading** | Skeleton nodes |
| **Dense graph** | Filter hint banner |
| **Selected edge** | Side panel with event timeline |
| **Error** | Retry + toast |

### Character detail tab

**Route:** `/projects/[id]/characters/[cid]?tab=relationships`

| Element | Behavior |
|---------|----------|
| Subgraph | Graph filtered to `character_ids=[cid]` |
| Link | "Mở sơ đồ đầy đủ" → graph route |

Phase 5 minimal trust list **retained** under psyche card; graph is additive tab content.

---

## Screen — Stakes board

**Route:** `/projects/[projectId]/stakes`  
**Stories:** US-O01 (partial — act-level only)

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `StakesBoardHeader` | title + act settings link |
| Columns | `StakesActColumn` × act_count | `GET .../stakes/board` |
| Card | `StakesCheckpointCard` | entry title, target_level, status |
| Drag | Optional reorder within act → PATCH sort_order | |
| Create | `StakesCheckpointModal` | POST entry |
| Settings drawer | `ActStructureSettingsDrawer` | GET/PATCH settings |

### Board column shape (API)

```json
{
  "acts": [
    {
      "act_number": 1,
      "label": "Hồi I",
      "start_chapter": 1,
      "end_chapter": 8,
      "entries": [ { "id": "...", "title": "...", "status": "planned", "target_level": 3 } ]
    }
  ]
}
```

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load board | `GET .../stakes/board` |
| Create checkpoint | `POST .../stakes/entries` |
| Update status | `PATCH .../stakes/entries/{id}` |
| Act settings | `GET/PATCH .../stakes/settings` |

### States

| State | UI |
|-------|-----|
| **Empty act** | Dashed column + add CTA |
| **Flat middle WARN** | Column header amber indicator |
| **Linked twist** | Badge with link to Twist Board |
| **Loading** | Column skeletons |

---

## Project Hub delta — Open stakes indicator

**Route:** `/projects/[projectId]` (existing hub)

| Widget | `StakesHubBadge` |
|--------|------------------|
| Condition | Latest continuity has `stakes_*` open WARN/FAIL |
| Action | Link to `/stakes?act=current` |

---

## MSW handlers (test doubles)

| Handler | Fixture |
|---------|---------|
| `GET .../relationships/graph` | `fixtures/relationship-graph.json` |
| `GET .../stakes/board` | `fixtures/stakes-board.json` |
| `POST .../scene-lint` | `fixtures/scene-lint-warn.json` |

---

## Screen parity checklist (Phase 8 additions)

| Screen | Empty | Loading | Error | Success |
|--------|-------|---------|-------|---------|
| Scene lint panel | ✅ no beats | ✅ | ✅ retry | ✅ badges clear |
| Relationship graph | ✅ | ✅ | ✅ | ✅ select edge |
| Stakes board | ✅ per act | ✅ | ✅ | ✅ CRUD |

Extend [screen-parity.md](../phase-7/screen-parity.md) patterns — no new parity doc required in specs PR.

---

## Links

- [openapi.yaml](./openapi.yaml)
- [api-contracts.md](./api-contracts.md)
- [test-strategy.md](./test-strategy.md)
- Phase 7: [design-system.md](../phase-7/design-system.md), [i18n.md](../phase-7/i18n.md)
