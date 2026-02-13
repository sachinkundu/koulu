/**
 * Central environment variable validation for E2E tests.
 *
 * Required variables (no fallback — forces use of run-e2e-tests.sh):
 *   BASE_URL, API_URL, MAILHOG_URL
 *
 * Optional variables (safe defaults that never hit dev):
 *   REDIS_CONTAINER, POSTGRES_CONTAINER, E2E_DB_NAME
 */

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `Missing required environment variable: ${name}\n\n` +
        `E2E tests must be run via the isolated test runner:\n` +
        `  ./scripts/run-e2e-tests.sh\n\n` +
        `This script creates a separate database and starts servers on\n` +
        `dedicated ports so E2E tests never touch the dev environment.\n\n` +
        `To run a specific test file:\n` +
        `  ./scripts/run-e2e-tests.sh specs/identity/login.spec.ts`,
    );
  }
  return value;
}

/** Frontend URL (e.g. http://localhost:5273) — set by run-e2e-tests.sh */
export const BASE_URL: string = requireEnv('BASE_URL');

/** Backend API URL (e.g. http://localhost:8100/api/v1) — set by run-e2e-tests.sh */
export const API_URL: string = requireEnv('API_URL');

/** MailHog web UI URL (e.g. http://localhost:8025) — set by run-e2e-tests.sh */
export const MAILHOG_URL: string = requireEnv('MAILHOG_URL');

/** Docker container name for Redis (safe default) */
export const REDIS_CONTAINER: string =
  process.env.REDIS_CONTAINER ?? 'koulu_redis';

/** Docker container name for PostgreSQL (safe default) */
export const POSTGRES_CONTAINER: string =
  process.env.POSTGRES_CONTAINER ?? 'koulu_postgres';

/** E2E database name — always koulu_e2e, never the dev database */
export const E2E_DB_NAME: string =
  process.env.E2E_DB_NAME ?? 'koulu_e2e';
