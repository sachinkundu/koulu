"""FastAPI dependencies for Classroom context."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from src.classroom.application.handlers import (
    AddLessonHandler,
    AddModuleHandler,
    CreateCourseHandler,
    DeleteCourseHandler,
    DeleteLessonHandler,
    DeleteModuleHandler,
    GetCourseDetailsHandler,
    GetCourseListHandler,
    GetLessonHandler,
    GetNextIncompleteLessonHandler,
    GetProgressHandler,
    MarkLessonCompleteHandler,
    ReorderLessonsHandler,
    ReorderModulesHandler,
    StartCourseHandler,
    UnmarkLessonHandler,
    UpdateCourseHandler,
    UpdateLessonHandler,
    UpdateModuleHandler,
)
from src.classroom.infrastructure.persistence import (
    SqlAlchemyCourseRepository,
    SqlAlchemyProgressRepository,
)
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


def get_progress_repository(session: SessionDep) -> SqlAlchemyProgressRepository:
    """Get progress repository."""
    return SqlAlchemyProgressRepository(session)


ProgressRepositoryDep = Annotated[SqlAlchemyProgressRepository, Depends(get_progress_repository)]


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


# Module handlers


def get_add_module_handler(course_repo: CourseRepositoryDep) -> AddModuleHandler:
    """Get add module handler."""
    return AddModuleHandler(course_repository=course_repo)


def get_update_module_handler(course_repo: CourseRepositoryDep) -> UpdateModuleHandler:
    """Get update module handler."""
    return UpdateModuleHandler(course_repository=course_repo)


def get_delete_module_handler(course_repo: CourseRepositoryDep) -> DeleteModuleHandler:
    """Get delete module handler."""
    return DeleteModuleHandler(course_repository=course_repo)


def get_reorder_modules_handler(course_repo: CourseRepositoryDep) -> ReorderModulesHandler:
    """Get reorder modules handler."""
    return ReorderModulesHandler(course_repository=course_repo)


# Lesson handlers


def get_add_lesson_handler(course_repo: CourseRepositoryDep) -> AddLessonHandler:
    """Get add lesson handler."""
    return AddLessonHandler(course_repository=course_repo)


def get_update_lesson_handler(course_repo: CourseRepositoryDep) -> UpdateLessonHandler:
    """Get update lesson handler."""
    return UpdateLessonHandler(course_repository=course_repo)


def get_delete_lesson_handler(course_repo: CourseRepositoryDep) -> DeleteLessonHandler:
    """Get delete lesson handler."""
    return DeleteLessonHandler(course_repository=course_repo)


def get_reorder_lessons_handler(course_repo: CourseRepositoryDep) -> ReorderLessonsHandler:
    """Get reorder lessons handler."""
    return ReorderLessonsHandler(course_repository=course_repo)


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


async def require_admin(
    current_user_id: CurrentUserIdDep,
    session: SessionDep,
) -> UUID:
    """Verify the current user has admin role in the community.

    Raises 403 if the user is not an admin.
    Returns the user_id for downstream use.
    """
    from src.community.infrastructure.persistence.models import CommunityMemberModel

    result = await session.execute(
        select(CommunityMemberModel.role).where(
            CommunityMemberModel.user_id == current_user_id,
            CommunityMemberModel.role == "ADMIN",
            CommunityMemberModel.is_active.is_(True),
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user_id


AdminVerifiedDep = Annotated[UUID, Depends(require_admin)]


# ============================================================================
# Progress Handler Dependencies
# ============================================================================


def get_start_course_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> StartCourseHandler:
    """Get start course handler."""
    return StartCourseHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )


def get_get_lesson_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> GetLessonHandler:
    """Get lesson handler."""
    return GetLessonHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )


def get_mark_lesson_complete_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> MarkLessonCompleteHandler:
    """Get mark lesson complete handler."""
    return MarkLessonCompleteHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )


def get_unmark_lesson_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> UnmarkLessonHandler:
    """Get unmark lesson handler."""
    return UnmarkLessonHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )


def get_progress_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> GetProgressHandler:
    """Get progress handler."""
    return GetProgressHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )


def get_next_incomplete_lesson_handler(
    course_repo: CourseRepositoryDep,
    progress_repo: ProgressRepositoryDep,
) -> GetNextIncompleteLessonHandler:
    """Get next incomplete lesson handler."""
    return GetNextIncompleteLessonHandler(
        course_repository=course_repo,
        progress_repository=progress_repo,
    )
