import { cn } from '@/lib/utils';
import { useCategories } from '../hooks';

interface CategoryTabsProps {
  selectedCategoryId: string | null;
  onCategoryChange: (categoryId: string | null) => void;
}

export function CategoryTabs({ selectedCategoryId, onCategoryChange }: CategoryTabsProps): JSX.Element {
  const { categories, isLoading } = useCategories();

  if (isLoading) {
    return (
      <nav className="flex gap-2 overflow-x-auto pb-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-9 w-20 shrink-0 animate-pulse rounded-full bg-gray-200" />
        ))}
      </nav>
    );
  }

  return (
    <nav
      className="flex gap-2 overflow-x-auto pb-1"
      style={{ scrollbarWidth: 'none' }}
      data-testid="category-tabs"
    >
      {/* All category option */}
      <button
        onClick={() => onCategoryChange(null)}
        className={cn(
          'shrink-0 whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
          selectedCategoryId === null
            ? 'bg-gray-900 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        )}
        data-testid="category-tab-all"
      >
        All
      </button>

      {/* Category pills */}
      {categories?.map((category) => (
        <button
          key={category.id}
          onClick={() => onCategoryChange(category.id)}
          className={cn(
            'flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
            selectedCategoryId === category.id
              ? 'bg-gray-900 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          )}
          data-testid={`category-tab-${category.slug}`}
        >
          {category.emoji !== '' && <span>{category.emoji}</span>}
          <span>{category.name}</span>
        </button>
      ))}

      {/* More button */}
      {categories !== undefined && categories.length > 6 && (
        <button className="shrink-0 whitespace-nowrap rounded-full bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200">
          More...
        </button>
      )}
    </nav>
  );
}
