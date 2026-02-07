"""Unlock post command handler."""

import structlog

from src.community.application.commands import UnlockPostCommand
from src.community.domain.exceptions import (
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnlockPostHandler:
    """Handler for unlocking posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: UnlockPostCommand) -> None:
        """
        Handle post unlocking.

        Args:
            command: The unlock post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If unlocker is not a member
            CannotLockPostError: If unlocker lacks permission
        """
        logger.info(
            "unlock_post_attempt",
            post_id=str(command.post_id),
            unlocker_id=str(command.unlocker_id),
        )

        post_id = PostId(command.post_id)
        unlocker_id = UserId(command.unlocker_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("unlock_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get unlocker's membership
        member = await self._member_repository.get_by_user_and_community(
            unlocker_id, post.community_id
        )
        if member is None:
            logger.warning("unlock_post_not_member", unlocker_id=str(unlocker_id))
            raise NotCommunityMemberError()

        # Unlock the post (domain entity checks permission)
        post.unlock(unlocker_id, member.role)
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("unlock_post_success", post_id=str(post_id))
