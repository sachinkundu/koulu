"""Lesson title value object."""

from dataclasses import dataclass

import bleach

from src.classroom.domain.exceptions import (
    LessonTitleRequiredError,
    LessonTitleTooLongError,
    LessonTitleTooShortError,
)

MIN_TITLE_LENGTH = 2
MAX_TITLE_LENGTH = 200


@dataclass(frozen=True)
class LessonTitle:
    """Lesson title value object.

    Validates: Length 2-200 chars, strips HTML tags, normalizes whitespace.
    """

    value: str

    def __post_init__(self) -> None:
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise LessonTitleRequiredError()
        if len(sanitized) < MIN_TITLE_LENGTH:
            raise LessonTitleTooShortError(MIN_TITLE_LENGTH)
        if len(sanitized) > MAX_TITLE_LENGTH:
            raise LessonTitleTooLongError(MAX_TITLE_LENGTH)
