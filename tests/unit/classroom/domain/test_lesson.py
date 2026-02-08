"""Unit tests for Lesson entity."""

import pytest

from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.exceptions import (
    InvalidVideoUrlError,
    TextContentRequiredError,
)
from src.classroom.domain.value_objects import (
    ContentType,
    LessonTitle,
)


def _create_text_lesson(
    title: str = "What is Python?",
    content: str = "Python is a programming language.",
    position: int = 1,
) -> Lesson:
    """Helper to create a text lesson."""
    return Lesson.create(
        title=LessonTitle(title),
        content_type=ContentType.TEXT,
        content=content,
        position=position,
    )


def _create_video_lesson(
    title: str = "Intro Video",
    content: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    position: int = 1,
) -> Lesson:
    """Helper to create a video lesson."""
    return Lesson.create(
        title=LessonTitle(title),
        content_type=ContentType.VIDEO,
        content=content,
        position=position,
    )


class TestLessonCreate:
    """Tests for Lesson.create() factory."""

    def test_create_text_lesson(self) -> None:
        lesson = _create_text_lesson()
        assert lesson.title.value == "What is Python?"
        assert lesson.content_type == ContentType.TEXT
        assert lesson.content == "Python is a programming language."
        assert lesson.position == 1
        assert lesson.is_deleted is False
        assert lesson.deleted_at is None

    def test_create_video_lesson(self) -> None:
        lesson = _create_video_lesson()
        assert lesson.title.value == "Intro Video"
        assert lesson.content_type == ContentType.VIDEO
        assert "youtube.com" in lesson.content

    def test_create_generates_unique_ids(self) -> None:
        l1 = _create_text_lesson("Lesson 1")
        l2 = _create_text_lesson("Lesson 2")
        assert l1.id != l2.id

    def test_create_sets_timestamps(self) -> None:
        lesson = _create_text_lesson()
        assert lesson.created_at is not None
        assert lesson.updated_at is not None

    def test_create_validates_text_content(self) -> None:
        with pytest.raises(TextContentRequiredError):
            Lesson.create(
                title=LessonTitle("Test"),
                content_type=ContentType.TEXT,
                content="",
                position=1,
            )

    def test_create_validates_video_url(self) -> None:
        with pytest.raises(InvalidVideoUrlError):
            Lesson.create(
                title=LessonTitle("Test"),
                content_type=ContentType.VIDEO,
                content="not-a-url",
                position=1,
            )


class TestLessonUpdate:
    """Tests for Lesson.update()."""

    def test_update_title(self) -> None:
        lesson = _create_text_lesson("Old Title")
        changed = lesson.update(title=LessonTitle("New Title"))
        assert "title" in changed
        assert lesson.title.value == "New Title"

    def test_update_content(self) -> None:
        lesson = _create_text_lesson()
        changed = lesson.update(content="Updated content here")
        assert "content" in changed
        assert lesson.content == "Updated content here"

    def test_update_content_type_and_content(self) -> None:
        lesson = _create_text_lesson()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        changed = lesson.update(content_type=ContentType.VIDEO, content=url)
        assert "content_type" in changed
        assert "content" in changed
        assert lesson.content_type == ContentType.VIDEO

    def test_no_changes_returns_empty(self) -> None:
        lesson = _create_text_lesson("Title")
        changed = lesson.update(title=LessonTitle("Title"))
        assert changed == []

    def test_update_updates_timestamp(self) -> None:
        lesson = _create_text_lesson()
        old_updated = lesson.updated_at
        lesson.update(title=LessonTitle("New Title"))
        assert lesson.updated_at >= old_updated


class TestLessonDelete:
    """Tests for Lesson.delete()."""

    def test_soft_delete(self) -> None:
        lesson = _create_text_lesson()
        lesson.delete()
        assert lesson.is_deleted is True
        assert lesson.deleted_at is not None

    def test_delete_updates_timestamp(self) -> None:
        lesson = _create_text_lesson()
        old_updated = lesson.updated_at
        lesson.delete()
        assert lesson.updated_at >= old_updated


class TestLessonEquality:
    """Tests for Lesson equality."""

    def test_equal_by_id(self) -> None:
        l1 = _create_text_lesson("Lesson AA")
        l2 = Lesson(
            id=l1.id,
            title=LessonTitle("Lesson BB"),
            content_type=ContentType.TEXT,
            content="Other content",
            position=2,
        )
        assert l1 == l2

    def test_not_equal_different_id(self) -> None:
        l1 = _create_text_lesson("Lesson AA")
        l2 = _create_text_lesson("Lesson AA")
        assert l1 != l2

    def test_hash_by_id(self) -> None:
        lesson = _create_text_lesson()
        assert hash(lesson) == hash(lesson.id)
