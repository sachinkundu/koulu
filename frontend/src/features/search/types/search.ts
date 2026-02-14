export interface MemberSearchItem {
  user_id: string;
  display_name: string | null;
  username: string | null;
  avatar_url: string | null;
  role: 'admin' | 'moderator' | 'member';
  bio: string | null;
  joined_at: string;
}

export interface PostSearchItem {
  id: string;
  title: string;
  body_snippet: string;
  author_name: string | null;
  author_avatar_url: string | null;
  category_name: string | null;
  category_emoji: string | null;
  created_at: string;
  like_count: number;
  comment_count: number;
}

export type SearchType = 'members' | 'posts';

export interface SearchQueryParams {
  q: string;
  type?: SearchType;
  limit?: number;
  offset?: number;
}

export interface SearchResponse {
  items: MemberSearchItem[] | PostSearchItem[];
  total_count: number;
  member_count: number;
  post_count: number;
  has_more: boolean;
}
