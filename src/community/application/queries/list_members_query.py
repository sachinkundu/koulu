"""List members query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListMembersQuery:
    """Query to list members of a community directory."""

    community_id: UUID
    requester_id: UUID
    sort: str = "most_recent"
    limit: int = 20
    cursor: str | None = None
