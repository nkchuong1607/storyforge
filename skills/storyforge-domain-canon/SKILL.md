---
name: storyforge-domain-canon
description: StoryForge Story Bible versioning, append-only ledgers, human approve-before-write for prose and state diff settlement.
---

# StoryForge Domain & Canon Skill

Use when implementing bible, chapters, settlement, or any canon mutation.

## Read First

- `docs/domain-model.md`
- `docs/schema-draft.md`

## Invariants (never violate)

1. **Bible versions are immutable** — Create `N+1` on settle; never UPDATE version `N`.
2. **Ledgers are append-only** — Corrections add new events with `supersedes_event_id`.
3. **Two human gates** — (a) prose accepted, (b) state diff approved before settle.
4. **Drafts pin bible version** — `bible_version_at_draft` on chapter records.

## Settlement Sequence

```
save draft → continuity check → fix/mark intentional → extract state diff → approve diff → SETTLE (txn)
```

Settle transaction must:

- Append all approved ledger events with `settled_at`
- Write new `bible_versions` row
- Bump `projects.bible_version_current`
- Set chapter `status = settled`

## State Diff Preview

Show before/after for: character status, location, cultivation, new canon candidates. Reject returns draft to editing; no ledger writes.

## Git Mirror (later)

Markdown/YAML export is derived from settled bible versions, not source of truth.

## Anti-Patterns

- Auto-settle after LLM extract
- Silent overwrite of character rank or death status
- Loading full bible into LLM prompts
