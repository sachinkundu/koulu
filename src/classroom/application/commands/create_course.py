"""Create course command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateCourseCommand:
    """Command to create a new course."""

    instructor_id: UUID
    title: str
    description: str | None = None
    cover_image_url: str | None = None
    estimated_duration: str | None = None
