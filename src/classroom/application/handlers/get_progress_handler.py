"""Get progress query handler."""

from dataclasses import dataclass

import structlog

from src.classroom.application.queries.get_progress import GetProgressQuery
from src.classroom.domain.exceptions import CourseNotFoundError, ProgressNotFoundError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass
class ProgressResult:
    """Result of progress query."""

    user_id: str
    course_id: str
    started_at: str
    completion_percentage: int
    completed_lesson_ids: list[str]
    next_incomplete_lesson_id: str | None
    last_accessed_lesson_id: str | None


class GetProgressHandler:
    """Handler for getting progress on a course."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, query: GetProgressQuery) -> ProgressResult:
        """Get progress for a user on a course."""
        user_id = UserId(query.user_id)
        course_id = CourseId(value=query.course_id)

        # Verify course exists (include deleted for progress retention)
        course = await self._course_repository.get_by_id_include_deleted(course_id)
        if course is None:
            raise CourseNotFoundError(str(query.course_id))

        # Get progress
        progress = await self._progress_repository.get_by_user_and_course(user_id, course_id)
        if progress is None:
            raise ProgressNotFoundError(str(query.user_id), str(query.course_id))

        total_lessons = course.lesson_count
        completion_pct = progress.calculate_completion_percentage(total_lessons)
        completed_ids = progress.get_completed_lesson_ids()

        # Find next incomplete
        next_incomplete = self._find_next_incomplete(course, completed_ids)

        return ProgressResult(
            user_id=str(query.user_id),
            course_id=str(query.course_id),
            started_at=progress.started_at.isoformat(),
            completion_percentage=completion_pct,
            completed_lesson_ids=[str(lid) for lid in completed_ids],
            next_incomplete_lesson_id=str(next_incomplete) if next_incomplete else None,
            last_accessed_lesson_id=(
                str(progress.last_accessed_lesson_id) if progress.last_accessed_lesson_id else None
            ),
        )

    def _find_next_incomplete(
        self, course: object, completed_ids: set[LessonId]
    ) -> LessonId | None:
        """Find first incomplete lesson by position order."""
        from src.classroom.domain.entities.course import Course

        assert isinstance(course, Course)
        for module in course.modules:
            for lesson in module.lessons:
                if lesson.id not in completed_ids:
                    return lesson.id
        return None
