import { Link } from 'react-router-dom';
import type { Post } from '../types';

interface FeedPostCardProps {
  post: Post;
}

export function FeedPostCard({ post }: FeedPostCardProps): JSX.Element {
  // Truncate content to ~500 characters
  const truncatedContent =
    post.content.length > 500 ? `${post.content.slice(0, 500)}...` : post.content;

  return (
    <Link
      to={`/community/posts/${post.id}`}
      className="block rounded-lg bg-white p-6 shadow hover:shadow-md transition-shadow"
      data-testid={`post-card-${post.id}`}
    >
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {/* Author avatar */}
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium">
            {post.author?.display_name?.[0]?.toUpperCase() ?? 'U'}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">
                {post.author?.display_name ?? 'Unknown'}
              </span>
              {post.is_edited && (
                <span className="text-xs text-gray-500">(edited)</span>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <time dateTime={post.created_at}>
                {new Date(post.created_at).toLocaleDateString()}
              </time>
            </div>
          </div>
        </div>

        {/* Category badge */}
        {post.category !== undefined && (
          <div className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-sm">
            <span>{post.category.emoji}</span>
            <span className="text-gray-700">{post.category.name}</span>
          </div>
        )}
      </div>

      {/* Pinned indicator */}
      {post.is_pinned && (
        <div className="mb-2 flex items-center gap-1 text-sm font-medium text-primary-600">
          <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a.75.75 0 01.75.75v7.5h3.5a.75.75 0 010 1.5h-3.5v5.5a.75.75 0 01-1.5 0v-5.5h-3.5a.75.75 0 010-1.5h3.5v-7.5A.75.75 0 0110 2z" />
          </svg>
          <span>Pinned</span>
        </div>
      )}

      {/* Post title */}
      <h2 className="mb-2 text-lg font-semibold text-gray-900 hover:text-primary-600">
        {post.title}
      </h2>

      {/* Post content (truncated) */}
      <p className="mb-4 text-gray-700 whitespace-pre-wrap">{truncatedContent}</p>

      {/* Image thumbnail */}
      {post.image_url !== null && (
        <div className="mb-4">
          <img
            src={post.image_url}
            alt=""
            className="max-h-64 w-full rounded-lg object-cover"
          />
        </div>
      )}

      {/* Engagement row */}
      <div className="flex items-center gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
            />
          </svg>
          <span>{post.like_count}</span>
        </div>

        <div className="flex items-center gap-1">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span>{post.comment_count}</span>
        </div>
      </div>
    </Link>
  );
}
