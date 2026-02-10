import { useComments } from '../hooks';
import type { Comment } from '../types';
import { CommentCard } from './CommentCard';
import { AddCommentForm } from './AddCommentForm';

interface CommentThreadProps {
  postId: string;
  currentUserId?: string;
  isLocked: boolean;
}

function buildTree(comments: Comment[]): Map<string | null, Comment[]> {
  const tree = new Map<string | null, Comment[]>();
  for (const comment of comments) {
    const parentId = comment.parent_comment_id;
    const existing = tree.get(parentId) ?? [];
    existing.push(comment);
    tree.set(parentId, existing);
  }
  return tree;
}

function renderComments(
  tree: Map<string | null, Comment[]>,
  parentId: string | null,
  postId: string,
  currentUserId: string | undefined,
  isLocked: boolean,
  depth: number,
): JSX.Element[] {
  const children = tree.get(parentId) ?? [];
  return children.map((comment) => (
    <div key={comment.id}>
      <CommentCard
        comment={comment}
        postId={postId}
        currentUserId={currentUserId}
        isLocked={isLocked}
        depth={depth}
      />
      {renderComments(tree, comment.id, postId, currentUserId, isLocked, depth + 1)}
    </div>
  ));
}

export function CommentThread({ postId, currentUserId, isLocked }: CommentThreadProps): JSX.Element {
  const { comments, isLoading, error } = useComments(postId);

  return (
    <div data-testid="comment-thread">
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Comments {comments !== undefined ? `(${comments.length})` : ''}
      </h3>

      {/* Add comment form */}
      {!isLocked ? (
        <div className="mb-4">
          <AddCommentForm postId={postId} />
        </div>
      ) : (
        <div className="mb-4 rounded-md bg-gray-100 px-4 py-2 text-sm text-gray-600">
          Comments are disabled for this post.
        </div>
      )}

      {/* Comments list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded bg-gray-100" />
          ))}
        </div>
      ) : error !== null ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700" role="alert">
          Failed to load comments.
        </div>
      ) : comments === undefined || comments.length === 0 ? (
        <p className="text-sm text-gray-500">No comments yet. Be the first to comment!</p>
      ) : (
        <div className="divide-y" data-testid="comments-list">
          {renderComments(buildTree(comments), null, postId, currentUserId, isLocked, 0)}
        </div>
      )}
    </div>
  );
}
