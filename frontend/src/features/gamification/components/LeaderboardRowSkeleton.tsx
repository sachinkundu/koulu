export function LeaderboardRowSkeleton(): JSX.Element {
  return (
    <div className="flex items-center gap-3 px-4 py-2.5">
      <div className="h-4 w-4 shrink-0 animate-pulse rounded-full bg-gray-200" />
      <div className="h-8 w-8 shrink-0 animate-pulse rounded-full bg-gray-200" />
      <div className="h-4 flex-1 animate-pulse rounded bg-gray-200" />
      <div className="h-4 w-8 shrink-0 animate-pulse rounded bg-gray-200" />
    </div>
  );
}
