/**
 * Forgot password page.
 */

import { Navigate } from 'react-router-dom';
import { ForgotPasswordForm } from '@/features/identity/components';
import { useAuth } from '@/features/identity/hooks';

export function ForgotPasswordPage(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Koulu</h1>
          <h2 className="mt-6 text-2xl font-bold text-gray-900">Reset your password</h2>
        </div>
        <div className="bg-white px-6 py-8 shadow rounded-lg">
          <ForgotPasswordForm />
        </div>
      </div>
    </div>
  );
}
