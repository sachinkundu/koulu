"""Classroom domain exceptions."""


class ClassroomDomainError(Exception):
    """Base exception for all classroom domain errors."""

    pass


# Course validation errors
class CourseTitleRequiredError(ClassroomDomainError):
    """Raised when course title is empty."""

    def __init__(self) -> None:
        super().__init__("Title is required")


class CourseTitleTooShortError(ClassroomDomainError):
    """Raised when course title is too short."""

    def __init__(self, min_length: int) -> None:
        super().__init__(f"Title must be at least {min_length} characters")


class CourseTitleTooLongError(ClassroomDomainError):
    """Raised when course title exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Title must be {max_length} characters or less")


class CourseDescriptionTooLongError(ClassroomDomainError):
    """Raised when course description exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Description must be {max_length} characters or less")


class InvalidCoverImageUrlError(ClassroomDomainError):
    """Raised when cover image URL is not a valid HTTPS URL."""

    def __init__(self) -> None:
        super().__init__("Cover image URL must be a valid HTTPS URL")


# Course state errors
class CourseNotFoundError(ClassroomDomainError):
    """Raised when a course cannot be found."""

    def __init__(self, course_id: str) -> None:
        super().__init__(f"Course not found: {course_id}")
        self.course_id = course_id


class CourseAlreadyDeletedError(ClassroomDomainError):
    """Raised when attempting to modify a deleted course."""

    def __init__(self) -> None:
        super().__init__("Course has been deleted")
