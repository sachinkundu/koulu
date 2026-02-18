import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { LeaderboardsPage } from '../../fixtures/pages/gamification/leaderboards-page';
import { FeedPage } from '../../fixtures/pages/community/feed-page';
import {
  cleanTestState,
  createCommunityMember,
} from '../../helpers/api-helpers';
import {
  getUserId,
  getCommunityId,
  awardPointsViaDb,
} from '../../helpers/gamification-helpers';

test.describe('Gamification: Leaderboards', () => {
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

  test('Member views leaderboard page with three ranking panels', async ({ page }) => {
    // Create a member who earns points so panels have data
    const member = await createCommunityMember(`E2E LB ${Date.now()}`);
    const userId = await getUserId(member.accessToken);
    const communityId = await getCommunityId(member.accessToken);

    // Award points so member appears in rankings
    awardPointsViaDb(userId, communityId, 10, 'e2e_test');

    // Login and navigate
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForPanels();

    // All three panels should be visible
    await expect(leaderboardsPage.getPanel('7day')).toBeVisible();
    await expect(leaderboardsPage.getPanel('30day')).toBeVisible();
    await expect(leaderboardsPage.getPanel('alltime')).toBeVisible();

    // All-time panel should have at least one row (the member we created)
    const allTimeRows = leaderboardsPage.getPanelRows('alltime');
    await expect(allTimeRows.first()).toBeVisible({ timeout: 5_000 });

    // Panel titles should be correct
    await expect(leaderboardsPage.getPanel('7day')).toContainText('7-day');
    await expect(leaderboardsPage.getPanel('30day')).toContainText('30-day');
    await expect(leaderboardsPage.getPanel('alltime')).toContainText('All-time');
  });

  test('Member with points appears in leaderboard rankings', async ({ page }) => {
    const displayName = `E2E Ranked ${Date.now()}`;
    const member = await createCommunityMember(displayName);
    const userId = await getUserId(member.accessToken);
    const communityId = await getCommunityId(member.accessToken);

    // Award enough points to appear on the board
    awardPointsViaDb(userId, communityId, 25, 'e2e_test');

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForPanels();

    // Member should appear somewhere in all-time panel
    const panel = leaderboardsPage.getPanel('alltime');
    await expect(panel).toContainText(displayName, { timeout: 5_000 });
    await expect(panel).toContainText('25');
  });

  test('Member sees own profile card with level info', async ({ page }) => {
    const member = await createCommunityMember(`E2E Profile ${Date.now()}`);

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForProfileCard();

    const card = leaderboardsPage.getProfileCard();
    await expect(card).toBeVisible();
    await expect(card).toContainText('E2E Profile');
    await expect(card).toContainText('Level 1');
  });

  test('Member sees "Your rank" section when outside top 10', async ({ page }) => {
    const members: Array<{ accessToken: string; email: string; password: string }> = [];

    // Create 11 members with decreasing points so the last one is outside top 10
    for (let i = 0; i < 11; i++) {
      const m = await createCommunityMember(`E2E Rank${i} ${Date.now()}`);
      members.push(m);
    }

    // Get community ID from first member
    const communityId = await getCommunityId(members[0].accessToken);

    // Award points: first 10 get high points, last one gets 1 point
    for (let i = 0; i < 10; i++) {
      const uid = await getUserId(members[i].accessToken);
      awardPointsViaDb(uid, communityId, 100 - i * 5, 'e2e_test');
    }
    const lastUserId = await getUserId(members[10].accessToken);
    awardPointsViaDb(lastUserId, communityId, 1, 'e2e_test');

    // Login as the last member (outside top 10)
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(members[10].email, members[10].password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForPanels();

    // "Your rank" section should be visible in all-time panel
    const yourRank = leaderboardsPage.getYourRankSection('alltime');
    await expect(yourRank).toBeVisible({ timeout: 10_000 });
    await expect(yourRank).toContainText('Your rank');
  });

  test('Sidebar widget shows leaderboard on community feed page', async ({ page }) => {
    const member = await createCommunityMember(`E2E Widget ${Date.now()}`);
    const userId = await getUserId(member.accessToken);
    const communityId = await getCommunityId(member.accessToken);

    // Award points so widget has data
    awardPointsViaDb(userId, communityId, 15, 'e2e_test');

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Feed page should show sidebar widget
    const feedPage = new FeedPage(page);
    await feedPage.goto();

    const widget = page.locator('[data-testid="leaderboard-sidebar-widget"]');
    await expect(widget).toBeVisible({ timeout: 15_000 });

    // Widget should show the "Leaderboard (30-day)" title
    await expect(widget).toContainText('Leaderboard (30-day)');

    // Widget should show the "See all leaderboards" link
    const seeAllLink = page.locator('[data-testid="see-all-leaderboards-link"]');
    await expect(seeAllLink).toBeVisible();
  });

  test('"See all leaderboards" link navigates to full page', async ({ page }) => {
    const member = await createCommunityMember(`E2E Nav ${Date.now()}`);
    const userId = await getUserId(member.accessToken);
    const communityId = await getCommunityId(member.accessToken);
    awardPointsViaDb(userId, communityId, 10, 'e2e_test');

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to feed and click the "See all leaderboards" link
    const feedPage = new FeedPage(page);
    await feedPage.goto();

    const seeAllLink = page.locator('[data-testid="see-all-leaderboards-link"]');
    await expect(seeAllLink).toBeVisible({ timeout: 15_000 });
    await seeAllLink.click();

    // Should navigate to /leaderboards
    await page.waitForURL('**/leaderboards', { timeout: 10_000 });

    // Full leaderboard page should be visible
    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.waitForPanels();
    await expect(leaderboardsPage.getPanel('7day')).toBeVisible();
  });

  test('Points display with + prefix for timed panels', async ({ page }) => {
    const displayName = `E2E Prefix ${Date.now()}`;
    const member = await createCommunityMember(displayName);
    const userId = await getUserId(member.accessToken);
    const communityId = await getCommunityId(member.accessToken);
    awardPointsViaDb(userId, communityId, 42, 'e2e_test');

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(member.email, member.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    const leaderboardsPage = new LeaderboardsPage(page);
    await leaderboardsPage.goto();
    await leaderboardsPage.waitForPanels();

    // Find the member's row in the 7-day panel by display name
    const panel7day = leaderboardsPage.getPanel('7day');
    const memberRow7day = panel7day.locator('[data-testid^="leaderboard-row-"]', { hasText: displayName });
    await expect(memberRow7day).toBeVisible({ timeout: 5_000 });
    // 7-day panel should show +42 (with prefix)
    await expect(memberRow7day).toContainText('+42');

    // Find the member's row in the all-time panel
    const panelAlltime = leaderboardsPage.getPanel('alltime');
    const memberRowAlltime = panelAlltime.locator('[data-testid^="leaderboard-row-"]', { hasText: displayName });
    await expect(memberRowAlltime).toBeVisible({ timeout: 5_000 });
    // All-time should show 42 without + prefix
    const allTimeText = await memberRowAlltime.textContent();
    expect(allTimeText).toContain('42');
    expect(allTimeText).not.toContain('+42');
  });
});
