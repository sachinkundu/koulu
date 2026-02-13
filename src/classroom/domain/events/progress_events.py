"""Progress domain events."""

from dataclasses import dataclass

from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ProgressStarted(DomainEvent):
    """Event published when a member starts a course."""

    user_id: UserId
    course_id: CourseId


@dataclass(frozen=True, kw_only=True)
class LessonCompleted(DomainEvent):
    """Event published when a member marks a lesson as complete."""

    user_id: UserId
    course_id: CourseId
    lesson_id: LessonId


@dataclass(frozen=True, kw_only=True)
class CourseCompleted(DomainEvent):
    """Event published when a member completes all lessons in a course."""

    user_id: UserId
    course_id: CourseId
