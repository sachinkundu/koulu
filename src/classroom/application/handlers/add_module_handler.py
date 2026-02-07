"""Add module handler."""

import structlog

from src.classroom.application.commands import AddModuleCommand
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import CourseId, ModuleDescription, ModuleId, ModuleTitle
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class AddModuleHandler:
    """Handler for adding modules to courses."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: AddModuleCommand) -> ModuleId:
        """Handle add module command. Returns the created module's ID."""
        logger.info("add_module_attempt", course_id=str(command.course_id))

        course_id = CourseId(command.course_id)
        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError(str(course_id))

        title = ModuleTitle(command.title)
        description = ModuleDescription(command.description) if command.description else None

        module = course.add_module(title=title, description=description)
        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("add_module_success", module_id=str(module.id))
        return module.id
