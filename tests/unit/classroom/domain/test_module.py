"""Unit tests for Module entity."""

import pytest

from src.classroom.domain.entities.module import Module
from src.classroom.domain.exceptions import (
    InvalidPositionError,
    LessonNotFoundError,
)
from src.classroom.domain.value_objects import (
    ContentType,
    LessonId,
    LessonTitle,
    ModuleDescription,
    ModuleTitle,
)


def _create_module(
    title: str = "Getting Started",
    description: str | None = None,
    position: int = 1,
) -> Module:
    """Helper to create a module."""
    return Module.create(
        title=ModuleTitle(title),
        description=ModuleDescription(description) if description else None,
        position=position,
    )


class TestModuleCreate:
    """Tests for Module.create() factory."""

    def test_create_with_title(self) -> None:
        module = _create_module("Getting Started")
        assert module.title.value == "Getting Started"
        assert module.description is None
        assert module.position == 1
        assert module.is_deleted is False
        assert module.deleted_at is None

    def test_create_with_description(self) -> None:
        module = _create_module("Intro", description="Learn basics")
        assert module.description is not None
        assert module.description.value == "Learn basics"

    def test_create_generates_unique_ids(self) -> None:
        m1 = _create_module("Module 1")
        m2 = _create_module("Module 2")
        assert m1.id != m2.id

    def test_create_sets_timestamps(self) -> None:
        module = _create_module()
        assert module.created_at is not None
        assert module.updated_at is not None


class TestModuleUpdate:
    """Tests for Module.update()."""

    def test_update_title(self) -> None:
        module = _create_module("Old Title")
        changed = module.update(title=ModuleTitle("New Title"))
        assert "title" in changed
        assert module.title.value == "New Title"

    def test_update_description(self) -> None:
        module = _create_module()
        changed = module.update(description=ModuleDescription("New desc"))
        assert "description" in changed
        assert module.description is not None

    def test_no_changes_returns_empty(self) -> None:
        module = _create_module("Title")
        changed = module.update(title=ModuleTitle("Title"))
        assert changed == []

    def test_update_updates_timestamp(self) -> None:
        module = _create_module()
        old_updated = module.updated_at
        module.update(title=ModuleTitle("New Title"))
        assert module.updated_at >= old_updated


class TestModuleDelete:
    """Tests for Module.delete()."""

    def test_soft_delete(self) -> None:
        module = _create_module()
        module.delete()
        assert module.is_deleted is True
        assert module.deleted_at is not None

    def test_delete_cascades_to_lessons(self) -> None:
        module = _create_module()
        module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "Content 1")
        module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "Content 2")

        module.delete()

        for lesson in module.all_lessons:
            assert lesson.is_deleted is True


class TestModuleLessons:
    """Tests for Module lesson management."""

    def test_add_lesson(self) -> None:
        module = _create_module()
        lesson = module.add_lesson(
            LessonTitle("What is Python?"),
            ContentType.TEXT,
            "Python is a programming language.",
        )
        assert lesson.title.value == "What is Python?"
        assert lesson.position == 1
        assert module.lesson_count == 1

    def test_add_multiple_lessons_sequential_positions(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "Content 1")
        l2 = module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "Content 2")
        l3 = module.add_lesson(LessonTitle("L3"), ContentType.TEXT, "Content 3")
        assert l1.position == 1
        assert l2.position == 2
        assert l3.position == 3
        assert module.lesson_count == 3

    def test_get_lesson_by_id(self) -> None:
        module = _create_module()
        lesson = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "Content")
        found = module.get_lesson_by_id(lesson.id)
        assert found is not None
        assert found.id == lesson.id

    def test_get_lesson_by_id_not_found(self) -> None:
        module = _create_module()
        from uuid import uuid4

        found = module.get_lesson_by_id(LessonId(uuid4()))
        assert found is None

    def test_remove_lesson(self) -> None:
        module = _create_module()
        lesson = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "Content")
        module.remove_lesson(lesson.id)
        assert module.lesson_count == 0
        assert lesson.is_deleted is True

    def test_remove_lesson_not_found_raises(self) -> None:
        module = _create_module()
        from uuid import uuid4

        with pytest.raises(LessonNotFoundError):
            module.remove_lesson(LessonId(uuid4()))

    def test_remove_lesson_repositions(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        l2 = module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")
        l3 = module.add_lesson(LessonTitle("L3"), ContentType.TEXT, "C3")

        module.remove_lesson(l2.id)

        active = module.lessons
        assert len(active) == 2
        assert active[0].id == l1.id
        assert active[0].position == 1
        assert active[1].id == l3.id
        assert active[1].position == 2

    def test_lessons_property_excludes_deleted(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        l2 = module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")
        module.remove_lesson(l1.id)

        lessons = module.lessons
        assert len(lessons) == 1
        assert lessons[0].id == l2.id

    def test_lessons_property_sorted_by_position(self) -> None:
        module = _create_module()
        module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")

        lessons = module.lessons
        assert lessons[0].position < lessons[1].position


class TestModuleReorderLessons:
    """Tests for Module.reorder_lessons()."""

    def test_reorder_lessons(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        l2 = module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")
        l3 = module.add_lesson(LessonTitle("L3"), ContentType.TEXT, "C3")

        module.reorder_lessons([l3.id, l1.id, l2.id])

        lessons = module.lessons
        assert lessons[0].id == l3.id
        assert lessons[0].position == 1
        assert lessons[1].id == l1.id
        assert lessons[1].position == 2
        assert lessons[2].id == l2.id
        assert lessons[2].position == 3

    def test_reorder_duplicate_raises(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")

        with pytest.raises(InvalidPositionError, match="Duplicate"):
            module.reorder_lessons([l1.id, l1.id])

    def test_reorder_missing_lesson_raises(self) -> None:
        module = _create_module()
        l1 = module.add_lesson(LessonTitle("L1"), ContentType.TEXT, "C1")
        module.add_lesson(LessonTitle("L2"), ContentType.TEXT, "C2")

        with pytest.raises(InvalidPositionError, match="all active"):
            module.reorder_lessons([l1.id])


class TestModuleEquality:
    """Tests for Module equality."""

    def test_equal_by_id(self) -> None:
        m1 = _create_module("Module AA")
        m2 = Module(
            id=m1.id,
            title=ModuleTitle("Module BB"),
            description=None,
            position=1,
        )
        assert m1 == m2

    def test_not_equal_different_id(self) -> None:
        m1 = _create_module("Module AA")
        m2 = _create_module("Module AA")
        assert m1 != m2

    def test_hash_by_id(self) -> None:
        m1 = _create_module()
        assert hash(m1) == hash(m1.id)
