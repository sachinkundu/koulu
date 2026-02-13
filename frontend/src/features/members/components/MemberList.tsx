import { useEffect, useRef } from 'react';
import type { DirectoryMember } from '../types';
import { MemberCard } from './MemberCard';
import { MemberCardSkeleton } from './MemberCardSkeleton';

interface MemberListProps {
  members: DirectoryMember[] | undefined;
  totalCount: number;
  isLoading: boolean;
  hasMore: boolean;
  isFetchingNextPage: boolean;
  fetchNextPage: () => void;
  error: Error | null;
}

export function MemberList({
  members,
  totalCount,
  isLoading,
  hasMore,
  isFetchingNextPage,
  fetchNextPage,
  error,
}: MemberListProps): JSX.Element {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (sentinel == null) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting === true && hasMore && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, isFetchingNextPage, fetchNextPage]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <MemberCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error != null) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
        <p className="text-sm text-red-600">Failed to load members. Please try again.</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-3 text-sm font-medium text-primary-600 hover:underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (members == null || members.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <h3 className="mt-2 text-lg font-medium text-gray-900">No members found</h3>
        <p className="mt-1 text-sm text-gray-500">
          Try adjusting your search or filters.
        </p>
      </div>
    );
  }

  return (
    <div data-testid="member-list">
      <p className="mb-3 text-sm font-medium text-gray-500">
        {totalCount} {totalCount === 1 ? 'member' : 'members'}
      </p>
      <div className="space-y-3">
        {members.map((member) => (
          <MemberCard key={member.user_id} member={member} />
        ))}
      </div>

      {/* Infinite scroll sentinel */}
      <div ref={sentinelRef} className="h-4" />

      {isFetchingNextPage && (
        <div className="flex justify-center py-4">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
        </div>
      )}
    </div>
  );
}
