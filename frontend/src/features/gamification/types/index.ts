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
