"""Reorder modules handler."""

import structlog

from src.classroom.application.commands import ReorderModulesCommand
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import CourseId, ModuleId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class ReorderModulesHandler:
    """Handler for reordering modules."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: ReorderModulesCommand) -> None:
        """Handle reorder modules command."""
        logger.info("reorder_modules_attempt", course_id=str(command.course_id))

        course_id = CourseId(command.course_id)
        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError(str(course_id))

        module_ids = [ModuleId(mid) for mid in command.module_ids]
        course.reorder_modules(module_ids)

        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("reorder_modules_success", course_id=str(course_id))
