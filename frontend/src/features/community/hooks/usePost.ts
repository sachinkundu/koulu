import { useQuery } from '@tanstack/react-query';
import { getPost } from '../api';
import type { Post } from '../types';

const POST_KEY = ['post'] as const;

export interface UsePostResult {
  post: Post | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function usePost(id: string): UsePostResult {
  const { data, isLoading, error } = useQuery({
    queryKey: [...POST_KEY, id],
    queryFn: () => getPost(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
    enabled: Boolean(id),
  });

  return {
    post: data,
    isLoading,
    error: error ?? null,
  };
}
