/**
 * Targeted E2E test data cleanup.
 *
 * Deletes only users created by E2E tests (identified by `e2e-` email prefix)
 * and their associated data. Runs against the koulu_e2e database (never dev).
 */

import { execSync } from 'child_process';
import { E2E_DB_NAME, POSTGRES_CONTAINER } from './env';

/**
 * Delete all E2E-created users and their associated data from the database.
 * Uses `e2e-` email prefix to identify test users (see generateTestEmail()).
 */
export function cleanupE2eUsers(): void {
  const container = POSTGRES_CONTAINER;
  const dbName = E2E_DB_NAME;
  try {
    execSync(
      `docker exec ${container} psql -U koulu -d ${dbName} -c "` +
        `DELETE FROM reactions WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM comments WHERE author_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM posts WHERE author_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM community_members WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM verification_tokens WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM reset_tokens WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM profiles WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'e2e-%'); ` +
        `DELETE FROM users WHERE email LIKE 'e2e-%'; ` +
        `"`,
      { stdio: 'pipe' },
    );
  } catch {
    // Tables may not exist yet (first run before migrations)
  }
}
