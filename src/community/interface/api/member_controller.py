"""Community membership API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.community.application.queries.list_members_query import ListMembersQuery
from src.community.domain.entities import CommunityMember
from src.community.domain.exceptions import NotCommunityMemberError
from src.community.domain.value_objects import CommunityId, MemberRole
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    ListMembersHandlerDep,
    MemberRepositoryDep,
    SessionDep,
)
from src.community.interface.api.schemas import (
    MemberDirectoryItemResponse,
    MemberDirectoryResponse,
    MessageResponse,
)
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()

router = APIRouter(
    prefix="/community",
    tags=["Community - Membership"],
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


@router.post(
    "/join",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def join_community(
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    member_repo: MemberRepositoryDep,
    session: SessionDep,
) -> MessageResponse:
    """Join the default community as a member."""
    user_id = UserId(value=current_user_id)
    comm_id = CommunityId(value=community_id)

    existing = await member_repo.get_by_user_and_community(user_id, comm_id)
    if existing is not None:
        return MessageResponse(message="Already a community member")

    member = CommunityMember.create(
        user_id=user_id,
        community_id=comm_id,
        role=MemberRole.MEMBER,
    )
    await member_repo.save(member)
    await session.commit()

    logger.info(
        "community_join_success", user_id=str(current_user_id), community_id=str(community_id)
    )
    return MessageResponse(message="Joined community successfully")


@router.get(
    "/members",
    response_model=MemberDirectoryResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not a community member"},
    },
)
async def list_members(
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: ListMembersHandlerDep,
    search: str | None = None,
    role: str | None = None,
    sort: str = "most_recent",
    limit: int = 20,
    cursor: str | None = None,
) -> MemberDirectoryResponse:
    """List community members in the directory."""
    try:
        query = ListMembersQuery(
            community_id=community_id,
            requester_id=current_user_id,
            search=search,
            role=role,
            sort=sort,
            limit=limit,
            cursor=cursor,
        )
        result = await handler.handle(query)
        return MemberDirectoryResponse(
            items=[
                MemberDirectoryItemResponse(
                    user_id=entry.user_id,
                    display_name=entry.display_name,
                    avatar_url=entry.avatar_url,
                    role=entry.role,
                    bio=entry.bio,
                    joined_at=entry.joined_at,
                )
                for entry in result.items
            ],
            total_count=result.total_count,
            cursor=result.cursor,
            has_more=result.has_more,
        )
    except NotCommunityMemberError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this community",
        ) from err
