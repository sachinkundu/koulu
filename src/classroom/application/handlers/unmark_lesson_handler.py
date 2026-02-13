"""Unmark lesson command handler."""

import structlog

from src.classroom.application.commands.unmark_lesson import UnmarkLessonCommand
from src.classroom.domain.exceptions import LessonNotFoundError, ProgressNotFoundError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class UnmarkLessonHandler:
    """Handler for un-marking a lesson as complete."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, command: UnmarkLessonCommand) -> None:
        """Un-mark a lesson as complete."""
        logger.info(
            "unmark_lesson_attempt",
            user_id=str(command.user_id),
            lesson_id=str(command.lesson_id),
        )

        user_id = UserId(command.user_id)
        lesson_id = LessonId(value=command.lesson_id)

        # Find the course
        course = await self._course_repository.get_course_by_lesson_id(lesson_id)
        if course is None:
            raise LessonNotFoundError(str(command.lesson_id))

        # Get progress
        progress = await self._progress_repository.get_by_user_and_course(user_id, course.id)
        if progress is None:
            raise ProgressNotFoundError(str(command.user_id), str(course.id))

        progress.unmark_lesson(lesson_id)
        await self._progress_repository.save(progress)

        logger.info(
            "unmark_lesson_success",
            lesson_id=str(lesson_id),
            completed_count=progress.completed_count,
        )
