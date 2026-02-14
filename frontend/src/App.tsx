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
  ClassroomPage,
  CourseDetailPage,
  LessonViewPage,
  MembersPage,
  SearchPage,
} from '@/pages';
import { PostDetailPage } from '@/pages';
import {
  CategoryTabs,
  CommunitySidebar,
  CreatePostInput,
  CreatePostModal,
  FeedPostCard,
  SortDropdown,
} from '@/features/community/components';
import { usePosts } from '@/features/community/hooks';
import type { Post, PostsQueryParams } from '@/features/community/types';
import { TabBar, UserDropdown } from '@/components';
import { SearchBar } from '@/features/search/components/SearchBar';
import type { User } from '@/features/identity/types';

const APP_TABS = [
  { label: 'Community', path: '/' },
  { label: 'Classroom', path: '/classroom' },
  { label: 'Members', path: '/members' },
];

function FullPageSpinner(): JSX.Element {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
    </div>
  );
}

function AppHeader({ user, onLogout }: { user: User | null; onLogout: () => void }): JSX.Element {
  const projectName = import.meta.env.VITE_PROJECT_NAME ?? 'koulu';

  return (
    <header className="bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-gray-900">Koulu</h1>
          <span className="rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-700">
            {projectName}
          </span>
        </div>
        {user !== null && <SearchBar />}
        {user !== null && (
          <div className="flex items-center space-x-4">
            <UserDropdown user={user} onLogout={onLogout} />
          </div>
        )}
      </div>
    </header>
  );
}

/**
 * Home page with community feed in Skool-style layout.
 */
function HomePage(): JSX.Element {
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuth();
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [selectedSort, setSelectedSort] = useState<'hot' | 'new' | 'top'>('hot');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const postsParams: PostsQueryParams = { sort: selectedSort };
  if (selectedCategoryId !== null) {
    postsParams.category_id = selectedCategoryId;
  }

  const { posts, isLoading: postsLoading, error, hasMore, isFetchingNextPage, fetchNextPage } = usePosts(postsParams);

  if (isLoading) {
    return <FullPageSpinner />;
  }

  const handlePostCreated = (post: Post): void => {
    navigate(`/community/posts/${post.id}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader user={user} onLogout={() => void logout()} />
      <TabBar tabs={APP_TABS} />

      {/* Main content: feed + sidebar */}
      <div className="mx-auto flex max-w-[1100px] gap-6 px-4 py-6">
        {/* Feed column */}
        <main className="min-w-0 flex-1">
          <div className="space-y-4">
            {/* Create post */}
            <CreatePostInput onClick={() => setIsCreateModalOpen(true)} />

            {/* Category tabs + Sort in one row */}
            <div className="flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <CategoryTabs
                  selectedCategoryId={selectedCategoryId}
                  onCategoryChange={setSelectedCategoryId}
                />
              </div>
              <SortDropdown
                selectedSort={selectedSort}
                onSortChange={setSelectedSort}
              />
            </div>

            {/* Posts list */}
            {postsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-48 animate-pulse rounded-lg border border-gray-200 bg-white" />
                ))}
              </div>
            ) : error !== null ? (
              <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
                <p className="text-sm text-red-600">Failed to load posts. Please try again later.</p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-3 text-sm font-medium text-primary-600 hover:underline"
                >
                  Retry
                </button>
              </div>
            ) : posts === undefined || posts.length === 0 ? (
              <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
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
                  className="mt-4 rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
                >
                  Create Post
                </button>
              </div>
            ) : (
              <div className="space-y-4" data-testid="posts-list">
                {posts.map((post) => (
                  <FeedPostCard key={post.id} post={post} />
                ))}

                {/* Load more */}
                {hasMore && (
                  <div className="py-4 text-center">
                    <button
                      onClick={() => fetchNextPage()}
                      disabled={isFetchingNextPage}
                      className="rounded-lg border border-gray-200 bg-white px-6 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:opacity-50"
                    >
                      {isFetchingNextPage ? (
                        <span className="flex items-center gap-2">
                          <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
                          Loading...
                        </span>
                      ) : (
                        'Load More'
                      )}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>

        {/* Right sidebar */}
        <CommunitySidebar />
      </div>

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
    return <FullPageSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.profile?.is_complete === false) {
    return <Navigate to="/onboarding/profile" replace />;
  }

  return children;
}

/**
 * Layout wrapper for classroom pages.
 */
function MembersLayout({ children }: { children: JSX.Element }): JSX.Element {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return <FullPageSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader user={user} onLogout={() => void logout()} />
      <TabBar tabs={APP_TABS} />
      {children}
    </div>
  );
}

function ClassroomLayout({ children }: { children: JSX.Element }): JSX.Element {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return <FullPageSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AppHeader user={user} onLogout={() => void logout()} />
      <TabBar tabs={APP_TABS} />
      <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
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

      {/* Members route */}
      <Route
        path="/members"
        element={
          <ProtectedRoute>
            <MembersLayout><MembersPage /></MembersLayout>
          </ProtectedRoute>
        }
      />

      {/* Classroom routes */}
      <Route
        path="/classroom"
        element={
          <ProtectedRoute>
            <ClassroomLayout><ClassroomPage /></ClassroomLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/classroom/courses/:courseId"
        element={
          <ProtectedRoute>
            <ClassroomLayout><CourseDetailPage /></ClassroomLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/classroom/courses/:courseId/lessons/:lessonId"
        element={
          <ProtectedRoute>
            <LessonViewPage />
          </ProtectedRoute>
        }
      />

      {/* Search route */}
      <Route
        path="/search"
        element={
          <ProtectedRoute>
            <SearchPage />
          </ProtectedRoute>
        }
      />

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
