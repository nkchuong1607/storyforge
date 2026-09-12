# Phase 7 Screen Parity Checklist

> Maps every Phase 1–6 screen to required **empty / loading / error / success** states.  
> Source of truth: [05-wireframes.md](../../product/05-wireframes.md) state tables + phase web-screens deltas.

**Acceptance:** Phase 7 implementation PR must check every row below. Status column filled during QA.

Legend: ✅ required | ⚪ optional polish | — not applicable

---

## Global chrome (all routes)

| State | Trigger | Required UI | Wireframe ref |
|-------|---------|-------------|---------------|
| Loading | Route transition | Top progress or skeleton shell; sidebar persists | — |
| Error (boundary) | Unhandled render error | Friendly fallback + reload | — |
| Offline banner | `navigator.onLine === false` | Dismissible banner; queue saves where safe | — |
| Locale switch | User toggles EN/VI | Chrome re-renders; prose content unchanged | i18n.md |
| Theme switch | User toggles light/dark | Instant token swap; no flash | design-system.md |

---

## Screen 1 — Dashboard (`/`)

**Phase:** 1 | **Wireframe:** #1

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Initial fetch | 4 card skeletons | ✅ |
| Empty | `total_items === 0` | Illustration + "Chưa có dự án" + FAB CTA | ✅ |
| Error | 401/5xx | Banner "Không tải được dự án" + Retry | ✅ |
| Filtered empty | Search no hits | "Không có kết quả cho '…'" + clear search | ✅ |
| Success | 200 + items | Project grid with genre pill, progress, date | ✅ |

---

## Screen 2 — Project Hub (`/projects/[id]`)

**Phase:** 1 (+ 2/4 deltas) | **Wireframe:** #2

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Initial fetch | Table skeleton + summary card skeletons | ✅ |
| Empty chapters | No chapters | "Chưa có chương" + "+ Thêm chương" | ✅ |
| Error | 404/5xx | Not found or error banner + back link | ✅ |
| Continuity WARN | Open WARN issues | Amber badge on summary card; link to gate | ✅ |
| Success | Data loaded | Chapter table with status labels | ✅ |

Status label mapping (VI chrome): `Đã viết` | `Đang viết` | `Đã lập kế hoạch` | `Đang xem xét` | `Bị khóa`

---

## Screen 3 — Chapter Editor (`/projects/[id]/chapters/[cid]`)

**Phase:** 2 (+ 6 Prompt Edit) | **Wireframe:** #3

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Chapter fetch | Beats + prose skeleton | ✅ |
| Empty prose | No content | Placeholder "Bắt đầu viết hoặc dùng Prompt Edit…" | ✅ |
| Saving | PATCH in flight | Footer "Đang lưu…" | ✅ |
| Saved | Success | Footer timestamp + check icon | ✅ |
| Locked | `status=locked` | Read-only editor + banner | ✅ |
| AI running | Prompt instruct | Panel spinner; Send disabled | ✅ |
| Proposal ready | Turn completed | Apply + Compare enabled | ✅ |
| Provider error | 502 LLM | Inline error + Regenerate | ✅ |
| Error | 404/5xx | Error state + back to hub | ✅ |

---

## Screen 4 — Story Bible (`/projects/[id]/bible`)

**Phase:** 1 | **Wireframe:** #4

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | TOC fetch | TOC skeleton + content skeleton | ✅ |
| No selection | TOC loaded | "Chọn mục từ mục lục" | ✅ |
| Edit mode | User editing | Staged draft indicator; Save | ✅ |
| Broken wiki-link | Unknown ref | Dashed link + "Tạo entry?" | ⚪ |
| Error | 404/5xx | Error banner | ✅ |
| Success | Entry loaded | Metadata block + markdown | ✅ |

---

## Screen 5 — Continuity Gate (`/projects/[id]/chapters/[cid]/continuity`)

**Phase:** 2 | **Wireframe:** #5

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Report fetch | Issue table skeleton + diff skeleton | ✅ |
| Running check | Job in progress | Progress indicator; table disabled | ✅ |
| Stale report | Draft newer than report | Banner "Draft đã đổi — chạy lại check" | ✅ |
| FAIL unresolved | Open FAIL | Settle disabled; highlight FAIL rows | ✅ |
| WARN only | No FAIL | Settle enabled with override audit | ✅ |
| PASS | Clean report | Green badge; settle enabled | ✅ |
| Settle success | TXN OK | Toast + redirect hub; chapter locked | ✅ |
| Error | 404/5xx | Error state | ✅ |

---

## Screen 6 — New Project wizard (`/projects/new`)

**Phase:** 1 (+ 6 genre step) | **Wireframe:** #6

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Validation error | Invalid field | Inline error; Next disabled | ✅ |
| Creating | POST in flight | Spinner on Confirm; double-submit blocked | ✅ |
| Slug conflict | 409 | Suggest alternate slug | ✅ |
| Success | 201 | Redirect to new project hub | ✅ |
| Error | 5xx | Error on Confirm step | ✅ |

---

## Screen 7 — Characters + Inbox (`/projects/[id]/characters`)

**Phase:** 3 (+ 5 psyche tab) | **Wireframe:** #7

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | List fetch | Table skeleton | ✅ |
| Empty cast | No characters | "Thêm nhân vật seed hoặc viết prose để extract" | ✅ |
| Inbox empty | Count 0 | Tab hidden or badge 0 | ✅ |
| Inbox items | Count > 0 | Badge count; merge/promote/reject actions | ✅ |
| Merge conflict | Duplicate fields | Side-by-side picker modal | ✅ |
| Error | 404/5xx | Error banner | ✅ |
| Success | Data loaded | Table with tier, role, filters | ✅ |

Character detail tabs: Overview, Psyche (#10), Relationships (stub), Ledger tail, Appearances.

---

## Screen 8 — Outline / Timeline / Twist Board (`/projects/[id]/outline`)

**Phase:** 4 | **Wireframe:** #8

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Board fetch | Kanban column skeletons | ✅ |
| Empty board | No twists | Empty per column or global CTA | ✅ |
| Payoff without plants | Fairness fail | Red border on card + rule link | ✅ |
| Outline stub | Phase 8+ | Placeholder tab; not blocking parity | ⚪ |
| Timeline stub | Phase 8+ | Placeholder tab | ⚪ |
| Twist success | Cards loaded | 4 columns: Secrets, Plants, Payoffs, Revealed | ✅ |
| Error | 404/5xx | Error state | ✅ |

Keyboard: Shift+link per wireframe — document in [accessibility.md](./accessibility.md).

---

## Screen 9 — Power System bible (`/projects/[id]/bible/power-system`)

**Phase:** 6 | **Wireframe:** #9

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Ladder fetch | Rank + technique skeletons | ✅ |
| Disabled | Non-xianxia genre | "Genre không dùng power system" + genre link | ✅ |
| Validation | Non-monotonic ranks | Inline block on save | ✅ |
| Empty ladder | No ranks | CTA add first rank | ✅ |
| Error | 404/5xx | Error banner | ✅ |
| Success | Enabled + data | Rank ladder + techniques table | ✅ |

---

## Screen 10 — Psych / Relationship panels (character detail tab)

**Phase:** 5 | **Wireframe:** #10

| State | Trigger | Required UI | AC |
|-------|---------|-------------|-----|
| Loading | Psyche fetch | Form skeleton + timeline skeleton | ✅ |
| Empty psyche | No card yet | CTA seed psyche fields | ✅ |
| Timeline empty | No psych events | "Chưa có sự kiện tâm lý" | ✅ |
| Timeline populated | Events exist | Chart/table per chapter | ✅ |
| Relationships stub | Phase 8+ | Placeholder OK | ⚪ |
| Error | 404/5xx | Error inline on tab | ✅ |

---

## Wireframe acceptance summary (from 05-wireframes.md)

Phase 7 **Definition of done** when all ✅ rows above pass manual QA against wireframe images in `docs/wireframes/images/`:

| # | Screen | Parity gate |
|---|--------|-------------|
| 1 | Dashboard | Empty + skeleton + error |
| 2 | Project Hub | Empty chapters + WARN badge |
| 3 | Chapter Editor | All editor + Prompt Edit states |
| 4 | Story Bible | No selection + edit |
| 5 | Continuity Gate | FAIL block + settle success |
| 6 | Wizard | Validation + creating |
| 7 | Characters | Cast empty + inbox |
| 8 | Twist Board | Kanban + fairness fail |
| 9 | Power System | Disabled genre + validation |
| 10 | Psych | Timeline states |

---

## QA worksheet (copy for PR)

```markdown
## Screen parity sign-off

- [ ] 1 Dashboard
- [ ] 2 Project Hub
- [ ] 3 Chapter Editor
- [ ] 4 Story Bible
- [ ] 5 Continuity Gate
- [ ] 6 Wizard
- [ ] 7 Characters
- [ ] 8 Twist Board
- [ ] 9 Power System
- [ ] 10 Psych
- [ ] Global chrome (theme, locale, offline)
```

---

## Links

- [05-wireframes.md](../../product/05-wireframes.md)
- [web-screens.md](./web-screens.md)
- [test-strategy.md](./test-strategy.md)
