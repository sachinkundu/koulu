import { useEffect } from 'react';
import { usePost } from '../hooks';
import { PostDetail } from './PostDetail';
import { useCurrentUser } from '@/features/identity/hooks';

interface PostDetailModalProps {
  postId: string;
  onClose: () => void;
}

export function PostDetailModal({ postId, onClose }: PostDetailModalProps): JSX.Element {
  const { post, isLoading, error } = usePost(postId);
  const { user } = useCurrentUser();

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent): void => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-20"
      onClick={onClose}
      data-testid="post-detail-modal"
    >
      <div
        className="relative w-full max-w-3xl rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          data-testid="close-modal-button"
          aria-label="Close"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Modal content */}
        <div className="p-6">
          {isLoading ? (
            // Loading state
            <div className="h-96 animate-pulse">
              <div className="mb-4 h-12 w-3/4 rounded bg-gray-200" />
              <div className="space-y-3">
                <div className="h-4 w-full rounded bg-gray-200" />
                <div className="h-4 w-5/6 rounded bg-gray-200" />
                <div className="h-4 w-4/6 rounded bg-gray-200" />
              </div>
            </div>
          ) : error !== null ? (
            // Error state
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
              Failed to load post. It may have been deleted.
            </div>
          ) : post === undefined ? (
            // Not found
            <div className="py-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">Post not found</h3>
              <p className="mt-1 text-sm text-gray-500">
                This post may have been deleted or does not exist.
              </p>
            </div>
          ) : (
            // Post detail
            <PostDetail
              post={post}
              currentUserId={user?.id}
              onNavigate={onClose}
            />
          )}
        </div>
      </div>
    </div>
  );
}
