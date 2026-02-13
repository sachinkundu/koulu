"""Mark lesson complete command handler."""

import structlog

from src.classroom.application.commands.mark_lesson_complete import MarkLessonCompleteCommand
from src.classroom.domain.entities.progress import Progress
from src.classroom.domain.exceptions import LessonNotFoundError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class MarkLessonCompleteHandler:
    """Handler for marking a lesson as complete."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, command: MarkLessonCompleteCommand) -> None:
        """Mark a lesson as complete, auto-starting the course if needed."""
        logger.info(
            "mark_lesson_complete_attempt",
            user_id=str(command.user_id),
            lesson_id=str(command.lesson_id),
        )

        user_id = UserId(command.user_id)
        lesson_id = LessonId(value=command.lesson_id)

        # Find the course that owns this lesson
        course = await self._course_repository.get_course_by_lesson_id(lesson_id)
        if course is None:
            raise LessonNotFoundError(str(command.lesson_id))

        course_id = course.id

        # Get or create progress (auto-start)
        progress = await self._progress_repository.get_by_user_and_course(user_id, course_id)
        if progress is None:
            progress = Progress.start_course(user_id=user_id, course_id=course_id)

        # Mark complete
        total_lessons = course.lesson_count
        progress.mark_lesson_complete(lesson_id, total_lessons)
        progress.update_last_accessed(lesson_id)

        await self._progress_repository.save(progress)
        await event_bus.publish_all(progress.clear_events())

        logger.info(
            "mark_lesson_complete_success",
            lesson_id=str(lesson_id),
            completed_count=progress.completed_count,
        )
