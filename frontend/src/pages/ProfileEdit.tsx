/**
 * Profile edit page.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Navigate, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { useAuth, useProfile, useUpdateProfile } from '@/features/identity/hooks';
import { cn } from '@/lib/utils';
import type { ApiError } from '@/features/identity/types';

const profileEditSchema = z.object({
  display_name: z
    .string()
    .min(2, 'Display name must be at least 2 characters')
    .max(50, 'Display name must be at most 50 characters'),
  avatar_url: z.string().url('Must be a valid URL').or(z.literal('')).optional(),
  bio: z.string().max(500, 'Bio must be at most 500 characters').optional(),
  city: z
    .string()
    .min(2, 'City must be at least 2 characters')
    .max(100, 'City must be at most 100 characters')
    .or(z.literal(''))
    .optional(),
  country: z
    .string()
    .min(2, 'Country must be at least 2 characters')
    .max(100, 'Country must be at most 100 characters')
    .or(z.literal(''))
    .optional(),
  twitter_url: z.string().url('Must be a valid URL').or(z.literal('')).optional(),
  linkedin_url: z.string().url('Must be a valid URL').or(z.literal('')).optional(),
  instagram_url: z.string().url('Must be a valid URL').or(z.literal('')).optional(),
  website_url: z.string().url('Must be a valid URL').or(z.literal('')).optional(),
});

type ProfileEditFormData = z.infer<typeof profileEditSchema>;

export function ProfileEditPage(): JSX.Element {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const { profile, isLoading: profileLoading } = useProfile();
  const { mutateAsync, isPending } = useUpdateProfile();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<ProfileEditFormData>({
    resolver: zodResolver(profileEditSchema),
    defaultValues: {
      display_name: '',
      avatar_url: '',
      bio: '',
      city: '',
      country: '',
      twitter_url: '',
      linkedin_url: '',
      instagram_url: '',
      website_url: '',
    },
  });

  // Populate form when profile loads
  useEffect(() => {
    if (profile !== undefined) {
      reset({
        display_name: profile.display_name ?? '',
        avatar_url: profile.avatar_url ?? '',
        bio: profile.bio ?? '',
        city: profile.location_city ?? '',
        country: profile.location_country ?? '',
        twitter_url: profile.twitter_url ?? '',
        linkedin_url: profile.linkedin_url ?? '',
        instagram_url: profile.instagram_url ?? '',
        website_url: profile.website_url ?? '',
      });
    }
  }, [profile, reset]);

  const bioValue = watch('bio') ?? '';
  const avatarUrl = watch('avatar_url');

  if (authLoading || profileLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const onSubmit = async (data: ProfileEditFormData): Promise<void> => {
    setError(null);
    setSuccess(false);
    try {
      await mutateAsync({
        display_name: data.display_name,
        avatar_url: data.avatar_url !== undefined && data.avatar_url !== '' ? data.avatar_url : null,
        bio: data.bio !== undefined && data.bio !== '' ? data.bio : null,
        city: data.city !== undefined && data.city !== '' ? data.city : null,
        country: data.country !== undefined && data.country !== '' ? data.country : null,
        twitter_url: data.twitter_url !== undefined && data.twitter_url !== '' ? data.twitter_url : null,
        linkedin_url: data.linkedin_url !== undefined && data.linkedin_url !== '' ? data.linkedin_url : null,
        instagram_url: data.instagram_url !== undefined && data.instagram_url !== '' ? data.instagram_url : null,
        website_url: data.website_url !== undefined && data.website_url !== '' ? data.website_url : null,
      });
      setSuccess(true);
      navigate(`/profile/${user?.id ?? 'me'}`);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.response?.data?.message ?? 'Failed to update profile');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">Edit Profile</h1>
        </div>
      </header>
      <main className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="rounded-lg bg-white p-6 shadow">
          <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="space-y-6">
            {error !== null && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert" data-testid="profile-edit-error">
                {error}
              </div>
            )}
            {success && (
              <div className="rounded-md bg-green-50 p-4 text-sm text-green-700" role="status" data-testid="profile-edit-success">
                Profile updated successfully
              </div>
            )}

            {/* Display name */}
            <div>
              <label htmlFor="display_name" className="block text-sm font-medium text-gray-700">
                Display name *
              </label>
              <input
                id="display_name"
                type="text"
                {...register('display_name')}
                className={cn(
                  'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                  errors.display_name !== undefined ? 'border-red-500' : 'border-gray-300'
                )}
                data-testid="profile-edit-display-name"
              />
              {errors.display_name !== undefined && (
                <p className="mt-1 text-sm text-red-600" data-testid="profile-edit-display-name-error">
                  {errors.display_name.message}
                </p>
              )}
            </div>

            {/* Avatar URL */}
            <div>
              <label htmlFor="avatar_url" className="block text-sm font-medium text-gray-700">
                Avatar URL
              </label>
              <input
                id="avatar_url"
                type="url"
                {...register('avatar_url')}
                className={cn(
                  'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                  errors.avatar_url !== undefined ? 'border-red-500' : 'border-gray-300'
                )}
                placeholder="https://example.com/avatar.jpg"
                data-testid="profile-edit-avatar-url"
              />
              {errors.avatar_url !== undefined && (
                <p className="mt-1 text-sm text-red-600">{errors.avatar_url.message}</p>
              )}
              {avatarUrl !== undefined && avatarUrl !== '' && errors.avatar_url === undefined && (
                <img
                  src={avatarUrl}
                  alt="Avatar preview"
                  className="mt-2 h-16 w-16 rounded-full object-cover"
                  data-testid="profile-edit-avatar-preview"
                />
              )}
            </div>

            {/* Bio */}
            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                Bio
              </label>
              <textarea
                id="bio"
                rows={3}
                {...register('bio')}
                className={cn(
                  'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                  errors.bio !== undefined ? 'border-red-500' : 'border-gray-300'
                )}
                data-testid="profile-edit-bio"
              />
              <div className="mt-1 flex justify-between">
                {errors.bio !== undefined ? (
                  <p className="text-sm text-red-600">{errors.bio.message}</p>
                ) : (
                  <span />
                )}
                <span className={cn(
                  'text-sm',
                  bioValue.length > 500 ? 'text-red-600' : 'text-gray-500'
                )} data-testid="profile-edit-bio-counter">
                  {bioValue.length}/500
                </span>
              </div>
            </div>

            {/* Location */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                  City
                </label>
                <input
                  id="city"
                  type="text"
                  {...register('city')}
                  className={cn(
                    'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                    errors.city !== undefined ? 'border-red-500' : 'border-gray-300'
                  )}
                  data-testid="profile-edit-city"
                />
                {errors.city !== undefined && (
                  <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>
                )}
              </div>
              <div>
                <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                  Country
                </label>
                <input
                  id="country"
                  type="text"
                  {...register('country')}
                  className={cn(
                    'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                    errors.country !== undefined ? 'border-red-500' : 'border-gray-300'
                  )}
                  data-testid="profile-edit-country"
                />
                {errors.country !== undefined && (
                  <p className="mt-1 text-sm text-red-600">{errors.country.message}</p>
                )}
              </div>
            </div>

            {/* Social links */}
            <fieldset>
              <legend className="text-sm font-medium text-gray-700">Social links</legend>
              <div className="mt-2 space-y-4">
                <div>
                  <label htmlFor="twitter_url" className="block text-sm text-gray-600">
                    Twitter
                  </label>
                  <input
                    id="twitter_url"
                    type="url"
                    {...register('twitter_url')}
                    className={cn(
                      'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                      errors.twitter_url !== undefined ? 'border-red-500' : 'border-gray-300'
                    )}
                    placeholder="https://twitter.com/username"
                    data-testid="profile-edit-twitter-url"
                  />
                  {errors.twitter_url !== undefined && (
                    <p className="mt-1 text-sm text-red-600">{errors.twitter_url.message}</p>
                  )}
                </div>
                <div>
                  <label htmlFor="linkedin_url" className="block text-sm text-gray-600">
                    LinkedIn
                  </label>
                  <input
                    id="linkedin_url"
                    type="url"
                    {...register('linkedin_url')}
                    className={cn(
                      'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                      errors.linkedin_url !== undefined ? 'border-red-500' : 'border-gray-300'
                    )}
                    placeholder="https://linkedin.com/in/username"
                    data-testid="profile-edit-linkedin-url"
                  />
                  {errors.linkedin_url !== undefined && (
                    <p className="mt-1 text-sm text-red-600">{errors.linkedin_url.message}</p>
                  )}
                </div>
                <div>
                  <label htmlFor="instagram_url" className="block text-sm text-gray-600">
                    Instagram
                  </label>
                  <input
                    id="instagram_url"
                    type="url"
                    {...register('instagram_url')}
                    className={cn(
                      'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                      errors.instagram_url !== undefined ? 'border-red-500' : 'border-gray-300'
                    )}
                    placeholder="https://instagram.com/username"
                    data-testid="profile-edit-instagram-url"
                  />
                  {errors.instagram_url !== undefined && (
                    <p className="mt-1 text-sm text-red-600">{errors.instagram_url.message}</p>
                  )}
                </div>
                <div>
                  <label htmlFor="website_url" className="block text-sm text-gray-600">
                    Website
                  </label>
                  <input
                    id="website_url"
                    type="url"
                    {...register('website_url')}
                    className={cn(
                      'mt-1 block w-full rounded-md border px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500',
                      errors.website_url !== undefined ? 'border-red-500' : 'border-gray-300'
                    )}
                    placeholder="https://example.com"
                    data-testid="profile-edit-website-url"
                  />
                  {errors.website_url !== undefined && (
                    <p className="mt-1 text-sm text-red-600">{errors.website_url.message}</p>
                  )}
                </div>
              </div>
            </fieldset>

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => navigate(`/profile/${user?.id ?? 'me'}`)}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                data-testid="profile-edit-cancel"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isPending}
                className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                data-testid="profile-edit-save"
              >
                {isPending ? 'Saving...' : 'Save'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
