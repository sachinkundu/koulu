"""Search query definition."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SearchQuery:
    """Query to search members and posts."""

    community_id: UUID
    requester_id: UUID
    query: str
    search_type: str = "members"  # "members" or "posts"
    limit: int = 10
    offset: int = 0
