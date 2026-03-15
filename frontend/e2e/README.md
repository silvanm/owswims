# E2E tests (Playwright)

Key app flows: app load, markers visible, open event (via URL), URL update, direct event URL, reload persistence.

## Prerequisites

- Backend (Django) running with GraphQL at `http://localhost:8000/graphql` (or set `E2E_GRAPHQL_URL` / `GRAPHQL_ENDPOINT`).
- Frontend (Nuxt) running at `http://localhost:3000` (or set `BASE_URL` / `E2E_BASE_URL`).
- At least one event in the default date range (today → +12 months) so the test target helper can resolve a location and slug.

## First-time setup

Install browsers (required once):

```bash
npx playwright install
```

## Run tests

```bash
npm run e2e
```

With UI:

```bash
npm run e2e:ui
```

## Optional env overrides

- `E2E_GRAPHQL_URL` or `GRAPHQL_ENDPOINT` – GraphQL endpoint (default: `http://localhost:8000/graphql`).
- `BASE_URL` or `E2E_BASE_URL` – frontend base URL (default: `http://localhost:3000`).
- `E2E_LOCATION_ID` and `E2E_EVENT_SLUG` – pin a specific location and event (e.g. for CI with seeded data).

## GitHub Actions (scheduled)

Workflow [`.github/workflows/e2e-scheduled.yml`](../../.github/workflows/e2e-scheduled.yml) runs E2E daily (06:00 UTC) and on manual trigger.

**Configure in repo → Settings → Secrets and variables → Actions:**

- **Variables:** Set `E2E_BASE_URL` and `E2E_GRAPHQL_URL` to your frontend and GraphQL URLs (e.g. production or staging). Required for the scheduled run.
- **Secret (optional):** `SLACK_WEBHOOK_URL` – Slack incoming webhook URL. If set, a failed run posts a message with a link to the workflow run.
