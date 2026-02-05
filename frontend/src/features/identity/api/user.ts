/**
 * User API functions.
 */

import { apiClient } from '@/lib/api-client';
import type { CompleteProfileRequest, Profile, User } from '../types';

/**
 * Get current authenticated user.
 */
export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/users/me');
  return response.data;
}

/**
 * Complete or update user profile.
 */
export async function completeProfile(data: CompleteProfileRequest): Promise<Profile> {
  const response = await apiClient.put<Profile>('/users/me/profile', data);
  return response.data;
}
