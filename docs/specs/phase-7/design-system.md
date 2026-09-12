# Phase 7 Design System

> Canonical tokens and component inventory for StoryForge author UI.  
> **Craft references:** taste-skill + ui-ux-pro-max on dev machines — principles summarized here; do not copy proprietary skill text into the repo.

---

## Design principles (anti-slop)

StoryForge is a **long-form writing tool**, not a marketing landing page. Visual direction:

| Principle | Application |
|-----------|-------------|
| **Editor-first** | Content areas dominate; chrome is quiet, low-contrast until interactive |
| **Purposeful density** | Tables and ledgers show data; avoid oversized hero whitespace on hub screens |
| **Restrained palette** | One accent (brand) + semantic colors; no gradient-heavy card grids |
| **Typographic hierarchy** | Clear H1/H2/body/mono distinction; prose editor uses comfortable reading size |
| **Motion with intent** | Transitions ≤ 200ms; respect `prefers-reduced-motion` |
| **No template chrome** | Avoid generic “AI dashboard” patterns: floating blobs, glassmorphism stacks, rainbow badges |

Install external skills before visual implementation (`docs/agent-setup.md`).

---

## Token architecture

Implement as CSS custom properties on `:root` and `[data-theme="dark"]`, consumed by Tailwind theme extension (`apps/web/tailwind.config.ts`).

### Color

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--sf-bg-base` | `#FAFAF9` | `#0C0C0D` | Page background |
| `--sf-bg-surface` | `#FFFFFF` | `#161618` | Cards, panels |
| `--sf-bg-muted` | `#F4F4F5` | `#1F1F23` | Sidebar, table stripe |
| `--sf-border` | `#E4E4E7` | `#2A2A2E` | Dividers, inputs |
| `--sf-text-primary` | `#18181B` | `#FAFAFA` | Headings, body |
| `--sf-text-secondary` | `#71717A` | `#A1A1AA` | Labels, meta |
| `--sf-accent` | `#2563EB` | `#3B82F6` | Primary actions, links |
| `--sf-accent-hover` | `#1D4ED8` | `#60A5FA` | Hover state |
| `--sf-success` | `#16A34A` | `#22C55E` | PASS, settled |
| `--sf-warning` | `#CA8A04` | `#EAB308` | WARN continuity |
| `--sf-danger` | `#DC2626` | `#EF4444` | FAIL, destructive |
| `--sf-info` | `#0891B2` | `#06B6D4` | Info banners |

**Contrast:** All text/background pairs used for chrome must meet WCAG AA (4.5:1 body, 3:1 large text). See [accessibility.md](./accessibility.md).

### Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--sf-font-sans` | `Inter, system-ui, sans-serif` | Chrome, tables, forms |
| `--sf-font-serif` | `Literata, Georgia, serif` | Optional prose preview (not editor monospace) |
| `--sf-font-mono` | `JetBrains Mono, ui-monospace, monospace` | Bible metadata, IDs, diff |
| `--sf-text-xs` | `0.75rem / 1rem` | Badges, table meta |
| `--sf-text-sm` | `0.875rem / 1.25rem` | Secondary UI |
| `--sf-text-base` | `1rem / 1.5rem` | Default chrome |
| `--sf-text-lg` | `1.125rem / 1.75rem` | Section titles |
| `--sf-text-xl` | `1.25rem / 1.875rem` | Page titles |
| `--sf-text-prose` | `1.0625rem / 1.75rem` | Chapter editor reading column |

### Spacing

Base unit **4px**. Scale: `1, 2, 3, 4, 5, 6, 8, 10, 12, 16` (×4px).

| Token | px | Usage |
|-------|-----|-------|
| `--sf-space-1` | 4 | Icon gaps |
| `--sf-space-2` | 8 | Inline padding |
| `--sf-space-3` | 12 | Input padding-y |
| `--sf-space-4` | 16 | Card padding |
| `--sf-space-6` | 24 | Section gaps |
| `--sf-space-8` | 32 | Page gutters |

### Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--sf-radius-sm` | `4px` | Badges, chips |
| `--sf-radius-md` | `8px` | Buttons, inputs |
| `--sf-radius-lg` | `12px` | Cards, modals |
| `--sf-radius-full` | `9999px` | Avatars, pills |

### Elevation (light mode only subtle shadows)

| Token | Value |
|-------|-------|
| `--sf-shadow-sm` | `0 1px 2px rgb(0 0 0 / 0.05)` |
| `--sf-shadow-md` | `0 4px 12px rgb(0 0 0 / 0.08)` |

Dark mode: prefer border emphasis over shadow.

---

## Light / dark mode

| Concern | Rule |
|---------|------|
| Default | Follow `prefers-color-scheme` on first visit |
| User override | Toggle in header/settings; persist `theme: light \| dark \| system` in `localStorage` key `storyforge.theme` |
| SSR hint | Mirror theme in cookie `sf_theme` for flash-free first paint (optional Phase 7) |
| Implementation | `data-theme="light|dark"` on `<html>`; tokens swap via CSS variables |
| Images | Wireframe placeholders OK; no photo-heavy assets |

---

## Component inventory

Location: `apps/web/components/ui/`. All accept `className` merge via `cn()` utility.

### Button

| Variant | Usage |
|---------|-------|
| `primary` | Main CTA (Save, Approve & Settle) |
| `secondary` | Cancel, Back |
| `ghost` | Toolbar icons |
| `destructive` | Reject draft, delete rank |

Sizes: `sm`, `md` (default), `lg`. States: default, hover, focus-visible ring, disabled, loading (spinner replaces label).

### Input

Text, textarea, select wrappers. Label + description + error slot. Required `aria-invalid` on validation error.

### Badge

Variants: `default`, `success`, `warning`, `danger`, `info`, `outline`. Used for chapter status, continuity level, genre pill.

### Table

Sortable header optional. Row hover, selected state, sticky header for long chapter lists. Empty row → delegate to Empty component.

### Modal

Focus trap, `role="dialog"`, `aria-modal="true"`, Escape to close, return focus to trigger. Used for Compare diff, merge conflict, confirm destructive.

### Skeleton

Pulse animation (disabled when `prefers-reduced-motion`). Preset layouts: `CardSkeleton`, `TableSkeleton`, `KanbanColumnSkeleton`.

### Empty

Illustration slot (simple SVG, not stock photo), title, description, optional CTA. Used for dashboard, inbox, cast.

### Toast

Global provider; variants mirror Badge semantics. Auto-dismiss 5s; pause on hover. `aria-live="polite"`.

---

## Layout shell

| Region | Spec |
|--------|------|
| App header | 56px height; logo, project search, theme toggle, locale toggle, avatar |
| Project sidebar | 240px fixed; collapsible to icons on `< lg` |
| Content max-width | Hub/table: fluid; Bible/editor: readable column max ~720px for prose |
| Z-index scale | modal 50, toast 60, tooltip 40 |

---

## Domain-specific styling notes

| Screen | Guidance |
|--------|----------|
| Chapter Editor | Beats sidebar narrower than prose; Prompt Edit panel visually secondary (muted bg) |
| Continuity Gate | FAIL rows use danger left border; do not color entire table red |
| Twist Kanban | Column headers fixed; cards draggable with visible focus ring when keyboard-selected |
| Power ladder | Monotonic rank indicator (step connector); invalid state inline, not modal-only |

---

## Migration plan (implementation)

1. Add tokens + Tailwind extension
2. Build primitives (Button → Toast)
3. Replace ad-hoc styles screen-by-screen per [web-screens.md](./web-screens.md)
4. Remove duplicate inline colors before PR merge

---

## Links

- [screen-parity.md](./screen-parity.md)
- [accessibility.md](./accessibility.md)
- [web-screens.md](./web-screens.md)
- [05-wireframes.md](../../product/05-wireframes.md)
