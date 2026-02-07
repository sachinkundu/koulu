"""CourseId value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CourseId:
    """Unique identifier for a Course."""

    value: UUID

    def __str__(self) -> str:
        """Return string representation of the UUID."""
        return str(self.value)
