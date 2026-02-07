"""Community application commands."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePostCommand:
    """Command to create a new post."""

    community_id: UUID
    author_id: UUID
    category_id: UUID | None  # If None, use category by name
    category_name: str | None  # Alternative to category_id
    title: str
    content: str
    image_url: str | None = None


@dataclass(frozen=True)
class UpdatePostCommand:
    """Command to update an existing post."""

    post_id: UUID
    editor_id: UUID
    title: str | None = None
    content: str | None = None
    image_url: str | None = None
    category_id: UUID | None = None


@dataclass(frozen=True)
class DeletePostCommand:
    """Command to delete a post."""

    post_id: UUID
    deleter_id: UUID


@dataclass(frozen=True)
class LockPostCommand:
    """Command to lock a post."""

    post_id: UUID
    locker_id: UUID


@dataclass(frozen=True)
class UnlockPostCommand:
    """Command to unlock a post."""

    post_id: UUID
    unlocker_id: UUID


@dataclass(frozen=True)
class AddCommentCommand:
    """Command to add a comment to a post."""

    post_id: UUID
    author_id: UUID
    content: str
    parent_comment_id: UUID | None = None


@dataclass(frozen=True)
class EditCommentCommand:
    """Command to edit a comment."""

    comment_id: UUID
    editor_id: UUID
    content: str


@dataclass(frozen=True)
class DeleteCommentCommand:
    """Command to delete a comment."""

    comment_id: UUID
    deleter_id: UUID


@dataclass(frozen=True)
class LikePostCommand:
    """Command to like a post."""

    post_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class UnlikePostCommand:
    """Command to unlike a post."""

    post_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class LikeCommentCommand:
    """Command to like a comment."""

    comment_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class UnlikeCommentCommand:
    """Command to unlike a comment."""

    comment_id: UUID
    user_id: UUID
