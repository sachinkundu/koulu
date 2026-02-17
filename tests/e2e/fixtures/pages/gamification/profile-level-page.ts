import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileLevelPage extends BasePage {
  private readonly levelSection = '[data-testid="profile-level-section"]';
  private readonly levelName = '[data-testid="profile-level-name"]';
  private readonly levelPoints = '[data-testid="profile-level-points"]';
  private readonly levelProgress = '[data-testid="profile-level-progress"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(userId: string): Promise<void> {
    await this.page.goto(`/profile/${userId}`);
    await this.waitForPageLoad();
  }

  async waitForLevelSection(): Promise<void> {
    await this.page.waitForSelector(this.levelSection, {
      state: 'visible',
      timeout: 15_000,
    });
  }

  async getLevelName(): Promise<string> {
    return (await this.page.locator(this.levelName).textContent()) ?? '';
  }

  async getLevelPoints(): Promise<string> {
    return (await this.page.locator(this.levelPoints).textContent()) ?? '';
  }

  async getLevelProgress(): Promise<string> {
    return (await this.page.locator(this.levelProgress).textContent()) ?? '';
  }

  async hasLevelSection(): Promise<boolean> {
    return this.page.locator(this.levelSection).isVisible();
  }
}
