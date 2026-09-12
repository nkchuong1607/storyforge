# StoryForge Web

Next.js 15 App Router frontend for Phase 1 author UI.

## Development

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

## API configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | StoryForge API base URL |

Copy root `.env.example` to `.env` and set `NEXT_PUBLIC_API_URL` when pointing at a real API.

### Auth stub

All API requests (except `/health`) send `X-User-Id` from `localStorage` key `storyforge-user-id`. Default dev user: `550e8400-e29b-41d4-a716-446655440000`.

## Offline / tests (MSW)

Tests use [MSW](https://mswjs.io/) handlers in `mocks/handlers.ts` that mirror `docs/specs/phase-1/openapi.yaml`. The UI works without a running API when MSW is active (test environment).

To develop against mocks manually, you can wire MSW in the browser — for Phase 1, run tests locally or start the API with `make api-dev`.

## Phase 1 routes

| Route | Screen |
|-------|--------|
| `/` | Dashboard |
| `/projects/new` | New Project wizard |
| `/projects/[id]` | Project Hub |
| `/projects/[id]/bible` | Story Bible |

## Testing (local only)

```bash
npm run test          # Vitest
npm run test:coverage # ≥90% gate on Phase 1 modules
make test-web-cov     # from repo root
```

Coverage scope: `lib/api`, dashboard, wizard, hub, bible, and shared UI components. E2E/Playwright is not run in CI.
