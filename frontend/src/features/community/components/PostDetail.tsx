import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { Post } from '../types';
import { deletePost } from '../api';

interface PostDetailProps {
  post: Post;
  currentUserId?: string;
}

export function PostDetail({ post, currentUserId }: PostDetailProps): JSX.Element {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const canEdit = currentUserId !== undefined && post.created_by === currentUserId;

  const deleteMutation = useMutation({
    mutationFn: () => deletePost(post.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['posts'] });
      navigate('/community');
    },
    onError: (error: Error) => {
      setDeleteError(error.message ?? 'Failed to delete post');
      setIsDeleting(false);
    },
  });

  const handleDelete = (): void => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }
    setIsDeleting(true);
    setDeleteError(null);
    deleteMutation.mutate();
  };

  return (
    <div className="rounded-lg bg-white p-6 shadow" data-testid="post-detail">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {/* Author avatar */}
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium text-lg">
            {post.author?.display_name?.[0]?.toUpperCase() ?? 'U'}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">
                {post.author?.display_name ?? 'Unknown'}
              </span>
              {post.is_edited && (
                <span className="text-sm text-gray-500">(edited)</span>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <time dateTime={post.created_at}>
                {new Date(post.created_at).toLocaleString()}
              </time>
            </div>
          </div>
        </div>

        {/* Category badge */}
        {post.category !== undefined && (
          <div className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1.5">
            <span>{post.category.emoji}</span>
            <span className="text-sm text-gray-700">{post.category.name}</span>
          </div>
        )}
      </div>

      {/* Pinned indicator */}
      {post.is_pinned && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-primary-50 px-4 py-2 text-sm font-medium text-primary-700">
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a.75.75 0 01.75.75v7.5h3.5a.75.75 0 010 1.5h-3.5v5.5a.75.75 0 01-1.5 0v-5.5h-3.5a.75.75 0 010-1.5h3.5v-7.5A.75.75 0 0110 2z" />
          </svg>
          <span>Pinned Post</span>
        </div>
      )}

      {/* Locked indicator */}
      {post.is_locked && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
          <span>Comments are disabled</span>
        </div>
      )}

      {/* Post title */}
      <h1 className="mb-4 text-2xl font-bold text-gray-900">{post.title}</h1>

      {/* Post content */}
      <div className="mb-6 text-gray-700 whitespace-pre-wrap">{post.content}</div>

      {/* Image */}
      {post.image_url !== null && (
        <div className="mb-6">
          <img
            src={post.image_url}
            alt=""
            className="w-full rounded-lg"
          />
        </div>
      )}

      {/* Engagement stats */}
      <div className="mb-6 flex items-center gap-6 border-t pt-4 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
            />
          </svg>
          <span>{post.like_count} likes</span>
        </div>

        <div className="flex items-center gap-2">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span>{post.comment_count} comments</span>
        </div>
      </div>

      {/* Actions (if user owns the post) */}
      {canEdit && (
        <div className="border-t pt-4">
          {deleteError !== null && (
            <div className="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
              {deleteError}
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/community/posts/${post.id}/edit`)}
              className="rounded-md bg-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-300"
              data-testid="post-edit-button"
            >
              Edit
            </button>

            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              data-testid="post-delete-button"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
