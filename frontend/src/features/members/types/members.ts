export interface DirectoryMember {
  user_id: string;
  display_name: string | null;
  avatar_url: string | null;
  role: 'admin' | 'moderator' | 'member';
  bio: string | null;
  joined_at: string;
}

export interface MembersQueryParams {
  search?: string;
  role?: 'admin' | 'moderator' | 'member';
  sort?: 'most_recent' | 'alphabetical';
  limit?: number;
  cursor?: string;
}

export interface MembersResponse {
  items: DirectoryMember[];
  total_count: number;
  cursor: string | null;
  has_more: boolean;
}
