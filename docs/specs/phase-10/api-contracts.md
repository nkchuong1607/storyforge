# Phase 10 API Contracts (Human-Readable)

> Companion to [openapi.yaml](./openapi.yaml). Machine contract wins on conflict.  
> Extends [Phase 9 api-contracts](../phase-9/api-contracts.md) — Phase 1–9 routes unchanged unless noted.

---

## Phase 10 delta summary

| Change | Detail |
|--------|--------|
| New routes | Reality settings GET/PATCH; fact-check run enqueue/list/detail; claim disposition, accept-fix, promote-evidence |
| Jobs | Redis queue `storyforge:fact_check_runs`; statuses `pending` / `running` / `done` / `failed` |
| `ContinuityCategory` | Adds **`fact_check`** — **WARN-only in Gate UI** when `reality_anchors=strict` |
| Continuity codes | `fact_check_unverified_claim`, `fact_check_contradiction` — bridge from open fact-check claims |
| Settle | Unchanged by default; optional `fact_check_blocks_settle=true` blocks on open FAIL dispositions |
| Providers | FakeVerifier default; HTTP Wikipedia/Wikidata stub behind env flags |
| Research | Promote-evidence creates Phase 9 `research_note`; links back via tags + metadata |

---

## Authentication & errors

Unchanged from Phase 1–9: `X-User-Id` required; cross-tenant → `404 not_found`.

### New error codes

| HTTP | code | When |
|------|------|------|
| 404 | `not_found` | Run/claim foreign to tenant |
| 409 | `fact_check_run_pending` | Duplicate enqueue for same prose_version |
| 409 | `fact_check_run_not_done` | Detail expected done but still running |
| 409 | `claim_no_proposed_correction` | accept-fix without correction |
| 409 | `claim_no_citations` | promote-evidence without citations |
| 409 | `claim_already_promoted` | promote-evidence idempotent conflict |
| 422 | `invalid_reality_anchors` | Unknown mode |
| 422 | `invalid_claim_category` | Unknown category in settings |
| 422 | `reality_off_skip` | Not an error — run completes with `skipped_reason` |

---

## Reality settings

### `GET /projects/{project_id}/reality-settings`

**200 example:**

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "reality_anchors": "soft",
  "enabled_categories": [],
  "fact_check_blocks_settle": false,
  "auto_run_on_save": false,
  "include_research_notes": true,
  "updated_at": "2026-09-14T00:00:00Z"
}
```

### `PATCH /projects/{project_id}/reality-settings`

**Request (historical fiction project):**

```json
{
  "reality_anchors": "strict",
  "enabled_categories": ["date", "place", "historical_event", "public_figure"],
  "fact_check_blocks_settle": false
}
```

**200:** Updated `ProjectRealitySettings`.

---

## Fact-check runs

### `POST /projects/{project_id}/chapters/{chapter_id}/fact-check/runs`

**Request:**

```json
{
  "prose_version_id": "a1000000-0000-4000-8000-000000000201",
  "force_refresh": false,
  "categories": ["date", "place"]
}
```

**202 example (enqueued):**

```json
{
  "id": "b2000000-0000-4000-8000-000000000301",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "chapter_id": "a1000000-0000-4000-8000-000000000101",
  "prose_version_id": "a1000000-0000-4000-8000-000000000201",
  "requested_by_user_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "skipped_reason": null,
  "error_message": null,
  "summary": null,
  "started_at": null,
  "finished_at": null,
  "created_at": "2026-09-14T12:00:00Z",
  "claims": []
}
```

**202 example (`reality_anchors=off`):**

```json
{
  "id": "b2000000-0000-4000-8000-000000000302",
  "status": "done",
  "skipped_reason": "reality_off",
  "summary": { "total_claims": 0, "pass": 0, "warn": 0, "fail": 0, "skipped": 0 },
  "finished_at": "2026-09-14T12:00:00Z",
  "claims": []
}
```

### `GET .../fact-check/runs/{run_id}` (poll until done)

**200 example (completed with issues):**

```json
{
  "id": "b2000000-0000-4000-8000-000000000301",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "chapter_id": "a1000000-0000-4000-8000-000000000101",
  "prose_version_id": "a1000000-0000-4000-8000-000000000201",
  "status": "done",
  "summary": { "total_claims": 3, "pass": 1, "warn": 1, "fail": 1, "skipped": 0 },
  "finished_at": "2026-09-14T12:00:05Z",
  "claims": [
    {
      "id": "c3000000-0000-4000-8000-000000000401",
      "run_id": "b2000000-0000-4000-8000-000000000301",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "category": "date",
      "text": "9 November 1985",
      "normalized_text": "1985-11-09",
      "span": { "start": 88, "end": 104, "excerpt": "...wall fell on 9 November 1985..." },
      "source_type": "prose",
      "severity": "fail",
      "confidence": 0.91,
      "summary": "Berlin Wall fell in 1989, not 1985",
      "proposed_correction": "9 November 1989",
      "author_disposition": "open",
      "citations": [
        {
          "id": "d4000000-0000-4000-8000-000000000501",
          "provider_id": "fake",
          "url": "https://fake.storyforge.test/berlin-wall",
          "title": "Berlin Wall",
          "snippet": "Opened: 9 November 1989",
          "retrieved_at": "2026-09-14T12:00:05Z",
          "research_note_id": null
        }
      ],
      "created_at": "2026-09-14T12:00:05Z"
    }
  ]
}
```

---

## Author actions

### `POST .../fact-check/claims/{claim_id}/disposition`

**Request (intentional fiction):**

```json
{
  "disposition": "intentional_fiction",
  "note": "Alternate history — wall falls early in this timeline"
}
```

**200:** `FactClaim` with `author_disposition: intentional_fiction`, `disposition_at` set.

### `POST .../fact-check/claims/{claim_id}/accept-fix`

**Request:**

```json
{
  "handoff_target": "prompt_edit",
  "correction_override": "9 November 1989"
}
```

**200 example:**

```json
{
  "claim_id": "c3000000-0000-4000-8000-000000000401",
  "handoff_target": "prompt_edit",
  "handoff_payload": {
    "chapter_id": "a1000000-0000-4000-8000-000000000101",
    "prose_version_id": "a1000000-0000-4000-8000-000000000201",
    "span": { "start": 88, "end": 104 },
    "original_text": "9 November 1985",
    "suggested_replacement": "9 November 1989",
    "prompt_edit_prefill": "Replace the date with the historically accurate November 1989."
  }
}
```

Claim disposition updated to `accepted_fix`. **Prose unchanged** until author applies Prompt Edit.

### `POST .../fact-check/claims/{claim_id}/promote-evidence`

**Request:**

```json
{
  "note_title": "Berlin Wall fall date",
  "tags": ["fact-check", "berlin"]
}
```

**201 example:**

```json
{
  "claim_id": "c3000000-0000-4000-8000-000000000401",
  "research_note_id": "e5000000-0000-4000-8000-000000000601",
  "research_note": {
    "id": "e5000000-0000-4000-8000-000000000601",
    "title": "Berlin Wall fall date",
    "body_md": "**Berlin Wall**\n\nOpened: 9 November 1989\n\nSource: https://fake.storyforge.test/berlin-wall",
    "source_url": "https://fake.storyforge.test/berlin-wall",
    "tags": ["fact-check", "berlin"],
    "status": "active"
  }
}
```

---

## Continuity bridge (strict mode)

When author runs `POST .../continuity-check` and project `reality_anchors=strict`:

**Additional WARN issues (never FAIL in Gate):**

```json
{
  "severity": "warn",
  "category": "fact_check",
  "code": "fact_check_contradiction",
  "description": "Real-world fact-check: Berlin Wall date contradicts sources",
  "chapter_ref": { "chapter_id": "...", "span": { "start": 88, "end": 104 } },
  "entity_ids": { "fact_claim_id": "c3000000-0000-4000-8000-000000000401" },
  "meta": { "bridge": true, "original_severity": "fail" }
}
```

Claims with `author_disposition` in `intentional_fiction`, `dismissed`, `accepted_fix`, `evidence_promoted` are **excluded**.

---

## Settle interaction

**Default:** Settle unchanged — fact-check ignored.

**When `fact_check_blocks_settle=true`:**

Settle returns **409** if latest done run for chapter has open claims with `severity=fail` and `author_disposition=open`:

```json
{
  "error": {
    "code": "fact_check_fail_blocks_settle",
    "message": "Unresolved fact-check FAIL blocks settle (project setting enabled)",
    "details": { "open_fail_count": 1, "run_id": "b2000000-..." }
  }
}
```

This is **separate** from `continuity_fail_blocks_settle`.

---

## Route index (Phase 10)

| Method | Path | Purpose |
|--------|------|---------|
| GET/PATCH | `/projects/{id}/reality-settings` | Project reality mode |
| POST | `/projects/{id}/chapters/{chapter_id}/fact-check/runs` | Enqueue run |
| GET | `/projects/{id}/chapters/{chapter_id}/fact-check/runs` | List runs |
| GET | `/projects/{id}/chapters/{chapter_id}/fact-check/runs/{run_id}` | Run + claims |
| GET | `/projects/{id}/fact-check/runs/{run_id}` | Project alias |
| POST | `/projects/{id}/fact-check/claims/{claim_id}/disposition` | Author disposition |
| POST | `/projects/{id}/fact-check/claims/{claim_id}/accept-fix` | Prompt Edit handoff |
| POST | `/projects/{id}/fact-check/claims/{claim_id}/promote-evidence` | Citation → research note |

---

## Links

- [fact-check.md](./fact-check.md)
- [providers.md](./providers.md)
- [schema.md](./schema.md)
- [Phase 9 research API](../phase-9/api-contracts.md#research)
