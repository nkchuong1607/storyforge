---
name: storyforge-characters
description: StoryForge progressive character bible — tiers T0–T3, provisional inbox, canonical IDs, merge workflow for large casts.
---

# StoryForge Characters Skill

Use when implementing cast management, extraction, or character-scoped context packs.

## Tier Model

| Tier | Label | Minimum fields |
|------|-------|----------------|
| T0 | Seed | name, role, one-line |
| T1 | Stub | + voice hint, first relations |
| T2 | Active | + psyche card skeleton, goals |
| T3 | Principal | + arc, secrets, full psyche |

Promote tier on recurrence rules or manual author action — never auto-promote to T3.

## Provisional Inbox

Fact extractor may propose `character_provisional` rows from prose:

- Author actions: **merge** (into canonical ID), **promote new**, **reject** (ignore mention)
- Never assign canonical ledger events to provisional IDs

## Canonical IDs

UUID stable across renames. Display name changes append metadata events, not ID changes.

## Context Packs

Include only characters in scene beat + T3 always if POV. Cap stub count; prefer ledger tail over full bios.

## Large Cast (xianxia scale)

Lazy depth: thousands of T0/T1 stubs OK; deep cards only for scene participants. Retrieval via pgvector on names/aliases (Phase 3).

## Related

- `storyforge-psychology` — psyche card + PsychState
- `storyforge-domain-canon` — ledger writes on settle
