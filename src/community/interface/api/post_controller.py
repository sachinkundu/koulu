"""Community post API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.community.application.commands import (
    CreatePostCommand,
    DeletePostCommand,
    LikePostCommand,
    LockPostCommand,
    UnlikePostCommand,
    UnlockPostCommand,
    UpdatePostCommand,
)
from src.community.application.handlers import (
    CreatePostHandler,
    DeletePostHandler,
    GetPostHandler,
    LikePostHandler,
    LockPostHandler,
    UnlikePostHandler,
    UnlockPostHandler,
    UpdatePostHandler,
)
from src.community.application.queries import GetPostQuery
from src.community.domain.exceptions import (
    CannotDeletePostError,
    CannotLockPostError,
    CategoryNotFoundError,
    CommunityDomainError,
    NotCommunityMemberError,
    NotPostAuthorError,
    PostAlreadyDeletedError,
    PostContentRequiredError,
    PostContentTooLongError,
    PostNotFoundError,
    PostTitleRequiredError,
    PostTitleTooLongError,
)
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    SessionDep,
    get_create_post_handler,
    get_delete_post_handler,
    get_get_post_handler,
    get_like_post_handler,
    get_lock_post_handler,
    get_unlike_post_handler,
    get_unlock_post_handler,
    get_update_post_handler,
)
from src.community.interface.api.schemas import (
    CreatePostRequest,
    CreatePostResponse,
    ErrorResponse,
    LikeResponse,
    MessageResponse,
    PostResponse,
    UpdatePostRequest,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/posts", tags=["Community Posts"])


# ============================================================================
# Helper Dependencies
# ============================================================================


async def get_default_community_id(session: SessionDep) -> UUID:
    """
    Get the default community ID.

    For MVP, there's only one community with slug 'default'.
    """
    result = await session.execute(
        select(CommunityModel.id).where(CommunityModel.slug == "default")
    )
    community_id = result.scalar_one_or_none()

    if community_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default community not found",
        )

    return community_id


DefaultCommunityIdDep = Annotated[UUID, Depends(get_default_community_id)]


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "",
    response_model=CreatePostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not a community member"},
        404: {"model": ErrorResponse, "description": "Category not found"},
    },
)
async def create_post(
    body: CreatePostRequest,
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: Annotated[CreatePostHandler, Depends(get_create_post_handler)],
) -> CreatePostResponse:
    """Create a new post in the community."""
    try:
        command = CreatePostCommand(
            community_id=community_id,
            author_id=current_user_id,
            category_id=body.category_id,
            category_name=body.category_name,
            title=body.title,
            content=body.content,
            image_url=body.image_url,
        )
        post_id = await handler.handle(command)

        logger.info("create_post_api_success", post_id=str(post_id))
        return CreatePostResponse(id=post_id.value)

    except NotCommunityMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CategoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (
        PostTitleRequiredError,
        PostTitleTooLongError,
        PostContentRequiredError,
        PostContentTooLongError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("create_post_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not a community member"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def get_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetPostHandler, Depends(get_get_post_handler)],
) -> PostResponse:
    """Get a post by ID."""
    try:
        query = GetPostQuery(post_id=post_id, requester_id=current_user_id)
        post = await handler.handle(query)

        logger.info("get_post_api_success", post_id=str(post_id))
        return PostResponse(
            id=post.id.value,
            community_id=post.community_id.value,
            author_id=post.author_id.value,
            category_id=post.category_id.value,
            title=post.title.value,
            content=post.content.value,
            image_url=post.image_url,
            is_pinned=post.is_pinned,
            is_locked=post.is_locked,
            is_edited=post.is_edited,
            created_at=post.created_at,
            updated_at=post.updated_at,
            edited_at=post.edited_at,
        )

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except NotCommunityMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("get_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch(
    "/{post_id}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to edit"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def update_post(
    post_id: UUID,
    body: UpdatePostRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UpdatePostHandler, Depends(get_update_post_handler)],
) -> MessageResponse:
    """Update a post."""
    try:
        command = UpdatePostCommand(
            post_id=post_id,
            editor_id=current_user_id,
            title=body.title,
            content=body.content,
            image_url=body.image_url,
            category_id=body.category_id,
        )
        await handler.handle(command)

        logger.info("update_post_api_success", post_id=str(post_id))
        return MessageResponse(message="Post updated successfully")

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, NotPostAuthorError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except PostAlreadyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except (
        PostTitleRequiredError,
        PostTitleTooLongError,
        PostContentRequiredError,
        PostContentTooLongError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("update_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to delete"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def delete_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[DeletePostHandler, Depends(get_delete_post_handler)],
) -> None:
    """Delete a post."""
    try:
        command = DeletePostCommand(
            post_id=post_id,
            deleter_id=current_user_id,
        )
        await handler.handle(command)

        logger.info("delete_post_api_success", post_id=str(post_id))

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotDeletePostError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("delete_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Lock/Unlock Endpoints
# ============================================================================


@router.post(
    "/{post_id}/lock",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to lock"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def lock_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[LockPostHandler, Depends(get_lock_post_handler)],
) -> None:
    """Lock a post to prevent new comments."""
    try:
        command = LockPostCommand(post_id=post_id, locker_id=current_user_id)
        await handler.handle(command)

        logger.info("lock_post_api_success", post_id=str(post_id))

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotLockPostError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("lock_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{post_id}/lock",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to unlock"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def unlock_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UnlockPostHandler, Depends(get_unlock_post_handler)],
) -> None:
    """Unlock a post to allow comments again."""
    try:
        command = UnlockPostCommand(post_id=post_id, unlocker_id=current_user_id)
        await handler.handle(command)

        logger.info("unlock_post_api_success", post_id=str(post_id))

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotLockPostError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("unlock_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Like/Unlike Post Endpoints
# ============================================================================


@router.post(
    "/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def like_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[LikePostHandler, Depends(get_like_post_handler)],
) -> LikeResponse:
    """Like a post."""
    try:
        command = LikePostCommand(post_id=post_id, user_id=current_user_id)
        await handler.handle(command)

        logger.info("like_post_api_success", post_id=str(post_id))
        return LikeResponse(message="Post liked successfully")

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("like_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def unlike_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UnlikePostHandler, Depends(get_unlike_post_handler)],
) -> LikeResponse:
    """Unlike a post."""
    command = UnlikePostCommand(post_id=post_id, user_id=current_user_id)
    await handler.handle(command)

    logger.info("unlike_post_api_success", post_id=str(post_id))
    return LikeResponse(message="Post unliked successfully")
