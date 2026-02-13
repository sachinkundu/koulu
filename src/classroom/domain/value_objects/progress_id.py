"""ProgressId value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ProgressId:
    """Unique identifier for a Progress record."""

    value: UUID

    def __str__(self) -> str:
        """Return string representation of the UUID."""
        return str(self.value)
