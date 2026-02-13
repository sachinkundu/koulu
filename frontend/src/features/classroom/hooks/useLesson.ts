import { useQuery } from '@tanstack/react-query';
import { getLesson } from '../api';
import type { LessonContext } from '../types';

export function useLesson(lessonId: string): {
  lesson: LessonContext | undefined;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => getLesson(lessonId),
    enabled: Boolean(lessonId),
  });

  return {
    lesson: data,
    isLoading,
    error: error as Error | null,
  };
}
