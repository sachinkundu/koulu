"""Edit comment command handler."""

import structlog

from src.community.application.commands import EditCommentCommand
from src.community.domain.exceptions import (
    CommentNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.repositories import ICommentRepository, IMemberRepository, IPostRepository
from src.community.domain.value_objects import CommentContent, CommentId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class EditCommentHandler:
    """Handler for editing comments."""

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

    async def handle(self, command: EditCommentCommand) -> None:
        """
        Handle editing a comment.

        Args:
            command: The edit comment command

        Raises:
            CommentNotFoundError: If comment doesn't exist
            NotCommunityMemberError: If editor is not a member
            CannotEditCommentError: If editor lacks permission
            CommentContentRequiredError: If content is empty
            CommentContentTooLongError: If content exceeds max length
        """
        logger.info(
            "edit_comment_attempt",
            comment_id=str(command.comment_id),
            editor_id=str(command.editor_id),
        )

        comment_id = CommentId(command.comment_id)
        editor_id = UserId(command.editor_id)

        # Load comment
        comment = await self._comment_repository.get_by_id(comment_id)
        if comment is None:
            logger.warning("edit_comment_not_found", comment_id=str(comment_id))
            raise CommentNotFoundError(str(comment_id))

        # Load the post to get the community ID
        post = await self._post_repository.get_by_id(comment.post_id)
        if post is None:
            logger.warning("edit_comment_post_not_found", post_id=str(comment.post_id))
            raise CommentNotFoundError(str(comment_id))

        # Get editor's membership
        member = await self._member_repository.get_by_user_and_community(
            editor_id, post.community_id
        )
        if member is None:
            logger.warning("edit_comment_not_member", editor_id=str(editor_id))
            raise NotCommunityMemberError()

        # Validate and edit comment (domain entity checks permission)
        content = CommentContent(command.content)
        comment.edit(editor_id, member.role, content)

        # Save comment
        await self._comment_repository.save(comment)

        # Publish domain events
        await event_bus.publish_all(comment.clear_events())

        logger.info("edit_comment_success", comment_id=str(comment_id))
