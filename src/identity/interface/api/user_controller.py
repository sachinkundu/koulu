"""User API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.identity.application.commands import CompleteProfileCommand
from src.identity.application.handlers import CompleteProfileHandler
from src.identity.domain.exceptions import InvalidDisplayNameError, UserNotFoundError
from src.identity.interface.api.dependencies import (
    CurrentUserDep,
    CurrentUserIdDep,
    get_complete_profile_handler,
)
from src.identity.interface.api.schemas import (
    CompleteProfileRequest,
    ErrorResponse,
    ProfileResponse,
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
