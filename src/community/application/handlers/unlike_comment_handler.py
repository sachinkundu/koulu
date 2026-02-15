"""Unlike comment command handler."""

import structlog

from src.community.application.commands import UnlikeCommentCommand
from src.community.domain.events import CommentUnliked
from src.community.domain.repositories import (
    ICommentRepository,
    IPostRepository,
    IReactionRepository,
)
from src.community.domain.value_objects import CommentId, CommunityId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnlikeCommentHandler:
    """Handler for unliking comments."""

    def __init__(
        self,
        reaction_repository: IReactionRepository,
        comment_repository: ICommentRepository,
        post_repository: IPostRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._reaction_repository = reaction_repository
        self._comment_repository = comment_repository
        self._post_repository = post_repository

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

        # Look up comment to get author_id and community_id
        comment = await self._comment_repository.get_by_id(CommentId(command.comment_id))
        author_id = comment.author_id if comment else user_id

        # Look up post to get community_id
        community_id = CommunityId(command.comment_id)
        if comment:
            post = await self._post_repository.get_by_id(comment.post_id)
            if post:
                community_id = post.community_id

        # Delete reaction
        await self._reaction_repository.delete(existing.id)

        # Publish event
        await event_bus.publish_all(
            [
                CommentUnliked(
                    comment_id=CommentId(command.comment_id),
                    community_id=community_id,
                    user_id=user_id,
                    author_id=author_id,
                )
            ]
        )

        logger.info(
            "unlike_comment_success", comment_id=str(command.comment_id), user_id=str(user_id)
        )
