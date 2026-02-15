"""Community domain events."""

from dataclasses import dataclass
from datetime import UTC, datetime

from src.community.domain.value_objects import (
    CategoryId,
    CommentId,
    CommunityId,
    PostId,
    ReactionId,
)
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True)
class PostCreated(DomainEvent):
    """Event published when a post is created."""

    post_id: PostId
    community_id: CommunityId
    author_id: UserId
    category_id: CategoryId
    title: str
    content: str
    image_url: str | None
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostCreated"


@dataclass(frozen=True)
class PostEdited(DomainEvent):
    """Event published when a post is edited."""

    post_id: PostId
    editor_id: UserId
    changed_fields: list[str]
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostEdited"


@dataclass(frozen=True)
class PostDeleted(DomainEvent):
    """Event published when a post is deleted."""

    post_id: PostId
    deleted_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostDeleted"


@dataclass(frozen=True)
class PostPinned(DomainEvent):
    """Event published when a post is pinned."""

    post_id: PostId
    pinned_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostPinned"


@dataclass(frozen=True)
class PostUnpinned(DomainEvent):
    """Event published when a post is unpinned."""

    post_id: PostId
    unpinned_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostUnpinned"


@dataclass(frozen=True)
class PostLocked(DomainEvent):
    """Event published when a post is locked."""

    post_id: PostId
    locked_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostLocked"


@dataclass(frozen=True)
class PostUnlocked(DomainEvent):
    """Event published when a post is unlocked."""

    post_id: PostId
    unlocked_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostUnlocked"


@dataclass(frozen=True)
class CategoryCreated(DomainEvent):
    """Event published when a category is created."""

    category_id: CategoryId
    community_id: CommunityId
    name: str
    slug: str
    created_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CategoryCreated"


@dataclass(frozen=True)
class CategoryUpdated(DomainEvent):
    """Event published when a category is updated."""

    category_id: CategoryId
    updated_by: UserId
    changed_fields: list[str]
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CategoryUpdated"


@dataclass(frozen=True)
class CategoryDeleted(DomainEvent):
    """Event published when a category is deleted."""

    category_id: CategoryId
    deleted_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CategoryDeleted"


@dataclass(frozen=True)
class CommentAdded(DomainEvent):
    """Event published when a comment is added to a post."""

    comment_id: CommentId
    post_id: PostId
    author_id: UserId
    content: str
    parent_comment_id: CommentId | None
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CommentAdded"


@dataclass(frozen=True)
class CommentEdited(DomainEvent):
    """Event published when a comment is edited."""

    comment_id: CommentId
    editor_id: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CommentEdited"


@dataclass(frozen=True)
class CommentDeleted(DomainEvent):
    """Event published when a comment is deleted."""

    comment_id: CommentId
    deleted_by: UserId
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CommentDeleted"


@dataclass(frozen=True)
class PostLiked(DomainEvent):
    """Event published when a post is liked."""

    reaction_id: ReactionId
    post_id: PostId
    user_id: UserId
    author_id: UserId  # content author (for gamification)
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostLiked"


@dataclass(frozen=True)
class PostUnliked(DomainEvent):
    """Event published when a post is unliked."""

    post_id: PostId
    user_id: UserId
    author_id: UserId  # content author (for gamification)
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostUnliked"


@dataclass(frozen=True)
class CommentLiked(DomainEvent):
    """Event published when a comment is liked."""

    reaction_id: ReactionId
    comment_id: CommentId
    user_id: UserId
    author_id: UserId  # content author (for gamification)
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CommentLiked"


@dataclass(frozen=True)
class CommentUnliked(DomainEvent):
    """Event published when a comment is unliked."""

    comment_id: CommentId
    user_id: UserId
    author_id: UserId  # content author (for gamification)
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "CommentUnliked"
