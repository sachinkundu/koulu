"""Delete post command handler."""

import structlog

from src.community.application.commands import DeletePostCommand
from src.community.domain.exceptions import (
    CannotDeletePostError,
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class DeletePostHandler:
    """Handler for deleting posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: DeletePostCommand) -> None:
        """
        Handle post deletion.

        Args:
            command: The delete post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If deleter is not a member
            CannotDeletePostError: If deleter lacks permission
        """
        logger.info(
            "delete_post_attempt",
            post_id=str(command.post_id),
            deleter_id=str(command.deleter_id),
        )

        post_id = PostId(command.post_id)
        deleter_id = UserId(command.deleter_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("delete_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get deleter's membership
        member = await self._member_repository.get_by_user_and_community(
            deleter_id, post.community_id
        )
        if member is None:
            logger.warning("delete_post_not_member", deleter_id=str(deleter_id))
            raise NotCommunityMemberError()

        # Check permission: must be author or admin/moderator
        if deleter_id != post.author_id and not member.role.can_delete_any_post():
            logger.warning(
                "delete_post_permission_denied",
                deleter_id=str(deleter_id),
                author_id=str(post.author_id),
                role=member.role.value,
            )
            raise CannotDeletePostError()

        # Delete the post
        post.delete(deleter_id)
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("delete_post_success", post_id=str(post_id))
