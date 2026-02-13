"""Classroom application handlers."""

from src.classroom.application.handlers.add_lesson_handler import AddLessonHandler
from src.classroom.application.handlers.add_module_handler import AddModuleHandler
from src.classroom.application.handlers.create_course_handler import CreateCourseHandler
from src.classroom.application.handlers.delete_course_handler import DeleteCourseHandler
from src.classroom.application.handlers.delete_lesson_handler import DeleteLessonHandler
from src.classroom.application.handlers.delete_module_handler import DeleteModuleHandler
from src.classroom.application.handlers.get_course_details_handler import GetCourseDetailsHandler
from src.classroom.application.handlers.get_course_list_handler import GetCourseListHandler
from src.classroom.application.handlers.get_lesson_handler import GetLessonHandler
from src.classroom.application.handlers.get_next_incomplete_lesson_handler import (
    GetNextIncompleteLessonHandler,
)
from src.classroom.application.handlers.get_progress_handler import GetProgressHandler
from src.classroom.application.handlers.mark_lesson_complete_handler import (
    MarkLessonCompleteHandler,
)
from src.classroom.application.handlers.reorder_lessons_handler import ReorderLessonsHandler
from src.classroom.application.handlers.reorder_modules_handler import ReorderModulesHandler
from src.classroom.application.handlers.start_course_handler import StartCourseHandler
from src.classroom.application.handlers.unmark_lesson_handler import UnmarkLessonHandler
from src.classroom.application.handlers.update_course_handler import UpdateCourseHandler
from src.classroom.application.handlers.update_lesson_handler import UpdateLessonHandler
from src.classroom.application.handlers.update_module_handler import UpdateModuleHandler

__all__ = [
    "AddLessonHandler",
    "AddModuleHandler",
    "CreateCourseHandler",
    "DeleteCourseHandler",
    "DeleteLessonHandler",
    "DeleteModuleHandler",
    "GetCourseDetailsHandler",
    "GetCourseListHandler",
    "GetLessonHandler",
    "GetNextIncompleteLessonHandler",
    "GetProgressHandler",
    "MarkLessonCompleteHandler",
    "ReorderLessonsHandler",
    "ReorderModulesHandler",
    "StartCourseHandler",
    "UnmarkLessonHandler",
    "UpdateCourseHandler",
    "UpdateLessonHandler",
    "UpdateModuleHandler",
]
