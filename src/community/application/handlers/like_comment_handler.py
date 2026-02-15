"""Like comment command handler."""

import structlog

from src.community.application.commands import LikeCommentCommand
from src.community.domain.entities import Reaction
from src.community.domain.events import CommentLiked
from src.community.domain.exceptions import CommentNotFoundError
from src.community.domain.repositories import ICommentRepository, IReactionRepository
from src.community.domain.value_objects import CommentId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class LikeCommentHandler:
    """Handler for liking comments."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
        comment_repository: ICommentRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository
        self._comment_repository = comment_repository

    async def handle(self, command: LikeCommentCommand) -> None:
        """
        Handle liking a comment.

        Idempotent: if already liked, no-op (no error).

        Args:
            command: The like comment command

        Raises:
            CommentNotFoundError: If comment doesn't exist
        """
        logger.info(
            "like_comment_attempt",
            comment_id=str(command.comment_id),
            user_id=str(command.user_id),
        )

        comment_id = CommentId(command.comment_id)
        user_id = UserId(command.user_id)

        # Check comment exists
        comment = await self._comment_repository.get_by_id(comment_id)
        if comment is None:
            logger.warning("like_comment_not_found", comment_id=str(comment_id))
            raise CommentNotFoundError(str(comment_id))

        # Check if already liked (idempotent)
        existing = await self._reaction_repository.find_by_user_and_target(
            user_id=user_id,
            target_type="comment",
            target_id=command.comment_id,
        )
        if existing is not None:
            logger.info(
                "like_comment_already_liked", comment_id=str(comment_id), user_id=str(user_id)
            )
            return

        # Create reaction
        reaction = Reaction.create(
            user_id=user_id,
            target_type="comment",
            target_id=comment_id,
        )

        # Save reaction
        await self._reaction_repository.save(reaction)

        # Publish event
        await event_bus.publish_all(
            [
                CommentLiked(
                    reaction_id=reaction.id,
                    comment_id=comment_id,
                    user_id=user_id,
                    author_id=comment.author_id,
                )
            ]
        )

        logger.info("like_comment_success", comment_id=str(comment_id), user_id=str(user_id))
