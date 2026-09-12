---
name: storyforge-twists
description: StoryForge TwistPlan ledger — secret_truth, plants, misdirection, payoff links, and fairness gates for mystery and cultivation reveals.
---

# StoryForge Twists Skill

Use when implementing plot secrets, foreshadow tracking, or continuity fairness checks.

## TwistPlan Entities

- **secret_truth** — Ground fact; author-visible; not in reader-facing bible export until reveal
- **plants** — `{ id, chapter, beat, strength, snippet_ref }` fair hints
- **misdirection** — Optional false trails linked to same secret
- **payoff** — `{ secret_id, target_chapter, required_plant_ids[] }`

## Fairness Rules

1. Payoff chapter triggers continuity **FAIL** if `required_plant_ids` empty and not marked intentional
2. **Strength** enum: subtle, moderate, explicit — auditor weights accordingly
3. Reveal must not contradict settled ledger without compensating event

## Context Packs for Writer

Pass active secrets' *plants only* to Writer — never `secret_truth` unless Editor/Architect role.

## Mystery vs Xianxia

Same ledger schema; genre_profile selects default strictness (mystery: stricter plant requirements).

## UI (future)

Twist dashboard: plant/payoff graph. Bootstrap does not implement UI.

## Related

- `storyforge-continuity` — foreshadow category checks
- `storyforge-domain-canon` — secrets not in public bible snapshot until reveal event
