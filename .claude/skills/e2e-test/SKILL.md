---
name: e2e-test
description: Run, debug, and fix end-to-end browser tests using Playwright
user_invocable: true
model: opus
---

# E2E Test Skill

## Purpose

Run Playwright end-to-end tests, debug failures, fix flaky tests, and add new E2E tests for critical user journeys.

**Key Principle:** E2E tests validate full-stack integration through browser automation. They complement (not replace) unit and BDD tests.

---

## Usage

```bash
# Run all E2E tests
/e2e-test

# Run specific test file
/e2e-test specs/identity/profile-edit.spec.ts

# Debug mode (opens interactive debugger)
/e2e-test --debug specs/identity/login.spec.ts

# Add new E2E test for feature
/e2e-test --add identity/profile-view

# Fix flaky test
/e2e-test --fix specs/community/feed.spec.ts
```

---

## Prerequisites

**Before running E2E tests, ensure:**

1. **Playwright is installed:**
   ```bash
   cd tests/e2e
   npm install
   npx playwright install chromium
   ```

2. **Backend is running:**
   ```bash
   docker-compose up -d  # Start postgres, redis, mailhog
   cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000 &
   ```

3. **Frontend is running:**
   ```bash
   cd frontend && npm run dev &  # Starts on http://localhost:3000
   ```

4. **Test database exists:**
   ```bash
   docker compose exec -T postgres psql -U koulu -d postgres -c "CREATE DATABASE koulu_e2e OWNER koulu;" 2>/dev/null || true
   ```

5. **Rate limits cleared (Redis):**
   ```bash
   docker compose exec -T redis redis-cli FLUSHALL
   ```
   Registration is rate-limited to 5 per 15 minutes per IP. Repeated test runs will hit this limit. Always flush Redis before running E2E tests.

**Verification:**
- Backend: `curl http://localhost:8000/health` → 200 OK
- Frontend: `curl http://localhost:3000` → HTML response
- Playwright: `cd tests/e2e && npx playwright --version` → version number

---

## Project-Specific Setup

- **Database isolation**: E2E uses `koulu_e2e` database, dev uses `koulu`. Script drops/recreates DB each run.
- **Port isolation**: Ports are computed per-worktree by `project-env.sh`. E2E ports = dev ports + 100.
- **Run E2E**: `./scripts/run-e2e-tests.sh` — starts its own backend + frontend, cleans up on exit
- **Seed data**: Do NOT truncate `communities` or `categories` — they're seeded by migration `66ce48aa6407`
- **Race condition**: FastAPI yield dependencies commit AFTER response sent; `createVerifiedUser` retries verification up to 5x
- **Rate limiting**: `cleanTestState()` must be in every test suite's `beforeEach`; `flushRateLimits()` MUST be awaited
- **Compose project name**: derived from directory basename by `project-env.sh`. Each worktree gets its own containers/volumes via `KOULU_VOLUME_PREFIX`.

---

## Workflow

### Mode 1: Run E2E Tests

**Step 1: Verify Prerequisites**

Check that backend and frontend are running:

```bash
# Check backend
curl -s http://localhost:8000/health | jq .

# Check frontend
curl -s http://localhost:3000 | head -1

# Check test database
docker compose exec -T postgres psql -U koulu -d koulu_e2e -c "\dt"
```

**If any service is down, start it before proceeding.**

**Step 2: Run Tests**

```bash
cd tests/e2e

# Run all tests (default: Chromium)
npx playwright test

# Run specific test file
npx playwright test specs/identity/profile-edit.spec.ts

# Run tests matching pattern
npx playwright test --grep "profile update"

# Run in UI mode (interactive)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
```

**Step 3: Analyze Results**

```bash
# View HTML report (auto-opens on failure)
npx playwright show-report

# View trace for failed test
npx playwright show-trace trace.zip
```

**Step 4: Report Status**

Report test results to user:

```
✅ All E2E tests passing (X tests in Ys)
❌ E2E tests failing: X failed, Y passed
   - Failed tests: [list test names]
   - See report: tests/e2e/playwright-report/index.html
```

---

### Mode 2: Debug Failing Test

**Step 1: Reproduce Failure**

Run the failing test in debug mode:

```bash
cd tests/e2e

# Debug mode (step through test)
npx playwright test specs/path/to/test.spec.ts --debug

# OR: Headed mode (see browser)
npx playwright test specs/path/to/test.spec.ts --headed
```

**Step 2: Analyze Failure**

Common failure patterns:

1. **Element not found:**
   - Check if `data-testid` attribute exists in frontend code
   - Check if selector is correct
   - Check if element is hidden/disabled

2. **Timeout waiting for element:**
   - Element may be loading slower than expected
   - Network request may be failing
   - Element may not exist at all

3. **Assertion failure:**
   - Expected value doesn't match actual
   - Check if backend API is returning correct data
   - Check if frontend is rendering correct data

4. **Navigation failure:**
   - Check if route exists in frontend router
   - Check if redirect logic is correct
   - Check if authentication is required

**Step 3: Check Trace**

View trace to see what happened:

```bash
# Traces are saved in test-results/ directory
npx playwright show-trace test-results/specs-identity-profile/trace.zip
```

**Trace shows:**
- Every action taken (click, fill, navigate)
- Network requests (API calls, responses)
- Console logs (errors, warnings)
- Screenshots at each step
- DOM snapshots

**Step 4: Identify Root Cause**

Ask:
- Is this a test issue (wrong selector, wrong assertion)?
- Is this a frontend bug (UI not rendering, wrong state)?
- Is this a backend bug (API returning wrong data)?
- Is this a timing issue (test runs too fast)?

**Step 5: Fix Issue**

**If test issue:**
- Update selector (use correct `data-testid`)
- Update assertion (check correct element)
- Add explicit wait (if timing issue)

**If frontend bug:**
- Fix frontend code
- Re-run E2E test to verify

**If backend bug:**
- Fix backend code
- Re-run BDD tests first, then E2E test

**If timing issue (flaky test):**
- Replace hard-coded waits with Playwright's auto-wait
- Add `waitForSelector` with explicit condition
- Use `waitForLoadState` for page loads

---

### Mode 3: Fix Flaky Test

**Flaky test = test that fails intermittently without code changes**

**Step 1: Identify Flakiness Pattern**

Run test multiple times:

```bash
cd tests/e2e

# Run test 10 times
for i in {1..10}; do
  echo "Run $i:"
  npx playwright test specs/path/to/test.spec.ts
done
```

**If test fails < 10% of runs → flaky test**

**Step 2: Common Causes**

| Symptom | Cause | Fix |
|---------|-------|-----|
| **"Element not found" sometimes** | Race condition (element not rendered yet) | Use `waitForSelector` with explicit state |
| **"Timeout" sometimes** | Network delay | Increase timeout or use `waitForLoadState('networkidle')` |
| **"Wrong text" sometimes** | Async update not complete | Wait for specific text with `waitForSelector('text=...')` |
| **"Wrong URL" sometimes** | Navigation not complete | Use `waitForURL` instead of checking immediately |
| **"Test data conflict"** | Test data from previous run | Use unique test data per run (timestamp) |

**Step 3: Anti-Patterns to Fix**

```typescript
// ❌ BAD: Hard-coded wait (flaky)
await page.click('[data-testid="submit"]');
await page.waitForTimeout(2000); // Arbitrary wait
const text = await page.textContent('.message');

// ✅ GOOD: Wait for specific condition
await page.click('[data-testid="submit"]');
await page.waitForSelector('.message', { state: 'visible' });
const text = await page.textContent('.message');

// ❌ BAD: Check URL immediately (flaky)
await page.click('[data-testid="login"]');
expect(page.url()).toContain('/feed'); // May not have navigated yet

// ✅ GOOD: Wait for URL change
await page.click('[data-testid="login"]');
await page.waitForURL('**/feed');
expect(page.url()).toContain('/feed');

// ❌ BAD: Reused test data (conflicts)
const email = 'test@example.com'; // Same across tests

// ✅ GOOD: Unique test data
const email = `test-${Date.now()}-${Math.random()}@example.com`;
```

**Step 4: Fix and Verify**

1. Update test with fix
2. Run 10 times to verify stability:
   ```bash
   for i in {1..10}; do npx playwright test specs/path/to/test.spec.ts; done
   ```
3. If passes 10/10 times → fixed!

---

### Mode 4: Add New E2E Test

**Step 1: Identify Critical Journey**

E2E tests should cover **critical user journeys only**:

✅ **Add E2E test for:**
- Multi-page workflows (register → verify → login → profile)
- Complex state management (update profile → see change in another page)
- Real-time features (post → see in feed immediately)
- Payment flows
- Authentication flows

❌ **Skip E2E test for:**
- Single API calls (use BDD tests)
- Validation edge cases (use unit tests)
- Backend-only features
- Simple CRUD operations

**Step 2: Check Existing Tests**

```bash
cd tests/e2e

# List all test files
find specs -name "*.spec.ts"

# Search for similar test
grep -r "profile" specs/
```

**Step 3: Create Test File**

Follow naming convention: `specs/{context}/{feature}.spec.ts`

**Example: Add E2E test for profile view**

```bash
cd tests/e2e
mkdir -p specs/identity
touch specs/identity/profile-view.spec.ts
```

**Step 4: Write Test Using Page Object Model**

```typescript
// specs/identity/profile-view.spec.ts
import { test, expect } from '@playwright/test';
import { createVerifiedUser } from '../../fixtures/auth';
import { ProfileViewPage } from '../../fixtures/pages/profile/profile-view-page';

test.describe('Profile View', () => {
  let email: string;
  let password: string;

  test.beforeEach(async ({ request }) => {
    // Setup: Create verified user via API (fast)
    const user = await createVerifiedUser(request);
    email = user.email;
    password = user.password;
  });

  test('should view own profile after login', async ({ page }) => {
    // Given: User is logged in
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.click('[data-testid="login-btn"]');
    await page.waitForURL('**/feed');

    // When: User navigates to profile
    const profilePage = new ProfileViewPage(page);
    await profilePage.goto();

    // Then: Profile information is displayed
    const displayedEmail = await profilePage.getEmail();
    expect(displayedEmail).toBe(email);

    const displayName = await profilePage.getDisplayName();
    expect(displayName).toBeTruthy(); // Should exist
  });
});
```

**Step 5: Create Page Object (if needed)**

```typescript
// fixtures/pages/profile/profile-view-page.ts
import { Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileViewPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators
  private readonly emailText = '[data-testid="profile-email"]';
  private readonly displayNameText = '[data-testid="profile-display-name"]';

  // Actions
  async goto() {
    await this.page.goto('/users/me/profile');
    await this.waitForPageLoad();
  }

  // Getters
  async getEmail(): Promise<string> {
    return await this.page.textContent(this.emailText) || '';
  }

  async getDisplayName(): Promise<string> {
    return await this.page.textContent(this.displayNameText) || '';
  }
}
```

**Step 6: Run Test**

```bash
cd tests/e2e
npx playwright test specs/identity/profile-view.spec.ts
```

**Step 7: Verify Test Quality**

Checklist:
- [ ] Test uses `data-testid` selectors (not CSS classes)
- [ ] Test uses Page Object Model (not direct page calls)
- [ ] Test setup uses API (not UI)
- [ ] Test has no hard-coded waits (`waitForTimeout`)
- [ ] Test uses unique data (no conflicts)
- [ ] Test is stable (passes 10/10 times)

---

## Commands Reference

### Basic Commands

```bash
cd tests/e2e

# Install dependencies (one-time)
npm install
npx playwright install chromium

# Run all tests
npx playwright test

# Run specific file
npx playwright test specs/identity/login.spec.ts

# Run specific test by name
npx playwright test --grep "should login successfully"

# Run in UI mode (interactive)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed --headed

# Debug mode (step through)
npx playwright test --debug

# Generate code (record actions)
npx playwright codegen http://localhost:3000
```

### Advanced Commands

```bash
# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run on mobile
npx playwright test --project=mobile-chrome

# Parallel execution (4 workers)
npx playwright test --workers=4

# Serial execution (1 worker)
npx playwright test --workers=1

# Update snapshots
npx playwright test --update-snapshots

# Trace viewer
npx playwright show-trace trace.zip

# HTML report
npx playwright show-report

# List all tests
npx playwright test --list
```

### CI Commands

```bash
# Run in CI mode (retries, parallel)
npx playwright test --retries=2 --workers=2

# Generate JUnit report
npx playwright test --reporter=junit

# Save artifacts
npx playwright test --output=./test-results
```

---

## Debugging Tips

### 1. Use Playwright Inspector

```bash
npx playwright test --debug
```

**Features:**
- Step through test line by line
- Inspect page at any step
- Run commands in console
- See locators highlighted

### 2. Use Trace Viewer

```bash
# Run with trace
npx playwright test --trace on

# View trace
npx playwright show-trace test-results/.../trace.zip
```

**Features:**
- Time-travel debugging
- Network logs (API calls)
- Console logs
- Screenshots
- DOM snapshots

### 3. Use Headed Mode

```bash
npx playwright test --headed --slowMo=1000
```

**Features:**
- See browser actions
- Slow down actions (1000ms delay)
- Useful for visual debugging

### 4. Console Logs

Add console logs to test:

```typescript
test('debug test', async ({ page }) => {
  console.log('Starting test...');

  await page.goto('/login');
  console.log('URL:', page.url());

  await page.fill('[data-testid="email"]', email);
  console.log('Filled email');

  const screenshot = await page.screenshot({ path: 'debug.png' });
  console.log('Screenshot saved');
});
```

### 5. Pause Execution

```typescript
test('pause test', async ({ page }) => {
  await page.goto('/login');

  // Pause here and inspect browser
  await page.pause();

  await page.click('[data-testid="submit"]');
});
```

---

## Best Practices

### ✅ DO

- **Use `data-testid` attributes** for stable selectors
- **Use Page Object Models** for reusability
- **Setup via API** (fast, reliable)
- **Use unique test data** (no conflicts)
- **Use Playwright's auto-wait** (no manual sleeps)
- **Test user journeys** (not implementation)
- **Write descriptive test names** (what + expected outcome)
- **Fix flaky tests immediately** (don't ignore)
- **Clean up test data** in `afterEach` using delete API helpers
- **Track created resource IDs** and delete them in reverse order

### ❌ DON'T

- **Don't use CSS classes/IDs** as selectors (fragile)
- **Don't use hard-coded waits** (`waitForTimeout`)
- **Don't setup via UI** (slow, flaky)
- **Don't reuse test data** (conflicts)
- **Don't test every edge case** (use unit/BDD tests)
- **Don't ignore flaky tests** (fix root cause)
- **Don't couple tests** (each test independent)
- **Don't test backend logic** (use BDD tests)
- **Don't leave test data behind** — every test must clean up after itself

---

## Common Issues

### Issue 1: "Browser not found"

**Symptom:**
```
Error: browserType.launch: Executable doesn't exist at ...
```

**Solution:**
```bash
cd tests/e2e
npx playwright install chromium
```

### Issue 2: "Cannot connect to localhost:3000"

**Symptom:**
```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000
```

**Solution:**
```bash
# Start frontend dev server
cd frontend
npm run dev
```

### Issue 3: "Test data conflict"

**Symptom:**
```
Error: Email already exists
```

**Solution:**
Use unique test data:
```typescript
const email = `test-${Date.now()}-${Math.random()}@example.com`;
```

### Issue 4: "Element not found"

**Symptom:**
```
Error: Timeout waiting for selector '[data-testid="submit"]'
```

**Solution:**
1. Check if `data-testid` exists in frontend code
2. Check if element is rendered (inspect page)
3. Check if element is hidden/disabled
4. Add explicit wait: `await page.waitForSelector('[data-testid="submit"]')`

### Issue 5: "Flaky test"

**Symptom:**
Test passes sometimes, fails sometimes

**Solution:**
1. Remove hard-coded waits (`waitForTimeout`)
2. Use `waitForSelector` with explicit state
3. Use `waitForURL` for navigation
4. Use `waitForLoadState('networkidle')` for API calls

### Issue 6: "Rate limit exceeded"

**Symptom:**
```
Error: Registration failed
```
Page shows `Registration failed` alert instead of success state. API returns `{"error":"Rate limit exceeded: 5 per 15 minute"}`.

**Solution:**
```bash
docker compose exec -T redis redis-cli FLUSHALL
```
This clears all rate limit counters. Always do this before E2E test runs.

### Issue 7: "MailHog email not found" (multipart parsing)

**Symptom:**
```
Error: No verification email found for <email> after 10 retries
```
But emails ARE visible in MailHog UI (http://localhost:8025).

**Cause:** `Content.Body` for multipart emails contains raw MIME boundaries with base64-encoded content. The token regex can't match inside base64 text.

**Solution:** In `getEmailBody()`, check `MIME.Parts` first (which decodes base64), then fall back to `Content.Body`.

---

## CI Integration

### GitHub Actions Workflow

E2E tests run automatically on PRs via `.github/workflows/e2e-tests.yml`.

**Manual trigger:**
```bash
# From GitHub UI: Actions → E2E Tests → Run workflow
```

**Local simulation of CI:**
```bash
# Run exactly as CI would
cd tests/e2e
npx playwright test --workers=2 --retries=2 --project=chromium
```

---

## Test Coverage Guidelines

**Target:** 10-20 E2E tests covering critical user journeys

**Current coverage:**
```bash
# Count E2E tests
cd tests/e2e
find specs -name "*.spec.ts" -exec grep -l "test(" {} \; | wc -l
```

**Priority order:**
1. **P0 (Critical):** Authentication, core workflows (5-8 tests)
2. **P1 (High):** Data updates, state management (3-5 tests)
3. **P2 (Medium):** Search, filtering, real-time (2-4 tests)
4. **P3 (Low):** Advanced features (1-3 tests)

**Stop adding E2E tests when:**
- Total count exceeds 20 tests
- Execution time exceeds 10 minutes
- You're testing edge cases (use unit/BDD instead)

---

## Success Metrics

**A good E2E test suite:**
- ✅ Covers critical user journeys (not exhaustive)
- ✅ Runs in < 10 minutes (all tests)
- ✅ Pass rate > 95% (low flakiness)
- ✅ Catches frontend-backend integration bugs
- ✅ Easy to maintain (Page Object Models)

**A bad E2E test suite:**
- ❌ Duplicates unit/BDD coverage
- ❌ Takes > 30 minutes to run
- ❌ Flaky (< 80% pass rate)
- ❌ Hard to maintain (no POMs, fragile selectors)
- ❌ Tests every edge case

---

## Related Documents

- `docs/testing/e2e-testing-design.md` - E2E testing strategy and architecture
- `tests/e2e/README.md` - Setup guide and usage instructions
- `CLAUDE.md` - Development rules and verification checklist
- `.claude/skills/implement-feature.md` - Feature implementation workflow

---

## Example Workflows

### Scenario 1: User reports "profile update not working"

```bash
# Step 1: Run E2E test for profile update
cd tests/e2e
npx playwright test specs/identity/profile-edit.spec.ts

# Step 2: If test passes, issue is not reproducible
# If test fails, debug to find root cause
npx playwright test specs/identity/profile-edit.spec.ts --debug

# Step 3: Fix bug (frontend or backend)

# Step 4: Re-run E2E test to verify fix
npx playwright test specs/identity/profile-edit.spec.ts

# Step 5: Run all tests to check for regressions
npx playwright test
```

### Scenario 2: Add E2E test for new feature

```bash
# Step 1: Implement feature (use /implement-feature)

# Step 2: Decide if E2E test is needed
# - Is it a critical user journey? YES
# - Does it span multiple pages? YES
# → Add E2E test

# Step 3: Create test file
cd tests/e2e
mkdir -p specs/classroom
touch specs/classroom/course-completion.spec.ts

# Step 4: Write test (see Mode 4 above)

# Step 5: Run test
npx playwright test specs/classroom/course-completion.spec.ts

# Step 6: Verify stability (run 10 times)
for i in {1..10}; do npx playwright test specs/classroom/course-completion.spec.ts; done
```

### Scenario 3: Fix flaky test in CI

```bash
# Step 1: Reproduce locally
cd tests/e2e
npx playwright test specs/community/feed.spec.ts --retries=0

# Step 2: Run multiple times to trigger flakiness
for i in {1..10}; do npx playwright test specs/community/feed.spec.ts; done

# Step 3: Debug failure
npx playwright test specs/community/feed.spec.ts --debug

# Step 4: Identify cause (see Mode 3 above)
# Common: hard-coded wait, race condition, test data conflict

# Step 5: Fix test

# Step 6: Verify stability
for i in {1..10}; do npx playwright test specs/community/feed.spec.ts; done

# Step 7: Push fix, CI should be green
```

---

## Notes

- E2E tests are **optional** but **recommended** for critical flows
- E2E tests are **not** part of Definition of Done for features
- E2E tests **complement** (not replace) unit and BDD tests
- Keep E2E test count low (10-20 tests max)
- Fix flaky tests immediately (don't ignore)
- Use manual execution scripts that CI can also use
