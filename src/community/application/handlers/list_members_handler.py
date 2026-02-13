"""List members query handler."""

import base64
import json

import structlog

from src.community.application.dtos.member_directory_entry import (
    MemberDirectoryResult,
)
from src.community.application.queries.list_members_query import ListMembersQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.repositories import IMemberRepository
from src.community.domain.value_objects import CommunityId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class ListMembersHandler:
    """Handler for listing community members in the directory."""

    def __init__(self, member_repository: IMemberRepository) -> None:
        """Initialize with dependencies."""
        self._member_repository = member_repository

    async def handle(self, query: ListMembersQuery) -> MemberDirectoryResult:
        """
        Handle listing community members.

        Args:
            query: The list members query

        Returns:
            MemberDirectoryResult with members and pagination metadata

        Raises:
            NotCommunityMemberError: If requester is not a member
        """
        logger.info(
            "member_directory_list_attempt",
            community_id=str(query.community_id),
            requester_id=str(query.requester_id),
            sort=query.sort,
            limit=query.limit,
        )

        community_id = CommunityId(query.community_id)
        requester_id = UserId(query.requester_id)

        # Check membership
        member = await self._member_repository.get_by_user_and_community(
            requester_id, community_id
        )
        if member is None:
            logger.warning(
                "member_directory_unauthorized",
                community_id=str(community_id),
                requester_id=str(requester_id),
            )
            raise NotCommunityMemberError()

        # Decode cursor to get offset
        offset = 0
        if query.cursor is not None:
            try:
                cursor_data = json.loads(base64.b64decode(query.cursor).decode())
                offset = cursor_data.get("offset", 0)
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

        # Fetch limit + 1 to determine has_more
        fetch_limit = query.limit + 1
        items = await self._member_repository.list_directory(
            community_id=community_id,
            sort=query.sort,
            limit=fetch_limit,
            offset=offset,
        )

        # Get total count
        total_count = await self._member_repository.count_directory(
            community_id=community_id,
        )

        # Determine pagination
        has_more = len(items) > query.limit
        if has_more:
            items = items[: query.limit]

        # Build next cursor
        next_cursor: str | None = None
        if has_more:
            new_offset = offset + query.limit
            next_cursor = base64.b64encode(json.dumps({"offset": new_offset}).encode()).decode()

        logger.info(
            "member_directory_list_success",
            community_id=str(community_id),
            result_count=len(items),
            total_count=total_count,
            has_more=has_more,
        )

        return MemberDirectoryResult(
            items=items,
            total_count=total_count,
            cursor=next_cursor,
            has_more=has_more,
        )
