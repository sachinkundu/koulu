import { apiClient } from '@/lib/api-client';
import type { SearchQueryParams, SearchResponse } from '../types';

export async function searchCommunity(params: SearchQueryParams): Promise<SearchResponse> {
  const response = await apiClient.get<SearchResponse>('/community/search', { params });
  return response.data;
}
