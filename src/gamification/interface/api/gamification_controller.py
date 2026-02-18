"""Gamification API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.community.domain.value_objects import CommunityId, MemberRole
from src.community.infrastructure.persistence import SqlAlchemyMemberRepository
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    MemberRepositoryDep,
    SessionDep,
)
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
from src.gamification.application.queries.get_leaderboards import (
    GetLeaderboardsHandler,
    GetLeaderboardsQuery,
    LeaderboardPeriodResult,
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
    LeaderboardEntrySchema,
    LeaderboardPeriodSchema,
    LeaderboardsResponse,
    LevelDefinitionSchema,
    LevelDefinitionsResponse,
    MemberLevelResponse,
    SetCourseLevelRequirementRequest,
    UpdateLevelConfigRequest,
)
from src.gamification.interface.api.dependencies import (
    get_check_course_access_handler,
    get_get_leaderboards_handler,
    get_get_level_definitions_handler,
    get_get_member_level_handler,
    get_set_course_level_requirement_handler,
    get_update_level_config_handler,
)
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()

router = APIRouter(prefix="/communities", tags=["Gamification"])

# Auto-resolving router (no community_id in URL — matches pattern used by post/member controllers)
default_router = APIRouter(prefix="/community", tags=["Gamification"])


async def _get_default_community_id(session: SessionDep) -> UUID:
    """Get the default community ID (first community by creation date)."""
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


DefaultCommunityIdDep = Annotated[UUID, Depends(_get_default_community_id)]


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


# ============================================================================
# Auto-resolving convenience routes (no community_id in URL)
# ============================================================================


@default_router.get(
    "/members/{user_id}/level",
    response_model=MemberLevelResponse,
)
async def get_member_level_default(
    user_id: UUID,
    community_id: DefaultCommunityIdDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetMemberLevelHandler, Depends(get_get_member_level_handler)],
) -> MemberLevelResponse:
    """Get a member's level and points (auto-resolves community)."""
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


@default_router.get(
    "/levels",
    response_model=LevelDefinitionsResponse,
)
async def get_level_definitions_default(
    community_id: DefaultCommunityIdDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetLevelDefinitionsHandler, Depends(get_get_level_definitions_handler)],
) -> LevelDefinitionsResponse:
    """Get level definitions with member distribution (auto-resolves community)."""
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


@default_router.get(
    "/courses/{course_id}/access",
    response_model=CourseAccessResponse,
)
async def check_course_access_default(
    course_id: UUID,
    community_id: DefaultCommunityIdDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[CheckCourseAccessHandler, Depends(get_check_course_access_handler)],
) -> CourseAccessResponse:
    """Check if user can access a course based on level requirements (auto-resolves community)."""
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


# ============================================================================
# Leaderboards
# ============================================================================


def _map_period(period_result: LeaderboardPeriodResult) -> LeaderboardPeriodSchema:
    return LeaderboardPeriodSchema(
        entries=[
            LeaderboardEntrySchema(
                rank=e.rank,
                user_id=e.user_id,
                display_name=e.display_name,
                avatar_url=e.avatar_url,
                level=e.level,
                points=e.points,
            )
            for e in period_result.entries
        ],
        your_rank=LeaderboardEntrySchema(
            rank=period_result.your_rank.rank,
            user_id=period_result.your_rank.user_id,
            display_name=period_result.your_rank.display_name,
            avatar_url=period_result.your_rank.avatar_url,
            level=period_result.your_rank.level,
            points=period_result.your_rank.points,
        )
        if period_result.your_rank
        else None,
    )


@router.get(
    "/{community_id}/leaderboards",
    response_model=LeaderboardsResponse,
)
async def get_leaderboards(
    community_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetLeaderboardsHandler, Depends(get_get_leaderboards_handler)],
) -> LeaderboardsResponse:
    """Get all three leaderboards for a community."""
    query = GetLeaderboardsQuery(
        community_id=community_id,
        current_user_id=current_user_id,
    )
    result = await handler.handle(query)
    return LeaderboardsResponse(
        seven_day=_map_period(result.seven_day),
        thirty_day=_map_period(result.thirty_day),
        all_time=_map_period(result.all_time),
        last_updated=result.last_updated,
    )


@default_router.get(
    "/leaderboards",
    response_model=LeaderboardsResponse,
)
async def get_leaderboards_default(
    community_id: DefaultCommunityIdDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetLeaderboardsHandler, Depends(get_get_leaderboards_handler)],
) -> LeaderboardsResponse:
    """Get all three leaderboards (auto-resolves community)."""
    query = GetLeaderboardsQuery(
        community_id=community_id,
        current_user_id=current_user_id,
    )
    result = await handler.handle(query)
    return LeaderboardsResponse(
        seven_day=_map_period(result.seven_day),
        thirty_day=_map_period(result.thirty_day),
        all_time=_map_period(result.all_time),
        last_updated=result.last_updated,
    )
