"""Add lesson handler."""

import structlog

from src.classroom.application.commands import AddLessonCommand
from src.classroom.domain.exceptions import ModuleNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import LessonId, LessonTitle, ModuleId
from src.classroom.domain.value_objects.content_type import ContentType
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class AddLessonHandler:
    """Handler for adding lessons to modules."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: AddLessonCommand) -> LessonId:
        """Handle add lesson command. Returns the created lesson's ID."""
        logger.info("add_lesson_attempt", module_id=str(command.module_id))

        module_id = ModuleId(command.module_id)
        course = await self._course_repository.get_course_by_module_id(module_id)
        if course is None:
            raise ModuleNotFoundError(str(module_id))

        title = LessonTitle(command.title)
        content_type = ContentType.from_string(command.content_type)

        lesson = course.add_lesson_to_module(
            module_id=module_id,
            title=title,
            content_type=content_type,
            content=command.content,
        )

        await self._course_repository.save(course)
        await event_bus.publish_all(course.clear_events())

        logger.info("add_lesson_success", lesson_id=str(lesson.id))
        return lesson.id
