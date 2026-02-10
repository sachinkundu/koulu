import { apiClient } from '@/lib/api-client';
import type {
  Post,
  CreatePostRequest,
  UpdatePostRequest,
  PostsQueryParams,
  PostsResponse,
  Category,
  Comment,
  AddCommentRequest,
  EditCommentRequest,
} from '../types';

/**
 * Get list of posts with optional filtering and pagination
 */
export async function getPosts(params?: PostsQueryParams): Promise<PostsResponse> {
  const response = await apiClient.get<PostsResponse>('/community/posts', { params });
  return response.data;
}

/**
 * Get a single post by ID
 */
export async function getPost(id: string): Promise<Post> {
  const response = await apiClient.get<Post>(`/community/posts/${id}`);
  return response.data;
}

/**
 * Create a new post
 */
export async function createPost(data: CreatePostRequest): Promise<Post> {
  const response = await apiClient.post<Post>('/community/posts', data);
  return response.data;
}

/**
 * Update an existing post
 */
export async function updatePost(id: string, data: UpdatePostRequest): Promise<Post> {
  const response = await apiClient.patch<Post>(`/community/posts/${id}`, data);
  return response.data;
}

/**
 * Delete a post
 */
export async function deletePost(id: string): Promise<void> {
  await apiClient.delete(`/community/posts/${id}`);
}

/**
 * Get all categories for the community
 */
export async function getCategories(): Promise<Category[]> {
  const response = await apiClient.get<Category[]>('/community/categories');
  return response.data;
}

// ============================================================================
// Post Likes
// ============================================================================

export async function likePost(postId: string): Promise<void> {
  await apiClient.post(`/community/posts/${postId}/like`);
}

export async function unlikePost(postId: string): Promise<void> {
  await apiClient.delete(`/community/posts/${postId}/like`);
}

// ============================================================================
// Comments
// ============================================================================

export async function getPostComments(postId: string): Promise<Comment[]> {
  const response = await apiClient.get<Comment[]>(`/community/posts/${postId}/comments`);
  return response.data;
}

export async function addComment(postId: string, data: AddCommentRequest): Promise<{ comment_id: string }> {
  const response = await apiClient.post<{ comment_id: string }>(`/community/posts/${postId}/comments`, data);
  return response.data;
}

export async function editComment(commentId: string, data: EditCommentRequest): Promise<void> {
  await apiClient.patch(`/community/comments/${commentId}`, data);
}

export async function deleteComment(commentId: string): Promise<void> {
  await apiClient.delete(`/community/comments/${commentId}`);
}

export async function likeComment(commentId: string): Promise<void> {
  await apiClient.post(`/community/comments/${commentId}/like`);
}

export async function unlikeComment(commentId: string): Promise<void> {
  await apiClient.delete(`/community/comments/${commentId}/like`);
}
