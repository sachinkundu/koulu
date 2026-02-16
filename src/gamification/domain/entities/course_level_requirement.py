"""CourseLevelRequirement entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.shared.domain.base_entity import BaseEntity


@dataclass
class CourseLevelRequirement(BaseEntity[UUID]):
    """Level requirement for accessing a course in a community."""

    community_id: UUID = field(default_factory=uuid4)
    course_id: UUID = field(default_factory=uuid4)
    minimum_level: int = 1

    @classmethod
    def create(
        cls,
        community_id: UUID,
        course_id: UUID,
        minimum_level: int,
    ) -> CourseLevelRequirement:
        """Create a new course level requirement."""
        return cls(
            id=uuid4(),
            community_id=community_id,
            course_id=course_id,
            minimum_level=minimum_level,
        )

    def update_minimum_level(self, new_level: int) -> None:
        """Update the minimum level requirement."""
        self.minimum_level = new_level
        self._update_timestamp()
