"""Progress aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.entities.lesson_completion import LessonCompletion
from src.classroom.domain.events.progress_events import (
    CourseCompleted,
    LessonCompleted,
    ProgressStarted,
)
from src.classroom.domain.exceptions import (
    LessonAlreadyCompletedError,
    LessonNotCompletedError,
)
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.progress_id import ProgressId
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass
class Progress:
    """Progress aggregate root.

    Tracks a member's progress through a specific course.
    One progress record per member per course.
    Manages lesson completions and calculates percentages on demand.
    """

    id: ProgressId
    user_id: UserId
    course_id: CourseId
    started_at: datetime
    last_accessed_lesson_id: LessonId | None = None
    last_accessed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _completions: list[LessonCompletion] = field(default_factory=list, repr=False)
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def start_course(cls, user_id: UserId, course_id: CourseId) -> "Progress":
        """Factory method to start tracking progress on a course."""
        now = datetime.now(UTC)
        progress = cls(
            id=ProgressId(value=uuid4()),
            user_id=user_id,
            course_id=course_id,
            started_at=now,
        )
        progress._add_event(ProgressStarted(user_id=user_id, course_id=course_id))
        return progress

    def mark_lesson_complete(
        self,
        lesson_id: LessonId,
        total_lessons: int,
    ) -> None:
        """Mark a lesson as complete.

        Args:
            lesson_id: The lesson to mark complete.
            total_lessons: Total non-deleted lessons in the course (for course completion check).
        """
        if self.is_lesson_completed(lesson_id):
            raise LessonAlreadyCompletedError(str(lesson_id))

        completion = LessonCompletion.create(lesson_id=lesson_id)
        self._completions.append(completion)
        self._update_last_accessed(lesson_id)
        self._update_timestamp()

        self._add_event(
            LessonCompleted(
                user_id=self.user_id,
                course_id=self.course_id,
                lesson_id=lesson_id,
            )
        )

        # Check for course completion
        if len(self._completions) >= total_lessons and total_lessons > 0:
            self._add_event(
                CourseCompleted(
                    user_id=self.user_id,
                    course_id=self.course_id,
                )
            )

    def unmark_lesson(self, lesson_id: LessonId) -> None:
        """Remove completion for a lesson."""
        if not self.is_lesson_completed(lesson_id):
            raise LessonNotCompletedError(str(lesson_id))

        self._completions = [c for c in self._completions if c.lesson_id != lesson_id]
        self._update_timestamp()

    def is_lesson_completed(self, lesson_id: LessonId) -> bool:
        """Check if a specific lesson has been completed."""
        return any(c.lesson_id == lesson_id for c in self._completions)

    def calculate_completion_percentage(self, total_lessons: int) -> int:
        """Calculate completion percentage.

        Args:
            total_lessons: Total non-deleted lessons in the course.

        Returns:
            Integer percentage 0-100.
        """
        if total_lessons == 0:
            return 0
        completed = len(self._completions)
        return min(round(completed / total_lessons * 100), 100)

    def get_completed_lesson_ids(self) -> set[LessonId]:
        """Get set of completed lesson IDs."""
        return {c.lesson_id for c in self._completions}

    def update_last_accessed(self, lesson_id: LessonId) -> None:
        """Update the last accessed lesson."""
        self._update_last_accessed(lesson_id)
        self._update_timestamp()

    @property
    def completions(self) -> list[LessonCompletion]:
        """Get all lesson completions (read-only view)."""
        return list(self._completions)

    @property
    def completed_count(self) -> int:
        """Get number of completed lessons."""
        return len(self._completions)

    # ========================================================================
    # Events
    # ========================================================================

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def events(self) -> list[DomainEvent]:
        return self._events.copy()

    def _update_last_accessed(self, lesson_id: LessonId) -> None:
        self.last_accessed_lesson_id = lesson_id
        self.last_accessed_at = datetime.now(UTC)

    def _update_timestamp(self) -> None:
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Progress):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
