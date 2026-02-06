import { type Page } from '@playwright/test';
import { BasePage } from './base-page';

export class HomePage extends BasePage {
  private readonly welcomeHeading = 'h2:has-text("Welcome")';
  private readonly headerUserName = '[data-testid="header-display-name"]';
  private readonly signOutButton = 'header button:has-text("Sign out")';

  constructor(page: Page) {
    super(page);
  }

  async waitForPage(): Promise<void> {
    await this.page.waitForSelector(this.welcomeHeading, { state: 'visible' });
  }

  async getWelcomeMessage(): Promise<string> {
    const heading = this.page.locator(this.welcomeHeading);
    return (await heading.textContent()) ?? '';
  }

  async getDisplayedName(): Promise<string> {
    const name = this.page.locator(this.headerUserName);
    return (await name.textContent()) ?? '';
  }

  async signOut(): Promise<void> {
    await this.page.click(this.signOutButton);
  }
}
