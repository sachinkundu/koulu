"""Pin post command handler."""

import structlog

from src.community.application.commands import PinPostCommand
from src.community.domain.exceptions import (
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class PinPostHandler:
    """Handler for pinning posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: PinPostCommand) -> None:
        """
        Handle post pinning.

        Args:
            command: The pin post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If pinner is not a member
            CannotPinPostError: If pinner lacks permission
        """
        logger.info(
            "pin_post_attempt",
            post_id=str(command.post_id),
            pinner_id=str(command.pinner_id),
        )

        post_id = PostId(command.post_id)
        pinner_id = UserId(command.pinner_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("pin_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get pinner's membership
        member = await self._member_repository.get_by_user_and_community(
            pinner_id, post.community_id
        )
        if member is None:
            logger.warning("pin_post_not_member", pinner_id=str(pinner_id))
            raise NotCommunityMemberError()

        # Pin the post (domain entity checks permission)
        post.pin(pinner_id, member.role)
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("pin_post_success", post_id=str(post_id))
