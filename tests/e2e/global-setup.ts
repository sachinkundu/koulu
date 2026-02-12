/**
 * Playwright global setup - runs once before all tests.
 * Truncates E2E database tables, flushes Redis, and clears MailHog emails
 * from previous test runs.
 */

import { execSync } from 'child_process';
import { flushRateLimits } from './helpers/api-helpers';
import { clearEmails } from './helpers/email-helpers';

/**
 * Truncate all user data tables in the E2E database via docker exec psql.
 * Ensures a clean slate even if the previous test run crashed before cleanup.
 */
function truncateTestData(): void {
  const container = process.env.POSTGRES_CONTAINER ?? 'koulu_postgres';
  const dbName = process.env.E2E_DB_NAME ?? 'koulu_e2e';
  try {
    // Truncate user data tables but preserve seed data (communities, categories)
    execSync(
      `docker exec ${container} psql -U koulu -d ${dbName} -c "` +
        `TRUNCATE TABLE ` +
        `reactions, comments, posts, lessons, modules, courses, ` +
        `community_members, ` +
        `verification_tokens, reset_tokens, profiles, users ` +
        `CASCADE;"`,
      { stdio: 'pipe' },
    );
  } catch {
    // Tables may not exist yet (first run before migrations)
  }
}

export default async function globalSetup(): Promise<void> {
  truncateTestData();
  await flushRateLimits();
  await clearEmails();
}
