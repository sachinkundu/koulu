import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { HomePage } from '../../fixtures/pages/home-page';
import {
  cleanTestState,
  createUserWithProfile,
} from '../../helpers/api-helpers';

test.describe('Logout', () => {
  test.beforeEach(async () => {
    await cleanTestState();
  });

  test('User logs out and is redirected to login page', async ({ page }) => {
    const user = await createUserWithProfile(`E2E Logout ${Date.now()}`);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Verify we're on homepage (avatar visible)
    const homePage = new HomePage(page);
    await homePage.waitForPage();

    // Sign out via user dropdown
    await homePage.signOut();

    // Verify redirect to login page
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});
