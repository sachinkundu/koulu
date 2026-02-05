"""Complete profile command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompleteProfileCommand:
    """Command to complete user profile."""

    user_id: UUID
    display_name: str
    avatar_url: str | None = None
