# Phase 6 Power Rules — Anti-Creep Deterministic v1

> Canonical deterministic rules for Phase 6 continuity engine extension.  
> Implements `storyforge-power-system` + `storyforge-continuity` for category **`power_system`**.

Phase 6 adds **deterministic** power checks only. LLM semantic rank detection is optional stub — keyword + ledger first.

---

## Rule engine placement

| Component | Responsibility |
|-----------|----------------|
| `continuity/engine.py` | New `power_system` rule module in check pipeline |
| `power_ranks`, `power_techniques`, `power_system_settings` | Read-only during check (staging + bible snapshot) |
| `ledger_events` | Latest settled `cultivation_change`, `technique_learned` |
| `continuity_overrides` | Mark intentional — suppresses matching fingerprint |
| `projects.genre_rule_pack_json` | `modules.power_system.enabled` off switch |

**Rule pack version:** append `+power-v1` in continuity report when Phase 6 rules run.

**Skip conditions:**

- `power_system_settings.enabled = false` OR `genre_rule_pack.modules.power_system.enabled = false`
- `genre_profile` in `literary`, `mystery`, `romance` with power module disabled (default)
- Scene has no characters with prior rank ledger (rules P3/P4 may still WARN on prose keywords)

---

## Rank resolution

| Source | Precedence |
|--------|------------|
| Settled `ledger_events` (`cultivation_change`) | **Authoritative** for character rank at chapter N-1 |
| Prose keyword match against `power_ranks.display_name` / `rank_key` | Detect **claimed** rank in draft |
| Bible snapshot `world.power_system.ranks` | Ladder order for delta math |

**Rank order:** `sort_order` ascending (0 = lowest). Sub-stages compare within same `rank_id` via `sub_stages[].sort_order`.

---

## Rule P1 — Rank jump without breakthrough

**When:** Continuity check on chapter `C`; character appears in scene cast; prose claims rank R2; last settled rank R1; `sort_order(R2) - sort_order(R1) > max_rank_jump_per_chapter`.

**Condition:** No approved `cultivation_change` proposal in current `state_diff` with `breakthrough: true` covering the jump, AND no settled breakthrough event in same chapter draft window.

| Severity | Code | Message (VI template) |
|----------|------|-------------------------|
| **FAIL** | `power_rank_jump_without_breakthrough` | {character} nhảy cảnh giới {from} → {to} không có breakthrough (max {max}/chương) |

**Fingerprint:** `power:{character_id}:rank_jump:{from_rank_id}:{to_rank_id}:ch{C.number}`

**Override:** `POST .../continuity-overrides` with reason (same as Phase 2 FAIL).

---

## Rule P2 — Rank regression

**When:** Prose claims rank lower than last settled rank without compensating ledger event.

| Severity | Code |
|----------|------|
| **FAIL** | `power_rank_regression` |

**Fingerprint:** `power:{character_id}:regression:{from}:{to}`

**Exception:** `supersedes_event_id` correction chain in approved state_diff (rare retcon — author must approve).

---

## Rule P3 — Technique eligibility

**When:** Prose mentions technique display name or key from `power_techniques`.

**Condition:** Character's effective rank < technique `min_rank_id` AND no settled `technique_learned` for that technique.

| Severity | Code |
|----------|------|
| **FAIL** | `power_technique_ineligible` |

**Fingerprint:** `power:{character_id}:technique:{technique_id}`

**Sect/lineage gates (Phase 6 v1):**

- If `sect_requirement` set and character affiliation (ledger/bible) mismatches → **WARN** `power_technique_sect_mismatch` (upgrade to FAIL if `genre_rule_pack.strictness.power = strict`).

---

## Rule P4 — Defeating higher rank without justification

**When:** Prose describes combat outcome where loser rank order > winner rank order + `priority_gap`.

**Condition:** No ledger refs to qualifying technique/item in prose metadata beats OR approved state_diff proposals.

| Severity | Code |
|----------|------|
| **FAIL** (xianxia strict) / **WARN** (relaxed) | `power_upset_without_justification` |

**Fingerprint:** `power:combat:{chapter_id}:{winner_id}:{loser_id}`

**Genre tuning:** See [genre-contracts.md](./genre-contracts.md) — `priority_gap` from `power_system_settings`.

---

## Rule P5 — Unknown rank label (stub)

**When:** Prose contains cultivation keyword from project glossary but label not in ladder.

| Severity | Code |
|----------|------|
| **WARN** | `power_unknown_rank_label` |

Replaces Phase 2 `world_rule_rank_violation_stub` when power module enabled.

---

## State diff extract (cultivation proposals)

Phase 6 extract extends settle stub:

```json
{
  "ledger_proposals": [
    {
      "entity_type": "character",
      "entity_id": "770e8400-e29b-41d4-a716-446655440002",
      "event_type": "cultivation_change",
      "payload": {
        "from_rank_id": "a1000000-0000-4000-8000-000000000001",
        "to_rank_id": "a1000000-0000-4000-8000-000000000002",
        "breakthrough": true,
        "method": "pill + seclusion"
      },
      "confidence": "extract_stub"
    }
  ],
  "power_system_snapshot_patch": {
    "action": "sync_staging_to_bible",
    "rank_count": 9,
    "technique_count": 12
  }
}
```

Author approves at settle → ledger append + bible `world.power_system` refresh.

---

## Interaction with other categories

| Category | Interaction |
|----------|-------------|
| `foreshadow` | Independent; genre pack may stricten both |
| `psychology` | Independent |
| `world_rule` | P5 supersedes rank stub when power enabled |
| `character` | Death still blocks alive appearance |

---

## Test vectors (implementation)

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Jump 2 ranks, no breakthrough | FAIL `power_rank_jump_without_breakthrough` |
| 2 | Jump 1 rank with breakthrough in state_diff | PASS |
| 3 | Use technique above rank | FAIL `power_technique_ineligible` |
| 4 | Mystery project, power disabled | Rules skipped |
| 5 | Override FAIL fingerprint | Settle proceeds |
| 6 | Combat upset across priority_gap | FAIL or WARN per genre |

---

## Deferred

- LLM-based rank mention extraction
- Dynamic priority_gap per technique type
- Cross-project rank templates

---

## Links

- [schema.md](./schema.md)
- [genre-contracts.md](./genre-contracts.md)
- [api-contracts.md](./api-contracts.md)
- [test-strategy.md](./test-strategy.md)
