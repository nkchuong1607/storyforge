# StoryForge Domain Model

Entities and invariants for canon, continuity, and the author workflow.

## Project

Top-level isolation boundary.

| Field | Notes |
|-------|-------|
| `id`, `slug`, `title` | Unique per workspace |
| `genre_profile` | xianxia, mystery, literary, etc. — drives power-system and twist skills |
| `bible_version_current` | Pointer to settled canon version |
| `settings` | Locale, tone, target word counts |

## Story Bible (versioned)

Immutable snapshot of settled canon at version `N`.

| Section | Contents |
|---------|----------|
| World | Rules, locations, factions, power system definition |
| Timeline | Ordered anchor events |
| Characters | Core entries + tier metadata |
| Objects | Named artifacts, MacGuffins |
| Glossary | Terms, ranks, techniques |

**Invariant:** Draft work references `bible_version_at_draft`; settlement creates version `N+1`. Never mutate version `N`.

## Chapter

| Field | Notes |
|-------|-------|
| `number`, `title` | Ordering within project |
| `status` | `outline` → `drafting` → `continuity_pending` → `settled` |
| `scene_beats[]` | Ordered beats (7.1, 7.2, …) with completion flags |
| `prose_versions[]` | Append-only; each has `version`, `content`, `source` (human/ai) |

## Scene Beat

Granular unit inside a chapter. Context packs often scope to one beat + neighbors.

## Ledgers (append-only)

All ledgers share: `project_id`, `entity_type`, `entity_id`, `event_type`, `payload`, `chapter_ref`, `settled_at`, `supersedes_event_id?`.

### Character State Ledger

- Status: alive, deceased, missing, transformed
- Location, affiliation, cultivation/power rank
- Injuries, resources, relationships (pointers)

### Object Ledger

- Ownership, location, condition, revealed properties

### Knowledge Ledger

- Who knows what; revelation events; reader vs character knowledge

### Promise / Foreshadow Ledger

- Plants, hints, open threads, payoff links

## Character (progressive bible)

| Tier | Depth | When populated |
|------|-------|----------------|
| T0 Seed | Name, role, one-line | Architect / manual |
| T1 Stub | Voice hint, relationships | First mention in prose |
| T2 Active | Psyche card, goals, secrets | Recurring scenes |
| T3 Principal | Full backstory, arc plan | POV or major plot |

**Provisional inbox:** Extracted mentions await human approve/merge/reject before canonical ID assignment.

## Psyche Card + PsychState Ledger

- **Psyche card:** Stable traits, wounds, desires, speech patterns, moral lines.
- **PsychState ledger:** Append-only emotional/ belief snapshots per chapter.
- **Earned change:** Personality shifts require documented triggering events; OOC flagged by continuity.

## TwistPlan Ledger

| Concept | Description |
|---------|-------------|
| `secret_truth` | Ground fact (author-only until reveal) |
| `plants` | Fair hints placed in text |
| `misdirection` | Deliberate false trails |
| `payoff` | Linked plant IDs + chapter target |

**Fairness gate:** Payoff without registered plants → FAIL unless marked intentional.

## Continuity Report

Result of deterministic + LLM audit on a draft version.

| Severity | Meaning |
|----------|---------|
| PASS | Check satisfied |
| WARN | Possible issue; author may mark intentional |
| FAIL | Blocks settle until fixed or overridden with reason |

Categories: character, timeline, world_rule, foreshadow, psychology, power_system.

## State Diff Preview

Proposed ledger append batch + bible patch candidates extracted from prose. Author approves before `settle` commits transaction.

## Context Pack

Structured bundle for agents:

```yaml
project_id: ...
bible_version: 12
chapter: 7
beat: 7.4
canon_snippets: [...]
ledger_tail: [...]      # last K events for involved entities
twist_relevant: [...]  # active plants only
psych_states: [...]
word_budget: 8000
```

Never include full manuscript text.

## Settlement Workflow

1. Author saves draft (`prose_version++`).
2. Continuity check → report.
3. Author fixes prose or marks issues intentional.
4. Fact extractor produces state diff.
5. Author approves diff.
6. API appends ledger events + publishes `bible_version++` atomically.

## Related

- [Schema draft](./schema-draft.md)
- [Architecture](./architecture.md)
