# Phase 7 Test Strategy

> Quality bar for Phase 7 **web implementation** PR. Specs PR adds validation only.  
> Extends [Phase 6 test strategy](../phase-6/test-strategy.md).

---

## Principles

1. **Spec-first** — Tests assert [design-system.md](./design-system.md), [screen-parity.md](./screen-parity.md), [i18n.md](./i18n.md), [accessibility.md](./accessibility.md).
2. **Web-primary** — No Phase 7 API tests unless prefs API added (default: skip).
3. **Coverage ≥ 90% line** — **Hard fail locally** on scoped polish modules via `make test-web-cov`.
4. **GHA lightweight** — CI runs `make check` only (includes `validate-specs` for Phase 7 OpenAPI stub).
5. **FakeLLM unchanged** — Existing Prompt Edit tests keep FakeLLM/MSW; polish must not break them.

---

## Coverage scope (Phase 7)

Add to quality-gates web scope:

| Path | Rationale |
|------|-----------|
| `apps/web/components/ui/**` | Design system primitives |
| `apps/web/components/providers/**` | Theme, locale, toast |
| `apps/web/lib/i18n/**` | Message loading, hooks |
| `apps/web/lib/prefs/**` | Theme/locale persistence |
| `apps/web/messages/**` | JSON validity (lint script) |

Existing phase route tests: maintain ≥90% combined for phase-scoped modules listed in prior specs; new assertions for states/i18n.

**API:** No new coverage requirement — `/health` unchanged.

---

## Test pyramid (Phase 7)

```text
        a11y smoke (jest-axe)     ← primary routes, zero critical violations
               │
        Component (Vitest)        ← ui primitives, providers, Empty/Skeleton
               │
        Integration (Vitest+MSW)  ← screen states, locale switch, theme toggle
               │
        E2E Playwright            ← DEFER Phase 8+
```

---

## Accessibility testing

**Tool:** `jest-axe` (or `@axe-core/react` in Vitest jsdom).

| Route | Min checks |
|-------|------------|
| `/` | Dashboard loaded (MSW) |
| `/projects/new` | Wizard step 1 |
| `/projects/[id]` | Hub with chapters |
| `/projects/[id]/chapters/[cid]` | Editor layout |
| `/projects/[id]/chapters/[cid]/continuity` | Gate with FAIL row |
| `/projects/[id]/characters` | List + inbox tab |
| `/projects/[id]/outline?tab=twist-board` | Kanban |

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

it('dashboard has no a11y violations', async () => {
  const { container } = render(<DashboardPage />);
  expect(await axe(container)).toHaveNoViolations();
});
```

**Gate:** Fail on **critical** violations; **serious** documented with ticket if third-party limitation.

Manual: keyboard tab spot-check on Gate + Editor before merge.

---

## i18n tests

| Test | Assert |
|------|--------|
| Default locale | Renders VI dashboard title |
| Switch to EN | Header toggle → English chrome |
| Missing key (dev) | Falls back per i18n.md |
| `messages/*.json` | Valid JSON; keys match between vi/en (CI script) |

---

## Theme tests

| Test | Assert |
|------|--------|
| Toggle dark | `data-theme="dark"` on documentElement |
| Persist | Reload mock localStorage retains choice |
| System preference | Mock `matchMedia` for system mode |

---

## Screen state tests

For each screen in [screen-parity.md](./screen-parity.md), at least one Vitest test:

| State | Example assert |
|-------|----------------|
| Loading | Skeleton testId present |
| Empty | Empty CTA visible |
| Error | Retry button + banner text |
| Success | Primary content rendered |

Use MSW to force 200/404/500 responses.

---

## Performance-related tests

| Test | Assert |
|------|--------|
| Skeleton dimensions | Table skeleton has min-height class |
| Optimistic save | Title updates before MSW resolves (editor) |
| Settle not optimistic | Button shows loading until 200 |

---

## Message key parity script

Add to `scripts/harness/` or web package:

```bash
# Pseudo: diff keys between vi.json and en.json
node scripts/check-i18n-keys.js
```

Wire into `make check` when implementation lands.

---

## CI matrix

| Job | Specs PR | Web implementation PR |
|-----|----------|----------------------|
| `make check` | ✅ | ✅ |
| `make validate-specs` | ✅ | ✅ if specs touched |
| `make test-web-cov` | skip | ✅ local ≥90% |
| `make test-api-cov` | skip | skip (no API) |
| jest-axe | skip | ✅ part of web tests |
| Playwright | skip | skip |

---

## FakeLLM regression

After polish, re-run Phase 6 Prompt Edit tests unchanged:

- MSW FakeLLM handlers still match OpenAPI
- Apply/Regenerate/Compare flows pass
- No new env vars required

---

## Agent checklist (before web PR)

1. Read Phase 7 spec package
2. Implement W1→W5 adoption plan
3. Extract i18n strings; verify vi/en parity
4. Add jest-axe smoke for listed routes
5. Run `make test-web-cov` — ≥90% on scoped paths
6. Run `make check`
7. Complete [screen-parity.md](./screen-parity.md) QA worksheet

---

## Links

- [quality-gates.md](../../engineering/quality-gates.md)
- [Phase 6 test strategy](../phase-6/test-strategy.md)
- [accessibility.md](./accessibility.md)
