# Phase 7 API Contracts

> **N/A — no new REST endpoints in Phase 7.**

Machine-readable stub: [openapi.yaml](./openapi.yaml) (`/health` only, documents the no-API decision).

Phase 1–6 [api-contracts](../phase-6/api-contracts.md) remain authoritative for all domain routes.

---

## Client-only preferences contract

Phase 7 stores author UI preferences in the browser. Implementers MUST follow this contract so a future server-prefs API can migrate without breaking users.

### Theme

| Field | Detail |
|-------|--------|
| Storage | `localStorage['storyforge.theme']` |
| Values | `light` \| `dark` \| `system` |
| Cookie (optional) | `sf_theme` — same enum; `Path=/`; `SameSite=Lax` |
| Default | `system` |
| Apply | Set `data-theme` on `<html>`; resolve `system` via `matchMedia('(prefers-color-scheme: dark)')` |

### Locale (chrome)

| Field | Detail |
|-------|--------|
| Storage | `localStorage['storyforge.locale']` |
| Values | `vi` \| `en` |
| Cookie (optional) | `sf_locale` |
| Default | `vi` |
| Apply | Load messages from [i18n.md](./i18n.md); set `<html lang>` |

### Migration path (Phase 8+)

If `GET/PATCH /users/me/preferences` ships later:

1. On login, merge server prefs over local if server timestamp newer
2. Write back to localStorage for offline consistency
3. Do not implement in Phase 7

---

## Why no API?

| Reason | Detail |
|--------|--------|
| Auth stub | MVP uses `X-User-Id` header — no real user record for prefs |
| Scope | Phase 7 is web polish; avoids API + migration churn |
| SSR | Cookie mirror sufficient for theme flash prevention |
| Cross-device sync | Explicitly out of Phase 7 — deferred with real auth |

---

## API agent checklist

- [ ] **Skip** Phase 7 API implementation PR unless product explicitly expands scope
- [ ] Do not add Alembic migrations for user prefs in Phase 7
- [ ] Ensure `/health` unchanged — no regressions from web work

---

## Links

- [i18n.md](./i18n.md)
- [design-system.md](./design-system.md)
- [Phase 6 api-contracts](../phase-6/api-contracts.md)
