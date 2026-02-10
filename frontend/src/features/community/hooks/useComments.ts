import { useQuery } from '@tanstack/react-query';
import { getPostComments } from '../api';
import type { Comment } from '../types';

export function useComments(postId: string): {
  comments: Comment[] | undefined;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery({
    queryKey: ['comments', postId],
    queryFn: () => getPostComments(postId),
    staleTime: 2 * 60 * 1000,
    retry: 1,
    enabled: postId !== '',
  });

  return {
    comments: data,
    isLoading,
    error: error ?? null,
  };
}
