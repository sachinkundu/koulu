import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileViewPage extends BasePage {
  private readonly sidebar = '[data-testid="profile-sidebar"]';
  private readonly displayName = '[data-testid="profile-display-name"]';
  private readonly bio = '[data-testid="profile-bio"]';
  private readonly location = '[data-testid="profile-location"]';
  private readonly editButton = '[data-testid="profile-edit-button"]';
  private readonly notFound = '[data-testid="profile-not-found"]';
  private readonly avatar = '[data-testid="profile-avatar"]';
  private readonly avatarPlaceholder = '[data-testid="profile-avatar-placeholder"]';
  private readonly contributions = '[data-testid="profile-contributions"]';
  private readonly joinedDate = '[data-testid="profile-joined-date"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(userId: string): Promise<void> {
    await this.page.goto(`/profile/${userId}`);
    await this.waitForPageLoad();
  }

  async waitForPage(): Promise<void> {
    await this.page.waitForSelector(this.sidebar, { state: 'visible' });
  }

  async getDisplayName(): Promise<string> {
    const el = this.page.locator(this.displayName);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async getBio(): Promise<string> {
    const el = this.page.locator(this.bio);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async getLocation(): Promise<string> {
    const el = this.page.locator(this.location);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async hasEditButton(): Promise<boolean> {
    return this.page.locator(this.editButton).isVisible();
  }

  async clickEditButton(): Promise<void> {
    await this.page.click(this.editButton);
  }

  async hasAvatar(): Promise<boolean> {
    return this.page.locator(this.avatar).isVisible();
  }

  async isNotFound(): Promise<boolean> {
    return this.page.locator(this.notFound).isVisible();
  }

  async getAvatarInitial(): Promise<string> {
    const el = this.page.locator(this.avatarPlaceholder);
    return (await el.textContent()) ?? '';
  }

  async getContributions(): Promise<string> {
    const el = this.page.locator(this.contributions);
    return (await el.textContent()) ?? '';
  }

  async getJoinedDate(): Promise<string> {
    const el = this.page.locator(this.joinedDate);
    return (await el.textContent()) ?? '';
  }
}
