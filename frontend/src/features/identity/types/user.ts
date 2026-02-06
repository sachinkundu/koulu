/**
 * User and Profile types for the Identity context.
 */

export interface Profile {
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  is_complete: boolean;
}

export interface User {
  id: string;
  email: string;
  is_verified: boolean;
  is_active: boolean;
  profile: Profile | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileDetail {
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  location_city: string | null;
  location_country: string | null;
  twitter_url: string | null;
  linkedin_url: string | null;
  instagram_url: string | null;
  website_url: string | null;
  is_complete: boolean;
  is_own_profile: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  display_name?: string | null;
  avatar_url?: string | null;
  bio?: string | null;
  city?: string | null;
  country?: string | null;
  twitter_url?: string | null;
  linkedin_url?: string | null;
  instagram_url?: string | null;
  website_url?: string | null;
}

export interface StatsResponse {
  contribution_count: number;
  joined_at: string;
}

export interface ActivityItem {
  id: string;
  type: string;
  content: string;
  created_at: string;
}

export interface ActivityResponse {
  items: ActivityItem[];
  total_count: number;
}

export interface ActivityChartResponse {
  days: string[];
  counts: number[];
}
