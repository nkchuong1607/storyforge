# Phase 7 Specifications — UI Polish

> **Status:** Canonical contract for Phase 7 implementation.  
> **Scope:** Design system, screen parity, accessibility, i18n, performance, web polish workstreams, and test strategy only — no feature code in the specs PR.

Phase 7 delivers **production-grade UX** after Phases 1–6 MVP: design tokens (light/dark), wireframe parity across all primary screens, WCAG AA accessibility, Vietnamese-primary chrome i18n, skeleton/loading/error states, and performance polish. **No new domain features** — polish only.

---

## Documents in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [design-system.md](./design-system.md) | Tokens, light/dark, component inventory, anti-slop principles |
| 2 | [screen-parity.md](./screen-parity.md) | Empty/loading/error/success checklist per screen; wireframe acceptance |
| 3 | [accessibility.md](./accessibility.md) | WCAG AA, keyboard, focus, contrast, reduced motion, ARIA patterns |
| 4 | [i18n.md](./i18n.md) | VI default chrome, EN secondary; message file layout |
| 5 | [performance.md](./performance.md) | Skeletons, optimistic UI, route loading, CLS avoidance |
| 6 | [openapi.yaml](./openapi.yaml) | **No new API** — documents client-only prefs decision; `/health` stub only |
| 7 | [api-contracts.md](./api-contracts.md) | N/A — client prefs contract reference |
| 8 | [web-screens.md](./web-screens.md) | Polish workstreams by route; design-system adoption plan |
| 9 | [test-strategy.md](./test-strategy.md) | ≥90% on new polish modules; a11y smoke; GHA lightweight |

---

## MVP Phase 7 scope (from [06-build-plan.md](../../product/06-build-plan.md))

### In scope

| Area | Deliverable |
|------|-------------|
| Design system | CSS variables / Tailwind theme extension: color, type, spacing, radius; light + dark |
| Component library | Button, Input, Badge, Table, Modal, Skeleton, Empty, Toast — shared under `apps/web/components/ui/` |
| Wireframe parity | All 10 wireframe screens + wizard/inbox — states from [05-wireframes.md](../../product/05-wireframes.md) |
| Accessibility | WCAG 2.1 AA targets; keyboard nav; focus rings; jest-axe smoke on primary routes |
| i18n | VI default chrome; EN toggle; `messages/vi.json`, `messages/en.json`; no hard-coded chrome |
| Theme + locale prefs | **Client-only** — `localStorage` + cookie mirror for SSR hint; no Phase 7 API |
| Performance | Route-level `loading.tsx`, skeleton placeholders, safe optimistic UI |
| External craft refs | taste-skill + ui-ux-pro-max on dev machines (not vendored) |

### Out of scope (Phase 7)

| Item | Deferred to |
|------|-------------|
| Neo4j relationship graph | Phase 8+ |
| EPUB / DOCX export | Phase 8+ |
| Series / parent bible projects | Phase 8+ |
| Scene engine lint | Phase 8+ |
| Research module | Phase 8+ |
| Realtime collaboration | Phase 8+ |
| Full E2E Playwright suite | Phase 8+ (a11y smoke in Vitest only) |
| Server-persisted user prefs API | Phase 8+ (unless auth ships first) |
| Outline tree + Timeline swimlane (advanced) | Phase 8+ stubs remain |

---

## Dependencies on Phase 1–6

Phase 7 **requires** Phases 1–6 feature-complete for MVP screens:

| Prior artifact | Phase 7 usage |
|----------------|---------------|
| All Phase 1–6 routes + components | Polish targets — no new routes except `/settings` chrome |
| Phase 6 OpenAPI | Unchanged; Phase 7 adds no endpoints |
| Wireframes 1–10 | Acceptance source for [screen-parity.md](./screen-parity.md) |
| FakeLLM / MSW | Unchanged — polish must not break test doubles |

Do not block Phase 7 on Phase 8+ modules. Polish what exists.

---

## Reading order for implementers

### Web agent (`apps/web`) — **primary**

1. This README — scope boundaries
2. [design-system.md](./design-system.md) — tokens + components
3. [screen-parity.md](./screen-parity.md) — per-screen state checklist
4. [web-screens.md](./web-screens.md) — route workstreams
5. [i18n.md](./i18n.md) — message keys + locale provider
6. [accessibility.md](./accessibility.md) — WCAG + ARIA
7. [performance.md](./performance.md) — loading + optimistic rules
8. [test-strategy.md](./test-strategy.md) — coverage + jest-axe
9. Skills: `storyforge-web-next`, `storyforge-ui-external`
10. Wireframes: [05-wireframes.md](../../product/05-wireframes.md)

### API agent (`apps/api`) — **only if needed**

Phase 7 default: **no API work**. Theme and locale are client-only. See [openapi.yaml](./openapi.yaml) and [api-contracts.md](./api-contracts.md).

Optional parallel PR only if product later requires server prefs — not in Phase 7 scope.

### Both agents

- **Spec-first:** Update specs before contradicting implementation.
- **Parallel safe:** Web PR primary; API PR **skipped** unless prefs API explicitly added later.
- **Quality gate:** Line coverage ≥ 90% locally on **new polish modules**; GHA runs `make check` only.
- **FakeLLM unchanged:** Prompt Edit tests keep FakeLLM default.

---

## Suggested PR sequence (after specs merge)

| Order | PR | Owner |
|-------|-----|-------|
| 1 | **Phase 7 specs** (this PR) | Platform |
| 2 | `web/phase-7-implementation` — design system, i18n, a11y, screen parity | Web agent |
| 3 | `api/phase-7-implementation` | **N/A** — skip unless server prefs added |

PR **2** is the sole implementation PR for Phase 7 default scope.

---

## Definition of done (Phase 7)

- [ ] Design tokens applied app-wide; dark mode toggle persists in `localStorage`
- [ ] Every primary screen passes [screen-parity.md](./screen-parity.md) checklist
- [ ] Chrome strings externalized to `messages/vi.json` / `messages/en.json`
- [ ] jest-axe smoke passes on routes listed in [test-strategy.md](./test-strategy.md)
- [ ] `make check` green; `make test-web-cov` ≥ 90% on scoped polish paths
- [ ] [05-wireframes.md](../../product/05-wireframes.md) acceptance criteria satisfied

---

## Validation

```bash
make validate-specs   # Phase 1–7 OpenAPI YAML (Phase 7: /health stub only)
make check            # full harness
```

---

## Links

- [Phase 1 specs](../phase-1/README.md) … [Phase 6 specs](../phase-6/README.md)
- [Build plan Phase 7](../../product/06-build-plan.md#phase-7--ui-polish)
- [Wireframes](../../product/05-wireframes.md)
- [Quality gates](../../engineering/quality-gates.md)
- [AGENTS.md](../../../AGENTS.md)
