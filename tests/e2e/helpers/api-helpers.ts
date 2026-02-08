import { getVerificationToken } from './email-helpers';

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
    throw new Error(`Verification failed: ${response.status}`);
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
  const tokens = await verifyUser(verificationToken);

  return { email, password, accessToken: tokens.access_token };
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
