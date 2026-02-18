import { useAuth } from '@/features/identity/context/AuthContext';
import { LevelDefinitionsGrid } from '@/features/gamification/components/LevelDefinitionsGrid';
import { LeaderboardPanel } from '@/features/gamification/components/LeaderboardPanel';
import { LeaderboardProfileCard } from '@/features/gamification/components/LeaderboardProfileCard';
import { useLeaderboards } from '@/features/gamification/hooks/useLeaderboards';
import { useLevelDefinitions, useMemberLevel } from '@/features/gamification/hooks';

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

export function LeaderboardsPage(): JSX.Element {
  const { user } = useAuth();
  const { data, isLoading: leaderboardsLoading, error: leaderboardsError } = useLeaderboards();
  const { levels, currentUserLevel, isLoading: levelsLoading } = useLevelDefinitions();
  const { memberLevel, isLoading: memberLoading } = useMemberLevel(user?.id);

  const isLoading = leaderboardsLoading || levelsLoading || memberLoading;

  // Find the level name for the current user
  const currentLevelDef = levels?.find((l) => l.level === (memberLevel?.level ?? currentUserLevel ?? 1));
  const levelName = currentLevelDef?.name ?? 'Newcomer';

  return (
    <div className="mx-auto max-w-[1100px] px-4 py-8">
      {/* Top section: Profile card + Level definitions */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[280px_1fr]">
        {isLoading ? (
          <>
            <div className="h-48 animate-pulse rounded-lg border border-gray-200 bg-white" />
            <div className="h-48 animate-pulse rounded-lg border border-gray-200 bg-white" />
          </>
        ) : (
          <>
            <LeaderboardProfileCard
              avatarUrl={user?.profile?.avatar_url ?? null}
              displayName={user?.profile?.display_name ?? user?.email ?? 'Member'}
              level={memberLevel?.level ?? 1}
              levelName={levelName}
              pointsToNextLevel={memberLevel?.points_to_next_level ?? null}
              isMaxLevel={memberLevel?.is_max_level ?? false}
            />
            {levels != null && currentUserLevel != null && (
              <LevelDefinitionsGrid levels={levels} currentUserLevel={currentUserLevel} />
            )}
          </>
        )}
      </div>

      {/* Timestamp */}
      {data?.last_updated != null && (
        <p className="mt-4 text-sm text-gray-500">
          Last updated: {formatTimestamp(data.last_updated)}
        </p>
      )}

      {/* Three leaderboard panels */}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <LeaderboardPanel
          title="Leaderboard (7-day)"
          entries={data?.seven_day.entries ?? []}
          yourRank={data?.seven_day.your_rank ?? null}
          period="7day"
          isLoading={leaderboardsLoading}
          error={leaderboardsError}
        />
        <LeaderboardPanel
          title="Leaderboard (30-day)"
          entries={data?.thirty_day.entries ?? []}
          yourRank={data?.thirty_day.your_rank ?? null}
          period="30day"
          isLoading={leaderboardsLoading}
          error={leaderboardsError}
        />
        <LeaderboardPanel
          title="Leaderboard (All-time)"
          entries={data?.all_time.entries ?? []}
          yourRank={data?.all_time.your_rank ?? null}
          period="alltime"
          isLoading={leaderboardsLoading}
          error={leaderboardsError}
        />
      </div>
    </div>
  );
}
