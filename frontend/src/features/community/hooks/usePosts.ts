import { useQuery } from '@tanstack/react-query';
import { getPosts } from '../api';
import type { Post, PostsQueryParams } from '../types';

const POSTS_KEY = ['posts'] as const;

export interface UsePostsResult {
  posts: Post[] | undefined;
  isLoading: boolean;
  error: Error | null;
  cursor: string | null | undefined;
  hasMore: boolean | undefined;
}

export function usePosts(params?: PostsQueryParams): UsePostsResult {
  const { data, isLoading, error } = useQuery({
    queryKey: [...POSTS_KEY, params],
    queryFn: () => getPosts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  return {
    posts: data?.items,
    cursor: data?.cursor,
    hasMore: data?.has_more,
    isLoading,
    error: error ?? null,
  };
}
