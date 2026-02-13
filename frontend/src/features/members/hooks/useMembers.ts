import { useInfiniteQuery } from '@tanstack/react-query';
import { getMembers } from '../api';
import type { DirectoryMember, MembersQueryParams } from '../types';

const MEMBERS_KEY = ['members'] as const;

export interface UseMembersResult {
  members: DirectoryMember[] | undefined;
  totalCount: number;
  isLoading: boolean;
  error: Error | null;
  hasMore: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
}

export function useMembers(params?: MembersQueryParams): UseMembersResult {
  const {
    data,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [...MEMBERS_KEY, params],
    queryFn: ({ pageParam }) => {
      const queryParams: MembersQueryParams = { ...params };
      if (pageParam != null) {
        queryParams.cursor = pageParam;
      }
      return getMembers(queryParams);
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.cursor : undefined,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const members = data?.pages.flatMap((page) => page.items);
  const totalCount = data?.pages[0]?.total_count ?? 0;

  return {
    members,
    totalCount,
    hasMore: hasNextPage ?? false,
    isLoading,
    isFetchingNextPage,
    fetchNextPage: () => void fetchNextPage(),
    error: error ?? null,
  };
}
