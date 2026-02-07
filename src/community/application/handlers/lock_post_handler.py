"""Lock post command handler."""

import structlog

from src.community.application.commands import LockPostCommand
from src.community.domain.exceptions import (
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class LockPostHandler:
    """Handler for locking posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: LockPostCommand) -> None:
        """
        Handle post locking.

        Args:
            command: The lock post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If locker is not a member
            CannotLockPostError: If locker lacks permission
        """
        logger.info(
            "lock_post_attempt",
            post_id=str(command.post_id),
            locker_id=str(command.locker_id),
        )

        post_id = PostId(command.post_id)
        locker_id = UserId(command.locker_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("lock_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get locker's membership
        member = await self._member_repository.get_by_user_and_community(
            locker_id, post.community_id
        )
        if member is None:
            logger.warning("lock_post_not_member", locker_id=str(locker_id))
            raise NotCommunityMemberError()

        # Lock the post (domain entity checks permission)
        post.lock(locker_id, member.role)
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("lock_post_success", post_id=str(post_id))
