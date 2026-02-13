"""Get next incomplete lesson query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetNextIncompleteLessonQuery:
    """Query to get the next incomplete lesson (for 'Continue' button)."""

    user_id: UUID
    course_id: UUID
