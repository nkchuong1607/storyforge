# Schema Draft (sketch)

Entity list and key tables for Postgres. **Not migrated yet** — reference for later phases and exploratory design.

> **Phase 1 canonical schema:** [docs/specs/phase-1/schema.md](specs/phase-1/schema.md)  
> **Phase 2 canonical schema:** [docs/specs/phase-2/schema.md](specs/phase-2/schema.md) — prose, beats, ledger, continuity, settle  
> **Phase 3 canonical schema:** [docs/specs/phase-3/schema.md](specs/phase-3/schema.md) — progressive characters, provisional inbox, search v1  
> **Phase 4 canonical schema:** [docs/specs/phase-4/schema.md](specs/phase-4/schema.md) — twist plans, plants, payoffs  
> **Phase 5 canonical schema:** [docs/specs/phase-5/schema.md](specs/phase-5/schema.md) — psyche card, psych_states  
> **Phase 6 canonical schema:** [docs/specs/phase-6/schema.md](specs/phase-6/schema.md) — power system, genre rule pack, prompt edit  
> **Phase 8 canonical schema:** [docs/specs/phase-8/schema.md](specs/phase-8/schema.md) — scene engine, relationships, stakes ledger  
> This draft remains for Phase 9+ tables not yet specified in detail.

## Naming Conventions

- Tables: `snake_case`, plural (`projects`, `chapters`)
- PK: `uuid` via `gen_random_uuid()`
- All tenant data includes `project_id` FK with index
- Ledger tables: append-only, no `UPDATE`/`DELETE` on settled rows

## Core Tables

### `projects`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| slug | text UNIQUE | |
| title | text | |
| genre_profile | text | |
| bible_version_current | int | default 0 |
| created_at | timestamptz | |

### `bible_versions`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| version | int | UNIQUE (project_id, version) |
| snapshot_json | jsonb | immutable world/character/world blob |
| settled_from_chapter_id | uuid | nullable for seed |
| created_at | timestamptz | |

### `chapters`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| number | int | |
| title | text | |
| status | text | enum-like |
| bible_version_at_draft | int | |
| created_at | timestamptz | |

### `scene_beats`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| chapter_id | uuid FK | |
| beat_key | text | e.g. "7.4" |
| summary | text | |
| sort_order | int | |
| completed | boolean | |

### `prose_versions`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| chapter_id | uuid FK | |
| version | int | UNIQUE (chapter_id, version) |
| content | text | |
| source | text | human, ai_writer, ai_editor |
| created_at | timestamptz | |

## Ledger Tables (pattern)

### `ledger_events`

Generic append-only stream (or split per domain later).

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| entity_type | text | character, object, knowledge, promise |
| entity_id | uuid | |
| event_type | text | status_change, location_change, ... |
| payload | jsonb | |
| chapter_ref | int | |
| settled_at | timestamptz | null until settled |
| supersedes_event_id | uuid | nullable |

Index: `(project_id, entity_type, entity_id, settled_at DESC)`

## Character System

### `characters`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | canonical ID |
| project_id | uuid FK | |
| display_name | text | |
| tier | smallint | 0–3 |
| psyche_card | jsonb | |
| merged_from_provisional_id | uuid | nullable |

### `character_provisional`

Inbox for extracted mentions before merge.

## Twist & Psychology

### `twist_plans`, `twist_plants`, `twist_payoffs`

**Canonical:** [docs/specs/phase-4/schema.md](specs/phase-4/schema.md) — status lifecycle `seeded|planted|armed|paid_off|abandoned`; promise reuse via `kind`; author-only `secret_truth`.

### `psych_states`

**Canonical:** [docs/specs/phase-5/schema.md](specs/phase-5/schema.md) — append-only per `(character_id, chapter_id)`; formal `psyche_card` jsonb on `characters`.

## Power System (Phase 6)

### `power_system_settings`, `power_ranks`, `power_techniques`

**Canonical:** [docs/specs/phase-6/schema.md](specs/phase-6/schema.md) — staging tables + bible snapshot `world.power_system`; cultivation ledger events on settle.

### `projects.genre_rule_pack_json`

**Canonical:** [docs/specs/phase-6/schema.md](specs/phase-6/schema.md) — genre contract JSON; tunes continuity severity.

### `prompt_edit_sessions`, `prompt_edit_turns`

**Canonical:** [docs/specs/phase-6/schema.md](specs/phase-6/schema.md) — instruction log; applied prose in `prose_versions` (`source=ai_editor`).

## Continuity

### `continuity_reports`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| chapter_id | uuid FK | |
| prose_version | int | |
| result | text | pass, warn, fail |
| issues_json | jsonb | |
| created_at | timestamptz | |

### `continuity_overrides`

Author-marked intentional issues.

## Vectors (Phase 3)

### `canon_embeddings`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| source_type | text | bible, ledger, prose |
| source_id | uuid | |
| embedding | vector(1536) | pgvector |

## Migration Discipline

1. One Alembic revision per logical change
2. Ledger migrations never drop columns on event tables
3. Bible snapshots remain readable for old versions
4. See skill `storyforge-db-design`
