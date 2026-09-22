# Mystery Craft Pack — `mystery.fair_play.v1`

> Canonical JSON schema and checklist rules for Phase 11a.

---

## Pack identity

| Field | Value |
|-------|-------|
| `id` | `mystery.fair_play.v1` |
| `display_name` | Mystery — Fair Play |
| `genre_tags` | `["mystery"]` |
| `min_app_phase` | 10 |

---

## JSON schema (v1)

```json
{
  "schema_version": 1,
  "id": "mystery.fair_play.v1",
  "display_name": "Mystery — Fair Play",
  "genre_tags": ["mystery"],
  "compat": {
    "requires_genre_profiles": ["mystery", "custom"],
    "min_app_phase": 10
  },
  "structure": {
    "template_id": "mystery_three_act_fair_play",
    "beats": [
      { "key": "hook", "act": 1, "required": true },
      { "key": "crime_or_puzzle", "act": 1, "required": true },
      { "key": "investigation_loop", "act": 2, "required": true },
      { "key": "midpoint_reversal", "act": 2, "required": true },
      { "key": "fair_clue_cluster", "act": 2, "required": true },
      { "key": "false_solution", "act": 2, "required": false },
      { "key": "reveal", "act": 3, "required": true },
      { "key": "payoff_wrap", "act": 3, "required": true }
    ]
  },
  "checklist": [
    {
      "id": "clue_before_reveal",
      "severity_default": "fail",
      "continuity_category": "foreshadow",
      "code": "craft_mystery_clue_after_reveal",
      "description": "Every reveal claim must map to ≥1 planted clue with earlier chapter_ref"
    },
    {
      "id": "red_herring_labeled",
      "severity_default": "warn",
      "continuity_category": "craft",
      "code": "craft_mystery_unlabeled_misdirection",
      "description": "Misdirection without TwistPlan misdirection entry"
    },
    {
      "id": "detective_knowledge_ledger",
      "severity_default": "warn",
      "continuity_category": "craft",
      "code": "craft_mystery_reader_spoiler",
      "description": "Reader-known secret appears in detective POV without knowledge ledger event"
    },
    {
      "id": "fair_play_min_clues",
      "severity_default": "fail",
      "continuity_category": "foreshadow",
      "code": "craft_mystery_insufficient_plants",
      "description": "Payoff requires ≥2 plants (align with mystery rule-pack threshold)"
    }
  ],
  "prompt_hooks": {
    "context_pack_extra_keys": ["craft_checklist_open", "active_clues", "active_misdirections"],
    "prompt_edit_skills": ["mystery_clue_plant", "mystery_reveal_align", "mystery_red_herring"]
  },
  "golden": {
    "fixture_project_slug": "golden-mystery-fair-play",
    "min_seeded_flags": 3,
    "fakellm_coverage_target": 0.9
  }
}
```

---

## Checklist evaluation (deterministic first)

| Rule ID | Code | Category | Severity | Trigger |
|---------|------|----------|----------|---------|
| `clue_before_reveal` | `craft_mystery_clue_after_reveal` | `foreshadow` | fail | Payoff chapter with zero plants registered before target |
| `fair_play_min_clues` | `craft_mystery_insufficient_plants` | `foreshadow` | fail | Payoff `min_plants` not met (default 2 for mystery) |
| `red_herring_labeled` | `craft_mystery_unlabeled_misdirection` | `craft` | warn | Prose contains misdirection marker without `twist_plans.misdirection` |
| `detective_knowledge_ledger` | `craft_mystery_reader_spoiler` | `craft` | warn | `secret_truth` substring in prose with active knowledge wall |

**LLM path:** Optional soft WARN via FakeLLM craft skills when `STORYFORGE_CRAFT_LLM=1` — never FAIL from LLM alone.

**Plant ledger:** Reuse Phase 4 `twist_plants` — no duplicate ledger.

---

## Prompt Edit injection

On `instruct` / `regenerate`, when active craft pack present:

| Slice | Content |
|-------|---------|
| `craft_beats` | Structure beat keys from pack |
| `craft_checklist_open` | Checklist items not satisfied for current chapter |
| `active_clues` | Plants from TwistPlan (no `secret_truth`) |
| `active_misdirections` | Twists with `misdirection` set |

Inject-only — Editor LLM receives context; output is author-controlled via Apply.

---

## Links

- [schema.md](./schema.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 4 fairness](../phase-4/fairness-rules.md)
