/**
 * Playwright global setup - runs once before all tests.
 * Flushes Redis to clear rate limits and clears MailHog emails
 * from previous test runs.
 */

import { flushRateLimits } from './helpers/api-helpers';
import { clearEmails } from './helpers/email-helpers';

export default async function globalSetup(): Promise<void> {
  await flushRateLimits();
  await clearEmails();
}
