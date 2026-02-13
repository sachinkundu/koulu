import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Avatar } from '@/components';
import { timeAgo } from '@/lib/timeAgo';
import type { Post } from '../types';
import { useLikePost } from '../hooks';
import { LikeButton } from './LikeButton';
import { PostDetailModal } from './PostDetailModal';

interface FeedPostCardProps {
  post: Post;
}

export function FeedPostCard({ post }: FeedPostCardProps): JSX.Element {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { like, unlike, isLiking } = useLikePost(post.id);
  const navigate = useNavigate();

  const handleAuthorClick = (e: React.MouseEvent): void => {
    e.stopPropagation();
    if (post.author?.id !== undefined) {
      navigate(`/profile/${post.author.id}`);
    }
  };

  const truncatedContent =
    post.content.length > 500 ? `${post.content.slice(0, 500)}...` : post.content;

  return (
    <>
      <article
        onClick={() => setIsModalOpen(true)}
        className="cursor-pointer rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm"
        data-testid={`post-card-${post.id}`}
      >
        {/* Header: Author + Category */}
        <header className="mb-3 flex items-start gap-3">
          <button type="button" onClick={handleAuthorClick} className="shrink-0" data-testid="post-author-avatar">
            <Avatar
              src={post.author?.avatar_url}
              alt={post.author?.display_name ?? 'Unknown'}
              fallback={post.author?.display_name ?? 'Unknown'}
              size="md"
            />
          </button>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleAuthorClick}
                className="text-base font-semibold text-gray-900 hover:underline"
                data-testid="post-author-name"
              >
                {post.author?.display_name ?? 'Unknown'}
              </button>
            </div>
            <p className="text-sm text-gray-500">
              {post.category !== undefined && (
                <>
                  <span>{post.category.name}</span>
                  <span> · </span>
                </>
              )}
              <time dateTime={post.created_at}>{timeAgo(post.created_at)}</time>
            </p>
          </div>

          {post.is_pinned && (
            <span className="flex shrink-0 items-center gap-1 text-sm text-gray-500">
              📌 <span className="hidden sm:inline">Pinned</span>
            </span>
          )}
        </header>

        {/* Title */}
        <h2 className="mb-2 text-lg font-bold text-gray-900">
          {post.title}
        </h2>

        {/* Content (truncated) */}
        <p className="mb-3 whitespace-pre-wrap text-base leading-relaxed text-gray-700">
          {truncatedContent}
        </p>
        {post.content.length > 500 && (
          <button
            className="mb-3 text-sm text-blue-600 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            See more
          </button>
        )}

        {/* Image */}
        {post.image_url !== null && (
          <div className="mb-3 overflow-hidden rounded-lg">
            <img
              src={post.image_url}
              alt="Post attachment"
              className="h-auto max-h-96 w-full object-cover"
              loading="lazy"
            />
          </div>
        )}

        {/* Engagement Footer */}
        <footer className="flex items-center gap-4 border-t border-gray-100 pt-3">
          <LikeButton
            likeCount={post.like_count}
            isLiked={post.liked_by_current_user === true}
            isLoading={isLiking}
            onLike={like}
            onUnlike={unlike}
          />

          <button
            className="flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-blue-600"
            onClick={(e) => e.stopPropagation()}
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <span>{post.comment_count}</span>
          </button>

          {post.is_edited && (
            <span className="ml-auto text-xs text-gray-400">(edited)</span>
          )}
        </footer>
      </article>

      {/* Post detail modal */}
      {isModalOpen && (
        <PostDetailModal
          postId={post.id}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
}
