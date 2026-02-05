/**
 * Forgot password form component.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { z } from 'zod';
import { cn } from '@/lib/utils';
import { forgotPassword } from '../api/auth';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

export function ForgotPasswordForm(): JSX.Element {
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData): Promise<void> => {
    try {
      await forgotPassword(data);
      setIsSuccess(true);
    } catch {
      // Always show success to prevent email enumeration
      setIsSuccess(true);
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
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">Check your email</h3>
        <p className="mt-2 text-sm text-gray-600">
          If an account exists with that email, we&apos;ve sent a password reset link.
        </p>
        <Link
          to="/login"
          className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Back to login
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="space-y-6">
      <p className="text-sm text-gray-600">
        Enter your email address and we&apos;ll send you a link to reset your password.
      </p>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          {...register('email')}
          className={cn(
            'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
            errors.email !== undefined ? 'border-red-500' : 'border-gray-300'
          )}
        />
        {errors.email !== undefined && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? 'Sending...' : 'Send reset link'}
      </button>

      <p className="text-center text-sm text-gray-600">
        <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
          Back to login
        </Link>
      </p>
    </form>
  );
}
