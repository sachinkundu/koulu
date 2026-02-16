"""Gamification API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from src.community.interface.api.dependencies import CurrentUserIdDep
from src.gamification.application.commands.update_level_config import (
    LevelUpdate,
    UpdateLevelConfigCommand,
    UpdateLevelConfigHandler,
)
from src.gamification.application.queries.get_level_definitions import (
    GetLevelDefinitionsHandler,
    GetLevelDefinitionsQuery,
)
from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.infrastructure.api.schemas import (
    LevelDefinitionSchema,
    LevelDefinitionsResponse,
    MemberLevelResponse,
    UpdateLevelConfigRequest,
)
from src.gamification.interface.api.dependencies import (
    get_get_level_definitions_handler,
    get_get_member_level_handler,
    get_update_level_config_handler,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/communities", tags=["Gamification"])


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


@router.get(
    "/{community_id}/levels",
    response_model=LevelDefinitionsResponse,
)
async def get_level_definitions(
    community_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetLevelDefinitionsHandler, Depends(get_get_level_definitions_handler)],
) -> LevelDefinitionsResponse:
    """Get level definitions with member distribution."""
    query = GetLevelDefinitionsQuery(
        community_id=community_id,
        requesting_user_id=current_user_id,
    )
    result = await handler.handle(query)
    return LevelDefinitionsResponse(
        levels=[
            LevelDefinitionSchema(
                level=ld.level,
                name=ld.name,
                threshold=ld.threshold,
                member_percentage=ld.member_percentage,
            )
            for ld in result.levels
        ],
        current_user_level=result.current_user_level,
    )


@router.put(
    "/{community_id}/levels",
    status_code=200,
)
async def update_level_config(
    community_id: UUID,
    current_user_id: CurrentUserIdDep,
    body: UpdateLevelConfigRequest,
    handler: Annotated[UpdateLevelConfigHandler, Depends(get_update_level_config_handler)],
) -> dict[str, str]:
    """Update level configuration for a community."""
    command = UpdateLevelConfigCommand(
        community_id=community_id,
        admin_user_id=current_user_id,
        levels=[
            LevelUpdate(level=lu.level, name=lu.name, threshold=lu.threshold) for lu in body.levels
        ],
    )
    await handler.handle(command)
    return {"status": "ok"}
