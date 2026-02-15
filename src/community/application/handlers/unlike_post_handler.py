"""Unlike post command handler."""

import structlog

from src.community.application.commands import UnlikePostCommand
from src.community.domain.events import PostUnliked
from src.community.domain.repositories import IPostRepository, IReactionRepository
from src.community.domain.value_objects import CommunityId, PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnlikePostHandler:
    """Handler for unliking posts."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
        post_repository: IPostRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository
        self._post_repository = post_repository

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

        # Look up post to get author_id
        post = await self._post_repository.get_by_id(PostId(command.post_id))
        author_id = post.author_id if post else user_id

        # Delete reaction
        await self._reaction_repository.delete(existing.id)

        # Publish event
        await event_bus.publish_all(
            [
                PostUnliked(
                    post_id=PostId(command.post_id),
                    community_id=post.community_id if post else CommunityId(command.post_id),
                    user_id=user_id,
                    author_id=author_id,
                )
            ]
        )

        logger.info("unlike_post_success", post_id=str(command.post_id), user_id=str(user_id))
