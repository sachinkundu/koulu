import { test, expect } from '@playwright/test';
import { FeedPage } from '../../fixtures/pages/community/feed-page';
import { PostDetailPage } from '../../fixtures/pages/community/post-detail-page';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import {
  cleanTestState,
  createCommunityMember,
  createPost,
  getCategories,
} from '../../helpers/api-helpers';

test.describe('Community Feed', () => {
  test.beforeEach(async () => {
    await cleanTestState();
  });
  test('Member creates post and sees it in feed', async ({ page }) => {
    const displayName = `E2E Poster ${Date.now()}`;
    const user = await createCommunityMember(displayName);

    // Step 1: Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 2: Create post via modal
    const feedPage = new FeedPage(page);
    const postTitle = `Test Post ${Date.now()}`;
    const postContent = 'This is a test post created via E2E test.';
    await feedPage.createPost(postTitle, postContent);

    // Step 3: After creation, navigates to the post detail page
    await page.waitForURL(/\/community\/posts\//, { timeout: 10_000 });

    // Step 4: Go back to feed and verify post appears
    await feedPage.goto();
    await feedPage.waitForFeed();
    const postCard = await feedPage.getPostCardByTitle(postTitle);
    await expect(postCard).toBeVisible();
  });

  test('Member views post detail in modal', async ({ page }) => {
    const user = await createCommunityMember(`E2E Modal ${Date.now()}`);

    // Create a post via API for fast setup
    const postTitle = `Modal Test ${Date.now()}`;
    const postContent = 'Content for modal viewing test.';
    await createPost(user.accessToken, postTitle, postContent);

    // Login and navigate to feed
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Wait for feed to load with the post
    const feedPage = new FeedPage(page);
    await feedPage.waitForFeed();

    // Click the post card to open modal
    await feedPage.clickPostCard(postTitle);

    // Verify modal opened with correct content
    const detailPage = new PostDetailPage(page);
    await detailPage.waitForModal();

    const modalTitle = await detailPage.getModalTitle();
    expect(modalTitle).toBe(postTitle);

    const modalContent = await detailPage.getModalContent();
    expect(modalContent).toBe(postContent);

    // Close modal and verify we're back on feed
    await detailPage.closeModal();
    await page.waitForSelector('[data-testid="post-detail-modal"]', {
      state: 'hidden',
      timeout: 5_000,
    });
  });

  test('Member views post detail page via direct URL', async ({ page }) => {
    const user = await createCommunityMember(`E2E Direct ${Date.now()}`);

    // Create a post via API
    const postTitle = `Direct URL Test ${Date.now()}`;
    const postContent = 'Content for direct URL viewing test.';
    const { id: postId } = await createPost(
      user.accessToken,
      postTitle,
      postContent,
    );

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate directly to post detail page
    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();

    // Verify post content
    const title = await detailPage.getTitle();
    expect(title).toBe(postTitle);

    const content = await detailPage.getContent();
    expect(content).toBe(postContent);

    // Click back — goes to /community which redirects to /
    await detailPage.goBackToFeed();
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });
  });

  test('Member filters feed by category', async ({ page }) => {
    const user = await createCommunityMember(`E2E Filter ${Date.now()}`);

    // Get categories to use for posts
    const categories = await getCategories(user.accessToken);
    expect(categories.length).toBeGreaterThanOrEqual(2);

    const cat1 = categories[0];
    const cat2 = categories[1];

    // Create posts in different categories
    const titleA = `Cat1 Post ${Date.now()}`;
    const titleB = `Cat2 Post ${Date.now()}`;
    await createPost(user.accessToken, titleA, 'Content in category 1', cat1.id);
    await createPost(user.accessToken, titleB, 'Content in category 2', cat2.id);

    // Login and go to feed
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const feedPage = new FeedPage(page);
    await feedPage.waitForFeed();
    await feedPage.waitForCategoryTabs();

    // Filter by category 1 — only its post should be visible
    await feedPage.selectCategory(cat1.slug);

    // Wait for the filtered post to be visible and the other to disappear
    const cardA = await feedPage.getPostCardByTitle(titleA);
    await expect(cardA).toBeVisible({ timeout: 10_000 });

    const cardB = await feedPage.getPostCardByTitle(titleB);
    await expect(cardB).toBeHidden({ timeout: 10_000 });

    // Click "All" — both posts should be visible
    await feedPage.selectAllCategories();

    const cardA2 = await feedPage.getPostCardByTitle(titleA);
    await expect(cardA2).toBeVisible({ timeout: 10_000 });

    const cardB2 = await feedPage.getPostCardByTitle(titleB);
    await expect(cardB2).toBeVisible({ timeout: 10_000 });
  });

  test('Member deletes own post', async ({ page }) => {
    const user = await createCommunityMember(`E2E Delete ${Date.now()}`);

    // Create a post via API
    const postTitle = `Delete Me ${Date.now()}`;
    const { id: postId } = await createPost(
      user.accessToken,
      postTitle,
      'This post will be deleted.',
    );

    // Login and go to feed
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to the post detail page
    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();

    // Verify delete button is visible (user owns the post)
    const hasDelete = await detailPage.hasDeleteButton();
    expect(hasDelete).toBe(true);

    // Delete the post (accepts confirm dialog)
    await detailPage.deletePost();

    // Should be redirected to feed
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Verify post is no longer visible in feed
    const feedPage = new FeedPage(page);
    const deletedCard = await feedPage.getPostCardByTitle(postTitle);
    await expect(deletedCard).toBeHidden({ timeout: 10_000 });
  });
});
