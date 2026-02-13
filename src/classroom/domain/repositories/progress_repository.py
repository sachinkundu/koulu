"""Progress repository interface."""

from abc import ABC, abstractmethod

from src.classroom.domain.entities.progress import Progress
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.progress_id import ProgressId
from src.identity.domain.value_objects import UserId


class IProgressRepository(ABC):
    """Interface for Progress persistence operations."""

    @abstractmethod
    async def save(self, progress: Progress) -> None:
        """Save a progress record (create or update)."""
        ...

    @abstractmethod
    async def get_by_id(self, progress_id: ProgressId) -> Progress | None:
        """Get progress by ID."""
        ...

    @abstractmethod
    async def get_by_user_and_course(self, user_id: UserId, course_id: CourseId) -> Progress | None:
        """Get progress for a specific user and course."""
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UserId) -> list[Progress]:
        """Get all progress records for a user."""
        ...
