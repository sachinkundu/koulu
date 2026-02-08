"""Module entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.exceptions import (
    InvalidPositionError,
    LessonNotFoundError,
)
from src.classroom.domain.value_objects.content_type import ContentType
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.lesson_title import LessonTitle
from src.classroom.domain.value_objects.module_description import ModuleDescription
from src.classroom.domain.value_objects.module_id import ModuleId
from src.classroom.domain.value_objects.module_title import ModuleTitle


@dataclass
class Module:
    """Module entity within a Course.

    Contains an ordered list of lessons.
    """

    id: ModuleId
    title: ModuleTitle
    description: ModuleDescription | None
    position: int
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _lessons: list[Lesson] = field(default_factory=list, repr=False)

    @classmethod
    def create(
        cls,
        title: ModuleTitle,
        description: ModuleDescription | None,
        position: int,
    ) -> "Module":
        """Factory method to create a new module."""
        return cls(
            id=ModuleId(value=uuid4()),
            title=title,
            description=description,
            position=position,
        )

    def update(
        self,
        title: ModuleTitle | None = None,
        description: ModuleDescription | None = None,
    ) -> list[str]:
        """Update module details. Returns list of changed field names."""
        changed_fields: list[str] = []

        if title is not None and title != self.title:
            self.title = title
            changed_fields.append("title")

        if description is not None and description != self.description:
            self.description = description
            changed_fields.append("description")

        if changed_fields:
            self._update_timestamp()

        return changed_fields

    def delete(self) -> None:
        """Soft delete the module and all its lessons."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self._update_timestamp()

        # Also soft delete all non-deleted lessons
        for lesson in self._lessons:
            if not lesson.is_deleted:
                lesson.delete()

    def add_lesson(
        self,
        title: LessonTitle,
        content_type: ContentType,
        content: str,
    ) -> Lesson:
        """Add a lesson to this module."""
        position = self.lesson_count + 1
        lesson = Lesson.create(
            title=title,
            content_type=content_type,
            content=content,
            position=position,
        )
        self._lessons.append(lesson)
        self._update_timestamp()
        return lesson

    def remove_lesson(self, lesson_id: LessonId) -> None:
        """Soft delete a lesson by ID."""
        lesson = self.get_lesson_by_id(lesson_id)
        if lesson is None:
            raise LessonNotFoundError(str(lesson_id))
        lesson.delete()
        # Reposition remaining lessons
        self._reposition_lessons()
        self._update_timestamp()

    def get_lesson_by_id(self, lesson_id: LessonId) -> Lesson | None:
        """Get a lesson by ID (including deleted)."""
        for lesson in self._lessons:
            if lesson.id == lesson_id:
                return lesson
        return None

    def reorder_lessons(self, lesson_ids: list[LessonId]) -> None:
        """Reorder lessons by providing ordered list of lesson IDs."""
        active_lessons = [ls for ls in self._lessons if not ls.is_deleted]

        # Validate that all active lesson IDs are provided
        active_ids = {ls.id for ls in active_lessons}
        provided_ids = set(lesson_ids)

        if len(lesson_ids) != len(set(lesson_ids)):
            raise InvalidPositionError("Duplicate position in reorder request")

        if active_ids != provided_ids:
            raise InvalidPositionError("Must include all active lessons in reorder")

        # Reorder
        lesson_map = {ls.id: ls for ls in active_lessons}
        for pos, lid in enumerate(lesson_ids, start=1):
            lesson_map[lid].position = pos

        self._update_timestamp()

    @property
    def lessons(self) -> list[Lesson]:
        """Get non-deleted lessons sorted by position."""
        return sorted(
            [ls for ls in self._lessons if not ls.is_deleted],
            key=lambda ls: ls.position,
        )

    @property
    def all_lessons(self) -> list[Lesson]:
        """Get all lessons including deleted."""
        return list(self._lessons)

    @property
    def lesson_count(self) -> int:
        """Count of non-deleted lessons."""
        return len([ls for ls in self._lessons if not ls.is_deleted])

    def _reposition_lessons(self) -> None:
        """Re-assign sequential positions to non-deleted lessons."""
        for pos, lesson in enumerate(self.lessons, start=1):
            lesson.position = pos

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Modules are equal if they have the same ID."""
        if not isinstance(other, Module):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on module ID."""
        return hash(self.id)
