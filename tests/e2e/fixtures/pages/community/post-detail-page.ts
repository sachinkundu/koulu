import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class PostDetailPage extends BasePage {
  private readonly postDetail = '[data-testid="post-detail"]';
  private readonly postDetailModal = '[data-testid="post-detail-modal"]';
  private readonly deleteButton = '[data-testid="post-delete-button"]';
  private readonly editButton = '[data-testid="post-edit-button"]';
  private readonly closeModalButton = '[data-testid="close-modal-button"]';
  private readonly backToFeed = '[data-testid="back-to-feed"]';
  private readonly likeButton = '[data-testid="like-button"]';
  private readonly commentThread = '[data-testid="comment-thread"]';
  private readonly addCommentForm = '[data-testid="add-comment-form"]';
  private readonly commentInput = '[data-testid="comment-content-input"]';
  private readonly commentSubmit = '[data-testid="comment-submit-button"]';
  private readonly editPostModal = '[data-testid="edit-post-modal"]';
  private readonly editPostTitleInput = '[data-testid="edit-post-title-input"]';
  private readonly editPostContentInput = '[data-testid="edit-post-content-input"]';
  private readonly editPostSubmit = '[data-testid="edit-post-submit-button"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(postId: string): Promise<void> {
    await this.page.goto(`/community/posts/${postId}`);
    await this.waitForPageLoad();
  }

  async waitForDetail(): Promise<void> {
    await this.page.waitForSelector(this.postDetail, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async waitForModal(): Promise<void> {
    await this.page.waitForSelector(this.postDetailModal, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async getTitle(): Promise<string> {
    const heading = this.page.locator(`${this.postDetail} h1`);
    await heading.waitFor({ state: 'visible' });
    return (await heading.textContent()) ?? '';
  }

  async getContent(): Promise<string> {
    const content = this.page.locator(`${this.postDetail} .whitespace-pre-wrap`);
    await content.waitFor({ state: 'visible' });
    return (await content.textContent()) ?? '';
  }

  async getModalTitle(): Promise<string> {
    const heading = this.page.locator(`${this.postDetailModal} h1`);
    await heading.waitFor({ state: 'visible' });
    return (await heading.textContent()) ?? '';
  }

  async getModalContent(): Promise<string> {
    const content = this.page.locator(
      `${this.postDetailModal} .whitespace-pre-wrap`,
    );
    await content.waitFor({ state: 'visible' });
    return (await content.textContent()) ?? '';
  }

  async deletePost(): Promise<void> {
    this.page.on('dialog', (dialog) => void dialog.accept());
    await this.page.click(this.deleteButton);
  }

  async closeModal(): Promise<void> {
    await this.page.click(this.closeModalButton);
  }

  async goBackToFeed(): Promise<void> {
    await this.page.click(this.backToFeed);
  }

  async hasDeleteButton(): Promise<boolean> {
    return this.page.locator(this.deleteButton).isVisible();
  }

  async hasEditButton(): Promise<boolean> {
    return this.page.locator(this.editButton).isVisible();
  }

  // Like interactions
  async clickLikeButton(): Promise<void> {
    await this.page.click(this.likeButton);
  }

  async getLikeCount(): Promise<string> {
    const span = this.page.locator(`${this.likeButton} span`);
    await span.waitFor({ state: 'visible' });
    return (await span.textContent()) ?? '0';
  }

  // Comment interactions
  async waitForCommentThread(): Promise<void> {
    await this.page.waitForSelector(this.commentThread, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async addComment(content: string): Promise<void> {
    await this.page.fill(this.commentInput, content);
    await this.page.click(this.commentSubmit);
    // Wait for comment to appear in the thread
    await this.page.waitForTimeout(1000);
  }

  async getCommentCount(): Promise<number> {
    const commentsList = this.page.locator('[data-testid="comments-list"]');
    const isVisible = await commentsList.isVisible();
    if (!isVisible) return 0;
    const comments = commentsList.locator('[data-testid^="comment-"]');
    return comments.count();
  }

  async getCommentText(index: number): Promise<string> {
    const comments = this.page.locator('[data-testid^="comment-"] .whitespace-pre-wrap');
    const comment = comments.nth(index);
    await comment.waitFor({ state: 'visible' });
    return (await comment.textContent()) ?? '';
  }

  // Comment reply interactions
  async replyToComment(commentId: string, content: string): Promise<void> {
    const comment = this.page.locator(`[data-testid="comment-${commentId}"]`);
    await comment.locator('[data-testid="comment-reply-button"]').click();
    const replyForm = comment.locator('[data-testid="add-comment-form"]');
    await replyForm.waitFor({ state: 'visible', timeout: 5_000 });
    await replyForm.locator('[data-testid="comment-content-input"]').fill(content);
    await replyForm.locator('[data-testid="comment-submit-button"]').click();
    await this.page.waitForTimeout(1000);
  }

  // Comment edit interactions
  async editComment(commentId: string, newContent: string): Promise<void> {
    const comment = this.page.locator(`[data-testid="comment-${commentId}"]`).first();
    await comment.locator('[data-testid="comment-edit-button"]').click();
    const editForm = comment.locator('[data-testid="edit-comment-form"]');
    await editForm.waitFor({ state: 'visible', timeout: 5_000 });
    await editForm.locator('[data-testid="edit-comment-input"]').fill(newContent);
    await editForm.locator('[data-testid="edit-comment-save"]').click();
    await this.page.waitForTimeout(1000);
  }

  // Comment delete interactions
  async deleteComment(commentId: string): Promise<void> {
    this.page.on('dialog', (dialog) => void dialog.accept());
    const comment = this.page.locator(`[data-testid="comment-${commentId}"]`).first();
    await comment.locator('[data-testid="comment-delete-button"]').click();
    await this.page.waitForTimeout(1000);
  }

  // Comment like interactions
  async clickCommentLikeButton(commentId: string): Promise<void> {
    const comment = this.page.locator(`[data-testid="comment-${commentId}"]`).first();
    await comment.locator('[data-testid="comment-like-button"]').click();
  }

  async getCommentLikeText(commentId: string): Promise<string> {
    const comment = this.page.locator(`[data-testid="comment-${commentId}"]`).first();
    const btn = comment.locator('[data-testid="comment-like-button"]');
    const span = btn.locator('span');
    await span.waitFor({ state: 'visible' });
    return (await span.textContent()) ?? '';
  }

  // Edit post interactions
  async clickEditButton(): Promise<void> {
    await this.page.click(this.editButton);
  }

  async waitForEditModal(): Promise<void> {
    await this.page.waitForSelector(this.editPostModal, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async editPost(title: string, content: string): Promise<void> {
    await this.clickEditButton();
    await this.waitForEditModal();
    await this.page.fill(this.editPostTitleInput, title);
    await this.page.fill(this.editPostContentInput, content);
    await this.page.click(this.editPostSubmit);
    // Wait for modal to close
    await this.page.waitForSelector(this.editPostModal, {
      state: 'hidden',
      timeout: 10_000,
    });
  }
}
