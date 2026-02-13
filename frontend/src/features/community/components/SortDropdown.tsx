import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface SortDropdownProps {
  selectedSort: 'hot' | 'new' | 'top';
  onSortChange: (sort: 'hot' | 'new' | 'top') => void;
}

const SORT_OPTIONS: { value: 'hot' | 'new' | 'top'; label: string; icon: string }[] = [
  { value: 'hot', label: 'Default', icon: '⚡' },
  { value: 'new', label: 'New', icon: '🆕' },
  { value: 'top', label: 'Top', icon: '🔝' },
];

export function SortDropdown({ selectedSort, onSortChange }: SortDropdownProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeOption = SORT_OPTIONS.find((o) => o.value === selectedSort) ?? SORT_OPTIONS[0]!;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (dropdownRef.current !== null && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef} data-testid="sort-dropdown">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
        data-testid="sort-trigger"
      >
        <span>{activeOption.icon}</span>
        <span>{activeOption.label}</span>
        <svg
          className={cn('h-4 w-4 transition-transform', isOpen && 'rotate-180')}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 z-10 mt-2 w-40 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => {
                onSortChange(option.value);
                setIsOpen(false);
              }}
              className={cn(
                'flex w-full items-center gap-2 px-4 py-2 text-left text-sm',
                selectedSort === option.value
                  ? 'bg-yellow-50 font-medium text-gray-900'
                  : 'text-gray-700 hover:bg-gray-50'
              )}
              data-testid={`sort-${option.value}`}
            >
              <span>{option.icon}</span>
              <span>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
