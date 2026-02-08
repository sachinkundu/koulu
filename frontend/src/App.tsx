import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@/features/identity/hooks';
import {
  ForgotPasswordPage,
  LoginPage,
  ProfileEditPage,
  ProfileSetupPage,
  ProfileViewPage,
  RegisterPage,
  ResetPasswordPage,
  VerifyEmailPage,
} from '@/pages';
import { PostDetailPage } from '@/pages';
import {
  CategoryTabs,
  CreatePostInput,
  CreatePostModal,
  FeedPostCard,
} from '@/features/community/components';
import { usePosts } from '@/features/community/hooks';
import type { Post } from '@/features/community/types';
import { TabBar, UserDropdown } from '@/components';

/**
 * Home page with community feed.
 */
function HomePage(): JSX.Element {
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuth();
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  const { posts, isLoading: postsLoading, error } = usePosts(
    selectedCategoryId !== null ? { category_id: selectedCategoryId } : undefined
  );

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  const handlePostCreated = (post: Post): void => {
    // Navigate to the new post
    navigate(`/community/posts/${post.id}`);
  };

  const tabs = [{ label: 'Community', path: '/' }];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">Koulu</h1>
            <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
              {projectName}
            </span>
          </div>
          {user !== null && (
            <div className="flex items-center space-x-4">
              <UserDropdown user={user} onLogout={() => void logout()} />
            </div>
          )}
        </div>
      </header>

      {/* Tab bar */}
      <TabBar tabs={tabs} />
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

/**
 * Protected route wrapper.
 * Redirects to login if not authenticated.
 * Redirects to profile setup if profile not complete.
 */
function ProtectedRoute({ children }: { children: JSX.Element }): JSX.Element {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.profile?.is_complete === false) {
    return <Navigate to="/onboarding/profile" replace />;
  }

  return children;
}

function App(): JSX.Element {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/verify" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Onboarding routes (authenticated but profile incomplete) */}
      <Route path="/onboarding/profile" element={<ProfileSetupPage />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile/edit"
        element={
          <ProtectedRoute>
            <ProfileEditPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile/:userId"
        element={
          <ProtectedRoute>
            <ProfileViewPage />
          </ProtectedRoute>
        }
      />

      {/* Community routes */}
      <Route path="/community" element={<Navigate to="/" replace />} />
      <Route
        path="/community/posts/:postId"
        element={
          <ProtectedRoute>
            <PostDetailPage />
          </ProtectedRoute>
        }
      />

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
