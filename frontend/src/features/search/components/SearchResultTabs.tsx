import type { SearchType } from '../types';

interface SearchResultTabsProps {
  activeTab: SearchType;
  memberCount: number;
  postCount: number;
  onTabChange: (tab: SearchType) => void;
}

const TABS: Array<{ key: SearchType; label: string }> = [
  { key: 'members', label: 'Members' },
  { key: 'posts', label: 'Posts' },
];

export function SearchResultTabs({
  activeTab,
  memberCount,
  postCount,
  onTabChange,
}: SearchResultTabsProps): JSX.Element {
  const countByKey: Record<SearchType, number> = {
    members: memberCount,
    posts: postCount,
  };

  return (
    <div className="border-b border-gray-200 bg-white" data-testid="search-tabs">
      <nav className="mx-auto flex max-w-7xl space-x-8 px-4">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            data-testid={`search-tab-${tab.key}`}
            onClick={() => onTabChange(tab.key)}
            className={`whitespace-nowrap border-b-2 px-1 py-4 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'border-gray-900 text-gray-900'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            }`}
          >
            {tab.label} {countByKey[tab.key]}
          </button>
        ))}
      </nav>
    </div>
  );
}
