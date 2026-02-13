/**
 * Playwright global setup - runs once before all tests.
 * Cleans up leftover E2E test data, flushes Redis, and clears MailHog emails
 * from previous test runs.
 */

import { flushRateLimits } from './helpers/api-helpers';
import { cleanupE2eUsers } from './helpers/db-cleanup';
import { clearEmails } from './helpers/email-helpers';

export default async function globalSetup(): Promise<void> {
  cleanupE2eUsers();
  await flushRateLimits();
  await clearEmails();
}
