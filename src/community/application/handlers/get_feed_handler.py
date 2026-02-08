"""Get feed query handler."""

import structlog

from src.community.application.queries import GetFeedQuery
from src.community.domain.entities import Post
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class GetFeedHandler:
    """Handler for getting the community feed."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, query: GetFeedQuery) -> list[Post]:
        """
        Handle getting the community feed.

        Args:
            query: The get feed query

        Returns:
            List of posts in the feed

        Raises:
            NotCommunityMemberError: If requester is not a member
        """
        logger.info(
            "get_feed_attempt",
            community_id=str(query.community_id),
            limit=query.limit,
            offset=query.offset,
        )

        community_id = CommunityId(query.community_id)

        # Check membership if requester is specified
        if query.requester_id is not None:
            requester_id = UserId(query.requester_id)
            member = await self._member_repository.get_by_user_and_community(
                requester_id, community_id
            )
            if member is None:
                logger.warning("get_feed_not_member", requester_id=str(requester_id))
                raise NotCommunityMemberError()

        # Get posts for the feed
        posts = await self._post_repository.list_by_community(
            community_id=community_id,
            limit=query.limit,
            offset=query.offset,
        )

        logger.info("get_feed_success", community_id=str(community_id), post_count=len(posts))
        return posts
