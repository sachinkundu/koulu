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
    PinPostCommand,
    UnlikePostCommand,
    UnlockPostCommand,
    UnpinPostCommand,
    UpdatePostCommand,
)
from src.community.application.handlers import (
    CreatePostHandler,
    DeletePostHandler,
    GetFeedHandler,
    GetPostHandler,
    LikePostHandler,
    LockPostHandler,
    PinPostHandler,
    UnlikePostHandler,
    UnlockPostHandler,
    UnpinPostHandler,
    UpdatePostHandler,
)
from src.community.application.queries import GetFeedQuery, GetPostQuery
from src.community.domain.exceptions import (
    CannotDeletePostError,
    CannotLockPostError,
    CannotPinPostError,
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
    RateLimitExceededError,
)
from src.community.domain.value_objects import PostId
from src.community.infrastructure.persistence.models import CommunityModel
from src.community.interface.api.dependencies import (
    CommentRepositoryDep,
    CurrentUserIdDep,
    ReactionRepositoryDep,
    SessionDep,
    get_create_post_handler,
    get_delete_post_handler,
    get_get_feed_handler,
    get_get_post_handler,
    get_like_post_handler,
    get_lock_post_handler,
    get_pin_post_handler,
    get_unlike_post_handler,
    get_unlock_post_handler,
    get_unpin_post_handler,
    get_update_post_handler,
)
from src.community.interface.api.schemas import (
    AuthorResponse,
    CreatePostRequest,
    CreatePostResponse,
    ErrorResponse,
    FeedResponse,
    LikeResponse,
    MessageResponse,
    PostResponse,
    UpdatePostRequest,
)
from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import ProfileModel

logger = structlog.get_logger()

router = APIRouter(prefix="/community/posts", tags=["Community Posts"])


# ============================================================================
# Helper Dependencies
# ============================================================================


async def get_default_community_id(session: SessionDep) -> UUID:
    """
    Get the default community ID.

    Uses the first available community (ordered by creation date).
    """
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


# ============================================================================
# Endpoints
# ============================================================================


@router.get(
    "",
    response_model=FeedResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not a community member"},
    },
)
async def get_feed(
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    community_id: DefaultCommunityIdDep,
    handler: Annotated[GetFeedHandler, Depends(get_get_feed_handler)],
    reaction_repo: ReactionRepositoryDep,
    comment_repo: CommentRepositoryDep,
    limit: int = 20,
    offset: int = 0,
    category_id: UUID | None = None,
    sort: str = "hot",
    cursor: str | None = None,
) -> FeedResponse:
    """Get the community feed (list of posts)."""
    # Validate sort parameter
    valid_sorts = ("hot", "new", "top")
    if sort not in valid_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter. Must be one of: {', '.join(valid_sorts)}",
        )

    try:
        query = GetFeedQuery(
            community_id=community_id,
            requester_id=current_user_id,
            category_id=category_id,
            limit=min(limit, 100),  # Cap at 100 posts
            offset=offset,
            sort=sort,
            cursor=cursor,
        )
        feed_result = await handler.handle(query)

        logger.info(
            "get_feed_api_success",
            community_id=str(community_id),
            count=len(feed_result.posts),
        )

        # Fetch author profiles for all posts
        author_ids = [post.author_id.value for post in feed_result.posts]
        profiles_result = await session.execute(
            select(ProfileModel).where(ProfileModel.user_id.in_(author_ids))
        )
        profiles_map = {p.user_id: p for p in profiles_result.scalars().all()}

        # Check which posts current user has liked
        user_id = UserId(value=current_user_id)
        liked_post_ids: set[UUID] = set()
        for post in feed_result.posts:
            reaction = await reaction_repo.find_by_user_and_target(user_id, "post", post.id.value)
            if reaction is not None:
                liked_post_ids.add(post.id.value)

        # Convert domain entities to response models with author info
        post_responses = []
        for post in feed_result.posts:
            author_profile = profiles_map.get(post.author_id.value)
            author = None
            if author_profile:
                author = AuthorResponse(
                    id=author_profile.user_id,
                    display_name=author_profile.display_name or "Unknown",
                    avatar_url=author_profile.avatar_url,
                )

            like_count = await reaction_repo.count_by_target("post", post.id.value)
            c_count = await comment_repo.count_by_post(PostId(value=post.id.value))

            post_responses.append(
                PostResponse(
                    id=post.id.value,
                    community_id=post.community_id.value,
                    created_by=post.author_id.value,
                    category_id=post.category_id.value,
                    title=post.title.value,
                    content=post.content.value,
                    image_url=post.image_url,
                    is_pinned=post.is_pinned,
                    is_locked=post.is_locked,
                    is_edited=post.is_edited,
                    like_count=like_count,
                    comment_count=c_count,
                    created_at=post.created_at,
                    updated_at=post.updated_at,
                    edited_at=post.edited_at,
                    author=author,
                    liked_by_current_user=post.id.value in liked_post_ids,
                )
            )

        return FeedResponse(
            items=post_responses,
            cursor=feed_result.cursor,
            has_more=feed_result.has_more,
        )

    except NotCommunityMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("get_feed_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


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
    session: SessionDep,
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
        await session.commit()

        logger.info("create_post_api_success", post_id=str(post_id))
        return CreatePostResponse(id=post_id.value)

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        ) from e
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
    session: SessionDep,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetPostHandler, Depends(get_get_post_handler)],
    reaction_repo: ReactionRepositoryDep,
    comment_repo: CommentRepositoryDep,
) -> PostResponse:
    """Get a post by ID."""
    try:
        query = GetPostQuery(post_id=post_id, requester_id=current_user_id)
        post = await handler.handle(query)

        # Fetch author profile
        author_profile_result = await session.execute(
            select(ProfileModel).where(ProfileModel.user_id == post.author_id.value)
        )
        author_profile = author_profile_result.scalar_one_or_none()

        author = None
        if author_profile:
            author = AuthorResponse(
                id=author_profile.user_id,
                display_name=author_profile.display_name or "Unknown",
                avatar_url=author_profile.avatar_url,
            )

        # Check if current user liked this post and get counts
        user_id = UserId(value=current_user_id)
        reaction = await reaction_repo.find_by_user_and_target(user_id, "post", post.id.value)
        like_count = await reaction_repo.count_by_target("post", post.id.value)
        c_count = await comment_repo.count_by_post(post.id)

        logger.info("get_post_api_success", post_id=str(post_id))
        return PostResponse(
            id=post.id.value,
            community_id=post.community_id.value,
            created_by=post.author_id.value,  # Map author_id to created_by for frontend
            category_id=post.category_id.value,
            title=post.title.value,
            content=post.content.value,
            image_url=post.image_url,
            is_pinned=post.is_pinned,
            is_locked=post.is_locked,
            is_edited=post.is_edited,
            like_count=like_count,
            comment_count=c_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            edited_at=post.edited_at,
            author=author,
            liked_by_current_user=reaction is not None,
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
    session: SessionDep,
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
        await session.commit()

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
    session: SessionDep,
) -> None:
    """Delete a post."""
    try:
        command = DeletePostCommand(
            post_id=post_id,
            deleter_id=current_user_id,
        )
        await handler.handle(command)
        await session.commit()

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
    session: SessionDep,
) -> None:
    """Lock a post to prevent new comments."""
    try:
        command = LockPostCommand(post_id=post_id, locker_id=current_user_id)
        await handler.handle(command)
        await session.commit()

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
    session: SessionDep,
) -> None:
    """Unlock a post to allow comments again."""
    try:
        command = UnlockPostCommand(post_id=post_id, unlocker_id=current_user_id)
        await handler.handle(command)
        await session.commit()

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
# Pin/Unpin Endpoints
# ============================================================================


@router.post(
    "/{post_id}/pin",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to pin"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def pin_post(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[PinPostHandler, Depends(get_pin_post_handler)],
    session: SessionDep,
) -> None:
    """Pin a post to the top of the feed."""
    try:
        command = PinPostCommand(post_id=post_id, pinner_id=current_user_id)
        await handler.handle(command)
        await session.commit()

        logger.info("pin_post_api_success", post_id=str(post_id))

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotPinPostError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("pin_post_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{post_id}/pin",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to unpin"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def unpin_post_endpoint(
    post_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UnpinPostHandler, Depends(get_unpin_post_handler)],
    session: SessionDep,
) -> None:
    """Unpin a post."""
    try:
        command = UnpinPostCommand(post_id=post_id, unpinner_id=current_user_id)
        await handler.handle(command)
        await session.commit()

        logger.info("unpin_post_api_success", post_id=str(post_id))

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotPinPostError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("unpin_post_domain_error", error=str(e), post_id=str(post_id))
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
    session: SessionDep,
) -> LikeResponse:
    """Like a post."""
    try:
        command = LikePostCommand(post_id=post_id, user_id=current_user_id)
        await handler.handle(command)
        await session.commit()

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
    session: SessionDep,
) -> LikeResponse:
    """Unlike a post."""
    command = UnlikePostCommand(post_id=post_id, user_id=current_user_id)
    await handler.handle(command)
    await session.commit()

    logger.info("unlike_post_api_success", post_id=str(post_id))
    return LikeResponse(message="Post unliked successfully")
