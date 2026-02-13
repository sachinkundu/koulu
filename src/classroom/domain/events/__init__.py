"""Classroom domain events."""

from src.classroom.domain.events.course_events import CourseCreated, CourseDeleted
from src.classroom.domain.events.progress_events import (
    CourseCompleted,
    LessonCompleted,
    ProgressStarted,
)

__all__ = [
    "CourseCompleted",
    "CourseCreated",
    "CourseDeleted",
    "LessonCompleted",
    "ProgressStarted",
]
