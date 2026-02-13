# End-to-End (E2E) Tests

Browser-based tests using Playwright to validate critical user journeys through the full Koulu stack.

---

## Quick Start

### Prerequisites

1. **Node.js 20+** installed
2. **Docker services running** (`docker compose up -d` — PostgreSQL, Redis, MailHog)

### Installation

```bash
cd tests/e2e
npm install
npx playwright install
npx playwright install-deps  # Linux only
```

### Run Tests

**Always use the isolated test runner** — it creates a separate `koulu_e2e` database and starts backend/frontend on dedicated ports so E2E tests never touch your dev environment:

```bash
# Run all E2E tests
./scripts/run-e2e-tests.sh

# Run a specific test file
./scripts/run-e2e-tests.sh specs/identity/login.spec.ts

# Run tests matching a name pattern
./scripts/run-e2e-tests.sh --grep "should login successfully"

# Run in headed mode (see browser)
./scripts/run-e2e-tests.sh --headed

# Run in debug mode
./scripts/run-e2e-tests.sh --debug
```

> **Do NOT run `npx playwright test` directly** — it will fail with a missing `BASE_URL` error. This is intentional to prevent tests from accidentally hitting the dev database.

---

## What `run-e2e-tests.sh` Does

1. Checks Docker services (PostgreSQL, Redis, MailHog)
2. Drops and recreates the `koulu_e2e` database
3. Runs Alembic migrations (includes seed data)
4. Flushes Redis rate limits
5. Starts an E2E backend on a separate port (+100 from dev)
6. Starts an E2E frontend on a separate port (+100 from dev)
7. Exports `BASE_URL`, `API_URL`, `MAILHOG_URL` pointing at E2E servers
8. Runs Playwright tests
9. Cleans up (kills E2E servers on exit)

---

## Directory Structure

```
tests/e2e/
├── helpers/               # Utility functions
│   ├── env.ts            # Environment variable validation (fail-fast)
│   ├── api-helpers.ts    # Backend API calls
│   ├── db-cleanup.ts     # Database cleanup
│   └── email-helpers.ts  # MailHog integration
│
├── specs/                 # Test specifications
│   ├── identity/          # Authentication, profile tests
│   ├── community/         # Feed, posts tests
│   └── classroom/         # Course, lesson tests
│
├── global-setup.ts        # Runs before all tests
├── global-teardown.ts     # Runs after all tests
├── playwright.config.ts   # Playwright configuration
├── package.json           # Dependencies
└── README.md              # This file
```

---

## Test Philosophy

**E2E tests are selective, not exhaustive:**

- Test critical user journeys (register -> login -> profile)
- Test multi-page workflows
- Test frontend-backend integration
- Don't test every edge case (use unit/BDD tests)
- Don't test backend logic (use BDD tests)

**Target:** 10-20 E2E tests covering critical paths (not 100+ tests)

---

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something when user takes action', async ({ page }) => {
    await page.goto('/some-page');
    await page.click('[data-testid="submit-btn"]');
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});
```

### Test Data Setup (API vs UI)

```typescript
// GOOD: Setup via API (fast, reliable)
import { createVerifiedUser } from '../helpers/api-helpers';

test.beforeEach(async () => {
  const user = await createVerifiedUser();
});

// BAD: Setup via UI (slow, flaky)
```

### Selectors

Use `data-testid` attributes:

```typescript
await page.click('[data-testid="login-btn"]');   // stable
// avoid: page.click('button.bg-blue-500')        // fragile
```

### Test Isolation

Each test must use unique data:

```typescript
import { generateTestEmail } from '../helpers/api-helpers';
const email = generateTestEmail(); // e2e-<timestamp>-<random>@example.com
```

---

## Debugging

```bash
# Step through test interactively
./scripts/run-e2e-tests.sh --debug specs/identity/login.spec.ts

# Run with trace for time-travel debugging
./scripts/run-e2e-tests.sh --trace on

# View trace after run
cd tests/e2e && npx playwright show-trace test-results/.../trace.zip

# View HTML report after run
cd tests/e2e && npx playwright show-report
```

---

## Common Issues

### "Missing required environment variable: BASE_URL"

You ran `npx playwright test` directly. Use `./scripts/run-e2e-tests.sh` instead.

### "Docker services not running"

```bash
docker compose up -d
```

### "Browser not found"

```bash
cd tests/e2e && npx playwright install chromium
```

---

## Environment Variables

These are set automatically by `run-e2e-tests.sh` — you should not need to set them manually:

| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | E2E frontend URL | `http://localhost:5273` |
| `API_URL` | E2E backend API URL | `http://localhost:8100/api/v1` |
| `MAILHOG_URL` | MailHog web UI URL | `http://localhost:8025` |
| `REDIS_CONTAINER` | Docker container name | `koulu_redis` |
| `POSTGRES_CONTAINER` | Docker container name | `koulu_postgres` |
| `E2E_DB_NAME` | E2E database name | `koulu_e2e` |

---

## Resources

- **Playwright Docs:** https://playwright.dev/
- **Design Doc:** `../../docs/testing/e2e-testing-design.md`
- **Skill Doc:** `../../.claude/skills/e2e-test/SKILL.md`
- **Examples:** See `specs/` directory for test examples
