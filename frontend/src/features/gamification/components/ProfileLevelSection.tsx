import { LevelBadge } from './LevelBadge';

interface ProfileLevelSectionProps {
  level: number;
  levelName: string;
  totalPoints: number;
  pointsToNextLevel: number | null;
  isMaxLevel: boolean;
}

export function ProfileLevelSection({
  level,
  levelName,
  totalPoints,
  pointsToNextLevel,
  isMaxLevel,
}: ProfileLevelSectionProps): JSX.Element {
  return (
    <div className="mt-4 rounded-lg bg-gray-50 p-4" data-testid="profile-level-section">
      <div className="flex items-center gap-3">
        <LevelBadge level={level} size="lg" />
        <div>
          <p className="text-sm font-semibold text-gray-900" data-testid="profile-level-name">
            Level {level} - {levelName}
          </p>
          <p className="text-xs text-gray-500" data-testid="profile-level-points">
            {totalPoints.toLocaleString()} points
          </p>
        </div>
      </div>

      {isMaxLevel ? (
        <p
          className="mt-3 text-center text-xs font-medium text-blue-600"
          data-testid="profile-level-progress"
        >
          Max Level
        </p>
      ) : (
        pointsToNextLevel !== null && (
          <p
            className="mt-3 text-center text-xs text-gray-500"
            data-testid="profile-level-progress"
          >
            {pointsToNextLevel.toLocaleString()} points to level up
          </p>
        )
      )}
    </div>
  );
}
