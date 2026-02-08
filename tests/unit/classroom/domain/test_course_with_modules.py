"""Unit tests for Course aggregate with Module and Lesson operations."""

from uuid import uuid4

import pytest

from src.classroom.domain.entities.course import Course
from src.classroom.domain.exceptions import (
    CourseAlreadyDeletedError,
    InvalidPositionError,
    ModuleNotFoundError,
)
from src.classroom.domain.value_objects import (
    ContentType,
    CourseTitle,
    LessonTitle,
    ModuleDescription,
    ModuleTitle,
)
from src.identity.domain.value_objects import UserId


def _create_course(title: str = "Test Course") -> Course:
    """Helper to create a course."""
    return Course.create(
        instructor_id=UserId(value=uuid4()),
        title=CourseTitle(title),
    )


class TestCourseAddModule:
    """Tests for Course.add_module()."""

    def test_add_module(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("Getting Started"))
        assert module.title.value == "Getting Started"
        assert module.position == 1
        assert course.module_count == 1

    def test_add_module_with_description(self) -> None:
        course = _create_course()
        module = course.add_module(
            ModuleTitle("Intro"),
            description=ModuleDescription("Learn basics"),
        )
        assert module.description is not None
        assert module.description.value == "Learn basics"

    def test_add_multiple_modules_sequential_positions(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        m2 = course.add_module(ModuleTitle("M2"))
        m3 = course.add_module(ModuleTitle("M3"))
        assert m1.position == 1
        assert m2.position == 2
        assert m3.position == 3
        assert course.module_count == 3

    def test_add_module_to_deleted_course_raises(self) -> None:
        course = _create_course()
        course.delete(deleter_id=UserId(value=uuid4()))
        with pytest.raises(CourseAlreadyDeletedError):
            course.add_module(ModuleTitle("New Module"))


class TestCourseRemoveModule:
    """Tests for Course.remove_module()."""

    def test_remove_module(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("M1"))
        course.remove_module(module.id)
        assert course.module_count == 0
        assert module.is_deleted is True

    def test_remove_module_repositions(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        m2 = course.add_module(ModuleTitle("M2"))
        m3 = course.add_module(ModuleTitle("M3"))

        course.remove_module(m2.id)

        active = course.modules
        assert len(active) == 2
        assert active[0].id == m1.id
        assert active[0].position == 1
        assert active[1].id == m3.id
        assert active[1].position == 2

    def test_remove_nonexistent_raises(self) -> None:
        from src.classroom.domain.value_objects import ModuleId

        course = _create_course()
        with pytest.raises(ModuleNotFoundError):
            course.remove_module(ModuleId(uuid4()))

    def test_remove_module_from_deleted_course_raises(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("M1"))
        course.delete(deleter_id=UserId(value=uuid4()))
        with pytest.raises(CourseAlreadyDeletedError):
            course.remove_module(module.id)


class TestCourseReorderModules:
    """Tests for Course.reorder_modules()."""

    def test_reorder_modules(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        m2 = course.add_module(ModuleTitle("M2"))
        m3 = course.add_module(ModuleTitle("M3"))

        course.reorder_modules([m3.id, m1.id, m2.id])

        modules = course.modules
        assert modules[0].id == m3.id
        assert modules[0].position == 1
        assert modules[1].id == m1.id
        assert modules[1].position == 2
        assert modules[2].id == m2.id
        assert modules[2].position == 3

    def test_reorder_duplicate_raises(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        course.add_module(ModuleTitle("M2"))

        with pytest.raises(InvalidPositionError, match="Duplicate"):
            course.reorder_modules([m1.id, m1.id])

    def test_reorder_missing_module_raises(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        course.add_module(ModuleTitle("M2"))

        with pytest.raises(InvalidPositionError, match="all active"):
            course.reorder_modules([m1.id])

    def test_reorder_on_deleted_course_raises(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        course.delete(deleter_id=UserId(value=uuid4()))
        with pytest.raises(CourseAlreadyDeletedError):
            course.reorder_modules([m1.id])


class TestCourseGetModule:
    """Tests for Course.get_module_by_id()."""

    def test_get_existing_module(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("M1"))
        found = course.get_module_by_id(module.id)
        assert found is not None
        assert found.id == module.id

    def test_get_nonexistent_module_returns_none(self) -> None:
        from src.classroom.domain.value_objects import ModuleId

        course = _create_course()
        found = course.get_module_by_id(ModuleId(uuid4()))
        assert found is None


class TestCourseModuleProperties:
    """Tests for Course module-related properties."""

    def test_modules_property_excludes_deleted(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        m2 = course.add_module(ModuleTitle("M2"))
        course.remove_module(m1.id)

        modules = course.modules
        assert len(modules) == 1
        assert modules[0].id == m2.id

    def test_modules_property_sorted_by_position(self) -> None:
        course = _create_course()
        course.add_module(ModuleTitle("M1"))
        course.add_module(ModuleTitle("M2"))

        modules = course.modules
        assert modules[0].position < modules[1].position

    def test_all_modules_includes_deleted(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        course.add_module(ModuleTitle("M2"))
        course.remove_module(m1.id)

        assert len(course.all_modules) == 2

    def test_module_count(self) -> None:
        course = _create_course()
        course.add_module(ModuleTitle("M1"))
        course.add_module(ModuleTitle("M2"))
        assert course.module_count == 2


class TestCourseLessonManagement:
    """Tests for Course lesson-related operations."""

    def test_add_lesson_to_module(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("M1"))
        lesson = course.add_lesson_to_module(
            module_id=module.id,
            title=LessonTitle("L1"),
            content_type=ContentType.TEXT,
            content="Some content",
        )
        assert lesson.title.value == "L1"
        assert lesson.position == 1
        assert module.lesson_count == 1

    def test_add_lesson_to_nonexistent_module_raises(self) -> None:
        from src.classroom.domain.value_objects import ModuleId

        course = _create_course()
        with pytest.raises(ModuleNotFoundError):
            course.add_lesson_to_module(
                module_id=ModuleId(uuid4()),
                title=LessonTitle("L1"),
                content_type=ContentType.TEXT,
                content="Content",
            )

    def test_add_lesson_to_deleted_module_raises(self) -> None:
        course = _create_course()
        module = course.add_module(ModuleTitle("M1"))
        course.remove_module(module.id)
        with pytest.raises(ModuleNotFoundError):
            course.add_lesson_to_module(
                module_id=module.id,
                title=LessonTitle("L1"),
                content_type=ContentType.TEXT,
                content="Content",
            )

    def test_lesson_count_across_modules(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        m2 = course.add_module(ModuleTitle("M2"))

        course.add_lesson_to_module(m1.id, LessonTitle("L1"), ContentType.TEXT, "C1")
        course.add_lesson_to_module(m1.id, LessonTitle("L2"), ContentType.TEXT, "C2")
        course.add_lesson_to_module(m2.id, LessonTitle("L3"), ContentType.TEXT, "C3")

        assert course.lesson_count == 3

    def test_find_module_for_lesson(self) -> None:
        course = _create_course()
        m1 = course.add_module(ModuleTitle("M1"))
        lesson = course.add_lesson_to_module(m1.id, LessonTitle("L1"), ContentType.TEXT, "Content")

        found = course.find_module_for_lesson(lesson.id)
        assert found is not None
        assert found.id == m1.id

    def test_find_module_for_nonexistent_lesson_returns_none(self) -> None:
        from src.classroom.domain.value_objects import LessonId

        course = _create_course()
        course.add_module(ModuleTitle("M1"))

        found = course.find_module_for_lesson(LessonId(uuid4()))
        assert found is None
