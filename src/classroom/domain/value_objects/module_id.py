"""Module ID value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ModuleId:
    """Unique identifier for a Module."""

    value: UUID

    def __str__(self) -> str:
        """Return string representation of the UUID."""
        return str(self.value)
