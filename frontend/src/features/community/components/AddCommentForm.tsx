import { useState } from 'react';
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
      <div className="flex gap-2">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={placeholder}
          rows={2}
          maxLength={2000}
          disabled={isPending}
          className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          data-testid="comment-content-input"
        />
        <button
          type="submit"
          disabled={isPending || content.trim() === ''}
          className="self-end rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          data-testid="comment-submit-button"
        >
          {isPending ? 'Posting...' : 'Post'}
        </button>
      </div>
    </form>
  );
}
