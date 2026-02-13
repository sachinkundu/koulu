interface ProgressBarProps {
  percentage: number;
  size?: 'sm' | 'md';
  showLabel?: boolean;
  testId?: string;
}

export function ProgressBar({
  percentage,
  size = 'md',
  showLabel = true,
  testId,
}: ProgressBarProps): JSX.Element {
  const height = size === 'sm' ? 'h-1.5' : 'h-2';
  const labelSize = size === 'sm' ? 'text-xs' : 'text-sm';

  return (
    <div data-testid={testId}>
      {showLabel && (
        <div className={`flex items-center justify-between ${labelSize} text-gray-600 mb-1`}>
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={`${height} w-full rounded-full bg-gray-200`}>
        <div
          className={`${height} rounded-full bg-green-500 transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
