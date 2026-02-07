"""PostContent value object."""

from dataclasses import dataclass

import bleach

MIN_CONTENT_LENGTH = 1
MAX_CONTENT_LENGTH = 5000


@dataclass(frozen=True)
class PostContent:
    """
    Post content value object.

    Validates:
    - Length: 1-5000 characters
    - Strips HTML tags for security (plain text only in MVP)
    - Normalizes whitespace
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and sanitize the content."""
        from src.community.domain.exceptions import (
            PostContentRequiredError,
            PostContentTooLongError,
        )

        # Sanitize HTML - strip all tags (plain text only for MVP)
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise PostContentRequiredError()

        if len(sanitized) > MAX_CONTENT_LENGTH:
            raise PostContentTooLongError(MAX_CONTENT_LENGTH)

    def __str__(self) -> str:
        """Return the content string."""
        return self.value
