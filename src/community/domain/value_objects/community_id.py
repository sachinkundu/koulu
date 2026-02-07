"""CommunityId value object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CommunityId:
    """
    Community identifier value object.

    Wraps a UUID to provide type safety and domain meaning.
    """

    value: UUID

    def __str__(self) -> str:
        """Return the string representation of the UUID."""
        return str(self.value)
