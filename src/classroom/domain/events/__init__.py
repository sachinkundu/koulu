"""Classroom domain events."""

from src.classroom.domain.events.course_events import CourseCreated, CourseDeleted

__all__ = [
    "CourseCreated",
    "CourseDeleted",
]
