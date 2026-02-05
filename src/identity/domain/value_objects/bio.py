"""Bio value object."""

from dataclasses import dataclass

import bleach

from src.identity.domain.exceptions import InvalidBioError

MAX_LENGTH = 500


@dataclass(frozen=True)
class Bio:
    """
    User bio value object.

    Short self-description text with HTML sanitization for XSS prevention.

    Validates:
    - Max 500 characters
    - Sanitizes HTML/script tags (security)
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and sanitize the bio."""
        # Sanitize HTML tags (XSS prevention)
        # First, remove dangerous tags (script, style) entirely including their content
        # Then strip remaining tags but keep their text content
        import re

        text = self.value
        # Remove script and style tags with their content
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)

        # Now use bleach to strip all remaining HTML tags (but keep their content)
        sanitized = bleach.clean(text, tags=[], strip=True)
        object.__setattr__(self, "value", sanitized)

        # Validate length
        if len(sanitized) > MAX_LENGTH:
            raise InvalidBioError(f"Bio must be at most {MAX_LENGTH} characters")

    def __str__(self) -> str:
        """Return the bio string."""
        return self.value
