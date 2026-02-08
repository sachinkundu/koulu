interface CreatePostInputProps {
  onClick: () => void;
}

export function CreatePostInput({ onClick }: CreatePostInputProps): JSX.Element {
  return (
    <button
      onClick={onClick}
      className="w-full rounded-lg bg-white p-4 text-left shadow hover:shadow-md transition-shadow"
      data-testid="create-post-input"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200 text-gray-600">
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </div>
        <span className="text-gray-500">Write something...</span>
      </div>
    </button>
  );
}
