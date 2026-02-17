import { useLevelDefinitions } from '@/features/gamification/hooks';
import { LevelDefinitionsGrid } from '@/features/gamification/components/LevelDefinitionsGrid';

export function LeaderboardsPage(): JSX.Element {
  const { levels, currentUserLevel, isLoading, error } = useLevelDefinitions();

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Leaderboards</h2>
        <p className="mt-1 text-sm text-gray-600">Levels</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg border border-gray-200 bg-white" />
          ))}
        </div>
      ) : error !== null ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-sm text-red-600">Failed to load level definitions.</p>
        </div>
      ) : levels !== undefined && currentUserLevel !== undefined ? (
        <LevelDefinitionsGrid levels={levels} currentUserLevel={currentUserLevel} />
      ) : null}
    </div>
  );
}
