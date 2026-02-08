"""Delete lesson handler."""

import structlog

from src.classroom.application.commands import DeleteLessonCommand
from src.classroom.domain.exceptions import LessonNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import LessonId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class DeleteLessonHandler:
    """Handler for deleting lessons."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: DeleteLessonCommand) -> None:
        """Handle delete lesson command."""
        logger.info("delete_lesson_attempt", lesson_id=str(command.lesson_id))

        lesson_id = LessonId(command.lesson_id)
        course = await self._course_repository.get_course_by_lesson_id(lesson_id)
        if course is None:
            raise LessonNotFoundError(str(lesson_id))

        module = course.find_module_for_lesson(lesson_id)
        if module is None:
            raise LessonNotFoundError(str(lesson_id))

        module.remove_lesson(lesson_id)
        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("delete_lesson_success", lesson_id=str(lesson_id))
