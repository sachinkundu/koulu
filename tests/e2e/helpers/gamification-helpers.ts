import { API_URL, POSTGRES_CONTAINER, E2E_DB_NAME } from './env';

export interface MemberLevelInfo {
  user_id: string;
  level: number;
  level_name: string;
  total_points: number;
  points_to_next_level: number | null;
  is_max_level: boolean;
}

/**
 * Get the current user's ID from the /users/me endpoint.
 */
export async function getUserId(accessToken: string): Promise<string> {
  const response = await fetch(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Get user failed: ${response.status}`);
  }

  const data = (await response.json()) as { id: string };
  return data.id;
}

/**
 * Get a member's level and points via the auto-resolving API.
 */
export async function getMemberLevel(
  accessToken: string,
  userId: string,
): Promise<MemberLevelInfo> {
  const response = await fetch(`${API_URL}/community/members/${userId}/level`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Get member level failed: ${response.status}`);
  }

  return response.json() as Promise<MemberLevelInfo>;
}

/**
 * Get the default community ID via direct DB query.
 * Uses docker exec psql against the E2E database.
 */
export function getCommunityId(accessToken: string): Promise<string> {
  // Use the levels endpoint to get data, but we need the community ID
  // for admin operations. Easiest: query DB directly.
  const { execSync } = require('child_process');
  const sql = `SELECT id FROM communities ORDER BY created_at LIMIT 1`;
  const result = execSync(
    `docker exec ${POSTGRES_CONTAINER} psql -U koulu -d ${E2E_DB_NAME} -t -c "${sql}"`,
    { encoding: 'utf-8' },
  ).trim();
  return Promise.resolve(result);
}

// ============================================================================
// Leaderboard Helpers
// ============================================================================

export interface LeaderboardEntry {
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  level: number;
  rank: number;
  points: number;
}

export interface LeaderboardPeriod {
  entries: LeaderboardEntry[];
  your_rank: LeaderboardEntry | null;
}

export interface LeaderboardsData {
  seven_day: LeaderboardPeriod;
  thirty_day: LeaderboardPeriod;
  all_time: LeaderboardPeriod;
  last_updated: string;
}

/**
 * Fetch leaderboards data via the auto-resolving API.
 */
export async function getLeaderboards(
  accessToken: string,
): Promise<LeaderboardsData> {
  const response = await fetch(`${API_URL}/community/leaderboards`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error(`Get leaderboards failed: ${response.status}`);
  }

  return response.json() as Promise<LeaderboardsData>;
}

/**
 * Award points to a member by upserting member_points and inserting a point_transaction.
 * This is faster than creating posts/likes for test setup.
 * Uses stdin to avoid shell escaping issues with $$ dollar-quoting.
 */
export function awardPointsViaDb(
  userId: string,
  communityId: string,
  points: number,
  source = 'e2e_test',
): void {
  const { execSync } = require('child_process');
  const sql = [
    `DO $$`,
    `DECLARE mp_id UUID;`,
    `BEGIN`,
    `INSERT INTO member_points (id, community_id, user_id, total_points, current_level, created_at, updated_at)`,
    `VALUES (gen_random_uuid(), '${communityId}', '${userId}', ${points}, 1, NOW(), NOW())`,
    `ON CONFLICT (community_id, user_id)`,
    `DO UPDATE SET total_points = member_points.total_points + ${points}, updated_at = NOW()`,
    `RETURNING id INTO mp_id;`,
    `INSERT INTO point_transactions (id, member_points_id, points, source, source_id, created_at)`,
    `VALUES (gen_random_uuid(), mp_id, ${points}, '${source}', gen_random_uuid(), NOW());`,
    `END $$;`,
  ].join(' ');
  execSync(
    `docker exec -i ${POSTGRES_CONTAINER} psql -U koulu -d ${E2E_DB_NAME}`,
    { input: sql, stdio: ['pipe', 'pipe', 'pipe'] },
  );
}

/**
 * Set a course's minimum level requirement (admin only).
 * Uses the community-scoped endpoint (not auto-resolving) since we need community_id.
 */
export async function setCourseLevelRequirement(
  accessToken: string,
  communityId: string,
  courseId: string,
  minimumLevel: number,
): Promise<void> {
  const response = await fetch(
    `${API_URL}/communities/${communityId}/courses/${courseId}/level-requirement`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ minimum_level: minimumLevel }),
    },
  );

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Set course level requirement failed: ${response.status} - ${body}`);
  }
}
