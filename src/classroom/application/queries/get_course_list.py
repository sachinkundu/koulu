"""Get course list query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetCourseListQuery:
    """Query to list all courses."""

    requester_id: UUID
    include_deleted: bool = False
    limit: int = 50
    offset: int = 0
