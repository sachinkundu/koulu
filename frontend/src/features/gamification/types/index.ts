export interface MemberLevel {
  user_id: string;
  level: number;
  level_name: string;
  total_points: number;
  points_to_next_level: number | null;
  is_max_level: boolean;
}

export type PointSource =
  | 'post_created'
  | 'comment_created'
  | 'post_liked'
  | 'comment_liked'
  | 'lesson_completed';

export interface LevelDefinition {
  level: number;
  name: string;
  threshold: number;
  member_percentage: number;
}

export interface LevelDefinitionsResponse {
  levels: LevelDefinition[];
  current_user_level: number;
}

export interface LevelUpdateRequest {
  levels: Array<{
    level: number;
    name: string;
    threshold: number;
  }>;
}

export interface CourseAccessResponse {
  course_id: string;
  has_access: boolean;
  minimum_level: number | null;
  minimum_level_name: string | null;
  current_level: number;
}

export interface SetCourseLevelRequirementRequest {
  minimum_level: number;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  avatar_url: string | null;
  level: number;
  points: number;
}

export interface LeaderboardPeriod {
  entries: LeaderboardEntry[];
  your_rank: LeaderboardEntry | null;
}

export interface LeaderboardsResponse {
  seven_day: LeaderboardPeriod;
  thirty_day: LeaderboardPeriod;
  all_time: LeaderboardPeriod;
  last_updated: string;
}

export interface LeaderboardWidgetResponse {
  entries: LeaderboardEntry[];
  last_updated: string;
}
