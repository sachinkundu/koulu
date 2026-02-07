"""Community domain events."""

from dataclasses import dataclass
from datetime import UTC, datetime

from src.community.domain.value_objects import CategoryId, CommunityId, PostId
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
