"""Unpin post command handler."""

import structlog

from src.community.application.commands import UnpinPostCommand
from src.community.domain.exceptions import (
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UnpinPostHandler:
    """Handler for unpinning posts."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, command: UnpinPostCommand) -> None:
        """
        Handle post unpinning.

        Args:
            command: The unpin post command

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If unpinner is not a member
            CannotPinPostError: If unpinner lacks permission
        """
        logger.info(
            "unpin_post_attempt",
            post_id=str(command.post_id),
            unpinner_id=str(command.unpinner_id),
        )

        post_id = PostId(command.post_id)
        unpinner_id = UserId(command.unpinner_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("unpin_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Get unpinner's membership
        member = await self._member_repository.get_by_user_and_community(
            unpinner_id, post.community_id
        )
        if member is None:
            logger.warning("unpin_post_not_member", unpinner_id=str(unpinner_id))
            raise NotCommunityMemberError()

        # Unpin the post (domain entity checks permission)
        post.unpin(unpinner_id, member.role)
        await self._post_repository.save(post)

        # Publish domain events
        await event_bus.publish_all(post.clear_events())

        logger.info("unpin_post_success", post_id=str(post_id))
