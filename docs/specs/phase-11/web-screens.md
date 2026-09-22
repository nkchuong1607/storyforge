# Phase 11 Web Screens — Craft Pack

> UI contract for Mystery craft pack binding and checklist progress.

---

## Project Settings — Craft Pack panel

**Route:** `/projects/{id}/settings/craft-pack`

| Element | Behavior |
|---------|----------|
| Active pack badge | Shows `display_name` when bound |
| Install button | Calls install + activate for catalog pack |
| Deactivate | Clears active pack |
| Genre hint | Copy distinguishes rule pack (thresholds) vs craft pack (beats/checklist) |
| Checklist progress | Read-only list of pack checklist items with open/satisfied state |

**Out of scope P11a:** Full beat-map editor; video export.

---

## Continuity Gate

Add filter chip **`craft`** when project has active craft pack (alongside existing categories).

Issue table shows `craft_*` codes with Vietnamese messages from i18n.

---

## Chapter Editor — Prompt Edit

When craft pack active, context indicator shows "Craft context injected" (beats + open clues count). No auto-apply of craft suggestions.

---

## Links

- [api-contracts.md](./api-contracts.md)
- [Phase 6 web-screens](../phase-6/web-screens.md)
