# Phase 7 Web Screens — Polish Workstreams

> Cross-cutting polish on all Phase 1–6 routes. **No new domain features.**  
> State checklist: [screen-parity.md](./screen-parity.md). Tokens: [design-system.md](./design-system.md).

---

## Shared conventions (Phase 7 delta)

| Topic | Rule |
|-------|------|
| Components | Import from `components/ui/*` — no ad-hoc button styles |
| i18n | All chrome via `t()` — see [i18n.md](./i18n.md) |
| Theme | `ThemeProvider` at root; tokens via CSS variables |
| Loading | Route `loading.tsx` + screen skeletons per [performance.md](./performance.md) |
| A11y | jest-axe on route smoke tests — [accessibility.md](./accessibility.md) |
| API | Unchanged Phase 6 client — no new endpoints |

---

## Design-system adoption plan

| Wave | Scope | Exit criteria |
|------|-------|---------------|
| **W1 Foundation** | Tokens, ThemeProvider, LocaleProvider, ui primitives | Storybook or Vitest renders Button/Badge/Modal |
| **W2 Shell** | App header, sidebar, layout | Theme + locale toggles work; skip link present |
| **W3 Data screens** | Dashboard, Hub, Characters, Twist board | Table/Badge/Empty/Skeleton adopted |
| **W4 Authoring** | Editor, Bible, Gate, Power, Psych | Editor/Gate a11y patterns; toast on settle |
| **W5 Wizard + sweep** | New project wizard, string audit, parity QA | [screen-parity.md](./screen-parity.md) all ✅ |

Waves may ship in one PR if small team; order reduces merge conflicts.

---

## Route workstreams

### `/` — Dashboard (Screen 1)

| Workstream | Tasks |
|------------|-------|
| Visual | Project cards use `Card` + tokens; genre `Badge` |
| States | Wire `EmptyState`, `CardSkeleton` ×4, `ErrorBanner` |
| i18n | Extract dashboard keys |
| a11y | FAB has accessible name; search `aria-label` |

---

### `/projects/new` — Wizard (Screen 6)

| Workstream | Tasks |
|------------|-------|
| Visual | Step indicator component; genre cards consistent hover/focus |
| States | Inline validation; confirm spinner |
| i18n | Step titles, validation messages |
| a11y | `aria-current="step"` on indicator; focus management on step change |

---

### `/projects/[projectId]` — Hub (Screen 2)

| Workstream | Tasks |
|------------|-------|
| Visual | Summary cards + `Table` for chapters |
| States | Empty chapters, table skeleton, WARN badge |
| i18n | Status labels from message keys |
| Performance | Parallel fetch; table min-height |

---

### `/projects/[projectId]/chapters/[chapterId]` — Editor (Screen 3)

| Workstream | Tasks |
|------------|-------|
| Visual | Three-column layout polish; Prompt Edit muted panel |
| States | All editor + AI states from parity doc |
| i18n | Footer save strings, Prompt Edit actions |
| a11y | Beats list keyboard; Prompt panel labels |
| Performance | Non-blocking AI spinner |

---

### `/projects/[projectId]/chapters/[chapterId]/continuity` — Gate (Screen 5)

| Workstream | Tasks |
|------------|-------|
| Visual | Issue `Table` with level badges; diff panel |
| States | Running, stale, FAIL block settle, success toast |
| i18n | Level labels FAIL/WARN/PASS |
| a11y | Table headers; settle disabled announced |

---

### `/projects/[projectId]/bible` — Story Bible (Screen 4)

| Workstream | Tasks |
|------------|-------|
| Visual | TOC tree + metadata `dl` styling |
| States | No selection, loading, edit mode |
| i18n | TOC section names (VI) |

---

### `/projects/[projectId]/bible/power-system` — Power (Screen 9)

| Workstream | Tasks |
|------------|-------|
| Visual | Rank ladder step UI; techniques table |
| States | Disabled genre, validation inline |
| i18n | Disabled message, rank labels |

---

### `/projects/[projectId]/characters` — Characters (Screen 7)

| Workstream | Tasks |
|------------|-------|
| Visual | Table + inbox split; detail tabs |
| States | Empty cast, inbox badge, merge modal |
| i18n | Inbox actions, tier labels |
| a11y | Tab `aria-selected`; merge modal focus trap |

---

### `/projects/[projectId]/characters/[characterId]` — Detail + Psych (Screen 10)

| Workstream | Tasks |
|------------|-------|
| Visual | Psyche form fields; timeline chart/table |
| States | Empty psyche, timeline empty/populated |
| i18n | Tab names, field labels |

---

### `/projects/[projectId]/outline` — Twist Board (Screen 8)

| Workstream | Tasks |
|------------|-------|
| Visual | Kanban columns + cards; fairness border |
| States | Column skeletons; payoff fail highlight |
| i18n | Column headers |
| a11y | Keyboard link alternative; column regions |

Outline/Timeline tabs: keep Phase 4 stubs styled consistently (muted placeholder).

---

### Global — Settings / header

| Route / region | Tasks |
|----------------|-------|
| Header | Theme toggle, locale toggle, user menu stub |
| Optional `/settings` | Duplicate prefs; keyboard shortcuts help (⌘K, ⌘S) |

---

## Files touched (implementation guide)

```
apps/web/
  app/globals.css              # token definitions
  tailwind.config.ts           # theme extension
  components/ui/               # Button, Input, Badge, Table, Modal, Skeleton, Empty, Toast
  components/providers/        # ThemeProvider, LocaleProvider, ToastProvider
  messages/vi.json, en.json
  lib/i18n/
  lib/prefs/theme.ts, locale.ts
  app/**/loading.tsx, error.tsx
```

---

## Out of scope per route

- Export button on editor (Phase 8+)
- Graph view on Bible/Psych (Phase 8+)
- Realtime presence indicators
- Server sync of theme/locale

---

## Links

- [screen-parity.md](./screen-parity.md)
- [Phase 1–6 web-screens](../phase-1/web-screens.md)
- [05-wireframes.md](../../product/05-wireframes.md)
