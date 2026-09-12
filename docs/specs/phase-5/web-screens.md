# Phase 5 Web Screens

> Maps [openapi.yaml](./openapi.yaml) → UI from [05-wireframes.md](../../product/05-wireframes.md).  
> **Phase 5 screens:** Character detail **Psyche** tab + **PsychState timeline** (#10).  
> **Minimal:** Relationships panel — trust list stub; full graph Phase 8+.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–4 |
| Types | Extend from Phase 5 OpenAPI |
| MSW | Handlers for psyche-card, psych-states, context-packs/psych |
| Routing | `/projects/[projectId]/characters/[characterId]?tab=psyche` |

---

## Screen 7b delta — Character detail Psyche tab

**Wireframe:** [psych-relationships.png](../../wireframes/images/psych-relationships.png)  
**Stories:** US-C03  
**Replaces:** Phase 3 Psyche **stub** — full editor in Phase 5.

### Tab bar (updated)

| Tab | Phase 5 scope | Data |
|-----|---------------|------|
| **Overview** | Unchanged Phase 3 | `GET .../characters/{id}` |
| **Psyche** | **Full Phase 5** | `GET/PATCH .../psyche-card`, `GET .../psych-states` |
| **Relationships** | **Minimal** | Trust list from `relationship_lens`; no graph |
| **Ledger tail** | Read-only | Phase 3 pattern |
| **Appearances** | Unchanged | Chapter refs |

---

## Screen 10 — Psyche panel (primary)

**Route:** `/projects/[projectId]/characters/[characterId]?tab=psyche`

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `PsycheTabHeader` | character name, tier badge, save status |
| Form | `PsycheCardForm` | `GET .../psyche-card` |
| Field groups | `PsycheCoreFields` | drive, need, wound, fear |
| Values | `ValueHierarchyEditor` | ordered list drag |
| Boundaries | `MoralBoundariesEditor` | string list |
| Voice | `VoiceTabooEditor`, `StressBehaviorField` | voice_taboo[], stress_behavior |
| Arc | `ArcFlagsPanel` | allow_moral_break, expected_arc_beats |
| Timeline | `PsychStateTimeline` | `GET .../psych-states` |
| Chart | `StressBeliefChart` | stress_level + belief_updates per chapter |

### Psyche form fields (wireframe parity)

| Field | UI control | API field |
|-------|------------|-----------|
| Drive | Textarea | `drive` |
| Need | Textarea | `need` |
| Wound | Textarea | `wound` |
| Fear | Textarea | `fear` |
| Value hierarchy | Ordered chips | `value_hierarchy[]` |
| Defense | Text input | `defense` |
| Voice taboo | Tag input | `voice_taboo[]` |
| Stress behavior | Text input | `stress_behavior` |
| Moral boundaries | Tag input (required T3) | `moral_boundaries[]` |

### API mapping — Psyche tab

| UI action | Endpoint |
|-----------|----------|
| Load psyche | `GET /projects/{id}/characters/{cid}/psyche-card` |
| Save psyche | `PATCH .../psyche-card` |
| Load timeline | `GET .../psych-states` |
| Drill chapter | `GET .../psych-states/by-chapter/{chapterId}` |
| Link to continuity | Navigate to chapter Continuity Gate for OOC issue |

### PsychState timeline (wireframe)

| Element | Behavior |
|---------|----------|
| X-axis | Chapter numbers |
| Y-axis / overlay | `stress_level` 0–10 line chart |
| Markers | `dominant_emotion` labels per chapter |
| Detail popover | `belief_updates`, `relationship_stance`, `arc_beat` |
| Empty state | "Chưa có PsychState — settle chương có nhân vật này" |

### Save / validation UX

| State | UI |
|-------|-----|
| T3 missing boundaries | Inline error; block save |
| Save success | Toast "Đã lưu psyche card" |
| 422 invalid_psyche_card | Field-level errors from API `details` |

---

## Screen 10b — Relationships panel (minimal)

**Same route tab:** `?tab=relationships` OR sub-panel within Psyche per wireframe split.

Phase 5 **minimal** scope:

| Element | Behavior |
|---------|----------|
| Trust list | Rows from `relationship_lens[]` — target name, role_label, trust bar (0–5) |
| Add/edit | PATCH psyche-card `relationship_lens` entry |
| History tail | Last 3 `relationship_stance` from psych timeline (read-only) |
| Graph view | Placeholder: "Graph view — Phase 8" |

**Out of scope:** Force-directed graph, Neo4j queries, relationship ledger events.

---

## Chapter Editor hook (Phase 5 delta)

Optional POV quick view from [Chapter Editor](../phase-2/web-screens.md):

| UI action | Endpoint |
|-----------|----------|
| POV character psych chip | `GET .../psych-states/by-chapter/{prevChapterId}` or latest |
| Context for agent | `POST .../context-packs/psych` |

---

## Continuity Gate delta (Phase 2 screen)

| UI change | Behavior |
|-----------|----------|
| Psychology issues | Category badge `psychology`; codes from [ooc-rules.md](./ooc-rules.md) |
| State diff panel | Show `psych_state_proposals[]` with approve-all bundle |
| Mark intentional | Unchanged — works for `psych_*` fingerprints |

---

## Empty / loading states

| State | UI |
|-------|-----|
| **No psyche card** | CTA "Tạo psyche card" with T2+ hint |
| **Timeline loading** | Skeleton chart |
| **T0–T1 character** | Banner: "Nâng tier để bật OOC checks" |

---

## MSW / test hooks

| Handler | Notes |
|---------|-------|
| `GET .../psyche-card` | Full T3 fixture |
| `PATCH .../psyche-card` | Echo merge |
| `GET .../psych-states` | 2+ chapter timeline |
| OOC continuity fixture | Report with `psych_ooc_moral_boundary_violation` |

---

## Coverage scope (web)

Phase 5 Vitest ≥90% line coverage paths:

- `apps/web/components/psyche/**`
- `apps/web/components/psych-timeline/**`
- `apps/web/app/projects/[projectId]/characters/[characterId]/**` (psyche tab)
- `apps/web/lib/api/psych.ts`

See [test-strategy.md](./test-strategy.md).

---

## Links

- [api-contracts.md](./api-contracts.md)
- [05-wireframes.md](../../product/05-wireframes.md) §10
- [Phase 3 web-screens](../phase-3/web-screens.md) — stub replaced
- [Phase 2 web-screens](../phase-2/web-screens.md) — Continuity Gate
