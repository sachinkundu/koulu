---
name: write-e2e-tests
description: Design and write E2E tests for implemented features with UI
user_invocable: true
---

# Write E2E Tests Skill

## Purpose

Analyze implemented features and generate E2E test scenarios + Playwright test code for critical user journeys.

**Key Principle:** E2E tests validate full user experience through browser automation. They test UI → API → DB → UI integration, focusing on high-level workflows (not implementation details).

---

## Usage

```bash
# Analyze feature and write E2E tests
/write-e2e-tests community-feed

# Write tests for specific workflow
/write-e2e-tests identity --workflow=profile-update

# Generate test plan only (no code)
/write-e2e-tests classroom --plan-only
```

---

## Prerequisites

**This skill requires BOTH backend AND frontend to be implemented.**

**Will exit with warning if:**
- ❌ No frontend components found for feature
- ❌ No routes/pages found for feature
- ❌ Backend endpoints exist but no UI to test

**Rationale:** E2E tests are UI-only. API testing belongs in BDD/integration tests.

---

## Workflow

### Step 1: Discovery (Analyze Implementation)

**Backend Check:**
1. Scan `src/{module}/interface/api/` for controllers
2. Read `tests/features/{module}/*.feature` for passing BDD scenarios
3. Identify available API endpoints

**Frontend Check:**
1. Scan `frontend/src/features/{module}/` for components
2. Check `frontend/src/pages/` for routes
3. Verify UI components exist for user workflows

**Specification Check:**
1. Read `docs/features/{module}/UI_SPEC.md` for component designs
2. Read `docs/features/{module}/*-prd.md` for user stories
3. Identify critical user paths from specs

**Decision Point:**

```
IF frontend_exists == FALSE:
  → Warn user: "No UI implementation found"
  → Show what's missing (components, pages, routes)
  → Exit (DO NOT write tests)

IF frontend_exists == TRUE:
  → Proceed to Step 2
```

---

### Step 2: Design Test Scenarios (High-Level)

**Principles:**

1. **Test user journeys, not implementation:**
   - ✅ GOOD: "Member creates post and sees it in feed"
   - ❌ BAD: "Member clicks 'Write something', modal opens, fills title input, clicks category dropdown, selects General, types content..."

2. **Focus on critical paths:**
   - Happy paths (primary user goals)
   - Multi-page workflows (login → action → verification)
   - State synchronization (update → see change elsewhere)
   - Skip edge cases (covered by BDD tests)

3. **Prioritize:**
   - **P0 (Critical):** Core workflows, authentication (MUST test)
   - **P1 (High):** Data updates, state management (SHOULD test)
   - **P2 (Medium):** Filtering, search, secondary features (NICE to test)

**Output: `E2E_TEST_PLAN.md`**

```markdown
# {Feature} E2E Tests

## Critical Paths (P0) - MUST IMPLEMENT
- [ ] User creates post and sees it in feed
- [ ] User comments on post and sees comment appear
- [ ] User likes post and sees like count increment

## Secondary Paths (P1) - SHOULD IMPLEMENT
- [ ] User edits their own post
- [ ] User deletes their own post
- [ ] Admin locks post, member cannot comment

## Optional Paths (P2) - NICE TO HAVE
- [ ] Feed loads next page on scroll
- [ ] Post with image displays correctly
- [ ] Filter feed by category

## Out of Scope (Covered by BDD)
- ❌ Post validation (title length, content required)
- ❌ Permission checks (non-author cannot edit)
- ❌ Error messages (network failures, 404s)
```

---

### Step 3: Generate Playwright Test Code

**File Structure:**

```
tests/e2e/
├── fixtures/pages/{module}/
│   └── {feature}-page.ts         # Page Object Model
├── specs/{module}/
│   └── {feature}.spec.ts         # Test scenarios
└── helpers/
    └── {module}-helpers.ts       # Test data factories (if needed)
```

**3.1: Create Page Object Model**

```typescript
// tests/e2e/fixtures/pages/community/feed-page.ts
import { Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class FeedPage extends BasePage {
  constructor(page: Page) {
    super(page);
  }

  // Locators (using data-testid)
  private readonly createPostButton = '[data-testid="create-post-btn"]';
  private readonly postTitleInput = '[data-testid="post-title-input"]';
  private readonly postContentInput = '[data-testid="post-content-textarea"]';
  private readonly submitPostButton = '[data-testid="submit-post-btn"]';

  // Actions (high-level, business-focused)
  async goto() {
    await this.page.goto('/community/feed');
    await this.waitForPageLoad();
  }

  async createPost(title: string, content: string) {
    await this.page.click(this.createPostButton);
    await this.page.fill(this.postTitleInput, title);
    await this.page.fill(this.postContentInput, content);
    await this.page.click(this.submitPostButton);
    await this.page.waitForSelector('[data-testid="post-card"]', { state: 'visible' });
  }

  async getPostByTitle(title: string) {
    return this.page.locator(`[data-testid="post-card"]:has-text("${title}")`);
  }

  async likePost(postTitle: string) {
    const post = await this.getPostByTitle(postTitle);
    await post.locator('[data-testid="like-btn"]').click();
  }

  async getLikeCount(postTitle: string): Promise<number> {
    const post = await this.getPostByTitle(postTitle);
    const text = await post.locator('[data-testid="like-count"]').textContent();
    return parseInt(text || '0', 10);
  }
}
```

**3.2: Write Test Specification**

```typescript
// tests/e2e/specs/community/feed.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { FeedPage } from '../../fixtures/pages/community/feed-page';
import { createUserWithProfile } from '../../helpers/api-helpers';

test.describe('Community Feed', () => {
  test('Member creates post and sees it in feed', async ({ page }) => {
    // Setup: Create authenticated user via API (fast)
    const user = await createUserWithProfile(`E2E Test ${Date.now()}`);

    // Given: User is logged in
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL('**/', { timeout: 10_000 });

    // When: User creates a post
    const feedPage = new FeedPage(page);
    await feedPage.goto();
    const postTitle = `Test Post ${Date.now()}`;
    await feedPage.createPost(postTitle, 'This is test content');

    // Then: Post appears in feed
    const post = await feedPage.getPostByTitle(postTitle);
    await expect(post).toBeVisible();
  });

  test('User likes post and sees like count increment', async ({ page }) => {
    const user = await createUserWithProfile(`E2E Test ${Date.now()}`);

    // Login and navigate to feed
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);

    const feedPage = new FeedPage(page);
    await feedPage.goto();

    // Create a post
    const postTitle = `Likeable Post ${Date.now()}`;
    await feedPage.createPost(postTitle, 'Please like this!');

    // Get initial like count
    const initialLikes = await feedPage.getLikeCount(postTitle);

    // Like the post
    await feedPage.likePost(postTitle);

    // Verify like count incremented
    const newLikes = await feedPage.getLikeCount(postTitle);
    expect(newLikes).toBe(initialLikes + 1);
  });
});
```

**Key Patterns:**

1. **Use `data-testid` attributes** (stable, explicit testing contract)
2. **Setup via API** (fast, avoids UI flakiness)
3. **Unique test data** (timestamp prevents conflicts)
4. **Page Object Model** (reusable, maintainable)
5. **Explicit waits** (no `waitForTimeout`, use state-based waits)
6. **High-level actions** (test "what" users do, not "how")

---

### Step 4: Add `data-testid` Recommendations to UI_SPEC.md

**If UI_SPEC.md exists but components aren't fully implemented:**

Add a "Test IDs" section to component specs:

```markdown
### FeedPostCard Component

**Test IDs:**
```tsx
<article data-testid="post-card">
  <h2 data-testid="post-title">{post.title}</h2>
  <p data-testid="post-content">{post.content}</p>
  <button data-testid="like-btn">
    <span data-testid="like-count">{likeCount}</span>
  </button>
  <button data-testid="comment-btn">
    <span data-testid="comment-count">{commentCount}</span>
  </button>
</article>
```
```

**Naming Convention:**
- Format: `{element-type}-{action/purpose}`
- Examples: `login-btn`, `email-input`, `error-message`, `profile-avatar`, `post-card`

---

## Outputs

### 1. Test Plan Document

**Location:** `docs/testing/e2e/{feature}-test-plan.md`

**Contents:**
- Critical user journeys to test (P0)
- Secondary paths (P1)
- Optional scenarios (P2)
- Explicitly out of scope (covered by BDD)

### 2. Page Object Models

**Location:** `tests/e2e/fixtures/pages/{module}/{feature}-page.ts`

**Contents:**
- Locators (using `data-testid`)
- High-level actions (user-centric methods)
- Getters (retrieve page state for assertions)

### 3. Test Specifications

**Location:** `tests/e2e/specs/{module}/{feature}.spec.ts`

**Contents:**
- Test scenarios (P0 critical paths)
- Setup via API helpers
- Assertions on user-visible outcomes

### 4. Test Data Helpers (Optional)

**Location:** `tests/e2e/helpers/{module}-helpers.ts`

**Contents:**
- Factory functions for test data
- API setup helpers (if not in main api-helpers.ts)

---

## Error Handling: Frontend Not Found

**If frontend doesn't exist, display:**

```
⚠️  Cannot write E2E tests: Frontend not implemented

📋 Analysis:
✅ Backend implemented:
   - 39 BDD scenarios passing
   - API endpoints: POST /posts, GET /posts/:id, PATCH /posts/:id, DELETE /posts/:id
   - Handlers: CreatePost, UpdatePost, DeletePost, GetPost

❌ Frontend missing:
   - No components found in frontend/src/features/community/
   - No routes found in frontend/src/pages/ for community
   - UI_SPEC.md exists but no React implementation

🛠️  Next Steps:
1. Implement frontend components (use /implement-feature with Phase 4+)
2. Add routes to frontend router
3. Re-run: /write-e2e-tests community-feed

💡 Alternative:
   - API integration is tested by BDD scenarios
   - E2E tests only needed for UI workflows
   - Focus on implementing frontend first
```

**Then EXIT (do not write skeletal tests or API-only tests).**

---

## Best Practices

### ✅ DO

- **Keep tests high-level** (test user goals, not UI mechanics)
- **Use stable selectors** (`data-testid`, not CSS classes)
- **Setup via API** (fast, reliable, no UI dependencies)
- **Use unique test data** (timestamp prevents conflicts)
- **Test critical paths only** (10-20 tests max per feature)
- **Follow Page Object Model** (maintainability)
- **Add explicit waits** (state-based, not time-based)

### ❌ DON'T

- **Don't test every edge case** (use BDD tests for validation)
- **Don't duplicate BDD coverage** (E2E is for UI integration)
- **Don't test implementation details** (internal state, props)
- **Don't write tests without frontend** (E2E = UI tests)
- **Don't use fragile selectors** (nth-child, CSS classes)
- **Don't hard-code waits** (`waitForTimeout(2000)`)
- **Don't couple tests** (each test must be independent)

---

## Test Quality Checklist

Before marking E2E tests complete, verify:

- [ ] Frontend exists (components, routes, pages)
- [ ] Test plan covers critical paths (P0)
- [ ] Page objects use `data-testid` selectors
- [ ] Tests use API setup (no UI setup)
- [ ] Tests use unique data (timestamp)
- [ ] No hard-coded waits (`waitForTimeout`)
- [ ] Tests are high-level (user journeys, not clicks)
- [ ] Tests run and pass locally
- [ ] Tests are stable (pass 3/3 times minimum)
- [ ] `data-testid` recommendations added to UI_SPEC.md (if applicable)

---

## Common Patterns

### Pattern 1: Login + Action Workflow

```typescript
test('User performs action after login', async ({ page }) => {
  // Setup
  const user = await createUserWithProfile(`E2E ${Date.now()}`);

  // Login
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login(user.email, user.password);
  await page.waitForURL('**/', { timeout: 10_000 });

  // Navigate to feature
  const featurePage = new FeaturePage(page);
  await featurePage.goto();

  // Perform action
  await featurePage.doSomething();

  // Verify outcome
  await expect(featurePage.getResult()).toBeVisible();
});
```

### Pattern 2: Multi-Page Workflow

```typescript
test('User updates data and sees change on another page', async ({ page }) => {
  const user = await createUserWithProfile(`E2E ${Date.now()}`);

  // Login
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login(user.email, user.password);

  // Page 1: Update data
  const editPage = new EditPage(page);
  await editPage.goto();
  await editPage.updateField('New Value');

  // Page 2: Verify change
  const viewPage = new ViewPage(page);
  await viewPage.goto();
  const value = await viewPage.getFieldValue();
  expect(value).toBe('New Value');
});
```

### Pattern 3: Optimistic Update

```typescript
test('User likes post and sees immediate update', async ({ page }) => {
  const user = await createUserWithProfile(`E2E ${Date.now()}`);
  await loginAndNavigate(page, user);

  const feedPage = new FeedPage(page);
  const initialLikes = await feedPage.getLikeCount(postTitle);

  // Like (optimistic update)
  await feedPage.likePost(postTitle);

  // Immediate check (optimistic)
  const newLikes = await feedPage.getLikeCount(postTitle);
  expect(newLikes).toBe(initialLikes + 1);

  // Refresh to verify persisted
  await page.reload();
  await feedPage.waitForPageLoad();
  const persistedLikes = await feedPage.getLikeCount(postTitle);
  expect(persistedLikes).toBe(initialLikes + 1);
});
```

---

## Limitations

**This skill does NOT:**
- ❌ Implement frontend components (use `/implement-feature`)
- ❌ Write BDD tests (use `/bdd` or BDD skill)
- ❌ Test backend APIs without UI (use BDD tests)
- ❌ Write tests for missing features (warns and exits)
- ❌ Test every edge case (focuses on critical paths)

**This skill DOES:**
- ✅ Analyze if frontend exists
- ✅ Generate E2E test plan (critical paths)
- ✅ Write Page Object Models
- ✅ Write Playwright test specs
- ✅ Add `data-testid` recommendations to UI_SPEC.md
- ✅ Warn user if frontend is missing

---

## Success Metrics

**Good E2E test suite:**
- ✅ 5-15 tests covering critical user journeys
- ✅ High-level (tests goals, not mechanics)
- ✅ Stable (> 95% pass rate)
- ✅ Fast (< 5 minutes total execution)
- ✅ Easy to maintain (Page Object Model)

**Bad E2E test suite:**
- ❌ > 30 tests (over-testing)
- ❌ Low-level (testing every click)
- ❌ Flaky (< 80% pass rate)
- ❌ Slow (> 15 minutes)
- ❌ Hard to maintain (no POMs, fragile selectors)

---

## Integration with Workflow

```
1. /write-feature-spec → PRD + BDD specs
2. /implement-feature → Backend + Frontend (Phases 1-4)
3. /write-e2e-tests → E2E test plan + Playwright tests  ← THIS SKILL
4. /e2e-test → Run/debug the E2E tests (existing skill)
```

---

## Related Documents

- `docs/testing/e2e-testing-design.md` - E2E testing strategy
- `.claude/skills/e2e-test.md` - Run and debug E2E tests
- `.claude/skills/implement-feature.md` - Feature implementation workflow
- `tests/e2e/README.md` - E2E setup guide

---

## Notes

- E2E tests require **both** backend AND frontend
- Focus on **critical paths** (not exhaustive coverage)
- **Warn and exit** if frontend doesn't exist (don't write placeholder tests)
- E2E tests are **UI-only** (no API-level tests)
- Keep test count **low** (5-15 tests per feature)
- **High-level** tests (user journeys, not implementation)
