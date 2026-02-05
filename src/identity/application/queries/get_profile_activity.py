"""Get profile activity query."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import structlog

from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass(frozen=True)
class ActivityItem:
    """Single activity item (placeholder for Community feature)."""

    id: str
    type: str  # "post", "comment", "like", etc.
    content: str
    created_at: datetime


@dataclass(frozen=True)
class ProfileActivity:
    """User profile activity data."""

    items: list[ActivityItem]
    total_count: int


@dataclass(frozen=True)
class GetProfileActivityQuery:
    """Query to get a user's activity feed."""

    user_id: UUID
    limit: int = 20
    offset: int = 0


class GetProfileActivityHandler:
    """Handler for getting user profile activity."""

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository

    async def handle(self, query: GetProfileActivityQuery) -> ProfileActivity:
        """
        Handle getting user profile activity.

        Raises ProfileNotFoundError if user doesn't exist.

        NOTE: Returns empty activity until Community feature is implemented.
        """
        logger.debug("get_profile_activity", user_id=str(query.user_id))

        # Verify user exists
        user_id = UserId(value=query.user_id)
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            logger.error("get_profile_activity_user_not_found", user_id=str(query.user_id))
            raise ProfileNotFoundError(str(query.user_id))

        # TODO: Once Community feature exists, query posts, comments, likes
        # For now, return empty activity
        return ProfileActivity(items=[], total_count=0)
