import { getVerificationToken } from './email-helpers';

const API_URL = process.env.API_URL ?? 'http://localhost:8000/api/v1';

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
 */
async function registerUser(email: string, password: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok && response.status !== 202) {
    throw new Error(`Registration failed: ${response.status}`);
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
