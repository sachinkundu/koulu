"""Profile entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.identity.domain.value_objects import DisplayName, UserId


@dataclass
class Profile:
    """
    User profile entity.

    Contains public-facing information about a user.
    This is a 1:1 relationship with User and is part of the User aggregate.
    """

    user_id: UserId
    display_name: DisplayName | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_complete: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def complete(
        self,
        display_name: DisplayName,
        avatar_url: str | None = None,
    ) -> None:
        """
        Complete the profile with required information.

        Args:
            display_name: The user's chosen display name
            avatar_url: Optional URL to the user's avatar
        """
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.is_complete = True
        self.updated_at = datetime.now(UTC)

    def update(
        self,
        display_name: DisplayName | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
    ) -> None:
        """
        Update profile fields.

        Args:
            display_name: New display name (if provided)
            avatar_url: New avatar URL (if provided)
            bio: New bio (if provided)
        """
        if display_name is not None:
            self.display_name = display_name
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if bio is not None:
            self.bio = bio
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Profiles are equal if they belong to the same user."""
        if not isinstance(other, Profile):
            return NotImplemented
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        """Hash based on user ID."""
        return hash(self.user_id)
