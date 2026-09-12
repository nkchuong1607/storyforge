# Phase 4 Web Screens

> Maps [openapi.yaml](./openapi.yaml) → UI from [05-wireframes.md](../../product/05-wireframes.md).  
> **Phase 4 screens:** Outline / Timeline / **Twist Board** (#8).  
> **Stub only:** Outline tree + Timeline swimlane — light placeholder; full advanced features Phase 8+.

---

## Shared conventions

| Topic | Rule |
|-------|------|
| API client | Same fetch wrapper + `X-User-Id` as Phase 1–3 |
| Types | Extend from Phase 4 OpenAPI |
| MSW | Handlers for all Phase 4 twist routes |
| Routing | `/projects/[projectId]/outline` with tab query `?tab=twist-board` (default tab for Phase 4 MVP: twist-board) |

---

## Hub updates (Phase 4 delta on Screen 2)

**Wireframe:** [project-hub.png](../../wireframes/images/project-hub.png)

| UI change | Behavior |
|-----------|----------|
| Outline / Twist nav | Link to Outline screen, default Twist Board tab |
| Fairness badge | Count payoffs with `fairness.state = fail` from board API |

| UI action | Endpoint |
|-----------|----------|
| Fairness badge | `GET /projects/{id}/twists/board` — count payoff cards with fail state |

---

## Screen 8 — Outline / Timeline / Twist Board

**Wireframe:** [outline-twist-board.png](../../wireframes/images/outline-twist-board.png)  
**Stories:** US-O01 (stub), US-O02 (stub), US-T01, US-T02

### Tab bar

| Tab | Phase 4 scope |
|-----|---------------|
| **Outline** | Light stub — static “Coming Phase 8” + chapter list from hub |
| **Timeline** | Light stub — placeholder swimlane message |
| **Twist Board** | **Full Phase 4 implementation** |

---

## Screen 8c — Twist Board Kanban (primary)

**Route:** `/projects/[projectId]/outline?tab=twist-board`

### Layout zones → components

| Zone | Component | Data source |
|------|-----------|-------------|
| Top bar | `TwistBoardHeader` | project title, "+ Secret", filter `kind` |
| Kanban | `TwistBoardColumns` | `GET .../twists/board` |
| Column | `TwistBoardColumn` | `columns[].cards` |
| Secret card | `SecretCard` | `card_type=twist`, status seeded |
| Plant card | `PlantCard` | `card_type=plant` |
| Payoff card | `PayoffCard` | `card_type=payoff` + fairness border |
| Revealed card | `RevealedCard` | read-only, status paid_off |
| Detail drawer | `TwistDetailDrawer` | `GET .../twists/{id}` + plants + payoff |
| Fairness panel | `FairnessCheckPanel` | board payoff `fairness` + link to continuity gate |

### Kanban columns (wireframe parity)

| Column (VI) | Column id | Card content |
|-------------|-----------|--------------|
| **Secrets** | `secrets` | `title`, `secret_truth` (author-only badge), status |
| **Plants** | `plants` | chapter #, salience, snippet, linked twist title |
| **Payoffs** | `payoffs` | target chapter, required plant ids / min_plants |
| **Revealed** | `revealed` | settled reveals read-only |

### API mapping

| UI action | Endpoint |
|-----------|----------|
| Load board | `GET /projects/{id}/twists/board` |
| Create secret | `POST /projects/{id}/twists` → opens in Secrets column |
| Edit secret | `PATCH .../twists/{twistId}` |
| Add plant | `POST .../twists/{twistId}/plants` |
| Edit plant | `PATCH .../twists/{twistId}/plants/{plantId}` |
| Register payoff | `POST .../twists/{twistId}/payoffs` |
| Abandon twist | `POST .../twists/{twistId}/transition` `{ status: abandoned }` |
| Open continuity | Navigate to `/chapters/{id}/continuity` for payoff chapter |
| Mark intentional | Continuity Gate `POST .../continuity-overrides` (Phase 2 screen) |

### Interaction — Shift+link (wireframe)

| Gesture | Client behavior | API |
|---------|-----------------|-----|
| Shift+drag plant → secret | Associate plant with twist | `PATCH .../plants/{plantId}` if moving twist_id |
| Shift+link payoff → plants | Set `required_plant_ids` | `PATCH .../payoffs/{payoffId}` |

Phase 4: client-side linking via existing PATCH routes; no dedicated link endpoint required.

### Payoff without plants UI (US-T02)

| State | UI |
|-------|-----|
| `fairness.state = fail` | Red border on payoff card |
| Tooltip | Issue code + link “Mở Continuity Gate” |
| After override | Orange “Intentional” chip; border neutral |

### Empty / loading states

| State | UI |
|-------|-----|
| **No twists** | “Đăng ký secret đầu tiên” CTA in Secrets column |
| **Loading** | Skeleton columns (wireframe) |
| **Revealed empty** | Muted placeholder text |

---

## Screen 8a — Outline tab (stub)

| Element | Behavior |
|---------|----------|
| Content | Chapter list reuse from hub + banner: “Outline tree — Phase 8” |
| API | `GET .../chapters` only |

---

## Screen 8b — Timeline tab (stub)

| Element | Behavior |
|---------|----------|
| Content | Placeholder swimlane graphic + “Timeline board — Phase 8” |
| API | None Phase 4 |

---

## Sidebar navigation

Add to `ProjectSidebar` (with Characters, Chapters):

```text
Outline / Twist  →  /projects/[projectId]/outline?tab=twist-board
```

---

## MSW / test hooks

| Handler | Notes |
|---------|-------|
| `GET .../twists/board` | Fixture with all four columns populated |
| Payoff fail fixture | One payoff card `fairness.state=fail` for US-T02 test |
| Writer context | Separate handler verifying no `secret_truth` in twist pack |

---

## Coverage scope (web)

Phase 4 Vitest ≥90% line coverage paths:

- `apps/web/components/twist-board/**`
- `apps/web/app/projects/[projectId]/outline/**`
- `apps/web/lib/api/twists.ts`

See [test-strategy.md](./test-strategy.md).

---

## Links

- [api-contracts.md](./api-contracts.md)
- [05-wireframes.md](../../product/05-wireframes.md) §8
- [Phase 3 web-screens](../phase-3/web-screens.md)
