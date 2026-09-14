# Phase 10 Test Strategy — Real-World Fact Check

> Mandatory quality bar for Phase 10 implementation PRs (API + web). Specs PR adds validation only.

Extends [Phase 9 test strategy](../phase-9/test-strategy.md).

---

## Principles (unchanged + Phase 10)

1. **Spec-first** — Tests assert [openapi.yaml](./openapi.yaml), [schema.md](./schema.md), [fact-check.md](./fact-check.md), [providers.md](./providers.md).
2. **Real Postgres** — Testcontainers for integration; no mocked DB.
3. **Redis for fact-check jobs** — Testcontainers Redis or `STORYFORGE_FACT_CHECK_SYNC=1` inline worker.
4. **FakeVerifier only in CI** — No live HTTP; `@pytest.mark.live_http` skipped in default runs.
5. **Coverage ≥ 90% line** — **Hard fail locally** via `make test-api-cov` / `make test-web-cov`.
6. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 10 OpenAPI).
7. **Deterministic extraction** — Unit tests for regex/heuristic extractor without LLM.
8. **Human-in-the-loop** — Tests verify accept-fix does **not** mutate `prose_versions` directly.

---

## Test pyramid (Phase 10 additions)

```text
        Integration (API)     ← enqueue→worker→report, disposition, promote→research note, settle block opt-in
               │
        Unit                  ← claim extractor, FakeVerifier map, cache keys, continuity bridge mapper
               │
        Web (Vitest + MSW)    ← Fact Check panel poll, actions, reality settings
```

---

## Backend (`apps/api`)

### Unit tests (new)

| Target | Examples |
|--------|----------|
| Claim extractor | date regex, anchor markers, category filter |
| FakeVerifier | deterministic pass/fail/contradiction map |
| Provider orchestrator | merges severities; citations union |
| Research note evidence | keyword overlap match |
| Wikidata stub loader | reads fixture JSON — no HTTP |
| Cache key builder | sha256 normalized claim |
| Continuity bridge | strict mode maps open fail → WARN code; excludes dispositions |
| Settle guard | `fact_check_blocks_settle=true` blocks; default allows |
| Accept-fix handoff | builds Prompt Edit payload; no prose write |

**Location:** `apps/api/tests/unit/test_phase10_*.py`

### Integration tests (mandatory Phase 10 scenarios)

| # | Scenario |
|---|----------|
| 1 | `GET/PATCH .../reality-settings` — defaults + update strict |
| 2 | `reality_anchors=off` — POST run → immediate done, `skipped_reason` |
| 3 | `POST .../fact-check/runs` — 202 pending |
| 4 | Worker (sync mode) → done + claims populated via FakeVerifier |
| 5 | Claim with contradiction — fail severity + citation snapshot persisted |
| 6 | `force_refresh=true` — bypasses cache (cache hit test separate) |
| 7 | `POST .../disposition` intentional_fiction — excluded from bridge |
| 8 | `POST .../accept-fix` — handoff payload; prose_version unchanged |
| 9 | `POST .../promote-evidence` — creates research_note; claim disposition |
| 10 | Promote idempotent — second call 409 or same note id |
| 11 | Continuity check strict — bridge WARN issues present |
| 12 | Continuity check soft/off — no fact_check category |
| 13 | Settle default — succeeds with open fact-check fail |
| 14 | Settle `fact_check_blocks_settle=true` — 409 with open fail |
| 15 | Duplicate enqueue same prose_version — 409 pending |
| 16 | Failed run — error_message populated |
| 17 | **Cross-tenant:** user A cannot read run on project B → 404 |
| 18 | Citations immutable — re-run adds new rows, old unchanged |

**Markers:** `@pytest.mark.integration`

**Redis:** Testcontainers Redis in `conftest.py` Phase 10 fixture, or `STORYFORGE_FACT_CHECK_SYNC=1`.

**Network:** `STORYFORGE_FACT_CHECK_HTTP=0`, `STORYFORGE_FACT_CHECK_LIVE_WIKI=0` in CI and default test env.

### Live HTTP tests (optional, local only)

```python
@pytest.mark.live_http
@pytest.mark.skipif(os.getenv("STORYFORGE_FACT_CHECK_LIVE_WIKI") != "1", ...)
async def test_wikipedia_live_summary(): ...
```

Never run in GHA.

### Dedicated test modules

| File | Focus |
|------|-------|
| `test_phase10_reality_settings.py` | GET/PATCH defaults |
| `test_phase10_fact_check_runs.py` | enqueue, worker, poll |
| `test_phase10_claim_actions.py` | disposition, accept-fix, promote |
| `test_phase10_continuity_bridge.py` | strict WARN bridge |
| `test_phase10_settle_guard.py` | opt-in block |
| `test_phase10_providers_fake.py` | FakeVerifier determinism |

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | `app/services/fact_check_*`, `app/providers/fact_*`, `app/workers/fact_check_*`, new routers |
| Branch | report only | — |

---

## Frontend (`apps/web`)

### Vitest + MSW scenarios

| # | Scenario |
|---|----------|
| 1 | Fact Check panel empty → run → loading → results |
| 2 | Issue row severity badges + category pills |
| 3 | Accept fix opens Prompt Edit with handoff payload |
| 4 | Mark intentional updates row disposition |
| 5 | Promote evidence shows link to research note |
| 6 | Run failed — error banner + retry |
| 7 | `reality_off` skipped banner + link settings |
| 8 | Reality settings save — PATCH + toast |
| 9 | Strict mode hint — gate bridge banner |
| 10 | i18n keys resolve VI + EN for `factCheck.*` |

**Location:** `apps/web/**/*.fact-check.test.tsx`, `apps/web/**/reality-settings.test.tsx`

### Coverage policy

| Metric | Gate | Scope |
|--------|------|-------|
| Line | ≥ 90% | Fact Check panel, reality settings section, MSW handlers |

---

## Specs PR validation

```bash
make validate-specs   # includes phase-10/openapi.yaml
make check            # harness green
```

No Testcontainers required for specs-only PR.

---

## Anti-patterns (do not)

- Do not call live Wikipedia/Wikidata in default pytest or Vitest runs
- Do not assert prose auto-updated after accept-fix
- Do not merge fact-check FAIL into continuity FAIL categories in tests (bridge is WARN-only)
- Do not mock Postgres in integration tests

---

## Links

- [providers.md](./providers.md)
- [api-contracts.md](./api-contracts.md)
- [Phase 9 test strategy](../phase-9/test-strategy.md)
- [Quality gates](../../engineering/quality-gates.md)
