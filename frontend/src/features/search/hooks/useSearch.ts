import { useQuery } from '@tanstack/react-query';
import { searchCommunity } from '../api';
import type { SearchResponse, SearchType } from '../types';

const SEARCH_KEY = ['search'] as const;

export interface UseSearchResult {
  data: SearchResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useSearch(
  query: string,
  type?: SearchType,
  limit?: number,
  offset?: number,
): UseSearchResult {
  const trimmedQuery = query.trim();

  const { data, isLoading, error } = useQuery({
    queryKey: [...SEARCH_KEY, trimmedQuery, type, limit, offset],
    queryFn: () => searchCommunity({ q: trimmedQuery, type, limit, offset }),
    enabled: trimmedQuery.length >= 3,
    staleTime: 30 * 1000, // 30 seconds
    retry: 1,
  });

  return {
    data,
    isLoading,
    error: error ?? null,
  };
}
