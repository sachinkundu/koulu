"""Delete lesson command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteLessonCommand:
    """Command to soft delete a lesson."""

    lesson_id: UUID
