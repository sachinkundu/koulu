"""Get post query handler."""

import structlog

from src.community.application.queries import GetPostQuery
from src.community.domain.entities import Post
from src.community.domain.exceptions import NotCommunityMemberError, PostNotFoundError
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import PostId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class GetPostHandler:
    """Handler for getting a post by ID."""

    def __init__(
        self,
        post_repository: IPostRepository,
        member_repository: IMemberRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._post_repository = post_repository
        self._member_repository = member_repository

    async def handle(self, query: GetPostQuery) -> Post:
        """
        Handle getting a post.

        Args:
            query: The get post query

        Returns:
            The post entity

        Raises:
            PostNotFoundError: If post doesn't exist
            NotCommunityMemberError: If requester is not a member
        """
        logger.info("get_post_attempt", post_id=str(query.post_id))

        post_id = PostId(query.post_id)

        # Get the post
        post = await self._post_repository.get_by_id(post_id)
        if post is None:
            logger.warning("get_post_not_found", post_id=str(post_id))
            raise PostNotFoundError(str(post_id))

        # Check membership if requester is specified
        if query.requester_id is not None:
            requester_id = UserId(query.requester_id)
            member = await self._member_repository.get_by_user_and_community(
                requester_id, post.community_id
            )
            if member is None:
                logger.warning("get_post_not_member", requester_id=str(requester_id))
                raise NotCommunityMemberError()

        logger.info("get_post_success", post_id=str(post_id))
        return post
