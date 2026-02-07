"""CourseTitle value object."""

from dataclasses import dataclass

import bleach

MIN_TITLE_LENGTH = 2
MAX_TITLE_LENGTH = 200


@dataclass(frozen=True)
class CourseTitle:
    """
    Course title value object.

    Validates:
    - Length: 2-200 characters
    - Strips HTML tags for security
    - Normalizes whitespace
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and sanitize the title."""
        from src.classroom.domain.exceptions import (
            CourseTitleRequiredError,
            CourseTitleTooLongError,
            CourseTitleTooShortError,
        )

        # Sanitize HTML - strip all tags
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise CourseTitleRequiredError()

        if len(sanitized) < MIN_TITLE_LENGTH:
            raise CourseTitleTooShortError(MIN_TITLE_LENGTH)

        if len(sanitized) > MAX_TITLE_LENGTH:
            raise CourseTitleTooLongError(MAX_TITLE_LENGTH)

    def __str__(self) -> str:
        """Return the title string."""
        return self.value
