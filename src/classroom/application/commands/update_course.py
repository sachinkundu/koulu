"""Update course command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateCourseCommand:
    """Command to update an existing course."""

    course_id: UUID
    editor_id: UUID
    title: str | None = None
    description: str | None = None
    cover_image_url: str | None = None
    estimated_duration: str | None = None
