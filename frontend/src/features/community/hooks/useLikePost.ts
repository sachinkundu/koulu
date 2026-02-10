import { useMutation, useQueryClient } from '@tanstack/react-query';
import { likePost, unlikePost } from '../api';

export function useLikePost(postId: string): {
  like: () => void;
  unlike: () => void;
  isLiking: boolean;
} {
  const queryClient = useQueryClient();

  const invalidate = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['posts'] });
    void queryClient.invalidateQueries({ queryKey: ['post', postId] });
  };

  const likeMutation = useMutation({
    mutationFn: () => likePost(postId),
    onSuccess: invalidate,
  });

  const unlikeMutation = useMutation({
    mutationFn: () => unlikePost(postId),
    onSuccess: invalidate,
  });

  return {
    like: () => likeMutation.mutate(),
    unlike: () => unlikeMutation.mutate(),
    isLiking: likeMutation.isPending || unlikeMutation.isPending,
  };
}
