import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addComment } from '../api';

export function useAddComment(postId: string): {
  mutateAsync: (data: { content: string; parent_comment_id?: string | null }) => Promise<{ comment_id: string }>;
  isPending: boolean;
  error: Error | null;
} {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: { content: string; parent_comment_id?: string | null }) =>
      addComment(postId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['comments', postId] });
      void queryClient.invalidateQueries({ queryKey: ['posts'] });
      void queryClient.invalidateQueries({ queryKey: ['post', postId] });
    },
  });

  return {
    mutateAsync: mutation.mutateAsync,
    isPending: mutation.isPending,
    error: mutation.error ?? null,
  };
}
