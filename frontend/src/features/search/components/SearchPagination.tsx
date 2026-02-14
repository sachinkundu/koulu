interface SearchPaginationProps {
  currentPage: number;
  totalResults: number;
  pageSize: number;
  hasMore: boolean;
  onPageChange: (page: number) => void;
}

export function SearchPagination({
  currentPage,
  totalResults,
  pageSize,
  hasMore,
  onPageChange,
}: SearchPaginationProps): JSX.Element | null {
  if (totalResults === 0) return null;

  const startIndex = (currentPage - 1) * pageSize + 1;
  const endIndex = Math.min(currentPage * pageSize, totalResults);

  return (
    <div className="mt-4 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3">
      <div className="flex items-center gap-2">
        <button
          type="button"
          disabled={currentPage === 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="rounded-full px-3 py-1 text-sm font-medium text-gray-600 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Previous
        </button>

        <span className="rounded-full bg-blue-600 px-3 py-1 text-sm font-medium text-white">
          {currentPage}
        </span>

        <button
          type="button"
          disabled={!hasMore}
          onClick={() => onPageChange(currentPage + 1)}
          className="rounded-full px-3 py-1 text-sm font-medium text-gray-600 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Next
        </button>
      </div>

      <span className="text-sm text-gray-500">
        {startIndex}-{endIndex} of {totalResults}
      </span>
    </div>
  );
}
