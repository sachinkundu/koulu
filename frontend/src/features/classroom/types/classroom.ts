export interface Lesson {
  id: string;
  title: string;
  content_type: string;
  content?: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Module {
  id: string;
  title: string;
  description: string | null;
  position: number;
  lesson_count: number;
  lessons: Lesson[];
  created_at: string;
  updated_at: string;
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
