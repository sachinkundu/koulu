import { test, expect } from '@playwright/test';
import { ClassroomPageObject } from '../../fixtures/pages/classroom/classroom-page';
import { LoginPage } from '../../fixtures/pages/auth/login-page';
import {
  cleanTestState,
  createCommunityMember,
  createCourseApi,
  addModuleApi,
  addLessonApi,
} from '../../helpers/api-helpers';

test.describe('Classroom', () => {
  test.beforeEach(async () => {
    await cleanTestState();
  });

  test('User creates a course and sees it in the list', async ({ page }) => {
    const user = await createCommunityMember(`E2E Course ${Date.now()}`);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Navigate to classroom
    const classroomPage = new ClassroomPageObject(page);
    await classroomPage.goto();
    await classroomPage.waitForClassroomPage();

    // Create course
    const courseTitle = `Test Course ${Date.now()}`;
    await classroomPage.createCourse(courseTitle, 'A test course description.');

    // Should be on course detail page
    await classroomPage.waitForCourseDetail();
    const title = await classroomPage.getCourseTitle();
    expect(title).toBe(courseTitle);

    // Go back and verify course appears in list
    await classroomPage.goBackToCourses();
    await classroomPage.waitForClassroomPage();
    await classroomPage.waitForCoursesGrid();

    const courseCard = await classroomPage.getCourseCardByTitle(courseTitle);
    await expect(courseCard).toBeVisible();
  });

  test('User views course with modules and lessons', async ({ page }) => {
    const user = await createCommunityMember(`E2E Detail ${Date.now()}`);

    // Create course with content via API
    const courseTitle = `Detail Course ${Date.now()}`;
    const { id: courseId } = await createCourseApi(user.accessToken, courseTitle, 'Course with modules.');
    const { id: moduleId } = await addModuleApi(user.accessToken, courseId, 'Module 1', 'First module');
    await addLessonApi(user.accessToken, moduleId, 'Lesson 1', 'text', 'Lesson content here.');
    await addLessonApi(user.accessToken, moduleId, 'Lesson 2', 'text', 'More content.');

    // Login and navigate to course
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Go to course detail
    await page.goto(`/classroom/courses/${courseId}`);
    const classroomPage = new ClassroomPageObject(page);
    await classroomPage.waitForCourseDetail();

    // Verify title
    const title = await classroomPage.getCourseTitle();
    expect(title).toBe(courseTitle);

    // Verify content structure
    await classroomPage.waitForCourseContent();
    const moduleCount = await classroomPage.getModuleCount();
    expect(moduleCount).toBe(1);

    const lessonCount = await classroomPage.getLessonCount();
    expect(lessonCount).toBe(2);
  });

  test('User deletes own course', async ({ page }) => {
    const user = await createCommunityMember(`E2E Delete ${Date.now()}`);

    // Create course via API
    const courseTitle = `Delete Me ${Date.now()}`;
    const { id: courseId } = await createCourseApi(user.accessToken, courseTitle);

    // Login
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(user.email, user.password);
    await page.waitForURL(/^\/$|.*\/$/, { timeout: 10_000 });

    // Go to course detail
    await page.goto(`/classroom/courses/${courseId}`);
    const classroomPage = new ClassroomPageObject(page);
    await classroomPage.waitForCourseDetail();

    // Delete course
    const hasDelete = await classroomPage.hasDeleteButton();
    expect(hasDelete).toBe(true);

    await classroomPage.deleteCourse();

    // Should be redirected to classroom
    await page.waitForURL(/\/classroom$/, { timeout: 10_000 });
    await classroomPage.waitForClassroomPage();

    // Verify course is gone
    const courseCard = await classroomPage.getCourseCardByTitle(courseTitle);
    await expect(courseCard).toBeHidden({ timeout: 5_000 });
  });
});
