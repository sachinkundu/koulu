import { clearEmails, getVerificationToken } from './email-helpers';

const API_URL = process.env.API_URL ?? 'http://localhost:8000/api/v1';
/**
 * Flush Redis to clear all rate limits.
 * Uses docker exec with the container name (set via REDIS_CONTAINER env var).
 * Falls back to common container names if env var is not set.
 */
export async function flushRateLimits(): Promise<void> {
  const { execSync } = await import('child_process');
  const containerName = process.env.REDIS_CONTAINER ?? 'koulu_redis';
  try {
    execSync(`docker exec ${containerName} redis-cli FLUSHALL`, { stdio: 'pipe' });
  } catch {
    // Fall back to docker compose (works when run from project root with COMPOSE_PROJECT_NAME)
    try {
      execSync('docker compose exec -T redis redis-cli FLUSHALL', { stdio: 'pipe' });
    } catch {
      // Redis might not be running via docker, ignore
    }
  }
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface TestUser {
  email: string;
  password: string;
  accessToken: string;
}

/**
 * Generate a unique test email address using timestamp + random suffix.
 */
export function generateTestEmail(): string {
  const rand = Math.random().toString(36).substring(2, 8);
  return `e2e-${Date.now()}-${rand}@example.com`;
}

/**
 * Register a user via the backend API.
 * Retries up to 3 times after flushing Redis if rate-limited (429).
 * Adds a short delay between retries to avoid re-triggering limits
 * when multiple parallel workers are registering simultaneously.
 */
async function registerUser(email: string, password: string): Promise<void> {
  const doRegister = async (): Promise<Response> =>
    fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

  const maxRetries = 3;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await doRegister();

    if (response.status === 429 && attempt < maxRetries) {
      await flushRateLimits();
      await new Promise((resolve) => setTimeout(resolve, 500));
      continue;
    }

    if (!response.ok && response.status !== 202) {
      throw new Error(`Registration failed: ${response.status}`);
    }

    return;
  }
}

/**
 * Verify a user's email via the backend API. Returns auth tokens.
 */
async function verifyUser(token: string): Promise<AuthTokens> {
  const response = await fetch(`${API_URL}/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Verification failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<AuthTokens>;
}

/**
 * Complete a user's profile via the backend API.
 */
async function completeProfile(
  accessToken: string,
  displayName: string,
): Promise<void> {
  const response = await fetch(`${API_URL}/users/me/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ display_name: displayName }),
  });

  if (!response.ok) {
    throw new Error(`Profile completion failed: ${response.status}`);
  }
}

/**
 * Create a verified user via API (register + verify email).
 * Uses MailHog to extract the verification token.
 */
export async function createVerifiedUser(
  password = 'testpass123',
): Promise<TestUser> {
  const email = generateTestEmail();

  await registerUser(email, password);
  const verificationToken = await getVerificationToken(email);

  // Retry verification to handle race condition where the DB commit
  // (from the registration session) hasn't completed yet when we verify.
  const maxRetries = 5;
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(`${API_URL}/auth/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: verificationToken }),
    });

    if (response.ok) {
      const tokens: AuthTokens = await response.json();
      return { email, password, accessToken: tokens.access_token };
    }

    // If 400 with invalid_token, the DB commit may not have landed yet — retry
    if (response.status === 400 && attempt < maxRetries - 1) {
      await new Promise((resolve) => setTimeout(resolve, 200));
      continue;
    }

    const body = await response.text();
    throw new Error(`Verification failed: ${response.status} - ${body}`);
  }

  throw new Error(`Verification failed after ${maxRetries} retries`);
}

/**
 * Create a verified user with a completed profile via API.
 * Ready for login tests that expect the homepage.
 */
export async function createUserWithProfile(
  displayName = 'Test User',
  password = 'testpass123',
): Promise<TestUser> {
  const user = await createVerifiedUser(password);
  await completeProfile(user.accessToken, displayName);
  return user;
}

// ============================================================================
// Community Helpers
// ============================================================================

/**
 * Join the default community (idempotent — safe to call multiple times).
 */
export async function joinCommunity(accessToken: string): Promise<void> {
  const response = await fetch(`${API_URL}/community/join`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Join community failed: ${response.status}`);
  }
}

export interface CreatedPost {
  id: string;
}

/**
 * Create a post via API (for fast test setup).
 */
export async function createPost(
  accessToken: string,
  title: string,
  content: string,
  categoryId?: string,
): Promise<CreatedPost> {
  // If no categoryId provided, fetch the first available category
  if (categoryId === undefined) {
    const cats = await getCategories(accessToken);
    if (cats.length > 0) {
      categoryId = cats[0].id;
    }
  }

  const response = await fetch(`${API_URL}/community/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      title,
      content,
      category_id: categoryId ?? null,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Create post failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<CreatedPost>;
}

export interface CategoryInfo {
  id: string;
  name: string;
  slug: string;
  emoji: string;
}

/**
 * Get categories for the default community.
 */
export async function getCategories(
  accessToken: string,
): Promise<CategoryInfo[]> {
  const response = await fetch(`${API_URL}/community/categories`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Get categories failed: ${response.status}`);
  }

  return response.json() as Promise<CategoryInfo[]>;
}

/**
 * Create a verified user with profile AND community membership.
 * Ready for community E2E tests.
 */
export async function createCommunityMember(
  displayName = 'Test User',
  password = 'testpass123',
): Promise<TestUser> {
  const user = await createUserWithProfile(displayName, password);
  await joinCommunity(user.accessToken);
  return user;
}

/**
 * Like a post via API.
 */
export async function likePost(accessToken: string, postId: string): Promise<void> {
  const response = await fetch(`${API_URL}/community/posts/${postId}/like`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Like post failed: ${response.status}`);
  }
}

/**
 * Add a comment to a post via API.
 */
export async function addComment(
  accessToken: string,
  postId: string,
  content: string,
  parentCommentId?: string,
): Promise<{ comment_id: string }> {
  const response = await fetch(`${API_URL}/community/posts/${postId}/comments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      content,
      parent_comment_id: parentCommentId ?? null,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Add comment failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<{ comment_id: string }>;
}

/**
 * Update a post via API.
 */
export async function updatePost(
  accessToken: string,
  postId: string,
  data: { title?: string; content?: string; category_id?: string },
): Promise<void> {
  const response = await fetch(`${API_URL}/community/posts/${postId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Update post failed: ${response.status} - ${body}`);
  }
}

// ============================================================================
// Classroom Helpers
// ============================================================================

export interface CreatedCourse {
  id: string;
}

/**
 * Create a course via API.
 */
export async function createCourseApi(
  accessToken: string,
  title: string,
  description?: string,
): Promise<CreatedCourse> {
  const response = await fetch(`${API_URL}/courses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ title, description: description ?? null }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Create course failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<CreatedCourse>;
}

/**
 * Add a module to a course via API.
 */
export async function addModuleApi(
  accessToken: string,
  courseId: string,
  title: string,
  description?: string,
): Promise<{ id: string }> {
  const response = await fetch(`${API_URL}/courses/${courseId}/modules`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ title, description: description ?? null }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Add module failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<{ id: string }>;
}

/**
 * Add a lesson to a module via API.
 */
export async function addLessonApi(
  accessToken: string,
  moduleId: string,
  title: string,
  contentType: string,
  content: string,
): Promise<{ id: string }> {
  const response = await fetch(`${API_URL}/modules/${moduleId}/lessons`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ title, content_type: contentType, content }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Add lesson failed: ${response.status} - ${body}`);
  }

  return response.json() as Promise<{ id: string }>;
}

// ============================================================================
// Delete Helpers (for test cleanup)
// ============================================================================

/**
 * Delete a post via API. Best-effort — ignores errors (post may already be deleted).
 */
export async function deletePostApi(accessToken: string, postId: string): Promise<void> {
  try {
    await fetch(`${API_URL}/community/posts/${postId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${accessToken}` },
    });
  } catch {
    // Best-effort cleanup
  }
}

/**
 * Delete a course via API. Best-effort — ignores errors (course may already be deleted).
 */
export async function deleteCourseApi(accessToken: string, courseId: string): Promise<void> {
  try {
    await fetch(`${API_URL}/courses/${courseId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${accessToken}` },
    });
  } catch {
    // Best-effort cleanup
  }
}

// ============================================================================
// Test State Management
// ============================================================================

/**
 * Reset all external services to a clean state.
 * Call this in beforeEach to ensure tests don't interfere with each other.
 *
 * Clears:
 * - Redis rate limits (prevents 429s from accumulated requests)
 * - MailHog emails (prevents stale verification tokens)
 *
 * Runs sequentially — MailHog needs time to settle after clearing
 * before new emails arrive.
 */
export async function cleanTestState(): Promise<void> {
  await flushRateLimits();
  await clearEmails();
  // MailHog needs time to fully process the clear before new emails arrive
  await new Promise((resolve) => setTimeout(resolve, 300));
}
