"""Update profile command handler."""

import structlog

from src.identity.application.commands.update_profile import UpdateProfileCommand
from src.identity.domain.exceptions import ProfileNotFoundError, UserNotFoundError
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.services import IAvatarGenerator
from src.identity.domain.value_objects import (
    Bio,
    DisplayName,
    Location,
    SocialLinks,
    UserId,
)
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UpdateProfileHandler:
    """Handler for updating user profile."""

    def __init__(
        self,
        user_repository: IUserRepository,
        avatar_generator: IAvatarGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._avatar_generator = avatar_generator

    async def handle(self, command: UpdateProfileCommand) -> None:
        """
        Handle profile update.

        Raises InvalidDisplayNameError if display name invalid.
        Raises InvalidBioError if bio invalid.
        Raises InvalidLocationError if location invalid.
        Raises InvalidSocialLinkError if social link invalid.
        Raises ProfileNotFoundError if profile doesn't exist.
        Raises UserNotFoundError if user doesn't exist.
        """
        logger.info("update_profile_attempt", user_id=str(command.user_id))

        user_id = UserId(value=command.user_id)

        # Get user
        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            logger.error("update_profile_user_not_found", user_id=str(command.user_id))
            raise UserNotFoundError(str(command.user_id))

        if user.profile is None:
            logger.error("update_profile_profile_not_found", user_id=str(command.user_id))
            raise ProfileNotFoundError(str(command.user_id))

        # Build value objects from command fields
        display_name = (
            DisplayName(command.display_name) if command.display_name is not None else None
        )
        bio = Bio(command.bio) if command.bio is not None else None

        # Handle location (both city and country required together)
        location = None
        if command.city is not None or command.country is not None:
            if command.city is None or command.country is None:
                # This will trigger Location validation error
                location = Location(city=command.city or "", country=command.country or "")
            else:
                location = Location(city=command.city, country=command.country)

        # Handle social links
        social_links = None
        if any(
            [command.twitter_url, command.linkedin_url, command.instagram_url, command.website_url]
        ):
            social_links = SocialLinks(
                twitter_url=command.twitter_url,
                linkedin_url=command.linkedin_url,
                instagram_url=command.instagram_url,
                website_url=command.website_url,
            )

        # Handle avatar_url - if empty string, regenerate from initials
        avatar_url = command.avatar_url
        if avatar_url == "":
            # User is clearing the avatar - regenerate from initials
            if display_name is not None:
                avatar_url = self._avatar_generator.generate_from_initials(display_name.initials)
            elif user.profile.display_name is not None:
                avatar_url = self._avatar_generator.generate_from_initials(
                    user.profile.display_name.initials
                )
            else:
                # Profile incomplete, can't regenerate
                avatar_url = None

        # Update profile
        changed_fields = user.update_profile(
            display_name=display_name,
            avatar_url=avatar_url,
            bio=bio,
            location=location,
            social_links=social_links,
        )

        if changed_fields:
            await self._user_repository.save(user)

            # Publish domain events
            await event_bus.publish_all(user.clear_events())

            logger.info(
                "update_profile_success",
                user_id=str(command.user_id),
                changed_fields=changed_fields,
            )
        else:
            logger.info("update_profile_no_changes", user_id=str(command.user_id))
