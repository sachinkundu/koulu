"""Start course command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class StartCourseCommand:
    """Command to start a course (create progress)."""

    user_id: UUID
    course_id: UUID
