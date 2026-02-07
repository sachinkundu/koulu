"""FastAPI dependencies for Community context."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.community.application.handlers import (
    CreatePostHandler,
    DeletePostHandler,
    GetPostHandler,
    UpdatePostHandler,
)
from src.community.infrastructure.persistence import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyMemberRepository,
    SqlAlchemyPostRepository,
)
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


PostRepositoryDep = Annotated[SqlAlchemyPostRepository, Depends(get_post_repository)]
CategoryRepositoryDep = Annotated[SqlAlchemyCategoryRepository, Depends(get_category_repository)]
MemberRepositoryDep = Annotated[SqlAlchemyMemberRepository, Depends(get_member_repository)]


# ============================================================================
# Handler Dependencies
# ============================================================================


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
    member_repo: MemberRepositoryDep,
) -> DeletePostHandler:
    """Get delete post handler."""
    return DeletePostHandler(
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
