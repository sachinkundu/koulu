import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { LeaderboardsPage } from '../../fixtures/pages/gamification/leaderboards-page';
import { ProfileLevelPage } from '../../fixtures/pages/gamification/profile-level-page';
import {
  cleanTestState,
  createCommunityMember,
  createCommunityAdmin,
  createPost,
  likePost,
  addComment,
  deletePostApi,
  createCourseApi,
  deleteCourseApi,
} from '../../helpers/api-helpers';
import {
  getMemberLevel,
  getUserId,
  setCourseLevelRequirement,
  getCommunityId,
} from '../../helpers/gamification-helpers';

test.describe('Gamification: Points & Levels', () => {
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

  test('Member views level definitions grid on leaderboards page', async ({ page }) => {
    const user = await createCommunityMember(`E2E Levels ${Date.now()}`);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForGrid();

    // All 9 level cards should be visible
    const cardCount = await leaderboardsPage.getLevelCardCount();
    expect(cardCount).toBe(9);

    // Level 1 card should exist with name and threshold
    const level1Card = leaderboardsPage.getLevelCard(1);
    await expect(level1Card).toBeVisible();
    await expect(level1Card).toContainText('0 points');

    // Level 9 card should exist
    const level9Card = leaderboardsPage.getLevelCard(9);
    await expect(level9Card).toBeVisible();
  });

  test('Member current level is highlighted in leaderboard grid', async ({ page }) => {
    const user = await createCommunityMember(`E2E Highlight ${Date.now()}`);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForGrid();

    // New member should be at level 1 (0 points), which should be highlighted
    const isHighlighted = await leaderboardsPage.isLevelHighlighted(1);
    expect(isHighlighted).toBe(true);

    // Level 2 should NOT be highlighted
    const isLevel2Highlighted = await leaderboardsPage.isLevelHighlighted(2);
    expect(isLevel2Highlighted).toBe(false);
  });

  test('Member views own level and points on profile page', async ({ page }) => {
    const user = await createCommunityMember(`E2E Profile ${Date.now()}`);
    const userId = await getUserId(user.accessToken);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const profilePage = new ProfileLevelPage(page);
    await profilePage.goto(userId);
    await profilePage.waitForLevelSection();

    // New member should show Level 1
    const levelName = await profilePage.getLevelName();
    expect(levelName).toContain('Level 1');

    // Should show 0 points
    const points = await profilePage.getLevelPoints();
    expect(points).toContain('0');

    // Should show points to level up (not max level)
    const progress = await profilePage.getLevelProgress();
    expect(progress).toContain('points to level up');
  });

  test('Member earns points from actions and sees level progress update', async ({ page }) => {
    // Create two members: one to create content, one to like it
    const author = await createCommunityMember(`E2E Author ${Date.now()}`);
    const authorId = await getUserId(author.accessToken);

    // Author creates a post (+2 points)
    const postTitle = `Points Test ${Date.now()}`;
    const { id: postId } = await createPost(author.accessToken, postTitle, 'Testing points');
    cleanupFns.push(() => deletePostApi(author.accessToken, postId));

    // Author adds a comment (+1 point)
    await addComment(author.accessToken, postId, 'Self-comment for points');

    // Wait briefly for event processing
    await new Promise((resolve) => setTimeout(resolve, 1_000));

    // Verify points via API first
    const level = await getMemberLevel(author.accessToken, authorId);
    expect(level.total_points).toBeGreaterThanOrEqual(2);

    // Now check the profile page shows updated points
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(author.email, author.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const profilePage = new ProfileLevelPage(page);
    await profilePage.goto(authorId);
    await profilePage.waitForLevelSection();

    // Points should be > 0
    const points = await profilePage.getLevelPoints();
    expect(points).not.toContain('0 points');
  });

  test('Locked course shows lock overlay on classroom page', async ({ page }) => {
    // Create admin to set up course with level requirement
    const admin = await createCommunityAdmin(`E2E Admin ${Date.now()}`);
    const communityId = await getCommunityId(admin.accessToken);

    // Create a course
    const courseTitle = `Locked Course ${Date.now()}`;
    const { id: courseId } = await createCourseApi(admin.accessToken, courseTitle);
    cleanupFns.push(() => deleteCourseApi(admin.accessToken, courseId));

    // Set level requirement to 5 (new member is level 1, so they can't access)
    await setCourseLevelRequirement(admin.accessToken, communityId, courseId, 5);

    // Create regular member who will be at level 1
    const member = await createCommunityMember(`E2E Locked ${Date.now()}`);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to classroom
    await page.goto('/classroom');
    await page.waitForLoadState('networkidle');

    // Course card should show lock overlay
    const courseCard = page.locator(`[data-testid="course-card-${courseId}"]`);
    await expect(courseCard).toBeVisible({ timeout: 10_000 });

    // Lock overlay should be visible with "Unlock at Level 5" text
    const lockOverlay = courseCard.locator('text=Unlock at Level 5');
    await expect(lockOverlay).toBeVisible({ timeout: 5_000 });
  });

  test('Course without level requirement is accessible to all members', async ({ page }) => {
    const admin = await createCommunityAdmin(`E2E NoLock ${Date.now()}`);

    // Create a course with NO level requirement
    const courseTitle = `Open Course ${Date.now()}`;
    const { id: courseId } = await createCourseApi(admin.accessToken, courseTitle);
    cleanupFns.push(() => deleteCourseApi(admin.accessToken, courseId));

    // Create regular member
    const member = await createCommunityMember(`E2E Open ${Date.now()}`);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    await page.goto('/classroom');
    await page.waitForLoadState('networkidle');

    // Course card should be visible without lock overlay
    const courseCard = page.locator(`[data-testid="course-card-${courseId}"]`);
    await expect(courseCard).toBeVisible({ timeout: 10_000 });

    // No lock text should be present on this card
    const lockOverlay = courseCard.locator('text=Unlock at Level');
    await expect(lockOverlay).toBeHidden();
  });
});
