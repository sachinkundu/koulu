interface LikeButtonProps {
  likeCount: number;
  isLiked: boolean;
  isLoading: boolean;
  onLike: () => void;
  onUnlike: () => void;
}

export function LikeButton({ likeCount, isLiked, isLoading, onLike, onUnlike }: LikeButtonProps): JSX.Element {
  const handleClick = (e: React.MouseEvent): void => {
    e.stopPropagation();
    if (isLoading) return;
    if (isLiked) {
      onUnlike();
    } else {
      onLike();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className={`flex items-center gap-1 text-sm transition-colors ${
        isLiked
          ? 'text-primary-600 font-medium'
          : 'text-gray-500 hover:text-primary-600'
      } disabled:opacity-50`}
      data-testid="like-button"
    >
      <svg
        className="h-5 w-5"
        fill={isLiked ? 'currentColor' : 'none'}
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
        />
      </svg>
      <span>{likeCount}</span>
    </button>
  );
}
