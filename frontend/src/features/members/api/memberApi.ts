import { apiClient } from '@/lib/api-client';
import type { MembersQueryParams, MembersResponse } from '../types';

export async function getMembers(params?: MembersQueryParams): Promise<MembersResponse> {
  const response = await apiClient.get<MembersResponse>('/community/members', { params });
  return response.data;
}
