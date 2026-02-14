import { useQuery } from '@tanstack/react-query';
import { getCourseProgress } from '../api';
import type { ProgressDetail } from '../types';

export function useCourseProgress(courseId: string): {
  progress: ProgressDetail | undefined;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery({
    queryKey: ['courseProgress', courseId],
    queryFn: () => getCourseProgress(courseId),
    enabled: Boolean(courseId),
  });

  return {
    progress: data,
    isLoading,
    error,
  };
}
