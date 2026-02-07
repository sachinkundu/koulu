"""Comment aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.community.domain.events import CommentAdded, CommentDeleted, CommentEdited
from src.community.domain.exceptions import (
    CannotDeleteCommentError,
    CannotEditCommentError,
)
from src.community.domain.value_objects import (
    CommentContent,
    CommentId,
    MemberRole,
    PostId,
)
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass
class Comment:
    """
    Comment aggregate root.

    Represents a comment on a post or reply to another comment.
    Supports threading with max depth of 1 (comment -> reply, no nested replies).
    Supports soft deletion (content becomes "[deleted]" if comment has replies).
    """

    id: CommentId
    post_id: PostId
    author_id: UserId
    content: CommentContent
    parent_comment_id: CommentId | None = None
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    edited_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        post_id: PostId,
        author_id: UserId,
        content: CommentContent,
        parent_comment_id: CommentId | None = None,
    ) -> "Comment":
        """
        Factory method to create a new comment.

        Args:
            post_id: The post this comment belongs to
            author_id: The user creating the comment
            content: The comment content (already validated)
            parent_comment_id: Optional parent comment for threading

        Returns:
            A new Comment instance
        """
        comment_id = CommentId(value=uuid4())
        comment = cls(
            id=comment_id,
            post_id=post_id,
            author_id=author_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )

        comment._add_event(
            CommentAdded(
                comment_id=comment_id,
                post_id=post_id,
                author_id=author_id,
                content=str(content),
                parent_comment_id=parent_comment_id,
            )
        )

        return comment

    def edit(
        self,
        editor_id: UserId,
        editor_role: MemberRole,
        content: CommentContent,
    ) -> None:
        """
        Edit the comment content.

        Args:
            editor_id: The user editing the comment
            editor_role: The role of the editor
            content: New content

        Raises:
            CannotEditCommentError: If editor is not author and not admin/moderator
        """
        # Check permission: must be author or have elevated role
        if editor_id != self.author_id and not editor_role.can_delete_any_post():
            raise CannotEditCommentError()

        if content != self.content:
            self.content = content
            self.edited_at = datetime.now(UTC)
            self._update_timestamp()
            self._add_event(CommentEdited(comment_id=self.id, editor_id=editor_id))

    def delete(
        self,
        deleter_id: UserId,
        deleter_role: MemberRole,
        has_replies: bool,
    ) -> None:
        """
        Delete the comment.

        If comment has replies, performs soft delete (content becomes "[deleted]").
        Otherwise, marks for hard delete.

        Args:
            deleter_id: The user deleting the comment
            deleter_role: The role of the deleter
            has_replies: Whether this comment has any replies

        Raises:
            CannotDeleteCommentError: If deleter is not author and not admin/moderator
        """
        # Check permission: must be author or have elevated role
        if deleter_id != self.author_id and not deleter_role.can_delete_any_post():
            raise CannotDeleteCommentError()

        if has_replies:
            # Soft delete: replace content with placeholder
            from src.community.domain.value_objects.comment_content import CommentContent

            self.content = CommentContent("[deleted]")
            self.is_deleted = True
        else:
            # Mark for hard delete (repository will actually delete)
            self.is_deleted = True

        self._update_timestamp()
        self._add_event(CommentDeleted(comment_id=self.id, deleted_by=deleter_id))

    @property
    def is_edited(self) -> bool:
        """Check if the comment has been edited."""
        return self.edited_at is not None

    def _add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published after persistence."""
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def events(self) -> list[DomainEvent]:
        """Get pending domain events (read-only view)."""
        return self._events.copy()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Comments are equal if they have the same ID."""
        if not isinstance(other, Comment):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on comment ID."""
        return hash(self.id)
