import type { LeaderboardEntry } from '../types';
import { LeaderboardRow } from './LeaderboardRow';

interface YourRankSectionProps {
  entry: LeaderboardEntry;
  period: '7day' | '30day' | 'alltime';
}

export function YourRankSection({ entry, period }: YourRankSectionProps): JSX.Element {
  return (
    <div data-testid="your-rank-section">
      <div className="flex items-center gap-2 px-4 py-2">
        <div className="h-px flex-1 bg-gray-200" />
        <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
          Your rank
        </span>
        <div className="h-px flex-1 bg-gray-200" />
      </div>
      <LeaderboardRow entry={entry} period={period} highlight />
    </div>
  );
}
