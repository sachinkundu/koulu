import { type Page } from '@playwright/test';
import { BasePage } from '../base-page';

export class ClassroomPageObject extends BasePage {
  private readonly classroomPage = '[data-testid="classroom-page"]';
  private readonly coursesGrid = '[data-testid="courses-grid"]';
  private readonly createCourseButton = '[data-testid="create-course-button"]';
  private readonly createCourseModal = '[data-testid="create-course-modal"]';
  private readonly courseTitleInput = '[data-testid="course-title-input"]';
  private readonly courseDescriptionInput = '[data-testid="course-description-input"]';
  private readonly createCourseSubmit = '[data-testid="create-course-submit"]';
  private readonly courseDetail = '[data-testid="course-detail"]';
  private readonly courseTitle = '[data-testid="course-title"]';
  private readonly courseContent = '[data-testid="course-content"]';
  private readonly backToCourses = '[data-testid="back-to-courses"]';
  private readonly deleteCourseButton = '[data-testid="delete-course-button"]';

  constructor(page: Page) {
    super(page);
  }

  async goto(): Promise<void> {
    await this.page.goto('/classroom');
    await this.waitForPageLoad();
  }

  async waitForClassroomPage(): Promise<void> {
    await this.page.waitForSelector(this.classroomPage, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async waitForCoursesGrid(): Promise<void> {
    await this.page.waitForSelector(this.coursesGrid, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async openCreateCourseModal(): Promise<void> {
    await this.page.click(this.createCourseButton);
    await this.page.waitForSelector(this.createCourseModal, {
      state: 'visible',
      timeout: 5_000,
    });
  }

  async createCourse(title: string, description?: string): Promise<void> {
    await this.openCreateCourseModal();
    const titleInput = this.page.locator(this.courseTitleInput);
    await titleInput.waitFor({ state: 'visible', timeout: 5_000 });
    // Wait for React useEffect reset() to complete before filling
    // The modal's useEffect clears the form on open — filling too early gets wiped
    await this.page.waitForTimeout(300);
    await titleInput.click();
    await titleInput.fill(title);
    if (description !== undefined) {
      const descInput = this.page.locator(this.courseDescriptionInput);
      await descInput.fill(description);
    }
    await this.page.locator(this.createCourseSubmit).click();
    // Wait for navigation to course detail
    await this.page.waitForURL(/\/classroom\/courses\//, { timeout: 15_000 });
  }

  async getCourseCardByTitle(title: string): ReturnType<Page['locator']> {
    return this.page.locator(`[data-testid^="course-card-"]`, { hasText: title });
  }

  async clickCourseCard(title: string): Promise<void> {
    const card = this.page.locator(`[data-testid^="course-card-"]`, { hasText: title });
    await card.click();
  }

  // Course detail methods
  async waitForCourseDetail(): Promise<void> {
    await this.page.waitForSelector(this.courseDetail, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async getCourseTitle(): Promise<string> {
    const el = this.page.locator(this.courseTitle);
    await el.waitFor({ state: 'visible' });
    return (await el.textContent()) ?? '';
  }

  async waitForCourseContent(): Promise<void> {
    await this.page.waitForSelector(this.courseContent, {
      state: 'visible',
      timeout: 10_000,
    });
  }

  async goBackToCourses(): Promise<void> {
    await this.page.click(this.backToCourses);
  }

  async deleteCourse(): Promise<void> {
    this.page.on('dialog', (dialog) => void dialog.accept());
    await this.page.click(this.deleteCourseButton);
  }

  async hasDeleteButton(): Promise<boolean> {
    return this.page.locator(this.deleteCourseButton).isVisible();
  }

  async getModuleCount(): Promise<number> {
    const modules = this.page.locator('[data-testid^="module-"]:not([data-testid*="-progress-"])');
    return modules.count();
  }

  async getLessonCount(): Promise<number> {
    const lessons = this.page.locator('[data-testid^="lesson-"]:not([data-testid*="complete-icon"])');
    return lessons.count();
  }
}
