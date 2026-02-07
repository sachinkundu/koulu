"""Course aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.events import CourseCreated, CourseDeleted
from src.classroom.domain.exceptions import CourseAlreadyDeletedError
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass
class Course:
    """
    Course aggregate root.

    Represents a learning course with title, description, cover image,
    and estimated duration. Enforces business rules for course lifecycle.
    """

    id: CourseId
    instructor_id: UserId
    title: CourseTitle
    description: CourseDescription | None = None
    cover_image_url: CoverImageUrl | None = None
    estimated_duration: EstimatedDuration | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        instructor_id: UserId,
        title: CourseTitle,
        description: CourseDescription | None = None,
        cover_image_url: CoverImageUrl | None = None,
        estimated_duration: EstimatedDuration | None = None,
    ) -> "Course":
        """
        Factory method to create a new course.

        Args:
            instructor_id: The admin user creating the course
            title: The course title (already validated)
            description: Optional course description
            cover_image_url: Optional HTTPS cover image URL
            estimated_duration: Optional estimated duration

        Returns:
            A new Course instance
        """
        course_id = CourseId(value=uuid4())
        course = cls(
            id=course_id,
            instructor_id=instructor_id,
            title=title,
            description=description,
            cover_image_url=cover_image_url,
            estimated_duration=estimated_duration,
        )

        course._add_event(
            CourseCreated(
                course_id=course_id,
                instructor_id=instructor_id,
                title=str(title),
            )
        )

        return course

    def update(
        self,
        title: CourseTitle | None = None,
        description: CourseDescription | None = None,
        cover_image_url: CoverImageUrl | None = None,
        estimated_duration: EstimatedDuration | None = None,
    ) -> list[str]:
        """
        Update course details.

        Args:
            title: New title (optional)
            description: New description (optional)
            cover_image_url: New cover image URL (optional)
            estimated_duration: New estimated duration (optional)

        Returns:
            List of changed field names

        Raises:
            CourseAlreadyDeletedError: If course is deleted
        """
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        changed_fields: list[str] = []

        if title is not None and title != self.title:
            self.title = title
            changed_fields.append("title")

        if description is not None and description != self.description:
            self.description = description
            changed_fields.append("description")

        if cover_image_url is not None and cover_image_url != self.cover_image_url:
            self.cover_image_url = cover_image_url
            changed_fields.append("cover_image_url")

        if estimated_duration is not None and estimated_duration != self.estimated_duration:
            self.estimated_duration = estimated_duration
            changed_fields.append("estimated_duration")

        if changed_fields:
            self._update_timestamp()

        return changed_fields

    def delete(self, deleter_id: UserId) -> None:
        """
        Soft delete the course.

        Args:
            deleter_id: The user deleting the course

        Raises:
            CourseAlreadyDeletedError: If already deleted
        """
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self._update_timestamp()
        self._add_event(CourseDeleted(course_id=self.id, deleted_by=deleter_id))

    def _add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published after persistence."""
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def events(self) -> list[DomainEvent]:
        """Get pending domain events (read-only view)."""
        return self._events.copy()

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Courses are equal if they have the same ID."""
        if not isinstance(other, Course):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on course ID."""
        return hash(self.id)
