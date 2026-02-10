import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { HomePage } from '../../fixtures/pages/home-page';
import { ProfileViewPage } from '../../fixtures/pages/profile/profile-view-page';
import { cleanTestState, createUserWithProfile } from '../../helpers/api-helpers';

test.describe('Profile View', () => {
  test.beforeEach(async () => {
    await cleanTestState();
  });
  test('should view own profile with display name and edit button', async ({
    page,
  }) => {
    const displayName = `E2E Profile ${Date.now()}`;
    const user = await createUserWithProfile(displayName);

    // Step 1: Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);

    // Step 2: Wait for homepage redirect
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 3: Navigate to own profile via user dropdown
    const homePage = new HomePage(page);
    await homePage.waitForPage();
    await homePage.navigateToProfile();

    // Step 4: Verify profile page loads
    const profilePage = new ProfileViewPage(page);
    await profilePage.waitForPage();

    // Step 5: Verify display name
    const shownName = await profilePage.getDisplayName();
    expect(shownName).toBe(displayName);

    // Step 6: Verify avatar is displayed (backend auto-generates avatar URL)
    const hasAvatar = await profilePage.hasAvatar();
    expect(hasAvatar).toBe(true);

    // Step 7: Verify edit button is visible (own profile)
    const hasEdit = await profilePage.hasEditButton();
    expect(hasEdit).toBe(true);
  });

  test('should not show edit button on another user profile', async ({
    page,
  }) => {
    // Create two users
    const userA = await createUserWithProfile(`UserA ${Date.now()}`);
    const userB = await createUserWithProfile(`UserB ${Date.now()}`);

    // Login as user A
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(userA.email, userA.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to user B's profile
    // Extract user B's ID from their access token (JWT payload)
    const tokenParts = userB.accessToken.split('.');
    const payload = JSON.parse(atob(tokenParts[1]));
    const userBId = payload.sub;

    const profilePage = new ProfileViewPage(page);
    await profilePage.goto(userBId);
    await profilePage.waitForPage();

    // Verify edit button is NOT visible
    const hasEdit = await profilePage.hasEditButton();
    expect(hasEdit).toBe(false);
  });
});
