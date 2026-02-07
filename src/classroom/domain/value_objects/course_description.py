"""CourseDescription value object."""

from dataclasses import dataclass

import bleach

MAX_DESCRIPTION_LENGTH = 2000


@dataclass(frozen=True)
class CourseDescription:
    """
    Course description value object.

    Validates:
    - Maximum 2000 characters
    - Strips HTML tags for security
    - Normalizes whitespace
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and sanitize the description."""
        from src.classroom.domain.exceptions import CourseDescriptionTooLongError

        # Sanitize HTML - strip all tags
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if len(sanitized) > MAX_DESCRIPTION_LENGTH:
            raise CourseDescriptionTooLongError(MAX_DESCRIPTION_LENGTH)

    def __str__(self) -> str:
        """Return the description string."""
        return self.value
