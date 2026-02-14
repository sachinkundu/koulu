import { useSearchParams } from 'react-router-dom';
import { useSearch } from '../hooks';
import { SearchResultTabs } from './SearchResultTabs';
import { SearchPagination } from './SearchPagination';
import { SearchSkeleton } from './SearchSkeleton';
import { MemberSearchCard } from './MemberSearchCard';
import { PostSearchCard } from './PostSearchCard';
import type { SearchType, MemberSearchItem, PostSearchItem, SearchResponse } from '../types';

const PAGE_SIZE = 10;

export function SearchResults(): JSX.Element {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const activeTab = (searchParams.get('t') ?? 'members') as SearchType;
  const currentPage = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10) || 1);
  const offset = (currentPage - 1) * PAGE_SIZE;

  const { data, isLoading, error } = useSearch(query, activeTab, PAGE_SIZE, offset);

  function handleTabChange(tab: SearchType): void {
    setSearchParams((prev) => {
      prev.set('t', tab);
      prev.delete('page');
      return prev;
    });
  }

  function handlePageChange(page: number): void {
    setSearchParams((prev) => {
      if (page <= 1) {
        prev.delete('page');
      } else {
        prev.set('page', String(page));
      }
      return prev;
    });
  }

  if (query.trim().length < 3) {
    const message =
      query.trim().length === 0
        ? 'Enter a search term above to find members and posts'
        : 'Please enter at least 3 characters to search';

    return (
      <div className="py-12 text-center" data-testid="search-empty-state">
        <p className="text-sm text-gray-500">{message}</p>
      </div>
    );
  }

  return (
    <div>
      <SearchResultTabs
        activeTab={activeTab}
        memberCount={data?.member_count ?? 0}
        postCount={data?.post_count ?? 0}
        onTabChange={handleTabChange}
      />

      <div className="mx-auto max-w-[1100px] px-4 py-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[2fr_360px]">
          <div className="space-y-4">
            <SearchResultContent
              isLoading={isLoading}
              error={error}
              data={data}
              activeTab={activeTab}
              query={query}
            />
            {data != null && data.items.length > 0 && (
              <SearchPagination
                currentPage={currentPage}
                totalResults={data.total_count}
                pageSize={PAGE_SIZE}
                hasMore={data.has_more}
                onPageChange={handlePageChange}
              />
            )}
          </div>

          {/* Sidebar placeholder */}
          <div className="hidden md:block" />
        </div>
      </div>
    </div>
  );
}

interface SearchResultContentProps {
  isLoading: boolean;
  error: Error | null;
  data: SearchResponse | undefined;
  activeTab: SearchType;
  query: string;
}

function SearchResultContent({
  isLoading,
  error,
  data,
  activeTab,
  query,
}: SearchResultContentProps): JSX.Element {
  if (isLoading) {
    return <SearchSkeleton />;
  }

  if (error != null) {
    return (
      <div className="py-12 text-center" data-testid="search-error">
        <p className="text-sm text-red-600">
          Search is temporarily unavailable. Please try again.
        </p>
      </div>
    );
  }

  if (data == null || data.items.length === 0) {
    return (
      <div className="py-12 text-center" data-testid="search-no-results">
        <p className="text-base font-semibold text-gray-900">
          No {activeTab} found for &ldquo;{query}&rdquo;
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Try a different search term
        </p>
      </div>
    );
  }

  if (activeTab === 'members') {
    return (
      <div data-testid="search-results-list">
        {(data.items as MemberSearchItem[]).map((member) => (
          <MemberSearchCard key={member.user_id} member={member} />
        ))}
      </div>
    );
  }

  return (
    <div data-testid="search-results-list">
      {(data.items as PostSearchItem[]).map((post) => (
        <PostSearchCard key={post.id} post={post} />
      ))}
    </div>
  );
}
