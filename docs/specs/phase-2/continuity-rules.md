# Phase 2 Deterministic Continuity Rules v1

> Canonical rule pack **`deterministic-v1`**. No LLM auditor in Phase 2.  
> Implements [storyforge-continuity](../../../skills/storyforge-continuity/SKILL.md) MVP subset.

---

## Execution model

| Property | Value |
|----------|-------|
| Trigger | `POST .../continuity-check` (sync; returns when complete) |
| Input | Latest `prose_versions.content` for chapter + settled ledger tail + bible snapshot at `bible_version_at_draft` + active staging rows |
| Output | `continuity_reports` row + optional inline `state_diff_json` |
| Re-run | New report each time; overrides matched by `issue.fingerprint` |
| Async queue | Out of scope Phase 2 (Redis optional later) |

---

## Issue schema

Every rule emits zero or more issues:

```json
{
  "fingerprint": "<category>:<entity_id>:<code>:<stable_hash>",
  "severity": "fail | warn | pass",
  "category": "character | timeline | location | world_rule | bible_staging",
  "code": "stable_machine_code",
  "message": "Human-readable Vietnamese message",
  "chapter_refs": [1],
  "entity_ids": ["uuid"],
  "evidence": {}
}
```

**Aggregate `result`:**

| Condition | `continuity_result` |
|-----------|---------------------|
| Zero issues | `pass` |
| Any FAIL without active override | `fail` |
| WARN only (or FAIL all overridden) | `warn` |
| Only PASS-level checks | `pass` |

Settle gate uses **effective FAIL count** = FAIL issues minus active overrides.

---

## Severity policy

| Severity | Blocks settle? | Typical author action |
|----------|----------------|------------------------|
| **FAIL** | Yes | Fix prose, fix ledger proposal, or Mark intentional with reason |
| **WARN** | No | Fix or Mark intentional |
| **PASS** | No | Informational only (usually omitted from `issues_json`) |

---

## Rule catalog

### R1 — Character death / status (`character`)

**Code:** `character_deceased_appears_alive`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Precondition | Latest settled ledger for character has `payload.to = deceased` (or `missing` treated as unavailable) |
| Violation | Prose mentions character as active/speaking in present scene without `transformed` / `revived` event in state diff |

**Code:** `character_status_regression`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | State diff proposes `deceased → alive` without `transformed` event type |

**Code:** `character_unknown_in_cast`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Proper name in prose not matching any `characters.display_name` (simple string match; no fuzzy LLM) |

---

### R2 — Timeline monotonicity (`timeline`)

**Code:** `timeline_anchor_order_violation`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Input | `bible_versions.snapshot_json` timeline section + ledger `timeline_anchor` events |
| Violation | State diff or prose implies anchor A before B while settled canon orders B before A |

**Code:** `timeline_chapter_backwards`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Explicit date/time marker in prose contradicts chapter number ordering (e.g. "three years before ch.1" in ch.5 without anchor) |

Phase 2 uses **structured anchors only** for FAIL; free-text dates → WARN.

---

### R3 — Location consistency (`location`)

**Code:** `location_same_scene_conflict`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Input | Latest settled `location_change` per character + scene beat boundaries |
| Violation | Two characters in same beat tagged locations that canon marks mutually exclusive (from bible location metadata `exclusive_with[]`) |

**Code:** `location_teleport_without_transition`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Character location changes between consecutive beats without transition prose keyword heuristic (`đến`, `tới`, `rời`, …) or ledger event in diff |

If location metadata absent in bible, skip FAIL rules; emit nothing (not PASS noise).

---

### R4 — World rule / bible staging (`world_rule`, `bible_staging`)

**Code:** `bible_staging_conflicts_settled`  
**Severity:** FAIL

| Check | Logic |
|-------|-------|
| Input | `bible_entry_staging` rows where `base_bible_version < projects.bible_version_current` AND `entry_key` exists in settled snapshot |
| Violation | Staging `content_md` contradicts settled snapshot entry on same `entry_key` (deterministic: normalized whitespace compare + explicit `metadata.status` conflict) |

**Code:** `world_rule_rank_violation_stub`  
**Severity:** WARN

| Check | Logic |
|-------|-------|
| Violation | Prose mentions cultivation rank label not present in bible glossary (string list match) |

Full rank monotonicity → Phase 6 (`power_system` category).

---

## State diff (simple extract stub)

Phase 2 **does not** run LLM fact extractor. State diff is produced by:

1. **Manual proposals** — author edits in Continuity Gate right panel (future web saves to report).
2. **Deterministic stub extract:**
   - Scan prose for `characters.display_name` mentions → propose `location_change` only if beat metadata includes `location:` tag.
   - Death keywords near character name (`chết`, `tử vong`, …) → propose `status_change` WARN for author confirmation.

`state_diff_json` shape:

```json
{
  "ledger_proposals": [
    {
      "entity_type": "character",
      "entity_id": "770e8400-e29b-41d4-a716-446655440002",
      "event_type": "status_change",
      "payload": { "from": "alive", "to": "deceased" },
      "confidence": "stub"
    }
  ],
  "bible_patch_candidates": [
    {
      "entry_key": "locations.thanhphong",
      "section": "locations",
      "title": "Thành Phong",
      "content_md": "...",
      "action": "promote_from_staging"
    }
  ]
}
```

Settle commits **approved** proposals only (Phase 2: entire diff approved via Approve & Settle — no partial approval UI).

---

## Intentional override semantics

| Topic | Rule |
|-------|------|
| Scope | Per `chapter_id` + `issue_fingerprint` |
| WARN override | Allowed; settle proceeds |
| FAIL override | Allowed with non-empty `reason`; settle proceeds |
| Re-audit | Skips fingerprint if `revoked_at IS NULL` |
| Revoke | PATCH override `revoked_at` — issue reappears |
| Settle without override | Any effective FAIL → `409 continuity_fail_blocks_settle` |

Override does **not** mutate prose or ledger — it only suppresses the issue for gate purposes. Author should still fix prose when possible.

---

## Out of Phase 2 (explicit)

| Category | Deferred |
|----------|----------|
| `foreshadow` | Phase 4 twist plants/payoffs |
| `psychology` | Phase 5 OOC |
| `power_system` | Phase 6 rank ladder |
| LLM semantic audit | Phase 6+ |
| Provisional character extract | Phase 3 |

---

## Test vectors (implementation)

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Character dead in ledger; alive in prose | FAIL `character_deceased_appears_alive` |
| 2 | FAIL + active override | `result: warn` or pass gate; settle OK |
| 3 | FAIL no override | settle 409 |
| 4 | Staging contradicts settled bible | FAIL `bible_staging_conflicts_settled` |
| 5 | WARN only | settle OK |
| 6 | Re-run after override | Overridden fingerprint absent |

---

## Links

- [schema.md](./schema.md) — `continuity_reports`, `continuity_overrides`
- [api-contracts.md](./api-contracts.md) — check + override endpoints
- [test-strategy.md](./test-strategy.md)
