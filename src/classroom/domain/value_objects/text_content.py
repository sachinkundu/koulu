"""Text content value object."""

from dataclasses import dataclass

import bleach

from src.classroom.domain.exceptions import TextContentRequiredError, TextContentTooLongError

MAX_CONTENT_LENGTH = 50000

# Allowed HTML tags for rich text content
ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "s",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "blockquote",
    "code",
    "pre",
    "img",
    "hr",
    "span",
    "div",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "span": ["class"],
    "div": ["class"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}


@dataclass(frozen=True)
class TextContent:
    """Text content value object.

    Validates: 1-50,000 chars, sanitizes HTML with allowed tags.
    """

    value: str

    def __post_init__(self) -> None:
        sanitized = bleach.clean(
            self.value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
        ).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise TextContentRequiredError()
        if len(sanitized) > MAX_CONTENT_LENGTH:
            raise TextContentTooLongError(MAX_CONTENT_LENGTH)
