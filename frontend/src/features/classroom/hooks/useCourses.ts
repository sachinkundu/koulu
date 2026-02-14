import { useQuery } from '@tanstack/react-query';
import { getCourses } from '../api';
import type { Course } from '../types';

export function useCourses(): {
  courses: Course[] | undefined;
  total: number;
  isLoading: boolean;
  error: Error | null;
} {
  const { data, isLoading, error } = useQuery({
    queryKey: ['courses'],
    queryFn: getCourses,
  });

  return {
    courses: data?.courses,
    total: data?.total ?? 0,
    isLoading,
    error,
  };
}
