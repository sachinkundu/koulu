/**
 * Login page.
 */

import { Navigate, useNavigate } from 'react-router-dom';
import { LoginForm } from '@/features/identity/components';
import { useAuth } from '@/features/identity/hooks';

export function LoginPage(): JSX.Element {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (isAuthenticated) {
    // Check if profile is complete
    if (user?.profile?.is_complete === false) {
      return <Navigate to="/onboarding/profile" replace />;
    }
    return <Navigate to="/" replace />;
  }

  const handleSuccess = (): void => {
    // After login, check if profile needs completion
    navigate('/');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Koulu</h1>
          <h2 className="mt-6 text-2xl font-bold text-gray-900">Sign in to your account</h2>
        </div>
        <LoginForm onSuccess={handleSuccess} />
      </div>
    </div>
  );
}
