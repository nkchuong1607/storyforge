# Phase 6 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 5 api-contracts](../phase-5/api-contracts.md) — Phase 1–5 routes unchanged unless noted.

---

## Phase 6 delta summary

| Change | Detail |
|--------|--------|
| New routes | Power system CRUD; genre rule pack; prompt-edit instruct/apply/regenerate/sessions |
| `ContinuityCategory` | Adds **`power_system`** |
| Continuity codes | `power_rank_jump_without_breakthrough`, `power_rank_regression`, `power_technique_ineligible`, `power_technique_sect_mismatch`, `power_upset_without_justification`, `power_unknown_rank_label` |
| `StateDiff` | Cultivation `ledger_proposals`; optional `power_system_snapshot_patch` |
| Settle | Appends `cultivation_change` / `technique_learned` / `resource_consumed`; refreshes bible `world.power_system` |
| LLM | FakeLLM default; LiteLLM via env — see [prompt-edit.md](./prompt-edit.md) |
| Genre | Formal `genre_rule_pack_json` GET/PATCH |

---

## Authentication & errors

Unchanged from Phase 1–5: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Power rank/technique/session foreign to project |
| 409 | `rank_in_use` | Delete rank referenced by technique |
| 409 | `power_system_disabled` | CRUD when module disabled |
| 409 | `chapter_locked` | Prompt edit on locked chapter |
| 422 | `invalid_rank_ladder` | Non-monotonic sort_order on batch save |
| 422 | `invalid_genre_rule_pack` | PATCH pack schema validation fail |
| 502 | `llm_provider_error` | LiteLLM failure after retries |
| 429 | `prompt_edit_rate_limited` | Hourly instruct cap exceeded |

---

## Power system settings

Base path: `/projects/{project_id}/power-system/settings`

### `GET .../power-system/settings`

**200 example:**

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "enabled": true,
  "priority_gap": 2,
  "max_rank_jump_per_chapter": 1,
  "require_breakthrough_event": true,
  "updated_at": "2026-09-12T10:00:00Z"
}
```

### `PATCH .../power-system/settings`

**Request:**

```json
{
  "enabled": true,
  "priority_gap": 3,
  "max_rank_jump_per_chapter": 1
}
```

---

## Power ranks (staging CRUD)

Base path: `/projects/{project_id}/power-system/ranks`

### `GET .../power-system/ranks`

Ordered by `sort_order` ascending.

**200 example:**

```json
{
  "items": [
    {
      "id": "a1000000-0000-4000-8000-000000000001",
      "rank_key": "qi_refining",
      "display_name": "Luyện Khí",
      "sort_order": 0,
      "sub_stages": [],
      "constraints_md": "Tu luyện cơ bản; lifespan +50 năm"
    }
  ]
}
```

### `POST .../power-system/ranks`

Creates rank at end of ladder (or specify `sort_order` with reorder).

### `PATCH .../power-system/ranks/{rank_id}`

Partial update — changing `sort_order` may reorder siblings.

### `DELETE .../power-system/ranks/{rank_id}`

409 if techniques reference rank.

### `PUT .../power-system/ranks/reorder`

**Request:** `{ "rank_ids": ["uuid", "..."] }` — validates full permutation.

---

## Power techniques (staging CRUD)

Base path: `/projects/{project_id}/power-system/techniques`

### `GET .../power-system/techniques`

**200 example:**

```json
{
  "items": [
    {
      "id": "b2000000-0000-4000-8000-000000000002",
      "technique_key": "azure_cloud_sword",
      "display_name": "Thanh Vân Kiếm",
      "min_rank_id": "a1000000-0000-4000-8000-000000000001",
      "min_rank_display_name": "Luyện Khí",
      "sect_requirement": "Thanh Vân Tông",
      "lineage_requirement": null,
      "resource_cost": { "spirit_stones": 50 },
      "notes_md": "Kiếm khí cơ bản"
    }
  ]
}
```

---

## Genre rule pack

Base path: `/projects/{project_id}/genre-rule-pack`

### `GET .../genre-rule-pack`

Returns merged pack + `defaults_from` metadata.

**200 example:**

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "genre_profile": "xianxia",
  "pack": {
    "schema_version": 1,
    "base_profile": "xianxia",
    "modules": { "power_system": { "enabled": true } },
    "strictness": { "foreshadow": "relaxed", "power": "strict" },
    "promises": ["Cảnh giới leo thang có căn cứ"],
    "forbidden": ["Nhảy cảnh giới không breakthrough"],
    "thresholds": {
      "foreshadow_min_plants_default": 1,
      "foreshadow_payoff_without_plants": "warn"
    }
  },
  "updated_at": "2026-09-12T10:00:00Z"
}
```

### `PATCH .../genre-rule-pack`

Partial merge — deep merge for `modules`, `thresholds`, `strictness`.

### `POST .../genre-rule-pack/reset`

Query: `confirm=true`. Resets to template defaults for current `genre_profile`.

---

## Prompt Edit

Base path: `/projects/{project_id}/chapters/{chapter_id}/prompt-edit`

### `POST .../prompt-edit/instruct`

**Request:**

```json
{
  "instruction": "Tăng tension ở beat 7.3; giữ giọng lạnh lùng của Lâm Phong",
  "base_prose_version": 3,
  "beat_key": "7.3"
}
```

**201 example:**

```json
{
  "session_id": "c3000000-0000-4000-8000-000000000003",
  "turn": {
    "id": "d4000000-0000-4000-8000-000000000004",
    "turn_index": 1,
    "instruction": "Tăng tension ở beat 7.3...",
    "proposed_content": "... full revised chapter ...",
    "model": "fake-llm",
    "provider": "fake",
    "latency_ms": 12,
    "token_usage": { "prompt_tokens": 1200, "completion_tokens": 800 }
  },
  "base_prose_version": 3
}
```

### `POST .../prompt-edit/regenerate`

**Request:** `{ "session_id": "...", "turn_id": "..." }` — re-runs instruction from referenced turn.

### `POST .../prompt-edit/apply`

**Request:**

```json
{
  "session_id": "c3000000-0000-4000-8000-000000000003",
  "turn_id": "d4000000-0000-4000-8000-000000000004"
}
```

**201 example:**

```json
{
  "prose_version": {
    "version": 4,
    "source": "ai_editor",
    "word_count": 4521,
    "created_at": "2026-09-12T10:05:00Z",
    "prompt_edit_turn_id": "d4000000-0000-4000-8000-000000000004"
  },
  "chapter": {
    "current_prose_version": 4,
    "word_count": 4521
  }
}
```

### `GET .../prompt-edit/sessions`

Lists sessions with turn summaries for chapter (newest first).

### Compare (existing)

`GET .../prose-versions/compare?from=3&to=4` — unchanged from Phase 2.

---

## Continuity — power_system category

### Example FAIL issue

```json
{
  "fingerprint": "power:770e8400-e29b-41d4-a716-446655440002:rank_jump:rank1:rank3:ch7",
  "severity": "fail",
  "category": "power_system",
  "code": "power_rank_jump_without_breakthrough",
  "message": "Lâm Phong nhảy cảnh giới Luyện Khí → Kim Đan không có breakthrough (max 1/chương)",
  "chapter_refs": [7],
  "entity_ids": ["770e8400-e29b-41d4-a716-446655440002"],
  "evidence": {
    "from_rank_id": "a1000000-0000-4000-8000-000000000001",
    "to_rank_id": "a1000000-0000-4000-8000-000000000003",
    "max_jump": 1
  }
}
```

---

## Settle extract (cultivation)

`GET .../state-diff` includes:

```json
{
  "ledger_proposals": [
    {
      "entity_type": "character",
      "entity_id": "770e8400-e29b-41d4-a716-446655440002",
      "event_type": "cultivation_change",
      "payload": {
        "from_rank_id": "a1000000-0000-4000-8000-000000000001",
        "to_rank_id": "a1000000-0000-4000-8000-000000000002",
        "breakthrough": true,
        "method": "độ kiếp"
      }
    }
  ],
  "power_system_snapshot_patch": {
    "action": "sync_staging_to_bible"
  }
}
```

Settle response adds: `"cultivation_events_appended": 1`.

---

## Route index (Phase 6 new)

| Method | Path | Purpose |
|--------|------|---------|
| GET/PATCH | `/projects/{id}/power-system/settings` | Anti-creep config |
| GET/POST | `/projects/{id}/power-system/ranks` | Rank ladder |
| PATCH/DELETE | `/projects/{id}/power-system/ranks/{rank_id}` | Rank CRUD |
| PUT | `/projects/{id}/power-system/ranks/reorder` | Ladder order |
| GET/POST | `/projects/{id}/power-system/techniques` | Techniques |
| PATCH/DELETE | `/projects/{id}/power-system/techniques/{tid}` | Technique CRUD |
| GET/PATCH | `/projects/{id}/genre-rule-pack` | Genre contract JSON |
| POST | `/projects/{id}/genre-rule-pack/reset` | Reset defaults |
| POST | `/projects/{id}/chapters/{cid}/prompt-edit/instruct` | LLM propose |
| POST | `/projects/{id}/chapters/{cid}/prompt-edit/regenerate` | Retry |
| POST | `/projects/{id}/chapters/{cid}/prompt-edit/apply` | Commit version |
| GET | `/projects/{id}/chapters/{cid}/prompt-edit/sessions` | Instruction log |

---

## Environment (LiteLLM / FakeLLM)

| Variable | Default | Notes |
|----------|---------|-------|
| `STORYFORGE_LLM_PROVIDER` | `fake` | Tests **must** leave default |
| `LITELLM_MODEL` | — | Required when provider=litellm |
| `OPENAI_API_KEY` | — | `.env.example` only |

See [prompt-edit.md](./prompt-edit.md) for full list.

---

## Links

- [openapi.yaml](./openapi.yaml)
- [power-rules.md](./power-rules.md)
- [genre-contracts.md](./genre-contracts.md)
- [prompt-edit.md](./prompt-edit.md)
- [test-strategy.md](./test-strategy.md)
