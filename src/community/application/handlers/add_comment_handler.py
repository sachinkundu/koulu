"""Add comment command handler."""

import structlog

from src.community.application.commands import AddCommentCommand
from src.community.domain.entities import Comment
from src.community.domain.exceptions import (
    CommentNotFoundError,
    MaxReplyDepthExceededError,
    NotCommunityMemberError,
    PostLockedError,
    PostNotFoundError,
)
from src.community.domain.repositories import ICommentRepository, IMemberRepository, IPostRepository
from src.community.domain.value_objects import CommentContent, CommentId, PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class AddCommentHandler:
    """Handler for adding comments to posts."""

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

    async def handle(self, command: AddCommentCommand) -> CommentId:
        """
        Handle adding a comment.

        Args:
            command: The add comment command

        Returns:
            The created comment's ID

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If author is not a member
            PostLockedError: If post is locked
            MaxReplyDepthExceededError: If reply exceeds max depth
            CommentContentRequiredError: If content is empty
            CommentContentTooLongError: If content exceeds max length
        """
        logger.info(
            "add_comment_attempt",
            post_id=str(command.post_id),
            author_id=str(command.author_id),
        )

        post_id = PostId(command.post_id)
        author_id = UserId(command.author_id)

        # Load post to check existence and lock status
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("add_comment_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        if post.is_locked:
            logger.warning("add_comment_post_locked", post_id=str(post_id))
            raise PostLockedError()

        # Check author is a member
        member = await self._member_repository.get_by_user_and_community(
            author_id, post.community_id
        )
        if member is None:
            logger.warning("add_comment_not_member", author_id=str(author_id))
            raise NotCommunityMemberError()

        # Handle parent comment (threading)
        parent_comment_id = None
        if command.parent_comment_id is not None:
            parent_comment_id = CommentId(command.parent_comment_id)
            parent = await self._comment_repository.get_by_id(parent_comment_id)
            if parent is None:
                logger.warning("add_comment_parent_not_found", parent_id=str(parent_comment_id))
                raise CommentNotFoundError(str(parent_comment_id))

            # Max depth: 1 (comment -> reply, no nested replies)
            if parent.parent_comment_id is not None:
                logger.warning("add_comment_max_depth", parent_id=str(parent_comment_id))
                raise MaxReplyDepthExceededError()

        # Validate and create comment
        content = CommentContent(command.content)
        comment = Comment.create(
            post_id=post_id,
            author_id=author_id,
            content=content,
            community_id=post.community_id,
            parent_comment_id=parent_comment_id,
        )

        # Save comment
        await self._comment_repository.save(comment)

        # Publish domain events
        await event_bus.publish_all(comment.clear_events())

        logger.info("add_comment_success", comment_id=str(comment.id))
        return comment.id
