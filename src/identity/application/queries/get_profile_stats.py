"""Get profile stats query."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import structlog

from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass(frozen=True)
class ProfileStats:
    """User profile statistics."""

    contribution_count: int
    joined_at: datetime


@dataclass(frozen=True)
class ActivityChartData:
    """30-day activity chart data."""

    days: list[datetime]  # List of dates
    counts: list[int]  # Activity count per day


@dataclass(frozen=True)
class GetProfileStatsQuery:
    """Query to get a user's profile statistics."""

    user_id: UUID


class GetProfileStatsHandler:
    """Handler for getting user profile statistics."""

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository

    async def handle(self, query: GetProfileStatsQuery) -> ProfileStats:
        """
        Handle getting user profile statistics.

        Raises ProfileNotFoundError if user doesn't exist.

        NOTE: Returns zero contributions until Community feature is implemented.
        """
        logger.debug("get_profile_stats", user_id=str(query.user_id))

        user_id = UserId(value=query.user_id)
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            logger.error("get_profile_stats_user_not_found", user_id=str(query.user_id))
            raise ProfileNotFoundError(str(query.user_id))

        # TODO: Once Community feature exists, count posts, comments, likes
        # For now, return zero contributions
        return ProfileStats(
            contribution_count=0,
            joined_at=user.created_at,
        )
