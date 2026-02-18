import { useQuery } from '@tanstack/react-query';
import { getLeaderboards } from '../api/gamificationApi';
import type { LeaderboardsResponse } from '../types';

interface UseLeaderboardsResult {
  data: LeaderboardsResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useLeaderboards(): UseLeaderboardsResult {
  const { data, isLoading, error } = useQuery<LeaderboardsResponse>({
    queryKey: ['leaderboards'],
    queryFn: getLeaderboards,
  });

  return { data, isLoading, error };
}
