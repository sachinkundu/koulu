import { useState } from 'react';
import { Avatar } from '@/components';
import { useCurrentUser } from '@/features/identity/hooks';
import { useAddComment } from '../hooks';

interface AddCommentFormProps {
  postId: string;
  parentCommentId?: string | null;
  onSuccess?: () => void;
  placeholder?: string;
}

export function AddCommentForm({
  postId,
  parentCommentId,
  onSuccess,
  placeholder = 'Write a comment...',
}: AddCommentFormProps): JSX.Element {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { mutateAsync, isPending } = useAddComment(postId);
  const { user } = useCurrentUser();

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (content.trim() === '') return;

    setError(null);
    try {
      await mutateAsync({
        content: content.trim(),
        parent_comment_id: parentCommentId,
      });
      setContent('');
      onSuccess?.();
    } catch {
      setError('Failed to add comment. Please try again.');
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(e)} data-testid="add-comment-form">
      {error !== null && (
        <div className="mb-2 rounded-md bg-red-50 p-2 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}
      <div className="flex items-start gap-2.5">
        <Avatar
          src={user?.profile?.avatar_url}
          alt={user?.profile?.display_name ?? 'You'}
          fallback={user?.profile?.display_name ?? 'You'}
          size={parentCommentId != null ? 'xs' : 'sm'}
        />
        <div className="min-w-0 flex-1">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={placeholder}
            rows={1}
            maxLength={2000}
            disabled={isPending}
            className="w-full resize-none rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm transition-colors placeholder:text-gray-400 focus:border-gray-300 focus:bg-white focus:outline-none focus:ring-1 focus:ring-gray-300 disabled:opacity-50"
            onFocus={(e) => { if (e.target.rows < 3) e.target.rows = 3; }}
            data-testid="comment-content-input"
          />
          {content.trim() !== '' && (
            <div className="mt-1.5 flex justify-end">
              <button
                type="submit"
                disabled={isPending || content.trim() === ''}
                className="rounded-lg bg-gray-900 px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-gray-800 disabled:opacity-50"
                data-testid="comment-submit-button"
              >
                {isPending ? 'Posting...' : 'Post'}
              </button>
            </div>
          )}
        </div>
      </div>
    </form>
  );
}
