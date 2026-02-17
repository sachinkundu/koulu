import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class FeedPage extends BasePage {
  private readonly createPostInput = '[data-testid="create-post-input"]';
  private readonly createPostModal = '[data-testid="create-post-modal"]';
  private readonly postTitleInput = '[data-testid="post-title-input"]';
  private readonly postCategorySelect = '[data-testid="post-category-select"]';
  private readonly postContentInput = '[data-testid="post-content-input"]';
  private readonly modalSubmitButton = '[data-testid="modal-submit-button"]';
  private readonly modalCloseButton = '[data-testid="modal-close-button"]';
  private readonly postsList = '[data-testid="posts-list"]';
  private readonly categoryTabs = '[data-testid="category-tabs"]';
  private readonly categoryTabAll = '[data-testid="category-tab-all"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.waitForPageLoad();
  }

  async waitForFeed(): Promise<void> {
    await this.page.waitForSelector(this.postsList, {
      state: 'visible',
      timeout: 15_000,
    });
  }

  async openCreatePostModal(): Promise<void> {
    await this.page.click(this.createPostInput);
    await this.page.waitForSelector(this.createPostModal, { state: 'visible' });
  }

  async createPost(
    title: string,
    content: string,
    categoryName?: string,
  ): Promise<void> {
    await this.openCreatePostModal();

    // Wait for categories to load (more than just the placeholder option)
    const select = this.page.locator(this.postCategorySelect);
    await select.locator('option:not([value=""])').first().waitFor({ state: 'attached', timeout: 10_000 });

    await this.page.fill(this.postTitleInput, title);

    // Select category BEFORE content so react-hook-form registers the change
    if (categoryName !== undefined) {
      await select.selectOption({ label: new RegExp(categoryName) });
    } else {
      // Select the first non-empty category option
      const firstOption = await select.locator('option:not([value=""])').first().getAttribute('value');
      if (firstOption) {
        await select.selectOption(firstOption);
      }
    }

    await this.page.fill(this.postContentInput, content);

    await this.page.click(this.modalSubmitButton);
  }

  async getPostCardByTitle(title: string): Promise<ReturnType<Page['locator']>> {
    return this.page.locator(`[data-testid^="post-card-"]`, {
      hasText: title,
    });
  }

  async clickPostCard(title: string): Promise<void> {
    const card = this.page.locator(`[data-testid^="post-card-"]`, {
      hasText: title,
    });
    await card.click();
  }

  async selectCategory(slug: string): Promise<void> {
    await this.page.click(`[data-testid="category-tab-${slug}"]`);
  }

  async selectAllCategories(): Promise<void> {
    await this.page.click(this.categoryTabAll);
  }

  async selectSort(sort: 'hot' | 'new' | 'top'): Promise<void> {
    await this.page.click('[data-testid="sort-trigger"]');
    await this.page.click(`[data-testid="sort-${sort}"]`);
    // Wait for feed to reload with new sort
    await this.page.waitForTimeout(500);
  }

  async getPostCount(): Promise<number> {
    const cards = this.page.locator('[data-testid^="post-card-"]');
    return cards.count();
  }

  async waitForCategoryTabs(): Promise<void> {
    await this.page.waitForSelector(this.categoryTabs, {
      state: 'visible',
      timeout: 10_000,
    });
  }
}
