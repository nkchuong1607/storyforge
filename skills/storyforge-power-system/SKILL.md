---
name: storyforge-power-system
description: StoryForge power and cultivation systems — rank ladders, costs, priority gaps, and anti power-creep rules for xianxia and similar genres.
---

# StoryForge Power System Skill (stub)

Use when defining or validating cultivation ranks, techniques, and combat outcomes in xianxia / progression fantasy projects.

## Bible Section

`bible_versions.snapshot_json.world.power_system`:

- Ordered **ranks** (e.g. Qi Refining → Golden Core)
- **Techniques** with requirements (sect, lineage, resource cost)
- **Priority gap** — minimum rank delta to guarantee outcome (configurable)

## Ledger Events

- `cultivation_change` — rank, sub-stage, method
- `technique_learned` — id, constraints
- `resource_consumed` — pills, spirit stones

## Anti-Creep Rules (deterministic)

1. Rank cannot increase more than N stages per chapter without flagged breakthrough event
2. Technique use requires ledger proof of eligibility (sect membership, etc.)
3. Defeating higher rank requires explicit technique/item ledger refs or FAIL

## Genre Off Switch

Non-progression genres (mystery, literary): omit power_system block; continuity skips these checks.

## Related

- `storyforge-continuity` — world_rule category
- `storyforge-domain-canon` — world bible section
