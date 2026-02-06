/**
 * React Query hooks for profile data.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getOwnProfile, getProfile, getProfileStats, updateProfile } from '../api/profile';
import type { ProfileDetail, StatsResponse, UpdateProfileRequest } from '../types';

const PROFILE_KEY = ['profile'] as const;
const PROFILE_STATS_KEY = ['profileStats'] as const;

export function useProfile(userId?: string): {
  profile: ProfileDetail | undefined;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery<ProfileDetail, Error>({
    queryKey: [...PROFILE_KEY, userId ?? 'me'],
    queryFn: () => (userId !== undefined ? getProfile(userId) : getOwnProfile()),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  return {
    profile: data,
    isLoading,
    error: error ?? null,
  };
}

export function useProfileStats(userId: string): {
  stats: StatsResponse | undefined;
  isLoading: boolean;
} {
  const { data, isLoading } = useQuery<StatsResponse, Error>({
    queryKey: [...PROFILE_STATS_KEY, userId],
    queryFn: () => getProfileStats(userId),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  return {
    stats: data,
    isLoading,
  };
}

export function useUpdateProfile(): {
  mutate: (data: UpdateProfileRequest) => void;
  mutateAsync: (data: UpdateProfileRequest) => Promise<ProfileDetail>;
  isPending: boolean;
  error: Error | null;
} {
  const queryClient = useQueryClient();

  const mutation = useMutation<ProfileDetail, Error, UpdateProfileRequest>({
    mutationFn: updateProfile,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PROFILE_KEY });
      void queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error ?? null,
  };
}
