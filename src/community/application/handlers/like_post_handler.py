"""Like post command handler."""

import structlog

from src.community.application.commands import LikePostCommand
from src.community.domain.entities import Reaction
from src.community.domain.events import PostLiked
from src.community.domain.exceptions import PostNotFoundError
from src.community.domain.repositories import IPostRepository, IReactionRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class LikePostHandler:
    """Handler for liking posts."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
        post_repository: IPostRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository
        self._post_repository = post_repository

    async def handle(self, command: LikePostCommand) -> None:
        """
        Handle liking a post.

        Idempotent: if already liked, no-op (no error).

        Args:
            command: The like post command

        Raises:
            PostNotFoundError: If post doesn't exist
        """
        logger.info(
            "like_post_attempt",
            post_id=str(command.post_id),
            user_id=str(command.user_id),
        )

        post_id = PostId(command.post_id)
        user_id = UserId(command.user_id)

        # Check post exists
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("like_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Check if already liked (idempotent)
        existing = await self._reaction_repository.find_by_user_and_target(
            user_id=user_id,
            target_type="post",
            target_id=command.post_id,
        )
        if existing is not None:
            logger.info("like_post_already_liked", post_id=str(post_id), user_id=str(user_id))
            return

        # Create reaction
        reaction = Reaction.create(
            user_id=user_id,
            target_type="post",
            target_id=post_id,
        )

        # Save reaction
        await self._reaction_repository.save(reaction)

        # Publish event manually (Reaction is immutable, no events list)
        await event_bus.publish_all(
            [
                PostLiked(
                    reaction_id=reaction.id,
                    post_id=post_id,
                    community_id=post.community_id,
                    user_id=user_id,
                    author_id=post.author_id,
                )
            ]
        )

        logger.info("like_post_success", post_id=str(post_id), user_id=str(user_id))
