import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class SearchPage extends BasePage {
  private readonly searchInput = '[data-testid="search-bar-input"]';
  private readonly searchForm = '[data-testid="search-bar-form"]';
  private readonly clearButton = '[data-testid="search-bar-clear"]';
  private readonly tabs = '[data-testid="search-tabs"]';
  private readonly membersTab = '[data-testid="search-tab-members"]';
  private readonly postsTab = '[data-testid="search-tab-posts"]';
  private readonly resultsList = '[data-testid="search-results-list"]';
  private readonly memberCard = '[data-testid="member-search-card"]';
  private readonly postCard = '[data-testid="post-search-card"]';
  private readonly noResults = '[data-testid="search-no-results"]';
  private readonly emptyState = '[data-testid="search-empty-state"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(query: string, type: 'members' | 'posts' = 'members'): Promise<void> {
    await this.page.goto(`/search?q=${encodeURIComponent(query)}&t=${type}`);
    await this.waitForPageLoad();
  }

  async searchFromHeader(query: string): Promise<void> {
    await this.page.fill(this.searchInput, query);
    await this.page.locator(this.searchForm).press('Enter');
    await this.page.waitForURL(/\/search\?/, { timeout: 10_000 });
    await this.waitForPageLoad();
  }

  async clearSearch(): Promise<void> {
    await this.page.click(this.clearButton);
  }

  async switchToMembersTab(): Promise<void> {
    await this.page.click(this.membersTab);
  }

  async switchToPostsTab(): Promise<void> {
    await this.page.click(this.postsTab);
  }

  async getTabText(tab: 'members' | 'posts'): Promise<string> {
    const selector = tab === 'members' ? this.membersTab : this.postsTab;
    return (await this.page.locator(selector).textContent()) ?? '';
  }

  async waitForResults(): Promise<void> {
    await this.page.waitForSelector(this.resultsList, {
      state: 'visible',
      timeout: 15_000,
    });
  }

  async waitForNoResults(): Promise<void> {
    await this.page.waitForSelector(this.noResults, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async waitForEmptyState(): Promise<void> {
    await this.page.waitForSelector(this.emptyState, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async getMemberCardCount(): Promise<number> {
    return this.page.locator(this.memberCard).count();
  }

  async getPostCardCount(): Promise<number> {
    return this.page.locator(this.postCard).count();
  }

  getMemberCardByName(name: string): ReturnType<Page['locator']> {
    return this.page.locator(this.memberCard, { hasText: name });
  }

  getPostCardByTitle(title: string): ReturnType<Page['locator']> {
    return this.page.locator(this.postCard, { hasText: title });
  }

  async clickMemberCard(name: string): Promise<void> {
    await this.getMemberCardByName(name).click();
  }

  async clickPostCard(title: string): Promise<void> {
    await this.getPostCardByTitle(title).click();
  }

  async getSearchInputValue(): Promise<string> {
    return (await this.page.locator(this.searchInput).inputValue()) ?? '';
  }
}
