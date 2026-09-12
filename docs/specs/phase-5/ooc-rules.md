# Phase 5 OOC Rules — Psychology Continuity (Deterministic v1)

> Canonical deterministic rules for Phase 5 continuity engine extension.  
> Implements `storyforge-psychology` + `storyforge-continuity` for category **`psychology`**.

Phase 5 adds **deterministic** psychology checks only. LLM voice-drift / subtle OOC detection is **optional later** (Phase 6+); note in report metadata when absent.

---

## Rule engine placement

| Component | Responsibility |
|-----------|----------------|
| `continuity/engine.py` | New psychology rule module in existing check pipeline |
| `characters.psyche_card` | Moral boundaries, value hierarchy, arc flags |
| `psych_states` | Prior chapter snapshots for earned-change comparison |
| `continuity_overrides` | Mark intentional — suppresses matching `issue.fingerprint` |
| `scene_beats` / prose scan | Keyword/heuristic triggers for stub extract |

**Rule pack version:** append `+psychology-v1` in report when Phase 5 rules run.

---

## Prerequisites for psychology checks

| Condition | Behavior |
|-----------|----------|
| Character tier ≥ T2 with non-empty `psyche_card` | Rules apply |
| Character tier T0–T1 or empty card | Rules **skipped** (no false positives on extras) |
| Scene character not in chapter beats | Optional WARN `psych_character_not_in_scene` — implementation may skip Phase 5 |

Checks run for characters **mentioned in prose** or listed in scene beats for the checked chapter.

---

## Rule P1 — OOC moral boundary violation

**When:** Continuity check on chapter `C`; character `K` tier ≥ T2 with `moral_boundaries[]` non-empty.

**Condition:** Prose (or beat metadata action tags) contains action verbs/patterns matching a crossed boundary without:

1. Active `continuity_override` for this fingerprint, OR
2. `psyche_card.arc_flags.allow_moral_break = true`, OR
3. Matching `arc_beat` registered in current chapter proposal.

**Detection (deterministic stub v1):**

- Maintain boundary → keyword map per locale (VI primary): e.g. `"không giết vô tội"` → patterns `["giết.*vô tội", "hạ sát dân thường"]`.
- Match within ±N characters of character `display_name` or alias in prose.

| Severity | Code | Message (VI template) |
|----------|------|-------------------------|
| FAIL (default) | `psych_ooc_moral_boundary_violation` | `{name}` vi phạm ranh giới đạo đức "{boundary}" ở ch.{n} |
| WARN | `psych_moral_boundary_crossed` | Same — used when `arc_flags.expected_arc_beats` contains pending break beat |

**Fingerprint:**

```text
psych:{character_id}:ooc_moral:{boundary_hash}:{chapter_id}
```

**Override:** `POST .../continuity-overrides` with non-empty `reason` — Mark intentional.

---

## Rule P2 — Value hierarchy jump

**When:** Character has `value_hierarchy[]` with ≥ 2 entries; belief update or action implies top value demoted without earned path.

**Condition:** Extract or beat tag suggests character acted against value at index `i` while claiming value at index `j` (j > i) as dominant, AND no `belief_updates` proposal with `trigger_event_refs` in state_diff for this chapter.

| Severity | Code |
|----------|------|
| WARN | `psych_value_hierarchy_jump` |

**Example:** Hierarchy `["gia đình", "công lý"]`; prose shows abandoning family for revenge without prior stress arc → WARN.

**Fingerprint:** `psych:{character_id}:value_jump:{from_value}:{to_value}:{chapter_id}`

**Earned change escape:** Approved `psych_state_proposal` with non-empty `belief_updates` + `trigger_event_refs` downgrades to PASS or INFO-only.

---

## Rule P3 — Arc beat skip

**When:** `psyche_card.arc_flags.expected_arc_beats[]` is non-empty.

**Condition:** Current chapter prose implies a later beat (e.g. redemption) without recorded prior beat (e.g. betrayal), based on ordered list or explicit beat labels in metadata.

| Severity | Code |
|----------|------|
| WARN | `psych_arc_beat_skip` |

**Fingerprint:** `psych:{character_id}:arc_skip:{expected_beat}:{chapter_id}`

**Escape:** `psych_state_proposal.arc_beat` matches expected next beat OR override.

---

## Rule P4 — Unearned personality shift (belief without trigger)

**When:** State diff or extract proposes `belief_updates` for character `K`.

**Condition:** Any update has empty `trigger_event_refs` AND prior psych state exists AND change contradicts `psyche_card.drive`/`need` without `stress_level` increase ≥ 3 from prior snapshot.

| Severity | Code |
|----------|------|
| WARN | `psych_unearned_belief_shift` |

**Fingerprint:** `psych:{character_id}:unearned_belief:{chapter_id}`

**Settle gate:** WARN does not block settle; author should confirm in state diff panel.

---

## Rule P5 — Stress / voice taboo (light deterministic)

**When:** `voice_taboo[]` non-empty; prose contains taboo phrase in character dialogue attribution.

**Condition:** Simple substring match on dialogue blocks tagged with character id (extract attributes speaker from `"..." — Name` pattern).

| Severity | Code |
|----------|------|
| WARN | `psych_voice_taboo_break` |

LLM semantic voice drift deferred Phase 6+.

---

## Earned change heuristics (settle extract)

Extract stub on continuity check / state-diff GET proposes `psych_state_proposals[]`:

| Signal | Proposal field |
|--------|----------------|
| Beat goal/conflict metadata | `active_goal`, `stress_level` delta |
| Death/betrayal keywords near name | `belief_updates`, `relationship_stance` |
| Prior psych state + stress keywords | `dominant_emotion`, `stress_level` |
| Arc metadata on beat | `arc_beat` |

Each proposal MUST include:

```json
{
  "character_id": "uuid",
  "chapter_id": "uuid",
  "stress_level": 6,
  "dominant_emotion": "anger",
  "active_goal": "Đối đầu sư phụ",
  "belief_updates": [],
  "relationship_stance": [],
  "value_pressure": "công lý",
  "arc_beat": null,
  "trigger_event_refs": ["beat:uuid"],
  "confidence": "extract_stub"
}
```

**Approval:** Settle with `approve_state_diff: true` appends approved proposals to `psych_states` with `settled_at = now()`.

---

## Mark intentional (unchanged semantics)

Same as Phase 2–4:

| Topic | Rule |
|-------|------|
| WARN override | Allowed; settle proceeds |
| FAIL override | Allowed with non-empty `reason`; settle proceeds |
| Fingerprint scope | Per `chapter_id` + `issue_fingerprint` |
| Override effect | Suppresses issue in gate only — does not mutate psyche card |

Authors use Continuity Gate **Mark intentional** for deliberate moral breaks (e.g. corruption arc).

---

## Severity summary

| Code | Default severity | Blocks settle |
|------|----------------|---------------|
| `psych_ooc_moral_boundary_violation` | FAIL | Yes, unless override |
| `psych_moral_boundary_crossed` | WARN | No |
| `psych_value_hierarchy_jump` | WARN | No |
| `psych_arc_beat_skip` | WARN | No |
| `psych_unearned_belief_shift` | WARN | No |
| `psych_voice_taboo_break` | WARN | No |

Genre strictness: Phase 5 psychology rules do **not** vary by `genre_profile` (unlike foreshadow). Future genre packs may tighten in Phase 6.

---

## Test vectors (implementation)

| # | Scenario | Expected |
|---|----------|----------|
| 1 | T3 character kills innocent; no arc flag | FAIL `psych_ooc_moral_boundary_violation` |
| 2 | Same + override with reason | Gate pass; settle OK |
| 3 | Same + `allow_moral_break: true` | WARN or PASS |
| 4 | Value jump without belief trigger | WARN `psych_value_hierarchy_jump` |
| 5 | Skip arc beat redemption before betrayal | WARN `psych_arc_beat_skip` |
| 6 | Settle with psych proposal | Row in `psych_states`; immutable |
| 7 | PATCH settled psych_state | 409 `psych_state_immutable` |
| 8 | T0 extra — kill innocent | No psychology issue (rules skipped) |

---

## Links

- [schema.md](./schema.md)
- [api-contracts.md](./api-contracts.md)
- [test-strategy.md](./test-strategy.md)
- [Phase 2 continuity overrides](../phase-2/continuity-rules.md#intentional-override-semantics)
- Skill: `skills/storyforge-psychology/SKILL.md`
