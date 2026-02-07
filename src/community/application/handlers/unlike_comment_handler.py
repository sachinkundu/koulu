"""Unlike comment command handler."""

import structlog

from src.community.application.commands import UnlikeCommentCommand
from src.community.domain.events import CommentUnliked
from src.community.domain.repositories import IReactionRepository
from src.community.domain.value_objects import CommentId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnlikeCommentHandler:
    """Handler for unliking comments."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository

    async def handle(self, command: UnlikeCommentCommand) -> None:
        """
        Handle unliking a comment.

        Idempotent: if not liked, no-op (no error).

        Args:
            command: The unlike comment command
        """
        logger.info(
            "unlike_comment_attempt",
            comment_id=str(command.comment_id),
            user_id=str(command.user_id),
        )

        user_id = UserId(command.user_id)

        # Find existing reaction
        existing = await self._reaction_repository.find_by_user_and_target(
            user_id=user_id,
            target_type="comment",
            target_id=command.comment_id,
        )
        if existing is None:
            logger.info(
                "unlike_comment_not_liked", comment_id=str(command.comment_id), user_id=str(user_id)
            )
            return

        # Delete reaction
        await self._reaction_repository.delete(existing.id)

        # Publish event
        await event_bus.publish_all(
            [
                CommentUnliked(
                    comment_id=CommentId(command.comment_id),
                    user_id=user_id,
                )
            ]
        )

        logger.info(
            "unlike_comment_success", comment_id=str(command.comment_id), user_id=str(user_id)
        )
