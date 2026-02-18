import { useQuery } from '@tanstack/react-query';
import { getLeaderboardWidget } from '../api/gamificationApi';
import type { LeaderboardWidgetResponse } from '../types';

interface UseLeaderboardWidgetResult {
  data: LeaderboardWidgetResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useLeaderboardWidget(): UseLeaderboardWidgetResult {
  const { data, isLoading, error } = useQuery<LeaderboardWidgetResponse>({
    queryKey: ['leaderboard-widget'],
    queryFn: getLeaderboardWidget,
  });

  return { data, isLoading, error };
}
