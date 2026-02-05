"""Location value object."""

import re
from dataclasses import dataclass

from src.identity.domain.exceptions import InvalidLocationError

MIN_LENGTH = 2
MAX_LENGTH = 100

# No HTML tags allowed
HTML_TAG_REGEX = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class Location:
    """
    User location value object.

    Represents a geographic location with city and country.
    Both fields must be provided together (no partial location).

    Validates:
    - Both city and country present (or both absent)
    - Length: 2-100 characters each
    - No HTML tags
    """

    city: str
    country: str

    def __post_init__(self) -> None:
        """Validate the location."""
        # Trim whitespace
        trimmed_city = self.city.strip()
        trimmed_country = self.country.strip()
        object.__setattr__(self, "city", trimmed_city)
        object.__setattr__(self, "country", trimmed_country)

        # Validate city
        if len(trimmed_city) < MIN_LENGTH:
            raise InvalidLocationError(f"City must be at least {MIN_LENGTH} characters")

        if len(trimmed_city) > MAX_LENGTH:
            raise InvalidLocationError(f"City must be at most {MAX_LENGTH} characters")

        if HTML_TAG_REGEX.search(trimmed_city):
            raise InvalidLocationError("City cannot contain HTML tags")

        # Validate country
        if len(trimmed_country) < MIN_LENGTH:
            raise InvalidLocationError(f"Country must be at least {MIN_LENGTH} characters")

        if len(trimmed_country) > MAX_LENGTH:
            raise InvalidLocationError(f"Country must be at most {MAX_LENGTH} characters")

        if HTML_TAG_REGEX.search(trimmed_country):
            raise InvalidLocationError("Country cannot contain HTML tags")

    def format(self) -> str:
        """Return formatted location string: 'City, Country'."""
        return f"{self.city}, {self.country}"

    def __str__(self) -> str:
        """Return the formatted location string."""
        return self.format()
