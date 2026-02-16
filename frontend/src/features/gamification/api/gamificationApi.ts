import { apiClient } from '@/lib/api-client';
import type {
  CourseAccessResponse,
  LevelDefinitionsResponse,
  LevelUpdateRequest,
  MemberLevel,
  SetCourseLevelRequirementRequest,
} from '../types';

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

/**
 * Get level definitions for a community.
 */
export async function getLevelDefinitions(
  communityId: string,
): Promise<LevelDefinitionsResponse> {
  const response = await apiClient.get<LevelDefinitionsResponse>(
    `/api/communities/${communityId}/levels`,
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
  await apiClient.put(`/api/communities/${communityId}/levels`, data);
}

/**
 * Check if a member can access a course based on level requirements.
 */
export async function checkCourseAccess(
  communityId: string,
  courseId: string,
): Promise<CourseAccessResponse> {
  const response = await apiClient.get<CourseAccessResponse>(
    `/api/communities/${communityId}/courses/${courseId}/access`,
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
    `/api/communities/${communityId}/courses/${courseId}/level-requirement`,
    data,
  );
}
