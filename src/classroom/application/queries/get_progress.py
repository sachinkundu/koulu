"""Get progress query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetProgressQuery:
    """Query to get a member's progress on a course."""

    user_id: UUID
    course_id: UUID
