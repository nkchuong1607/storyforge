# Phase 4 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 3 api-contracts](../phase-3/api-contracts.md) — Phase 1–3 routes unchanged unless noted.

---

## Phase 4 delta summary

| Change | Detail |
|--------|--------|
| New routes | Twist CRUD, plants CRUD, payoffs CRUD, board view, twist context pack |
| `ContinuityCategory` | Adds **`foreshadow`** |
| Continuity codes | `foreshadow_payoff_without_plants`, `foreshadow_plant_count_below_minimum`, `foreshadow_required_plants_missing`, `foreshadow_unseeded_reveal`, `foreshadow_constrained_fact_leaked`, `foreshadow_knowledge_wall` |
| Context packs | `POST .../context-packs/twists` — plants-only; **never** `secret_truth` |
| Author vs Writer | Query `?audience=author` (default UI) vs `audience=writer` strips secrets |

---

## Authentication & errors

Unchanged from Phase 1–3: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Twist/plant/payoff foreign to project |
| 409 | `chapter_locked` | Plant mutation on locked chapter |
| 409 | `twist_paid_off_immutable` | PATCH/DELETE on `paid_off` twist |
| 409 | `invalid_twist_status_transition` | Illegal status change |
| 422 | `invalid_plant_reference` | Payoff `required_plant_ids` not owned by twist |
| 422 | `payoff_already_exists` | Second payoff for same twist |

---

## Twists

Base path: `/projects/{project_id}/twists`

### `GET /projects/{project_id}/twists`

**Query:** `status`, `kind` (`twist`|`promise`), `q` (title search), pagination.

**200 example (author audience):**

```json
{
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440099",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Sát thủ là sư phụ",
      "secret_truth": "Sư phụ Thanh Phong đã giết môn chủ cũ.",
      "status": "armed",
      "kind": "twist",
      "misdirection": "Gợi ý đệ tử ngoại môn",
      "constraints_json": {
        "min_plants_before_payoff": 2,
        "constrained_facts": [],
        "knowledge_walls": []
      },
      "genre_strictness": null,
      "plant_count": 1,
      "payoff": {
        "id": "bb0e8400-e29b-41d4-a716-446655440088",
        "target_chapter_id": "660e8400-e29b-41d4-a716-446655440005",
        "target_chapter_number": 12,
        "min_plants": 2,
        "required_plant_ids": []
      },
      "created_at": "2026-09-12T10:00:00Z",
      "updated_at": "2026-09-12T14:00:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_items": 1, "total_pages": 1 }
}
```

**Writer audience** (`?audience=writer`): same shape **without** `secret_truth`, `misdirection`, or `constraints_json.constrained_facts` values that embed secrets.

### `POST /projects/{project_id}/twists`

**Request:**

```json
{
  "title": "Huyết mạch thật sự",
  "secret_truth": "Lý Phong mang huyết mạch cổ đại.",
  "kind": "twist",
  "misdirection": null,
  "constraints_json": { "min_plants_before_payoff": 1 },
  "genre_strictness": null
}
```

**201:** Created twist with `status: seeded`.

### `GET/PATCH/DELETE .../twists/{twist_id}`

PATCH supports `title`, `secret_truth`, `misdirection`, `constraints_json`, `genre_strictness`, `status` (validated transitions).

DELETE soft-abandons (`status = abandoned`) unless `paid_off` → 409.

---

## Plants

Base path: `/projects/{project_id}/twists/{twist_id}/plants`

### `POST` — create plant

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440003",
  "beat_id": null,
  "salience": "hard",
  "snippet": "Lý Phong nhìn ngón tay run — huyết mạch?",
  "prose_span_start": 1204,
  "prose_span_end": 1260,
  "sort_order": 0
}
```

**Side effect:** If twist was `seeded`, status → `planted`.

### `GET` — list plants ordered by `sort_order`

### `PATCH/DELETE .../plants/{plant_id}`

Blocked when plant chapter locked → 409.

---

## Payoffs

Base path: `/projects/{project_id}/twists/{twist_id}/payoffs`

### `POST` — register payoff (one per twist)

```json
{
  "target_chapter_id": "660e8400-e29b-41d4-a716-446655440005",
  "required_plant_ids": [],
  "min_plants": 2
}
```

**Side effect:** Twist status → `armed`.

### `GET` — get payoff for twist

Returns 404 if no payoff row.

### `PATCH .../payoffs/{payoff_id}`

Update `target_chapter_id`, `required_plant_ids`, `min_plants`.

---

## Twist Board

### `GET /projects/{project_id}/twists/board`

Kanban column view aligned with wireframe §8c.

**Query:** `kind`, `include_abandoned=false`

**200 example:**

```json
{
  "columns": [
    {
      "id": "secrets",
      "label": "Secrets",
      "cards": [
        {
          "card_type": "twist",
          "twist_id": "aa0e8400-e29b-41d4-a716-446655440099",
          "title": "Sát thủ là sư phụ",
          "status": "seeded",
          "kind": "twist",
          "secret_truth_preview": "Sư phụ Thanh Phong đã giết…",
          "plant_count": 0,
          "fairness": { "state": "ok", "issue_codes": [] }
        }
      ]
    },
    {
      "id": "plants",
      "label": "Plants",
      "cards": [
        {
          "card_type": "plant",
          "plant_id": "cc0e8400-e29b-41d4-a716-446655440077",
          "twist_id": "aa0e8400-e29b-41d4-a716-446655440099",
          "twist_title": "Sát thủ là sư phụ",
          "chapter_number": 4,
          "salience": "soft",
          "snippet": "Mùi hương quen thuộc trên dao"
        }
      ]
    },
    {
      "id": "payoffs",
      "label": "Payoffs",
      "cards": [
        {
          "card_type": "payoff",
          "payoff_id": "bb0e8400-e29b-41d4-a716-446655440088",
          "twist_id": "aa0e8400-e29b-41d4-a716-446655440099",
          "twist_title": "Sát thủ là sư phụ",
          "target_chapter_number": 12,
          "min_plants": 2,
          "plant_count": 1,
          "fairness": {
            "state": "fail",
            "issue_codes": ["foreshadow_plant_count_below_minimum"]
          }
        }
      ]
    },
    {
      "id": "revealed",
      "label": "Revealed",
      "cards": []
    }
  ]
}
```

**Column assignment rules:**

| Column | Cards |
|--------|-------|
| `secrets` | Twists `status = seeded` |
| `plants` | All plants for twists not `abandoned`/`paid_off` (card_type plant) |
| `payoffs` | Twists `status = armed` (card_type payoff) |
| `revealed` | Twists `status = paid_off` (read-only) |

Shift+link UX is client-side; optional `POST .../twists/board/links` deferred — drag updates plant `twist_id` or payoff via existing PATCH routes.

---

## Continuity integration

### Extended check behavior

`POST /projects/{project_id}/chapters/{chapter_id}/continuity-check` runs Phase 2 + Phase 3 + **Phase 4 foreshadow rules** ([fairness-rules.md](./fairness-rules.md)).

No request body change. Response `issues[]` may include `category: foreshadow`.

### Mark intentional (unchanged route)

```json
POST /projects/{project_id}/chapters/{chapter_id}/continuity-overrides
{
  "issue_fingerprint": "foreshadow:aa0e8400-e29b-41d4-a716-446655440099:payoff_without_plants:660e8400-e29b-41d4-a716-446655440005",
  "reason": "Cố ý reveal sớm cho beta reader — sẽ thêm plant retroactive"
}
```

---

## Context pack — twists strip

### `POST /projects/{project_id}/context-packs/twists`

**Request:**

```json
{
  "chapter_id": "660e8400-e29b-41d4-a716-446655440003",
  "chapter_number": 4,
  "max_plants": 20,
  "audience": "writer"
}
```

**200 example:**

```json
{
  "twist_relevant": [
    {
      "plant_id": "cc0e8400-e29b-41d4-a716-446655440077",
      "twist_id": "aa0e8400-e29b-41d4-a716-446655440099",
      "twist_title": "Sát thủ là sư phụ",
      "chapter_number": 4,
      "salience": "soft",
      "snippet": "Mùi hương quen thuộc trên dao"
    }
  ],
  "meta": {
    "audience": "writer",
    "secret_truth_stripped": true,
    "plant_count": 1
  }
}
```

**Invariants:**

- Response MUST NOT contain key `secret_truth` at any nesting level for `audience=writer`.
- Contract test: recursive JSON key scan in integration suite.

### Combined Writer pack (implementation note)

Chapter Editor / future Writer agent composes:

1. `POST .../context-packs/characters`
2. `POST .../context-packs/twists`

Merged YAML per [domain-model.md](../../domain-model.md) — `twist_relevant` from step 2 only.

---

## Transition helper

### `POST /projects/{project_id}/twists/{twist_id}/transition`

**Request:**

```json
{ "status": "abandoned" }
```

Validates transition table in [schema.md](./schema.md). Prefer explicit endpoint over raw PATCH for lifecycle clarity.

---

## Links

- [openapi.yaml](./openapi.yaml)
- [fairness-rules.md](./fairness-rules.md)
- [web-screens.md](./web-screens.md)
- [Phase 3 api-contracts](../phase-3/api-contracts.md)
