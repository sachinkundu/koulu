/**
 * Email verification component.
 */

import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { verifyEmail, resendVerification } from '../api/auth';
import type { ApiError } from '../types';

interface VerifyEmailProps {
  onSuccess: () => void;
}

export function VerifyEmail({ onSuccess }: VerifyEmailProps): JSX.Element {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'no-token'>('loading');
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [resendEmail, setResendEmail] = useState('');
  const [resendStatus, setResendStatus] = useState<'idle' | 'loading' | 'success'>('idle');

  useEffect(() => {
    if (token === null) {
      setStatus('no-token');
      return;
    }

    const verify = async (): Promise<void> => {
      try {
        await verifyEmail({ token });
        setStatus('success');
        // Delay navigation to show success message
        setTimeout(onSuccess, 1500);
      } catch (err) {
        const apiError = err as ApiError;
        setErrorCode(apiError.response?.data?.code ?? 'unknown');
        setStatus('error');
      }
    };

    void verify();
  }, [token, onSuccess]);

  const handleResend = async (): Promise<void> => {
    if (resendEmail.length === 0) return;

    setResendStatus('loading');
    try {
      await resendVerification(resendEmail);
      setResendStatus('success');
    } catch {
      setResendStatus('idle');
    }
  };

  if (status === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
        <p className="text-gray-600">Verifying your email...</p>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
          <svg
            className="h-6 w-6 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">Email verified!</h3>
        <p className="mt-2 text-sm text-gray-600">
          Redirecting you to complete your profile...
        </p>
      </div>
    );
  }

  if (status === 'no-token') {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">Invalid link</h3>
        <p className="mt-2 text-sm text-gray-600">
          This verification link is invalid. Please check your email for the correct link.
        </p>
        <Link
          to="/login"
          className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Go to login
        </Link>
      </div>
    );
  }

  // Error state
  return (
    <div className="text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
        <svg
          className="h-6 w-6 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </div>
      <h3 className="mt-4 text-lg font-medium text-gray-900">
        {errorCode === 'already_verified' ? 'Already verified' : 'Verification failed'}
      </h3>
      <p className="mt-2 text-sm text-gray-600">
        {errorCode === 'already_verified'
          ? 'Your email has already been verified.'
          : 'This verification link is invalid or has expired.'}
      </p>

      {errorCode === 'already_verified' ? (
        <Link
          to="/login"
          className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Go to login
        </Link>
      ) : (
        <div className="mt-6">
          <p className="text-sm text-gray-600 mb-2">Enter your email to get a new link:</p>
          <div className="flex space-x-2">
            <input
              type="email"
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              placeholder="your@email.com"
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={() => void handleResend()}
              disabled={resendStatus === 'loading' || resendEmail.length === 0}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {resendStatus === 'loading' ? 'Sending...' : 'Resend'}
            </button>
          </div>
          {resendStatus === 'success' && (
            <p className="mt-2 text-sm text-green-600">Check your email for a new link!</p>
          )}
        </div>
      )}
    </div>
  );
}
