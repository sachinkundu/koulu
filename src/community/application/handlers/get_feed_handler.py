"""Get feed query handler."""

import base64
import json
from dataclasses import dataclass

import structlog

from src.community.application.queries import GetFeedQuery
from src.community.domain.entities import Post
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.repositories import IMemberRepository, IPostRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass
class FeedResult:
    """Result of a feed query with pagination metadata."""

    posts: list[Post]
    cursor: str | None
    has_more: bool


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

    async def handle(self, query: GetFeedQuery) -> FeedResult:
        """
        Handle getting the community feed.

        Args:
            query: The get feed query

        Returns:
            FeedResult with posts and pagination metadata

        Raises:
            NotCommunityMemberError: If requester is not a member
        """
        logger.info(
            "get_feed_attempt",
            community_id=str(query.community_id),
            limit=query.limit,
            offset=query.offset,
            sort=query.sort,
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

        # Get posts for the feed - request limit + 1 to determine has_more
        from src.community.domain.value_objects import CategoryId

        category_id = CategoryId(query.category_id) if query.category_id is not None else None
        fetch_limit = query.limit + 1
        posts = await self._post_repository.list_by_community(
            community_id=community_id,
            category_id=category_id,
            limit=fetch_limit,
            offset=query.offset,
            sort=query.sort,
            cursor=query.cursor,
        )

        # Determine pagination
        has_more = len(posts) > query.limit
        if has_more:
            posts = posts[: query.limit]

        # Build next cursor
        next_cursor: str | None = None
        if has_more:
            # Decode current offset from cursor or use query offset
            current_offset = query.offset
            if query.cursor is not None:
                try:
                    cursor_data = json.loads(base64.b64decode(query.cursor).decode())
                    current_offset = cursor_data.get("offset", 0)
                except (json.JSONDecodeError, ValueError, KeyError):
                    pass
            new_offset = current_offset + query.limit
            next_cursor = base64.b64encode(json.dumps({"offset": new_offset}).encode()).decode()

        logger.info(
            "get_feed_success",
            community_id=str(community_id),
            post_count=len(posts),
            has_more=has_more,
        )
        return FeedResult(posts=posts, cursor=next_cursor, has_more=has_more)
