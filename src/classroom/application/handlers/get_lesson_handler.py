"""Get lesson query handler."""

from dataclasses import dataclass

import structlog

from src.classroom.application.queries.get_lesson import GetLessonQuery
from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.exceptions import LessonNotFoundError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId

logger = structlog.get_logger()


@dataclass
class LessonWithContext:
    """Lesson with navigation and completion context."""

    lesson: Lesson
    is_complete: bool
    next_lesson_id: LessonId | None
    prev_lesson_id: LessonId | None
    module_title: str
    course_id: str
    course_title: str


class GetLessonHandler:
    """Handler for getting a lesson with context."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, query: GetLessonQuery) -> LessonWithContext:
        """Get a lesson with navigation and completion context."""
        user_id = UserId(query.user_id)
        lesson_id = LessonId(value=query.lesson_id)

        # Find course containing this lesson
        course = await self._course_repository.get_course_by_lesson_id(lesson_id)
        if course is None:
            raise LessonNotFoundError(str(query.lesson_id))

        # Find the module and lesson
        module = course.find_module_for_lesson(lesson_id)
        if module is None:
            raise LessonNotFoundError(str(query.lesson_id))

        lesson = module.get_lesson_by_id(lesson_id)
        if lesson is None or lesson.is_deleted:
            raise LessonNotFoundError(str(query.lesson_id))

        # Get completion status
        progress = await self._progress_repository.get_by_user_and_course(user_id, course.id)
        is_complete = progress.is_lesson_completed(lesson_id) if progress else False

        # Update last accessed
        if progress is not None:
            progress.update_last_accessed(lesson_id)
            await self._progress_repository.save(progress)

        # Calculate prev/next navigation
        prev_id, next_id = self._get_navigation(course, module, lesson)

        return LessonWithContext(
            lesson=lesson,
            is_complete=is_complete,
            next_lesson_id=next_id,
            prev_lesson_id=prev_id,
            module_title=module.title.value,
            course_id=str(course.id),
            course_title=course.title.value,
        )

    def _get_navigation(
        self, course: object, current_module: object, current_lesson: Lesson
    ) -> tuple[LessonId | None, LessonId | None]:
        """Calculate previous and next lesson IDs across modules."""
        # Build a flat ordered list of all lessons across all modules
        from src.classroom.domain.entities.course import Course
        from src.classroom.domain.entities.module import Module

        assert isinstance(course, Course)
        assert isinstance(current_module, Module)

        all_lessons: list[Lesson] = []
        for mod in course.modules:
            all_lessons.extend(mod.lessons)

        # Find current lesson index
        current_idx = None
        for i, ls in enumerate(all_lessons):
            if ls.id == current_lesson.id:
                current_idx = i
                break

        if current_idx is None:
            return None, None

        prev_id = all_lessons[current_idx - 1].id if current_idx > 0 else None
        next_id = all_lessons[current_idx + 1].id if current_idx < len(all_lessons) - 1 else None

        return prev_id, next_id
