import { Routes, Route, Navigate, Link } from 'react-router-dom';
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

/**
 * Home page placeholder.
 * Will be replaced with actual feed when Community context is implemented.
 */
function HomePage(): JSX.Element {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Koulu</h1>
          {user !== null && (
            <div className="flex items-center space-x-4">
              <Link
                to={`/profile/${user.id}`}
                className="text-gray-600 hover:text-gray-900"
                data-testid="header-profile-link"
              >
                <span data-testid="header-display-name">
                  {user.profile?.display_name ?? user.email}
                </span>
              </Link>
              <Link
                to="/profile/edit"
                className="text-sm text-gray-600 hover:text-gray-900"
                data-testid="header-edit-profile-link"
              >
                Edit Profile
              </Link>
              <button
                onClick={() => void logout()}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg bg-white p-8 shadow">
          <h2 className="text-xl font-semibold text-gray-900">
            Welcome{user?.profile?.display_name !== undefined && user.profile.display_name !== null ? `, ${user.profile.display_name}` : ''}!
          </h2>
          <p className="mt-2 text-gray-600">
            Your account is set up and ready to go. Community features coming soon!
          </p>
        </div>
      </main>
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

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
