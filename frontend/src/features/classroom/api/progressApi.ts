import { apiClient } from '@/lib/api-client';
import type {
  LessonContext,
  StartCourseResponse,
  NextLessonResponse,
  ProgressDetail,
  MessageResponse,
} from '../types';

export async function getLesson(lessonId: string): Promise<LessonContext> {
  const response = await apiClient.get<LessonContext>(`/lessons/${lessonId}`);
  return response.data;
}

export async function startCourse(courseId: string): Promise<StartCourseResponse> {
  const response = await apiClient.post<StartCourseResponse>(`/courses/${courseId}/start`);
  return response.data;
}

export async function getContinueLesson(courseId: string): Promise<NextLessonResponse> {
  const response = await apiClient.get<NextLessonResponse>(`/courses/${courseId}/continue`);
  return response.data;
}

export async function getCourseProgress(courseId: string): Promise<ProgressDetail> {
  const response = await apiClient.get<ProgressDetail>(`/progress/courses/${courseId}`);
  return response.data;
}

export async function markLessonComplete(lessonId: string): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>(`/progress/lessons/${lessonId}/complete`);
  return response.data;
}

export async function unmarkLessonComplete(lessonId: string): Promise<void> {
  await apiClient.delete(`/progress/lessons/${lessonId}/complete`);
}
