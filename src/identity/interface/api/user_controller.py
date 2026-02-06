"""User API endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.identity.application.commands import CompleteProfileCommand, UpdateProfileCommand
from src.identity.application.handlers import CompleteProfileHandler, UpdateProfileHandler
from src.identity.application.queries import (
    GetProfileActivityHandler,
    GetProfileActivityQuery,
    GetProfileHandler,
    GetProfileQuery,
    GetProfileStatsHandler,
    GetProfileStatsQuery,
)
from src.identity.domain.exceptions import (
    InvalidBioError,
    InvalidDisplayNameError,
    InvalidLocationError,
    InvalidSocialLinkError,
    ProfileNotFoundError,
    UserNotFoundError,
)
from src.identity.interface.api.dependencies import (
    CurrentUserDep,
    CurrentUserIdDep,
    get_complete_profile_handler,
    get_profile_activity_handler,
    get_profile_handler,
    get_profile_stats_handler,
    get_update_profile_handler,
)
from src.identity.interface.api.schemas import (
    ActivityChartResponse,
    ActivityItemResponse,
    ActivityResponse,
    CompleteProfileRequest,
    ErrorResponse,
    ProfileDetailResponse,
    ProfileResponse,
    StatsResponse,
    UpdateProfileRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_current_user(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Get current authenticated user."""
    profile = None
    if current_user.profile is not None:
        profile = ProfileResponse(
            display_name=(
                current_user.profile.display_name.value
                if current_user.profile.display_name
                else None
            ),
            avatar_url=current_user.profile.avatar_url,
            bio=current_user.profile.bio,
            is_complete=current_user.profile.is_complete,
        )

    return UserResponse(
        id=current_user.id.value,
        email=current_user.email.value,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        profile=profile,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put(
    "/me/profile",
    response_model=ProfileResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def complete_profile(
    body: CompleteProfileRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[CompleteProfileHandler, Depends(get_complete_profile_handler)],
) -> ProfileResponse:
    """Complete or update user profile."""
    try:
        command = CompleteProfileCommand(
            user_id=current_user_id,
            display_name=body.display_name,
            avatar_url=body.avatar_url,
        )
        await handler.handle(command)
    except InvalidDisplayNameError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "user_not_found", "message": "User not found"},
        ) from e

    return ProfileResponse(
        display_name=body.display_name,
        avatar_url=body.avatar_url,
        bio=None,
        is_complete=True,
    )


@router.patch(
    "/me/profile",
    response_model=ProfileDetailResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
    },
)
async def update_profile(
    body: UpdateProfileRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UpdateProfileHandler, Depends(get_update_profile_handler)],
) -> ProfileDetailResponse:
    """Update user profile fields."""
    try:
        command = UpdateProfileCommand(
            user_id=current_user_id,
            display_name=body.display_name,
            avatar_url=body.avatar_url,
            bio=body.bio,
            city=body.city,
            country=body.country,
            twitter_url=body.twitter_url,
            linkedin_url=body.linkedin_url,
            instagram_url=body.instagram_url,
            website_url=body.website_url,
        )
        await handler.handle(command)
    except (
        InvalidDisplayNameError,
        InvalidBioError,
        InvalidLocationError,
        InvalidSocialLinkError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "profile_not_found", "message": "Profile not found"},
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "user_not_found", "message": "User not found"},
        ) from e

    # Return updated profile by fetching it
    from src.identity.domain.value_objects import UserId

    user_repo = handler._user_repository
    user = await user_repo.get_by_id(UserId(value=current_user_id))

    profile = user.profile if user else None
    assert profile is not None

    return ProfileDetailResponse(
        display_name=profile.display_name.value if profile.display_name else None,
        avatar_url=profile.avatar_url,
        bio=profile.bio.value if profile.bio else None,
        location_city=profile.location.city if profile.location else None,
        location_country=profile.location.country if profile.location else None,
        twitter_url=profile.social_links.twitter_url if profile.social_links else None,
        linkedin_url=profile.social_links.linkedin_url if profile.social_links else None,
        instagram_url=profile.social_links.instagram_url if profile.social_links else None,
        website_url=profile.social_links.website_url if profile.social_links else None,
        is_complete=profile.is_complete,
        is_own_profile=True,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/me/profile",
    response_model=ProfileDetailResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
    },
)
async def get_own_profile(
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetProfileHandler, Depends(get_profile_handler)],
) -> ProfileDetailResponse:
    """Get current user's profile with all details."""
    try:
        query = GetProfileQuery(user_id=current_user_id)
        user = await handler.handle(query)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "profile_not_found", "message": "Profile not found"},
        ) from e

    profile = user.profile
    assert profile is not None  # Handler raises if profile is None

    return ProfileDetailResponse(
        display_name=profile.display_name.value if profile.display_name else None,
        avatar_url=profile.avatar_url,
        bio=profile.bio.value if profile.bio else None,
        location_city=profile.location.city if profile.location else None,
        location_country=profile.location.country if profile.location else None,
        twitter_url=profile.social_links.twitter_url if profile.social_links else None,
        linkedin_url=profile.social_links.linkedin_url if profile.social_links else None,
        instagram_url=profile.social_links.instagram_url if profile.social_links else None,
        website_url=profile.social_links.website_url if profile.social_links else None,
        is_complete=profile.is_complete,
        is_own_profile=True,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/{user_id}/profile",
    response_model=ProfileDetailResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
    },
)
async def get_user_profile(
    user_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetProfileHandler, Depends(get_profile_handler)],
) -> ProfileDetailResponse:
    """Get another user's profile."""
    try:
        query = GetProfileQuery(user_id=user_id)
        user = await handler.handle(query)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "profile_not_found", "message": "Profile not found"},
        ) from e

    profile = user.profile
    assert profile is not None  # Handler raises if profile is None

    is_own_profile = user_id == current_user_id

    return ProfileDetailResponse(
        display_name=profile.display_name.value if profile.display_name else None,
        avatar_url=profile.avatar_url,
        bio=profile.bio.value if profile.bio else None,
        location_city=profile.location.city if profile.location else None,
        location_country=profile.location.country if profile.location else None,
        twitter_url=profile.social_links.twitter_url if profile.social_links else None,
        linkedin_url=profile.social_links.linkedin_url if profile.social_links else None,
        instagram_url=profile.social_links.instagram_url if profile.social_links else None,
        website_url=profile.social_links.website_url if profile.social_links else None,
        is_complete=profile.is_complete,
        is_own_profile=is_own_profile,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/me/profile/activity",
    response_model=ActivityResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
    },
)
async def get_profile_activity(
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetProfileActivityHandler, Depends(get_profile_activity_handler)],
    limit: int = 20,
    offset: int = 0,
) -> ActivityResponse:
    """Get current user's activity feed."""
    try:
        query = GetProfileActivityQuery(user_id=current_user_id, limit=limit, offset=offset)
        activity = await handler.handle(query)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "profile_not_found", "message": "Profile not found"},
        ) from e

    return ActivityResponse(
        items=[
            ActivityItemResponse(
                id=item.id,
                type=item.type,
                content=item.content,
                created_at=item.created_at,
            )
            for item in activity.items
        ],
        total_count=activity.total_count,
    )


@router.get(
    "/me/profile/stats",
    response_model=StatsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
    },
)
async def get_profile_stats(
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetProfileStatsHandler, Depends(get_profile_stats_handler)],
) -> StatsResponse:
    """Get current user's profile statistics."""
    try:
        query = GetProfileStatsQuery(user_id=current_user_id)
        stats = await handler.handle(query)
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "profile_not_found", "message": "Profile not found"},
        ) from e

    return StatsResponse(
        contribution_count=stats.contribution_count,
        joined_at=stats.joined_at,
    )


@router.get(
    "/me/profile/activity/chart",
    response_model=ActivityChartResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_activity_chart(
    _current_user_id: CurrentUserIdDep,
) -> ActivityChartResponse:
    """Get 30-day activity chart data."""
    # Generate 30 days of empty data (placeholder until Community feature exists)
    # Note: _current_user_id ensures authentication but isn't used yet (will be used in Community feature)
    now = datetime.now(UTC)
    days = [now - timedelta(days=i) for i in range(30)]
    days.reverse()  # Oldest to newest
    counts = [0] * 30

    return ActivityChartResponse(
        days=days,
        counts=counts,
    )
