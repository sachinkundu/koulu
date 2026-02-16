import type { LevelDefinition } from '../types';
import { LevelBadge } from './LevelBadge';

interface LevelDefinitionsGridProps {
  levels: LevelDefinition[];
  currentUserLevel: number;
}

export function LevelDefinitionsGrid({
  levels,
  currentUserLevel,
}: LevelDefinitionsGridProps): JSX.Element {
  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      data-testid="level-definitions-grid"
    >
      {levels.map((levelDef) => {
        const isCurrent = levelDef.level === currentUserLevel;
        return (
          <div
            key={levelDef.level}
            className={`rounded-lg border p-4 ${
              isCurrent
                ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                : 'border-gray-200 bg-white'
            }`}
            data-testid={`level-card-${levelDef.level}`}
          >
            <div className="flex items-center gap-3">
              <LevelBadge level={levelDef.level} size="lg" />
              <div>
                <p className="text-sm font-semibold text-gray-900">{levelDef.name}</p>
                <p className="text-xs text-gray-500">
                  {levelDef.threshold.toLocaleString()} points
                </p>
              </div>
            </div>
            <p className="mt-2 text-xs text-gray-400">
              {levelDef.member_percentage.toFixed(1)}% of members
            </p>
          </div>
        );
      })}
    </div>
  );
}
