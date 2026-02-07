"""Get course details query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetCourseDetailsQuery:
    """Query to get course details."""

    course_id: UUID
    requester_id: UUID
