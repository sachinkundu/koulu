"""Course aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.entities.module import Module
from src.classroom.domain.events import CourseCreated, CourseDeleted
from src.classroom.domain.exceptions import (
    CourseAlreadyDeletedError,
    InvalidPositionError,
    ModuleNotFoundError,
)
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
    ModuleDescription,
    ModuleId,
    ModuleTitle,
)
from src.classroom.domain.value_objects.content_type import ContentType
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.lesson_title import LessonTitle
from src.identity.domain.value_objects import UserId
from src.shared.domain import DomainEvent


@dataclass
class Course:
    """Course aggregate root.

    Represents a learning course with title, description, cover image,
    and estimated duration. Contains modules which contain lessons.
    Enforces business rules for course lifecycle.
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
    _modules: list[Module] = field(default_factory=list, repr=False)
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
        """Factory method to create a new course."""
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
        """Update course details. Returns list of changed field names."""
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
        """Soft delete the course."""
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self._update_timestamp()
        self._add_event(CourseDeleted(course_id=self.id, deleted_by=deleter_id))

    # ========================================================================
    # Module Management
    # ========================================================================

    def add_module(
        self,
        title: ModuleTitle,
        description: ModuleDescription | None = None,
    ) -> Module:
        """Add a module to this course."""
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        position = self.module_count + 1
        module = Module.create(
            title=title,
            description=description,
            position=position,
        )
        self._modules.append(module)
        self._update_timestamp()
        return module

    def remove_module(self, module_id: ModuleId) -> None:
        """Soft delete a module by ID."""
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        module = self.get_module_by_id(module_id)
        if module is None:
            raise ModuleNotFoundError(str(module_id))
        module.delete()
        # Reposition remaining modules
        self._reposition_modules()
        self._update_timestamp()

    def get_module_by_id(self, module_id: ModuleId) -> Module | None:
        """Get a module by ID (including deleted)."""
        for module in self._modules:
            if module.id == module_id:
                return module
        return None

    def reorder_modules(self, module_ids: list[ModuleId]) -> None:
        """Reorder modules by providing ordered list of module IDs."""
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        active_modules = [m for m in self._modules if not m.is_deleted]

        # Validate that all active module IDs are provided
        active_ids = {m.id for m in active_modules}
        provided_ids = set(module_ids)

        if len(module_ids) != len(set(module_ids)):
            raise InvalidPositionError("Duplicate position in reorder request")

        if active_ids != provided_ids:
            raise InvalidPositionError("Must include all active modules in reorder")

        # Reorder
        module_map = {m.id: m for m in active_modules}
        for pos, mid in enumerate(module_ids, start=1):
            module_map[mid].position = pos

        self._update_timestamp()

    @property
    def modules(self) -> list[Module]:
        """Get non-deleted modules sorted by position."""
        return sorted(
            [m for m in self._modules if not m.is_deleted],
            key=lambda m: m.position,
        )

    @property
    def all_modules(self) -> list[Module]:
        """Get all modules including deleted."""
        return list(self._modules)

    @property
    def module_count(self) -> int:
        """Count of non-deleted modules."""
        return len([m for m in self._modules if not m.is_deleted])

    @property
    def lesson_count(self) -> int:
        """Count of non-deleted lessons across all non-deleted modules."""
        return sum(m.lesson_count for m in self._modules if not m.is_deleted)

    # ========================================================================
    # Lesson convenience methods (via module lookup)
    # ========================================================================

    def find_module_for_lesson(self, lesson_id: LessonId) -> Module | None:
        """Find the module that contains a given lesson."""
        for module in self._modules:
            if module.get_lesson_by_id(lesson_id) is not None:
                return module
        return None

    def add_lesson_to_module(
        self,
        module_id: ModuleId,
        title: LessonTitle,
        content_type: ContentType,
        content: str,
    ) -> Lesson:
        """Add a lesson to a specific module."""
        if self.is_deleted:
            raise CourseAlreadyDeletedError()

        module = self.get_module_by_id(module_id)
        if module is None or module.is_deleted:
            raise ModuleNotFoundError(str(module_id))

        lesson = module.add_lesson(title=title, content_type=content_type, content=content)
        self._update_timestamp()
        return lesson

    # ========================================================================
    # Events
    # ========================================================================

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

    def _reposition_modules(self) -> None:
        """Re-assign sequential positions to non-deleted modules."""
        for pos, module in enumerate(self.modules, start=1):
            module.position = pos

    def __eq__(self, other: object) -> bool:
        """Courses are equal if they have the same ID."""
        if not isinstance(other, Course):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on course ID."""
        return hash(self.id)
