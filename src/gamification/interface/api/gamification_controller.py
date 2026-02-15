"""Gamification API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from src.community.interface.api.dependencies import CurrentUserIdDep
from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.infrastructure.api.schemas import MemberLevelResponse
from src.gamification.interface.api.dependencies import get_get_member_level_handler

logger = structlog.get_logger()

router = APIRouter(prefix="/api/communities", tags=["Gamification"])


@router.get(
    "/{community_id}/members/{user_id}/level",
    response_model=MemberLevelResponse,
)
async def get_member_level(
    community_id: UUID,
    user_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetMemberLevelHandler, Depends(get_get_member_level_handler)],
) -> MemberLevelResponse:
    """Get a member's level and points."""
    query = GetMemberLevelQuery(
        community_id=community_id,
        user_id=user_id,
        requesting_user_id=current_user_id,
    )
    result = await handler.handle(query)
    return MemberLevelResponse(
        user_id=result.user_id,
        level=result.level,
        level_name=result.level_name,
        total_points=result.total_points,
        points_to_next_level=result.points_to_next_level,
        is_max_level=result.is_max_level,
    )
