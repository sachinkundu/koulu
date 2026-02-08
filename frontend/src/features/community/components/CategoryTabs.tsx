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
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-9 w-24 animate-pulse rounded-full bg-gray-200" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-2 overflow-x-auto pb-2" data-testid="category-tabs">
      {/* All category option */}
      <button
        onClick={() => onCategoryChange(null)}
        className={cn(
          'whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
          selectedCategoryId === null
            ? 'bg-gray-900 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
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
            'flex items-center gap-2 whitespace-nowrap rounded-full px-4 py-2 text-sm font-medium transition-colors',
            selectedCategoryId === category.id
              ? 'bg-gray-900 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          )}
          data-testid={`category-tab-${category.slug}`}
        >
          <span>{category.emoji}</span>
          <span>{category.name}</span>
        </button>
      ))}
    </div>
  );
}
