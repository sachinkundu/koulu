"""Content type value object."""

from enum import Enum

from src.classroom.domain.exceptions import InvalidContentTypeError


class ContentType(Enum):
    """Supported lesson content types."""

    TEXT = "text"
    VIDEO = "video"

    @classmethod
    def from_string(cls, value: str) -> "ContentType":
        """Create ContentType from string, raising domain error if invalid."""
        try:
            return cls(value.lower())
        except ValueError:
            raise InvalidContentTypeError(value) from None
