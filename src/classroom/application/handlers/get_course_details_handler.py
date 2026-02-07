"""Get course details query handler."""

import structlog

from src.classroom.application.queries import GetCourseDetailsQuery
from src.classroom.domain.entities import Course
from src.classroom.domain.exceptions import CourseNotFoundError
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import CourseId

logger = structlog.get_logger()


class GetCourseDetailsHandler:
    """Handler for getting course details."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, query: GetCourseDetailsQuery) -> Course:
        """
        Handle get course details query.

        Args:
            query: The get course details query

        Returns:
            The course entity

        Raises:
            CourseNotFoundError: If course doesn't exist
        """
        logger.info(
            "get_course_details_attempt",
            course_id=str(query.course_id),
        )

        course_id = CourseId(query.course_id)

        course = await self._course_repository.get_by_id(course_id)
        if course is None:
            logger.warning("get_course_details_not_found", course_id=str(course_id))
            raise CourseNotFoundError(str(course_id))

        logger.info("get_course_details_success", course_id=str(course_id))
        return course
