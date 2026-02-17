/**
 * Profile view page.
 */

import { Navigate, useParams } from 'react-router-dom';
import {
  ActivityChart,
  ActivityFeed,
  ProfileSidebar,
  ProfileStats,
} from '@/features/identity/components';
import { useAuth, useProfile, useProfileStats } from '@/features/identity/hooks';
import { useMemberLevel } from '@/features/gamification/hooks';

export function ProfileViewPage(): JSX.Element {
  const { userId } = useParams<{ userId: string }>();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();

  // Use userId from URL, or undefined for own profile
  const { profile, isLoading: profileLoading, error } = useProfile(userId);
  const { stats, isLoading: statsLoading } = useProfileStats(userId ?? 'me');
  const levelUserId = userId ?? user?.id;
  const { memberLevel } = useMemberLevel(levelUserId);

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (profileLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      </div>
    );
  }

  if (error !== null || profile === undefined) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-lg bg-white p-8 text-center shadow" data-testid="profile-not-found">
            <h1 className="text-2xl font-bold text-gray-900">Profile not found</h1>
            <p className="mt-2 text-gray-600">
              The profile you are looking for does not exist.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="md:col-span-1">
            <ProfileSidebar
              profile={profile}
              levelInfo={memberLevel !== undefined ? {
                level: memberLevel.level,
                levelName: memberLevel.level_name,
                totalPoints: memberLevel.total_points,
                pointsToNextLevel: memberLevel.points_to_next_level,
                isMaxLevel: memberLevel.is_max_level,
              } : undefined}
            />
          </div>
          <div className="space-y-6 md:col-span-2">
            <ProfileStats stats={stats} isLoading={statsLoading} />
            <ActivityChart />
            <ActivityFeed />
          </div>
        </div>
      </main>
    </div>
  );
}
