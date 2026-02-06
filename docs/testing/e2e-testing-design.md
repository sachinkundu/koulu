# End-to-End (E2E) Testing Design Document

**Version:** 1.0
**Last Updated:** February 6, 2026
**Status:** Approved
**Document Type:** Technical Design Document

---

## 1. Executive Summary

This document outlines the strategy, architecture, and implementation plan for browser-based end-to-end (E2E) testing in the Koulu platform. E2E tests complement existing unit and BDD tests by validating critical user journeys through the full stack (frontend + backend + database + browser).

**Key Decisions:**
- **Tool:** Playwright (TypeScript-first, multi-browser, fast)
- **Scope:** Critical user journeys only (not exhaustive)
- **Strategy:** Selective coverage (happy paths + critical flows)
- **CI Integration:** Run on PRs, Chromium initially, expand to matrix later

---

## 2. Problem Statement

### 2.1 Current Testing Gaps

Koulu currently has:
- ✅ **Unit tests** (pytest + vitest) - Domain logic, value objects, handlers
- ✅ **BDD tests** (pytest-bdd) - API-level behavior, backend integration
- ❌ **E2E tests** - Missing browser-based full-stack validation

**What's not covered:**
1. Frontend-backend integration (API wiring, state management)
2. Browser-specific issues (rendering, JavaScript errors, CORS)
3. User workflows spanning multiple pages/systems
4. Visual regression (layout, responsive design)
5. Real user interactions (clicking, typing, navigation)

**Example bugs E2E tests catch:**
- Backend returns 200 OK, but frontend shows error message (state management bug)
- Email verification link works in API tests, but clicking it in browser fails (routing issue)
- Profile update succeeds, but avatar doesn't refresh (cache invalidation bug)
- Form validation works, but submit button stays disabled (UI state bug)

### 2.2 Why Now?

- Phase 3 of user profile is complete (backend + BDD tests passing)
- Frontend UI will be built in Phase 5
- Need E2E tests before scaling to more features
- Prevent integration bugs from reaching production

---

## 3. Tool Selection

### 3.1 Comparison

| Criteria | Playwright | Cypress | Selenium |
|----------|-----------|---------|----------|
| **Multi-browser** | ✅ Chrome, Firefox, Safari, Edge | ⚠️ Primarily Chrome | ✅ All browsers |
| **Speed** | ✅ Parallel by default | ⚠️ Serial (paid for parallel) | ❌ Slow |
| **TypeScript** | ✅ First-class support | ✅ First-class support | ⚠️ Limited |
| **Auto-wait** | ✅ Built-in | ✅ Built-in | ❌ Manual waits |
| **API Testing** | ✅ Built-in HTTP client | ⚠️ Limited | ❌ None |
| **CI Integration** | ✅ Official Docker images | ✅ Good | ⚠️ Complex |
| **Learning Curve** | ⚠️ Moderate | ✅ Easy | ❌ Hard |
| **Cost** | ✅ Free & Open Source | ⚠️ Free tier limited | ✅ Open Source |
| **Network Mocking** | ✅ Built-in | ✅ Built-in | ❌ External tools |
| **Debugging** | ✅ Trace viewer, time-travel | ✅ Time-travel | ❌ Basic |

### 3.2 Decision: Playwright

**Rationale:**
1. **Aligns with Koulu's tech stack** - TypeScript-first (matches frontend)
2. **Multi-browser out of the box** - Test Safari/Firefox without extra setup
3. **Fast execution** - Parallel by default (4x faster than serial)
4. **API testing** - Can setup test data via backend API (faster than UI)
5. **CI-friendly** - Official Docker images, no licensing issues
6. **Modern architecture** - WebSocket-based (more reliable than WebDriver)

**Trade-offs accepted:**
- Steeper learning curve than Cypress (mitigated by good docs)
- Less community content (but growing rapidly)

---

## 4. E2E Test Architecture

### 4.1 Directory Structure

```
tests/e2e/
├── fixtures/
│   ├── auth.ts                    # Authentication helpers (login, logout, token)
│   ├── test-data.ts               # Test data generators (users, posts, courses)
│   └── pages/                     # Page Object Models (POM)
│       ├── base-page.ts           # Base class with common methods
│       ├── auth/
│       │   ├── login-page.ts
│       │   ├── register-page.ts
│       │   └── verify-email-page.ts
│       ├── profile/
│       │   ├── profile-view-page.ts
│       │   └── profile-edit-page.ts
│       ├── community/
│       │   ├── feed-page.ts
│       │   └── post-page.ts
│       └── classroom/
│           └── course-page.ts
│
├── specs/                         # Test specifications
│   ├── identity/
│   │   ├── registration.spec.ts   # New user registration flow
│   │   ├── login.spec.ts          # Login and logout
│   │   ├── profile-view.spec.ts   # View profile (self and others)
│   │   └── profile-edit.spec.ts   # Update profile fields
│   ├── community/
│   │   ├── feed.spec.ts           # View feed, filter categories
│   │   └── posts.spec.ts          # Create, edit, delete posts
│   └── classroom/
│       └── courses.spec.ts        # View course, complete lesson
│
├── helpers/
│   ├── api-helpers.ts             # Backend API setup/teardown
│   ├── db-helpers.ts              # Database seeding/cleanup
│   ├── assertions.ts              # Custom assertions
│   └── email-helpers.ts           # Mailhog integration for email verification
│
├── playwright.config.ts           # Playwright configuration
├── package.json                   # E2E-specific dependencies
├── tsconfig.json                  # TypeScript config for E2E tests
└── README.md                      # E2E testing guide
```

### 4.2 Page Object Model (POM)

**Pattern:** Encapsulate page interactions in classes to improve maintainability.

```typescript
// tests/e2e/fixtures/pages/profile/profile-edit-page.ts
import { Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileEditPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators (centralized, easy to update)
  private readonly displayNameInput = '[data-testid="display-name-input"]';
  private readonly bioTextarea = '[data-testid="bio-textarea"]';
  private readonly saveButton = '[data-testid="save-profile-btn"]';
  private readonly successMessage = '[data-testid="success-message"]';

  // Actions
  async goto() {
    await this.page.goto('/users/me/profile/edit');
    await this.waitForPageLoad();
  }

  async updateDisplayName(name: string) {
    await this.page.fill(this.displayNameInput, name);
  }

  async updateBio(bio: string) {
    await this.page.fill(this.bioTextarea, bio);
  }

  async clickSave() {
    await this.page.click(this.saveButton);
    await this.waitForSelector(this.successMessage);
  }

  async updateProfile(data: { displayName?: string; bio?: string }) {
    if (data.displayName) await this.updateDisplayName(data.displayName);
    if (data.bio) await this.updateBio(data.bio);
    await this.clickSave();
  }

  // Assertions
  async expectSuccessMessage() {
    await this.page.waitForSelector(this.successMessage, { state: 'visible' });
  }
}
```

**Benefits:**
- ✅ Centralized selectors (change once, updates all tests)
- ✅ Reusable actions (DRY principle)
- ✅ Readable tests (business language, not technical details)
- ✅ Easy to maintain when UI changes

---

## 5. Test Strategy

### 5.1 Three-Layer Testing Pyramid

```
           /\
          /E2E\      E2E Tests: Critical user journeys
         /____\      (~10-20 tests, slow, selective)
        /      \
       /  BDD   \    BDD Tests: API-level behavior
      /_________ \   (~50-100 scenarios, medium speed, comprehensive)
     /            \
    /  Unit Tests  \ Unit Tests: Domain logic
   /________________\ (~200-500 tests, fast, exhaustive)
```

**Coverage Philosophy:**
- **Unit tests:** Exhaustive (all edge cases, error paths, validation)
- **BDD tests:** Comprehensive (all scenarios from PRD, API behavior)
- **E2E tests:** Selective (critical happy paths only, integration validation)

**Example: Profile Update Feature**
- **Unit tests:** 10 tests (handler logic, validation, edge cases)
- **BDD tests:** 17 scenarios (API behavior, error codes, security)
- **E2E tests:** 2 tests (update via UI, see changes reflected in another page)

### 5.2 Test Scope

| Priority | User Journey | Why E2E? | Estimated Tests |
|----------|--------------|----------|-----------------|
| **P0 - Critical** | New member onboarding | Touches multiple systems (email verification, DB, frontend state, routing) | 3 tests |
| **P0 - Critical** | Login → View profile | Authentication integration, session management | 2 tests |
| **P0 - Critical** | Create post → View in feed | Core product value, real-time updates | 2 tests |
| **P1 - High** | Update profile → See changes | State synchronization across pages | 2 tests |
| **P1 - High** | Complete course lesson → Progress updates | Complex state management, nested navigation | 2 tests |
| **P2 - Medium** | Search posts → Filter results | Full-stack integration, query parsing | 1 test |
| **P2 - Medium** | Like post → Leaderboard updates | Event-driven updates, gamification | 1 test |
| **P2 - Medium** | Calendar event → Add to calendar | External integration (iCal export) | 1 test |
| **P3 - Low** | Direct message flow | Real-time WebSocket communication | 1 test |

**Total MVP:** ~15-20 E2E tests covering critical paths.

**Explicitly OUT of scope:**
- ❌ Exhaustive form validation (covered by BDD tests)
- ❌ Error handling edge cases (covered by unit tests)
- ❌ Visual regression (can add Playwright screenshots later)
- ❌ Performance testing (use dedicated tools like k6)
- ❌ Security testing (use dedicated tools like OWASP ZAP)

---

## 6. Test Data Management

### 6.1 Setup Strategy

**Option A: API Setup (Recommended for most tests)**

```typescript
// tests/e2e/fixtures/auth.ts
import { APIRequestContext } from '@playwright/test';

export async function createVerifiedUser(request: APIRequestContext) {
  // Step 1: Register via API (fast, no UI flakiness)
  const registerResponse = await request.post('/api/v1/auth/register', {
    data: {
      email: `test-${Date.now()}@example.com`,
      password: 'testpass123',
    },
  });
  const { user_id } = await registerResponse.json();

  // Step 2: Verify email via API (bypass email step)
  await request.post('/api/v1/auth/verify', {
    data: { user_id, code: 'test-verification-code' },
  });

  // Step 3: Complete profile via API
  const token = await login(request, email, password);
  await request.patch('/api/v1/users/me/profile', {
    headers: { Authorization: `Bearer ${token}` },
    data: { display_name: 'Test User', bio: 'Test bio' },
  });

  return { user_id, email, password, token };
}
```

**Benefits:**
- ✅ Fast (no browser clicks)
- ✅ Reliable (no UI state management)
- ✅ Reusable across tests

**Option B: Database Seeding (For complex scenarios)**

```typescript
// tests/e2e/helpers/db-helpers.ts
import { Pool } from 'pg';

export async function seedUser(db: Pool, userData: Partial<User>) {
  const result = await db.query(`
    INSERT INTO users (id, email, hashed_password, is_verified, created_at)
    VALUES ($1, $2, $3, $4, NOW())
    RETURNING *
  `, [userData.id, userData.email, userData.hashedPassword, true]);

  return result.rows[0];
}
```

**Benefits:**
- ✅ Even faster than API
- ✅ Fine-grained control over data
- ⚠️ Couples to DB schema (maintenance burden)

**Recommendation:** Use **API setup** for 90% of tests. Reserve DB seeding for edge cases (invalid state, legacy data).

### 6.2 Test Isolation

**Critical principle:** Each test must be independent and leave no side effects.

**Strategies:**

1. **Unique test data per run**
   ```typescript
   const testEmail = `test-${Date.now()}-${Math.random()}@example.com`;
   ```

2. **Database cleanup (afterEach hook)**
   ```typescript
   test.afterEach(async ({ request }) => {
     await request.delete(`/api/v1/test/cleanup`); // Special test endpoint
   });
   ```

3. **Separate test database**
   - Use `koulu_e2e` database (not `koulu_test` or `koulu_dev`)
   - Reset schema before test suite runs

---

## 7. Configuration

### 7.1 Playwright Config

```typescript
// tests/e2e/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs',

  // Parallel execution (4 workers = 4x faster)
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,

  // Retry failed tests (flake protection)
  retries: process.env.CI ? 2 : 0,

  // Timeout settings
  timeout: 30000,  // 30s per test
  expect: {
    timeout: 5000, // 5s for assertions
  },

  // Reporter configuration
  reporter: [
    ['html'],                              // HTML report for local debugging
    ['list'],                              // Console output
    ['junit', { outputFile: 'results.xml' }], // CI integration
  ],

  // Base URL and global settings
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',  // Debug failed tests
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // Authentication state persistence
    storageState: undefined, // Set per-test if needed
  },

  // Multi-browser testing
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
    },
  ],

  // Local dev server (auto-start frontend)
  webServer: {
    command: 'cd ../../frontend && npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 120000, // 2 minutes to start
  },
});
```

### 7.2 Environment Variables

```bash
# .env.e2e (test environment config)
BASE_URL=http://localhost:3000
API_URL=http://localhost:8000
DATABASE_URL=postgresql://koulu:koulu@localhost:5432/koulu_e2e
REDIS_URL=redis://localhost:6379/2
MAILHOG_URL=http://localhost:8025
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  e2e-tests:
    name: E2E Tests (Chromium)
    runs-on: ubuntu-latest
    timeout-minutes: 30

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: koulu_e2e
          POSTGRES_USER: koulu
          POSTGRES_PASSWORD: koulu
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      mailhog:
        image: mailhog/mailhog:latest
        ports:
          - 1025:1025
          - 8025:8025

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # ===== BACKEND SETUP =====
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run database migrations
        run: alembic upgrade head
        env:
          DATABASE_URL: postgresql://koulu:koulu@localhost:5432/koulu_e2e

      - name: Start FastAPI backend
        run: |
          uvicorn src.main:app --host 0.0.0.0 --port 8000 &
          sleep 5  # Wait for server to start
        env:
          DATABASE_URL: postgresql://koulu:koulu@localhost:5432/koulu_e2e
          REDIS_URL: redis://localhost:6379/2
          SMTP_HOST: localhost
          SMTP_PORT: 1025

      # ===== FRONTEND SETUP =====
      - name: Setup Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install frontend dependencies
        run: cd frontend && npm ci

      - name: Build frontend
        run: cd frontend && npm run build

      - name: Start frontend dev server
        run: |
          cd frontend && npm run preview -- --port 3000 &
          sleep 5  # Wait for server to start

      # ===== E2E TESTS =====
      - name: Install Playwright browsers
        run: |
          cd tests/e2e
          npm ci
          npx playwright install chromium --with-deps

      - name: Run E2E tests
        run: |
          cd tests/e2e
          npx playwright test --project=chromium
        env:
          BASE_URL: http://localhost:3000
          API_URL: http://localhost:8000

      # ===== REPORTING =====
      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: tests/e2e/playwright-report/
          retention-days: 7

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-results
          path: tests/e2e/test-results/
          retention-days: 7

      - name: Comment PR with results
        if: github.event_name == 'pull_request' && failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ E2E tests failed. [View report](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})'
            })
```

### 8.2 CI Optimization Strategies

| Strategy | Benefit | Implementation Complexity |
|----------|---------|---------------------------|
| **Parallel execution (2-4 workers)** | 2-4x faster | Low (config change) |
| **Browser caching** | 2-3x faster setup | Low (GitHub Actions cache) |
| **Dependency caching (pip, npm)** | 50% faster setup | Low (built-in Actions) |
| **Skip on docs-only PRs** | Save CI minutes | Medium (path filters) |
| **Matrix testing (Chrome, Firefox, Safari)** | Better coverage | Low (config change) |
| **Sharding (split tests across runners)** | Linear speedup | Medium (config + orchestration) |

**Recommended for MVP:**
- ✅ Run on PRs targeting `main` + manual dispatch
- ✅ Chromium only (add Firefox/Safari in matrix later)
- ✅ 2 parallel workers in CI (balance speed vs cost)
- ✅ Cache dependencies (pip, npm, Playwright browsers)
- ⏳ Add path filters (skip on `docs/**` changes)

---

## 9. Local Development

### 9.1 Setup Instructions

```bash
# One-time setup
cd tests/e2e
npm install

# Install Playwright browsers (Chromium, Firefox, WebKit)
npx playwright install

# Optional: Install system dependencies (Linux only)
npx playwright install-deps
```

### 9.2 Running Tests

```bash
# Prerequisites: Backend and frontend must be running
docker-compose up -d                    # Start postgres, redis, mailhog
cd backend && uvicorn src.main:app &    # Start FastAPI
cd frontend && npm run dev &            # Start Vite

# Run all E2E tests
cd tests/e2e
npx playwright test

# Run specific test file
npx playwright test specs/identity/profile-edit.spec.ts

# Run tests matching pattern
npx playwright test --grep "profile update"

# Run in UI mode (interactive debugging)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox

# Debug mode (step through test)
npx playwright test --debug

# Update snapshots (if using visual regression)
npx playwright test --update-snapshots
```

### 9.3 Debugging

**Playwright Inspector:**
```bash
npx playwright test --debug
# Opens interactive debugger with step-through controls
```

**Trace Viewer:**
```bash
npx playwright test --trace on
npx playwright show-trace trace.zip
# Time-travel debugger with network logs, screenshots, DOM snapshots
```

**VS Code Extension:**
- Install "Playwright Test for VSCode"
- Run/debug tests directly from editor
- Set breakpoints in test code

---

## 10. Best Practices

### 10.1 Writing Maintainable Tests

**DO:**
- ✅ Use `data-testid` attributes for stable selectors
- ✅ Use Page Object Models for reusability
- ✅ Use Playwright's auto-wait (avoid manual sleeps)
- ✅ Setup test data via API (fast, reliable)
- ✅ Test user journeys, not implementation details
- ✅ Write descriptive test names (what + expected outcome)
- ✅ Use fixtures for common setup (auth, test data)

**DON'T:**
- ❌ Use fragile selectors (CSS classes, nth-child)
- ❌ Hard-code waits (`setTimeout`, `sleep`)
- ❌ Test every edge case (covered by unit/BDD tests)
- ❌ Couple tests to each other (shared state)
- ❌ Setup test data via UI (slow, flaky)
- ❌ Ignore flaky tests (fix root cause)
- ❌ Test implementation details (internal state, private methods)

### 10.2 Flakiness Prevention

**Common causes and solutions:**

1. **Race conditions**
   ```typescript
   // ❌ BAD
   await page.click('[data-testid="submit"]');
   const text = await page.textContent('.message'); // May not be rendered yet

   // ✅ GOOD
   await page.click('[data-testid="submit"]');
   await page.waitForSelector('.message', { state: 'visible' });
   const text = await page.textContent('.message');
   ```

2. **Network timing**
   ```typescript
   // ❌ BAD
   await page.goto('/profile');
   await page.waitForTimeout(2000); // Arbitrary wait

   // ✅ GOOD
   await page.goto('/profile');
   await page.waitForLoadState('networkidle'); // Wait for all requests
   ```

3. **Test data conflicts**
   ```typescript
   // ❌ BAD
   const email = 'test@example.com'; // Reused across tests

   // ✅ GOOD
   const email = `test-${Date.now()}-${Math.random()}@example.com`;
   ```

4. **Browser state leakage**
   ```typescript
   // ✅ GOOD (Playwright does this automatically)
   test.use({ storageState: undefined }); // Clear cookies/localStorage
   ```

### 10.3 Test-Friendly Frontend

**Add `data-testid` attributes to interactive elements:**

```tsx
// ❌ BAD: Fragile selector
<button className="bg-blue-500 rounded-lg px-4 py-2 hover:bg-blue-600">
  Save Profile
</button>

// ✅ GOOD: Stable test ID
<button
  className="bg-blue-500 rounded-lg px-4 py-2 hover:bg-blue-600"
  data-testid="save-profile-btn"
>
  Save Profile
</button>
```

**Why `data-testid` over other selectors:**
- ✅ Stable across CSS changes
- ✅ Stable across text changes (i18n)
- ✅ Explicit testing contract
- ✅ Easily searchable in codebase

**Convention:**
- Format: `{element-type}-{action/purpose}`
- Examples: `login-btn`, `email-input`, `error-message`, `profile-avatar`

---

## 11. Maintenance

### 11.1 Test Ownership

| Owner | Responsibility |
|-------|----------------|
| **Feature Developer** | Write E2E test for critical flow when adding new feature |
| **QA/Test Engineer** | Review E2E tests, maintain test infrastructure |
| **DevOps Engineer** | Maintain CI/CD pipeline, optimize execution time |
| **Team Lead** | Ensure E2E tests are not overused (keep pyramid healthy) |

### 11.2 When to Add E2E Tests

**Add E2E test when:**
- ✅ Feature involves multi-page user journey
- ✅ Feature has complex frontend-backend integration
- ✅ Feature is critical to business (payment, auth, core workflow)
- ✅ Bug found in production that unit/BDD tests missed

**Skip E2E test when:**
- ❌ Feature is backend-only (use BDD tests)
- ❌ Feature is simple CRUD (BDD tests sufficient)
- ❌ Feature is internal/admin-only (lower priority)
- ❌ You're testing edge cases (use unit tests)

### 11.3 Test Maintenance Schedule

| Frequency | Task |
|-----------|------|
| **Daily** | Monitor CI failures, fix flaky tests immediately |
| **Weekly** | Review test execution time, optimize slow tests |
| **Monthly** | Review test coverage, remove redundant tests |
| **Quarterly** | Upgrade Playwright, update browser versions |

---

## 12. Success Metrics

### 12.1 Test Health

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Pass Rate** | > 95% | TBD | Flaky tests hurt confidence |
| **Execution Time** | < 10 min (all tests) | TBD | Keep CI feedback fast |
| **Flakiness Rate** | < 2% | TBD | Retries mask root cause |
| **Coverage** | 10-20 critical flows | TBD | Not exhaustive, selective |

### 12.2 Bug Detection

**Measure effectiveness:**
- How many production bugs would E2E tests have caught?
- How many integration bugs found before BDD tests?
- Are E2E tests catching issues unit/BDD tests miss?

**Goal:** E2E tests should catch **frontend-backend integration bugs**, not duplicate unit/BDD coverage.

---

## 13. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Flaky tests** | High (team loses confidence) | High | Auto-wait, stable selectors, retries, fix root cause |
| **Slow execution** | Medium (slow CI) | Medium | Parallel execution, API setup, selective coverage |
| **Maintenance burden** | Medium (test rot) | Medium | Page Object Models, `data-testid`, ownership model |
| **Over-reliance on E2E** | High (inverted pyramid) | Low | Enforce coverage limits (10-20 tests max), BDD first |
| **CI cost** | Low (minutes add up) | Medium | Run on PRs only, cache dependencies, Chromium only |

---

## 14. Implementation Roadmap

### Phase 1: Setup (Week 1)
- [x] Design document approved
- [ ] Install Playwright in `tests/e2e/`
- [ ] Configure `playwright.config.ts`
- [ ] Setup Page Object Models structure
- [ ] Create auth fixtures (login, register helpers)
- [ ] Write first E2E test (registration flow)

### Phase 2: Critical Flows (Week 2-3)
- [ ] Login/logout flow
- [ ] Profile view and edit
- [ ] Post creation and viewing in feed
- [ ] Course lesson completion
- [ ] Email verification flow (Mailhog integration)

### Phase 3: CI Integration (Week 3)
- [ ] GitHub Actions workflow
- [ ] Chromium-only execution
- [ ] Test result reporting
- [ ] Slack/PR comment notifications

### Phase 4: Stabilization (Week 4)
- [ ] Fix flaky tests
- [ ] Optimize execution time
- [ ] Add debugging guides
- [ ] Train team on E2E best practices

### Phase 5: Expansion (Future)
- [ ] Firefox and Safari matrix
- [ ] Mobile browser testing
- [ ] Visual regression testing
- [ ] Accessibility testing (axe-core integration)

---

## 15. Browser Compatibility Notes

### 15.1 Playwright's Bundled Browsers

Playwright downloads and manages its own browser binaries:
- **Chromium** ~170MB
- **Firefox** ~80MB
- **WebKit** ~60MB

**Installed location:** `~/.cache/ms-playwright/`

### 15.2 Using Local Browsers (Optional)

**Brave browser (Chromium-based):**

Playwright can use system-installed Brave, but **not recommended** for testing:

```typescript
// playwright.config.ts
use: {
  channel: 'chrome', // Uses system Chrome/Brave
  // OR
  executablePath: '/usr/bin/brave-browser',
}
```

**Why bundled browsers are better:**
- ✅ Consistent across team/CI (same version)
- ✅ Known behavior (tested by Playwright team)
- ✅ Isolated from system updates
- ⚠️ Brave-specific features not relevant for testing

**Recommendation:** Use Playwright's bundled Chromium for tests, even if you use Brave for browsing.

**What you need to install:**
1. **Playwright package:** `npm install @playwright/test` (done)
2. **Browser binaries:** `npx playwright install` (downloads Chromium/Firefox/WebKit)
3. **System dependencies (Linux only):** `npx playwright install-deps` (if missing libglib, etc.)

**On macOS/Windows:** Step 3 not needed (dependencies included).

---

## 16. Related Documents

- `CLAUDE.md` - Development rules and scope management
- `.claude/skills/implement-feature.md` - Feature implementation workflow
- `.claude/skills/e2e-test.md` - E2E test execution and debugging (NEW)
- `docs/testing/bdd-testing-guide.md` - BDD test specifications
- `tests/e2e/README.md` - E2E test setup and usage guide

---

## 17. Appendices

### Appendix A: Sample E2E Test

```typescript
// tests/e2e/specs/identity/profile-edit.spec.ts
import { test, expect } from '@playwright/test';
import { createVerifiedUser } from '../../fixtures/auth';
import { ProfileEditPage } from '../../fixtures/pages/profile/profile-edit-page';
import { ProfileViewPage } from '../../fixtures/pages/profile/profile-view-page';

test.describe('Profile Edit', () => {
  let email: string;
  let password: string;
  let token: string;

  test.beforeEach(async ({ request }) => {
    // Setup: Create verified user via API (fast)
    const user = await createVerifiedUser(request);
    email = user.email;
    password = user.password;
    token = user.token;
  });

  test('should update display name and see change on profile page', async ({ page }) => {
    // Given: User is logged in
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.click('[data-testid="login-btn"]');
    await page.waitForURL('/feed'); // Wait for redirect

    // When: User navigates to edit profile
    const editPage = new ProfileEditPage(page);
    await editPage.goto();

    // And: User updates display name
    const newName = `Updated Name ${Date.now()}`;
    await editPage.updateProfile({ displayName: newName });

    // Then: Success message is shown
    await editPage.expectSuccessMessage();

    // When: User navigates to view profile
    const viewPage = new ProfileViewPage(page);
    await viewPage.goto();

    // Then: Updated name is displayed
    const displayedName = await viewPage.getDisplayName();
    expect(displayedName).toBe(newName);
  });

  test('should show validation error for display name too short', async ({ page }) => {
    // Given: User is logged in
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', email);
    await page.fill('[data-testid="password-input"]', password);
    await page.click('[data-testid="login-btn"]');
    await page.waitForURL('/feed');

    // When: User tries to update with invalid display name
    const editPage = new ProfileEditPage(page);
    await editPage.goto();
    await editPage.updateDisplayName('AB'); // Too short (min 3 chars)
    await editPage.clickSave();

    // Then: Validation error is shown
    const errorMessage = await page.textContent('[data-testid="display-name-error"]');
    expect(errorMessage).toContain('must be at least 3 characters');

    // And: Profile is not updated (stays on edit page)
    await expect(page).toHaveURL(/\/profile\/edit$/);
  });
});
```

### Appendix B: Glossary

- **E2E Test:** Browser-based test validating full user journey
- **Page Object Model (POM):** Design pattern encapsulating page interactions
- **Flaky Test:** Test that fails intermittently without code changes
- **Playwright:** Modern browser automation framework
- **Test Isolation:** Each test runs independently without shared state
- **Auto-wait:** Playwright's automatic waiting for elements to be actionable
- **Trace Viewer:** Time-travel debugger for Playwright tests
- **Headless Mode:** Running browser without visible UI (faster)
- **Test Fixture:** Reusable setup/teardown logic for tests

---

**Document Status:** Approved for implementation
**Next Step:** Phase 1 - Setup (see Roadmap Section 14)
