"""Classroom course API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.classroom.application.commands import (
    CreateCourseCommand,
    DeleteCourseCommand,
    UpdateCourseCommand,
)
from src.classroom.application.handlers import (
    CreateCourseHandler,
    DeleteCourseHandler,
    GetCourseDetailsHandler,
    GetCourseListHandler,
    UpdateCourseHandler,
)
from src.classroom.application.queries import GetCourseDetailsQuery, GetCourseListQuery
from src.classroom.domain.exceptions import (
    ClassroomDomainError,
    CourseAlreadyDeletedError,
    CourseDescriptionTooLongError,
    CourseNotFoundError,
    CourseTitleRequiredError,
    CourseTitleTooLongError,
    CourseTitleTooShortError,
    InvalidCoverImageUrlError,
)
from src.classroom.interface.api.dependencies import (
    CurrentUserIdDep,
    get_course_details_handler,
    get_course_list_handler,
    get_create_course_handler,
    get_delete_course_handler,
    get_update_course_handler,
)
from src.classroom.interface.api.schemas import (
    CourseDetailResponse,
    CourseListResponse,
    CourseResponse,
    CreateCourseRequest,
    CreateCourseResponse,
    ErrorResponse,
    MessageResponse,
    UpdateCourseRequest,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/courses", tags=["Classroom Courses"])


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "",
    response_model=CreateCourseResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def create_course(
    body: CreateCourseRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[CreateCourseHandler, Depends(get_create_course_handler)],
) -> CreateCourseResponse:
    """Create a new course."""
    try:
        command = CreateCourseCommand(
            instructor_id=current_user_id,
            title=body.title,
            description=body.description,
            cover_image_url=body.cover_image_url,
            estimated_duration=body.estimated_duration,
        )
        course_id = await handler.handle(command)

        logger.info("create_course_api_success", course_id=str(course_id))
        return CreateCourseResponse(id=course_id.value)

    except (
        CourseTitleRequiredError,
        CourseTitleTooShortError,
        CourseTitleTooLongError,
        CourseDescriptionTooLongError,
        InvalidCoverImageUrlError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("create_course_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=CourseListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def list_courses(
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetCourseListHandler, Depends(get_course_list_handler)],
) -> CourseListResponse:
    """List all courses."""
    try:
        query = GetCourseListQuery(requester_id=current_user_id)
        courses = await handler.handle(query)

        course_responses = [
            CourseResponse(
                id=c.id.value,
                instructor_id=c.instructor_id.value,
                title=c.title.value,
                description=c.description.value if c.description else None,
                cover_image_url=c.cover_image_url.value if c.cover_image_url else None,
                estimated_duration=c.estimated_duration.value if c.estimated_duration else None,
                module_count=0,
                lesson_count=0,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in courses
        ]

        return CourseListResponse(courses=course_responses, total=len(course_responses))

    except ClassroomDomainError as e:
        logger.error("list_courses_domain_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def get_course(
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetCourseDetailsHandler, Depends(get_course_details_handler)],
) -> CourseDetailResponse:
    """Get course details."""
    try:
        query = GetCourseDetailsQuery(course_id=course_id, requester_id=current_user_id)
        course = await handler.handle(query)

        return CourseDetailResponse(
            id=course.id.value,
            instructor_id=course.instructor_id.value,
            title=course.title.value,
            description=course.description.value if course.description else None,
            cover_image_url=course.cover_image_url.value if course.cover_image_url else None,
            estimated_duration=(
                course.estimated_duration.value if course.estimated_duration else None
            ),
            module_count=0,
            lesson_count=0,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("get_course_domain_error", error=str(e), course_id=str(course_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch(
    "/{course_id}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def update_course(
    course_id: UUID,
    body: UpdateCourseRequest,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[UpdateCourseHandler, Depends(get_update_course_handler)],
) -> MessageResponse:
    """Update a course."""
    try:
        command = UpdateCourseCommand(
            course_id=course_id,
            editor_id=current_user_id,
            title=body.title,
            description=body.description,
            cover_image_url=body.cover_image_url,
            estimated_duration=body.estimated_duration,
        )
        await handler.handle(command)

        logger.info("update_course_api_success", course_id=str(course_id))
        return MessageResponse(message="Course updated successfully")

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CourseAlreadyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except (
        CourseTitleRequiredError,
        CourseTitleTooShortError,
        CourseTitleTooLongError,
        CourseDescriptionTooLongError,
        InvalidCoverImageUrlError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("update_course_domain_error", error=str(e), course_id=str(course_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Course not found"},
    },
)
async def delete_course(
    course_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[DeleteCourseHandler, Depends(get_delete_course_handler)],
) -> None:
    """Soft delete a course."""
    try:
        command = DeleteCourseCommand(
            course_id=course_id,
            deleter_id=current_user_id,
        )
        await handler.handle(command)

        logger.info("delete_course_api_success", course_id=str(course_id))

    except CourseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CourseAlreadyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ClassroomDomainError as e:
        logger.error("delete_course_domain_error", error=str(e), course_id=str(course_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
