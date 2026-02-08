import { Navigate, useParams, Link } from 'react-router-dom';
import { useAuth, useCurrentUser } from '@/features/identity/hooks';
import { usePost } from '@/features/community/hooks';
import { PostDetail } from '@/features/community/components';

export function PostDetailPage(): JSX.Element {
  const { postId } = useParams<{ postId: string }>();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { user } = useCurrentUser();
  const { post, isLoading: postLoading, error } = usePost(postId ?? '');

  // Auth check
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Validate postId
  if (postId === undefined) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
            Invalid post ID
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with back button */}
      <header className="bg-white shadow">
        <div className="mx-auto max-w-4xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              to="/community"
              className="rounded-md p-2 text-gray-600 hover:bg-gray-100"
              data-testid="back-to-feed"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Post</h1>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {postLoading ? (
          // Loading state
          <div className="h-96 animate-pulse rounded-lg bg-white shadow" />
        ) : error !== null ? (
          // Error state
          <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
            Failed to load post. It may have been deleted.
          </div>
        ) : post === undefined ? (
          // Not found
          <div className="rounded-lg bg-white p-12 text-center shadow">
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
            <Link
              to="/community"
              className="mt-4 inline-block rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              Back to Feed
            </Link>
          </div>
        ) : (
          // Post detail
          <PostDetail post={post} currentUserId={user?.id} />
        )}
      </main>
    </div>
  );
}
