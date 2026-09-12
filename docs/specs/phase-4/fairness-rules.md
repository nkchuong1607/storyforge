# Phase 4 Fairness Rules — TwistPlan / Foreshadow Continuity

> Canonical deterministic rules for Phase 4 continuity engine extension.  
> Implements `storyforge-twists` + `storyforge-continuity` for category **`foreshadow`**.

Phase 4 adds **deterministic** foreshadow checks only. LLM semantic plant detection is deferred to Phase 6+.

---

## Rule engine placement

| Component | Responsibility |
|-----------|----------------|
| `continuity/engine.py` | New foreshadow rule module invoked from existing check pipeline |
| `twist_plans` / `twist_plants` / `twist_payoffs` | Read-only during check |
| `continuity_overrides` | Existing Mark intentional — suppresses matching `issue.fingerprint` |
| `projects.genre_profile` | Default strictness: `mystery` stricter than `xianxia` |

**Rule pack version:** `deterministic-v1` → append `+foreshadow-v1` in report when Phase 4 rules run.

---

## Genre strictness defaults

| `genre_profile` | Default | Payoff without plants | `min_plants` default |
|-----------------|---------|------------------------|---------------------|
| `mystery` | **strict** | **FAIL** | `2` if not set on payoff |
| `xianxia` | relaxed | **WARN** (upgrade to FAIL if `genre_strictness=strict` on twist) | `1` |
| `literary` | relaxed | WARN | `1` |
| other | relaxed | WARN | `1` |

Per-twist `twist_plans.genre_strictness` overrides project default when set.

---

## Rule F1 — Payoff without plants

**When:** Continuity check on chapter `C` where ∃ payoff with `target_chapter_id = C.id` and twist `status IN (armed, planted, seeded)`.

**Condition:** Count of eligible plants for twist `< max(payoff.min_plants, constraints_json.min_plants_before_payoff, genre_default_min)`.

Eligible plants: rows in `twist_plants` where `chapter.number < C.number` OR `chapter_id = C.id` with plant snippet registered before check (Phase 4: all plants with `chapter.number <= C.number`).

| Severity | Code | Message (VI template) |
|----------|------|-------------------------|
| FAIL (strict) / WARN (relaxed) | `foreshadow_payoff_without_plants` | Payoff ch.{n} cho "{title}" thiếu plant (cần {min}, có {count}) |

**Fingerprint:**

```text
foreshadow:{twist_id}:payoff_without_plants:{target_chapter_id}
```

**Override:** Existing `POST .../continuity-overrides` with non-empty `reason` — same semantics as Phase 2 FAIL override.

---

## Rule F2 — Required plant IDs missing

**When:** Payoff has non-empty `required_plant_ids`.

**Condition:** Any id in array not found in `twist_plants` for same twist, OR plant chapter number > target chapter number.

| Severity | Code |
|----------|------|
| FAIL | `foreshadow_required_plants_missing` |

**Fingerprint:** `foreshadow:{twist_id}:required_plants_missing:{plant_id}`

---

## Rule F3 — Plant count below minimum (explicit gate)

**When:** Payoff registered with `min_plants = N` where `N > 0`.

**Condition:** Eligible plant count < N (even if some plants exist).

| Severity | Code |
|----------|------|
| FAIL if strict else WARN | `foreshadow_plant_count_below_minimum` |

Distinct from F1 when partial plants exist but below explicit threshold.

---

## Rule F4 — Unseeded reveal (FAIL)

**When:** Prose in chapter `C` appears to reveal twist ground truth before plants registered.

**Phase 4 deterministic heuristic (MVP):**

1. Author flagged `constraints_json.constrained_facts[].revealed_in_prose = true` via optional manual marker in state diff — **or**
2. Payoff chapter check runs with **zero** plants anywhere for twist and prose contains `title` token match ≥3 times (case-fold) — **WARN only** unless `status = armed` → **FAIL**
3. Target chapter settle attempted while twist still `seeded` (no plants) → **FAIL** `foreshadow_unseeded_reveal`

| Severity | Code |
|----------|------|
| **FAIL** | `foreshadow_unseeded_reveal` |

**Fingerprint:** `foreshadow:{twist_id}:unseeded_reveal:{chapter_id}`

**Note:** Full NLP reveal detection is Phase 6 LLM auditor. Phase 4 FAIL is structural (no plants at payoff), not semantic paraphrase detection.

---

## Rule F5 — Constrained facts violation

**When:** `constraints_json.constrained_facts` lists keys that must remain hidden until payoff.

**Phase 4 check:** If prose version contains explicit `secret_truth` substring (author pasted secret into draft) → **FAIL**.

| Severity | Code |
|----------|------|
| FAIL | `foreshadow_constrained_fact_leaked` |

Writer context must never include `secret_truth` — this rule catches author accidental paste into prose.

---

## Rule F6 — Knowledge wall (WARN)

**When:** `constraints_json.knowledge_walls[]` lists character must not know before chapter N.

**Phase 4:** If character appears in scene and chapter number < N with dialogue implying secret knowledge (deterministic: quoted `secret_truth` substring attributed via `@character` in prose — optional heuristic) → **WARN** `foreshadow_knowledge_wall`.

Full OOC/psych integration Phase 5. Phase 4 stores walls; emits WARN when simple substring match.

---

## Continuity category extension

Add to `continuity_category` enum (Phase 4 migration on enum type):

| Value | Phase |
|-------|-------|
| `foreshadow` | **Phase 4** |

Phase 2 categories unchanged: `character`, `timeline`, `location`, `world_rule`, `bible_staging`.

**Issue JSON example:**

```json
{
  "fingerprint": "foreshadow:aa0e8400-e29b-41d4-a716-446655440099:payoff_without_plants:660e8400-e29b-41d4-a716-446655440005",
  "severity": "fail",
  "category": "foreshadow",
  "code": "foreshadow_payoff_without_plants",
  "message": "Payoff ch.12 cho \"Sát thủ là sư phụ\" thiếu plant (cần 2, có 0)",
  "chapter_refs": [12],
  "entity_ids": ["aa0e8400-e29b-41d4-a716-446655440099"],
  "evidence": {
    "twist_id": "aa0e8400-e29b-41d4-a716-446655440099",
    "twist_title": "Sát thủ là sư phụ",
    "min_plants": 2,
    "plant_count": 0,
    "payoff_id": "bb0e8400-e29b-41d4-a716-446655440088"
  }
}
```

**Never include `secret_truth` in `evidence` or `message` for responses consumed by Writer agents.**

---

## Intentional override semantics (unchanged from Phase 2)

| Topic | Rule |
|-------|------|
| Scope | Per `chapter_id` + `issue_fingerprint` |
| FAIL override | Allowed with non-empty `reason`; settle proceeds |
| Re-audit | Skips fingerprint if active override |
| Board UI | Payoff card red border clears when overridden OR plants added |

Mark intentional endpoint unchanged: `POST /projects/{project_id}/chapters/{chapter_id}/continuity-overrides`.

---

## Writer context pack strip

**Endpoint:** `POST /projects/{project_id}/context-packs/twists`

| Field | Included for Writer? |
|-------|----------------------|
| `twist_plans.secret_truth` | **Never** |
| `twist_plans.misdirection` | **Never** |
| `twist_plants.*` (active twists) | Yes — bounded list |
| Payoff targets | Optional chapter number only — no secret |

**Active twist definition:** `status IN (planted, armed)` with plants in chapters ≤ current chapter.

**Combined Writer pack (implementation note):** Chapter editor may call character pack + twist pack; merge into `twist_relevant[]` per [domain-model.md](../../domain-model.md).

---

## Settle interaction

| Scenario | Behavior |
|----------|----------|
| Effective foreshadow FAIL on payoff chapter | Settle blocked (`409 continuity_fail_blocks_settle`) unless overridden |
| Settle success on payoff chapter | Twist → `paid_off`, `twist_payoffs.revealed_at` set |
| Plants on locked chapters | Immutable — edit requires new plant in later draft chapter |

---

## Test vectors (implementation)

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Payoff ch.5, 0 plants, mystery project | FAIL `foreshadow_payoff_without_plants` |
| 2 | Same, xianxia project | WARN (strict override on twist → FAIL) |
| 3 | Payoff min_plants=2, 1 plant | FAIL/WARN per F3 |
| 4 | required_plant_ids lists missing uuid | FAIL `foreshadow_required_plants_missing` |
| 5 | FAIL + active override | Settle OK |
| 6 | Context pack twists | Response JSON has no `secret_truth` key anywhere |
| 7 | Cross-tenant twist GET | 404 |
| 8 | Payoff on seeded twist, settle | FAIL `foreshadow_unseeded_reveal` |

---

## Out of Phase 4

| Item | Deferred |
|------|----------|
| LLM foreshadow fairness | Phase 6 |
| Semantic paraphrase reveal detection | Phase 6 |
| Auto-suggest plants from prose | Optional future |
| Mystery vs xianxia runtime genre packs JSON | Phase 6 (`genre_rule_packs`) |

---

## Links

- [schema.md](./schema.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 2 continuity-rules](../phase-2/continuity-rules.md)
- Skill: `skills/storyforge-twists/SKILL.md`
