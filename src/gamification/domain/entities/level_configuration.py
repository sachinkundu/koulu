"""LevelConfiguration aggregate root."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.gamification.domain.exceptions import InvalidLevelNameError, InvalidThresholdError
from src.shared.domain.base_entity import BaseEntity

MAX_LEVEL_NAME_LENGTH = 30
_HTML_TAG_RE = re.compile(r"<[^>]+>")


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

    def update_levels(self, new_levels: list[LevelDefinition]) -> None:
        """
        Update the level definitions.

        Validates:
        - Exactly 9 levels
        - Level 1 threshold must be 0
        - Thresholds strictly increasing
        - Names 1-30 chars, non-empty after sanitization
        - Unique names (case-sensitive)
        - No HTML tags (stripped)

        Raises:
            InvalidLevelNameError: If a level name is invalid.
            InvalidThresholdError: If thresholds are invalid.
        """
        if len(new_levels) != 9:
            raise InvalidThresholdError(f"Exactly 9 levels required, got {len(new_levels)}")

        # Sanitize names and validate
        sanitized_levels: list[LevelDefinition] = []
        seen_names: set[str] = set()

        for ld in sorted(new_levels, key=lambda x: x.level):
            # Strip HTML tags and whitespace
            sanitized_name = _HTML_TAG_RE.sub("", ld.name).strip()

            if not sanitized_name:
                raise InvalidLevelNameError("Level name is required")

            if len(sanitized_name) > MAX_LEVEL_NAME_LENGTH:
                raise InvalidLevelNameError(
                    f"Level name must be {MAX_LEVEL_NAME_LENGTH} characters or less"
                )

            if sanitized_name in seen_names:
                raise InvalidLevelNameError(f"Duplicate level name: {sanitized_name}")
            seen_names.add(sanitized_name)

            sanitized_levels.append(
                LevelDefinition(level=ld.level, name=sanitized_name, threshold=ld.threshold)
            )

        # Validate thresholds
        if sanitized_levels[0].threshold != 0:
            raise InvalidThresholdError("Level 1 threshold must be 0")

        for i in range(1, len(sanitized_levels)):
            if sanitized_levels[i].threshold <= sanitized_levels[i - 1].threshold:
                raise InvalidThresholdError(
                    f"Thresholds must be strictly increasing: "
                    f"level {sanitized_levels[i].level} threshold ({sanitized_levels[i].threshold}) "
                    f"must be greater than level {sanitized_levels[i - 1].level} "
                    f"threshold ({sanitized_levels[i - 1].threshold})"
                )

        self.levels = sanitized_levels
        self._update_timestamp()
