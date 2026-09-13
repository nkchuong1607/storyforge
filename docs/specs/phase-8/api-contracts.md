# Phase 8 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 6 api-contracts](../phase-6/api-contracts.md) — Phase 1–7 routes unchanged unless noted.

---

## Phase 8 delta summary

| Change | Detail |
|--------|--------|
| Extended schemas | `SceneBeat` adds goal/conflict/outcome/stakes_level/pressure_tags/pov_character_id/scene_type |
| New routes | Scene engine settings + scene-lint; relationships CRUD + graph + events; stakes settings + entries + board; context packs |
| `ContinuityCategory` | Adds **`scene_structure`**, **`relationship_arc`**, **`stakes`** |
| Continuity codes | Scene: `scene_missing_*`, `scene_stakes_level_drift`; Relationship: `relationship_*`; Stakes: `stakes_*` |
| `StateDiff` | Adds `relationship_event_proposals`, `stakes_ledger_proposals`; extends `ledger_proposals` |
| Settle | Appends relationship events + stakes ledger updates; bible `world.stakes` snapshot |
| LLM stub | Optional scene auditor via FakeLLM when `llm_auditor_enabled` |

---

## Authentication & errors

Unchanged from Phase 1–7: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Relationship/stakes entry foreign to project |
| 409 | `chapter_locked` | Beat/relationship/stakes mutate on locked chapter |
| 409 | `relationship_exists` | Duplicate character pair |
| 409 | `relationship_event_immutable` | Mutate settled event |
| 422 | `invalid_relationship_pair` | Same character or ordering violation |
| 422 | `invalid_stakes_level` | stakes_level outside 0–5 |
| 422 | `invalid_act_number` | act_number > act_count |
| 422 | `invalid_scene_type` | Unknown scene_type enum |
| 502 | `scene_llm_auditor_error` | Optional LLM stub failure |

---

## Scene engine

### `GET/PATCH .../scene-engine/settings`

**GET 200 example:**

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "enabled": true,
  "require_conflict": true,
  "require_outcome_on_complete": true,
  "min_goal_length": 8,
  "llm_auditor_enabled": false,
  "strictness": "standard",
  "updated_at": "2026-09-13T00:00:00Z"
}
```

### Extended `PATCH .../beats/{beat_id}`

**Request:**

```json
{
  "goal": "Lâm Phong phải lấy được Huyết Đan trước khi môn phái phát hiện",
  "conflict": "Đồ đệ nội môn canh gác; linh lực suy yếu",
  "outcome": "Lấy được đan nhưng bị truy đuổi — trust với sư huynh giảm",
  "stakes_level": 4,
  "scene_type": "scene",
  "pov_character_id": "a1000000-0000-4000-8000-000000000001",
  "pressure_tags": [
    { "tag": "sect_lockdown", "source": "bible:locations.inner_hall", "weight": 2 }
  ],
  "completed": true
}
```

**422:** `scene_missing_outcome` pre-check when `completed=true` and outcome empty (optional server-side validation before lint).

### `POST .../chapters/{chapter_id}/scene-lint`

Runs scene_structure rules only; does not persist continuity report.

**200 example:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440001",
  "result": "warn",
  "issues": [
    {
      "fingerprint": "scene_structure:770e8400-e29b-41d4-a716-446655440099:missing_conflict",
      "severity": "warn",
      "category": "scene_structure",
      "code": "scene_missing_conflict",
      "message": "Beat 7.3 thiếu xung đột",
      "chapter_refs": [7],
      "entity_ids": ["770e8400-e29b-41d4-a716-446655440099"],
      "evidence": { "beat_key": "7.3" }
    }
  ],
  "stats": { "fail": 0, "warn": 1, "pass": 5 }
}
```

---

## Relationships

### `POST .../relationships`

**Request:**

```json
{
  "character_a_id": "a1000000-0000-4000-8000-000000000001",
  "character_b_id": "b2000000-0000-4000-8000-000000000002",
  "relation_type": "rival",
  "baseline_intensity": -1,
  "notes_md": "Tranh đoạt vị trí đệ tử chính thức"
}
```

Server normalizes pair order (`character_a_id < character_b_id`).

**201:** Full `Relationship` object.

### `GET .../relationships/graph`

**Query:** `?character_ids=uuid1&character_ids=uuid2&act_number=2&min_intensity=-3`

**200:** See [relationships.md](./relationships.md#graph-read-model).

### `GET .../relationships/{id}/events`

**200 example:**

```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440010",
      "event_type": "trust_shift",
      "intensity_delta": -2,
      "intensity_after": -3,
      "chapter_number": 12,
      "settled_at": "2026-09-01T10:00:00Z",
      "payload": { "trigger": "broken_oath", "visibility": "public" }
    }
  ]
}
```

---

## Stakes

### `GET/PATCH .../stakes/settings`

**PATCH request:**

```json
{
  "act_count": 3,
  "chapters_per_act": [
    { "act_number": 1, "start_chapter": 1, "end_chapter": 10, "label": "Hồi I" }
  ],
  "flat_middle_window_chapters": 3
}
```

### `POST .../stakes/entries`

**Request:**

```json
{
  "act_number": 2,
  "checkpoint_key": "act2_midpoint",
  "title": "Mất sư phụ",
  "description_md": "Sư phụ hy sinh — stakes leo lên đỉnh hồi 2",
  "target_level": 4,
  "sort_order": 1,
  "linked_twist_id": null
}
```

### `GET .../stakes/board`

**200 example:**

```json
{
  "settings": {
    "act_count": 3,
    "enabled": true
  },
  "acts": [
    {
      "act_number": 1,
      "label": "Hồi I",
      "start_chapter": 1,
      "end_chapter": 10,
      "entries": [
        {
          "id": "990e8400-e29b-41d4-a716-446655440020",
          "checkpoint_key": "act1_midpoint",
          "title": "Phản bội nội gián",
          "target_level": 3,
          "status": "resolved",
          "plant_chapter_id": "660e8400-e29b-41d4-a716-446655440005",
          "resolve_chapter_id": "660e8400-e29b-41d4-a716-446655440008"
        }
      ]
    }
  ],
  "warnings": {
    "flat_middle": false,
    "open_fail_count": 0
  }
}
```

---

## Continuity — new categories

### `scene_structure`

| Code | Default severity |
|------|------------------|
| `scene_missing_goal` | WARN |
| `scene_missing_conflict` | WARN |
| `scene_missing_outcome` | FAIL |
| `scene_goal_too_short` | WARN |
| `scene_stakes_level_drift` | WARN |
| `scene_pov_unknown_character` | WARN |
| `scene_beat_order_invalid` | FAIL |
| `scene_llm_weak_turn` | WARN (stub only) |

### `relationship_arc`

| Code | Default severity |
|------|------------------|
| `relationship_intensity_jump_without_event` | FAIL |
| `relationship_type_contradiction` | WARN |
| `relationship_unregistered_pair` | WARN |
| `relationship_secret_visibility_leak` | WARN |

### `stakes`

| Code | Default severity |
|------|------------------|
| `stakes_flat_middle` | WARN |
| `stakes_plant_without_beat_stakes` | WARN |
| `stakes_escalation_regression` | WARN |
| `stakes_unresolved_past_act` | FAIL (strict) |
| `stakes_level_jump_without_checkpoint` | WARN |

**Example FAIL issue:**

```json
{
  "fingerprint": "relationship_arc:rel-uuid:intensity_jump_without_event",
  "severity": "fail",
  "category": "relationship_arc",
  "code": "relationship_intensity_jump_without_event",
  "message": "Phản bội giữa Lâm Phong và Hàn Vân chưa có relationship event trong state diff",
  "chapter_refs": [12],
  "entity_ids": ["rel-uuid"],
  "evidence": {
    "character_a_id": "...",
    "character_b_id": "...",
    "keywords_matched": ["phản bội", "đâm sau lưng"]
  }
}
```

---

## State diff extensions

```json
{
  "relationship_event_proposals": [
    {
      "relationship_id": "rel-uuid",
      "event_type": "betrayal",
      "intensity_delta": -3,
      "relation_type_after": "enemy",
      "payload": { "trigger": "sect_betrayal", "visibility": "public" }
    }
  ],
  "stakes_ledger_proposals": [
    {
      "entry_id": "stakes-uuid",
      "status": "planted",
      "plant_chapter_id": "chapter-uuid"
    }
  ],
  "ledger_proposals": [
    {
      "entity_type": "relationship",
      "entity_id": "rel-uuid",
      "event_type": "relationship_change",
      "payload": { "intensity_delta": -3, "intensity_after": -4 }
    }
  ]
}
```

---

## Context packs

### `POST .../context-packs/scene`

**Request:** `{ "chapter_id": "...", "beat_ids": ["..."] }`  
**Response:** `{ "beats": [ { "beat_key", "goal", "conflict", "outcome", "stakes_level" } ] }`

### `POST .../context-packs/relationships`

**Request:** `{ "chapter_id": "...", "character_ids": ["..."] }`  
**Response:** `{ "edges": [ { "relation_type", "intensity", "recent_events": [] } ] }`

### `POST .../context-packs/stakes`

**Request:** `{ "chapter_id": "..." }`  
**Response:** `{ "act_number": 2, "checkpoints": [ { "checkpoint_key", "target_level", "status" } ], "current_peak_level": 3 }`

---

## Settle delta

**Response fields added:**

```json
{
  "relationship_events_appended": 1,
  "stakes_entries_updated": 1,
  "bible_version": 5,
  "snapshot_includes": ["world.stakes"]
}
```

---

## Links

- [openapi.yaml](./openapi.yaml)
- [scene-engine.md](./scene-engine.md)
- [relationships.md](./relationships.md)
- [stakes.md](./stakes.md)
