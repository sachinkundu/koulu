export interface Lesson {
  id: string;
  title: string;
  content_type: string;
  content?: string;
  position: number;
  is_complete?: boolean;
  created_at: string;
  updated_at: string;
}

export interface Module {
  id: string;
  title: string;
  description: string | null;
  position: number;
  lesson_count: number;
  completion_percentage?: number | null;
  lessons: Lesson[];
  created_at: string;
  updated_at: string;
}

export interface ProgressSummary {
  started: boolean;
  completion_percentage: number;
  last_accessed_lesson_id: string | null;
  next_incomplete_lesson_id: string | null;
}

export interface Course {
  id: string;
  instructor_id: string;
  title: string;
  description: string | null;
  cover_image_url: string | null;
  estimated_duration: string | null;
  module_count: number;
  lesson_count: number;
  progress?: ProgressSummary | null;
  created_at: string;
  updated_at: string;
}

export interface CourseDetail extends Course {
  modules: Module[];
}

export interface CourseListResponse {
  courses: Course[];
  total: number;
}

export interface CreateCourseRequest {
  title: string;
  description?: string | null;
  cover_image_url?: string | null;
  estimated_duration?: string | null;
}

export interface UpdateCourseRequest {
  title?: string;
  description?: string | null;
  cover_image_url?: string | null;
  estimated_duration?: string | null;
}

export interface AddModuleRequest {
  title: string;
  description?: string | null;
}

export interface AddLessonRequest {
  title: string;
  content_type: string;
  content: string;
}

export interface LessonContext {
  id: string;
  title: string;
  content_type: string;
  content: string;
  position: number;
  is_complete: boolean;
  next_lesson_id: string | null;
  prev_lesson_id: string | null;
  module_title: string;
  course_id: string;
  course_title: string;
}

export interface StartCourseResponse {
  progress_id: string;
  first_lesson_id: string;
}

export interface NextLessonResponse {
  lesson_id: string;
}

export interface ProgressDetail {
  user_id: string;
  course_id: string;
  started_at: string;
  completion_percentage: number;
  completed_lesson_ids: string[];
  next_incomplete_lesson_id: string | null;
  last_accessed_lesson_id: string | null;
}

export interface UpdateLessonRequest {
  title?: string;
  content_type?: string;
  content?: string;
}

export interface MessageResponse {
  message: string;
}
