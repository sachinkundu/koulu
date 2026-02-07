"""Lesson ID value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LessonId:
    """Unique identifier for a Lesson."""

    value: UUID

    def __str__(self) -> str:
        """Return string representation of the UUID."""
        return str(self.value)
