import { useMutation, useQueryClient } from '@tanstack/react-query';
import { startCourse } from '../api';
import type { StartCourseResponse } from '../types';

export function useStartCourse(courseId: string): {
  start: () => void;
  data: StartCourseResponse | undefined;
  isPending: boolean;
  error: Error | null;
} {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => startCourse(courseId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['courses'] });
      void queryClient.invalidateQueries({ queryKey: ['course', courseId] });
    },
  });

  return {
    start: () => mutation.mutate(),
    data: mutation.data,
    isPending: mutation.isPending,
    error: mutation.error,
  };
}
