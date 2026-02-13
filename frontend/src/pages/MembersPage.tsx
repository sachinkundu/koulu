import { CommunitySidebar } from '@/features/community/components';
import { MemberList } from '@/features/members/components';
import { useMembers } from '@/features/members/hooks';

export function MembersPage(): JSX.Element {
  const {
    members,
    totalCount,
    isLoading,
    error,
    hasMore,
    isFetchingNextPage,
    fetchNextPage,
  } = useMembers();

  return (
    <div className="mx-auto flex max-w-[1100px] gap-6 px-4 py-6">
      <main className="min-w-0 flex-1">
        <MemberList
          members={members}
          totalCount={totalCount}
          isLoading={isLoading}
          hasMore={hasMore}
          isFetchingNextPage={isFetchingNextPage}
          fetchNextPage={fetchNextPage}
          error={error}
        />
      </main>
      <CommunitySidebar />
    </div>
  );
}
