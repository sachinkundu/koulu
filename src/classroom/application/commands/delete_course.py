"""Delete course command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteCourseCommand:
    """Command to soft delete a course."""

    course_id: UUID
    deleter_id: UUID
