/**
 * Playwright global teardown - runs once after all tests complete.
 * Removes E2E test users so they don't pollute the dev database.
 */

import { cleanupE2eUsers } from './helpers/db-cleanup';

export default async function globalTeardown(): Promise<void> {
  cleanupE2eUsers();
}
