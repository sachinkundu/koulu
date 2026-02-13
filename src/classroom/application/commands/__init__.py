"""Classroom application commands."""

from src.classroom.application.commands.add_lesson import AddLessonCommand
from src.classroom.application.commands.add_module import AddModuleCommand
from src.classroom.application.commands.create_course import CreateCourseCommand
from src.classroom.application.commands.delete_course import DeleteCourseCommand
from src.classroom.application.commands.delete_lesson import DeleteLessonCommand
from src.classroom.application.commands.delete_module import DeleteModuleCommand
from src.classroom.application.commands.mark_lesson_complete import MarkLessonCompleteCommand
from src.classroom.application.commands.reorder_lessons import ReorderLessonsCommand
from src.classroom.application.commands.reorder_modules import ReorderModulesCommand
from src.classroom.application.commands.start_course import StartCourseCommand
from src.classroom.application.commands.unmark_lesson import UnmarkLessonCommand
from src.classroom.application.commands.update_course import UpdateCourseCommand
from src.classroom.application.commands.update_lesson import UpdateLessonCommand
from src.classroom.application.commands.update_module import UpdateModuleCommand

__all__ = [
    "AddLessonCommand",
    "AddModuleCommand",
    "CreateCourseCommand",
    "DeleteCourseCommand",
    "DeleteLessonCommand",
    "DeleteModuleCommand",
    "MarkLessonCompleteCommand",
    "ReorderLessonsCommand",
    "ReorderModulesCommand",
    "StartCourseCommand",
    "UnmarkLessonCommand",
    "UpdateCourseCommand",
    "UpdateLessonCommand",
    "UpdateModuleCommand",
]
