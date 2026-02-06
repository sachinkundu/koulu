"""Update profile command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateProfileCommand:
    """Command to update user profile fields."""

    user_id: UUID
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    city: str | None = None
    country: str | None = None
    twitter_url: str | None = None
    linkedin_url: str | None = None
    instagram_url: str | None = None
    website_url: str | None = None
