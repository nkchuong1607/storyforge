# Phase 11 Schema — CraftPack

> Alembic revision **`032_craft_packs`**. Depends on `031_fact_citations`.

---

## Enum extension

```sql
ALTER TYPE continuity_category ADD VALUE IF NOT EXISTS 'craft';
```

Python: `ContinuityCategory.craft = "craft"`.

---

## Table: `craft_packs`

Catalog of installable craft packs (seeded in migration).

| Column | Type | Notes |
|--------|------|-------|
| `id` | `TEXT` PK | e.g. `mystery.fair_play.v1` |
| `schema_version` | `INTEGER` NOT NULL | Pack JSON schema version |
| `pack_json` | `JSONB` NOT NULL | Full pack document |
| `installed_at` | `TIMESTAMPTZ` NOT NULL DEFAULT now() | Catalog row timestamp |

---

## Table: `project_craft_packs`

Project binding — MVP allows **one active** pack per project.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `UUID` PK | |
| `project_id` | `UUID` FK → `projects` CASCADE | |
| `craft_pack_id` | `TEXT` FK → `craft_packs` | |
| `active` | `BOOLEAN` NOT NULL DEFAULT false | Only one `true` per project (app-enforced) |
| `bound_at` | `TIMESTAMPTZ` NOT NULL DEFAULT now() | |

**Unique:** `(project_id, craft_pack_id)`.

**Index:** `(project_id, active)` for active lookup.

---

## Seed data

Migration inserts `mystery.fair_play.v1` from [mystery-craft-pack.md](./mystery-craft-pack.md).

---

## Invariants

1. Installing a craft pack does **not** mutate `projects.genre_rule_pack_json`.
2. Deactivating clears `active=false`; row retained for audit.
3. Genre compatibility: reject install when `genre_profile` not in pack `compat.requires_genre_profiles`.

---

## Links

- [mystery-craft-pack.md](./mystery-craft-pack.md)
- [api-contracts.md](./api-contracts.md)
