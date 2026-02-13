import { test, expect } from '@playwright/test';
import { PostDetailPage } from '../../fixtures/pages/community/post-detail-page';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import {
  cleanTestState,
  createCommunityMember,
  createPost,
  addComment,
  deletePostApi,
} from '../../helpers/api-helpers';

test.describe('Comment Interactions', () => {
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

  test('Member replies to a comment', async ({ page }) => {
    const user = await createCommunityMember(`E2E Reply ${Date.now()}`);
    const postTitle = `Reply Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Post with comments.');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Add a top-level comment via API
    const { comment_id: commentId } = await addComment(
      user.accessToken,
      postId,
      'Original comment for reply test',
    );

    // Login and navigate to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();
    await detailPage.waitForCommentThread();

    // Verify original comment is visible
    const initialCount = await detailPage.getCommentCount();
    expect(initialCount).toBeGreaterThanOrEqual(1);

    // Reply to the comment
    const replyText = `E2E reply ${Date.now()}`;
    await detailPage.replyToComment(commentId, replyText);

    // Verify reply appears (comment count increased)
    await expect.poll(
      async () => detailPage.getCommentCount(),
      { timeout: 10_000 },
    ).toBeGreaterThan(initialCount);

    // Verify reply text is visible on the page
    const pageText = await page.locator('[data-testid="comments-list"]').textContent();
    expect(pageText).toContain(replyText);
  });

  test('Member edits their own comment', async ({ page }) => {
    const user = await createCommunityMember(`E2E EditComment ${Date.now()}`);
    const postTitle = `Edit Comment Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Post for comment edit.');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Add a comment via API
    const originalContent = 'Original comment content';
    const { comment_id: commentId } = await addComment(
      user.accessToken,
      postId,
      originalContent,
    );

    // Login and navigate to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();
    await detailPage.waitForCommentThread();

    // Verify original content is visible
    const commentText = await detailPage.getCommentText(0);
    expect(commentText).toBe(originalContent);

    // Edit the comment
    const updatedContent = `Edited comment ${Date.now()}`;
    await detailPage.editComment(commentId, updatedContent);

    // Verify edited content appears
    await expect.poll(
      async () => detailPage.getCommentText(0),
      { timeout: 10_000 },
    ).toBe(updatedContent);

    // Verify "· edited" indicator shows
    const commentEl = page.locator(`[data-testid="comment-${commentId}"]`).first();
    await expect(commentEl.locator('text=· edited')).toBeVisible({ timeout: 5_000 });
  });

  test('Member deletes their own comment', async ({ page }) => {
    const user = await createCommunityMember(`E2E DeleteComment ${Date.now()}`);
    const postTitle = `Delete Comment Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Post for comment delete.');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Add a comment via API
    const { comment_id: commentId } = await addComment(
      user.accessToken,
      postId,
      'Comment to be deleted',
    );

    // Login and navigate to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();
    await detailPage.waitForCommentThread();

    // Verify comment exists
    const initialCount = await detailPage.getCommentCount();
    expect(initialCount).toBeGreaterThanOrEqual(1);

    // Delete the comment
    await detailPage.deleteComment(commentId);

    // Verify comment is removed (count decreased or comment shows [deleted])
    await expect.poll(
      async () => {
        const el = page.locator(`[data-testid="comment-${commentId}"]`).first();
        const visible = await el.isVisible();
        if (!visible) return 'removed';
        const text = await el.textContent();
        if (text?.includes('[deleted]')) return 'soft-deleted';
        return 'present';
      },
      { timeout: 10_000 },
    ).not.toBe('present');
  });

  test('Member likes a comment', async ({ page }) => {
    const user = await createCommunityMember(`E2E CommentLike ${Date.now()}`);
    const postTitle = `Comment Like Test ${Date.now()}`;
    const { id: postId } = await createPost(user.accessToken, postTitle, 'Post for comment like.');
    cleanupFns.push(() => deletePostApi(user.accessToken, postId));

    // Add a comment via API
    const { comment_id: commentId } = await addComment(
      user.accessToken,
      postId,
      'Likeable comment',
    );

    // Login and navigate to post detail
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const detailPage = new PostDetailPage(page);
    await detailPage.goto(postId);
    await detailPage.waitForDetail();
    await detailPage.waitForCommentThread();

    // Initial like count should be "0" (no likes yet)
    const initialText = await detailPage.getCommentLikeText(commentId);
    expect(initialText).toBe('0');

    // Like the comment
    await detailPage.clickCommentLikeButton(commentId);

    // Verify like count changes to "1"
    await expect.poll(
      async () => detailPage.getCommentLikeText(commentId),
      { timeout: 10_000 },
    ).toBe('1');
  });
});
