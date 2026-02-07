"""FastAPI dependencies for Classroom context."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.classroom.application.handlers import (
    CreateCourseHandler,
    DeleteCourseHandler,
    GetCourseDetailsHandler,
    GetCourseListHandler,
    UpdateCourseHandler,
)
from src.classroom.infrastructure.persistence import SqlAlchemyCourseRepository
from src.config import settings
from src.identity.infrastructure.services import JWTService

# Import shared database dependencies from identity
from src.identity.interface.api.dependencies import SessionDep

# ============================================================================
# Repository Dependencies
# ============================================================================


def get_course_repository(session: SessionDep) -> SqlAlchemyCourseRepository:
    """Get course repository."""
    return SqlAlchemyCourseRepository(session)


CourseRepositoryDep = Annotated[SqlAlchemyCourseRepository, Depends(get_course_repository)]


# ============================================================================
# Handler Dependencies
# ============================================================================


def get_create_course_handler(course_repo: CourseRepositoryDep) -> CreateCourseHandler:
    """Get create course handler."""
    return CreateCourseHandler(course_repository=course_repo)


def get_update_course_handler(course_repo: CourseRepositoryDep) -> UpdateCourseHandler:
    """Get update course handler."""
    return UpdateCourseHandler(course_repository=course_repo)


def get_delete_course_handler(course_repo: CourseRepositoryDep) -> DeleteCourseHandler:
    """Get delete course handler."""
    return DeleteCourseHandler(course_repository=course_repo)


def get_course_list_handler(course_repo: CourseRepositoryDep) -> GetCourseListHandler:
    """Get course list handler."""
    return GetCourseListHandler(course_repository=course_repo)


def get_course_details_handler(course_repo: CourseRepositoryDep) -> GetCourseDetailsHandler:
    """Get course details handler."""
    return GetCourseDetailsHandler(course_repository=course_repo)


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
    """Get current user ID from JWT token."""
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
