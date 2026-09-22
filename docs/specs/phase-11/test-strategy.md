# Phase 11 Test Strategy — Mystery CraftPack

---

## Coverage gate

| Module scope | Line coverage |
|--------------|---------------|
| `app/services/craft_*` | ≥ 90% |
| `app/services/continuity/craft.py` | ≥ 90% |
| `app/services/llm/craft_skills.py` | ≥ 90% |
| `app/repositories/craft_pack.py` | ≥ 90% |

Run locally: `cd apps/api && pytest --cov=app --cov-fail-under=90 -q` (craft modules in scope for Phase 11 PR).

GHA: `make check` only (light).

---

## Golden fixture

**API:** `apps/api/tests/fixtures/golden/mystery_fair_play/`

| File | Purpose |
|------|---------|
| `pack.json` | Expected pack shape |
| `expected_flags.json` | ≥3 continuity codes from seeded MS scenario |
| `scenario.json` | Twist/plant/payoff/prose setup metadata |

**Web mirror:** `apps/web/tests/fixtures/phase11/mystery_fair_play.json`

---

## Golden scenario (minimum flags)

1. **FAIL** `craft_mystery_clue_after_reveal` — payoff ch.5, zero prior plants
2. **FAIL** `craft_mystery_insufficient_plants` — payoff min_plants=2, count=1
3. **WARN** `craft_mystery_unlabeled_misdirection` — prose red-herring marker, no twist.misdirection

---

## Integration tests

| Test | Assert |
|------|--------|
| `test_phase11_install_mystery_pack` | Binding created; genre_rule_pack unchanged |
| `test_phase11_craft_continuity_golden` | Golden scenario ≥3 expected codes |
| `test_phase11_craft_context_no_secret` | Context pack JSON has no `secret_truth` |
| `test_phase11_fact_check_regression` | P10 bridge unchanged on non-strict project |

---

## FakeLLM craft skills

Unit tests for `mystery_clue_plant`, `mystery_reveal_align`, `mystery_red_herring` — deterministic output, no network.

Optional LLM audit path gated by `STORYFORGE_CRAFT_LLM=1` — skipped in CI.

---

## Regression

Existing Phase 4 foreshadow + Phase 10 fact-check integration tests must pass unchanged.

---

## Links

- [mystery-craft-pack.md](./mystery-craft-pack.md)
- [Quality gates](../../engineering/quality-gates.md)
