/**
 * Recent activity feed component (placeholder).
 */

export function ActivityFeed(): JSX.Element {
  return (
    <div className="rounded-lg bg-white p-6 shadow" data-testid="activity-feed">
      <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
      <p className="mt-4 text-sm text-gray-500" data-testid="activity-feed-empty">
        No posts or comments yet
      </p>
    </div>
  );
}
