/**
 * Profile API functions.
 */

import { apiClient } from '@/lib/api-client';
import type {
  ActivityChartResponse,
  ActivityResponse,
  ProfileDetail,
  StatsResponse,
  UpdateProfileRequest,
} from '../types';

/**
 * Get a user's profile by ID.
 */
export async function getProfile(userId: string): Promise<ProfileDetail> {
  const response = await apiClient.get<ProfileDetail>(`/users/${userId}/profile`);
  return response.data;
}

/**
 * Get the current user's own profile.
 */
export async function getOwnProfile(): Promise<ProfileDetail> {
  const response = await apiClient.get<ProfileDetail>('/users/me/profile');
  return response.data;
}

/**
 * Update the current user's profile.
 */
export async function updateProfile(data: UpdateProfileRequest): Promise<ProfileDetail> {
  const response = await apiClient.patch<ProfileDetail>('/users/me/profile', data);
  return response.data;
}

/**
 * Get profile statistics.
 */
export async function getProfileStats(userId: string): Promise<StatsResponse> {
  const response = await apiClient.get<StatsResponse>(`/users/${userId}/profile/stats`);
  return response.data;
}

/**
 * Get profile activity feed.
 */
export async function getProfileActivity(userId: string): Promise<ActivityResponse> {
  const response = await apiClient.get<ActivityResponse>(`/users/${userId}/profile/activity`);
  return response.data;
}

/**
 * Get 30-day activity chart data.
 */
export async function getActivityChart(userId: string): Promise<ActivityChartResponse> {
  const response = await apiClient.get<ActivityChartResponse>(
    `/users/${userId}/profile/activity/chart`
  );
  return response.data;
}
