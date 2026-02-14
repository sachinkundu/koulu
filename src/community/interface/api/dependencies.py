"""FastAPI dependencies for Community context."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.community.application.handlers import (
    AddCommentHandler,
    CreateCategoryHandler,
    CreatePostHandler,
    DeleteCategoryHandler,
    DeleteCommentHandler,
    DeletePostHandler,
    EditCommentHandler,
    GetFeedHandler,
    GetPostCommentsHandler,
    GetPostHandler,
    LikeCommentHandler,
    LikePostHandler,
    ListCategoriesHandler,
    ListMembersHandler,
    LockPostHandler,
    PinPostHandler,
    SearchHandler,
    UnlikeCommentHandler,
    UnlikePostHandler,
    UnlockPostHandler,
    UnpinPostHandler,
    UpdateCategoryHandler,
    UpdatePostHandler,
)
from src.community.infrastructure.persistence import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyCommentRepository,
    SqlAlchemyMemberRepository,
    SqlAlchemyPostRepository,
    SqlAlchemyReactionRepository,
    SqlAlchemySearchRepository,
)
from src.community.infrastructure.services import InMemoryRateLimiter
from src.config import settings
from src.identity.infrastructure.services import JWTService

# Import shared database dependencies from identity
# (reusing the same database instance)
from src.identity.interface.api.dependencies import SessionDep as SessionDep

# ============================================================================
# Repository Dependencies
# ============================================================================


def get_post_repository(session: SessionDep) -> SqlAlchemyPostRepository:
    """Get post repository."""
    return SqlAlchemyPostRepository(session)


def get_category_repository(session: SessionDep) -> SqlAlchemyCategoryRepository:
    """Get category repository."""
    return SqlAlchemyCategoryRepository(session)


def get_member_repository(session: SessionDep) -> SqlAlchemyMemberRepository:
    """Get member repository."""
    return SqlAlchemyMemberRepository(session)


def get_comment_repository(session: SessionDep) -> SqlAlchemyCommentRepository:
    """Get comment repository."""
    return SqlAlchemyCommentRepository(session)


def get_reaction_repository(session: SessionDep) -> SqlAlchemyReactionRepository:
    """Get reaction repository."""
    return SqlAlchemyReactionRepository(session)


PostRepositoryDep = Annotated[SqlAlchemyPostRepository, Depends(get_post_repository)]
CategoryRepositoryDep = Annotated[SqlAlchemyCategoryRepository, Depends(get_category_repository)]
MemberRepositoryDep = Annotated[SqlAlchemyMemberRepository, Depends(get_member_repository)]
CommentRepositoryDep = Annotated[SqlAlchemyCommentRepository, Depends(get_comment_repository)]
ReactionRepositoryDep = Annotated[SqlAlchemyReactionRepository, Depends(get_reaction_repository)]


def get_search_repository(session: SessionDep) -> SqlAlchemySearchRepository:
    """Get search repository."""
    return SqlAlchemySearchRepository(session)


SearchRepositoryDep = Annotated[SqlAlchemySearchRepository, Depends(get_search_repository)]


# ============================================================================
# Handler Dependencies
# ============================================================================


def get_rate_limiter() -> InMemoryRateLimiter:
    """Get rate limiter."""
    return InMemoryRateLimiter()


def get_create_post_handler(
    post_repo: PostRepositoryDep,
    category_repo: CategoryRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> CreatePostHandler:
    """Get create post handler."""
    return CreatePostHandler(
        post_repository=post_repo,
        category_repository=category_repo,
        member_repository=member_repo,
        rate_limiter=get_rate_limiter(),
    )


def get_get_post_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> GetPostHandler:
    """Get post handler."""
    return GetPostHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_update_post_handler(
    post_repo: PostRepositoryDep,
    category_repo: CategoryRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> UpdatePostHandler:
    """Get update post handler."""
    return UpdatePostHandler(
        post_repository=post_repo,
        category_repository=category_repo,
        member_repository=member_repo,
    )


def get_delete_post_handler(
    post_repo: PostRepositoryDep,
    comment_repo: CommentRepositoryDep,
    reaction_repo: ReactionRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> DeletePostHandler:
    """Get delete post handler."""
    return DeletePostHandler(
        post_repository=post_repo,
        comment_repository=comment_repo,
        reaction_repository=reaction_repo,
        member_repository=member_repo,
    )


def get_lock_post_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> LockPostHandler:
    """Get lock post handler."""
    return LockPostHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_unlock_post_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> UnlockPostHandler:
    """Get unlock post handler."""
    return UnlockPostHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_pin_post_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> PinPostHandler:
    """Get pin post handler."""
    return PinPostHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_unpin_post_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> UnpinPostHandler:
    """Get unpin post handler."""
    return UnpinPostHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_add_comment_handler(
    comment_repo: CommentRepositoryDep,
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> AddCommentHandler:
    """Get add comment handler."""
    return AddCommentHandler(
        comment_repository=comment_repo,
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_edit_comment_handler(
    comment_repo: CommentRepositoryDep,
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> EditCommentHandler:
    """Get edit comment handler."""
    return EditCommentHandler(
        comment_repository=comment_repo,
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_delete_comment_handler(
    comment_repo: CommentRepositoryDep,
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> DeleteCommentHandler:
    """Get delete comment handler."""
    return DeleteCommentHandler(
        comment_repository=comment_repo,
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_like_post_handler(
    reaction_repo: ReactionRepositoryDep,
    post_repo: PostRepositoryDep,
) -> LikePostHandler:
    """Get like post handler."""
    return LikePostHandler(
        reaction_repository=reaction_repo,
        post_repository=post_repo,
    )


def get_unlike_post_handler(
    reaction_repo: ReactionRepositoryDep,
) -> UnlikePostHandler:
    """Get unlike post handler."""
    return UnlikePostHandler(
        reaction_repository=reaction_repo,
    )


def get_like_comment_handler(
    reaction_repo: ReactionRepositoryDep,
    comment_repo: CommentRepositoryDep,
) -> LikeCommentHandler:
    """Get like comment handler."""
    return LikeCommentHandler(
        reaction_repository=reaction_repo,
        comment_repository=comment_repo,
    )


def get_unlike_comment_handler(
    reaction_repo: ReactionRepositoryDep,
) -> UnlikeCommentHandler:
    """Get unlike comment handler."""
    return UnlikeCommentHandler(
        reaction_repository=reaction_repo,
    )


def get_get_post_comments_handler(
    comment_repo: CommentRepositoryDep,
    reaction_repo: ReactionRepositoryDep,
) -> GetPostCommentsHandler:
    """Get post comments handler."""
    return GetPostCommentsHandler(
        comment_repository=comment_repo,
        reaction_repository=reaction_repo,
    )


def get_list_categories_handler(
    category_repo: CategoryRepositoryDep,
) -> ListCategoriesHandler:
    """Get list categories handler."""
    return ListCategoriesHandler(
        category_repository=category_repo,
    )


def get_create_category_handler(
    category_repo: CategoryRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> CreateCategoryHandler:
    """Get create category handler."""
    return CreateCategoryHandler(
        category_repository=category_repo,
        member_repository=member_repo,
    )


def get_update_category_handler(
    category_repo: CategoryRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> UpdateCategoryHandler:
    """Get update category handler."""
    return UpdateCategoryHandler(
        category_repository=category_repo,
        member_repository=member_repo,
    )


def get_delete_category_handler(
    category_repo: CategoryRepositoryDep,
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> DeleteCategoryHandler:
    """Get delete category handler."""
    return DeleteCategoryHandler(
        category_repository=category_repo,
        post_repository=post_repo,
        member_repository=member_repo,
    )


def get_list_members_handler(
    member_repo: MemberRepositoryDep,
) -> ListMembersHandler:
    """Get list members handler."""
    return ListMembersHandler(
        member_repository=member_repo,
    )


ListMembersHandlerDep = Annotated[ListMembersHandler, Depends(get_list_members_handler)]


def get_search_handler(
    search_repo: SearchRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> SearchHandler:
    """Get search handler."""
    return SearchHandler(
        search_repository=search_repo,
        member_repository=member_repo,
    )


SearchHandlerDep = Annotated[SearchHandler, Depends(get_search_handler)]


def get_get_feed_handler(
    post_repo: PostRepositoryDep,
    member_repo: MemberRepositoryDep,
) -> GetFeedHandler:
    """Get feed handler."""
    return GetFeedHandler(
        post_repository=post_repo,
        member_repository=member_repo,
    )


# ============================================================================
# Authentication Dependencies
# ============================================================================

security = HTTPBearer(auto_error=False)


def get_token_generator() -> JWTService:
    """Get JWT service instance."""
    return JWTService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
        refresh_token_remember_me_days=settings.jwt_refresh_token_remember_me_days,
    )


async def get_current_user_id(
    _request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> UUID:
    """
    Get current user ID from JWT token.

    Raises HTTPException 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_generator = get_token_generator()
    user_id = token_generator.validate_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id.value


CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
