"""Repository interface for course level requirements."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.gamification.domain.entities.course_level_requirement import CourseLevelRequirement


class ICourseLevelRequirementRepository(ABC):
    """Interface for course level requirement persistence."""

    @abstractmethod
    async def save(self, requirement: CourseLevelRequirement) -> None:
        """Save a course level requirement."""

    @abstractmethod
    async def get_by_community_and_course(
        self, community_id: UUID, course_id: UUID
    ) -> CourseLevelRequirement | None:
        """Get requirement by community and course."""

    @abstractmethod
    async def delete(self, community_id: UUID, course_id: UUID) -> None:
        """Delete a course level requirement."""
