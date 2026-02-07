"""Lesson entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.classroom.domain.value_objects.content_type import ContentType
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.lesson_title import LessonTitle
from src.classroom.domain.value_objects.text_content import TextContent
from src.classroom.domain.value_objects.video_url import VideoUrl


@dataclass
class Lesson:
    """Lesson entity within a Module.

    Represents a single learning unit with either text or video content.
    """

    id: LessonId
    title: LessonTitle
    content_type: ContentType
    content: str
    position: int
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        title: LessonTitle,
        content_type: ContentType,
        content: str,
        position: int,
    ) -> "Lesson":
        """Factory method to create a new lesson."""
        # Validate content based on type
        validated_content = cls._validate_content(content_type, content)

        return cls(
            id=LessonId(value=uuid4()),
            title=title,
            content_type=content_type,
            content=validated_content,
            position=position,
        )

    def update(
        self,
        title: LessonTitle | None = None,
        content_type: ContentType | None = None,
        content: str | None = None,
    ) -> list[str]:
        """Update lesson details. Returns list of changed field names."""
        changed_fields: list[str] = []

        if title is not None and title != self.title:
            self.title = title
            changed_fields.append("title")

        # Handle content type and content together
        new_content_type = content_type if content_type is not None else self.content_type
        if content is not None:
            validated_content = self._validate_content(new_content_type, content)
            if validated_content != self.content:
                self.content = validated_content
                changed_fields.append("content")

        if content_type is not None and content_type != self.content_type:
            self.content_type = content_type
            changed_fields.append("content_type")

        if changed_fields:
            self._update_timestamp()

        return changed_fields

    def delete(self) -> None:
        """Soft delete the lesson."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self._update_timestamp()

    @staticmethod
    def _validate_content(content_type: ContentType, content: str) -> str:
        """Validate content based on content type. Returns the validated content string."""
        if content_type == ContentType.TEXT:
            text_content = TextContent(content)
            return text_content.value
        else:
            video_url = VideoUrl(content)
            return video_url.value

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Lessons are equal if they have the same ID."""
        if not isinstance(other, Lesson):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on lesson ID."""
        return hash(self.id)
