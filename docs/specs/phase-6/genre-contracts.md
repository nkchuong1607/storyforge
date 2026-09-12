# Phase 6 Genre Contracts — Rule Packs & Continuity Tuning

> Formalizes genre promises, forbidden patterns, and expected payoffs.  
> Extends Phase 4 implicit `genre_profile` strictness with explicit JSON rule packs.

Each project carries:

- **`genre_profile`** — enum tag for templates, wizard, UI labels
- **`genre_rule_pack_json`** — tunable contract (this document)

Continuity engine merges **defaults(base_profile) + project overrides** at check time.

---

## Rule pack JSON schema

Stored in `projects.genre_rule_pack_json`:

```json
{
  "schema_version": 1,
  "base_profile": "xianxia",
  "display_name": "Kiếm hiệp tu chân",
  "modules": {
    "power_system": { "enabled": true },
    "foreshadow": { "enabled": true },
    "psychology": { "enabled": true },
    "timeline": { "enabled": true }
  },
  "strictness": {
    "foreshadow": "relaxed",
    "power": "strict",
    "psychology": "standard"
  },
  "promises": [
    "Cảnh giới leo thang có căn cứ; breakthrough được foreshadow",
    "Vật phẩm / công pháp có cost"
  ],
  "forbidden": [
    "Nhảy cảnh giới không breakthrough ở strict mode",
    "Payoff twist không plant (mystery strict)"
  ],
  "expected_payoffs": [
    { "kind": "cultivation_breakthrough", "by_chapter_percent": 25 },
    { "kind": "twist_reveal", "by_chapter_percent": 60 }
  ],
  "thresholds": {
    "foreshadow_min_plants_default": 1,
    "foreshadow_payoff_without_plants": "warn",
    "power_max_rank_jump_per_chapter": 1,
    "power_combat_upset": "fail"
  },
  "tone": {
    "primary": "vi",
    "violence_ceiling": "moderate",
    "romance_subplot": "optional"
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | integer | Pack migrator version |
| `base_profile` | string | Mirrors `GenreProfile` enum |
| `modules.*.enabled` | boolean | Off switch per subsystem |
| `strictness.*` | string | `strict`, `relaxed`, `standard` |
| `promises` | string[] | Author-facing genre contract (UI) |
| `forbidden` | string[] | Shown in Continuity Gate help |
| `expected_payoffs` | object[] | Planning hints — not auto-FAIL in Phase 6 |
| `thresholds` | object | Overrides numeric defaults |

---

## Default packs by `genre_profile`

Seeded on `POST /projects` (wizard). PATCH may override any field.

### `xianxia`

| Setting | Default |
|---------|---------|
| `modules.power_system.enabled` | `true` |
| `strictness.power` | `strict` |
| `strictness.foreshadow` | `relaxed` |
| `thresholds.foreshadow_min_plants_default` | `1` |
| `thresholds.foreshadow_payoff_without_plants` | `warn` |
| `thresholds.power_combat_upset` | `fail` |

### `mystery`

| Setting | Default |
|---------|---------|
| `modules.power_system.enabled` | `false` |
| `strictness.foreshadow` | `strict` |
| `thresholds.foreshadow_min_plants_default` | `2` |
| `thresholds.foreshadow_payoff_without_plants` | `fail` |
| `strictness.psychology` | `standard` |

### `literary`

| Setting | Default |
|---------|---------|
| `modules.power_system.enabled` | `false` |
| `strictness.foreshadow` | `relaxed` |
| `modules.psychology.enabled` | `true` |
| Most thresholds | relaxed WARN defaults |

### `romance`

| Setting | Default |
|---------|---------|
| `modules.power_system.enabled` | `false` |
| `strictness.psychology` | `standard` |
| `tone.romance_subplot` | `primary` |

### `custom`

Empty pack `{}` with `base_profile: custom` — author configures in Project Settings.

---

## How packs tune continuity severity

| Continuity category | Tuning mechanism |
|--------------------|------------------|
| `foreshadow` | `thresholds.foreshadow_*` overrides Phase 4 [fairness-rules](../phase-4/fairness-rules.md) table; per-twist `genre_strictness` still wins |
| `power_system` | `modules.power_system.enabled`; `strictness.power`; numeric thresholds mirror `power_system_settings` unless pack stricter |
| `psychology` | Phase 5 rules unchanged; `strictness.psychology = strict` upgrades WARN → FAIL for OOC (optional implementation flag) |
| `timeline`, `character` | `modules.*.enabled` skip category entirely |

**Merge order:**

1. Phase rule hardcoded floor (e.g. deceased character)
2. `genre_rule_pack_json.thresholds`
3. `power_system_settings` project config
4. Per-entity overrides (`twist_plans.genre_strictness`)

---

## Genre promises vs forbidden (author UX)

**Project Settings → Genre contract** panel displays:

- **Promises** — what readers expect (editable markdown list)
- **Forbidden** — patterns continuity will flag harder
- **Module toggles** — enable/disable power, foreshadow strictness preset

Wizard **Genre step** selects card → seeds pack → preview promises before confirm.

---

## API surface

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/projects/{id}/genre-rule-pack` | Full merged pack + defaults metadata |
| PATCH | `/projects/{id}/genre-rule-pack` | Partial merge; validates schema_version |
| POST | `/projects/{id}/genre-rule-pack/reset` | Reset to defaults for `base_profile` |

Changing `genre_profile` on project PATCH **does not** auto-reset pack — author must call reset (avoid silent rule changes).

---

## Hybrid / multi-tag genres (Phase 6 note)

Phase 6 supports **single** `base_profile` only. Future: `tags: ["xianxia", "mystery"]` with conflict resolution UI (Phase 8+).

---

## Links

- [Phase 4 fairness-rules](../phase-4/fairness-rules.md)
- [power-rules.md](./power-rules.md)
- [schema.md](./schema.md)
- [api-contracts.md](./api-contracts.md)
- [web-screens.md](./web-screens.md)
