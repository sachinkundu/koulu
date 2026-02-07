"""CoverImageUrl value object."""

import re
from dataclasses import dataclass

# Simple HTTPS URL pattern
HTTPS_URL_PATTERN = re.compile(r"^https://[^\s]+$")


@dataclass(frozen=True)
class CoverImageUrl:
    """
    Cover image URL value object.

    Validates:
    - Must be a valid HTTPS URL
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the URL."""
        from src.classroom.domain.exceptions import InvalidCoverImageUrlError

        stripped = self.value.strip()
        object.__setattr__(self, "value", stripped)

        if not HTTPS_URL_PATTERN.match(stripped):
            raise InvalidCoverImageUrlError()

    def __str__(self) -> str:
        """Return the URL string."""
        return self.value
