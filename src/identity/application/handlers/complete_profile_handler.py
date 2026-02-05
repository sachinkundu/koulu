"""Complete profile command handler."""

import structlog

from src.identity.application.commands.complete_profile import CompleteProfileCommand
from src.identity.domain.exceptions import UserNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.services import IAvatarGenerator
from src.identity.domain.value_objects import DisplayName, UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class CompleteProfileHandler:
    """Handler for completing user profile."""

    def __init__(
        self,
        user_repository: IUserRepository,
        avatar_generator: IAvatarGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._avatar_generator = avatar_generator

    async def handle(self, command: CompleteProfileCommand) -> None:
        """
        Handle profile completion.

        Raises InvalidDisplayNameError if display name invalid.
        Raises UserNotFoundError if user doesn't exist.
        """
        logger.info("complete_profile_attempt", user_id=str(command.user_id))

        user_id = UserId(value=command.user_id)

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.error("complete_profile_user_not_found", user_id=str(command.user_id))
            raise UserNotFoundError(str(command.user_id))

        # Validate display name
        display_name = DisplayName(command.display_name)

        # Generate avatar if not provided
        avatar_url = command.avatar_url
        if avatar_url is None:
            avatar_url = self._avatar_generator.generate_from_initials(display_name.initials)

        # Complete profile
        user.complete_profile(display_name, avatar_url)
        await self._user_repository.save(user)

        # Publish domain events
        await event_bus.publish_all(user.clear_events())

        logger.info("complete_profile_success", user_id=str(command.user_id))
