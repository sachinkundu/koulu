"""Classroom API interface layer."""

from src.classroom.interface.api.course_controller import router as courses_router

__all__ = ["courses_router"]
