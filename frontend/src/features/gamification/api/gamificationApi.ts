import { apiClient } from '@/lib/api-client';
import type { MemberLevel } from '../types';

/**
 * Get a member's level and points in a community.
 */
export async function getMemberLevel(
  communityId: string,
  userId: string,
): Promise<MemberLevel> {
  const response = await apiClient.get<MemberLevel>(
    `/api/communities/${communityId}/members/${userId}/level`,
  );
  return response.data;
}
