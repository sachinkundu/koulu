"""PostTitle value object."""

from dataclasses import dataclass

import bleach

MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 200


@dataclass(frozen=True)
class PostTitle:
    """
    Post title value object.

    Validates:
    - Length: 1-200 characters
    - Strips HTML tags for security
    - Normalizes whitespace
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and sanitize the title."""
        from src.community.domain.exceptions import PostTitleRequiredError, PostTitleTooLongError

        # Sanitize HTML - strip all tags
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise PostTitleRequiredError()

        if len(sanitized) > MAX_TITLE_LENGTH:
            raise PostTitleTooLongError(MAX_TITLE_LENGTH)

    def __str__(self) -> str:
        """Return the title string."""
        return self.value
