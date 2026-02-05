"""UserId value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserId:
    """
    Unique identifier for a User.

    This is a value object wrapping a UUID v4. It provides type safety
    and ensures we don't accidentally mix user IDs with other UUID types.
    """

    value: UUID

    def __str__(self) -> str:
        """Return string representation of the UUID."""
        return str(self.value)

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create a UserId from a string."""
        return cls(value=UUID(value))
