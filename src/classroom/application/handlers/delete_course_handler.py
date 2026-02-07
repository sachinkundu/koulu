"""Delete course command handler."""

import structlog

from src.classroom.application.commands import DeleteCourseCommand
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import CourseId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class DeleteCourseHandler:
    """Handler for deleting courses."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: DeleteCourseCommand) -> None:
        """
        Handle course soft deletion.

        Args:
            command: The delete course command

        Raises:
            CourseNotFoundError: If course doesn't exist
            CourseAlreadyDeletedError: If already deleted
        """
        logger.info(
            "delete_course_attempt",
            course_id=str(command.course_id),
            deleter_id=str(command.deleter_id),
        )

        course_id = CourseId(command.course_id)
        deleter_id = UserId(command.deleter_id)

        # Get the course
        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            logger.warning("delete_course_not_found", course_id=str(course_id))
            raise CourseNotFoundError(str(course_id))

        # Soft delete
        course.delete(deleter_id)
        await self._course_repository.save(course)

        # Publish domain events
        await event_bus.publish_all(course.clear_events())

        logger.info("delete_course_success", course_id=str(course_id))
