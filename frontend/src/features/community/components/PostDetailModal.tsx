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
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-12 pb-12"
      onClick={onClose}
      data-testid="post-detail-modal"
    >
      <div
        className="relative w-full max-w-2xl rounded-xl border border-gray-200 bg-white shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-3 top-3 z-10 rounded-full p-1.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          data-testid="close-modal-button"
          aria-label="Close"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Modal content */}
        <div className="p-5">
          {isLoading ? (
            <div className="animate-pulse space-y-4 py-8">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-gray-200" />
                <div className="space-y-1.5">
                  <div className="h-4 w-32 rounded bg-gray-200" />
                  <div className="h-3 w-24 rounded bg-gray-200" />
                </div>
              </div>
              <div className="h-6 w-3/4 rounded bg-gray-200" />
              <div className="space-y-2">
                <div className="h-4 w-full rounded bg-gray-100" />
                <div className="h-4 w-5/6 rounded bg-gray-100" />
                <div className="h-4 w-4/6 rounded bg-gray-100" />
              </div>
            </div>
          ) : error !== null ? (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700" role="alert">
              Failed to load post. It may have been deleted.
            </div>
          ) : post === undefined ? (
            <div className="py-12 text-center">
              <h3 className="text-lg font-medium text-gray-900">Post not found</h3>
              <p className="mt-1 text-sm text-gray-500">
                This post may have been deleted or does not exist.
              </p>
            </div>
          ) : (
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
