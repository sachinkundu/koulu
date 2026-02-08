import { type Page } from '@playwright/test';
import { BasePage } from './base-page';

export class HomePage extends BasePage {
  private readonly communityTab = 'nav[aria-label="Tabs"] a:has-text("Community")';
  private readonly userAvatarButton = '[data-testid="user-avatar-button"]';
  private readonly dropdownMenu = '[data-testid="user-dropdown-menu"]';
  private readonly dropdownProfileLink = '[data-testid="dropdown-profile-link"]';
  private readonly dropdownEditProfileLink = '[data-testid="dropdown-edit-profile-link"]';
  private readonly dropdownLogoutButton = '[data-testid="dropdown-logout-button"]';

  constructor(page: Page) {
    super(page);
  }

  async waitForPage(): Promise<void> {
    await this.page.waitForSelector(this.userAvatarButton, { state: 'visible' });
  }

  async getAvatarAltText(): Promise<string> {
    const img = this.page.locator(`${this.userAvatarButton} img`);
    return (await img.getAttribute('alt')) ?? '';
  }

  async openUserDropdown(): Promise<void> {
    await this.page.click(this.userAvatarButton);
    await this.page.waitForSelector(this.dropdownMenu, { state: 'visible' });
  }

  async navigateToProfile(): Promise<void> {
    await this.openUserDropdown();
    await this.page.click(this.dropdownProfileLink);
  }

  async navigateToEditProfile(): Promise<void> {
    await this.openUserDropdown();
    await this.page.click(this.dropdownEditProfileLink);
  }

  async signOut(): Promise<void> {
    await this.openUserDropdown();
    await this.page.click(this.dropdownLogoutButton);
  }
}
