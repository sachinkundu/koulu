"""Get lesson query."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetLessonQuery:
    """Query to get a lesson's content."""

    lesson_id: UUID
    user_id: UUID
