"""Course repository interface."""

from abc import ABC, abstractmethod

from src.classroom.domain.entities import Course
from src.classroom.domain.value_objects import CourseId, LessonId, ModuleId


class ICourseRepository(ABC):
    """Interface for Course persistence operations."""

    @abstractmethod
    async def save(self, course: Course) -> None:
        """Save a course (create or update)."""
        ...

    @abstractmethod
    async def get_by_id(self, course_id: CourseId) -> Course | None:
        """Get a course by ID (excluding deleted)."""
        ...

    @abstractmethod
    async def get_by_id_include_deleted(self, course_id: CourseId) -> Course | None:
        """Get a course by ID including deleted courses."""
        ...

    @abstractmethod
    async def list_all(
        self,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Course]:
        """List all courses."""
        ...

    @abstractmethod
    async def get_course_by_module_id(self, module_id: ModuleId) -> Course | None:
        """Get the course that contains a specific module (excluding deleted courses)."""
        ...

    @abstractmethod
    async def get_course_by_lesson_id(self, lesson_id: LessonId) -> Course | None:
        """Get the course that contains a specific lesson (excluding deleted courses)."""
        ...
