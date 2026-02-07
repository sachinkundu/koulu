"""Update course command handler."""

import structlog

from src.classroom.application.commands import UpdateCourseCommand
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UpdateCourseHandler:
    """Handler for updating courses."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: UpdateCourseCommand) -> None:
        """
        Handle course update.

        Args:
            command: The update course command

        Raises:
            CourseNotFoundError: If course doesn't exist
            CourseAlreadyDeletedError: If course is deleted
        """
        logger.info(
            "update_course_attempt",
            course_id=str(command.course_id),
            editor_id=str(command.editor_id),
        )

        course_id = CourseId(command.course_id)

        # Get the course
        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            logger.warning("update_course_not_found", course_id=str(course_id))
            raise CourseNotFoundError(str(course_id))

        # Build update parameters
        title = CourseTitle(command.title) if command.title is not None else None
        description = (
            CourseDescription(command.description) if command.description is not None else None
        )
        cover_image_url = (
            CoverImageUrl(command.cover_image_url) if command.cover_image_url is not None else None
        )
        estimated_duration = (
            EstimatedDuration(command.estimated_duration)
            if command.estimated_duration is not None
            else None
        )

        # Update the course
        changed_fields = course.update(
            title=title,
            description=description,
            cover_image_url=cover_image_url,
            estimated_duration=estimated_duration,
        )

        # Save if anything changed
        if changed_fields:
            await self._course_repository.save(course)
            await event_bus.publish_all(course.clear_events())
            logger.info(
                "update_course_success", course_id=str(course_id), changed_fields=changed_fields
            )
        else:
            logger.info("update_course_no_changes", course_id=str(course_id))
