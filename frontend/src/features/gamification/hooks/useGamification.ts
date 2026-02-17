import { useQuery } from '@tanstack/react-query';
import { getMemberLevel, getLevelDefinitions, checkCourseAccess } from '../api/gamificationApi';
import type { MemberLevel, LevelDefinitionsResponse, CourseAccessResponse } from '../types';

export function useMemberLevel(userId: string | undefined) {
  const { data, isLoading, error } = useQuery<MemberLevel>({
    queryKey: ['memberLevel', userId],
    queryFn: () => getMemberLevel(userId!),
    enabled: userId !== undefined,
  });

  return { memberLevel: data, isLoading, error };
}

export function useLevelDefinitions() {
  const { data, isLoading, error } = useQuery<LevelDefinitionsResponse>({
    queryKey: ['levelDefinitions'],
    queryFn: getLevelDefinitions,
  });

  return {
    levels: data?.levels,
    currentUserLevel: data?.current_user_level,
    isLoading,
    error,
  };
}

export function useCourseAccess(courseId: string) {
  const { data, isLoading, error } = useQuery<CourseAccessResponse>({
    queryKey: ['courseAccess', courseId],
    queryFn: () => checkCourseAccess(courseId),
  });

  return { access: data, isLoading, error };
}
