/**
 * React Query hook for current user data.
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getCurrentUser } from '../api/user';
import type { User } from '../types';

const CURRENT_USER_KEY = ['currentUser'] as const;

export function useCurrentUser(): {
  user: User | undefined;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
} {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<User, Error>({
    queryKey: CURRENT_USER_KEY,
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const refetch = (): void => {
    void queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY });
  };

  return {
    user: data,
    isLoading,
    error: error ?? null,
    refetch,
  };
}

export function useInvalidateCurrentUser(): () => void {
  const queryClient = useQueryClient();

  return (): void => {
    void queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY });
  };
}
