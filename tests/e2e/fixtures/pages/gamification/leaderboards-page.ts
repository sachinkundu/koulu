import { type Locator, type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class LeaderboardsPage extends BasePage {
  private readonly levelGrid = '[data-testid="level-definitions-grid"]';
  private readonly profileCard = '[data-testid="leaderboard-profile-card"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/leaderboards');
    await this.waitForPageLoad();
  }

  // --- Level Grid ---

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

  // --- Profile Card ---

  async waitForProfileCard(): Promise<void> {
    await this.page.waitForSelector(this.profileCard, {
      state: 'visible',
      timeout: 15_000,
    });
  }

  getProfileCard(): Locator {
    return this.page.locator(this.profileCard);
  }

  // --- Leaderboard Panels ---

  getPanel(period: '7day' | '30day' | 'alltime'): Locator {
    return this.page.locator(`[data-testid="leaderboard-panel-${period}"]`);
  }

  async waitForPanels(): Promise<void> {
    await this.page.waitForSelector('[data-testid="leaderboard-panel-7day"]', {
      state: 'visible',
      timeout: 15_000,
    });
  }

  getPanelRows(period: '7day' | '30day' | 'alltime'): Locator {
    return this.getPanel(period).locator('[data-testid^="leaderboard-row-"]');
  }

  getPanelRow(period: '7day' | '30day' | 'alltime', rank: number): Locator {
    return this.getPanel(period).locator(`[data-testid="leaderboard-row-${rank}"]`);
  }

  getYourRankSection(period: '7day' | '30day' | 'alltime'): Locator {
    return this.getPanel(period).locator('[data-testid="your-rank-section"]');
  }
}
