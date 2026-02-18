import { Avatar } from '@/components/Avatar';
import type { LeaderboardEntry } from '../types';
import { RankMedal } from './RankMedal';

interface LeaderboardRowProps {
  entry: LeaderboardEntry;
  period: '7day' | '30day' | 'alltime';
  highlight?: boolean;
}

export function LeaderboardRow({ entry, period, highlight = false }: LeaderboardRowProps): JSX.Element {
  const pointsDisplay = period !== 'alltime' ? `+${entry.points}` : String(entry.points);

  return (
    <div
      className={`flex items-center gap-3 px-4 py-2.5 ${highlight ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
    >
      <div className="flex w-6 shrink-0 items-center justify-center">
        {entry.rank <= 3 ? (
          <RankMedal rank={entry.rank as 1 | 2 | 3} />
        ) : (
          <span className="text-sm font-medium text-gray-400">{entry.rank}</span>
        )}
      </div>
      <Avatar
        src={entry.avatar_url}
        alt={entry.display_name}
        size="sm"
        fallback={entry.display_name}
        level={entry.level}
      />
      <span className="min-w-0 flex-1 truncate text-sm font-medium text-gray-900">
        {entry.display_name}
      </span>
      <span className="shrink-0 text-sm font-semibold text-gray-700">{pointsDisplay}</span>
    </div>
  );
}
