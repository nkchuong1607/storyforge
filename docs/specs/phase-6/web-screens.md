# Phase 6 Web Screens

> Maps [openapi.yaml](./openapi.yaml) → UI from [05-wireframes.md](../../product/05-wireframes.md).  
> **Phase 6 screens:** Power System bible (#9), Chapter Editor Prompt Edit panel (#3 delta), Genre settings (wizard + project settings).

---

## Shared conventions

| Topic | Rule |
|-------|------|
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–5 |
| Types | Extend from Phase 6 OpenAPI |
| MSW | Handlers for power-system, genre-rule-pack, prompt-edit routes |
| FakeLLM | MSW returns deterministic proposals in component tests |

---

## Screen 3 delta — Chapter Editor Prompt Edit panel

**Wireframe:** [chapter-editor.png](../../wireframes/images/chapter-editor.png)  
**Stories:** US-W03  
**Replaces:** Phase 2 `PromptEditPanelStub` — full functional panel in Phase 6.

### Layout zones → components (right rail)

| Zone | Component | Data source |
|------|-----------|-------------|
| Header | `PromptEditPanelHeader` | "Prompt Edit" + model badge (fake/litellm) |
| Log | `PromptEditTurnLog` | `GET .../prompt-edit/sessions` |
| Log row | `PromptEditTurnItem` | instruction, turn_index, status, expand preview |
| Preview | `PromptEditProposalPreview` | latest turn `proposed_content` (truncated) |
| Input | `PromptEditInstructionInput` | textarea max 4000 chars |
| Actions | `PromptEditActionBar` | Send, Apply, Regenerate, Compare |

### API mapping — Prompt Edit

| UI action | Endpoint |
|-----------|----------|
| Load history | `GET /projects/{id}/chapters/{cid}/prompt-edit/sessions` |
| Send instruction | `POST .../prompt-edit/instruct` |
| Regenerate | `POST .../prompt-edit/regenerate` |
| Apply | `POST .../prompt-edit/apply` |
| Compare | `GET .../prose-versions/compare?from=&to=` + fetch version bodies |
| Refresh editor | `GET .../prose-versions/{version}` after Apply |

### States (wireframe parity)

| State | UI |
|-------|-----|
| **Stub removed** | Panel enabled for drafting/reviewing chapters |
| **AI running** | Spinner on Send/Regenerate; buttons disabled |
| **Proposal ready** | Apply + Compare enabled; preview shows diff hint |
| **Applied** | Toast "Đã lưu phiên bản {N}"; version dropdown updates `ai_editor` badge |
| **Locked chapter** | Panel read-only; banner links to unlock flow |
| **Provider error** | Inline error from 502; retry via Regenerate |
| **Empty log** | Placeholder "Mô tả chỉnh sửa để bắt đầu…" |

### Compare modal

| Element | Behavior |
|---------|----------|
| Left pane | `base_prose_version` content |
| Right pane | Proposed or applied version |
| Diff | Line-based diff component (reuse Phase 2 compare if exists) |

---

## Screen 9 — Power System bible

**Route:** `/projects/[projectId]/bible/power-system`  
**Wireframe:** [power-system.png](../../wireframes/images/power-system.png)  
**Stories:** US-PW01, US-PW02

Sub-view under Story Bible → World Rules → Power System.

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Gate | `PowerSystemGate` | `genre_rule_pack.modules.power_system.enabled` + settings |
| Settings bar | `PowerSystemSettingsForm` | `GET/PATCH .../power-system/settings` |
| Rank ladder | `PowerRankLadderEditor` | `GET .../power-system/ranks` |
| Rank row | `PowerRankRow` | display_name, sub_stages, constraints_md, drag handle |
| Priority gap | `PriorityGapField` | `priority_gap` from settings |
| Techniques | `PowerTechniqueTable` | `GET .../power-system/techniques` |
| Technique row | `PowerTechniqueRow` | min rank, sect, cost, notes |
| Add actions | `AddRankButton`, `AddTechniqueButton` | POST routes |

### API mapping — Power bible

| UI action | Endpoint |
|-----------|----------|
| Load settings | `GET .../power-system/settings` |
| Save settings | `PATCH .../power-system/settings` |
| Load ranks | `GET .../power-system/ranks` |
| Add/edit rank | `POST/PATCH .../power-system/ranks/{id}` |
| Reorder ranks | `PUT .../power-system/ranks/reorder` |
| Load techniques | `GET .../power-system/techniques` |
| Add/edit technique | `POST/PATCH .../power-system/techniques/{id}` |

### States

| State | UI |
|-------|-----|
| **Disabled (non-xianxia)** | `PowerSystemDisabledBanner` — "Genre không dùng power system" + link to Project Settings → Genre |
| **Validation error** | Non-monotonic ranks blocked inline on save |
| **Empty ladder** | CTA "Thêm cảnh giới đầu tiên" + xianxia template seed button |
| **Saving** | Optimistic UI optional; skeleton on first load |

### Continuity link

Rank jump FAIL issues in Continuity Gate link back to Power bible + affected character.

---

## Genre settings — Wizard step + Project Settings

**Wireframe:** Wizard step 2 in [05-wireframes.md](../../product/05-wireframes.md) §8  
**Stories:** US-P01 (wizard), genre contract editing

### Wizard Genre step (delta)

| Element | Behavior |
|---------|----------|
| Genre cards | xianxia, mystery, literary, romance, custom |
| Preview | Shows 2–3 `promises` from default pack |
| Submit | `POST /projects` seeds `genre_rule_pack_json` from template |

### Project Settings — Genre contract tab

**Route:** `/projects/[projectId]/settings/genre`

| Zone | Component | Data |
|------|-----------|------|
| Profile | `GenreProfileSelect` | `PATCH /projects/{id}` genre_profile (with reset warning) |
| Modules | `GenreModuleToggles` | power, foreshadow, psychology |
| Strictness | `GenreStrictnessPresets` | relaxed / standard / strict |
| Promises | `GenrePromisesEditor` | string list |
| Forbidden | `GenreForbiddenEditor` | string list |
| Thresholds | `GenreThresholdsForm` | advanced collapsible |
| Reset | `ResetGenrePackButton` | `POST .../genre-rule-pack/reset` |

---

## Navigation updates

| Location | Change |
|----------|--------|
| Story Bible sidebar | Add **Power System** link when module enabled |
| Chapter Editor | Enable Prompt Edit panel (remove Phase 6 badge stub) |
| Project Settings | New **Genre** tab |
| Continuity Gate | `power_system` category badge styling |

---

## Phase 6 web coverage scope

Include in ≥90% coverage gate:

- `PromptEditPanel`, `PromptEditTurnLog`, `PromptEditActionBar`
- `PowerRankLadderEditor`, `PowerTechniqueTable`, `PowerSystemGate`
- `GenreModuleToggles`, `GenrePromisesEditor`
- API clients: `power-system.ts`, `genre-rule-pack.ts`, `prompt-edit.ts`

Exclude: Phase 7 polish animations, export flows.

---

## Links

- [prompt-edit.md](./prompt-edit.md)
- [api-contracts.md](./api-contracts.md)
- [test-strategy.md](./test-strategy.md)
- [05-wireframes.md](../../product/05-wireframes.md)
