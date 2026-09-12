---
name: storyforge-psychology
description: StoryForge psyche cards, PsychState append-only ledger, earned character change, and out-of-character continuity checks.
---

# StoryForge Psychology Skill

Use when modeling character interiority, emotional continuity, or OOC detection.

## Psyche Card (stable)

Stored on `characters.psyche_card` jsonb:

- Core traits, wounds, desires, fears
- Speech patterns, moral boundaries
- Relationship templates (trust/betrayal triggers)

Updated only via author edit or approved extract — not every draft.

## PsychState Ledger

Append-only snapshot per `(character_id, chapter_ref)`:

- Emotional state, beliefs, stressors
- Triggering events reference ledger event IDs

Writer context: latest PsychState + psyche card for scene POV characters.

## Earned Change

Personality or moral line shifts require:

1. Documented triggering events in prose (extracted to ledger)
2. Author approval in state diff
3. Optional WARN if shift lacks trigger; FAIL if contradicts psyche without arc flag

## OOC Checks

Deterministic: action vs `moral_boundaries` without override flag.

LLM auditor: subtle voice drift, inconsistent decision under stated stress.

## Related

- `storyforge-characters` — tier promotion includes psyche depth
- `storyforge-continuity` — psychology category
