"""Get next incomplete lesson query handler."""

import structlog

from src.classroom.application.queries.get_next_incomplete_lesson import (
    GetNextIncompleteLessonQuery,
)
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


class GetNextIncompleteLessonHandler:
    """Handler for getting the next incomplete lesson (Continue button)."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, query: GetNextIncompleteLessonQuery) -> LessonId | None:
        """Get the next incomplete lesson for a user.

        Returns:
            LessonId of the next incomplete lesson, or None if all complete.
            If no progress exists, returns the first lesson.
        """
        user_id = UserId(query.user_id)
        course_id = CourseId(value=query.course_id)

        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError(str(query.course_id))

        # If no progress, return first lesson
        progress = await self._progress_repository.get_by_user_and_course(user_id, course_id)
        if progress is None:
            return self._get_first_lesson(course)

        # Find next incomplete
        completed_ids = progress.get_completed_lesson_ids()
        from src.classroom.domain.entities.course import Course

        assert isinstance(course, Course)
        for module in course.modules:
            for lesson in module.lessons:
                if lesson.id not in completed_ids:
                    return lesson.id

        # All complete — return last lesson
        return self._get_last_lesson(course)

    def _get_first_lesson(self, course: object) -> LessonId | None:
        from src.classroom.domain.entities.course import Course

        assert isinstance(course, Course)
        modules = course.modules
        if modules:
            lessons = modules[0].lessons
            if lessons:
                return lessons[0].id
        return None

    def _get_last_lesson(self, course: object) -> LessonId | None:
        from src.classroom.domain.entities.course import Course

        assert isinstance(course, Course)
        modules = course.modules
        if modules:
            lessons = modules[-1].lessons
            if lessons:
                return lessons[-1].id
        return None
