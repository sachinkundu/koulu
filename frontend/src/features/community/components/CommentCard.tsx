import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Avatar } from '@/components';
import { timeAgo } from '@/lib/timeAgo';
import type { Comment } from '../types';
import { editComment, deleteComment, likeComment, unlikeComment } from '../api';
import { AddCommentForm } from './AddCommentForm';

interface CommentCardProps {
  comment: Comment;
  postId: string;
  currentUserId?: string;
  isLocked: boolean;
  depth?: number;
}

export function CommentCard({
  comment,
  postId,
  currentUserId,
  isLocked,
  depth = 0,
}: CommentCardProps): JSX.Element {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [isReplying, setIsReplying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthor = currentUserId !== undefined && comment.author_id === currentUserId;
  const maxDepth = 3;

  const invalidateComments = (): void => {
    void queryClient.invalidateQueries({ queryKey: ['comments', postId] });
    void queryClient.invalidateQueries({ queryKey: ['posts'] });
    void queryClient.invalidateQueries({ queryKey: ['post', postId] });
  };

  const editMutation = useMutation({
    mutationFn: () => editComment(comment.id, { content: editContent.trim() }),
    onSuccess: () => {
      setIsEditing(false);
      invalidateComments();
    },
    onError: () => setError('Failed to edit comment.'),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteComment(comment.id),
    onSuccess: () => {
      invalidateComments();
    },
    onError: () => setError('Failed to delete comment.'),
  });

  const likeMutation = useMutation({
    mutationFn: () => likeComment(comment.id),
    onSuccess: () => {
      invalidateComments();
    },
  });

  const unlikeMutation = useMutation({
    mutationFn: () => unlikeComment(comment.id),
    onSuccess: () => {
      invalidateComments();
    },
  });

  const handleDelete = (): void => {
    if (!window.confirm('Delete this comment?')) return;
    deleteMutation.mutate();
  };

  const handleEditSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (editContent.trim() === '') return;
    editMutation.mutate();
  };

  if (comment.is_deleted) {
    return (
      <div
        className="py-2 text-sm italic text-gray-400"
        style={{ marginLeft: depth * 32 }}
        data-testid={`comment-${comment.id}`}
      >
        [deleted]
      </div>
    );
  }

  return (
    <div
      className="py-2"
      style={{ marginLeft: depth * 32 }}
      data-testid={`comment-${comment.id}`}
    >
      {error !== null && (
        <div className="mb-2 rounded-md bg-red-50 p-2 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      <div className="flex items-start gap-2.5">
        <Avatar
          src={comment.author?.avatar_url}
          alt={comment.author?.display_name ?? 'Unknown'}
          fallback={comment.author?.display_name ?? 'Unknown'}
          size={depth > 0 ? 'xs' : 'sm'}
        />

        <div className="min-w-0 flex-1">
          {/* Comment bubble */}
          <div className="rounded-lg bg-gray-50 px-3 py-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-gray-900">
                {comment.author?.display_name ?? 'Unknown'}
              </span>
              <time dateTime={comment.created_at} className="text-xs text-gray-400">
                {timeAgo(comment.created_at)}
              </time>
              {comment.is_edited && (
                <span className="text-xs text-gray-400">· edited</span>
              )}
            </div>

            {isEditing ? (
              <form onSubmit={handleEditSubmit} className="mt-1.5" data-testid="edit-comment-form">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={2}
                  maxLength={2000}
                  className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  data-testid="edit-comment-input"
                />
                <div className="mt-1.5 flex gap-2">
                  <button
                    type="submit"
                    disabled={editMutation.isPending || editContent.trim() === ''}
                    className="rounded-md bg-gray-900 px-3 py-1 text-xs font-medium text-white hover:bg-gray-800 disabled:opacity-50"
                    data-testid="edit-comment-save"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => { setIsEditing(false); setEditContent(comment.content); }}
                    className="rounded-md px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <p className="mt-0.5 whitespace-pre-wrap text-sm text-gray-700">{comment.content}</p>
            )}
          </div>

          {/* Actions row */}
          <div className="mt-1 flex items-center gap-3 px-1">
            <button
              onClick={() => likeMutation.isPending || unlikeMutation.isPending ? undefined : (comment.like_count > 0 ? unlikeMutation.mutate() : likeMutation.mutate())}
              className="flex items-center gap-1 text-xs text-gray-400 transition-colors hover:text-gray-600"
              data-testid="comment-like-button"
            >
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
              {comment.like_count > 0 && <span>{comment.like_count}</span>}
            </button>

            {!isLocked && depth < maxDepth && (
              <button
                onClick={() => setIsReplying(!isReplying)}
                className="text-xs text-gray-400 transition-colors hover:text-gray-600"
                data-testid="comment-reply-button"
              >
                Reply
              </button>
            )}

            {isAuthor && !isEditing && (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-xs text-gray-400 transition-colors hover:text-gray-600"
                  data-testid="comment-edit-button"
                >
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                  className="text-xs text-gray-400 transition-colors hover:text-red-500 disabled:opacity-50"
                  data-testid="comment-delete-button"
                >
                  Delete
                </button>
              </>
            )}
          </div>

          {/* Reply form */}
          {isReplying && !isLocked && (
            <div className="mt-2">
              <AddCommentForm
                postId={postId}
                parentCommentId={comment.id}
                placeholder="Write a reply..."
                onSuccess={() => setIsReplying(false)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
