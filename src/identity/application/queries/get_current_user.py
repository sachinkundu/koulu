"""Get current user query."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.identity.domain.entities import User
from src.identity.domain.exceptions import UserNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass(frozen=True)
class GetCurrentUserQuery:
    """Query to get current authenticated user."""

    user_id: UUID


class GetCurrentUserHandler:
    """Handler for getting current user."""

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository

    async def handle(self, query: GetCurrentUserQuery) -> User:
        """
        Handle getting current user.

        Raises UserNotFoundError if user doesn't exist.
        """
        logger.debug("get_current_user", user_id=str(query.user_id))

        user_id = UserId(value=query.user_id)
        user = await self._user_repository.get_by_id(user_id)

        if user is None:
            logger.error("get_current_user_not_found", user_id=str(query.user_id))
            raise UserNotFoundError(str(query.user_id))

        return user
