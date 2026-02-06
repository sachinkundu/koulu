# End-to-End (E2E) Tests

Browser-based tests using Playwright to validate critical user journeys through the full Koulu stack.

---

## Quick Start

### Prerequisites

1. **Node.js 18+** installed
2. **Backend running** (FastAPI on port 8000)
3. **Frontend running** (Vite dev server on port 3000)
4. **Test database** (`koulu_e2e`) created

### Installation

```bash
# From this directory
cd tests/e2e

# Install dependencies
npm install

# Install Playwright browsers (Chromium, Firefox, WebKit)
npx playwright install

# Optional: Install system dependencies (Linux only)
npx playwright install-deps
```

### Run Tests

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test specs/identity/login.spec.ts

# Run in UI mode (interactive)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

---

## Directory Structure

```
tests/e2e/
├── fixtures/               # Reusable test helpers
│   ├── auth.ts            # Login, register, create user helpers
│   ├── test-data.ts       # Test data generators
│   └── pages/             # Page Object Models
│       ├── base-page.ts
│       ├── auth/
│       ├── profile/
│       ├── community/
│       └── classroom/
│
├── specs/                 # Test specifications
│   ├── identity/          # Authentication, profile tests
│   ├── community/         # Feed, posts tests
│   └── classroom/         # Course, lesson tests
│
├── helpers/               # Utility functions
│   ├── api-helpers.ts     # Backend API calls
│   ├── db-helpers.ts      # Database seeding/cleanup
│   └── email-helpers.ts   # Mailhog integration
│
├── playwright.config.ts   # Playwright configuration
├── package.json           # Dependencies
└── README.md              # This file
```

---

## Test Philosophy

**E2E tests are selective, not exhaustive:**

- ✅ Test critical user journeys (register → login → profile)
- ✅ Test multi-page workflows
- ✅ Test frontend-backend integration
- ❌ Don't test every edge case (use unit/BDD tests)
- ❌ Don't test backend logic (use BDD tests)
- ❌ Don't test validation rules (use unit tests)

**Target:** 10-20 E2E tests covering critical paths (not 100+ tests)

---

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate to starting page, login if needed
  });

  test('should do something when user takes action', async ({ page }) => {
    // Given: Initial state
    await page.goto('/some-page');

    // When: User action
    await page.click('[data-testid="submit-btn"]');

    // Then: Expected outcome
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });
});
```

### Using Page Object Models

```typescript
import { ProfileEditPage } from '../../fixtures/pages/profile/profile-edit-page';

test('should update profile', async ({ page }) => {
  const editPage = new ProfileEditPage(page);

  await editPage.goto();
  await editPage.updateDisplayName('New Name');
  await editPage.clickSave();

  await expect(page).toHaveURL(/\/profile$/);
});
```

### Test Data Setup (API vs UI)

```typescript
// ✅ GOOD: Setup via API (fast, reliable)
test.beforeEach(async ({ request }) => {
  const response = await request.post('/api/v1/auth/register', {
    data: { email: `test-${Date.now()}@example.com`, password: 'testpass123' }
  });
  const { user_id } = await response.json();
  // User ready for test
});

// ❌ BAD: Setup via UI (slow, flaky)
test.beforeEach(async ({ page }) => {
  await page.goto('/register');
  await page.fill('[data-testid="email"]', email);
  await page.fill('[data-testid="password"]', password);
  await page.click('[data-testid="submit"]');
  // Too many UI steps, prone to failure
});
```

---

## Best Practices

### Selectors

**Use `data-testid` attributes:**

```typescript
// ✅ GOOD: Stable, explicit test contract
await page.click('[data-testid="login-btn"]');

// ❌ BAD: Fragile, breaks on CSS changes
await page.click('button.bg-blue-500');

// ❌ BAD: Fragile, breaks on text changes
await page.click('button:has-text("Login")');
```

**Frontend must have `data-testid` attributes:**

```tsx
<button data-testid="login-btn" className="...">Login</button>
```

### Waits

**Use Playwright's auto-wait (no manual sleeps):**

```typescript
// ✅ GOOD: Wait for specific condition
await page.click('[data-testid="submit"]');
await page.waitForSelector('[data-testid="success-message"]', { state: 'visible' });

// ❌ BAD: Hard-coded wait (flaky)
await page.click('[data-testid="submit"]');
await page.waitForTimeout(2000); // Arbitrary wait
```

### Test Isolation

**Each test must be independent:**

```typescript
// ✅ GOOD: Unique test data
const email = `test-${Date.now()}-${Math.random()}@example.com`;

// ❌ BAD: Reused test data (conflicts)
const email = 'test@example.com';
```

---

## Debugging

### 1. Playwright Inspector

Step through test interactively:

```bash
npx playwright test --debug specs/identity/login.spec.ts
```

### 2. Trace Viewer

Time-travel debugger with network logs, screenshots, DOM snapshots:

```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace test-results/.../trace.zip
```

### 3. Headed Mode

See browser actions in real-time:

```bash
npx playwright test --headed --slowMo=1000
```

### 4. Screenshots

Add screenshots to test:

```typescript
await page.screenshot({ path: 'debug.png' });
```

### 5. Pause Execution

Pause and inspect browser:

```typescript
await page.pause();
```

---

## Common Issues

### "Browser not found"

```bash
npx playwright install chromium
```

### "Cannot connect to localhost:3000"

Start frontend dev server:

```bash
cd ../../frontend
npm run dev
```

### "Backend API not responding"

Start backend:

```bash
cd ../..
docker-compose up -d
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### "Test data conflict"

Use unique test data:

```typescript
const email = `test-${Date.now()}-${Math.random()}@example.com`;
```

### "Element not found"

1. Check if `data-testid` exists in frontend
2. Check if element is rendered (inspect page)
3. Add explicit wait: `await page.waitForSelector('[data-testid="..."]')`

---

## CI Integration

E2E tests run automatically on pull requests via `.github/workflows/e2e-tests.yml`.

**Manual CI trigger:**
- Go to GitHub Actions → E2E Tests → Run workflow

**Simulate CI locally:**

```bash
# Run exactly as CI would
npx playwright test --workers=2 --retries=2 --project=chromium
```

---

## Configuration

### Environment Variables

```bash
# .env.e2e
BASE_URL=http://localhost:3000
API_URL=http://localhost:8000
DATABASE_URL=postgresql://koulu:koulu@localhost:5432/koulu_e2e
MAILHOG_URL=http://localhost:8025
```

### Playwright Config

See `playwright.config.ts` for:
- Browser configuration (Chromium, Firefox, WebKit)
- Timeout settings
- Retry configuration
- Reporter settings
- WebServer auto-start

---

## Commands Reference

### Run Tests

```bash
# All tests
npx playwright test

# Specific file
npx playwright test specs/identity/login.spec.ts

# Specific test by name
npx playwright test --grep "should login successfully"

# Specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox

# Parallel execution (4 workers)
npx playwright test --workers=4

# UI mode (interactive)
npx playwright test --ui

# Headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

### Generate Tests

```bash
# Record actions and generate test code
npx playwright codegen http://localhost:3000
```

### Reports

```bash
# HTML report
npx playwright show-report

# Trace viewer
npx playwright show-trace trace.zip
```

### Maintenance

```bash
# Update Playwright
npm update @playwright/test

# Update browsers
npx playwright install

# List all tests
npx playwright test --list
```

---

## Resources

- **Playwright Docs:** https://playwright.dev/
- **Design Doc:** `../../docs/testing/e2e-testing-design.md`
- **Skill Doc:** `../../.claude/skills/e2e-test/SKILL.md`
- **Examples:** See `specs/` directory for test examples

---

## Questions?

- Run `/e2e-test` command for guided execution
- Read `docs/testing/e2e-testing-design.md` for strategy
- Check Playwright docs for API reference
