import { test, expect } from '@playwright/test';
import { RegisterPage } from '../../fixtures/pages/auth/register-page';
import { ProfileSetupPage } from '../../fixtures/pages/profile/profile-setup-page';
import { HomePage } from '../../fixtures/pages/home-page';
import { generateTestEmail } from '../../helpers/api-helpers';
import { getVerificationToken } from '../../helpers/email-helpers';

test.describe('New Member Onboarding', () => {
  test('should complete full registration flow: register, verify email, complete profile, see homepage', async ({
    page,
  }) => {
    const email = generateTestEmail();
    const password = 'testpass123';
    const displayName = `E2E User ${Date.now()}`;

    // Step 1: Register
    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    await registerPage.register(email, password);

    // Step 2: See "Check your email" confirmation
    await registerPage.expectSuccessMessage();

    // Step 3: Retrieve verification token from MailHog
    const verificationToken = await getVerificationToken(email);
    expect(verificationToken).toBeTruthy();

    // Step 4: Navigate to verification URL (simulates clicking email link)
    await page.goto(`/verify?token=${verificationToken}`);

    // Step 5: Wait for "Email verified!" success message
    await page.waitForSelector('text=Email verified!', { state: 'visible' });

    // Step 6: Wait for redirect to profile setup (1.5s delay + navigation)
    await page.waitForURL('**/onboarding/profile', { timeout: 10_000 });

    // Step 7: Complete profile
    const profileSetupPage = new ProfileSetupPage(page);
    await profileSetupPage.completeProfile(displayName);

    // Step 8: Should be redirected to homepage
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Step 9: Verify homepage shows welcome message with display name
    const homePage = new HomePage(page);
    await homePage.waitForPage();

    const welcomeMessage = await homePage.getWelcomeMessage();
    expect(welcomeMessage).toContain(displayName);

    const headerName = await homePage.getDisplayedName();
    expect(headerName).toBe(displayName);
  });
});
