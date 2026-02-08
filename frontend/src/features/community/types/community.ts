// Community Feed Types

export interface Category {
  id: string;
  community_id: string;
  name: string;
  slug: string;
  emoji: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommunityMember {
  id: string;
  user_id: string;
  community_id: string;
  display_name: string;
  avatar_url: string | null;
  role: 'admin' | 'moderator' | 'member';
  joined_at: string;
}

export interface Post {
  id: string;
  community_id: string;
  category_id: string;
  created_by: string;
  title: string;
  content: string;
  image_url: string | null;
  is_pinned: boolean;
  is_locked: boolean;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  // Aggregates
  like_count: number;
  comment_count: number;
  // Relations
  author?: CommunityMember;
  category?: Category;
  liked_by_current_user?: boolean;
}

export interface CreatePostRequest {
  title: string;
  content: string;
  category_id: string;
  image_url?: string | null;
}

export interface UpdatePostRequest {
  title?: string;
  content?: string;
  category_id?: string;
  image_url?: string | null;
}

export interface PostsQueryParams {
  category_id?: string;
  limit?: number;
  cursor?: string;
}

export interface PostsResponse {
  items: Post[];
  cursor: string | null;
  has_more: boolean;
}
