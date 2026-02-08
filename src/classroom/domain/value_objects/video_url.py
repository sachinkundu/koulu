"""Video URL value object."""

import re
from dataclasses import dataclass

from src.classroom.domain.exceptions import InvalidVideoUrlError, VideoUrlRequiredError

# YouTube patterns: standard, short, embed
YOUTUBE_PATTERN = re.compile(
    r"^https?://(www\.)?(youtube\.com/(watch\?v=|embed/)|youtu\.be/)[a-zA-Z0-9_-]+",
)

# Vimeo patterns: standard and player embed
VIMEO_PATTERN = re.compile(
    r"^https?://(www\.)?(vimeo\.com|player\.vimeo\.com/video)/\d+",
)

# Loom patterns
LOOM_PATTERN = re.compile(
    r"^https?://(www\.)?loom\.com/(share|embed)/[a-zA-Z0-9]+",
)


@dataclass(frozen=True)
class VideoUrl:
    """Video URL value object.

    Validates: Must be a valid YouTube, Vimeo, or Loom URL.
    """

    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        object.__setattr__(self, "value", stripped)

        if not stripped:
            raise VideoUrlRequiredError()

        if not (
            YOUTUBE_PATTERN.match(stripped)
            or VIMEO_PATTERN.match(stripped)
            or LOOM_PATTERN.match(stripped)
        ):
            raise InvalidVideoUrlError()
