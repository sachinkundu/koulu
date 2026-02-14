"""Search API endpoint."""

from typing import Annotated, cast
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from src.community.application.dtos.search_results import (
    MemberSearchEntry,
    PostSearchEntry,
)
from src.community.application.queries.search_query import SearchQuery
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    SearchHandlerDep,
    SessionDep,
)
from src.community.interface.api.schemas import (
    ErrorResponse,
    MemberSearchItemResponse,
    PostSearchItemResponse,
    SearchResponse,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Search"],
)


async def get_default_community_id(session: SessionDep) -> UUID:
    """Get the default community ID."""
    result = await session.execute(
        select(CommunityModel.id).order_by(CommunityModel.created_at).limit(1)
    )
    community_id = result.scalar_one_or_none()
    if community_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No community found",
        )
    return community_id


DefaultCommunityIdDep = Annotated[UUID, Depends(get_default_community_id)]


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not a community member"},
    },
)
async def search(
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: SearchHandlerDep,
    q: str = Query("", description="Search query"),
    type: str = Query("members", description="Search type: members or posts"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    """Search community members and posts."""
    trimmed = q.strip()
    if not trimmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "QUERY_REQUIRED", "message": "A search query is required"},
        )
    if len(trimmed) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "QUERY_TOO_SHORT",
                "message": "Please enter at least 3 characters to search",
            },
        )
    if type not in ("members", "posts"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SEARCH_TYPE",
                "message": "Search type must be 'members' or 'posts'",
            },
        )
    if len(trimmed) > 200:
        trimmed = trimmed[:200]

    try:
        query = SearchQuery(
            community_id=community_id,
            requester_id=current_user_id,
            query=trimmed,
            search_type=type,
            limit=limit,
            offset=offset,
        )
        result = await handler.handle(query)

        if type == "posts":
            post_items = cast(list[PostSearchEntry], result.items)
            response_items: list[MemberSearchItemResponse] | list[PostSearchItemResponse] = [
                PostSearchItemResponse(
                    id=entry.id,
                    title=entry.title,
                    body_snippet=entry.body_snippet,
                    author_name=entry.author_name,
                    author_avatar_url=entry.author_avatar_url,
                    category_name=entry.category_name,
                    category_emoji=entry.category_emoji,
                    created_at=entry.created_at,
                    like_count=entry.like_count,
                    comment_count=entry.comment_count,
                )
                for entry in post_items
            ]
        else:
            member_items = cast(list[MemberSearchEntry], result.items)
            response_items = [
                MemberSearchItemResponse(
                    user_id=entry.user_id,
                    display_name=entry.display_name,
                    username=entry.username,
                    avatar_url=entry.avatar_url,
                    role=entry.role,
                    bio=entry.bio,
                    joined_at=entry.joined_at,
                )
                for entry in member_items
            ]

        return SearchResponse(
            items=response_items,
            total_count=result.total_count,
            member_count=result.member_count,
            post_count=result.post_count,
            has_more=result.has_more,
        )
    except NotCommunityMemberError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this community",
        ) from err
