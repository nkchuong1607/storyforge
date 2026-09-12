# Phase 7 Accessibility

> WCAG 2.1 **Level AA** targets for StoryForge author UI.  
> Verification: jest-axe smoke on primary routes (see [test-strategy.md](./test-strategy.md)).

---

## Targets

| Criterion | Target | Notes |
|-----------|--------|-------|
| Contrast | 4.5:1 normal text; 3:1 large text / UI components | Use design tokens from [design-system.md](./design-system.md); verify both themes |
| Keyboard | All interactive controls operable without pointer | Tab order follows visual layout |
| Focus | Visible focus indicator on all focusable elements | `focus-visible` ring 2px `--sf-accent`; never `outline: none` without replacement |
| Motion | Respect `prefers-reduced-motion` | Disable skeleton pulse, toast slide, Kanban drag animations |
| Screen readers | Meaningful names, roles, states | See patterns below |
| Touch | Min target 44×44px where feasible | Mobile not primary but wizard usable on tablet |

---

## Global patterns

### Skip link

First focusable element on every layout: "Skip to main content" → `#main-content`.

### Landmarks

```html
<header role="banner">
<nav aria-label="Project navigation">
<main id="main-content">
<aside aria-label="...">
```

### Live regions

| Component | ARIA |
|-----------|------|
| Toast | `role="status"` / `aria-live="polite"` |
| Save indicator | `aria-live="polite"` — "Đã lưu" |
| Continuity running | `aria-busy="true"` on issue table region |

### Theme / locale toggles

- `aria-label` includes current value: e.g. `aria-label="Theme: dark. Switch to light"`.
- Locale toggle: `lang` attribute on `<html>` updates with chrome locale (`vi` | `en`).

---

## Keyboard navigation

| Area | Keys | Behavior |
|------|------|----------|
| Global | `Tab` / `Shift+Tab` | Move focus; trap only inside modals |
| Modals | `Escape` | Close; restore focus to trigger |
| Wizard | `Enter` on primary when valid | Advance step (not when textarea focused) |
| Data tables | Arrow keys optional | Row `Enter` opens chapter; header sort `Space` |
| Dropdowns | `↑` `↓` `Enter` `Escape` | Menu pattern |

---

## Screen-specific patterns

### Chapter Editor

| Element | Pattern |
|---------|---------|
| Beats list | `role="listbox"` or semantic `<ul>`; selected beat `aria-current="true"` |
| Prose area | Labelled via `aria-labelledby` pointing to chapter title |
| Version dropdown | Native `<select>` or combobox with `aria-expanded` |
| Prompt Edit input | `aria-describedby` for char limit / error |
| Apply / Regenerate | `aria-disabled` when AI running |

### Continuity Gate

| Element | Pattern |
|---------|---------|
| FAIL/WARN/PASS badge | Not color-only — include text label |
| Issue table | `<table>` with `<th scope="col">`; sortable headers `aria-sort` |
| "Mark intentional" | Opens dialog with required reason field labelled |
| Settle button | Disabled state exposed via `aria-disabled` + tooltip reason when FAIL open |
| State diff panel | `aria-label="State diff preview"`; diff sections as headings |

### Twist Board (Kanban)

| Element | Pattern |
|---------|---------|
| Columns | `role="region"` + `aria-label="Plants"` etc. |
| Cards | `article` or `role="group"`; title as heading |
| Drag (pointer) | Optional Phase 7 — if implemented, provide **keyboard alternative**: move card via menu actions |
| Shift+link | Document as pointer-only enhancement; keyboard users use card action menu "Link to…" |
| Fairness fail | `aria-describedby` links to explanation text |

### Story Bible

| Element | Pattern |
|---------|---------|
| TOC tree | `tree` / `treeitem` with `aria-expanded` on folders |
| Metadata block | Definition list `<dl>` for id/type/version |
| Broken link | Announce via text, not dashed line alone |

### Characters / Inbox

| Element | Pattern |
|---------|---------|
| Inbox tab | `aria-selected` on tab; badge count in tab label |
| Merge modal | Two-column comparison; radio to pick canonical field |
| Tier badge | Text + color |

### Power System ladder

| Element | Pattern |
|---------|---------|
| Rank rows | Reorder buttons `aria-label="Move rank X up"` |
| Validation errors | `aria-invalid="true"` + `aria-describedby` error id |

---

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Skeleton: static gray block instead of pulse when reduced motion preferred.

---

## Color independence

Never convey state by color alone:

| State | Required non-color cue |
|-------|------------------------|
| FAIL | Icon + text "FAIL" |
| WARN | Icon + text "WARN" |
| Locked chapter | Lock icon + banner text |
| Payoff fairness fail | Border + text label on card |

---

## Testing checklist (manual + automated)

- [ ] Tab through each primary route without focus trap escape failures
- [ ] jest-axe zero **critical** violations on routes in test-strategy
- [ ] Dark mode contrast spot-check (Dashboard, Gate, Editor)
- [ ] Screen reader spot-check: Gate issue table, Wizard steps, Toast announcement
- [ ] Zoom 200% — no horizontal scroll on hub table (wrap or scroll region)

---

## Links

- [design-system.md](./design-system.md)
- [screen-parity.md](./screen-parity.md)
- [test-strategy.md](./test-strategy.md)
- [WCAG 2.1 Quick Ref](https://www.w3.org/WAI/WCAG21/quickref/)
