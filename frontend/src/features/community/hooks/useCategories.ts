import { useQuery } from '@tanstack/react-query';
import { getCategories } from '../api';
import type { Category } from '../types';

const CATEGORIES_KEY = ['categories'] as const;

export interface UseCategoriesResult {
  categories: Category[] | undefined;
  isLoading: boolean;
  error: Error | null;
}

export function useCategories(): UseCategoriesResult {
  const { data, isLoading, error } = useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: getCategories,
    staleTime: 10 * 60 * 1000, // 10 minutes (categories change infrequently)
    retry: 1,
  });

  return {
    categories: data,
    isLoading,
    error: error ?? null,
  };
}
