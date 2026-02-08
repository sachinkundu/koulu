import { test, expect } from '@playwright/test';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import { HomePage } from '../../fixtures/pages/home-page';
import { ProfileEditPage } from '../../fixtures/pages/profile/profile-edit-page';
import { ProfileViewPage } from '../../fixtures/pages/profile/profile-view-page';
import { createUserWithProfile } from '../../helpers/api-helpers';

test.describe('Profile Edit', () => {
  test('should edit profile and see changes on profile view', async ({
    page,
  }) => {
    const originalName = `E2E Edit ${Date.now()}`;
    const user = await createUserWithProfile(originalName);

    // Step 1: Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 2: Navigate to edit profile via user dropdown
    const homePage = new HomePage(page);
    await homePage.waitForPage();
    await homePage.navigateToEditProfile();
    await page.waitForURL('**/profile/edit', { timeout: 10_000 });

    // Step 3: Edit the profile
    const editPage = new ProfileEditPage(page);
    await editPage.waitForPage();

    const newName = `Updated ${Date.now()}`;
    const newBio = 'This is my updated bio for testing';

    await editPage.fillDisplayName(newName);
    await editPage.fillBio(newBio);
    await editPage.fillCity('Helsinki');
    await editPage.fillCountry('Finland');
    await editPage.save();

    // Step 4: Should redirect to profile view
    await page.waitForURL('**/profile/**', { timeout: 10_000 });

    // Step 5: Verify changes on profile view
    const profilePage = new ProfileViewPage(page);
    await profilePage.waitForPage();

    const shownName = await profilePage.getDisplayName();
    expect(shownName).toBe(newName);

    const shownBio = await profilePage.getBio();
    expect(shownBio).toBe(newBio);

    const shownLocation = await profilePage.getLocation();
    expect(shownLocation).toBe('Helsinki, Finland');
  });

  test('should show validation error for empty display name', async ({
    page,
  }) => {
    const user = await createUserWithProfile(`E2E Validate ${Date.now()}`);

    // Step 1: Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 2: Navigate to edit profile via user dropdown
    const homePage = new HomePage(page);
    await homePage.waitForPage();
    await homePage.navigateToEditProfile();
    await page.waitForURL('**/profile/edit', { timeout: 10_000 });

    // Step 3: Clear display name and submit
    const editPage = new ProfileEditPage(page);
    await editPage.waitForPage();
    await editPage.fillDisplayName('');
    await editPage.save();

    // Step 4: Should show validation error
    const errorMessage = await editPage.getDisplayNameError();
    expect(errorMessage).toContain('Display name must be at least 2 characters');

    // Step 5: Should still be on edit page
    expect(page.url()).toContain('/profile/edit');
  });
});
