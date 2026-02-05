/**
 * Login form component.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { z } from 'zod';
import { cn } from '@/lib/utils';
import { useAuth } from '../context/AuthContext';
import type { ApiError } from '../types';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
  remember_me: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps): JSX.Element {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      remember_me: false,
    },
  });

  const onSubmit = async (data: LoginFormData): Promise<void> => {
    setError(null);
    try {
      await login({
        email: data.email,
        password: data.password,
        remember_me: data.remember_me,
      });
      onSuccess();
    } catch (err) {
      const apiError = err as ApiError;
      const code = apiError.response?.data?.code;

      if (code === 'email_not_verified') {
        setError('Please verify your email before logging in');
      } else if (code === 'account_disabled') {
        setError('Your account has been disabled');
      } else {
        setError('Invalid email or password');
      }
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="space-y-6">
      {error !== null && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

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

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
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

      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            id="remember_me"
            type="checkbox"
            {...register('remember_me')}
            className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-700">
            Remember me
          </label>
        </div>

        <Link
          to="/forgot-password"
          className="text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>

      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="font-medium text-primary-600 hover:text-primary-500">
          Create one
        </Link>
      </p>
    </form>
  );
}
