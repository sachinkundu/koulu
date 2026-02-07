"""Classroom lesson API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.classroom.application.commands import (
    AddLessonCommand,
    DeleteLessonCommand,
    ReorderLessonsCommand,
    UpdateLessonCommand,
)
from src.classroom.application.handlers import (
    AddLessonHandler,
    DeleteLessonHandler,
    ReorderLessonsHandler,
    UpdateLessonHandler,
)
from src.classroom.domain.exceptions import (
    ClassroomDomainError,
    InvalidContentTypeError,
    InvalidPositionError,
    InvalidVideoUrlError,
    LessonNotFoundError,
    LessonTitleRequiredError,
    LessonTitleTooLongError,
    LessonTitleTooShortError,
    ModuleNotFoundError,
    TextContentRequiredError,
    TextContentTooLongError,
    VideoUrlRequiredError,
)
from src.classroom.interface.api.dependencies import (
    CurrentUserIdDep,
    get_add_lesson_handler,
    get_delete_lesson_handler,
    get_reorder_lessons_handler,
    get_update_lesson_handler,
)
from src.classroom.interface.api.schemas import (
    AddLessonRequest,
    CreateLessonResponse,
    ErrorResponse,
    MessageResponse,
    ReorderRequest,
    UpdateLessonRequest,
)

logger = structlog.get_logger()

router = APIRouter(tags=["Classroom Lessons"])


@router.post(
    "/modules/{module_id}/lessons",
    response_model=CreateLessonResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Module not found"},
    },
)
async def add_lesson(
    module_id: UUID,
    body: AddLessonRequest,
    current_user_id: CurrentUserIdDep,  # noqa: ARG001
    handler: Annotated[AddLessonHandler, Depends(get_add_lesson_handler)],
) -> CreateLessonResponse:
    """Add a lesson to a module."""
    try:
        command = AddLessonCommand(
            module_id=module_id,
            title=body.title,
            content_type=body.content_type,
            content=body.content,
        )
        lesson_id = await handler.handle(command)

        logger.info("add_lesson_api_success", lesson_id=str(lesson_id))
        return CreateLessonResponse(id=lesson_id.value)

    except ModuleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (
        LessonTitleRequiredError,
        LessonTitleTooShortError,
        LessonTitleTooLongError,
        InvalidContentTypeError,
        TextContentRequiredError,
        TextContentTooLongError,
        VideoUrlRequiredError,
        InvalidVideoUrlError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("add_lesson_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch(
    "/lessons/{lesson_id}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Lesson not found"},
    },
)
async def update_lesson(
    lesson_id: UUID,
    body: UpdateLessonRequest,
    current_user_id: CurrentUserIdDep,  # noqa: ARG001
    handler: Annotated[UpdateLessonHandler, Depends(get_update_lesson_handler)],
) -> MessageResponse:
    """Update a lesson."""
    try:
        command = UpdateLessonCommand(
            lesson_id=lesson_id,
            title=body.title,
            content_type=body.content_type,
            content=body.content,
        )
        await handler.handle(command)

        logger.info("update_lesson_api_success", lesson_id=str(lesson_id))
        return MessageResponse(message="Lesson updated successfully")

    except LessonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (
        LessonTitleRequiredError,
        LessonTitleTooShortError,
        LessonTitleTooLongError,
        InvalidContentTypeError,
        TextContentRequiredError,
        TextContentTooLongError,
        VideoUrlRequiredError,
        InvalidVideoUrlError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("update_lesson_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/lessons/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Lesson not found"},
    },
)
async def delete_lesson(
    lesson_id: UUID,
    current_user_id: CurrentUserIdDep,  # noqa: ARG001
    handler: Annotated[DeleteLessonHandler, Depends(get_delete_lesson_handler)],
) -> None:
    """Soft delete a lesson."""
    try:
        command = DeleteLessonCommand(lesson_id=lesson_id)
        await handler.handle(command)

        logger.info("delete_lesson_api_success", lesson_id=str(lesson_id))

    except LessonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("delete_lesson_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.put(
    "/modules/{module_id}/lessons/reorder",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Module not found"},
    },
)
async def reorder_lessons(
    module_id: UUID,
    body: ReorderRequest,
    current_user_id: CurrentUserIdDep,  # noqa: ARG001
    handler: Annotated[ReorderLessonsHandler, Depends(get_reorder_lessons_handler)],
) -> MessageResponse:
    """Reorder lessons in a module."""
    try:
        command = ReorderLessonsCommand(
            module_id=module_id,
            lesson_ids=body.ordered_ids,
        )
        await handler.handle(command)

        logger.info("reorder_lessons_api_success", module_id=str(module_id))
        return MessageResponse(message="Lessons reordered successfully")

    except ModuleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except InvalidPositionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("reorder_lessons_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
