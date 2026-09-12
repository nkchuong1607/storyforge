# Schema Draft (sketch)

Entity list and key tables for Postgres. **Not migrated yet** — reference for later phases and exploratory design.

> **Phase 1 canonical schema:** [docs/specs/phase-1/schema.md](specs/phase-1/schema.md)  
> Use the Phase 1 spec for migrations and API implementation. This draft remains for Phase 2+ tables (ledgers, prose, continuity) not yet specified in detail.

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

### `twist_plans`

| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| project_id | uuid FK | |
| secret_truth | text | author-only |
| status | text | active, revealed |

### `twist_plants`, `twist_payoffs`

Link plants to chapters and payoff targets.

### `psych_states`

Append-only per character per chapter snapshot.

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
