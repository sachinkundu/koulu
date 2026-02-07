"""Unit tests for Course entity."""

from uuid import uuid4

import pytest

from src.classroom.domain.entities import Course
from src.classroom.domain.events import CourseCreated, CourseDeleted
from src.classroom.domain.exceptions import CourseAlreadyDeletedError
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)
from src.identity.domain.value_objects import UserId


class TestCourseCreate:
    """Tests for Course.create() factory method."""

    def test_create_with_required_fields_only(self) -> None:
        """Course can be created with just title."""
        instructor_id = UserId(value=uuid4())
        title = CourseTitle("Introduction to Python")

        course = Course.create(instructor_id=instructor_id, title=title)

        assert course.instructor_id == instructor_id
        assert course.title == title
        assert course.description is None
        assert course.cover_image_url is None
        assert course.estimated_duration is None
        assert course.is_deleted is False
        assert course.deleted_at is None

    def test_create_with_all_fields(self) -> None:
        """Course can be created with all optional fields."""
        instructor_id = UserId(value=uuid4())
        title = CourseTitle("Advanced Web Dev")
        description = CourseDescription("Learn React and TypeScript")
        cover_image_url = CoverImageUrl("https://example.com/cover.jpg")
        estimated_duration = EstimatedDuration("8 hours")

        course = Course.create(
            instructor_id=instructor_id,
            title=title,
            description=description,
            cover_image_url=cover_image_url,
            estimated_duration=estimated_duration,
        )

        assert course.title == title
        assert course.description == description
        assert course.cover_image_url == cover_image_url
        assert course.estimated_duration == estimated_duration

    def test_create_publishes_course_created_event(self) -> None:
        """Creating a course publishes a CourseCreated event."""
        instructor_id = UserId(value=uuid4())
        title = CourseTitle("Test Course")

        course = Course.create(instructor_id=instructor_id, title=title)

        events = course.events
        assert len(events) == 1
        assert isinstance(events[0], CourseCreated)
        assert events[0].course_id == course.id
        assert events[0].instructor_id == instructor_id
        assert events[0].title == "Test Course"

    def test_create_generates_unique_id(self) -> None:
        """Each course gets a unique ID."""
        instructor_id = UserId(value=uuid4())
        course1 = Course.create(instructor_id=instructor_id, title=CourseTitle("Course 1"))
        course2 = Course.create(instructor_id=instructor_id, title=CourseTitle("Course 2"))

        assert course1.id != course2.id


class TestCourseUpdate:
    """Tests for Course.update()."""

    def _create_course(self) -> Course:
        """Helper to create a test course."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("Original Title"),
            description=CourseDescription("Original description"),
        )
        course.clear_events()  # Clear creation event
        return course

    def test_update_title(self) -> None:
        """Title can be updated."""
        course = self._create_course()
        new_title = CourseTitle("New Title")

        changed = course.update(title=new_title)

        assert "title" in changed
        assert course.title == new_title

    def test_update_description(self) -> None:
        """Description can be updated."""
        course = self._create_course()
        new_desc = CourseDescription("New description")

        changed = course.update(description=new_desc)

        assert "description" in changed
        assert course.description == new_desc

    def test_update_no_changes_returns_empty(self) -> None:
        """No changes returns empty list."""
        course = self._create_course()

        changed = course.update(title=CourseTitle("Original Title"))

        assert changed == []

    def test_update_deleted_course_raises(self) -> None:
        """Cannot update a deleted course."""
        course = self._create_course()
        course.delete(UserId(value=uuid4()))

        with pytest.raises(CourseAlreadyDeletedError):
            course.update(title=CourseTitle("New Title"))

    def test_update_multiple_fields(self) -> None:
        """Multiple fields can be updated at once."""
        course = self._create_course()
        new_title = CourseTitle("Updated Title")
        new_desc = CourseDescription("Updated desc")
        new_url = CoverImageUrl("https://example.com/new.jpg")

        changed = course.update(
            title=new_title,
            description=new_desc,
            cover_image_url=new_url,
        )

        assert "title" in changed
        assert "description" in changed
        assert "cover_image_url" in changed


class TestCourseDelete:
    """Tests for Course.delete()."""

    def test_soft_delete(self) -> None:
        """Course can be soft deleted."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("To Delete"),
        )
        course.clear_events()
        deleter_id = UserId(value=uuid4())

        course.delete(deleter_id)

        assert course.is_deleted is True
        assert course.deleted_at is not None

    def test_delete_publishes_event(self) -> None:
        """Deleting publishes CourseDeleted event."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("To Delete"),
        )
        course.clear_events()
        deleter_id = UserId(value=uuid4())

        course.delete(deleter_id)

        events = course.events
        assert len(events) == 1
        assert isinstance(events[0], CourseDeleted)
        assert events[0].course_id == course.id
        assert events[0].deleted_by == deleter_id

    def test_delete_already_deleted_raises(self) -> None:
        """Cannot delete an already deleted course."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("Already Deleted"),
        )
        course.delete(UserId(value=uuid4()))

        with pytest.raises(CourseAlreadyDeletedError):
            course.delete(UserId(value=uuid4()))


class TestCourseEquality:
    """Tests for Course equality and hashing."""

    def test_courses_equal_by_id(self) -> None:
        """Two courses with the same ID are equal."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("Test"),
        )
        # Same course entity should equal itself
        assert course == course

    def test_courses_not_equal_to_other_types(self) -> None:
        """Course is not equal to non-Course objects."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("Test"),
        )
        assert course != "not a course"

    def test_clear_events(self) -> None:
        """clear_events returns and clears events."""
        course = Course.create(
            instructor_id=UserId(value=uuid4()),
            title=CourseTitle("Test"),
        )
        events = course.clear_events()

        assert len(events) == 1
        assert len(course.events) == 0
