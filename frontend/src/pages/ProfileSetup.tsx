/**
 * Profile setup (onboarding) page.
 */

import { Navigate, useNavigate } from 'react-router-dom';
import { ProfileSetupForm } from '@/features/identity/components';
import { useAuth } from '@/features/identity/hooks';

export function ProfileSetupPage(): JSX.Element {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, user, refreshUser } = useAuth();

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

  // If profile is already complete, redirect to home
  if (user?.profile?.is_complete === true) {
    return <Navigate to="/" replace />;
  }

  const handleSuccess = (): void => {
    void refreshUser();
    navigate('/');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Koulu</h1>
        </div>
        <div className="bg-white px-6 py-8 shadow rounded-lg">
          <ProfileSetupForm onSuccess={handleSuccess} />
        </div>
      </div>
    </div>
  );
}
