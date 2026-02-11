import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Avatar } from '@/components';
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

  // Truncate content to ~500 characters
  const truncatedContent =
    post.content.length > 500 ? `${post.content.slice(0, 500)}...` : post.content;

  return (
    <>
      <div
        onClick={() => setIsModalOpen(true)}
        className="cursor-pointer rounded-lg bg-white p-6 shadow hover:shadow-md transition-shadow"
        data-testid={`post-card-${post.id}`}
      >
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          {/* Author avatar */}
          <button type="button" onClick={handleAuthorClick} className="shrink-0" data-testid="post-author-avatar">
            <Avatar
              src={post.author?.avatar_url}
              alt={post.author?.display_name ?? 'Unknown'}
              fallback={post.author?.display_name ?? 'Unknown'}
              size="md"
            />
          </button>

          <div>
            <div className="flex items-center gap-2">
              <button type="button" onClick={handleAuthorClick} className="font-medium text-gray-900 hover:underline" data-testid="post-author-name">
                {post.author?.display_name ?? 'Unknown'}
              </button>
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
        <LikeButton
          likeCount={post.like_count}
          isLiked={post.liked_by_current_user === true}
          isLoading={isLiking}
          onLike={like}
          onUnlike={unlike}
        />

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
    </div>

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
