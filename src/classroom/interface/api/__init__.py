"""Classroom API interface layer."""

from src.classroom.interface.api.course_controller import router as courses_router
from src.classroom.interface.api.lesson_controller import router as lessons_router
from src.classroom.interface.api.module_controller import router as modules_router

__all__ = ["courses_router", "lessons_router", "modules_router"]
