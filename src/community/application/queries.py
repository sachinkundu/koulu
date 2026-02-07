"""Community application queries."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetPostQuery:
    """Query to get a post by ID."""

    post_id: UUID
    requester_id: UUID | None = None  # For permission checking


@dataclass(frozen=True)
class GetPostCommentsQuery:
    """Query to get comments for a post."""

    post_id: UUID
    limit: int = 100
    offset: int = 0
