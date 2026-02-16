"""Gamification API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.community.domain.value_objects import CommunityId, MemberRole
from src.community.infrastructure.persistence import SqlAlchemyMemberRepository
from src.community.interface.api.dependencies import CurrentUserIdDep, MemberRepositoryDep
from src.gamification.application.commands.set_course_level_requirement import (
    SetCourseLevelRequirementCommand,
    SetCourseLevelRequirementHandler,
)
from src.gamification.application.commands.update_level_config import (
    LevelUpdate,
    UpdateLevelConfigCommand,
    UpdateLevelConfigHandler,
)
from src.gamification.application.queries.check_course_access import (
    CheckCourseAccessHandler,
    CheckCourseAccessQuery,
)
from src.gamification.application.queries.get_level_definitions import (
    GetLevelDefinitionsHandler,
    GetLevelDefinitionsQuery,
)
from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.domain.exceptions import (
    GamificationDomainError,
    InvalidLevelNameError,
    InvalidThresholdError,
)
from src.gamification.infrastructure.api.schemas import (
    CourseAccessResponse,
    LevelDefinitionSchema,
    LevelDefinitionsResponse,
    MemberLevelResponse,
    SetCourseLevelRequirementRequest,
    UpdateLevelConfigRequest,
)
from src.gamification.interface.api.dependencies import (
    get_check_course_access_handler,
    get_get_level_definitions_handler,
    get_get_member_level_handler,
    get_set_course_level_requirement_handler,
    get_update_level_config_handler,
)
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()

router = APIRouter(prefix="/communities", tags=["Gamification"])


async def _require_admin(
    member_repo: SqlAlchemyMemberRepository,
    community_id: UUID,
    user_id: UUID,
) -> None:
    """Check that user is an admin of the community. Raises 403 if not."""
    member = await member_repo.get_by_user_and_community(
        UserId(value=user_id), CommunityId(value=community_id)
    )
    if member is None or member.role != MemberRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action",
        )


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
    member_repo: MemberRepositoryDep,
) -> dict[str, str]:
    """Update level configuration for a community (admin only)."""
    await _require_admin(member_repo, community_id, current_user_id)

    try:
        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=current_user_id,
            levels=[
                LevelUpdate(level=lu.level, name=lu.name, threshold=lu.threshold)
                for lu in body.levels
            ],
        )
        await handler.handle(command)
        return {"status": "ok"}
    except InvalidLevelNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except InvalidThresholdError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except GamificationDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get(
    "/{community_id}/courses/{course_id}/access",
    response_model=CourseAccessResponse,
)
async def check_course_access(
    community_id: UUID,
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[CheckCourseAccessHandler, Depends(get_check_course_access_handler)],
) -> CourseAccessResponse:
    """Check if user can access a course based on level requirements."""
    query = CheckCourseAccessQuery(
        community_id=community_id,
        course_id=course_id,
        user_id=current_user_id,
    )
    result = await handler.handle(query)
    return CourseAccessResponse(
        course_id=result.course_id,
        has_access=result.has_access,
        minimum_level=result.minimum_level,
        minimum_level_name=result.minimum_level_name,
        current_level=result.current_level,
    )


@router.put(
    "/{community_id}/courses/{course_id}/level-requirement",
    status_code=200,
)
async def set_course_level_requirement(
    community_id: UUID,
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    body: SetCourseLevelRequirementRequest,
    handler: Annotated[
        SetCourseLevelRequirementHandler, Depends(get_set_course_level_requirement_handler)
    ],
    member_repo: MemberRepositoryDep,
) -> dict[str, str]:
    """Set minimum level requirement for a course (admin only)."""
    await _require_admin(member_repo, community_id, current_user_id)

    command = SetCourseLevelRequirementCommand(
        community_id=community_id,
        course_id=course_id,
        admin_user_id=current_user_id,
        minimum_level=body.minimum_level,
    )
    await handler.handle(command)
    return {"status": "ok"}
