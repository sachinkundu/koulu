"""Update module handler."""

import structlog

from src.classroom.application.commands import UpdateModuleCommand
from src.classroom.domain.exceptions import ModuleNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import ModuleDescription, ModuleId, ModuleTitle
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UpdateModuleHandler:
    """Handler for updating modules."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: UpdateModuleCommand) -> None:
        """Handle update module command."""
        logger.info("update_module_attempt", module_id=str(command.module_id))

        module_id = ModuleId(command.module_id)
        course = await self._course_repository.get_course_by_module_id(module_id)
        if course is None:
            raise ModuleNotFoundError(str(module_id))

        module = course.get_module_by_id(module_id)
        if module is None or module.is_deleted:
            raise ModuleNotFoundError(str(module_id))

        title = ModuleTitle(command.title) if command.title is not None else None
        description = (
            ModuleDescription(command.description) if command.description is not None else None
        )

        changed_fields = module.update(title=title, description=description)

        if changed_fields:
            await self._course_repository.save(course)
            await event_bus.publish_all(course.clear_events())
            logger.info(
                "update_module_success",
                module_id=str(module_id),
                changed_fields=changed_fields,
            )
        else:
            logger.info("update_module_no_changes", module_id=str(module_id))
