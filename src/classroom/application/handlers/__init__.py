"""Classroom application handlers."""

from src.classroom.application.handlers.create_course_handler import CreateCourseHandler
from src.classroom.application.handlers.delete_course_handler import DeleteCourseHandler
from src.classroom.application.handlers.get_course_details_handler import GetCourseDetailsHandler
from src.classroom.application.handlers.get_course_list_handler import GetCourseListHandler
from src.classroom.application.handlers.update_course_handler import UpdateCourseHandler

__all__ = [
    "CreateCourseHandler",
    "DeleteCourseHandler",
    "GetCourseDetailsHandler",
    "GetCourseListHandler",
    "UpdateCourseHandler",
]
