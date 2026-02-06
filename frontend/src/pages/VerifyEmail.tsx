/**
 * Email verification page.
 */

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { VerifyEmail } from '@/features/identity/components';
import { useAuth } from '@/features/identity/hooks';

export function VerifyEmailPage(): JSX.Element {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const handleSuccess = useCallback((): void => {
    void refreshUser().then(() => {
      navigate('/onboarding/profile');
    });
  }, [navigate, refreshUser]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Koulu</h1>
          <h2 className="mt-6 text-2xl font-bold text-gray-900">Email Verification</h2>
        </div>
        <div className="bg-white px-6 py-8 shadow rounded-lg">
          <VerifyEmail onSuccess={handleSuccess} />
        </div>
      </div>
    </div>
  );
}
