import { useQuery } from '@tanstack/react-query';
import { getCourse } from '../api';
import type { CourseDetail } from '../types';

export function useCourse(courseId: string): {
  course: CourseDetail | undefined;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery({
    queryKey: ['course', courseId],
    queryFn: () => getCourse(courseId),
    enabled: courseId !== '',
  });

  return {
    course: data,
    isLoading,
    error,
  };
}
