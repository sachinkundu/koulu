import { Avatar } from '@/components/Avatar';

interface LeaderboardProfileCardProps {
  avatarUrl: string | null;
  displayName: string;
  level: number;
  levelName: string;
  pointsToNextLevel: number | null;
  isMaxLevel: boolean;
}

export function LeaderboardProfileCard({
  avatarUrl,
  displayName,
  level,
  levelName,
  pointsToNextLevel,
  isMaxLevel,
}: LeaderboardProfileCardProps): JSX.Element {
  return (
    <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-6" data-testid="leaderboard-profile-card">
      <Avatar src={avatarUrl} alt={displayName} size="lg" fallback={displayName} level={level} />
      <h2 className="mt-3 text-lg font-bold text-gray-900">{displayName}</h2>
      <p className="mt-1 text-sm font-medium text-gray-600">
        Level {level} - {levelName}
      </p>
      {!isMaxLevel && pointsToNextLevel != null && (
        <p className="mt-1 text-xs text-gray-400">{pointsToNextLevel} points to level up</p>
      )}
    </div>
  );
}
