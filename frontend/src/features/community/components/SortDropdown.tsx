import { cn } from '@/lib/utils';

interface SortDropdownProps {
  selectedSort: 'hot' | 'new' | 'top';
  onSortChange: (sort: 'hot' | 'new' | 'top') => void;
}

const SORT_OPTIONS: { value: 'hot' | 'new' | 'top'; label: string }[] = [
  { value: 'hot', label: 'Hot' },
  { value: 'new', label: 'New' },
  { value: 'top', label: 'Top' },
];

export function SortDropdown({ selectedSort, onSortChange }: SortDropdownProps): JSX.Element {
  return (
    <div className="flex gap-2" data-testid="sort-dropdown">
      {SORT_OPTIONS.map((option) => (
        <button
          key={option.value}
          onClick={() => onSortChange(option.value)}
          className={cn(
            'whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
            selectedSort === option.value
              ? 'bg-gray-900 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          )}
          data-testid={`sort-${option.value}`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
