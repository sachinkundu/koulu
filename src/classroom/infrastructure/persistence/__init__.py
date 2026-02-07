"""Classroom infrastructure persistence layer."""

from src.classroom.infrastructure.persistence.course_repository import SqlAlchemyCourseRepository
from src.classroom.infrastructure.persistence.models import CourseModel

__all__ = [
    "CourseModel",
    "SqlAlchemyCourseRepository",
]
