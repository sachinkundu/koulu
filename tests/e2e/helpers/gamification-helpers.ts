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
