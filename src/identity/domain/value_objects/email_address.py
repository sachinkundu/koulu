"""EmailAddress value object."""

import re
from dataclasses import dataclass

from src.identity.domain.exceptions import InvalidEmailError

# RFC 5322 simplified regex for email validation
# This covers most common email formats without being overly strict
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

MAX_EMAIL_LENGTH = 254


@dataclass(frozen=True)
class EmailAddress:
    """
    Email address value object.

    Validates:
    - RFC 5322 format (simplified)
    - Maximum 254 characters
    - Stores as lowercase
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the email address."""
        # Use object.__setattr__ because dataclass is frozen
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)

        if not normalized:
            raise InvalidEmailError(self.value)

        if len(normalized) > MAX_EMAIL_LENGTH:
            raise InvalidEmailError(self.value)

        if not EMAIL_REGEX.match(normalized):
            raise InvalidEmailError(self.value)

    def __str__(self) -> str:
        """Return the email address string."""
        return self.value

    @property
    def local_part(self) -> str:
        """Get the local part (before @) of the email."""
        return self.value.split("@")[0]

    @property
    def domain(self) -> str:
        """Get the domain part (after @) of the email."""
        return self.value.split("@")[1]
