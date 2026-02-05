/**
 * Profile setup form component.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { cn } from '@/lib/utils';
import { completeProfile } from '../api/user';
import type { ApiError } from '../types';

const profileSchema = z.object({
  display_name: z
    .string()
    .min(2, 'Display name must be at least 2 characters')
    .max(50, 'Display name must be at most 50 characters'),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface ProfileSetupFormProps {
  onSuccess: () => void;
}

export function ProfileSetupForm({ onSuccess }: ProfileSetupFormProps): JSX.Element {
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  const onSubmit = async (data: ProfileFormData): Promise<void> => {
    setError(null);
    try {
      await completeProfile({ display_name: data.display_name });
      onSuccess();
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.response?.data?.message ?? 'Failed to save profile');
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Complete your profile</h2>
        <p className="mt-2 text-gray-600">
          Choose a display name that others will see.
        </p>
      </div>

      {error !== null && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="display_name" className="block text-sm font-medium text-gray-700">
          Display name
        </label>
        <input
          id="display_name"
          type="text"
          autoComplete="name"
          {...register('display_name')}
          className={cn(
            'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
            errors.display_name !== undefined ? 'border-red-500' : 'border-gray-300'
          )}
          placeholder="John Doe"
        />
        {errors.display_name !== undefined && (
          <p className="mt-1 text-sm text-red-600">{errors.display_name.message}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          This is how other users will see you.
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? 'Saving...' : 'Continue'}
      </button>
    </form>
  );
}
