"""Update lesson command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateLessonCommand:
    """Command to update a lesson."""

    lesson_id: UUID
    title: str | None = None
    content_type: str | None = None
    content: str | None = None
