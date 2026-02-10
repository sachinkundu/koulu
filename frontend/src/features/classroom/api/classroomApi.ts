import { apiClient } from '@/lib/api-client';
import type {
  CourseListResponse,
  CourseDetail,
  CreateCourseRequest,
  AddModuleRequest,
  AddLessonRequest,
} from '../types';

export async function getCourses(): Promise<CourseListResponse> {
  const response = await apiClient.get<CourseListResponse>('/courses');
  return response.data;
}

export async function getCourse(id: string): Promise<CourseDetail> {
  const response = await apiClient.get<CourseDetail>(`/courses/${id}`);
  return response.data;
}

export async function createCourse(data: CreateCourseRequest): Promise<{ id: string }> {
  const response = await apiClient.post<{ id: string }>('/courses', data);
  return response.data;
}

export async function deleteCourse(id: string): Promise<void> {
  await apiClient.delete(`/courses/${id}`);
}

export async function addModule(courseId: string, data: AddModuleRequest): Promise<{ id: string }> {
  const response = await apiClient.post<{ id: string }>(`/courses/${courseId}/modules`, data);
  return response.data;
}

export async function addLesson(moduleId: string, data: AddLessonRequest): Promise<{ id: string }> {
  const response = await apiClient.post<{ id: string }>(`/modules/${moduleId}/lessons`, data);
  return response.data;
}
