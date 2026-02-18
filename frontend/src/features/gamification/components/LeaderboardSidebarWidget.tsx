import { Link } from 'react-router-dom';
import { Avatar } from '@/components/Avatar';
import { useLeaderboardWidget } from '../hooks/useLeaderboardWidget';
import { RankMedal } from './RankMedal';

export function LeaderboardSidebarWidget(): JSX.Element | null {
  const { data, isLoading, error } = useLeaderboardWidget();

  if (error != null) {
    return null;
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-700">Leaderboard (30-day)</h3>
      </div>
      {isLoading ? (
        <div className="space-y-2 px-4 py-3">
          {Array.from({ length: 5 }, (_, i) => (
            <div key={i} className="flex animate-pulse items-center gap-2">
              <div className="h-4 w-4 rounded bg-gray-200" />
              <div className="h-6 w-6 rounded-full bg-gray-200" />
              <div className="h-3 flex-1 rounded bg-gray-200" />
              <div className="h-3 w-8 rounded bg-gray-200" />
            </div>
          ))}
        </div>
      ) : data != null && data.entries.length > 0 ? (
        <div className="divide-y divide-gray-50">
          {data.entries.map((entry) => (
            <div key={entry.user_id} className="flex items-center gap-2 px-4 py-2">
              <div className="flex w-5 shrink-0 items-center justify-center">
                {entry.rank <= 3 ? (
                  <RankMedal rank={entry.rank as 1 | 2 | 3} />
                ) : (
                  <span className="text-xs font-medium text-gray-400">{entry.rank}</span>
                )}
              </div>
              <Avatar
                src={entry.avatar_url}
                alt={entry.display_name}
                size="xs"
                fallback={entry.display_name}
                level={entry.level}
              />
              <span className="min-w-0 flex-1 truncate text-xs font-medium text-gray-900">
                {entry.display_name}
              </span>
              <span className="shrink-0 text-xs font-semibold text-gray-700">+{entry.points}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="px-4 py-6 text-center">
          <p className="text-xs text-gray-500">No rankings yet.</p>
        </div>
      )}
      <div className="border-t border-gray-100 px-4 py-2.5">
        <Link
          to="/leaderboards"
          className="block text-center text-xs font-medium text-blue-600 hover:text-blue-700"
        >
          See all leaderboards
        </Link>
      </div>
    </div>
  );
}
