/**
 * 30-day activity chart component (placeholder).
 */

export function ActivityChart(): JSX.Element {
  return (
    <div className="rounded-lg bg-white p-6 shadow" data-testid="activity-chart">
      <h2 className="text-lg font-semibold text-gray-900">Activity</h2>
      <p className="mt-4 text-sm text-gray-500" data-testid="activity-chart-empty">
        No activity yet
      </p>
    </div>
  );
}
