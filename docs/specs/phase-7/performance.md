# Phase 7 Performance

> Perceived performance and layout stability for author UI. No new backend caching in Phase 7.

---

## Goals

| Metric | Target | Tool |
|--------|--------|------|
| CLS | < 0.1 on primary routes | Lighthouse manual spot-check |
| First meaningful paint | Skeleton within 100ms of navigation | Visual QA |
| Save feedback | Optimistic UI < 50ms | Vitest timing optional |
| Bundle | No heavy chart libs for psych timeline MVP | Review import graph |

---

## Skeleton loading

Every data-heavy screen implements skeleton matching final layout (see [screen-parity.md](./screen-parity.md)):

| Screen | Skeleton pattern |
|--------|------------------|
| Dashboard | 4 card skeletons |
| Hub | Summary cards + table rows |
| Editor | Beats list + prose block |
| Bible | TOC + content panel |
| Gate | Table rows + diff panel |
| Characters | Table rows |
| Twist board | 4 column placeholders |
| Power system | Rank list + technique rows |

Use shared `Skeleton` primitive from [design-system.md](./design-system.md). Reserve min-height to prevent layout shift when data arrives.

---

## Route-level loading

Next.js App Router:

```
app/
  projects/[projectId]/loading.tsx
  projects/[projectId]/chapters/[chapterId]/loading.tsx
  ...
```

| Rule | Detail |
|------|--------|
| `loading.tsx` | Shows shell + skeleton; inherits layout sidebar |
| Suspense boundaries | Wrap slow client widgets (Prompt Edit history) |
| Error boundaries | `error.tsx` per segment — retry button |

Avoid full-page spinner without layout skeleton.

---

## Optimistic UI (safe only)

| Action | Optimistic? | Rollback |
|--------|-------------|----------|
| Chapter title edit | Yes | Revert on 4xx/5xx + toast |
| Beat reorder (local) | Yes | Refetch on failure |
| Settle / Approve | **No** | Wait for server — canon mutation |
| Prompt Edit Apply | **No** | Wait for new version id |
| Theme / locale toggle | Yes (local) | N/A — client prefs |
| Twist card drag | Optional | Refetch board on failure |

---

## Data fetching

| Pattern | Use |
|---------|-----|
| Parallel fetch | Hub summary + chapter list concurrently |
| Stale-while-revalidate | Optional — cache project header in client store |
| Debounce | Search 300ms (existing Phase 1) |
| Polling | Continuity job — exponential backoff, max 30s |

No Redis or CDN changes in Phase 7.

---

## Layout shift prevention

| Technique | Application |
|-----------|-------------|
| Fixed header/sidebar dimensions | App shell |
| `aspect-ratio` on project card covers | Dashboard |
| Table `min-height` | Empty → skeleton → rows |
| Font `display: swap` | Inter preload in layout |
| No dynamic injection above fold | Toasts portal only |

---

## Images and assets

- Wireframe placeholders: SVG or CSS gradients — no large PNGs
- Icons: single icon set (e.g. Lucide) tree-shaken imports
- Dark mode: no separate image assets required

---

## Prompt Edit / LLM panel

| State | UX |
|-------|-----|
| Instruct pending | Disable Send; show inline spinner in panel only — do not block prose editing |
| Long operations | Elapsed timer optional after 3s |
| Compare modal | Lazy-load diff content on open |

FakeLLM responses remain instant in tests — no artificial delay.

---

## Monitoring (optional Phase 7)

- `reportWebVitals` to console in dev only
- No production APM requirement in Phase 7

---

## Links

- [screen-parity.md](./screen-parity.md)
- [web-screens.md](./web-screens.md)
- [test-strategy.md](./test-strategy.md)
