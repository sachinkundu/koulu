"""LevelConfiguration aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.shared.domain.base_entity import BaseEntity


@dataclass
class LevelDefinition:
    """A single level's configuration."""

    level: int
    name: str
    threshold: int


DEFAULT_LEVELS = [
    LevelDefinition(level=1, name="Student", threshold=0),
    LevelDefinition(level=2, name="Practitioner", threshold=10),
    LevelDefinition(level=3, name="Builder", threshold=30),
    LevelDefinition(level=4, name="Leader", threshold=60),
    LevelDefinition(level=5, name="Mentor", threshold=100),
    LevelDefinition(level=6, name="Empire Builder", threshold=150),
    LevelDefinition(level=7, name="Ruler", threshold=210),
    LevelDefinition(level=8, name="Legend", threshold=280),
    LevelDefinition(level=9, name="Icon", threshold=360),
]


@dataclass
class LevelConfiguration(BaseEntity[UUID]):
    """Per-community level configuration (9 levels)."""

    community_id: UUID = field(default_factory=uuid4)
    levels: list[LevelDefinition] = field(default_factory=list)

    @classmethod
    def create_default(cls, community_id: UUID) -> LevelConfiguration:
        """Create a default configuration with standard levels."""
        return cls(
            id=uuid4(),
            community_id=community_id,
            levels=[
                LevelDefinition(level=ld.level, name=ld.name, threshold=ld.threshold)
                for ld in DEFAULT_LEVELS
            ],
        )

    def get_level_for_points(self, points: int) -> int:
        """Return the level number for a given point total."""
        current_level = 1
        for ld in self.levels:
            if points >= ld.threshold:
                current_level = ld.level
        return current_level

    def threshold_for_level(self, level: int) -> int:
        """Return the point threshold for a given level number."""
        for ld in self.levels:
            if ld.level == level:
                return ld.threshold
        raise ValueError(f"Invalid level: {level}")

    def name_for_level(self, level: int) -> str:
        """Return the name for a given level number."""
        for ld in self.levels:
            if ld.level == level:
                return ld.name
        raise ValueError(f"Invalid level: {level}")

    def points_to_next_level(self, current_level: int, total_points: int) -> int | None:
        """Return points needed to reach the next level, or None if max."""
        if current_level >= 9:
            return None
        next_threshold = self.threshold_for_level(current_level + 1)
        return max(0, next_threshold - total_points)
