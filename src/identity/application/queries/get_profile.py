"""Get profile query."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.identity.domain.entities import User
from src.identity.domain.exceptions import ProfileNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass(frozen=True)
class GetProfileQuery:
    """Query to get a user's profile."""

    user_id: UUID


class GetProfileHandler:
    """Handler for getting a user profile."""

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository

    async def handle(self, query: GetProfileQuery) -> User:
        """
        Handle getting user profile.

        Raises ProfileNotFoundError if user or profile doesn't exist.
        """
        logger.debug("get_profile", user_id=str(query.user_id))

        user_id = UserId(value=query.user_id)
        user = await self._user_repository.get_by_id(user_id)

        if user is None or user.profile is None:
            logger.error("get_profile_not_found", user_id=str(query.user_id))
            raise ProfileNotFoundError(str(query.user_id))

        return user
