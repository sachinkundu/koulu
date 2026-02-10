import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';
import { flushRateLimits } from '../../../helpers/api-helpers';

export class LoginPage extends BasePage {
  private readonly emailInput = '#email';
  private readonly passwordInput = '#password';
  private readonly submitButton = 'button[type="submit"]';
  private readonly errorAlert = '[role="alert"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/login');
    await this.waitForPageLoad();
  }

  async fillEmail(email: string): Promise<void> {
    await this.page.fill(this.emailInput, email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.page.fill(this.passwordInput, password);
  }

  async submit(): Promise<void> {
    await this.page.click(this.submitButton);
  }

  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    // Flush rate limits right before submitting to prevent 429s
    // when parallel workers have accumulated API calls
    await flushRateLimits();
    await this.submit();
  }

  async getErrorMessage(): Promise<string> {
    const alert = this.page.locator(this.errorAlert);
    await alert.waitFor({ state: 'visible' });
    return (await alert.textContent()) ?? '';
  }
}
