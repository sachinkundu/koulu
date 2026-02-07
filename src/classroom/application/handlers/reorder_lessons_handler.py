"""Reorder lessons handler."""

import structlog

from src.classroom.application.commands import ReorderLessonsCommand
from src.classroom.domain.exceptions import ModuleNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import LessonId, ModuleId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class ReorderLessonsHandler:
    """Handler for reordering lessons."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: ReorderLessonsCommand) -> None:
        """Handle reorder lessons command."""
        logger.info("reorder_lessons_attempt", module_id=str(command.module_id))

        module_id = ModuleId(command.module_id)
        course = await self._course_repository.get_course_by_module_id(module_id)
        if course is None:
            raise ModuleNotFoundError(str(module_id))

        module = course.get_module_by_id(module_id)
        if module is None or module.is_deleted:
            raise ModuleNotFoundError(str(module_id))

        lesson_ids = [LessonId(lid) for lid in command.lesson_ids]
        module.reorder_lessons(lesson_ids)

        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("reorder_lessons_success", module_id=str(module_id))
