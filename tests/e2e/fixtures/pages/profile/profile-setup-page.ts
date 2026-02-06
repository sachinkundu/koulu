import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileSetupPage extends BasePage {
  private readonly displayNameInput = '#display_name';
  private readonly submitButton = 'button[type="submit"]';
  private readonly heading = 'text=Complete your profile';

  constructor(page: Page) {
    super(page);
  }

  async waitForPage(): Promise<void> {
    await this.page.waitForSelector(this.heading, { state: 'visible' });
  }

  async fillDisplayName(name: string): Promise<void> {
    await this.page.fill(this.displayNameInput, name);
  }

  async submit(): Promise<void> {
    await this.page.click(this.submitButton);
  }

  async completeProfile(displayName: string): Promise<void> {
    await this.waitForPage();
    await this.fillDisplayName(displayName);
    await this.submit();
  }
}
