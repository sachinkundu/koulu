"""Add module command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddModuleCommand:
    """Command to add a module to a course."""

    course_id: UUID
    title: str
    description: str | None = None
