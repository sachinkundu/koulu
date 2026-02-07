"""Unlike post command handler."""

import structlog

from src.community.application.commands import UnlikePostCommand
from src.community.domain.events import PostUnliked
from src.community.domain.repositories import IReactionRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnlikePostHandler:
    """Handler for unliking posts."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository

    async def handle(self, command: UnlikePostCommand) -> None:
        """
        Handle unliking a post.

        Idempotent: if not liked, no-op (no error).

        Args:
            command: The unlike post command
        """
        logger.info(
            "unlike_post_attempt",
            post_id=str(command.post_id),
            user_id=str(command.user_id),
        )

        user_id = UserId(command.user_id)

        # Find existing reaction
        existing = await self._reaction_repository.find_by_user_and_target(
            user_id=user_id,
            target_type="post",
            target_id=command.post_id,
        )
        if existing is None:
            logger.info("unlike_post_not_liked", post_id=str(command.post_id), user_id=str(user_id))
            return

        # Delete reaction
        await self._reaction_repository.delete(existing.id)

        # Publish event
        await event_bus.publish_all(
            [
                PostUnliked(
                    post_id=PostId(command.post_id),
                    user_id=user_id,
                )
            ]
        )

        logger.info("unlike_post_success", post_id=str(command.post_id), user_id=str(user_id))
