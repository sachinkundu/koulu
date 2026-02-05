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
