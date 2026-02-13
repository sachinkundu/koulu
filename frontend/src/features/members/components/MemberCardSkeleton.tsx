export function MemberCardSkeleton(): JSX.Element {
  return (
    <div className="flex items-start gap-4 rounded-lg border border-gray-200 bg-white p-4">
      {/* Avatar */}
      <div className="h-12 w-12 shrink-0 animate-pulse rounded-full bg-gray-200" />
      <div className="min-w-0 flex-1 space-y-2">
        {/* Name + badge */}
        <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
        {/* Bio */}
        <div className="h-3 w-48 animate-pulse rounded bg-gray-200" />
        {/* Join date */}
        <div className="h-3 w-24 animate-pulse rounded bg-gray-200" />
      </div>
    </div>
  );
}
