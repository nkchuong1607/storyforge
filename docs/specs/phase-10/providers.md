# Phase 10 — Fact Check Providers

> **Skill:** `storyforge-api-python`, `storyforge-architecture`  
> **Tests:** FakeVerifier only in CI; live HTTP opt-in via env

---

## Purpose

Verification providers answer: **does this claim match external evidence?** Providers are pluggable, rate-limited, and cacheable. Implementation uses a small registry — not a generic plugin framework.

---

## Provider interface

```python
# Conceptual contract (implementation PR)
class FactCheckProvider(Protocol):
    provider_id: str  # e.g. "fake", "wikidata_stub", "research_note"

    async def verify(
        self,
        claim: FactClaim,
        context: ProviderContext,
    ) -> ProviderResult: ...


@dataclass
class ProviderContext:
    project_id: UUID
    research_notes: list[ResearchNoteSnapshot]  # linked evidence
    cache: CitationCache
    http_enabled: bool  # STORYFORGE_FACT_CHECK_HTTP


@dataclass
class ProviderResult:
    status: Literal["verified", "contradiction", "inconclusive", "skipped"]
    severity: Literal["pass", "warn", "fail"]
    confidence: float  # 0.0 - 1.0
    summary: str
    proposed_correction: str | None
    citations: list[CitationDraft]
```

**Orchestrator:** Runs providers in order per claim category; merges results (highest severity wins; citations unioned).

---

## Built-in providers

### 1. FakeVerifier (required — tests + local default)

| Property | Value |
|----------|-------|
| `provider_id` | `fake` |
| **When active** | Always registered; sole provider when `STORYFORGE_FACT_CHECK_HTTP=0` (default) |
| **Behavior** | Deterministic lookup table keyed by `(category, normalized_text)` |

**Fixture map (examples for tests):**

| normalized_text | category | Result |
|-----------------|----------|--------|
| `1945-03` | date | verified, pass |
| `1985-11-09` | date | contradiction, fail, correction `1989-11-09` |
| `Berlin` | place | verified, pass |
| `Mount FakePeak` | place | inconclusive, warn |

FakeVerifier returns synthetic citations with `url: https://fake.storyforge.test/...` — never hits network.

**Env:** `STORYFORGE_FACT_CHECK_PROVIDER=fake` (default)

---

### 2. ResearchNoteEvidenceProvider

| Property | Value |
|----------|-------|
| `provider_id` | `research_note` |
| **When active** | When `include_research_notes=true` and notes linked to chapter or claim keyword match |
| **Behavior** | Treats author-supplied note body + `source_url` as evidence; match/contradict via deterministic keyword overlap stub (LLM optional Phase 11+) |
| **Privacy** | Only reads project's own `research_notes` — no external fetch |

**Citation source:** Note title, `source_url`, excerpt from `body_md`, `retrieved_at = note.updated_at`.

---

### 3. WikidataStubProvider (HTTP optional)

| Property | Value |
|----------|-------|
| `provider_id` | `wikidata_stub` |
| **When active** | Registered when `STORYFORGE_FACT_CHECK_HTTP=1`; still uses **stubbed responses** unless `STORYFORGE_FACT_CHECK_LIVE_WIKI=1` |
| **Behavior** | Maps `place`, `public_figure`, `historical_event`, `organization` to Wikidata Q-id lookup **stub**; live mode calls public Wikidata API with rate limit |
| **Default in CI/dev** | Stub JSON files under `apps/api/tests/fixtures/wikidata/` |

**Live mode constraints:**

- Rate limit: max 5 req/s per worker (token bucket)
- User-Agent: `StoryForgeFactCheck/1.0 (+https://storyforge.test)`
- Timeout: 10s per request
- Only HTTPS public endpoints (Wikidata, Wikipedia REST summary)

---

### 4. WikipediaSummaryProvider (HTTP optional)

| Property | Value |
|----------|-------|
| `provider_id` | `wikipedia_stub` |
| **When active** | Same HTTP flags as Wikidata stub |
| **Behavior** | Fetches Wikipedia REST `/page/summary/{title}` when live; stub otherwise |
| **Categories** | `public_figure`, `historical_event`, `place`, `technology` |

---

## Provider selection matrix

| Category | Default order (HTTP off) | With HTTP + live |
|----------|--------------------------|------------------|
| all | `research_note` → `fake` | `research_note` → `wikidata_stub` → `wikipedia_stub` → `fake` (fallback inconclusive) |

When HTTP off, `fake` must return `inconclusive` for unknown keys — not error.

---

## Citation schema

Persisted in `fact_citations` (see [schema.md](./schema.md)):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | uuid | yes | PK |
| `claim_id` | uuid | yes | FK |
| `provider_id` | text | yes | `fake`, `research_note`, etc. |
| `url` | text | yes | May be fake:// or https:// |
| `title` | text | yes | |
| `snippet` | text | yes | Supporting excerpt |
| `retrieved_at` | timestamptz | yes | Snapshot time |
| `snapshot_json` | jsonb | yes | Full provider payload for reproducibility |
| `research_note_id` | uuid | null | When provider is research_note |

**Immutability:** Citation rows append-only; new run may add citations, never update in place.

---

## Caching

| Layer | Key | TTL | Notes |
|-------|-----|-----|-------|
| Redis | `storyforge:fc_cache:{provider}:{sha256(normalized_claim)}` | 24h default | Skip provider call on hit |
| Postgres | `fact_citations` | permanent | Report reproducibility |

Cache bypass: `options.force_refresh=true` on enqueue run.

**Tests:** Disable Redis cache with `STORYFORGE_FACT_CHECK_CACHE=0` or use FakeVerifier fixed responses.

---

## Rate limits and failures

| Concern | Policy |
|---------|--------|
| HTTP 429 | Retry once with backoff; else `inconclusive` + warn |
| HTTP 5xx | Same |
| Timeout | `inconclusive`, severity warn |
| Provider exception | Log; claim marked `provider_error` in run `result_json`; other claims continue |

Run completes `done` even if some claims inconclusive — partial success.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STORYFORGE_FACT_CHECK_PROVIDER` | `fake` | Primary provider set |
| `STORYFORGE_FACT_CHECK_HTTP` | `0` | Enable HTTP provider registration |
| `STORYFORGE_FACT_CHECK_LIVE_WIKI` | `0` | Live Wikipedia/Wikidata (requires HTTP=1) |
| `STORYFORGE_FACT_CHECK_SYNC` | `0` | Inline worker for tests |
| `STORYFORGE_FACT_CHECK_CACHE` | `1` | Redis citation cache |
| `STORYFORGE_FACT_CHECK_LLM_EXTRACT` | `0` | Optional LLM claim extraction |

**CI:** All `*_HTTP`, `*_LIVE_*`, `*_LLM_*` remain `0`.

---

## Test strategy (provider-focused)

| Test | Provider | Network |
|------|----------|---------|
| Deterministic pass/fail | FakeVerifier | No |
| Research note match | research_note | No |
| Wikidata stub fixture | wikidata_stub | No |
| Live wiki opt-in | wikipedia_stub | Manual only — `@pytest.mark.live_http` skipped in CI |
| Cache hit | fake + Redis | No |

See [test-strategy.md](./test-strategy.md).

---

## Deferred (Phase 11+)

- Paid search APIs (Google, Bing)
- Custom provider plugins via config file
- LLM-as-judge verification (with FakeLLM tests)
