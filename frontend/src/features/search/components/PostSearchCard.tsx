import { useNavigate } from 'react-router-dom';
import { HeartIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline';
import { Avatar } from '@/components/Avatar';
import type { PostSearchItem } from '../types';

function relativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;

  return date.toLocaleDateString();
}

interface PostSearchCardProps {
  post: PostSearchItem;
}

export function PostSearchCard({ post }: PostSearchCardProps): JSX.Element {
  const navigate = useNavigate();
  const authorName = post.author_name ?? 'Unknown';

  return (
    <button
      type="button"
      data-testid="post-search-card"
      onClick={() => navigate(`/community/posts/${post.id}`)}
      className="flex w-full flex-col gap-3 rounded-lg border border-gray-200 bg-white p-4 text-left transition-shadow hover:shadow-sm"
    >
      {/* Title */}
      <h3 className="text-sm font-semibold text-gray-900">{post.title}</h3>

      {/* Body snippet */}
      <p className="line-clamp-3 text-sm leading-relaxed text-gray-600">
        {post.body_snippet}
      </p>

      {/* Footer: author, category, time, engagement */}
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <Avatar
            src={post.author_avatar_url}
            alt={authorName}
            size="xs"
            fallback={authorName}
          />
          <span>{authorName}</span>
        </div>

        {post.category_name != null && (
          <>
            <span className="text-gray-300">|</span>
            <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
              {post.category_emoji != null && (
                <span>{post.category_emoji}</span>
              )}
              {post.category_name}
            </span>
          </>
        )}

        <span className="text-gray-300">|</span>
        <time dateTime={post.created_at}>{relativeTime(post.created_at)}</time>

        <div className="ml-auto flex items-center gap-3">
          <span className="flex items-center gap-1">
            <HeartIcon className="h-3.5 w-3.5" />
            {post.like_count}
          </span>
          <span className="flex items-center gap-1">
            <ChatBubbleLeftIcon className="h-3.5 w-3.5" />
            {post.comment_count}
          </span>
        </div>
      </div>
    </button>
  );
}
