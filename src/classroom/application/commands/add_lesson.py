"""Add lesson command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddLessonCommand:
    """Command to add a lesson to a module."""

    module_id: UUID
    title: str
    content_type: str
    content: str
