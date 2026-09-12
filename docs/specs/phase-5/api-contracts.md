# Phase 5 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 4 api-contracts](../phase-4/api-contracts.md) — Phase 1–4 routes unchanged unless noted.

---

## Phase 5 delta summary

| Change | Detail |
|--------|--------|
| New routes | Psyche card GET/PATCH; PsychState timeline; psych context pack |
| `ContinuityCategory` | Adds **`psychology`** |
| Continuity codes | `psych_ooc_moral_boundary_violation`, `psych_moral_boundary_crossed`, `psych_value_hierarchy_jump`, `psych_arc_beat_skip`, `psych_unearned_belief_shift`, `psych_voice_taboo_break` |
| `StateDiff` | Adds **`psych_state_proposals[]`** |
| Settle | Appends approved psych proposals → `psych_states` rows |
| Context packs | `POST .../context-packs/psych` — psyche card + latest psych state per scene character |

---

## Authentication & errors

Unchanged from Phase 1–4: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Character/psych state foreign to project |
| 409 | `psych_state_immutable` | PATCH/DELETE on settled psych_state |
| 409 | `psych_state_already_settled` | Duplicate settle append for same character+chapter |
| 422 | `invalid_psyche_card` | PATCH fails schema validation (missing T3 fields on save) |
| 422 | `tier_requirements_not_met` | Psyche save would break T3 minimum (unchanged promote gate) |

---

## Psyche card

Base path: `/projects/{project_id}/characters/{character_id}/psyche-card`

Dedicated route separates stable psyche editing from general character PATCH (overview/aliases).

### `GET .../psyche-card`

**200 example:**

```json
{
  "character_id": "770e8400-e29b-41d4-a716-446655440002",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "tier": 3,
  "psyche_card": {
    "drive": "Báo thù cho gia tộc",
    "need": "Được công nhận xứng đáng",
    "wound": "Chứng kiến sư phụ hy sinh vô ích",
    "fear": "Trở thành kẻ phản bội",
    "value_hierarchy": ["gia đình", "công lý", "sức mạnh"],
    "defense": "Lạnh lùng, né tránh cảm xúc",
    "voice_taboo": ["xin lỗi"],
    "stress_behavior": "Im lặng, rút kiếm",
    "moral_boundaries": ["không giết vô tội", "không phản bội sư môn"],
    "relationship_lens": [
      {
        "target_character_id": "880e8400-e29b-41d4-a716-446655440003",
        "role_label": "rival",
        "trust_level": 1,
        "notes": "Đối thủ kiếm đạo"
      }
    ],
    "arc_flags": {
      "allow_moral_break": false,
      "expected_arc_beats": ["breakthrough_ch12"],
      "current_arc_beat": null
    }
  },
  "updated_at": "2026-09-12T10:00:00Z"
}
```

### `PATCH .../psyche-card`

**Request (partial merge):**

```json
{
  "psyche_card": {
    "moral_boundaries": ["không giết vô tội", "không phản bội sư môn", "không liên minh ma đạo"],
    "arc_flags": { "allow_moral_break": true }
  }
}
```

**200:** Updated psyche card response.

**Invariants:**

- Does not change `character.id`.
- Tier changes still via `promote-tier` only.
- T3 characters MUST retain `value_hierarchy` (≥1) and `moral_boundaries` (≥1) after merge.

---

## PsychState timeline

Base path: `/projects/{project_id}/characters/{character_id}/psych-states`

### `GET .../psych-states`

Timeline list ordered by chapter number ascending (or `settled_at`).

**Query:** `from_chapter_number`, `to_chapter_number`, pagination.

**200 example:**

```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440010",
      "character_id": "770e8400-e29b-41d4-a716-446655440002",
      "chapter_id": "660e8400-e29b-41d4-a716-446655440003",
      "chapter_number": 3,
      "stress_level": 4,
      "dominant_emotion": "resolve",
      "active_goal": "Rèn luyện kiếm pháp",
      "belief_updates": [],
      "relationship_stance": [],
      "value_pressure": null,
      "arc_beat": null,
      "trigger_event_refs": ["beat:aa0e8400-e29b-41d4-a716-446655440001"],
      "settled_at": "2026-09-10T08:00:00Z"
    },
    {
      "id": "991e8400-e29b-41d4-a716-446655440011",
      "character_id": "770e8400-e29b-41d4-a716-446655440002",
      "chapter_id": "660e8400-e29b-41d4-a716-446655440005",
      "chapter_number": 7,
      "stress_level": 8,
      "dominant_emotion": "anger",
      "active_goal": "Đối đầu sư phụ",
      "belief_updates": [
        {
          "from_belief": "Sư phụ vô tội",
          "to_belief": "Sư phụ che giấu sự thật",
          "confidence": "extract_stub",
          "trigger_ref": "beat:bb0e8400-e29b-41d4-a716-446655440002"
        }
      ],
      "relationship_stance": [
        {
          "target_character_id": "880e8400-e29b-41d4-a716-446655440003",
          "stance": "distrust",
          "trust_delta": -2,
          "notes": "Phát hiện nói dối"
        }
      ],
      "value_pressure": "công lý",
      "arc_beat": "confrontation_ch7",
      "trigger_event_refs": ["beat:bb0e8400-e29b-41d4-a716-446655440002"],
      "settled_at": "2026-09-12T14:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 50, "total_items": 2, "total_pages": 1 }
}
```

**Read-only:** No POST/PATCH/DELETE on this collection — writes via settle only.

### `GET .../psych-states/by-chapter/{chapter_id}`

Returns single settled snapshot for `(character_id, chapter_id)`.

**404** if chapter not settled for this character.

---

## Continuity integration

### Extended check behavior

`POST /projects/{project_id}/chapters/{chapter_id}/continuity-check` runs Phase 2 + Phase 3 + Phase 4 + **Phase 5 psychology rules** ([ooc-rules.md](./ooc-rules.md)).

Response `issues[]` may include `category: psychology`.

**Example issue:**

```json
{
  "fingerprint": "psych:770e8400-e29b-41d4-a716-446655440002:ooc_moral:abc123:660e8400-e29b-41d4-a716-446655440005",
  "severity": "fail",
  "category": "psychology",
  "code": "psych_ooc_moral_boundary_violation",
  "message": "Lý Phong vi phạm ranh giới đạo đức \"không giết vô tội\" ở ch.7",
  "chapter_refs": [7],
  "entity_ids": ["770e8400-e29b-41d4-a716-446655440002"],
  "evidence": {
    "boundary": "không giết vô tội",
    "matched_span": "Lý Phong hạ sát dân thường"
  }
}
```

### Mark intentional

```json
POST /projects/{project_id}/chapters/{chapter_id}/continuity-overrides
{
  "issue_fingerprint": "psych:770e8400-e29b-41d4-a716-446655440002:ooc_moral:abc123:660e8400-e29b-41d4-a716-446655440005",
  "reason": "Cố ý — nhân vật rơi vào ma đạo sau Ch.6"
}
```

---

## State diff extension

### `GET .../state-diff` and continuity report `state_diff`

Extended shape:

```json
{
  "ledger_proposals": [],
  "bible_patch_candidates": [],
  "psyche_card_patches": [
    {
      "character_id": "770e8400-e29b-41d4-a716-446655440002",
      "patch": { "arc_flags": { "current_arc_beat": "confrontation_ch7" } },
      "confidence": "extract_stub"
    }
  ],
  "psych_state_proposals": [
    {
      "character_id": "770e8400-e29b-41d4-a716-446655440002",
      "chapter_id": "660e8400-e29b-41d4-a716-446655440005",
      "stress_level": 8,
      "dominant_emotion": "anger",
      "active_goal": "Đối đầu sư phụ",
      "belief_updates": [
        {
          "from_belief": "Sư phụ vô tội",
          "to_belief": "Sư phụ che giấu sự thật",
          "confidence": "extract_stub",
          "trigger_ref": "beat:bb0e8400-e29b-41d4-a716-446655440002"
        }
      ],
      "relationship_stance": [],
      "value_pressure": "công lý",
      "arc_beat": "confrontation_ch7",
      "trigger_event_refs": ["beat:bb0e8400-e29b-41d4-a716-446655440002"],
      "confidence": "extract_stub"
    }
  ]
}
```

Phase 5: approve-all bundle — `approve_state_diff: true` applies psyche patches + psych state appends atomically in settle transaction.

---

## Settle delta

### `POST .../chapters/{chapter_id}/settle`

**200 response extension:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440005",
  "status": "locked",
  "bible_version_before": 4,
  "bible_version_after": 5,
  "ledger_events_appended": 2,
  "psych_states_appended": 1,
  "settled_at": "2026-09-12T14:30:00Z"
}
```

**Side effects:**

1. Insert `psych_states` rows from approved proposals (unique per character+chapter).
2. Apply optional `psyche_card_patches` to `characters.psyche_card`.
3. Existing twist paid_off / ledger append unchanged from Phase 4.

---

## Context pack — psych snapshot

### `POST /projects/{project_id}/context-packs/psych`

Writer/agent context: latest psych state + psyche card summary for scene cast.

**Request:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440005",
  "beat_ids": ["aa0e8400-e29b-41d4-a716-446655440001"],
  "character_ids": ["770e8400-e29b-41d4-a716-446655440002"],
  "include_psyche_card": true,
  "psych_history_limit": 1
}
```

**200 example:**

```json
{
  "entries": [
    {
      "character_id": "770e8400-e29b-41d4-a716-446655440002",
      "display_name": "Lý Phong",
      "tier": 3,
      "psyche_summary": {
        "drive": "Báo thù cho gia tộc",
        "need": "Được công nhận xứng đáng",
        "moral_boundaries": ["không giết vô tội"],
        "value_hierarchy": ["gia đình", "công lý", "sức mạnh"]
      },
      "latest_psych_state": {
        "chapter_number": 6,
        "stress_level": 6,
        "dominant_emotion": "resolve",
        "active_goal": "Tìm manh mối sư phụ"
      },
      "included_reason": "scene_beat"
    }
  ],
  "truncated": false
}
```

**Rules:**

- Omit full `relationship_lens` graph — include only targets in scene when space allows.
- Never include draft-only proposals — settled snapshots only.
- Compose with existing character + twist context packs in agent pipeline.

---

## Endpoint summary table

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/projects/{id}/characters/{cid}/psyche-card` | Read structured psyche card |
| PATCH | `/projects/{id}/characters/{cid}/psyche-card` | Author edit psyche card |
| GET | `/projects/{id}/characters/{cid}/psych-states` | Timeline list |
| GET | `/projects/{id}/characters/{cid}/psych-states/by-chapter/{chid}` | Snapshot for chapter |
| POST | `/projects/{id}/context-packs/psych` | Scene cast psych snapshot |
| POST | `/projects/{id}/chapters/{cid}/continuity-check` | *(extended)* psychology issues |
| GET | `/projects/{id}/chapters/{cid}/state-diff` | *(extended)* psych proposals |
| POST | `/projects/{id}/chapters/{cid}/settle` | *(extended)* append psych_states |

---

## Links

- [openapi.yaml](./openapi.yaml)
- [ooc-rules.md](./ooc-rules.md)
- [web-screens.md](./web-screens.md)
- [Phase 4 api-contracts](../phase-4/api-contracts.md)
