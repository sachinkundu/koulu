"""DisplayName value object."""

import re
from dataclasses import dataclass

from src.identity.domain.exceptions import InvalidDisplayNameError

MIN_LENGTH = 2
MAX_LENGTH = 50

# No HTML tags allowed
HTML_TAG_REGEX = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class DisplayName:
    """
    User display name value object.

    Validates:
    - Length: 2-50 characters
    - No HTML tags
    - Trimmed whitespace
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the display name."""
        # Trim whitespace
        trimmed = self.value.strip()
        object.__setattr__(self, "value", trimmed)

        if len(trimmed) < MIN_LENGTH:
            raise InvalidDisplayNameError(f"Display name must be at least {MIN_LENGTH} characters")

        if len(trimmed) > MAX_LENGTH:
            raise InvalidDisplayNameError(f"Display name must be at most {MAX_LENGTH} characters")

        if HTML_TAG_REGEX.search(trimmed):
            raise InvalidDisplayNameError("Display name cannot contain HTML tags")

    def __str__(self) -> str:
        """Return the display name string."""
        return self.value

    @property
    def initials(self) -> str:
        """
        Get initials from the display name.

        Takes the first letter of each word (up to 2 letters).
        Example: "John Doe" -> "JD", "Alice" -> "A"
        """
        words = self.value.split()
        if len(words) >= 2:
            return (words[0][0] + words[1][0]).upper()
        return self.value[0].upper()
