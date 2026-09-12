# Phase 6 Test Strategy

> Mandatory quality bar for Phase 6 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 5 test strategy](../phase-5/test-strategy.md).

---

## Principles (unchanged + Phase 6)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [power-rules.md](./power-rules.md), [prompt-edit.md](./prompt-edit.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 6 OpenAPI).
5. **FakeLLM default** — No paid API in CI/local default; real LiteLLM opt-in via env.

---

## LLM testing policy

| Mode | When | Config |
|------|------|--------|
| **FakeLLM** | Default; all CI; `make test-api` | `STORYFORGE_LLM_PROVIDER=fake` (default) |
| **LiteLLM live** | Manual dev only | `@pytest.mark.llm_live` — skipped unless env set |

**FakeLLM contract tests:**

- Deterministic output for fixed instruction + prose hash
- `provider=fake`, `model=fake-llm` stored on turn
- No network mocks required — use real FakeLLM provider class

**Never in CI:**

- Calls to OpenAI/Anthropic/etc.
- Tests that require `OPENAI_API_KEY`

Document opt-in in `docs/agent-setup.md`:

```bash
export STORYFORGE_LLM_PROVIDER=litellm
export LITELLM_MODEL=gpt-4o
export OPENAI_API_KEY=sk-...
pytest -m llm_live  # manual only
```

---

## Test pyramid (Phase 6 additions)

```text
        Integration (API)     ← rank jump FAIL, FakeLLM prompt edit, genre pack merge
               │
        Unit                  ← rank delta math, genre merge, instruction sanitize
               │
        Web (Vitest + MSW)    ← Prompt Edit loop, Power ladder, Genre toggles
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Rank delta | sort_order jump > max → issue |
| Technique eligibility | rank below min_rank → ineligible |
| Genre pack merge | mystery defaults → foreshadow FAIL threshold |
| Power module off | literary → skip all P* rules |
| FakeLLM provider | instruct returns proposed_content |
| Instruction sanitize | strip template injection patterns |
| Priority gap combat | upset detection keyword stub |

**Location:** `apps/api/tests/unit/test_power_*.py`, `test_genre_pack.py`, `test_fake_llm.py`

### Integration tests (mandatory Phase 6 scenarios)

| # | Scenario |
|---|----------|
| 1 | CRUD `power-system/ranks` — reorder + unique sort_order |
| 2 | DELETE rank in use → 409 `rank_in_use` |
| 3 | CRUD `power-system/techniques` — min_rank FK |
| 4 | PATCH `power-system/settings` — priority_gap |
| 5 | **Rank jump FAIL:** prose fixture → `power_rank_jump_without_breakthrough` |
| 6 | Breakthrough in state_diff → settle → PASS on re-check |
| 7 | **Technique ineligible FAIL** |
| 8 | Mystery project + default pack → power rules skipped |
| 9 | Mystery pack → foreshadow stricter than xianxia (genre merge) |
| 10 | GET/PATCH `genre-rule-pack` — partial merge |
| 11 | POST `genre-rule-pack/reset` |
| 12 | **Prompt edit instruct** (FakeLLM) → turn created |
| 13 | **Apply** → new prose_version `source=ai_editor` |
| 14 | **Regenerate** → new turn_index, same instruction |
| 15 | Locked chapter prompt-edit → 409 |
| 16 | Settle with cultivation proposal → ledger_events row |
| 17 | Bible snapshot contains `world.power_system` after settle |
| 18 | **Cross-tenant:** power ranks on project B → 404 |

**Markers:** `@pytest.mark.integration`

### Power-focused test module

`apps/api/tests/integration/test_phase6_power.py`:

- Parameterized rank jump + override paths
- Asserts fingerprints stable for Mark intentional

### Prompt edit test module

`apps/api/tests/integration/test_phase6_prompt_edit.py`:

- FakeLLM only
- Apply idempotency: double apply same turn → 409 or no-op per spec

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | `app/` including power, genre, prompt_edit, fake_llm |
| Branch | ≥ 80% stretch | FAIL vs WARN vs module disabled |

```bash
cd apps/api && pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

---

## Frontend (`apps/web`)

### Component tests (Phase 6 modules)

| Module | Scenarios |
|--------|-----------|
| PromptEditPanel | Send → preview → Apply updates version |
| PromptEditTurnLog | Renders turns; expand preview |
| PromptEditActionBar | Disabled while loading; Compare opens modal |
| PowerRankLadderEditor | Drag reorder calls PUT reorder |
| PowerTechniqueTable | Min rank select validation |
| PowerSystemGate | Hidden when module disabled |
| GenreModuleToggles | PATCH pack on toggle |
| GenrePromisesEditor | Save promises list |
| API clients | Types match OpenAPI |

**MSW handlers:** All Phase 6 routes; FakeLLM fixed response body.

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line coverage | ≥ **90%** | Phase 6 paths in [web-screens.md](./web-screens.md) |

```bash
make test-web-cov
```

---

## CI matrix (unchanged policy)

| Job | Specs PR | Implementation PR |
|-----|----------|-------------------|
| `make check` | ✅ required | ✅ required |
| `make validate-specs` | ✅ Phase 1–6 OpenAPI | ✅ if specs touched |
| `make test-api-cov` | **local only** | **local only** |
| `make test-web-cov` | skip | ✅ when web tests exist |

**No LiteLLM in GHA.** FakeLLM is the only provider in automated tests.

---

## Specs PR validation (this PR)

```bash
make validate-specs   # includes docs/specs/phase-6/openapi.yaml
make check
```

No Testcontainers required for specs-only PR.

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [power-rules.md](./power-rules.md)
- [prompt-edit.md](./prompt-edit.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 5 test strategy](../phase-5/test-strategy.md)
