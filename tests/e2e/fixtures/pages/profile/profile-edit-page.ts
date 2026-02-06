import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ProfileEditPage extends BasePage {
  private readonly displayNameInput = '[data-testid="profile-edit-display-name"]';
  private readonly bioInput = '[data-testid="profile-edit-bio"]';
  private readonly bioCounter = '[data-testid="profile-edit-bio-counter"]';
  private readonly cityInput = '[data-testid="profile-edit-city"]';
  private readonly countryInput = '[data-testid="profile-edit-country"]';
  private readonly saveButton = '[data-testid="profile-edit-save"]';
  private readonly cancelButton = '[data-testid="profile-edit-cancel"]';
  private readonly errorAlert = '[data-testid="profile-edit-error"]';
  private readonly displayNameError = '[data-testid="profile-edit-display-name-error"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/profile/edit');
    await this.waitForPageLoad();
  }

  async waitForPage(): Promise<void> {
    await this.page.waitForSelector(this.displayNameInput, { state: 'visible' });
  }

  async fillDisplayName(name: string): Promise<void> {
    await this.page.fill(this.displayNameInput, name);
  }

  async fillBio(bio: string): Promise<void> {
    await this.page.fill(this.bioInput, bio);
  }

  async fillCity(city: string): Promise<void> {
    await this.page.fill(this.cityInput, city);
  }

  async fillCountry(country: string): Promise<void> {
    await this.page.fill(this.countryInput, country);
  }

  async save(): Promise<void> {
    await this.page.click(this.saveButton);
  }

  async cancel(): Promise<void> {
    await this.page.click(this.cancelButton);
  }

  async getBioCounter(): Promise<string> {
    const el = this.page.locator(this.bioCounter);
    return (await el.textContent()) ?? '';
  }

  async getErrorMessage(): Promise<string> {
    const el = this.page.locator(this.errorAlert);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async getDisplayNameError(): Promise<string> {
    const el = this.page.locator(this.displayNameError);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async getDisplayNameValue(): Promise<string> {
    return this.page.locator(this.displayNameInput).inputValue();
  }
}
