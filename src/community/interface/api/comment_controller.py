"""Community comment API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.community.application.commands import (
    AddCommentCommand,
    DeleteCommentCommand,
    EditCommentCommand,
    LikeCommentCommand,
    UnlikeCommentCommand,
)
from src.community.application.handlers import (
    AddCommentHandler,
    DeleteCommentHandler,
    EditCommentHandler,
    GetPostCommentsHandler,
    LikeCommentHandler,
    UnlikeCommentHandler,
)
from src.community.application.queries import GetPostCommentsQuery
from src.community.domain.exceptions import (
    CannotDeleteCommentError,
    CannotEditCommentError,
    CommentContentRequiredError,
    CommentContentTooLongError,
    CommentNotFoundError,
    CommunityDomainError,
    MaxReplyDepthExceededError,
    NotCommunityMemberError,
    PostLockedError,
    PostNotFoundError,
)
from src.community.interface.api.dependencies import (
    CurrentUserIdDep,
    get_add_comment_handler,
    get_delete_comment_handler,
    get_edit_comment_handler,
    get_get_post_comments_handler,
    get_like_comment_handler,
    get_unlike_comment_handler,
)
from src.community.interface.api.schemas import (
    AddCommentRequest,
    CommentResponse,
    CreateCommentResponse,
    EditCommentRequest,
    ErrorResponse,
    LikeResponse,
)

logger = structlog.get_logger()

# Router for /api/v1/community/posts/{post_id}/comments
post_comments_router = APIRouter(prefix="/community/posts", tags=["Comments"])

# Router for /api/v1/community/comments/{comment_id}
comments_router = APIRouter(prefix="/community/comments", tags=["Comments"])


# ============================================================================
# Post Comments Endpoints
# ============================================================================


@post_comments_router.post(
    "/{post_id}/comments",
    response_model=CreateCommentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def add_comment(
    post_id: UUID,
    body: AddCommentRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[AddCommentHandler, Depends(get_add_comment_handler)],
) -> CreateCommentResponse:
    """Add a comment to a post."""
    try:
        command = AddCommentCommand(
            post_id=post_id,
            author_id=current_user_id,
            content=body.content,
            parent_comment_id=body.parent_comment_id,
        )
        comment_id = await handler.handle(command)

        logger.info("add_comment_api_success", post_id=str(post_id), comment_id=str(comment_id))
        return CreateCommentResponse(comment_id=comment_id.value)

    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (PostLockedError, MaxReplyDepthExceededError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except NotCommunityMemberError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except (CommentContentRequiredError, CommentContentTooLongError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except CommentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("add_comment_domain_error", error=str(e), post_id=str(post_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@post_comments_router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_post_comments(
    post_id: UUID,
    handler: Annotated[GetPostCommentsHandler, Depends(get_get_post_comments_handler)],
    limit: int = 100,
    offset: int = 0,
) -> list[CommentResponse]:
    """Get comments for a post."""
    query = GetPostCommentsQuery(post_id=post_id, limit=limit, offset=offset)
    comments_with_likes = await handler.handle(query)

    return [
        CommentResponse(
            id=cwl.comment.id.value,
            post_id=cwl.comment.post_id.value,
            author_id=cwl.comment.author_id.value,
            content=str(cwl.comment.content),
            parent_comment_id=cwl.comment.parent_comment_id.value
            if cwl.comment.parent_comment_id
            else None,
            is_deleted=cwl.comment.is_deleted,
            like_count=cwl.like_count,
            is_edited=cwl.comment.is_edited,
            created_at=cwl.comment.created_at,
            updated_at=cwl.comment.updated_at,
            edited_at=cwl.comment.edited_at,
        )
        for cwl in comments_with_likes
    ]


# ============================================================================
# Comment Endpoints (by comment ID)
# ============================================================================


@comments_router.patch(
    "/{comment_id}",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to edit"},
        404: {"model": ErrorResponse, "description": "Comment not found"},
    },
)
async def edit_comment(
    comment_id: UUID,
    body: EditCommentRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[EditCommentHandler, Depends(get_edit_comment_handler)],
) -> LikeResponse:
    """Edit a comment."""
    try:
        command = EditCommentCommand(
            comment_id=comment_id,
            editor_id=current_user_id,
            content=body.content,
        )
        await handler.handle(command)

        logger.info("edit_comment_api_success", comment_id=str(comment_id))
        return LikeResponse(message="Comment edited successfully")

    except CommentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotEditCommentError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except (CommentContentRequiredError, CommentContentTooLongError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("edit_comment_domain_error", error=str(e), comment_id=str(comment_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@comments_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not authorized to delete"},
        404: {"model": ErrorResponse, "description": "Comment not found"},
    },
)
async def delete_comment(
    comment_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[DeleteCommentHandler, Depends(get_delete_comment_handler)],
) -> None:
    """Delete a comment."""
    try:
        command = DeleteCommentCommand(comment_id=comment_id, deleter_id=current_user_id)
        await handler.handle(command)

        logger.info("delete_comment_api_success", comment_id=str(comment_id))

    except CommentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (NotCommunityMemberError, CannotDeleteCommentError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("delete_comment_domain_error", error=str(e), comment_id=str(comment_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Like/Unlike Comment Endpoints
# ============================================================================


@comments_router.post(
    "/{comment_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Comment not found"},
    },
)
async def like_comment(
    comment_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[LikeCommentHandler, Depends(get_like_comment_handler)],
) -> LikeResponse:
    """Like a comment."""
    try:
        command = LikeCommentCommand(comment_id=comment_id, user_id=current_user_id)
        await handler.handle(command)

        logger.info("like_comment_api_success", comment_id=str(comment_id))
        return LikeResponse(message="Comment liked successfully")

    except CommentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CommunityDomainError as e:
        logger.error("like_comment_domain_error", error=str(e), comment_id=str(comment_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@comments_router.delete(
    "/{comment_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def unlike_comment(
    comment_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UnlikeCommentHandler, Depends(get_unlike_comment_handler)],
) -> LikeResponse:
    """Unlike a comment."""
    command = UnlikeCommentCommand(comment_id=comment_id, user_id=current_user_id)
    await handler.handle(command)

    logger.info("unlike_comment_api_success", comment_id=str(comment_id))
    return LikeResponse(message="Comment unliked successfully")
