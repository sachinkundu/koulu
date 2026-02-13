import { useInfiniteQuery } from '@tanstack/react-query';
import { getPosts } from '../api';
import type { Post, PostsQueryParams } from '../types';

const POSTS_KEY = ['posts'] as const;

export interface UsePostsResult {
  posts: Post[] | undefined;
  isLoading: boolean;
  error: Error | null;
  hasMore: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
}

export function usePosts(params?: PostsQueryParams): UsePostsResult {
  const {
    data,
    isLoading,
    error,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useInfiniteQuery({
    queryKey: [...POSTS_KEY, params],
    queryFn: ({ pageParam }) => {
      const queryParams: PostsQueryParams = { ...params };
      if (pageParam != null) {
        queryParams.cursor = pageParam;
      }
      return getPosts(queryParams);
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.cursor : undefined,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const posts = data?.pages.flatMap((page) => page.items);

  return {
    posts,
    hasMore: hasNextPage ?? false,
    isLoading,
    isFetchingNextPage,
    fetchNextPage: () => void fetchNextPage(),
    error: error ?? null,
  };
}
