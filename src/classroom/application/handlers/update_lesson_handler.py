"""Update lesson handler."""

import structlog

from src.classroom.application.commands import UpdateLessonCommand
from src.classroom.domain.exceptions import LessonNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import LessonId, LessonTitle
from src.classroom.domain.value_objects.content_type import ContentType
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class UpdateLessonHandler:
    """Handler for updating lessons."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, command: UpdateLessonCommand) -> None:
        """Handle update lesson command."""
        logger.info("update_lesson_attempt", lesson_id=str(command.lesson_id))

        lesson_id = LessonId(command.lesson_id)
        course = await self._course_repository.get_course_by_lesson_id(lesson_id)
        if course is None:
            raise LessonNotFoundError(str(lesson_id))

        module = course.find_module_for_lesson(lesson_id)
        if module is None:
            raise LessonNotFoundError(str(lesson_id))

        lesson = module.get_lesson_by_id(lesson_id)
        if lesson is None or lesson.is_deleted:
            raise LessonNotFoundError(str(lesson_id))

        title = LessonTitle(command.title) if command.title is not None else None
        content_type = (
            ContentType.from_string(command.content_type)
            if command.content_type is not None
            else None
        )

        changed_fields = lesson.update(
            title=title,
            content_type=content_type,
            content=command.content,
        )

        if changed_fields:
            await self._course_repository.save(course)
            await event_bus.publish_all(course.clear_events())
            logger.info(
                "update_lesson_success",
                lesson_id=str(lesson_id),
                changed_fields=changed_fields,
            )
        else:
            logger.info("update_lesson_no_changes", lesson_id=str(lesson_id))
