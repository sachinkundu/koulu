"""Classroom application queries."""

from src.classroom.application.queries.get_course_details import GetCourseDetailsQuery
from src.classroom.application.queries.get_course_list import GetCourseListQuery
from src.classroom.application.queries.get_lesson import GetLessonQuery
from src.classroom.application.queries.get_next_incomplete_lesson import (
    GetNextIncompleteLessonQuery,
)
from src.classroom.application.queries.get_progress import GetProgressQuery

__all__ = [
    "GetCourseDetailsQuery",
    "GetCourseListQuery",
    "GetLessonQuery",
    "GetNextIncompleteLessonQuery",
    "GetProgressQuery",
]
