import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import { getMembers } from '../api';

type RoleFilter = 'admin' | 'moderator' | 'member' | undefined;
type SortOption = 'most_recent' | 'alphabetical';

interface MemberFiltersProps {
  search: string;
  role: RoleFilter;
  sort: SortOption;
  onSearchChange: (search: string) => void;
  onRoleChange: (role: RoleFilter) => void;
  onSortChange: (sort: SortOption) => void;
}

const ROLE_TABS: { value: RoleFilter; label: string }[] = [
  { value: undefined, label: 'All' },
  { value: 'admin', label: 'Admin' },
  { value: 'moderator', label: 'Mod' },
];

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'most_recent', label: 'Most Recent' },
  { value: 'alphabetical', label: 'Alphabetical' },
];

function useRoleCount(role: RoleFilter): number | undefined {
  const { data } = useQuery({
    queryKey: ['members', 'count', role ?? 'all'],
    queryFn: () => getMembers({ role, limit: 1 }),
    staleTime: 30 * 1000,
  });
  return data?.total_count;
}

export function MemberFilters({
  search,
  role,
  sort,
  onSearchChange,
  onRoleChange,
  onSortChange,
}: MemberFiltersProps): JSX.Element {
  const [localSearch, setLocalSearch] = useState(search);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const allCount = useRoleCount(undefined);
  const adminCount = useRoleCount('admin');
  const modCount = useRoleCount('moderator');
  const counts: Record<string, number | undefined> = {
    all: allCount,
    admin: adminCount,
    moderator: modCount,
  };

  useEffect(() => {
    if (debounceRef.current != null) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      onSearchChange(localSearch);
    }, 300);
    return () => {
      if (debounceRef.current != null) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [localSearch, onSearchChange]);

  // Sort dropdown state
  const [isSortOpen, setIsSortOpen] = useState(false);
  const sortRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (sortRef.current != null && !sortRef.current.contains(event.target as Node)) {
        setIsSortOpen(false);
      }
    }
    if (isSortOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isSortOpen]);

  const activeSort = SORT_OPTIONS.find((o) => o.value === sort) ?? SORT_OPTIONS[0]!;

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          placeholder="Search members..."
          className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-10 pr-4 text-sm text-gray-900 placeholder-gray-400 outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          data-testid="member-search"
        />
      </div>

      {/* Role tabs + Sort */}
      <div className="flex items-center justify-between">
        <div className="flex gap-1" data-testid="role-tabs">
          {ROLE_TABS.map((tab) => {
            const isActive = role === tab.value;
            const countKey = tab.value ?? 'all';
            const count = counts[countKey];
            return (
              <button
                key={tab.label}
                onClick={() => onRoleChange(tab.value)}
                className={cn(
                  'rounded-full px-3 py-1.5 text-xs font-medium transition-colors',
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                )}
                data-testid={`role-tab-${tab.value ?? 'all'}`}
              >
                {tab.label}
                {count != null && (
                  <span className={cn('ml-1', isActive ? 'text-gray-300' : 'text-gray-400')}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Sort dropdown */}
        <div className="relative" ref={sortRef} data-testid="member-sort">
          <button
            onClick={() => setIsSortOpen(!isSortOpen)}
            className="flex items-center gap-1.5 rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-200"
          >
            <span>{activeSort.label}</span>
            <svg
              className={cn('h-3.5 w-3.5 transition-transform', isSortOpen && 'rotate-180')}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {isSortOpen && (
            <div className="absolute right-0 z-10 mt-1 w-36 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
              {SORT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    onSortChange(option.value);
                    setIsSortOpen(false);
                  }}
                  className={cn(
                    'flex w-full items-center px-3 py-1.5 text-left text-xs',
                    sort === option.value
                      ? 'bg-gray-50 font-medium text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50',
                  )}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
