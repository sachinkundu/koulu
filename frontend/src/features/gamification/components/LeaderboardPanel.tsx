import type { LeaderboardEntry } from '../types';
import { LeaderboardRow } from './LeaderboardRow';
import { LeaderboardRowSkeleton } from './LeaderboardRowSkeleton';
import { YourRankSection } from './YourRankSection';

interface LeaderboardPanelProps {
  title: string;
  entries: LeaderboardEntry[];
  yourRank: LeaderboardEntry | null;
  period: '7day' | '30day' | 'alltime';
  isLoading?: boolean;
  error?: Error | null;
}

export function LeaderboardPanel({
  title,
  entries,
  yourRank,
  period,
  isLoading = false,
  error = null,
}: LeaderboardPanelProps): JSX.Element {
  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      </div>
      {isLoading ? (
        <div>
          {Array.from({ length: 5 }, (_, i) => (
            <LeaderboardRowSkeleton key={i} />
          ))}
        </div>
      ) : error != null ? (
        <div className="px-4 py-8 text-center">
          <p className="text-sm text-red-600">Failed to load leaderboard.</p>
        </div>
      ) : entries.length === 0 ? (
        <div className="px-4 py-8 text-center">
          <p className="text-sm text-gray-500">No rankings yet — be the first to earn points!</p>
        </div>
      ) : (
        <>
          <div className="divide-y divide-gray-50">
            {entries.map((e) => (
              <LeaderboardRow key={e.user_id} entry={e} period={period} />
            ))}
          </div>
          {yourRank != null && <YourRankSection entry={yourRank} period={period} />}
        </>
      )}
    </div>
  );
}
