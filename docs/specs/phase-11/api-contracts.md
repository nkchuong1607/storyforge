# Phase 11 API Contracts — CraftPack

> Examples and error codes. OpenAPI: [openapi.yaml](./openapi.yaml).

**Auth:** `X-User-Id: <uuid>` (unchanged).

---

## Catalog

### `GET /craft-packs`

List seeded catalog entries.

```json
{
  "items": [
    {
      "id": "mystery.fair_play.v1",
      "display_name": "Mystery — Fair Play",
      "genre_tags": ["mystery"],
      "schema_version": 1
    }
  ]
}
```

### `GET /craft-packs/{craft_pack_id}`

Full pack JSON (author-facing structure + checklist; no internal golden fields required in response).

---

## Project binding

### `GET /projects/{project_id}/craft-packs`

```json
{
  "project_id": "...",
  "active_pack_id": "mystery.fair_play.v1",
  "bindings": [
    {
      "craft_pack_id": "mystery.fair_play.v1",
      "active": true,
      "bound_at": "2026-09-22T10:00:00Z",
      "display_name": "Mystery — Fair Play"
    }
  ]
}
```

### `POST /projects/{project_id}/craft-packs/{craft_pack_id}/install`

Install (bind) pack. Idempotent if already bound.

**Errors:**

| Code | When |
|------|------|
| `404` | Unknown pack id |
| `409` | `genre_incompatible` — profile not in pack compat list |

Does **not** modify `genre_rule_pack_json`.

### `POST /projects/{project_id}/craft-packs/{craft_pack_id}/activate`

Set pack active (deactivates other bindings).

### `POST /projects/{project_id}/craft-packs/{craft_pack_id}/deactivate`

Set `active=false`.

---

## Context pack

### `POST /projects/{project_id}/context-packs/craft`

**Body:**

```json
{
  "chapter_id": "...",
  "chapter_number": 5,
  "audience": "writer"
}
```

**Response:**

```json
{
  "craft_pack_id": "mystery.fair_play.v1",
  "craft_beats": [{"key": "reveal", "act": 3, "required": true}],
  "craft_checklist_open": [{"id": "fair_play_min_clues", "code": "craft_mystery_insufficient_plants"}],
  "active_clues": [{"twist_title": "Killer identity", "chapter_number": 2, "snippet": "..."}],
  "active_misdirections": [],
  "meta": {"audience": "writer", "secret_truth_stripped": true}
}
```

Never includes `secret_truth`.

---

## Continuity codes (when craft pack active)

| Code | Category | Severity |
|------|----------|----------|
| `craft_mystery_clue_after_reveal` | `foreshadow` | fail |
| `craft_mystery_insufficient_plants` | `foreshadow` | fail |
| `craft_mystery_unlabeled_misdirection` | `craft` | warn |
| `craft_mystery_reader_spoiler` | `craft` | warn |

Existing Phase 4 foreshadow codes unchanged when craft pack inactive.

**Fact Check:** Phase 10 bridge semantics unchanged — craft rules never emit `fact_check` category.

---

## Prompt Edit

When active craft pack present, `instruct` / `regenerate` compose craft context slice server-side (same fields as context pack subset). Response turn unchanged; context logged in turn metadata optional field `craft_context_keys`.

---

## Links

- [openapi.yaml](./openapi.yaml)
- [test-strategy.md](./test-strategy.md)
