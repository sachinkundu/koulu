import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { HomePage } from '../../fixtures/pages/home-page';
import { createUserWithProfile } from '../../helpers/api-helpers';

test.describe('Login', () => {
  test('should login successfully and see homepage with display name', async ({
    page,
  }) => {
    const displayName = `E2E Tester ${Date.now()}`;
    const user = await createUserWithProfile(displayName);

    // Step 1: Navigate to login
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Step 2: Fill credentials and submit
    await loginPage.login(user.email, user.password);

    // Step 3: Should be redirected to homepage
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 4: Verify homepage shows the user's display name
    const homePage = new HomePage(page);
    await homePage.waitForPage();

    const headerName = await homePage.getDisplayedName();
    expect(headerName).toBe(displayName);

    const welcomeMessage = await homePage.getWelcomeMessage();
    expect(welcomeMessage).toContain(displayName);
  });

  test('should show error message for invalid credentials', async ({
    page,
  }) => {
    // Step 1: Navigate to login
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Step 2: Try to login with wrong credentials
    await loginPage.login('nonexistent@example.com', 'wrongpassword');

    // Step 3: Should see error message
    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toContain('Invalid email or password');

    // Step 4: Should still be on login page
    expect(page.url()).toContain('/login');
  });
});
