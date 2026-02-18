import { apiClient } from '@/lib/api-client';
import type {
  CourseAccessResponse,
  LeaderboardWidgetResponse,
  LeaderboardsResponse,
  LevelDefinitionsResponse,
  LevelUpdateRequest,
  MemberLevel,
  SetCourseLevelRequirementRequest,
} from '../types';

/**
 * Get a member's level and points (auto-resolves community).
 */
export async function getMemberLevel(
  userId: string,
): Promise<MemberLevel> {
  const response = await apiClient.get<MemberLevel>(
    `/community/members/${userId}/level`,
  );
  return response.data;
}

/**
 * Get level definitions (auto-resolves community).
 */
export async function getLevelDefinitions(): Promise<LevelDefinitionsResponse> {
  const response = await apiClient.get<LevelDefinitionsResponse>(
    `/community/levels`,
  );
  return response.data;
}

/**
 * Update level configuration for a community (admin only).
 */
export async function updateLevelConfig(
  communityId: string,
  data: LevelUpdateRequest,
): Promise<void> {
  await apiClient.put(`/communities/${communityId}/levels`, data);
}

/**
 * Check if the current user can access a course based on level requirements (auto-resolves community).
 */
export async function checkCourseAccess(
  courseId: string,
): Promise<CourseAccessResponse> {
  const response = await apiClient.get<CourseAccessResponse>(
    `/community/courses/${courseId}/access`,
  );
  return response.data;
}

/**
 * Set minimum level requirement for a course (admin only).
 */
export async function setCourseLevelRequirement(
  communityId: string,
  courseId: string,
  data: SetCourseLevelRequirementRequest,
): Promise<void> {
  await apiClient.put(
    `/communities/${communityId}/courses/${courseId}/level-requirement`,
    data,
  );
}

/**
 * Get leaderboards for the current community.
 */
export async function getLeaderboards(): Promise<LeaderboardsResponse> {
  const response = await apiClient.get<LeaderboardsResponse>('/community/leaderboards');
  return response.data;
}

/**
 * Get the compact 30-day leaderboard widget for the sidebar.
 */
export async function getLeaderboardWidget(): Promise<LeaderboardWidgetResponse> {
  const response = await apiClient.get<LeaderboardWidgetResponse>('/community/leaderboards/widget');
  return response.data;
}
