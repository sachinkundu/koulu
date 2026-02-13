"""Classroom domain entities."""

from src.classroom.domain.entities.course import Course
from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.entities.lesson_completion import LessonCompletion
from src.classroom.domain.entities.module import Module
from src.classroom.domain.entities.progress import Progress

__all__ = [
    "Course",
    "Lesson",
    "LessonCompletion",
    "Module",
    "Progress",
]
