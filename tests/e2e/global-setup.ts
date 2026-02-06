/**
 * Playwright global setup - runs once before all tests.
 * Flushes Redis to clear rate limits from previous test runs.
 */

import { flushRateLimits } from './helpers/api-helpers';

export default async function globalSetup(): Promise<void> {
  await flushRateLimits();
}
