"""Module description value object."""

from dataclasses import dataclass

import bleach

from src.classroom.domain.exceptions import ModuleDescriptionTooLongError

MAX_DESCRIPTION_LENGTH = 1000


@dataclass(frozen=True)
class ModuleDescription:
    """Module description value object.

    Validates: Max 1000 chars, strips HTML, normalizes whitespace.
    """

    value: str

    def __post_init__(self) -> None:
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if len(sanitized) > MAX_DESCRIPTION_LENGTH:
            raise ModuleDescriptionTooLongError(MAX_DESCRIPTION_LENGTH)
