import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { SearchPage } from '../../fixtures/pages/search/search-page';
import {
  cleanTestState,
  createCommunityMember,
  createPost,
  deletePostApi,
} from '../../helpers/api-helpers';

test.describe('Community Search', () => {
  const cleanupFns: Array<() => Promise<void>> = [];

  test.beforeEach(async () => {
    await cleanTestState();
  });

  test.afterEach(async () => {
    for (const fn of cleanupFns.reverse()) {
      await fn().catch(() => {});
    }
    cleanupFns.length = 0;
  });

  test('User searches for member by name and sees results', async ({ page }) => {
    const uniqueName = `Findable Member ${Date.now()}`;
    const user = await createCommunityMember(uniqueName);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Search from header
    const searchPage = new SearchPage(page);
    await searchPage.searchFromHeader('Findable Member');

    // Verify results
    await searchPage.waitForResults();
    const card = searchPage.getMemberCardByName(uniqueName);
    await expect(card).toBeVisible();
  });

  test('User searches for post by title and sees results', async ({ page }) => {
    const user = await createCommunityMember(`E2E Searcher ${Date.now()}`);

    // Create a searchable post via API
    const postTitle = `Searchable Post ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Content for search test');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to search results for posts
    const searchPage = new SearchPage(page);
    await searchPage.goto('Searchable Post', 'posts');

    // Verify post result
    await searchPage.waitForResults();
    const card = searchPage.getPostCardByTitle(postTitle);
    await expect(card).toBeVisible();
  });

  test('User switches between Members and Posts tabs', async ({ page }) => {
    const user = await createCommunityMember(`E2E Tab ${Date.now()}`);

    // Create a post so both tabs have content
    const postTitle = `Tab Test Post ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Tab switching test');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Search for the user's name (should have member results)
    const searchPage = new SearchPage(page);
    await searchPage.goto('Tab', 'members');
    await searchPage.waitForResults();

    // Verify Members tab shows count
    const membersTabText = await searchPage.getTabText('members');
    expect(membersTabText).toMatch(/Members\s+\d+/);

    // Switch to Posts tab
    await searchPage.switchToPostsTab();
    await page.waitForURL(/t=posts/, { timeout: 5_000 });

    // Verify Posts tab shows count
    const postsTabText = await searchPage.getTabText('posts');
    expect(postsTabText).toMatch(/Posts\s+\d+/);
  });

  test('User clicks member card and navigates to profile', async ({ page }) => {
    const memberName = `Clickable Member ${Date.now()}`;
    const user = await createCommunityMember(memberName);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Search for the member
    const searchPage = new SearchPage(page);
    await searchPage.goto('Clickable Member', 'members');
    await searchPage.waitForResults();

    // Click the member card
    await searchPage.clickMemberCard(memberName);

    // Verify navigation to profile
    await page.waitForURL(/\/profile\//, { timeout: 10_000 });
  });

  test('User clicks post card and navigates to post detail', async ({ page }) => {
    const user = await createCommunityMember(`E2E PostClick ${Date.now()}`);

    const postTitle = `Clickable Post ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Click me to navigate');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Search for the post
    const searchPage = new SearchPage(page);
    await searchPage.goto('Clickable Post', 'posts');
    await searchPage.waitForResults();

    // Click the post card
    await searchPage.clickPostCard(postTitle);

    // Verify navigation to post detail
    await page.waitForURL(/\/community\/posts\//, { timeout: 10_000 });
  });

  test('Search with no results shows empty state', async ({ page }) => {
    const user = await createCommunityMember(`E2E NoResults ${Date.now()}`);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Search for something that won't exist
    const searchPage = new SearchPage(page);
    await searchPage.goto('zzzznonexistent99999', 'members');

    // Verify no-results state
    await searchPage.waitForNoResults();
    const noResultsEl = page.locator('[data-testid="search-no-results"]');
    await expect(noResultsEl).toContainText('No members found');
  });

  test('Short query shows guidance message', async ({ page }) => {
    const user = await createCommunityMember(`E2E Short ${Date.now()}`);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to search with short query
    const searchPage = new SearchPage(page);
    await searchPage.goto('ab', 'members');

    // Verify guidance message
    await searchPage.waitForEmptyState();
    const emptyState = page.locator('[data-testid="search-empty-state"]');
    await expect(emptyState).toContainText('at least 3 characters');
  });
});
