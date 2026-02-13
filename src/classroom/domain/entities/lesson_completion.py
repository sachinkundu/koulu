"""LessonCompletion entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.value_objects.lesson_id import LessonId


@dataclass
class LessonCompletion:
    """Tracks that a member has completed a specific lesson.

    Entity within the Progress aggregate. Each completion records
    the lesson ID and when it was completed.
    """

    id: LessonId  # Reuse LessonId type for the completion record ID
    lesson_id: LessonId
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, lesson_id: LessonId) -> "LessonCompletion":
        """Factory method to create a new lesson completion."""
        return cls(
            id=LessonId(value=uuid4()),
            lesson_id=lesson_id,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LessonCompletion):
            return NotImplemented
        return self.lesson_id == other.lesson_id

    def __hash__(self) -> int:
        return hash(self.lesson_id)
