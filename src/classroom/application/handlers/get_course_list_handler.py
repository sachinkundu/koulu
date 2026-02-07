"""Get course list query handler."""

import structlog

from src.classroom.application.queries import GetCourseListQuery
from src.classroom.domain.entities import Course
from src.classroom.domain.repositories import ICourseRepository

logger = structlog.get_logger()


class GetCourseListHandler:
    """Handler for listing courses."""

    def __init__(self, course_repository: ICourseRepository) -> None:
        """Initialize with dependencies."""
        self._course_repository = course_repository

    async def handle(self, query: GetCourseListQuery) -> list[Course]:
        """
        Handle course list query.

        Args:
            query: The get course list query

        Returns:
            List of courses
        """
        logger.info(
            "get_course_list_attempt",
            requester_id=str(query.requester_id),
        )

        courses = await self._course_repository.list_all(
            include_deleted=query.include_deleted,
            limit=query.limit,
            offset=query.offset,
        )

        logger.info("get_course_list_success", count=len(courses))
        return courses
