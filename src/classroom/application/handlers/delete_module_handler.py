"""Delete module handler."""

import structlog

from src.classroom.application.commands import DeleteModuleCommand
from src.classroom.domain.exceptions import ModuleNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import ModuleId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class DeleteModuleHandler:
    """Handler for deleting modules."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: DeleteModuleCommand) -> None:
        """Handle delete module command."""
        logger.info("delete_module_attempt", module_id=str(command.module_id))

        module_id = ModuleId(command.module_id)
        course = await self._course_repository.get_course_by_module_id(module_id)
        if course is None:
            raise ModuleNotFoundError(str(module_id))

        course.remove_module(module_id)
        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("delete_module_success", module_id=str(module_id))
