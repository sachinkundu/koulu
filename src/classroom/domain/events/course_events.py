"""Course domain events."""

from dataclasses import dataclass

from src.classroom.domain.value_objects.course_id import CourseId
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass(frozen=True, kw_only=True)
class CourseCreated(DomainEvent):
    """Event published when a course is created."""

    course_id: CourseId
    instructor_id: UserId
    title: str


@dataclass(frozen=True, kw_only=True)
class CourseDeleted(DomainEvent):
    """Event published when a course is soft deleted."""

    course_id: CourseId
    deleted_by: UserId
