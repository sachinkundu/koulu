/**
 * Reset password form component.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useSearchParams } from 'react-router-dom';
import { z } from 'zod';
import { cn } from '@/lib/utils';
import { resetPassword } from '../api/auth';
import type { ApiError } from '../types';

const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

interface ResetPasswordFormProps {
  onSuccess: () => void;
}

export function ResetPasswordForm({ onSuccess }: ResetPasswordFormProps): JSX.Element {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  if (token === null) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">Invalid link</h3>
        <p className="mt-2 text-sm text-gray-600">
          This password reset link is invalid. Please request a new one.
        </p>
        <Link
          to="/forgot-password"
          className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Request new link
        </Link>
      </div>
    );
  }

  const onSubmit = async (data: ResetPasswordFormData): Promise<void> => {
    setError(null);
    try {
      await resetPassword({ token, new_password: data.password });
      setIsSuccess(true);
      setTimeout(onSuccess, 2000);
    } catch (err) {
      const apiError = err as ApiError;
      const code = apiError.response?.data?.code;

      if (code === 'invalid_token') {
        setError('This link is invalid or has expired. Please request a new one.');
      } else {
        setError(apiError.response?.data?.message ?? 'Password reset failed');
      }
    }
  };

  if (isSuccess) {
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
        <h3 className="mt-4 text-lg font-medium text-gray-900">Password reset!</h3>
        <p className="mt-2 text-sm text-gray-600">
          Your password has been reset. Redirecting to login...
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="space-y-6">
      {error !== null && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          New password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          {...register('password')}
          className={cn(
            'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
            errors.password !== undefined ? 'border-red-500' : 'border-gray-300'
          )}
        />
        {errors.password !== undefined && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
          Confirm password
        </label>
        <input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          {...register('confirmPassword')}
          className={cn(
            'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
            errors.confirmPassword !== undefined ? 'border-red-500' : 'border-gray-300'
          )}
        />
        {errors.confirmPassword !== undefined && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? 'Resetting...' : 'Reset password'}
      </button>
    </form>
  );
}
