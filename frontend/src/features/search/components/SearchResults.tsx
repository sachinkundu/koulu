import { useSearchParams } from 'react-router-dom';
import { useSearch } from '../hooks';
import { SearchResultTabs } from './SearchResultTabs';
import { SearchSkeleton } from './SearchSkeleton';
import { MemberSearchCard } from './MemberSearchCard';
import { PostSearchCard } from './PostSearchCard';
import type { SearchType, MemberSearchItem, PostSearchItem } from '../types';

export function SearchResults(): JSX.Element {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const activeTab = (searchParams.get('t') ?? 'members') as SearchType;

  const { data, isLoading, error } = useSearch(query, activeTab);

  function handleTabChange(tab: SearchType): void {
    setSearchParams((prev) => {
      prev.set('t', tab);
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
  data: { items: MemberSearchItem[] | PostSearchItem[]; member_count: number; post_count: number } | undefined;
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
