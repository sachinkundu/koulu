import { useCallback, useState } from 'react';
import { CommunitySidebar } from '@/features/community/components';
import { MemberFilters, MemberList } from '@/features/members/components';
import { useMembers } from '@/features/members/hooks';
import type { MembersQueryParams } from '@/features/members/types';

type RoleFilter = MembersQueryParams['role'];
type SortOption = NonNullable<MembersQueryParams['sort']>;

export function MembersPage(): JSX.Element {
  const [search, setSearch] = useState('');
  const [role, setRole] = useState<RoleFilter>(undefined);
  const [sort, setSort] = useState<SortOption>('most_recent');

  const params: MembersQueryParams = {
    sort,
    ...(search !== '' ? { search } : {}),
    ...(role != null ? { role } : {}),
  };

  const {
    members,
    totalCount,
    isLoading,
    error,
    hasMore,
    isFetchingNextPage,
    fetchNextPage,
  } = useMembers(params);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
  }, []);

  const handleRoleChange = useCallback((value: RoleFilter) => {
    setRole(value);
  }, []);

  const handleSortChange = useCallback((value: SortOption) => {
    setSort(value);
  }, []);

  return (
    <div className="mx-auto flex max-w-[1100px] gap-6 px-4 py-6">
      <main className="min-w-0 flex-1">
        <MemberFilters
          search={search}
          role={role}
          sort={sort}
          onSearchChange={handleSearchChange}
          onRoleChange={handleRoleChange}
          onSortChange={handleSortChange}
        />
        <div className="mt-4">
          <MemberList
            members={members}
            totalCount={totalCount}
            isLoading={isLoading}
            hasMore={hasMore}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
            error={error}
          />
        </div>
      </main>
      <CommunitySidebar />
    </div>
  );
}
