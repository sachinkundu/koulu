/**
 * Profile statistics component.
 */

import type { StatsResponse } from '../types';

interface ProfileStatsProps {
  stats: StatsResponse | undefined;
  isLoading: boolean;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function ProfileStats({ stats, isLoading }: ProfileStatsProps): JSX.Element {
  if (isLoading) {
    return (
      <div className="rounded-lg bg-white p-6 shadow" data-testid="profile-stats">
        <div className="h-16 animate-pulse rounded bg-gray-100" />
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow" data-testid="profile-stats">
      <h2 className="text-lg font-semibold text-gray-900">Stats</h2>
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold text-gray-900" data-testid="profile-contributions">
            {stats?.contribution_count ?? 0}
          </p>
          <p className="text-sm text-gray-500">Contributions</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900" data-testid="profile-joined-date">
            {stats?.joined_at !== undefined ? formatDate(stats.joined_at) : '-'}
          </p>
          <p className="text-sm text-gray-500">Member since</p>
        </div>
      </div>
    </div>
  );
}
