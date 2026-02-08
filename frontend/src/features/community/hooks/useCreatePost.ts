import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createPost } from '../api';
import type { Post, CreatePostRequest } from '../types';

export interface UseCreatePostResult {
  mutate: (data: CreatePostRequest) => void;
  mutateAsync: (data: CreatePostRequest) => Promise<Post>;
  isPending: boolean;
  error: Error | null;
}

export function useCreatePost(): UseCreatePostResult {
  const queryClient = useQueryClient();

  const mutation = useMutation<Post, Error, CreatePostRequest>({
    mutationFn: createPost,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });

  return {
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error ?? null,
  };
}
