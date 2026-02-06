import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class RegisterPage extends BasePage {
  private readonly emailInput = '#email';
  private readonly passwordInput = '#password';
  private readonly submitButton = 'button[type="submit"]';
  private readonly errorAlert = '[role="alert"]';
  private readonly successHeading = 'text=Check your email';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/register');
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

  async register(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.submit();
  }

  async expectSuccessMessage(): Promise<void> {
    await this.page.waitForSelector(this.successHeading, { state: 'visible' });
  }

  async expectError(): Promise<string> {
    const alert = this.page.locator(this.errorAlert);
    await alert.waitFor({ state: 'visible' });
    return (await alert.textContent()) ?? '';
  }
}
