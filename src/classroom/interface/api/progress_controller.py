"""Classroom progress and lesson consumption API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.classroom.application.commands import (
    MarkLessonCompleteCommand,
    StartCourseCommand,
    UnmarkLessonCommand,
)
from src.classroom.application.handlers import (
    GetLessonHandler,
    GetNextIncompleteLessonHandler,
    GetProgressHandler,
    MarkLessonCompleteHandler,
    StartCourseHandler,
    UnmarkLessonHandler,
)
from src.classroom.application.queries import (
    GetLessonQuery,
    GetNextIncompleteLessonQuery,
    GetProgressQuery,
)
from src.classroom.domain.exceptions import (
    ClassroomDomainError,
    CourseNotFoundError,
    LessonAlreadyCompletedError,
    LessonNotCompletedError,
    LessonNotFoundError,
    ProgressAlreadyExistsError,
    ProgressNotFoundError,
)
from src.classroom.interface.api.dependencies import (
    CurrentUserIdDep,
    get_get_lesson_handler,
    get_mark_lesson_complete_handler,
    get_next_incomplete_lesson_handler,
    get_progress_handler,
    get_start_course_handler,
    get_unmark_lesson_handler,
)
from src.classroom.interface.api.schemas import (
    ErrorResponse,
    LessonContextResponse,
    MessageResponse,
    NextLessonResponse,
    ProgressDetailResponse,
    StartCourseResponse,
)

logger = structlog.get_logger()

router = APIRouter(tags=["Classroom Progress"])


# ============================================================================
# Lesson Consumption
# ============================================================================


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonContextResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Lesson not found"},
    },
)
async def get_lesson(
    lesson_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetLessonHandler, Depends(get_get_lesson_handler)],
) -> LessonContextResponse:
    """Get a lesson with content, navigation context, and completion status."""
    try:
        query = GetLessonQuery(lesson_id=lesson_id, user_id=current_user_id)
        result = await handler.handle(query)

        return LessonContextResponse(
            id=result.lesson.id.value,
            title=result.lesson.title.value,
            content_type=result.lesson.content_type.value,
            content=result.lesson.content,
            position=result.lesson.position,
            is_complete=result.is_complete,
            next_lesson_id=result.next_lesson_id.value if result.next_lesson_id else None,
            prev_lesson_id=result.prev_lesson_id.value if result.prev_lesson_id else None,
            module_title=result.module_title,
            course_id=UUID(result.course_id),
            course_title=result.course_title,
            created_at=result.lesson.created_at,
            updated_at=result.lesson.updated_at,
        )

    except LessonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("get_lesson_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Course Start & Continue
# ============================================================================


@router.post(
    "/courses/{course_id}/start",
    response_model=StartCourseResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
        409: {"model": ErrorResponse, "description": "Already started"},
    },
)
async def start_course(
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[StartCourseHandler, Depends(get_start_course_handler)],
) -> StartCourseResponse:
    """Start a course. Creates a progress record."""
    try:
        command = StartCourseCommand(user_id=current_user_id, course_id=course_id)
        progress, first_lesson_id = await handler.handle(command)

        return StartCourseResponse(
            progress_id=progress.id.value,
            first_lesson_id=first_lesson_id.value if first_lesson_id else None,
        )

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ProgressAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("start_course_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/courses/{course_id}/continue",
    response_model=NextLessonResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def continue_course(
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetNextIncompleteLessonHandler, Depends(get_next_incomplete_lesson_handler)],
) -> NextLessonResponse:
    """Get the next incomplete lesson for 'Continue' button."""
    try:
        query = GetNextIncompleteLessonQuery(user_id=current_user_id, course_id=course_id)
        lesson_id = await handler.handle(query)

        return NextLessonResponse(
            lesson_id=lesson_id.value if lesson_id else None,
        )

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("continue_course_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Progress Tracking
# ============================================================================


@router.get(
    "/progress/courses/{course_id}",
    response_model=ProgressDetailResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course or progress not found"},
    },
)
async def get_progress(
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetProgressHandler, Depends(get_progress_handler)],
) -> ProgressDetailResponse:
    """Get progress for the current user on a course."""
    try:
        query = GetProgressQuery(user_id=current_user_id, course_id=course_id)
        result = await handler.handle(query)

        return ProgressDetailResponse(
            user_id=UUID(result.user_id),
            course_id=UUID(result.course_id),
            started_at=result.started_at,
            completion_percentage=result.completion_percentage,
            completed_lesson_ids=[UUID(lid) for lid in result.completed_lesson_ids],
            next_incomplete_lesson_id=(
                UUID(result.next_incomplete_lesson_id) if result.next_incomplete_lesson_id else None
            ),
            last_accessed_lesson_id=(
                UUID(result.last_accessed_lesson_id) if result.last_accessed_lesson_id else None
            ),
        )

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ProgressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("get_progress_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/progress/lessons/{lesson_id}/complete",
    response_model=MessageResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Lesson not found"},
        409: {"model": ErrorResponse, "description": "Already completed"},
    },
)
async def mark_lesson_complete(
    lesson_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[MarkLessonCompleteHandler, Depends(get_mark_lesson_complete_handler)],
) -> MessageResponse:
    """Mark a lesson as complete."""
    try:
        command = MarkLessonCompleteCommand(user_id=current_user_id, lesson_id=lesson_id)
        await handler.handle(command)

        return MessageResponse(message="Lesson marked as complete")

    except LessonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except LessonAlreadyCompletedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("mark_lesson_complete_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/progress/lessons/{lesson_id}/complete",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Lesson or progress not found"},
    },
)
async def unmark_lesson_complete(
    lesson_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UnmarkLessonHandler, Depends(get_unmark_lesson_handler)],
) -> None:
    """Un-mark a lesson as complete."""
    try:
        command = UnmarkLessonCommand(user_id=current_user_id, lesson_id=lesson_id)
        await handler.handle(command)

    except LessonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ProgressNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except LessonNotCompletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("unmark_lesson_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
