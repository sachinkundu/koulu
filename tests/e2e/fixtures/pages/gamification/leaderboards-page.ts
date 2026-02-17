import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class LeaderboardsPage extends BasePage {
  private readonly levelGrid = '[data-testid="level-definitions-grid"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/leaderboards');
    await this.waitForPageLoad();
  }

  async waitForGrid(): Promise<void> {
    await this.page.waitForSelector(this.levelGrid, {
      state: 'visible',
      timeout: 15_000,
    });
  }

  getLevelCard(level: number) {
    return this.page.locator(`[data-testid="level-card-${level}"]`);
  }

  async getLevelCardCount(): Promise<number> {
    return this.page.locator('[data-testid^="level-card-"]').count();
  }

  async isLevelHighlighted(level: number): Promise<boolean> {
    const card = this.getLevelCard(level);
    const classes = await card.getAttribute('class');
    return classes?.includes('ring-blue-500') ?? false;
  }
}
