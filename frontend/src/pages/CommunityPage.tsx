import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/identity/hooks';
import {
  CategoryTabs,
  CreatePostInput,
  CreatePostModal,
  FeedPostCard,
} from '@/features/community/components';
import { usePosts } from '@/features/community/hooks';
import type { Post } from '@/features/community/types';

export function CommunityPage(): JSX.Element {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  const { posts, isLoading: postsLoading, error } = usePosts(
    selectedCategoryId !== null ? { category_id: selectedCategoryId } : undefined
  );

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

  const handlePostCreated = (post: Post): void => {
    // Navigate to the new post
    navigate(`/community/posts/${post.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">Community Feed</h1>
            <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
              {projectName}
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Create post input */}
          <CreatePostInput onClick={() => setIsCreateModalOpen(true)} />

          {/* Category tabs */}
          <CategoryTabs
            selectedCategoryId={selectedCategoryId}
            onCategoryChange={setSelectedCategoryId}
          />

          {/* Posts list */}
          {postsLoading ? (
            // Loading state
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 animate-pulse rounded-lg bg-white shadow" />
              ))}
            </div>
          ) : error !== null ? (
            // Error state
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
              Failed to load posts. Please try again later.
            </div>
          ) : posts === undefined || posts.length === 0 ? (
            // Empty state
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
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3 className="mt-2 text-lg font-medium text-gray-900">No posts yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Be the first to post in this community!
              </p>
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="mt-4 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                Create Post
              </button>
            </div>
          ) : (
            // Posts
            <div className="space-y-4" data-testid="posts-list">
              {posts.map((post) => (
                <FeedPostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create post modal */}
      <CreatePostModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={handlePostCreated}
      />
    </div>
  );
}
