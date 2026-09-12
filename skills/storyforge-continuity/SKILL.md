---
name: storyforge-continuity
description: StoryForge continuity — deterministic rule checks plus LLM auditor; PASS/WARN/FAIL severities and intentional author overrides.
---

# StoryForge Continuity Skill

Use when building Continuity Gate, auditors, or issue resolution flows.

## Read First

- `docs/domain-model.md` (Continuity Report, categories)
- Wireframe context in `docs/architecture.md`

## Two-Stage Audit

### 1. Deterministic (fast, required for MVP)

Rule engine over ledger + bible snapshot:

- Character marked deceased cannot appear alive without `transformed` event
- Timeline: event A before B if ledger order says so
- Location conflicts at same narrative time
- Power rank monotonicity (see `storyforge-power-system`)
- Twist plant registry for payoff chapters

Return structured issues: `{ severity, category, description, chapter_ref, entity_ids }`.

### 2. LLM Auditor (Phase 2)

Semantic checks: foreshadow fairness, subtle OOC, world-rule nuance. Same issue schema. Never auto-settle on LLM output alone.

## Severities

| Level | Blocks settle? | UI |
|-------|----------------|-----|
| PASS | — | Green check |
| WARN | No (default) | Author may "Mark intentional" |
| FAIL | Yes | Must fix or explicit override with reason |

## Intentional Overrides

Store in `continuity_overrides`: issue fingerprint, author note, timestamp. Auditors skip matching fingerprints on re-run.

## API Shape (sketch)

```
POST /projects/{id}/chapters/{id}/continuity-check
→ { result: pass|warn|fail, issues: [...], stats: { passed, warnings, errors } }
```

## Related

- `storyforge-characters`, `storyforge-twists`, `storyforge-psychology`
