"""Mark lesson complete command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MarkLessonCompleteCommand:
    """Command to mark a lesson as complete."""

    user_id: UUID
    lesson_id: UUID
