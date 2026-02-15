"""LevelNumber value object."""

from dataclasses import dataclass

from src.gamification.domain.exceptions import InvalidLevelNumberError
from src.shared.domain.base_value_object import BaseValueObject


@dataclass(frozen=True)
class LevelNumber(BaseValueObject):
    """Level number (1-9)."""

    value: int

    def _validate(self) -> None:
        if not isinstance(self.value, int) or self.value < 1 or self.value > 9:
            raise InvalidLevelNumberError(self.value)
