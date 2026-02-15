interface LevelBadgeProps {
  level: number;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

const badgeSizeClasses = {
  xs: 'h-4 w-4 text-[10px]',
  sm: 'h-4 w-4 text-[10px]',
  md: 'h-5 w-5 text-xs',
  lg: 'h-6 w-6 text-sm',
};

export function LevelBadge({ level, size = 'md' }: LevelBadgeProps): JSX.Element {
  return (
    <div
      aria-hidden="true"
      className={`${badgeSizeClasses[size]} flex items-center justify-center rounded-full bg-blue-600 border-2 border-white text-white font-semibold`}
    >
      {level}
    </div>
  );
}
