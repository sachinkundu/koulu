"""Post aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.community.domain.events import (
    PostCreated,
    PostDeleted,
    PostEdited,
    PostLocked,
    PostUnlocked,
)
from src.community.domain.exceptions import (
    CannotLockPostError,
    InvalidImageUrlError,
    NotPostAuthorError,
    PostAlreadyDeletedError,
)
from src.community.domain.value_objects import (
    CategoryId,
    CommunityId,
    MemberRole,
    PostContent,
    PostId,
    PostTitle,
)
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass
class Post:
    """
    Post aggregate root.

    Represents a community post with title, content, and optional image.
    Enforces business rules for post creation, editing, and deletion.
    """

    id: PostId
    community_id: CommunityId
    author_id: UserId
    category_id: CategoryId
    title: PostTitle
    content: PostContent
    image_url: str | None = None
    is_pinned: bool = False
    pinned_at: datetime | None = None
    is_locked: bool = False
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    edited_at: datetime | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
        image_url: str | None = None,
    ) -> "Post":
        """
        Factory method to create a new post.

        Args:
            community_id: The community this post belongs to
            author_id: The user creating the post
            category_id: The category for this post
            title: The post title (already validated)
            content: The post content (already validated)
            image_url: Optional HTTPS URL to an image

        Returns:
            A new Post instance

        Raises:
            InvalidImageUrlError: If image_url is not HTTPS
        """
        # Validate image URL if provided
        if image_url is not None and not image_url.startswith("https://"):
            raise InvalidImageUrlError()

        post_id = PostId(value=uuid4())
        post = cls(
            id=post_id,
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
            image_url=image_url,
        )

        post._add_event(
            PostCreated(
                post_id=post_id,
                community_id=community_id,
                author_id=author_id,
                category_id=category_id,
                title=str(title),
                content=str(content),
                image_url=image_url,
            )
        )

        return post

    def edit(
        self,
        editor_id: UserId,
        editor_role: MemberRole,
        title: PostTitle | None = None,
        content: PostContent | None = None,
        image_url: str | None = None,
        category_id: CategoryId | None = None,
    ) -> list[str]:
        """
        Edit the post.

        Args:
            editor_id: The user editing the post
            editor_role: The role of the editor
            title: New title (optional)
            content: New content (optional)
            image_url: New image URL (optional)
            category_id: New category (optional)

        Returns:
            List of changed field names

        Raises:
            PostAlreadyDeletedError: If post is deleted
            NotPostAuthorError: If editor is not author and not admin/moderator
            InvalidImageUrlError: If image_url is not HTTPS
        """
        if self.is_deleted:
            raise PostAlreadyDeletedError()

        # Check permission: must be author or have elevated role
        if editor_id != self.author_id and not editor_role.can_delete_any_post():
            raise NotPostAuthorError()

        # Validate image URL if provided
        if image_url is not None and image_url != "" and not image_url.startswith("https://"):
            raise InvalidImageUrlError()

        # Track changed fields
        changed_fields: list[str] = []

        if title is not None and title != self.title:
            self.title = title
            changed_fields.append("title")

        if content is not None and content != self.content:
            self.content = content
            changed_fields.append("content")

        if image_url is not None and image_url != self.image_url:
            # Empty string means remove image
            self.image_url = image_url if image_url != "" else None
            changed_fields.append("image_url")

        if category_id is not None and category_id != self.category_id:
            self.category_id = category_id
            changed_fields.append("category_id")

        # Update timestamps and publish event if anything changed
        if changed_fields:
            self.edited_at = datetime.now(UTC)
            self._update_timestamp()
            self._add_event(
                PostEdited(post_id=self.id, editor_id=editor_id, changed_fields=changed_fields)
            )

        return changed_fields

    def delete(self, deleter_id: UserId) -> None:
        """
        Soft delete the post.

        Args:
            deleter_id: The user deleting the post

        Raises:
            PostAlreadyDeletedError: If already deleted
        """
        if self.is_deleted:
            raise PostAlreadyDeletedError()

        self.is_deleted = True
        self._update_timestamp()
        self._add_event(PostDeleted(post_id=self.id, deleted_by=deleter_id))

    def lock(self, locker_id: UserId, locker_role: MemberRole) -> None:
        """
        Lock the post to prevent new comments.

        Args:
            locker_id: The user locking the post
            locker_role: The role of the locker

        Raises:
            PostAlreadyDeletedError: If post is deleted
            CannotLockPostError: If user doesn't have permission
        """
        if self.is_deleted:
            raise PostAlreadyDeletedError()

        # Check permission: must be admin or moderator
        if not locker_role.can_lock_posts():
            raise CannotLockPostError()

        if not self.is_locked:
            self.is_locked = True
            self._update_timestamp()
            self._add_event(PostLocked(post_id=self.id, locked_by=locker_id))

    def unlock(self, unlocker_id: UserId, unlocker_role: MemberRole) -> None:
        """
        Unlock the post to allow comments again.

        Args:
            unlocker_id: The user unlocking the post
            unlocker_role: The role of the unlocker

        Raises:
            PostAlreadyDeletedError: If post is deleted
            CannotLockPostError: If user doesn't have permission
        """
        if self.is_deleted:
            raise PostAlreadyDeletedError()

        # Check permission: must be admin or moderator
        if not unlocker_role.can_lock_posts():
            raise CannotLockPostError()

        if self.is_locked:
            self.is_locked = False
            self._update_timestamp()
            self._add_event(PostUnlocked(post_id=self.id, unlocked_by=unlocker_id))

    @property
    def is_edited(self) -> bool:
        """Check if the post has been edited."""
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
        """Posts are equal if they have the same ID."""
        if not isinstance(other, Post):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on post ID."""
        return hash(self.id)
