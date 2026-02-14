"""Search query handler."""

import re

import structlog

from src.community.application.dtos.search_results import (
    MemberSearchEntry,
    PostSearchEntry,
    SearchResult,
)
from src.community.application.queries.search_query import SearchQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.repositories import IMemberRepository, ISearchRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()

_HTML_TAG_RE = re.compile(r"<[^>]+>")


class SearchHandler:
    """Handler for searching community members and posts."""

    def __init__(
        self,
        member_repository: IMemberRepository,
        search_repository: ISearchRepository,
    ) -> None:
        """Initialize with dependencies."""
        self._member_repository = member_repository
        self._search_repository = search_repository

    async def handle(self, query: SearchQuery) -> SearchResult:
        """
        Handle a search query.

        Args:
            query: The search query

        Returns:
            SearchResult with items and counts for both tabs

        Raises:
            NotCommunityMemberError: If requester is not a member
        """
        logger.info(
            "search_attempt",
            community_id=str(query.community_id),
            requester_id=str(query.requester_id),
            search_type=query.search_type,
            query_length=len(query.query),
        )

        community_id = CommunityId(query.community_id)
        requester_id = UserId(query.requester_id)

        # Check membership
        member = await self._member_repository.get_by_user_and_community(requester_id, community_id)
        if member is None:
            logger.warning(
                "search_unauthorized",
                community_id=str(community_id),
                requester_id=str(requester_id),
            )
            raise NotCommunityMemberError()

        # Sanitize query: strip HTML tags and normalize whitespace
        sanitized = _HTML_TAG_RE.sub("", query.query)
        sanitized = " ".join(sanitized.split())

        # Always fetch counts for both tabs
        member_count = await self._search_repository.count_members(community_id, sanitized)
        post_count = await self._search_repository.count_posts(community_id, sanitized)

        # Fetch items for the active search type
        items: list[MemberSearchEntry] | list[PostSearchEntry]
        if query.search_type == "posts":
            items = await self._search_repository.search_posts(
                community_id,
                sanitized,
                limit=query.limit,
                offset=query.offset,
            )
            total_count = post_count
        else:
            items = await self._search_repository.search_members(
                community_id,
                sanitized,
                limit=query.limit,
                offset=query.offset,
            )
            total_count = member_count

        has_more = query.offset + query.limit < total_count

        logger.info(
            "search_success",
            community_id=str(community_id),
            search_type=query.search_type,
            result_count=len(items),
            member_count=member_count,
            post_count=post_count,
        )

        return SearchResult(
            items=items,
            total_count=total_count,
            member_count=member_count,
            post_count=post_count,
            has_more=has_more,
        )
