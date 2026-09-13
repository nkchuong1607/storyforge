# Phase 8 Scene Engine — Beat Structure & Lint

> Deterministic scene-level structure checks for Continuity Gate.  
> Implements product [03-domain-and-subsystems.md](../../product/03-domain-and-subsystems.md) §7.

---

## Purpose

Every scene beat should carry **goal**, **conflict**, and **outcome** so chapters avoid filler and the Writer context pack can surface intent. Phase 8 extends Phase 2 `scene_beats` with structure fields and runs **deterministic lint** on `POST .../continuity-check` under continuity category **`scene_structure`**.

LLM semantic scene-quality audit is **optional stub only** (disabled by default; FakeLLM when enabled in tests).

---

## Beat / scene model

### Extended `scene_beats` columns (migration `020`)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `goal` | `text` | No (lint if empty when `completed`) | What the POV/scene wants |
| `conflict` | `text` | No | Obstacle / opposition |
| `outcome` | `text` | No (required when `completed=true`) | Result + value shift summary |
| `stakes_level` | `smallint` | No, DEFAULT `null` | 0–5 scale; links to stakes ledger |
| `pressure_tags` | `jsonb` | DEFAULT `'[]'` | Location/faction pressure refs — see shape |
| `pov_character_id` | `uuid` | NULL | FK → `characters(id)`; chapter-level POV fallback |
| `scene_type` | `text` | DEFAULT `'scene'` | `scene`, `sequel`, `transition`, `exposition` |

**`pressure_tags[]` item shape:**

```json
{ "tag": "siege", "source": "bible:locations.winter_capital", "weight": 1 }
```

### Scene engine settings (`scene_engine_settings`)

One row per project (create on first scene API call or template seed).

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| `enabled` | `boolean` | `true` | Master switch for scene_structure category |
| `require_conflict` | `boolean` | `true` | WARN/FAIL when conflict empty on completed beat |
| `require_outcome_on_complete` | `boolean` | `true` | FAIL when `completed=true` and outcome empty |
| `min_goal_length` | `smallint` | `8` | Character count; shorter → WARN |
| `llm_auditor_enabled` | `boolean` | `false` | Optional stub auditor |
| `strictness` | `text` | `standard` | `relaxed`, `standard`, `strict` — merges with genre pack |

---

## Lint execution model

| Property | Value |
|----------|-------|
| Trigger | `POST .../continuity-check` (same pipeline as Phase 2–6) |
| Input | Chapter `scene_beats` + latest prose + `scene_engine_settings` + genre pack |
| Category | **`scene_structure`** |
| Rule pack | `deterministic-v1+scene-v1` appended to report metadata |
| Standalone lint | `POST .../chapters/{id}/scene-lint` — same rules, no ledger/state_diff side effects (optional fast path for editor) |

---

## Deterministic rule catalog

### S1 — Missing goal on active beat

**Code:** `scene_missing_goal`  
**Severity:** WARN (relaxed) / FAIL (strict)

| Check | Logic |
|-------|-------|
| Precondition | Beat `completed=true` OR prose word count in beat span > 0 (beat boundary heuristic: sort_order sections) |
| Violation | `goal` null or empty after trim |

**Fingerprint:** `scene_structure:{beat_id}:missing_goal`

---

### S2 — Missing conflict

**Code:** `scene_missing_conflict`  
**Severity:** WARN (default) / FAIL when `require_conflict=true` AND strictness=strict

| Check | Logic |
|-------|-------|
| Precondition | `scene_type IN (scene, sequel)` and beat marked completed |
| Violation | `conflict` empty |

**Fingerprint:** `scene_structure:{beat_id}:missing_conflict`

---

### S3 — Completed beat without outcome

**Code:** `scene_missing_outcome`  
**Severity:** FAIL when `require_outcome_on_complete=true`

| Check | Logic |
|-------|-------|
| Violation | `completed=true` AND `outcome` empty |

**Fingerprint:** `scene_structure:{beat_id}:missing_outcome`

---

### S4 — Goal too vague

**Code:** `scene_goal_too_short`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Non-empty `goal` with length < `min_goal_length` |

---

### S5 — Stakes level mismatch

**Code:** `scene_stakes_level_drift`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Input | Beat `stakes_level` vs nearest act checkpoint `target_level` from `stakes_ledger_entries` |
| Violation | Beat stakes_level > act checkpoint target + 2 without linked escalation entry in state_diff |

Cross-links [stakes.md](./stakes.md) category **`stakes`**.

---

### S6 — POV character not in cast

**Code:** `scene_pov_unknown_character`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | `pov_character_id` set but not in project `characters` or provisional merge pending |

Uses existing **`character`** category optionally; Phase 8 emits under `scene_structure` for beat-scoped UX.

---

### S7 — Duplicate beat keys / sort gaps

**Code:** `scene_beat_order_invalid`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Violation | Non-contiguous `sort_order` or duplicate `beat_key` within chapter |

Reuses Phase 2 validation; surfaced in `scene_structure` for editor lint panel grouping.

---

## Optional LLM auditor stub

When `scene_engine_settings.llm_auditor_enabled=true` AND env `STORYFORGE_SCENE_LLM_AUDITOR=true`:

| Property | Value |
|----------|-------|
| Provider | FakeLLM default; LiteLLM opt-in (server-side keys) |
| Input slice | Beat goal/conflict/outcome + prose excerpt for beat span only |
| Output | Zero or more issues with codes prefixed `scene_llm_` |
| Severity cap | WARN only in Slice 1 — never FAIL without deterministic rule |
| Tests | FakeLLM returns fixed fixture in `tests/fixtures/scene_llm_audit.json` |

**Out of scope:** Production-quality semantic scene critique; full prompt template lives in implementation PR behind feature flag.

---

## Continuity Gate integration

Issues appear in standard `continuity_reports.issues_json[]`:

```json
{
  "fingerprint": "scene_structure:550e8400-e29b-41d4-a716-446655440099:missing_outcome",
  "severity": "fail",
  "category": "scene_structure",
  "code": "scene_missing_outcome",
  "message": "Beat 7.4 đánh dấu hoàn thành nhưng thiếu outcome",
  "chapter_refs": [7],
  "entity_ids": ["550e8400-e29b-41d4-a716-446655440099"],
  "evidence": {
    "beat_key": "7.4",
    "sort_order": 3
  }
}
```

**Settle gate:** Unchanged — effective FAIL count includes `scene_structure` FAILs unless overridden.

---

## State diff / settle

Scene structure does **not** append ledger events by default. Optional bible patch on settle:

```json
{
  "bible_patch_candidates": [
    {
      "path": "world.scene_structure_summary",
      "op": "merge",
      "value": {
        "chapter_7": {
          "beats_with_outcome": 6,
          "avg_stakes_level": 3.2
        }
      }
    }
  ]
}
```

Author approves at settle; copied into next `bible_versions.snapshot_json` if accepted.

---

## API touchpoints

| Action | Endpoint |
|--------|----------|
| CRUD beats (extended fields) | Existing `.../chapters/{id}/beats` — see [openapi.yaml](./openapi.yaml) |
| Scene engine settings | `GET/PATCH .../scene-engine/settings` |
| Fast lint (editor) | `POST .../chapters/{id}/scene-lint` |
| Full check | `POST .../chapters/{id}/continuity-check` (includes scene rules) |
| Context pack header | `POST .../context-packs/scene` — beats with goal/conflict for Writer |

See [api-contracts.md](./api-contracts.md) for examples.

---

## Web touchpoints

| Surface | Component | Spec |
|---------|-----------|------|
| Chapter Editor beats sidebar | `SceneBeatStructureFields` | [web-screens.md](./web-screens.md) |
| Continuity Gate | Issue group filter `scene_structure` | Same |
| Scene lint panel | Inline WARN badges on beats | Same |

**i18n namespace:** `scene.*` — see [web-screens.md](./web-screens.md).

---

## Context pack (progressive)

`POST /projects/{project_id}/context-packs/scene`

| Rule | Detail |
|------|--------|
| Input | `chapter_id`, optional `beat_ids[]` |
| Output | Beats with `goal`, `conflict`, `outcome`, `stakes_level`, `pressure_tags` |
| Omit | Empty beats unless `include_empty=true` |
| Cap | Max 12 beats per pack |

Relationship/stakes packs compose separately — only edges/checkpoints referenced in beat `pressure_tags` or scene character list.

---

## Links

- [schema.md](./schema.md) — migration `020`
- [stakes.md](./stakes.md) — S5 cross-link
- [openapi.yaml](./openapi.yaml)
- Skill: `storyforge-continuity`
