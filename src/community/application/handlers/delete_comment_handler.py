"""Delete comment command handler."""

import structlog

from src.community.application.commands import DeleteCommentCommand
from src.community.domain.exceptions import (
    CommentNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import ICommentRepository, IMemberRepository, IPostRepository
from src.community.domain.value_objects import CommentId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class DeleteCommentHandler:
    """Handler for deleting comments."""

    def __init__(
        self,
        comment_repository: ICommentRepository,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._comment_repository = comment_repository
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: DeleteCommentCommand) -> None:
        """
        Handle deleting a comment.

        If the comment has replies, performs soft delete (content becomes "[deleted]").
        Otherwise, performs hard delete.

        Args:
            command: The delete comment command

        Raises:
            CommentNotFoundError: If comment doesn't exist
            NotCommunityMemberError: If deleter is not a member
            CannotDeleteCommentError: If deleter lacks permission
        """
        logger.info(
            "delete_comment_attempt",
            comment_id=str(command.comment_id),
            deleter_id=str(command.deleter_id),
        )

        comment_id = CommentId(command.comment_id)
        deleter_id = UserId(command.deleter_id)

        # Load comment
        comment = await self._comment_repository.get_by_id(comment_id)
        if comment is None:
            logger.warning("delete_comment_not_found", comment_id=str(comment_id))
            raise CommentNotFoundError(str(comment_id))

        # Load the post to get the community ID
        post = await self._post_repository.get_by_id(comment.post_id)
        if post is None:
            logger.warning("delete_comment_post_not_found", post_id=str(comment.post_id))
            raise CommentNotFoundError(str(comment_id))

        # Get deleter's membership
        member = await self._member_repository.get_by_user_and_community(
            deleter_id, post.community_id
        )
        if member is None:
            logger.warning("delete_comment_not_member", deleter_id=str(deleter_id))
            raise NotCommunityMemberError()

        # Check if comment has replies
        has_replies = await self._comment_repository.has_replies(comment.id)

        # Delete comment (domain entity checks permission)
        comment.delete(deleter_id, member.role, has_replies)

        if has_replies:
            # Soft delete: save updated comment with "[deleted]" content
            await self._comment_repository.save(comment)
        else:
            # Hard delete: remove from database
            await self._comment_repository.delete(comment.id)

        # Publish domain events
        await event_bus.publish_all(comment.clear_events())

        logger.info("delete_comment_success", comment_id=str(comment_id), soft_delete=has_replies)
