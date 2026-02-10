import { test, expect } from '@playwright/test';
import { PostDetailPage } from '../../fixtures/pages/community/post-detail-page';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import {
  cleanTestState,
  createCommunityMember,
  createPost,
} from '../../helpers/api-helpers';

test.describe('Community Interactions', () => {
  test.beforeEach(async () => {
    await cleanTestState();
  });

  test('Member likes and unlikes a post', async ({ page }) => {
    const user = await createCommunityMember(`E2E Like ${Date.now()}`);
    const postTitle = `Like Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Likeable content.');

    // Login and go to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();

    // Initial like count should be 0
    const initialCount = await detailPage.getLikeCount();
    expect(initialCount).toBe('0');

    // Click like and wait for count to update
    await detailPage.clickLikeButton();
    await expect.poll(
      async () => detailPage.getLikeCount(),
      { timeout: 10_000 },
    ).toBe('1');

    // Click unlike and wait for count to go back to 0
    await detailPage.clickLikeButton();
    await expect.poll(
      async () => detailPage.getLikeCount(),
      { timeout: 10_000 },
    ).toBe('0');
  });

  test('Member adds a comment to a post', async ({ page }) => {
    const user = await createCommunityMember(`E2E Comment ${Date.now()}`);
    const postTitle = `Comment Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Commentable content.');

    // Login and go to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();
    await detailPage.waitForCommentThread();

    // Add a comment
    const commentText = `E2E comment ${Date.now()}`;
    await detailPage.addComment(commentText);

    // Verify comment appears
    const commentCount = await detailPage.getCommentCount();
    expect(commentCount).toBeGreaterThanOrEqual(1);

    const displayedComment = await detailPage.getCommentText(0);
    expect(displayedComment).toBe(commentText);
  });

  test('Member edits own post via modal', async ({ page }) => {
    const user = await createCommunityMember(`E2E Edit ${Date.now()}`);
    const postTitle = `Edit Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Original content.');

    // Login and go to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();

    // Verify edit button visible
    const hasEdit = await detailPage.hasEditButton();
    expect(hasEdit).toBe(true);

    // Edit post
    const newTitle = `Edited Title ${Date.now()}`;
    const newContent = 'Updated content via E2E test.';
    await detailPage.editPost(newTitle, newContent);

    // Wait for page to refresh with updated data
    await page.waitForTimeout(1000);

    // Verify updated content
    const title = await detailPage.getTitle();
    expect(title).toBe(newTitle);

    const content = await detailPage.getContent();
    expect(content).toBe(newContent);
  });
});
