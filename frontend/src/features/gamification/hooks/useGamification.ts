import { useQuery } from '@tanstack/react-query';
import { getMemberLevel, getLevelDefinitions, checkCourseAccess } from '../api/gamificationApi';
import type { MemberLevel, LevelDefinition, LevelDefinitionsResponse, CourseAccessResponse } from '../types';

interface UseMemberLevelResult {
  memberLevel: MemberLevel | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useMemberLevel(userId: string | undefined): UseMemberLevelResult {
  const { data, isLoading, error } = useQuery<MemberLevel>({
    queryKey: ['memberLevel', userId],
    queryFn: () => getMemberLevel(userId!),
    enabled: userId !== undefined,
  });

  return { memberLevel: data, isLoading, error };
}

interface UseLevelDefinitionsResult {
  levels: LevelDefinition[] | undefined;
  currentUserLevel: number | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useLevelDefinitions(): UseLevelDefinitionsResult {
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

interface UseCourseAccessResult {
  access: CourseAccessResponse | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useCourseAccess(courseId: string): UseCourseAccessResult {
  const { data, isLoading, error } = useQuery<CourseAccessResponse>({
    queryKey: ['courseAccess', courseId],
    queryFn: () => checkCourseAccess(courseId),
  });

  return { access: data, isLoading, error };
}
