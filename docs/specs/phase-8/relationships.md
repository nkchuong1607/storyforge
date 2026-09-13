# Phase 8 Relationship Arcs — Ledger & Graph

> Canonical relationship history via append-only events; Postgres-backed graph read model.  
> Implements product [03-domain-and-subsystems.md](../../product/03-domain-and-subsystems.md) §9.

**No Neo4j in Phase 8 Slice 1.** Adjacency is stored in Postgres (`relationships` registry + `relationship_events` ledger + materialized graph JSON view).

---

## Purpose

Track **trust, rivalry, alliance, betrayal** arcs over time with ledger events on settle. The graph UI is a **read model** derived from settled events — not a separate source of truth. Phase 5 psyche `relationship_lens` remains author-facing intent templates; ledger events record **what happened in canon**.

---

## Entities

### `relationships` (registry)

Canonical undirected pair between two characters (ordered storage for uniqueness).

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | Stable edge id |
| `project_id` | `uuid` FK | Tenant |
| `character_a_id` | `uuid` FK | `character_a_id < character_b_id` enforced |
| `character_b_id` | `uuid` FK | |
| `relation_type` | `text` | `ally`, `rival`, `mentor`, `family`, `romantic`, `enemy`, `custom` |
| `custom_label` | `text` | When `relation_type=custom` |
| `baseline_intensity` | `smallint` | -5..+5 trust scale at registration |
| `notes_md` | `text` | Author notes |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Metadata only — intensity history in events |

**Uniqueness:** `UNIQUE (project_id, character_a_id, character_b_id)`

**Self-edge:** Rejected with `422 invalid_relationship_pair`.

---

### `relationship_events` (append-only ledger)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` PK | |
| `project_id` | `uuid` FK | |
| `relationship_id` | `uuid` FK | |
| `event_type` | `text` | `relationship_change`, `trust_shift`, `betrayal`, `reconciliation`, `status_change` |
| `intensity_delta` | `smallint` | -5..+5 applied to running intensity |
| `intensity_after` | `smallint` | Denormalized snapshot after event |
| `relation_type_after` | `text` | NULL if unchanged |
| `payload` | `jsonb` | `{ "trigger": "...", "evidence_refs": [], "visibility": "public|secret" }` |
| `chapter_id` | `uuid` FK | Source chapter |
| `chapter_number` | `integer` | Denormalized |
| `prose_version` | `integer` | |
| `settled_at` | `timestamptz` | NULL until settle |
| `created_at` | `timestamptz` | |

**Rules:**

- INSERT on settle from approved `state_diff.relationship_event_proposals[]`
- No UPDATE/DELETE after `settled_at` set
- Running intensity computed as: `baseline_intensity + SUM(intensity_delta)` for settled events ordered by `(chapter_number, settled_at)`

**Also mirrored in generic `ledger_events`** with `entity_type=relationship`, `event_type=relationship_change` for cross-domain queries (migration `023`).

---

## Graph read model

### `GET .../relationships/graph`

Returns nodes + edges for force-directed or list-layout UI.

```json
{
  "nodes": [
    {
      "id": "char-uuid-a",
      "display_name": "Lâm Phong",
      "tier": 2,
      "degree": 3
    }
  ],
  "edges": [
    {
      "id": "rel-uuid",
      "source_id": "char-uuid-a",
      "target_id": "char-uuid-b",
      "relation_type": "rival",
      "intensity": -2,
      "last_event": {
        "chapter_number": 12,
        "event_type": "trust_shift",
        "intensity_delta": -1
      },
      "event_count": 5
    }
  ],
  "meta": {
    "filtered_character_ids": [],
    "act_number": null,
    "generated_at": "2026-09-13T00:00:00Z"
  }
}
```

**Query params:**

| Param | Purpose |
|-------|---------|
| `character_ids[]` | Focus subgraph |
| `act_number` | Filter events with `chapter_number <= act_end_chapter` |
| `min_intensity` | Hide weak edges |
| `relation_types[]` | Filter edge types |

**Implementation note:** Build graph in SQL using latest settled event per `relationship_id`; cache optional in Redis Phase 9+.

---

## List read model

### `GET .../relationships`

Paginated registry rows with **latest settled intensity** (not live draft proposals).

### `GET .../relationships/{id}/events`

Timeline ordered by `chapter_number ASC`, `settled_at ASC`.

---

## Continuity category: `relationship_arc`

Deterministic rules on `POST .../continuity-check`:

### R-A1 — Contradictory intensity jump

**Code:** `relationship_intensity_jump_without_event`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Input | Prose sentiment keywords + state_diff proposals |
| Violation | Implied trust collapse (betrayal keywords) without `relationship_event_proposals` entry for pair |

### R-A2 — Relation type regression

**Code:** `relationship_type_contradiction`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Prose treats pair as allies while latest settled `relation_type_after=enemy` without reconciliation event in diff |

### R-A3 — Unknown pair interaction

**Code:** `relationship_unregistered_pair`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Both characters in same beat POV/dialogue tags; no `relationships` row and tier ≥ T1 for both |

### R-A4 — Secret relationship visibility leak

**Code:** `relationship_secret_visibility_leak`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Latest event `payload.visibility=secret` but prose POV character not in `payload.knows[]` reveals relationship explicitly |

**Override:** Standard `continuity_overrides` on fingerprint.

---

## State diff / settle

Extract proposes:

```json
{
  "relationship_event_proposals": [
    {
      "relationship_id": "rel-uuid",
      "event_type": "trust_shift",
      "intensity_delta": -2,
      "relation_type_after": null,
      "payload": {
        "trigger": "broken_oath",
        "evidence_refs": [{ "beat_id": "...", "quote_span": [120, 180] }]
      }
    }
  ]
}
```

Settle response includes `relationship_events_appended: N`.

**Psyche sync (optional):** Settle may propose `psyche_card_patches` updating `relationship_lens` trust bars — author approves separately in bundle.

---

## API summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/projects/{id}/relationships` | List registry |
| POST | `/projects/{id}/relationships` | Register pair |
| GET/PATCH/DELETE | `/projects/{id}/relationships/{rid}` | CRUD metadata |
| GET | `/projects/{id}/relationships/{rid}/events` | Event timeline |
| GET | `/projects/{id}/relationships/graph` | Graph read model |
| POST | `/projects/{id}/context-packs/relationships` | Progressive LLM slice |

Full contract: [openapi.yaml](./openapi.yaml), [api-contracts.md](./api-contracts.md).

---

## Web UI

| Screen | Route | Spec |
|--------|-------|------|
| Relationship graph | `/projects/[id]/relationships/graph` | [web-screens.md](./web-screens.md) |
| Relationship list + detail | `/projects/[id]/relationships` | Same |
| Character detail tab extension | `?tab=relationships` — graph deep-link | Extends Phase 5 screen 10 |

**i18n namespace:** `relationships.*`

---

## Progressive context pack

`POST .../context-packs/relationships`

| Rule | Detail |
|------|--------|
| Input | `chapter_id`, `character_ids[]` (scene cast) |
| Output | Edges where both endpoints in cast OR one endpoint is POV + other mentioned in beat summaries |
| Cap | Max 8 edges, 3 events per edge (most recent settled) |
| Omit | `secret` visibility events unless POV in `payload.knows[]` |

---

## Phase 5 complement

| Phase 5 | Phase 8 |
|---------|---------|
| `relationship_lens[]` on psyche card | Registry + history |
| Trust bar UI (list) | Graph + timeline |
| No ledger events | `relationship_events` on settle |

Implementers: editing trust in psyche card does **not** write ledger — only settle-approved proposals do.

---

## Links

- [schema.md](./schema.md) — migrations `021`, `023`
- [scene-engine.md](./scene-engine.md) — beat POV / cast resolution
- Skill: `storyforge-characters`, `storyforge-domain-canon`
