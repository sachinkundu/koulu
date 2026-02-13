"""Start course command handler."""

import structlog

from src.classroom.application.commands.start_course import StartCourseCommand
from src.classroom.domain.entities.progress import Progress
from src.classroom.domain.exceptions import CourseNotFoundError, ProgressAlreadyExistsError
from src.classroom.domain.repositories.course_repository import ICourseRepository
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class StartCourseHandler:
    """Handler for starting a course."""

    def __init__(
        self,
        course_repository: ICourseRepository,
        progress_repository: IProgressRepository,
    ) -> None:
        self._course_repository = course_repository
        self._progress_repository = progress_repository

    async def handle(self, command: StartCourseCommand) -> tuple[Progress, LessonId | None]:
        """Start a course for a member.

        Returns:
            Tuple of (progress, first_lesson_id).
        """
        logger.info(
            "start_course_attempt",
            user_id=str(command.user_id),
            course_id=str(command.course_id),
        )

        user_id = UserId(command.user_id)
        course_id = CourseId(value=command.course_id)

        # Verify course exists
        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            raise CourseNotFoundError(str(command.course_id))

        # Check if already started
        existing = await self._progress_repository.get_by_user_and_course(user_id, course_id)
        if existing is not None:
            raise ProgressAlreadyExistsError(str(command.user_id), str(command.course_id))

        # Create progress
        progress = Progress.start_course(user_id=user_id, course_id=course_id)

        # Find first lesson
        first_lesson_id: LessonId | None = None
        modules = course.modules
        if modules:
            lessons = modules[0].lessons
            if lessons:
                first_lesson_id = lessons[0].id
                progress.update_last_accessed(first_lesson_id)

        await self._progress_repository.save(progress)
        await event_bus.publish_all(progress.clear_events())

        logger.info("start_course_success", progress_id=str(progress.id))
        return progress, first_lesson_id
