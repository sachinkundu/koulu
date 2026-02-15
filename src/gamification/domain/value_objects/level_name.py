"""LevelName value object."""

from dataclasses import dataclass

import bleach

from src.gamification.domain.exceptions import InvalidLevelNameError
from src.shared.domain.base_value_object import BaseValueObject

MAX_LEVEL_NAME_LENGTH = 30


@dataclass(frozen=True)
class LevelName(BaseValueObject):
    """Level name (1-30 chars, sanitized)."""

    value: str

    def _validate(self) -> None:
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise InvalidLevelNameError("Level name is required")

        if len(sanitized) > MAX_LEVEL_NAME_LENGTH:
            raise InvalidLevelNameError(
                f"Level name must be {MAX_LEVEL_NAME_LENGTH} characters or less"
            )
