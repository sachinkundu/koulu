import { useMutation, useQueryClient } from '@tanstack/react-query';
import { markLessonComplete, unmarkLessonComplete } from '../api';

export function useLessonComplete(lessonId: string, courseId: string): {
  markComplete: () => void;
  unmarkComplete: () => void;
  isMarkPending: boolean;
  isUnmarkPending: boolean;
  error: Error | null;
} {
  const queryClient = useQueryClient();

  const invalidateQueries = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['lesson', lessonId] });
    void queryClient.invalidateQueries({ queryKey: ['course', courseId] });
    void queryClient.invalidateQueries({ queryKey: ['courseProgress', courseId] });
    void queryClient.invalidateQueries({ queryKey: ['courses'] });
  };

  const markMutation = useMutation({
    mutationFn: () => markLessonComplete(lessonId),
    onSuccess: invalidateQueries,
  });

  const unmarkMutation = useMutation({
    mutationFn: () => unmarkLessonComplete(lessonId),
    onSuccess: invalidateQueries,
  });

  return {
    markComplete: () => markMutation.mutate(),
    unmarkComplete: () => unmarkMutation.mutate(),
    isMarkPending: markMutation.isPending,
    isUnmarkPending: unmarkMutation.isPending,
    error: markMutation.error ?? unmarkMutation.error,
  };
}
