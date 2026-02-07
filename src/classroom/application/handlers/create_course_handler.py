"""Create course command handler."""

import structlog

from src.classroom.application.commands import CreateCourseCommand
from src.classroom.domain.entities import Course
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class CreateCourseHandler:
    """Handler for creating courses."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: CreateCourseCommand) -> CourseId:
        """
        Handle course creation.

        Args:
            command: The create course command

        Returns:
            The created course's ID

        Raises:
            CourseTitleRequiredError: If title is invalid
            CourseTitleTooShortError: If title is too short
            CourseTitleTooLongError: If title is too long
            CourseDescriptionTooLongError: If description is too long
            InvalidCoverImageUrlError: If cover image URL is invalid
        """
        logger.info(
            "create_course_attempt",
            instructor_id=str(command.instructor_id),
        )

        instructor_id = UserId(command.instructor_id)

        # Validate and create value objects (will raise if invalid)
        title = CourseTitle(command.title)
        description = CourseDescription(command.description) if command.description else None
        cover_image_url = (
            CoverImageUrl(command.cover_image_url) if command.cover_image_url else None
        )
        estimated_duration = (
            EstimatedDuration(command.estimated_duration) if command.estimated_duration else None
        )

        # Create course
        course = Course.create(
            instructor_id=instructor_id,
            title=title,
            description=description,
            cover_image_url=cover_image_url,
            estimated_duration=estimated_duration,
        )

        # Save course
        await self._course_repository.save(course)

        # Publish domain events
        await event_bus.publish_all(course.clear_events())

        logger.info("create_course_success", course_id=str(course.id))
        return course.id
